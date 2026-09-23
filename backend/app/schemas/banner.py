from pydantic import BaseModel, ConfigDict
from typing import Optional

class BannerOut(BaseModel):
    id: int
    title: str
    subtitle: Optional[str] = None
    image_url: str
    button_text: str = "Order Now"
    button_link: str = "/shop"
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
