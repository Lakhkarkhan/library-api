from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_admin
from app.models import Book, User
from app.schemas import BookCreate, BookOut

router = APIRouter(prefix="/books", tags=["books"])


def _get_book_or_404(db: Session, book_id: int) -> Book:
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Book not found")
    return book


def _commit_or_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "A book with this ISBN already exists")


@router.get("", response_model=list[BookOut])
def list_books(
    q: str | None = Query(default=None, description="Search title or author"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    stmt = select(Book).order_by(Book.id)
    if q:
        like = f"%{q}%"
        stmt = stmt.where(or_(Book.title.ilike(like), Book.author.ilike(like)))
    return db.scalars(stmt.offset(skip).limit(limit)).all()


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
def create_book(
    data: BookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = Book(**data.model_dump(), created_by=user.id)
    db.add(book)
    _commit_or_conflict(db)
    db.refresh(book)
    return book


@router.get("/{book_id}", response_model=BookOut)
def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return _get_book_or_404(db, book_id)


@router.put("/{book_id}", response_model=BookOut)
def update_book(
    book_id: int,
    data: BookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    book = _get_book_or_404(db, book_id)
    if book.created_by != user.id and user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You can only edit your own books")
    for field, value in data.model_dump().items():
        setattr(book, field, value)
    _commit_or_conflict(db)
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    db.delete(_get_book_or_404(db, book_id))
    db.commit()
