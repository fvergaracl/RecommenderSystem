# from crud.base import CRUDBase
# from models.State import State
# from schemas.State import StateCreate, StateUpdate
# from crud.base import CRUDBase
# from sqlalchemy.orm import Session
# from sqlalchemy import and_, extract
# from typing import Any, Dict, Optional, Union, List

# from models.Recommendation import Recommendation
# from models.Cell import Cell
# from fastapi.encoders import jsonable_encoder
# from sqlalchemy import and_, extract

# class CRUDState(CRUDBase[State, StateCreate, StateUpdate]):
#         pass

#         def create_state(self, db: Session, *, obj_in: StateCreate) -> State:
#                 obj_in_data = jsonable_encoder(obj_in) 
#                 db_obj = self.model(**obj_in_data)  # type: ignore
#                 db.add(db_obj)
#                 db.commit()
#                 return db_obj
#         def get_state_from_recommendation(self,db: Session, *, recommendation_id: int)->State:
#                 return db.query(State).join(Recommendation).filter(and_(Recommendation.id==recommendation_id,Recommendation.state_id==State.id)).first()

#         def get_aceptance_state_of_cell(self,db: Session, *, cell_id:int, )-> List[State]:
#                 return db.query(State).join(Recommendation).join(Cell).filter(and_(State.state=="Acepted", Recommendation.state_id==State.id, Recommendation.cell_id == cell_id)).all()
                        

# state = CRUDState(State)
