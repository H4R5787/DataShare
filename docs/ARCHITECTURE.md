# SECURE PASS RxQ — System Architecture & Technical Specification

**Version:** 1.0.0  
**Stack:** FastAPI (Python 3.11+) • React 18 + TypeScript + Tailwind CSS • PostgreSQL / SQLite • Redis  

---

## 1. High-Level Architecture Overview

Secure Pass RxQ utilizes a layered Clean Architecture model ensuring modularity, strict separation of concerns, and pluggable telecom and payment provider adapters.

```
┌─────────────────────────────────────────────────────────────┐
│               Client Tier (Mobile-First Web / PWA)          │
│   React 18 + TypeScript + Tailwind CSS + Lucide Icons       │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS (TLS 1.3) / JSON
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               API Gateway & Security Middleware             │
│   FastAPI • CORS • Rate Limiter • Security Headers • Auth   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Application Service Tier                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │   Auth Service   │  │ Recipient Service│  │Plan Service│ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │   Order Service  │  │ Payment Service  │  │Recharge Svc│ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │Idempotency Guard │  │  State Machine   │  │Audit Logger│ │
│  └──────────────────┘  └──────────────────┘  └────────────┘ │
└───────────────┬──────────────────────────────┬──────────────┘
                │                              │
                ▼                              ▼
┌───────────────────────────────┐ ┌───────────────────────────┐
│       Adapter Layer           │ │     Persistence Tier      │
│  ├── Telecom Adapters         │ │  ├── PostgreSQL (or       │
│  │   ├── JioAdapter           │ │  │   SQLite for Dev)      │
│  │   ├── AirtelAdapter        │ │  ├── SQLAlchemy 2.0 Async │
│  │   ├── ViAdapter            │ │  └── Alembic Migrations   │
│  │   ├── BSNLAdapter          │ └───────────────────────────┘
│  │   └── MockOperatorAdapter  │ ┌───────────────────────────┐
│  └── Payment Adapters         │ │   Background Worker       │
│      ├── RazorpayAdapter      │ │  ├── Status Polling       │
│      ├── CashfreeAdapter      │ │  ├── Exponential Retry   │
│      └── MockPaymentAdapter   │ │  └── Auto-Refund Trigger  │
└───────────────────────────────┘ └───────────────────────────┘
```

---

## 2. Finite State Machine (FSM)

The transaction lifecycle enforces strict transitions. Invalid transitions throw `InvalidStateTransitionException` and are logged in `audit_logs`.

```
                    ┌──────────────┐
                    │   CREATED    │
                    └──────┬───────┘
                           │ Order Checked Out
                           ▼
                 ┌──────────────────┐
                 │ PAYMENT_PENDING  │
                 └──────┬─────┬─────┘
    Payment Success     │     │   Payment Failed / Timeout
   ┌────────────────────┘     └────────────────────────┐
   ▼                                                   ▼
┌──────────────────┐                         ┌──────────────────┐
│ PAYMENT_SUCCESS  │                         │  PAYMENT_FAILED  │
└────────┬─────────┘                         └──────────────────┘
         │ Telecom Request Dispatched
         ▼
┌──────────────────┐
│ RECHARGE_PENDING │
└────────┬─────────┘
         ├──────────────────────────────┐
         │ Telecom Success              │ Telecom Terminal Failure
         ▼                              ▼
   ┌───────────┐              ┌──────────────────┐
   │  SUCCESS  │              │ RECHARGE_FAILED  │
   └───────────┘              └────────┬─────────┘
                                       │ Initiate Gateway Refund
                                       ▼
                              ┌──────────────────┐
                              │  REFUND_PENDING  │
                              └────────┬─────────┘
                                       │ Refund Confirmed
                                       ▼
                              ┌──────────────────┐
                              │     REFUNDED     │
                              └──────────────────┘
```

