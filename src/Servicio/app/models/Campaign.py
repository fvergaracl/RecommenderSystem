
from sqlalchemy import Integer, String, Column, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from db.base_class import Base
from models.Hive import Hive
from models.Member import Member


class Campaign(Base):
    __tablename__='Campaign'
    hive_id=Column(Integer,ForeignKey(Hive.id, ondelete="CASCADE"),primary_key=True)
    id=Column(Integer, unique=True, primary_key=True, autoincrement=True) 
    creator_id=Column(Integer,ForeignKey(Member.id, ondelete="CASCADE"))
    city=Column(String, nullable=False)
    start_timestamp=Column(DateTime)
    cells_distance=Column(Integer)
    min_samples=Column(Integer,default=12)
    sampling_period=Column(Integer,default=3600)
    campaign_duration=Column(Integer, default=3600*24*14)
    hypothesis = Column(String ) 
    surfaces=relationship("Surface",cascade="all, delete")
    # cells=relationship("Cell")


