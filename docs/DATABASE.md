# SECURE PASS RxQ — Database Schema Specification

**Engine:** PostgreSQL 15+ / SQLite Async (Dev mode)  
**ORM:** SQLAlchemy 2.0 Async (Pydantic v2 schemas)  

---

## Entity Relationship Overview

```
 [users] 1──* [user_sessions]
    │
    ├──1──* [saved_recipients]
    │
    └──1──* [orders] 1──1 [payments] 1──* [refunds]
               │
               ├──1──1 [recharges]
               │
               └──*──1 [plans] *──1 [operators]
```

---

## Table Definitions

### 1. `users`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) / UUID | PRIMARY KEY | Unique user identifier |
| `phone_number` | VARCHAR(15) | UNIQUE, NOT NULL | E.164 phone (`+919876543210`) |
| `full_name` | VARCHAR(100) | NULL | Optional user display name |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account active flag |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Account creation time |
| `updated_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Last update timestamp |

### 2. `user_sessions`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Session identifier |
| `user_id` | VARCHAR(36) | FK -> users(id) | Reference to user |
| `token_hash` | VARCHAR(64) | NOT NULL, INDEX | SHA-256 hash of access token |
| `device_info` | VARCHAR(255) | NULL | Client user agent / device model |
| `ip_address` | VARCHAR(45) | NULL | Client IP |
| `expires_at` | TIMESTAMP WITH TZ | NOT NULL | Session expiry timestamp |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Login timestamp |

### 3. `otp_verifications`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | OTP session ID |
| `phone_number` | VARCHAR(15) | NOT NULL, INDEX | Target mobile number |
| `otp_hash` | VARCHAR(64) | NOT NULL | Salted SHA-256 hash of OTP |
| `attempts` | INTEGER | DEFAULT 0 | Failed attempts counter |
| `is_used` | BOOLEAN | DEFAULT FALSE | Consumption flag |
| `expires_at` | TIMESTAMP WITH TZ | NOT NULL | 5-minute expiry |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Request timestamp |

### 4. `operators`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Operator ID |
| `code` | VARCHAR(20) | UNIQUE, NOT NULL | JIO, AIRTEL, VI, BSNL |
| `name` | VARCHAR(50) | NOT NULL | Reliance Jio, Bharti Airtel, etc. |
| `logo_url` | VARCHAR(255) | NULL | Brand asset path |
| `is_active` | BOOLEAN | DEFAULT TRUE | Operational status |

### 5. `circles`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Circle ID |
| `code` | VARCHAR(20) | UNIQUE, NOT NULL | DL, MUM, MAH, KAR, AP, etc. |
| `name` | VARCHAR(100) | NOT NULL | Telecom service area name |

### 6. `plans`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Unique plan identifier |
| `operator_id` | VARCHAR(36) | FK -> operators(id) | Associated carrier |
| `circle_id` | VARCHAR(36) | FK -> circles(id), NULL| Circle specific or pan-India |
| `plan_code` | VARCHAR(50) | NOT NULL | Carrier SKU code |
| `data_amount` | VARCHAR(20) | NOT NULL | e.g. "1 GB", "2 GB", "12 GB" |
| `data_amount_mb`| INTEGER | NOT NULL | Raw MB for sorting/filtering |
| `validity_desc` | VARCHAR(50) | NOT NULL | "Active Plan", "28 Days" |
| `price_in_paise`| INTEGER | NOT NULL | e.g. 2900 for ₹29 |
| `category` | VARCHAR(30) | NOT NULL | BOOSTER, DAILY, WORK, BULK |
| `description` | TEXT | NOT NULL | Plan benefits and carrier terms |
| `is_active` | BOOLEAN | DEFAULT TRUE | Availability status |

### 7. `saved_recipients`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Saved contact ID |
| `user_id` | VARCHAR(36) | FK -> users(id) | Owner user ID |
| `phone_number` | VARCHAR(15) | NOT NULL | Recipient phone |
| `nickname` | VARCHAR(50) | NOT NULL | e.g. "Arjun Hostel", "Mom" |
| `operator_id` | VARCHAR(36) | FK -> operators(id) | Detected/saved operator |
| `circle_id` | VARCHAR(36) | FK -> circles(id) | Detected/saved circle |
| `last_recharged_at`| TIMESTAMP WITH TZ| NULL | Last gift timestamp |

### 8. `orders`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Unique order ID (`ORD-...`) |
| `user_id` | VARCHAR(36) | FK -> users(id) | Buyer user ID |
| `recipient_phone`| VARCHAR(15) | NOT NULL | Target mobile number |
| `operator_id` | VARCHAR(36) | FK -> operators(id) | Target carrier |
| `circle_id` | VARCHAR(36) | FK -> circles(id) | Target circle |
| `plan_id` | VARCHAR(36) | FK -> plans(id) | Selected data pack |
| `amount_in_paise`| INTEGER | NOT NULL | Total charged amount |
| `currency` | VARCHAR(3) | DEFAULT 'INR' | Currency code |
| `status` | VARCHAR(30) | NOT NULL, INDEX | FSM state |
| `idempotency_key`| VARCHAR(64) | UNIQUE, NOT NULL | Anti-duplicate key |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Order placement time |
| `updated_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | State update time |

