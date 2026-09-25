from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.repositories.coupon_repository import CouponRepository
from app.services.coupon_service import CouponService
from app.schemas.coupon import (
    CouponApply,
    CouponCreate,
    CouponUpdate,
    CouponOut,
    CouponValidationResult,
)

router = APIRouter(tags=["Coupons & Offers"])

def get_coupon_service(db: Session = Depends(get_db)) -> CouponService:
    return CouponService(CouponRepository(db))

# ----------------- Customer Endpoints -----------------

@router.get("/coupons", response_model=List[CouponOut])
def list_active_coupons(service: CouponService = Depends(get_coupon_service)):
    """List all active, unexpired coupons available for customers."""
    return service.list_active_coupons()

@router.post("/coupons/validate", response_model=CouponValidationResult)
def validate_coupon_endpoint(
    data: CouponApply,
    service: CouponService = Depends(get_coupon_service)
):
    """Validate a coupon against an order subtotal amount."""
    return service.validate_coupon(data.code, data.order_amount)

# ----------------- Admin Management Endpoints -----------------

@router.get("/admin/coupons", response_model=List[CouponOut])
def admin_list_all_coupons(
    skip: int = Query(0, ge=0, description="Items to skip"),
    limit: int = Query(50, ge=1, le=100, description="Items to return"),
    admin: User = Depends(get_current_admin),
    service: CouponService = Depends(get_coupon_service)
):
    """Admin: List all coupons with pagination."""
    return service.list_all_coupons(skip=skip, limit=limit)

@router.post("/admin/coupons", response_model=CouponOut, status_code=status.HTTP_201_CREATED)
def admin_create_coupon(
    coupon_in: CouponCreate,
    admin: User = Depends(get_current_admin),
    service: CouponService = Depends(get_coupon_service)
):
    """Admin: Create a new promotional coupon."""
    return service.create_coupon(coupon_in)

@router.get("/admin/coupons/{coupon_id}", response_model=CouponOut)
def admin_get_coupon(
    coupon_id: int = Path(..., gt=0, description="Coupon ID must be greater than zero"),
    admin: User = Depends(get_current_admin),
    service: CouponService = Depends(get_coupon_service)
):
    """Admin: Retrieve coupon details by ID."""
    return service.get_coupon(coupon_id)

@router.put("/admin/coupons/{coupon_id}", response_model=CouponOut)
def admin_update_coupon(
    coupon_id: int = Path(..., gt=0, description="Coupon ID must be greater than zero"),
    coupon_in: CouponUpdate = ...,
    admin: User = Depends(get_current_admin),
    service: CouponService = Depends(get_coupon_service)
):
    """Admin: Update coupon properties."""
    return service.update_coupon(coupon_id, coupon_in)

@router.delete("/admin/coupons/{coupon_id}")
def admin_delete_coupon(
    coupon_id: int = Path(..., gt=0, description="Coupon ID must be greater than zero"),
    admin: User = Depends(get_current_admin),
    service: CouponService = Depends(get_coupon_service)
):
    """Admin: Delete a coupon."""
    service.delete_coupon(coupon_id)
    return {"message": "Coupon deleted successfully"}
