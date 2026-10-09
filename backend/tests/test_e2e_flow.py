"""End-to-end integration tests: Full gifting flow, duplicate idempotency protection, auto-refund, and IDOR defense."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.core.database import Base, get_db
from backend.app.core.seeder import seed_initial_data
from backend.app.main import app


@pytest_asyncio.fixture
async def client():
    # Setup test engine
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        await seed_initial_data(session)

    async def override_get_db():
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
async def test_full_send_data_journey(client: AsyncClient):
    """
    Test complete 12-step flow:
    1. Auth OTP
    2. Detect Operator
    3. List Plans
    4. Create Order with Idempotency Key
    5. Duplicate request with same Idempotency Key (verifies cached replay!)
    6. Create Payment Intent
    7. Verify Payment -> triggers telecom recharge
    8. Check Transaction Details and Timeline
    """
    phone = "+919876543210"

    # Step 1: Auth
    otp_res = await client.post("/api/v1/auth/request-otp", json={"phone_number": phone})
    assert otp_res.status_code == 200
    dev_otp = otp_res.json()["dev_otp"]

    token_res = await client.post("/api/v1/auth/verify-otp", json={"phone_number": phone, "otp": dev_otp})
    assert token_res.status_code == 200
    token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Detect operator
    recipient_phone = "+917012345678"
    detect_res = await client.post("/api/v1/operators/detect", json={"phone_number": recipient_phone})
    assert detect_res.status_code == 200
    detect_data = detect_res.json()
    assert detect_data["operator"]["code"] == "JIO"
    operator_id = detect_data["operator"]["id"]

    # Step 3: Fetch plans
    plans_res = await client.get(f"/api/v1/plans?operator_id={operator_id}")
    assert plans_res.status_code == 200
    plans = plans_res.json()
    assert len(plans) > 0
    selected_plan = next(p for p in plans if p["data_amount"] == "2 GB")
    plan_id = selected_plan["id"]

    # Step 4: Create Order with Idempotency Key
    idempotency_key = str(uuid.uuid4())
    order_payload = {
        "recipient_phone": recipient_phone,
        "operator_id": operator_id,
        "circle_id": detect_data["circle"]["id"],
        "plan_id": plan_id,
    }
    order_res = await client.post(
        "/api/v1/orders",
        json=order_payload,
        headers={**headers, "X-Idempotency-Key": idempotency_key},
    )
    assert order_res.status_code == 201
    order_data = order_res.json()
    order_id = order_data["order_id"]
    assert order_data["status"] == "PAYMENT_PENDING"

    # Step 5: Duplicate request protection (Idempotency Replay test)
    duplicate_res = await client.post(
        "/api/v1/orders",
        json=order_payload,
        headers={**headers, "X-Idempotency-Key": idempotency_key},
    )
    assert duplicate_res.status_code == 201
    assert duplicate_res.json()["order_id"] == order_id  # Replayed identical cached order

    # Step 6: Create Payment Intent
    intent_res = await client.post(
        "/api/v1/payments/create-intent",
        json={"order_id": order_id, "payment_method": "UPI"},
        headers=headers,
    )
    assert intent_res.status_code == 200
    intent_data = intent_res.json()
    payment_id = intent_data["payment_id"]

    # Step 7: Verify Payment -> immediately activates telecom recharge
    verify_res = await client.post(
        "/api/v1/payments/verify",
        json={
            "order_id": order_id,
            "payment_id": payment_id,
            "gateway_payment_id": "pay_test_success_9981",
            "payment_method": "UPI",
            "signature": "valid_signature",
        },
        headers=headers,
    )
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    assert verify_data["order_status"] == "SUCCESS"
    assert "JIO-TXN-" in verify_data["telecom_reference_id"]

    # Step 8: Transaction Details and Timeline Stepper
    txn_res = await client.get(f"/api/v1/transactions/{order_id}", headers=headers)
    assert txn_res.status_code == 200
    txn_data = txn_res.json()
    assert txn_data["current_state"] == "SUCCESS"
    assert txn_data["telecom_reference_id"] is not None
    assert len(txn_data["timeline"]) >= 4  # Placed -> Paid -> Dispatched -> Activated


@pytest.mark.asyncio
async def test_recharge_failure_and_auto_refund_flow(client: AsyncClient):
    """
    Verify carrier decline handling:
    Payment succeeds -> Telecom carrier declines (number ending in 000) ->
    State transitions to RECHARGE_FAILED -> REFUND_PENDING -> REFUNDED.
    """
    phone = "+919876543220"
    # Login
    await client.post("/api/v1/auth/request-otp", json={"phone_number": phone})
    token_res = await client.post("/api/v1/auth/verify-otp", json={"phone_number": phone, "otp": "123456"})
    headers = {"Authorization": f"Bearer {token_res.json()['access_token']}"}

    # Recipient ending in '000' triggers carrier failure hook in mock adapter
    fail_recipient = "+919820000000"
    detect = (await client.post("/api/v1/operators/detect", json={"phone_number": fail_recipient})).json()
    plans = (await client.get(f"/api/v1/plans?operator_id={detect['operator']['id']}")).json()

    # Create Order
    order_res = await client.post(
        "/api/v1/orders",
        json={
            "recipient_phone": fail_recipient,
            "operator_id": detect["operator"]["id"],
            "plan_id": plans[0]["id"],
        },
        headers={**headers, "X-Idempotency-Key": str(uuid.uuid4())},
    )
    order_id = order_res.json()["order_id"]

    # Create Payment Intent
    intent = (await client.post("/api/v1/payments/create-intent", json={"order_id": order_id}, headers=headers)).json()

    # Verify Payment -> Carrier fails -> Auto-refund initiates!
    verify_res = await client.post(
        "/api/v1/payments/verify",
        json={
            "order_id": order_id,
            "payment_id": intent["payment_id"],
            "gateway_payment_id": "pay_test_99218",
            "payment_method": "UPI",
            "signature": "valid_sig",
        },
        headers=headers,
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["order_status"] == "REFUNDED"

    # Verify transaction details shows REFUNDED state
    txn_data = (await client.get(f"/api/v1/transactions/{order_id}", headers=headers)).json()
    assert txn_data["current_state"] == "REFUNDED"
    assert txn_data["refund_status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_idor_protection(client: AsyncClient):
    """Verify User B cannot access User A's order."""
    # User A
    await client.post("/api/v1/auth/request-otp", json={"phone_number": "+919876543231"})
    tA = (await client.post("/api/v1/auth/verify-otp", json={"phone_number": "+919876543231", "otp": "123456"})).json()["access_token"]

    # User B
    await client.post("/api/v1/auth/request-otp", json={"phone_number": "+919876543232"})
    tB = (await client.post("/api/v1/auth/verify-otp", json={"phone_number": "+919876543232", "otp": "123456"})).json()["access_token"]

    # User A creates order
    plans = (await client.get("/api/v1/plans?operator_code=JIO")).json()
    op = (await client.get("/api/v1/operators")).json()[0]
    order = (
        await client.post(
            "/api/v1/orders",
            json={"recipient_phone": "+919876543231", "operator_id": op["id"], "plan_id": plans[0]["id"]},
            headers={"Authorization": f"Bearer {tA}", "X-Idempotency-Key": str(uuid.uuid4())},
        )
    ).json()

    # User B attempts to access User A's order -> asserts 403 Forbidden
    unauth_res = await client.get(f"/api/v1/orders/{order['order_id']}", headers={"Authorization": f"Bearer {tB}"})
    assert unauth_res.status_code == 403


@pytest.mark.asyncio
async def test_root_serves_html(client: AsyncClient):
    """Verify root / serves index.html."""
    res = await client.get("/")
    assert res.status_code == 200
    assert "Secure Pass RxQ" in res.text
