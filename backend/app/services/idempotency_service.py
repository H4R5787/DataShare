"""Idempotency engine for duplicate request detection and response replay."""

import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.security import hash_request_payload
from backend.app.models.idempotency import IdempotencyRecord


class IdempotencyService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def acquire_lock_or_replay(
        self,
        key: str,
        user_id: str,
        request_path: str,
        payload_data: Any,
    ) -> Optional[Tuple[int, Dict[str, Any]]]:
        """
        Check idempotency key.
        - If completed, returns (status_code, response_body) for direct replay.
        - If currently processing, raises HTTP 409 Conflict.
        - If new, reserves atomic lock with PROCESSING state.
        """
        if not key or len(key.strip()) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Valid 'X-Idempotency-Key' header is required for this operation.",
            )

        payload_str = json.dumps(payload_data, sort_keys=True, default=str)
        payload_hash = hash_request_payload(payload_str)
        now = datetime.now(timezone.utc)

        existing = await self.session.get(IdempotencyRecord, key)
        if existing:
            if existing.status == "COMPLETED" and existing.response_body:
                # Cache replay!
                return existing.response_code or 200, json.loads(existing.response_body)
            elif existing.status == "PROCESSING":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A transaction with this Idempotency Key is already being processed. Please wait.",
                )

        # Create lock
        record = IdempotencyRecord(
            key=key,
            user_id=user_id,
            request_path=request_path,
            request_hash=payload_hash,
            status="PROCESSING",
            expires_at=now + timedelta(hours=2),
        )
        self.session.add(record)
        await self.session.commit()
        return None

    async def record_completed(
        self,
        key: str,
        response_code: int,
        response_body: Dict[str, Any],
    ) -> None:
        """Mark idempotency record as COMPLETED and cache response."""
        record = await self.session.get(IdempotencyRecord, key)
        if record:
            record.status = "COMPLETED"
            record.response_code = response_code
            record.response_body = json.dumps(response_body, default=str)
            await self.session.commit()

    async def release_lock_on_failure(self, key: str) -> None:
        """Release lock if initial validation fails before state transition."""
        record = await self.session.get(IdempotencyRecord, key)
        if record and record.status == "PROCESSING":
            await self.session.delete(record)
            await self.session.commit()
