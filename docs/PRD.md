# SECURE PASS RxQ — Product Requirements Document (PRD)

**Document Version:** 1.0.0  
**Status:** Approved / In Development  
**Product Name:** Secure Pass RxQ (Short: Secure Pass)  
**Tagline:** Secure. Simple. Connected.

---

## 1. Executive Summary & Vision
Secure Pass RxQ is a modern, high-trust, mobile-first telecom data gifting and recharge platform. It enables smartphone users to easily purchase and instantly send mobile data booster packs to another person's mobile phone number across all major telecom operators in India (Jio, Airtel, Vi, BSNL).

The user journey is engineered to be friction-free and completed in under 30 seconds:
```
Enter Number ➔ Auto-Detect Operator ➔ Select Data Pack ➔ Confirm ➔ Pay ➔ Recharge ➔ Track ➔ Complete
```

---

## 2. Core Business Rule & Transparency Directive
The application strictly distinguishes between:
1. **Direct Data Balance Transfer** (transferring existing unspent GB from user's SIM to another SIM) — **NOT CLAIMED OR PROMISED**, as Indian telecom carriers do not offer peer-to-peer data balance routing APIs.
2. **Data-Pack Gifting / Recharge** (purchasing an authorized top-up data pack for the recipient's mobile number via authorized telecom recharge gateways) — **THE ACTIVE BUSINESS MODEL**.

The platform provides complete transparency, never misleading users about balance transfers. All recharges are legitimate carrier data top-ups.

---

## 3. Goals & Non-Goals

### Goals
- **Sub-30-Second Gifting Flow:** From entering the recipient's phone number to successful payment.
- **Zero Duplicate Charges:** 100% idempotency enforcement preventing double-tapping or network-retry duplicate payments.
- **Operator Adapter Architecture:** Pluggable telco engine allowing seamless switching between Jio, Airtel, Vi, BSNL, and development Mock providers.
- **Resilient State Machine:** Strict transaction state lifecycle with automated reconciliation and refund triggers.
- **Bank-Grade Security:** OWASP compliance, encrypted tokens, masked sensitive data, and rate-limited authentication.

### Non-Goals
- Not a general digital wallet or UPI peer-to-peer money transfer app.
- No general utility bill payments (electricity, gas, water).
- No unauthorized scraping or reverse-engineering of telecom operator subscriber portals.

---

## 4. User Personas

### Persona 1: Arjun Sharma (The College Student)
- **Age:** 21 | **Location:** Bengaluru | **Device:** Android
- **Context:** Friend ran out of daily 1.5 GB quota during an online hackathon or gaming session.
- **Goal:** Quickly gift a 2 GB / ₹29 data pack to his friend without asking for UPI IDs or banking details.
- **Pain Point:** Mainstream payment apps require navigating 8 screens filled with loans, credit cards, and scratch cards.

### Persona 2: Priya Nair (The Working Professional / Elder Sibling)
- **Age:** 29 | **Location:** Mumbai | **Device:** iOS
- **Context:** Younger sibling studying at a hostel has an emergency power/Wi-Fi outage and needs cellular data for an exam.
- **Goal:** Send a high-speed 12 GB booster pack instantly and receive immediate verification of recharge success.
- **Pain Point:** Anxiety about double deductions during flaky connectivity; unclear validity terms.

### Persona 3: Rajesh Gupta (Small Business Owner)
- **Age:** 45 | **Location:** Delhi NCR | **Device:** Android
- **Context:** Manages 4 field delivery staff whose GPS apps halt when monthly data expires.
- **Goal:** Re-gift data packs to saved recipient contacts with one tap and download clear receipts.

---

## 5. Functional Requirements & Feature Specification

### 5.1 Authentication & Session Management
- **Phone Number Authentication:** 10-digit mobile number entry (`+91`).
- **OTP Verification:** 6-digit numeric OTP with 5-minute validity. Rate limited to 3 requests per 10 minutes.
- **Session Tokens:** Secure JWT (Access Token 15-min expiry, Refresh Token 7-day expiry).
- **Session Revocation:** Secure logout and remote session termination.

### 5.2 Recipient Management & Operator Detection
- **Input Validation:** E.164 standard formatting, regex validation for Indian mobile numbering series (starts with 6, 7, 8, or 9).
- **Operator & Circle Auto-Detection:** Resolved via telecom series lookup / MNP API adapter.
- **Manual Confirmation & Override:** User can verify and change operator/circle if recently ported via MNP.
- **Saved Contacts / Frequent Recipients:** Ability to bookmark recipients with nicknames and carrier icons.

### 5.3 Data Pack Catalog
- **Curated Plans:** Categorized by Booster, Daily Add-on, Unlimited, and Validity Extension packs.
- **Plan Details:** Data allowance (e.g., 1 GB, 3 GB, 12 GB, 50 GB), Price in ₹, Validity (e.g., "Active Base Plan", "30 Days"), Benefits summary.
- **Carrier Rules Display:** Informs user if the pack requires an active base plan.

### 5.4 Order Review & Idempotency
- **Summary Card:** Recipient number (masked: `+91 98765 •••••`), Operator logo, Pack quota, Validity, Base Price, Taxes, Total Payable.
- **Idempotency Key:** Client generates unique UUIDv4 per checkout session passed via `X-Idempotency-Key` header. Prevents double billing.

### 5.5 Payment Processing
- **Supported Methods:** UPI (Intent & QR), Credit/Debit Cards, Net Banking.
- **Payment Verification:** Server-side gateway verification and webhook listener with HMAC SHA-256 signature checking.
- **Mock Payment Mode:** Realistic sandbox supporting Instant Success, Payment Delay, and Failure simulation for offline testing.

### 5.6 Recharge Fulfillment & State Machine
- **Transaction Lifecycle:**
  `CREATED` ➔ `PAYMENT_PENDING` ➔ `PAYMENT_SUCCESS` ➔ `RECHARGE_PENDING` ➔ `SUCCESS`
- **Failure Lifecycle:**
  `PAYMENT_FAILED` | `RECHARGE_FAILED` ➔ `REFUND_PENDING` ➔ `REFUNDED`
- **Automatic Retry:** Transient carrier timeouts retry up to 3 times with exponential backoff and jitter.
- **Automated Refund:** If telecom fulfillment fails permanently, payment gateway refund is triggered automatically.

### 5.7 Real-time Tracking & History
- **Live Progress Stepper:** Animated 3-step state tracking (Payment ➔ Telecom Dispatch ➔ Confirmation).
- **Transaction History:** Paginated list with filtering by status and date range.
- **Transaction Details & Timeline:** Audit timestamps for each state transition, operator reference number, and receipt download.

---

## 6. Non-Functional Requirements
- **Performance:** API p95 response time < 150ms; Client initial load < 1.2s.
- **Reliability:** 99.9% uptime target; zero duplicate recharge executions.
- **Security:** OWASP Top 10 compliance; strict IDOR checks; no plain-text PII storage; parameterized SQL queries.
- **Maintainability:** Modular clean architecture, type safety (TypeScript & Pydantic), automated test suite with >85% code coverage.