### Valid State Transitions Table
| Source State | Destination State | Trigger / Event |
|---|---|---|
| `CREATED` | `PAYMENT_PENDING` | User initiates checkout |
| `CREATED` | `CANCELLED` | User abandons checkout |
| `PAYMENT_PENDING` | `PAYMENT_SUCCESS` | Webhook / verification confirms payment |
| `PAYMENT_PENDING` | `PAYMENT_FAILED` | Gateway returns failure or timeout |
| `PAYMENT_SUCCESS` | `RECHARGE_PENDING` | Recharge worker takes order |
| `RECHARGE_PENDING` | `SUCCESS` | Telecom returns operator txn ID |
| `RECHARGE_PENDING` | `RECHARGE_FAILED` | Exhausted retries or carrier rejection |
| `RECHARGE_FAILED` | `REFUND_PENDING` | Automated refund submitted to gateway |
| `REFUND_PENDING` | `REFUNDED` | Refund confirmed by payment gateway |

---

## 3. Telecom Adapter Architecture

All telecom communications run through the `OperatorAdapter` abstraction:

```python
class OperatorAdapter(ABC):
    @abstractmethod
    async def validate_number(self, phone: str) -> bool:
        """Validate format and carrier compatibility."""
        pass

    @abstractmethod
    async def detect_operator(self, phone: str) -> OperatorDetectionResult:
        """Resolve carrier and circle via MNP lookup."""
        pass

    @abstractmethod
    async def get_plans(self, circle_id: str, category: Optional[str] = None) -> List[PlanDTO]:
        """Fetch real-time data plans."""
        pass

    @abstractmethod
    async def execute_recharge(self, request: RechargeRequest) -> RechargeResponse:
        """Execute retail data recharge with carrier."""
        pass

    @abstractmethod
    async def query_recharge_status(self, telecom_reference_id: str) -> RechargeStatusResponse:
        """Query terminal status of a pending recharge."""
        pass
```

### Adapter Implementations:
1. `MockOperatorAdapter`: High-fidelity development simulator supporting configurable network latency, test number behaviors (e.g. numbers ending in `999` trigger timeout, `000` trigger carrier failure for refund verification).
2. `JioAdapter`, `AirtelAdapter`, `ViAdapter`, `BSNLAdapter`: Production-ready stubs implementing the normalized carrier API contract.

---

## 4. Payment Adapter Architecture

Payment processing implements the `PaymentGatewayAdapter` interface:

```python
class PaymentGatewayAdapter(ABC):
    @abstractmethod
    async def create_payment_order(self, order_id: str, amount_in_paise: int, currency: str) -> PaymentOrderResult:
        """Initialize payment gateway checkout session."""
        pass

    @abstractmethod
    async def verify_signature(self, payload: dict, signature: str) -> bool:
        """Verify HMAC SHA-256 signature from client or webhook."""
        pass

    @abstractmethod
    async def process_refund(self, payment_id: str, amount_in_paise: int, reason: str) -> RefundResult:
        """Execute automated refund back to source."""
        pass
```

---

## 5. Duplicate Protection & Idempotency Engine

Every checkout and recharge request requires an `X-Idempotency-Key` header (UUIDv4):
1. **Atomic Lock**: A database entry in `idempotency_keys` is inserted inside an ACID transaction.
2. **In-Flight Conflict**: If a concurrent request arrives with the same key while status is `PROCESSING`, the engine responds with `409 Conflict` ("Request currently being processed, please wait").
3. **Replay Cache**: If a completed transaction arrives with the same key, the stored response is returned directly without re-invoking payment gateways or telecom operators.

---

## 6. Security Architecture

1. **OWASP Best Practices**:
   - Parameterized queries across all database calls via SQLAlchemy 2.0 ORM.
   - Secure HTTP Headers: `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Content-Security-Policy`.
   - In-memory rate limiting for OTP verification (3 attempts per 10 minutes) and API endpoints (60 req/min).
2. **Cryptographic Protection**:
   - JWT tokens signed with HS256 / RS256 with short 15-minute expiration.
   - OTP codes hashed with SHA-256 and salted.
   - Zero storage of card PAN, CVV, or UPI PINs.
   - Sensitive phone numbers masked in logs and client read payloads (`+91 98765 •••••`).
3. **Audit Trail**:
   - Every state transition, payment callback, and authentication event logs an immutable entry in `audit_logs`.
