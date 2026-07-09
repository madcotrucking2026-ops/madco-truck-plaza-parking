from pydantic import BaseModel


class SearchResultItem(BaseModel):
    type: str  # "company" | "vehicle"
    label: str
    sublabel: str | None = None
    query: str
