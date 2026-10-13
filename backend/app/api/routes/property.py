from fastapi import APIRouter

from app.schemas.property import PropertyInfoResponse
from app.services.property import load_property_info

router = APIRouter(prefix="/api/property", tags=["property"])


@router.get("", response_model=PropertyInfoResponse)
async def get_property_info() -> PropertyInfoResponse:
    """The full Meridian property information sheet, grouped by section."""
    return load_property_info()
