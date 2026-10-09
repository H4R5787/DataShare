"""Database initialization and master data seeding for operators, circles, and data packs."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.operator import Operator, Circle
from backend.app.models.plan import Plan


DEFAULT_OPERATORS = [
    {
        "id": "op_jio",
        "code": "JIO",
        "name": "Reliance Jio",
        "logo_url": "/assets/operators/jio.svg",
        "is_active": True,
    },
    {
        "id": "op_airtel",
        "code": "AIRTEL",
        "name": "Bharti Airtel",
        "logo_url": "/assets/operators/airtel.svg",
        "is_active": True,
    },
    {
        "id": "op_vi",
        "code": "VI",
        "name": "Vodafone Idea (Vi)",
        "logo_url": "/assets/operators/vi.svg",
        "is_active": True,
    },
    {
        "id": "op_bsnl",
        "code": "BSNL",
        "name": "BSNL",
        "logo_url": "/assets/operators/bsnl.svg",
        "is_active": True,
    },
]

DEFAULT_CIRCLES = [
    {"id": "cir_mum", "code": "MUM", "name": "Mumbai", "region": "West"},
    {"id": "cir_dl", "code": "DL", "name": "Delhi NCR", "region": "North"},
    {"id": "cir_mah", "code": "MAH", "name": "Maharashtra & Goa", "region": "West"},
    {"id": "cir_ka", "code": "KA", "name": "Karnataka", "region": "South"},
    {"id": "cir_tn", "code": "TN", "name": "Tamil Nadu & Chennai", "region": "South"},
    {"id": "cir_ap", "code": "AP", "name": "Andhra Pradesh & Telangana", "region": "South"},
    {"id": "cir_guj", "code": "GUJ", "name": "Gujarat", "region": "West"},
    {"id": "cir_up", "code": "UP", "name": "Uttar Pradesh", "region": "North"},
]

DEFAULT_PLANS = [
    # Jio Plans
    {
        "id": "plan_jio_1gb",
        "operator_id": "op_jio",
        "plan_code": "JIO_4G_19",
        "data_amount": "1 GB",
        "data_amount_mb": 1024,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 1900,
        "category": "BOOSTER",
        "description": "High-speed 4G/5G data add-on. Works alongside active base plan.",
    },
    {
        "id": "plan_jio_2gb",
        "operator_id": "op_jio",
        "plan_code": "JIO_4G_29",
        "data_amount": "2 GB",
        "data_amount_mb": 2048,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 2900,
        "category": "BOOSTER",
        "description": "2 GB emergency high-speed booster for gaming & browsing.",
    },
    {
        "id": "plan_jio_6gb",
        "operator_id": "op_jio",
        "plan_code": "JIO_4G_61",
        "data_amount": "6 GB",
        "data_amount_mb": 6144,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 6100,
        "category": "WORK",
        "description": "6 GB work-from-anywhere high-speed pack.",
    },
    {
        "id": "plan_jio_12gb",
        "operator_id": "op_jio",
        "plan_code": "JIO_4G_121",
        "data_amount": "12 GB",
        "data_amount_mb": 12288,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 12100,
        "category": "WORK",
        "description": "12 GB heavy multimedia & conference pack.",
    },
    {
        "id": "plan_jio_50gb",
        "operator_id": "op_jio",
        "plan_code": "JIO_4G_301",
        "data_amount": "50 GB",
        "data_amount_mb": 51200,
        "validity_desc": "30 Days",
        "price_in_paise": 30100,
        "category": "BULK",
        "description": "50 GB standalone data booster pack valid for 30 days.",
    },

    # Airtel Plans
    {
        "id": "plan_airtel_1gb",
        "operator_id": "op_airtel",
        "plan_code": "AIR_DATA_19",
        "data_amount": "1 GB",
        "data_amount_mb": 1024,
        "validity_desc": "1 Day",
        "price_in_paise": 1900,
        "category": "BOOSTER",
        "description": "1 GB quick data pack valid till midnight.",
    },
    {
        "id": "plan_airtel_2gb",
        "operator_id": "op_airtel",
        "plan_code": "AIR_DATA_33",
        "data_amount": "2 GB",
        "data_amount_mb": 2048,
        "validity_desc": "1 Day",
        "price_in_paise": 3300,
        "category": "BOOSTER",
        "description": "2 GB high-speed daily data top-up.",
    },
    {
        "id": "plan_airtel_6gb",
        "operator_id": "op_airtel",
        "plan_code": "AIR_DATA_65",
        "data_amount": "6 GB",
        "data_amount_mb": 6144,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 6500,
        "category": "WORK",
        "description": "6 GB data add-on with validity tied to base plan.",
    },
    {
        "id": "plan_airtel_12gb",
        "operator_id": "op_airtel",
        "plan_code": "AIR_DATA_118",
        "data_amount": "12 GB",
        "data_amount_mb": 12288,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 11800,
        "category": "WORK",
        "description": "12 GB high capacity 4G/5G data pack.",
    },
    {
        "id": "plan_airtel_50gb",
        "operator_id": "op_airtel",
        "plan_code": "AIR_DATA_301",
        "data_amount": "50 GB",
        "data_amount_mb": 51200,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 30100,
        "category": "BULK",
        "description": "50 GB bulk entertainment and hotspot pack.",
    },

    # Vi Plans
    {
        "id": "plan_vi_1gb",
        "operator_id": "op_vi",
        "plan_code": "VI_DATA_19",
        "data_amount": "1 GB",
        "data_amount_mb": 1024,
        "validity_desc": "1 Day",
        "price_in_paise": 1900,
        "category": "BOOSTER",
        "description": "1 GB instant booster for emergency internet.",
    },
    {
        "id": "plan_vi_2gb",
        "operator_id": "op_vi",
        "plan_code": "VI_DATA_29",
        "data_amount": "2 GB",
        "data_amount_mb": 2048,
        "validity_desc": "2 Days",
        "price_in_paise": 2900,
        "category": "BOOSTER",
        "description": "2 GB pack valid for 2 full days.",
    },
    {
        "id": "plan_vi_6gb",
        "operator_id": "op_vi",
        "plan_code": "VI_DATA_58",
        "data_amount": "6 GB",
        "data_amount_mb": 6144,
        "validity_desc": "Active Base Plan",
        "price_in_paise": 5800,
        "category": "WORK",
        "description": "6 GB flexible add-on for video calling and work.",
    },
    {
        "id": "plan_vi_12gb",
        "operator_id": "op_vi",
        "plan_code": "VI_DATA_118",
        "data_amount": "12 GB",
        "data_amount_mb": 12288,
        "validity_desc": "28 Days",
        "price_in_paise": 11800,
        "category": "WORK",
        "description": "12 GB monthly data booster.",
    },
    {
        "id": "plan_vi_50gb",
        "operator_id": "op_vi",
        "plan_code": "VI_DATA_298",
        "data_amount": "50 GB",
        "data_amount_mb": 51200,
        "validity_desc": "28 Days",
        "price_in_paise": 29800,
        "category": "BULK",
        "description": "50 GB jumbo data bundle.",
    },

    # BSNL Plans
    {
        "id": "plan_bsnl_2gb",
        "operator_id": "op_bsnl",
        "plan_code": "BSNL_DATA_16",
        "data_amount": "2 GB",
        "data_amount_mb": 2048,
        "validity_desc": "1 Day",
        "price_in_paise": 1600,
        "category": "BOOSTER",
        "description": "2 GB daily mini booster pack.",
    },
    {
        "id": "plan_bsnl_5gb",
        "operator_id": "op_bsnl",
        "plan_code": "BSNL_DATA_48",
        "data_amount": "5 GB",
        "data_amount_mb": 5120,
        "validity_desc": "30 Days",
        "price_in_paise": 4800,
        "category": "BOOSTER",
        "description": "5 GB 30-day budget data voucher.",
    },
    {
        "id": "plan_bsnl_10gb",
        "operator_id": "op_bsnl",
        "plan_code": "BSNL_DATA_94",
        "data_amount": "10 GB",
        "data_amount_mb": 10240,
        "validity_desc": "30 Days",
        "price_in_paise": 9400,
        "category": "WORK",
        "description": "10 GB high speed data voucher.",
    },
    {
        "id": "plan_bsnl_40gb",
        "operator_id": "op_bsnl",
        "plan_code": "BSNL_DATA_251",
        "data_amount": "40 GB",
        "data_amount_mb": 40960,
        "validity_desc": "28 Days",
        "price_in_paise": 25100,
        "category": "BULK",
        "description": "40 GB work from home data special.",
    },
]


async def seed_initial_data(session: AsyncSession) -> None:
    """Seed default operators, circles, and data plans if not already present."""
    # Seed Operators
    for op_data in DEFAULT_OPERATORS:
        result = await session.execute(
            select(Operator).where(Operator.id == op_data["id"])
        )
        if not result.scalar_one_or_none():
            op = Operator(**op_data)
            session.add(op)

    # Seed Circles
    for cir_data in DEFAULT_CIRCLES:
        result = await session.execute(
            select(Circle).where(Circle.id == cir_data["id"])
        )
        if not result.scalar_one_or_none():
            cir = Circle(**cir_data)
            session.add(cir)

    await session.commit()

    # Seed Plans
    for plan_data in DEFAULT_PLANS:
        result = await session.execute(
            select(Plan).where(Plan.id == plan_data["id"])
        )
        if not result.scalar_one_or_none():
            plan = Plan(**plan_data)
            session.add(plan)

    await session.commit()
