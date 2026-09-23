from typing import List
from sqlalchemy.orm import Session
from app.repositories.base_repository import BaseRepository
from app.models.banner import Banner

class BannerRepository(BaseRepository[Banner]):
    def __init__(self, db: Session):
        super().__init__(Banner, db)

    def list_active(self) -> List[Banner]:
        return self.db.query(Banner).filter(Banner.is_active == True).all()
