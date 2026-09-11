from pydantic import BaseModel

from app.models.category import CategoryType

class CategoryResponse(BaseModel):
    id: int
    name: str
    type: CategoryType
    is_active: bool

    model_config = {
        "from_attributes": True,
    }