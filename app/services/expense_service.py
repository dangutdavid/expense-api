from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.models.user import User


def create_expense(
    db: Session,
    title: str,
    amount: float,
    category: str,
    description: str | None,
    owner_id: int,
):
    expense = Expense(
        title=title,
        amount=amount,
        category=category,
        description=description,
        status="draft",
        owner_id=owner_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expenses_for_user(
    db: Session,
    current_user: User,
    category: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    page: int = 1,
    size: int = 10,
):
    query = db.query(Expense)

    if current_user.role != "admin":
        query = query.filter(Expense.owner_id == current_user.id)

    if category:
        query = query.filter(Expense.category == category)

    if min_amount is not None:
        query = query.filter(Expense.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(Expense.amount <= max_amount)

    offset = (page - 1) * size
    return query.offset(offset).limit(size).all()


def get_expense_by_id(db: Session, expense_id: int, current_user: User):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if current_user.role != "admin" and expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this expense")

    return expense


def update_expense(db: Session, expense_id: int, data: dict, current_user: User):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if current_user.role != "admin" and expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if expense.status != "draft" and current_user.role != "admin":
        raise HTTPException(status_code=400, detail="Only draft expenses can be edited")

    for key, value in data.items():
        setattr(expense, key, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int, current_user: User):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if current_user.role != "admin" and expense.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    if expense.status != "draft" and current_user.role != "admin":
        raise HTTPException(status_code=400, detail="Only draft expenses can be deleted")

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted"}


def submit_expense(db: Session, expense_id: int, current_user: User):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")

    if expense.status != "draft":
        raise HTTPException(status_code=400, detail="Only draft expenses can be submitted")

    expense.status = "submitted"
    db.commit()
    db.refresh(expense)
    return expense


def approve_expense(db: Session, expense_id: int, current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted expenses can be approved")

    expense.status = "approved"
    db.commit()
    db.refresh(expense)
    return expense


def reject_expense(db: Session, expense_id: int, current_user: User):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    expense = db.query(Expense).filter(Expense.id == expense_id).first()

    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    if expense.status != "submitted":
        raise HTTPException(status_code=400, detail="Only submitted expenses can be rejected")

    expense.status = "rejected"
    db.commit()
    db.refresh(expense)
    return expense