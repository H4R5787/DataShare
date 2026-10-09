"""Test telecom adapter system, MNP detection, and plan catalog."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from backend.app.adapters.telecom.base import RechargeRequest
from backend.app.adapters.telecom.factory import OperatorAdapterFactory
from backend.app.adapters.telecom.mock import MockOperatorAdapter
from backend.app.core.database import Base
from backend.app.core.seeder import seed_initial_data
from backend.app.services.telecom_service import TelecomService


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_maker() as session:
        await seed_initial_data(session)
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_mnp_operator_detection():
    """Verify prefix-based MNP operator and circle resolution."""
    adapter = MockOperatorAdapter()

    # Jio prefix (70xxx)
    jio_res = await adapter.detect_operator("+917012345678")
    assert jio_res.operator_code == "JIO"
    assert jio_res.circle_code == "MUM"

    # Airtel prefix (98xxx)
    airtel_res = await adapter.detect_operator("+919812345678")
    assert airtel_res.operator_code == "AIRTEL"
    assert airtel_res.circle_code == "DL"

    # Vi prefix (91xxx)
    vi_res = await adapter.detect_operator("+919112345678")
    assert vi_res.operator_code == "VI"
    assert vi_res.circle_code == "MAH"

    # BSNL prefix (94xxx)
    bsnl_res = await adapter.detect_operator("+919412345678")
    assert bsnl_res.operator_code == "BSNL"
    assert bsnl_res.circle_code == "KA"


@pytest.mark.asyncio
async def test_recharge_execution_behaviors():
    """Verify success, timeout, and failure simulation hooks."""
    adapter = OperatorAdapterFactory.get_adapter("JIO")

    # Regular success
    req_success = RechargeRequest(
        order_id="ORD_1",
        recipient_phone="+919820012345",
        operator_code="JIO",
        plan_code="JIO_4G_29",
        amount_in_paise=2900,
    )
    res_success = await adapter.execute_recharge(req_success)
    assert res_success.success is True
    assert res_success.status == "SUCCESS"
    assert "JIO-TXN-" in res_success.telecom_reference_id

    # Simulated carrier failure (ending in 000)
    req_fail = RechargeRequest(
        order_id="ORD_2",
        recipient_phone="+919820000000",
        operator_code="JIO",
        plan_code="JIO_4G_29",
        amount_in_paise=2900,
    )
    res_fail = await adapter.execute_recharge(req_fail)
    assert res_fail.success is False
    assert res_fail.status == "FAILED"

    # Simulated timeout / pending (ending in 999)
    req_pending = RechargeRequest(
        order_id="ORD_3",
        recipient_phone="+919820000999",
        operator_code="JIO",
        plan_code="JIO_4G_29",
        amount_in_paise=2900,
    )
    res_pending = await adapter.execute_recharge(req_pending)
    assert res_pending.status == "PENDING"
    assert "JIO-PEND-" in res_pending.telecom_reference_id


@pytest.mark.asyncio
async def test_telecom_service_plan_retrieval(db_session: AsyncSession):
    """Verify querying plans via TelecomService."""
    service = TelecomService(db_session)

    # Fetch Jio plans
    jio_plans = await service.get_plans_for_operator(operator_code="JIO")
    assert len(jio_plans) >= 5
    assert any(p.data_amount == "2 GB" and p.price_in_paise == 2900 for p in jio_plans)

    # Fetch Booster category
    boosters = await service.get_plans_for_operator(category="BOOSTER")
    assert len(boosters) >= 4
    for p in boosters:
        assert p.category == "BOOSTER"
