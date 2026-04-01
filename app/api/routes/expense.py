from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.expense_service import (
    approve_expense,
    create_expense,
    delete_expense,
    get_expense_by_id,
    get_expenses_for_user,
    reject_expense,
    submit_expense,
    update_expense,
)

router = APIRouter()


@router.post("/", response_model=ExpenseResponse)
def create_expense_route(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_expense(
        db=db,
        title=expense.title,
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        owner_id=current_user.id,
    )


@router.get("/", response_model=list[ExpenseResponse])
def get_my_expenses_route(
    category: str | None = Query(default=None),
    min_amount: float | None = Query(default=None),
    max_amount: float | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_expenses_for_user(
        db=db,
        current_user=current_user,
        category=category,
        min_amount=min_amount,
        max_amount=max_amount,
        page=page,
        size=size,
    )


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense_route(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_expense_by_id(db, expense_id, current_user)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense_route(
    expense_id: int,
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return update_expense(
        db,
        expense_id,
        expense.model_dump(),
        current_user,
    )


@router.delete("/{expense_id}")
def delete_expense_route(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return delete_expense(db, expense_id, current_user)

@router.post("/{expense_id}/submit", response_model=ExpenseResponse)
def submit_expense_route(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return submit_expense(db, expense_id, current_user)



@router.post("/{expense_id}/approve", response_model=ExpenseResponse)
def approve_expense_route(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return approve_expense(db, expense_id, current_user)


@router.post("/{expense_id}/reject", response_model=ExpenseResponse)
def reject_expense_route(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return reject_expense(db, expense_id, current_user)