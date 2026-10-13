from pydantic import BaseModel


class PropertyItem(BaseModel):
    name: str
    details: str


class PropertySection(BaseModel):
    title: str
    items: list[PropertyItem]


class PropertyInfoResponse(BaseModel):
    sections: list[PropertySection]
