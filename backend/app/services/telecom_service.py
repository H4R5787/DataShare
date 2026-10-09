"""Operator detection and plan retrieval services."""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.adapters.telecom.factory import OperatorAdapterFactory
from backend.app.core.security import mask_phone_number
from backend.app.models.operator import Circle, Operator
from backend.app.models.plan import Plan
from backend.app.schemas.operator import CircleDTO, OperatorDetectResponse, OperatorDTO
from backend.app.schemas.plan import PlanDTO


class TelecomService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_operators(self) -> List[OperatorDTO]:
        """List all active telecom operators."""
        query = select(Operator).where(Operator.is_active == True).order_by(Operator.name)
        operators = (await self.session.execute(query)).scalars().all()
        return [OperatorDTO.model_validate(op) for op in operators]

    async def list_circles(self) -> List[CircleDTO]:
        """List supported telecom circles."""
        query = select(Circle).order_by(Circle.name)
        circles = (await self.session.execute(query)).scalars().all()
        return [CircleDTO.model_validate(cir) for cir in circles]

    async def detect_operator_for_phone(self, phone_number: str) -> OperatorDetectResponse:
        """Resolve carrier and circle for a recipient number."""
        adapter = OperatorAdapterFactory.get_adapter("MOCK")
        detected = await adapter.detect_operator(phone_number)

        # Lookup DB Operator
        op_query = select(Operator).where(Operator.code == detected.operator_code)
        op = (await self.session.execute(op_query)).scalars().first()
        if not op:
            # Fallback to first available operator
            op = (await self.session.execute(select(Operator))).scalars().first()

        # Lookup DB Circle
        cir_query = select(Circle).where(Circle.code == detected.circle_code)
        cir = (await self.session.execute(cir_query)).scalars().first()
        if not cir:
            cir = (await self.session.execute(select(Circle))).scalars().first()

        return OperatorDetectResponse(
            phone_number=detected.phone_number,
            phone_number_masked=mask_phone_number(detected.phone_number),
            operator=OperatorDTO.model_validate(op),
            circle=CircleDTO.model_validate(cir),
            is_portable=detected.is_portable,
            confidence=detected.confidence,
        )

    async def get_plans_for_operator(
        self,
        operator_id: Optional[str] = None,
        operator_code: Optional[str] = None,
        category: Optional[str] = None,
    ) -> List[PlanDTO]:
        """Retrieve available retail data packs."""
        query = select(Plan).where(Plan.is_active == True)

        if operator_id:
            query = query.where(Plan.operator_id == operator_id)
        elif operator_code:
            op_subquery = select(Operator.id).where(Operator.code == operator_code.upper())
            query = query.where(Plan.operator_id.in_(op_subquery))

        if category:
            query = query.where(Plan.category == category.upper())

        query = query.order_by(Plan.price_in_paise.asc())
        plans = (await self.session.execute(query)).scalars().all()

        results = []
        for p in plans:
            price_fmt = f"₹{p.price_in_paise // 100}"
            results.append(
                PlanDTO(
                    id=p.id,
                    operator_id=p.operator_id,
                    circle_id=p.circle_id,
                    plan_code=p.plan_code,
                    data_amount=p.data_amount,
                    data_amount_mb=p.data_amount_mb,
                    validity_desc=p.validity_desc,
                    price_in_paise=p.price_in_paise,
                    price_formatted=price_fmt,
                    category=p.category,
                    description=p.description,
                    is_active=p.is_active,
                )
            )
        return results
