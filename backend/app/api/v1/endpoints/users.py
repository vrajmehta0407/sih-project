from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user, require_admin, get_password_hash
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import ResponseEnvelope, PaginatedResponse
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/", response_model=ResponseEnvelope[PaginatedResponse[UserResponse]], summary="List All Users (Admin only)")
def list_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
    role: Optional[str] = Query(None, description="Filter by role: inspector, admin, supervisor"),
    district: Optional[str] = Query(None, description="Filter by district"),
    search: Optional[str] = Query(None, description="Search by name, email, or badge number"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Any:
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if district:
        query = query.filter(User.jurisdiction_district.ilike(f"%{district}%"))
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.badge_number.ilike(f"%{search}%"))
        )

    total = query.count()
    items = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    pages = (total + page_size - 1) // page_size if total > 0 else 1

    return ResponseEnvelope(
        success=True,
        message="Users fetched successfully",
        data=PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
    )


@router.get("/{user_id}", response_model=ResponseEnvelope[UserResponse], summary="Get User By ID")
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this user profile."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return ResponseEnvelope(
        success=True,
        message="User details retrieved",
        data=user
    )


@router.put("/{user_id}", response_model=ResponseEnvelope[UserResponse], summary="Update User (Admin only)")
def update_user(
    user_id: str,
    user_in: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
) -> Any:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    audit_service.log(
        db=db,
        action="USER_UPDATED",
        entity_name="User",
        entity_id=user.id,
        user_id=current_admin.id,
        request=request,
        details={"updated_fields": list(update_data.keys())}
    )

    return ResponseEnvelope(
        success=True,
        message="User updated successfully",
        data=user
    )
