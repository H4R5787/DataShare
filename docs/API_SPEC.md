# SECURE PASS RxQ — RESTful API Specification

**Base URL:** `/api/v1`  
**Protocol:** HTTPS / TLS 1.3  
**Content-Type:** `application/json`  
**Authentication:** `Authorization: Bearer <JWT_ACCESS_TOKEN>`  
**Idempotency Header:** `X-Idempotency-Key: <UUIDv4>` (required on state-changing requests)  

---

## 1. Authentication Endpoints

### 1.1 Request OTP
- **Endpoint:** `POST /api/v1/auth/request-otp`
- **Request Body:**
```json
{
  "phone_number": "+919876543210"
}
```
- **Response `200 OK`:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "expires_in_seconds": 300,
  "dev_otp": "123456" // Returned ONLY in Mock/Development mode
}
```

### 1.2 Verify OTP
- **Endpoint:** `POST /api/v1/auth/verify-otp`
- **Request Body:**
```json
{
  "phone_number": "+919876543210",
  "otp": "123456"
}
```
- **Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "usr_990184",
    "phone_number": "+919876543210",
    "full_name": null,
    "is_verified": true
  }
}
```

---

## 2. Operator & Plan Endpoints

### 2.1 Detect Operator & Circle
- **Endpoint:** `POST /api/v1/operators/detect`
- **Request Body:**
```json
{
  "phone_number": "+919876543210"
}
```
- **Response `200 OK`:**
```json
{
  "phone_number": "+919876543210",
  "operator": {
    "id": "op_jio",
    "code": "JIO",
    "name": "Reliance Jio",
    "logo_url": "/assets/operators/jio.svg"
  },
  "circle": {
    "id": "cir_mum",
    "code": "MUM",
    "name": "Mumbai & Maharashtra"
  },
  "is_portable": true
}
```

### 2.2 List Operators
- **Endpoint:** `GET /api/v1/operators`
- **Response `200 OK`:** Array of operator objects (JIO, AIRTEL, VI, BSNL).

### 2.3 List Data Plans
- **Endpoint:** `GET /api/v1/plans?operator_code=JIO&circle_code=MUM&category=BOOSTER`
- **Response `200 OK`:**
```json
[
  {
    "id": "plan_jio_2gb",
    "operator_code": "JIO",
    "plan_code": "JIO_4G_29",
    "data_amount": "2 GB",
    "data_amount_mb": 2048,
    "validity_desc": "Active Plan Validity",
    "price_in_paise": 2900,
    "price_formatted": "₹29",
    "category": "BOOSTER",
    "description": "High speed 4G/5G data add-on. Works with active base plan."
  }
]
```

---

## 3. Order & Checkout Endpoints

### 3.1 Create Order (Idempotent)
- **Endpoint:** `POST /api/v1/orders`
- **Headers:** `X-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000`
- **Request Body:**
```json
{
  "recipient_phone": "+919876543210",
  "operator_id": "op_jio",
  "circle_id": "cir_mum",
  "plan_id": "plan_jio_2gb"
}
```
- **Response `201 Created`:**
```json
{
  "order_id": "ORD_20261009_8819",
  "recipient_phone_masked": "+91 98765 •••••",
  "operator_name": "Reliance Jio",
  "plan_summary": "2 GB Data Booster",
  "amount_in_paise": 2900,
  "status": "PAYMENT_PENDING",
  "created_at": "2026-10-09T23:15:00Z"
}
```

---

## 4. Payment Endpoints

### 4.1 Create Payment Intent
- **Endpoint:** `POST /api/v1/payments/create-intent`
- **Request Body:**
```json
{
  "order_id": "ORD_20261009_8819",
  "payment_method": "UPI"
}
```
- **Response `200 OK`:**
```json
{
  "payment_id": "pay_981293",
  "order_id": "ORD_20261009_8819",
  "amount_in_paise": 2900,
  "gateway": "MOCK",
  "gateway_order_id": "mock_order_99018",
  "checkout_url": null
}
```

### 4.2 Verify / Complete Payment (Client Mock Callback)
- **Endpoint:** `POST /api/v1/payments/verify`
- **Request Body:**
```json
{
  "payment_id": "pay_981293",
  "gateway_payment_id": "mock_pay_success_123",
  "signature": "simulated_valid_signature"
}
```
- **Response `200 OK`:**
```json
{
  "success": true,
  "order_id": "ORD_20261009_8819",
  "order_status": "PAYMENT_SUCCESS",
  "recharge_status": "RECHARGE_PENDING"
}
```

### 4.3 Payment Gateway Webhook
- **Endpoint:** `POST /api/v1/payments/webhook`
- **Headers:** `X-Webhook-Signature: <HMAC_SHA256>`
- **Response `200 OK`:** Processes payment and queues background recharge dispatch.

---

## 5. Transaction & Tracking Endpoints

### 5.1 Get Transaction Details & Live Status
- **Endpoint:** `GET /api/v1/transactions/{order_id}`
- **Response `200 OK`:**
```json
{
  "order_id": "ORD_20261009_8819",
  "recipient_phone_masked": "+91 98765 •••••",
  "operator_code": "JIO",
  "operator_name": "Reliance Jio",
  "plan_data": "2 GB",
  "plan_validity": "Active Plan",
  "amount_formatted": "₹29",
  "current_state": "SUCCESS",
  "telecom_reference_id": "JIO-TXN-99812304",
  "timeline": [
    { "state": "CREATED", "timestamp": "2026-10-09T23:15:00Z" },
    { "state": "PAYMENT_PENDING", "timestamp": "2026-10-09T23:15:02Z" },
    { "state": "PAYMENT_SUCCESS", "timestamp": "2026-10-09T23:15:08Z" },
    { "state": "RECHARGE_PENDING", "timestamp": "2026-10-09T23:15:09Z" },
    { "state": "SUCCESS", "timestamp": "2026-10-09T23:15:12Z" }
  ]
}
```

### 5.2 List User Transactions
- **Endpoint:** `GET /api/v1/transactions?limit=20&offset=0`
- **Response `200 OK`:** Paginated array of past transactions.
