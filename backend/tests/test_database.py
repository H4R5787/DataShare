"""Test database schema creation, models, and initial seeding."""

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from backend.app.core.database import Base
from backend.app.core.seeder import seed_initial_data
from backend.app.models.operator import Operator, Circle
from backend.app.models.plan import Plan
from backend.app.models.user import User
from backend.app.models.order import Order
from backend.app.core.state_machine import TransactionState, validate_transition, InvalidStateTransitionException


@pytest_asyncio.fixture
async def test_session():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_tables_and_seeding(test_session: AsyncSession):
    """Verify that tables are created and seed_initial_data populates operators, circles, and plans."""
    await seed_initial_data(test_session)

    # Verify operators
    operators = (await test_session.execute(select(Operator))).scalars().all()
    assert len(operators) == 4
    codes = {op.code for op in operators}
    assert codes == {"JIO", "AIRTEL", "VI", "BSNL"}

    # Verify circles
    circles = (await test_session.execute(select(Circle))).scalars().all()
    assert len(circles) >= 8

    # Verify plans
    plans = (await test_session.execute(select(Plan))).scalars().all()
    assert len(plans) >= 19

    # Verify Jio 2 GB plan details
    jio_2gb = next((p for p in plans if p.id == "plan_jio_2gb"), None)
    assert jio_2gb is not None
    assert jio_2gb.price_in_paise == 2900
    assert jio_2gb.data_amount == "2 GB"


def test_state_machine_valid_transitions():
    """Verify state machine valid transitions."""
    # CREATED -> PAYMENT_PENDING
    validate_transition(TransactionState.CREATED, TransactionState.PAYMENT_PENDING)

    # PAYMENT_PENDING -> PAYMENT_SUCCESS
    validate_transition(TransactionState.PAYMENT_PENDING, TransactionState.PAYMENT_SUCCESS)

    # PAYMENT_SUCCESS -> RECHARGE_PENDING
    validate_transition(TransactionState.PAYMENT_SUCCESS, TransactionState.RECHARGE_PENDING)

    # RECHARGE_PENDING -> SUCCESS
    validate_transition(TransactionState.RECHARGE_PENDING, TransactionState.SUCCESS)

    # RECHARGE_PENDING -> RECHARGE_FAILED
    validate_transition(TransactionState.RECHARGE_PENDING, TransactionState.RECHARGE_FAILED)

    # RECHARGE_FAILED -> REFUND_PENDING
    validate_transition(TransactionState.RECHARGE_FAILED, TransactionState.REFUND_PENDING)

    # REFUND_PENDING -> REFUNDED
    validate_transition(TransactionState.REFUND_PENDING, TransactionState.REFUNDED)


def test_state_machine_invalid_transitions():
    """Verify state machine catches illegal transitions."""
    # Cannot jump directly from CREATED to SUCCESS
    with pytest.raises(InvalidStateTransitionException):
        validate_transition(TransactionState.CREATED, TransactionState.SUCCESS)

    # Cannot transition from terminal SUCCESS to anything
    with pytest.raises(InvalidStateTransitionException):
        validate_transition(TransactionState.SUCCESS, TransactionState.CREATED)

    # Cannot transition from PAYMENT_FAILED to SUCCESS
    with pytest.raises(InvalidStateTransitionException):
        validate_transition(TransactionState.PAYMENT_FAILED, TransactionState.SUCCESS)
