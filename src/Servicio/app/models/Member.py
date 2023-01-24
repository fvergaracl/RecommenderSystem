

from sqlalchemy import Integer, String, Column, Boolean, ForeignKey,Boolean
from sqlalchemy.orm import relationship

from db.base_class import Base
from models.Device import Device
from sqlalchemy import Integer, Enum





class Member(Base):
    __tablename__='Member'
    mail=Column(String, nullable=False)
    id=Column(Integer, primary_key=True, index=True, unique=True,  autoincrement=True, nullable=False)
    name=Column(String,nullable=True)
    age=Column(Integer,nullable=True)
    surname=Column(String,nullable=True)
    city=Column(String,nullable=True)
    gender=Column(Enum("NoBinary","Male","Female",'I dont want to answer'),nullable=False)
    real_user=Column(Boolean,default=True)
    # device_id=Column(Integer,ForeignKey(Device.id, ondelete='CASCADE'))
    
    Measurements=relationship("Measurement",cascade="all, delete")
    roles=relationship("Role", back_populates="member",cascade="all, delete")
    # campaign_creator= relationship("Campaign",cascade="all, delete")

    