from pydantic import BaseModel, ConfigDict, Field


class ExpenseCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    category: str = Field(..., min_length=1, max_length=50)
    description: str | None = None


class ExpenseResponse(BaseModel):
    id: int
    title: str
    amount: float
    category: str
    description: str | None
    status: str
    owner_id: int

    model_config = ConfigDict(from_attributes=True)