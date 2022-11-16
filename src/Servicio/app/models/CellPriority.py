
from sqlalchemy import (Column, DateTime, Float, ForeignKey,
                        Integer)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Float
from db.base_class import Base
from models.Cell import Cell
from models.CellMeasurement import CellMeasurement
# sys.path.append("/home/ubuntu/carpeta_compartida_docker/RecommenderSystem/src")
# print(sys.path)



class CellPriority(Base):
    __tablename__='CellPriority'
    timestamp=Column(DateTime, primary_key=True)
    cell_id=Column(Integer, ForeignKey(Cell.id),primary_key=True)
    temporal_priority=Column(Float) 
    trend_priority=Column(Float)
        
   
    # cells = relationship("Cell", back_populates="priority")