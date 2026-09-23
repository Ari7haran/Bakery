from sqlalchemy import Column, Integer, String, Boolean
from app.core.database import Base

class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), nullable=False)
    subtitle = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=False)
    button_text = Column(String(50), default="Order Now")
    button_link = Column(String(255), default="/shop")
    is_active = Column(Boolean, default=True)
