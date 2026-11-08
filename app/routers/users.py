from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_admin
from app.models import User
from app.schemas import RoleUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/{user_id}/role", response_model=UserOut)
def set_role(
    user_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    user.role = data.role
    db.commit()
    db.refresh(user)
    return user