### 9. `payments`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Unique payment ID |
| `order_id` | VARCHAR(36) | FK -> orders(id), UNIQUE| Associated order |
| `gateway_name` | VARCHAR(30) | NOT NULL | RAZORPAY, CASHFREE, MOCK |
| `gateway_payment_id`| VARCHAR(100)| NULL | External PG transaction ID |
| `amount_in_paise`| INTEGER | NOT NULL | Amount paid |
| `status` | VARCHAR(30) | NOT NULL | PENDING, SUCCESS, FAILED |
| `payment_method` | VARCHAR(30) | NULL | UPI, CARD, NETBANKING |
| `failure_reason`| TEXT | NULL | Reason for payment failure |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Gateway checkout time |

### 10. `recharges`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Unique recharge task ID |
| `order_id` | VARCHAR(36) | FK -> orders(id), UNIQUE| Associated order |
| `operator_id` | VARCHAR(36) | FK -> operators(id) | Telecom operator |
| `recipient_phone`| VARCHAR(15) | NOT NULL | Target phone number |
| `telecom_reference_id`| VARCHAR(100)| NULL | Carrier acknowledgment code |
| `status` | VARCHAR(30) | NOT NULL | PENDING, SUCCESS, FAILED |
| `retry_count` | INTEGER | DEFAULT 0 | Automatic retry attempts |
| `last_error` | TEXT | NULL | Carrier failure details |
| `completed_at` | TIMESTAMP WITH TZ | NULL | Carrier confirmation timestamp |

### 11. `refunds`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Unique refund task ID |
| `payment_id` | VARCHAR(36) | FK -> payments(id) | Associated payment |
| `order_id` | VARCHAR(36) | FK -> orders(id) | Associated order |
| `gateway_refund_id`| VARCHAR(100)| NULL | External refund ID |
| `amount_in_paise`| INTEGER | NOT NULL | Amount refunded |
| `status` | VARCHAR(30) | NOT NULL | PENDING, SUCCESS, FAILED |
| `reason` | VARCHAR(255) | NOT NULL | e.g. "Recharge failure auto-refund" |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Refund initiation time |

### 12. `idempotency_keys`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `key` | VARCHAR(64) | PRIMARY KEY | UUIDv4 idempotency key |
| `user_id` | VARCHAR(36) | NOT NULL | Calling user ID |
| `request_path` | VARCHAR(100) | NOT NULL | Target endpoint |
| `request_hash` | VARCHAR(64) | NOT NULL | SHA-256 of request payload |
| `status` | VARCHAR(20) | NOT NULL | PROCESSING, COMPLETED |
| `response_code`| INTEGER | NULL | HTTP status code |
| `response_body`| TEXT | NULL | Cached JSON response |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Lock creation time |
| `expires_at` | TIMESTAMP WITH TZ | NOT NULL | Lock TTL |

### 13. `audit_logs`
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | VARCHAR(36) | PRIMARY KEY | Audit event ID |
| `user_id` | VARCHAR(36) | NULL | Acting user |
| `action` | VARCHAR(50) | NOT NULL | ORDER_CREATED, PAYMENT_VERIFIED, etc. |
| `entity_type` | VARCHAR(30) | NOT NULL | ORDER, PAYMENT, RECHARGE, AUTH |
| `entity_id` | VARCHAR(36) | NOT NULL | Target record ID |
| `ip_address` | VARCHAR(45) | NULL | Client IP |
| `metadata_json`| TEXT | NULL | Contextual audit attributes |
| `created_at` | TIMESTAMP WITH TZ | DEFAULT NOW() | Event timestamp |
