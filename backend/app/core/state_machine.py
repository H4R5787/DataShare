"""Transaction Finite State Machine (FSM) with strict transition verification."""

from enum import Enum
from typing import Dict, Set


class TransactionState(str, Enum):
    CREATED = "CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    RECHARGE_PENDING = "RECHARGE_PENDING"
    SUCCESS = "SUCCESS"
    RECHARGE_FAILED = "RECHARGE_FAILED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


# Allowed state transitions
VALID_TRANSITIONS: Dict[TransactionState, Set[TransactionState]] = {
    TransactionState.CREATED: {
        TransactionState.PAYMENT_PENDING,
        TransactionState.CANCELLED,
        TransactionState.EXPIRED,
    },
    TransactionState.PAYMENT_PENDING: {
        TransactionState.PAYMENT_SUCCESS,
        TransactionState.PAYMENT_FAILED,
        TransactionState.CANCELLED,
        TransactionState.EXPIRED,
    },
    TransactionState.PAYMENT_SUCCESS: {
        TransactionState.RECHARGE_PENDING,
        # Direct failure safeguard in case carrier outage detected immediately
        TransactionState.RECHARGE_FAILED,
    },
    TransactionState.RECHARGE_PENDING: {
        TransactionState.SUCCESS,
        TransactionState.RECHARGE_FAILED,
    },
    TransactionState.RECHARGE_FAILED: {
        TransactionState.REFUND_PENDING,
    },
    TransactionState.REFUND_PENDING: {
        TransactionState.REFUNDED,
    },
    # Terminal states have no further transitions
    TransactionState.SUCCESS: set(),
    TransactionState.PAYMENT_FAILED: set(),
    TransactionState.REFUNDED: set(),
    TransactionState.CANCELLED: set(),
    TransactionState.EXPIRED: set(),
}


class InvalidStateTransitionException(Exception):
    """Raised when an illegal transaction state transition is attempted."""
    def __init__(self, current_state: str, target_state: str):
        self.current_state = current_state
        self.target_state = target_state
        super().__init__(
            f"Illegal state transition from '{current_state}' to '{target_state}'."
        )


def validate_transition(current: TransactionState, target: TransactionState) -> None:
    """Validate that transition from current to target state is legally permitted."""
    allowed = VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidStateTransitionException(current.value, target.value)
