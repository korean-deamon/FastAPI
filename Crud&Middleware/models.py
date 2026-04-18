from sqlalchemy import Column, String, Integer, Float
from db import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), nullable=False, unique=True, index=True)
    description = Column(String(200), nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)