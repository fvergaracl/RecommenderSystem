from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from sqlalchemy.orm import Session

from schemas.Slot import Slot, SlotCreate,SlotSearchResults

from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point, CellUpdate
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime
import math
from fastapi import BackgroundTasks
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

import asyncio
from fastapi_utils.session import FastAPISessionMaker
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:mypasswd@localhost:3306/SocioBee"
sessionmaker = FastAPISessionMaker(SQLALCHEMY_DATABASE_URL)

api_router_cell = APIRouter(prefix="/surfaces/{surface_id}/cells")


@api_router_cell.get("/", status_code=200, response_model=CellSearchResults)
def search_all_cells_of_surface(
    *,
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Search all cells of a surface of a campaign of a hive
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    return {"results": list(surface.cells)}

@api_router_cell.get("/{cell_id}", status_code=200, response_model=Cell)
def get_cell(
    *,
    hive_id:int,
    campaign_id:int,
    surface_id:int, 
    cell_id: int,
    db: Session = Depends(deps.get_db),
) -> Cell:
    """
    Get a cell
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    result = crud.cell.get_Cell(db=db, cell_id=cell_id, surface_id=surface_id, campaign_id=campaign_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Cell with id=={cell_id} not found"
        )
    return result


@api_router_cell.delete("/{cell_id}", status_code=204)
def delete_cell(   *,
    hive_id:int,
    campaign_id:int,
    surface_id:int, 
    cell_id: int,
    db: Session = Depends(deps.get_db),
):
    """
    Delete a cell in the database.
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    result = crud.cell.get_Cell(db=db, cell_id=cell_id)
    if  result is None:
        raise HTTPException(
            status_code=404, detail=f"Cell with id=={cell_id} not found"
        )
    crud.cell.remove(db=db, cell=result)
    return  {"ok": True}

@api_router_cell.post("/",status_code=201, response_model=Cell)
def create_cell(
    *, 
    hive_id:int,
    campaign_id:int, 
    surface_id:int,
    recipe_in: CellCreate,
    db: Session = Depends(deps.get_db),
    background_tasks: BackgroundTasks

) -> dict:
    """
    Create a new cell in a surface
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    if datetime.utcnow() > Campaign.start_datetime:
        raise HTTPException(
            status_code=400, detail=f"We can not create a surface in an active campaigm"
        )
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )
    
    centro=surface.boundary.centre
    point=recipe_in.centre
    distancia= math.sqrt((centro['Longitude'] - point['Longitude'])**2+(centro['Latitude']-point['Latitude'])**2)
    if distancia<=surface.boundary.radius:
        cell = crud.cell.create_cell(db=db, obj_in=recipe_in,surface_id=surface_id)
        background_tasks.add_task(create_slots_cell, surface,hive_id,cell.id)
        return cell
    else:
        raise HTTPException(
            status_code=400, detail=f"INVALID REQUEST: The cell does not have the centre inside the surface"
        )
   

async def create_slots_cell(surface: Surface,hive_id:int,cell_id:int):
    """
    Create all the slot of each cells of the campaign. 
    """
    await asyncio.sleep(3)
    with sessionmaker.context_session() as db:
        #       campaigns=crud.campaign.get_all_campaign(db=db)
        #       for cam in campaigns:
        # if cam.start_datetime.strftime("%m/%d/%Y, %H:%M:%S")==date_time:
        cam=crud.campaign.get_campaign(db=db,hive_id=hive_id,campaign_id=surface.campaign_id)
        duration= cam.end_datetime - cam.start_datetime 
        n_slot = int(duration.total_seconds()//cam.sampling_period)
        if duration.total_seconds() % cam.sampling_period != 0:
                n_slot = n_slot+1
        for i in range(n_slot):
            time_extra=i*cam.sampling_period
            start = cam.start_datetime + timedelta(seconds=time_extra-1)
            end = start + timedelta(seconds=cam.sampling_period)
            # for sur in cam.surfaces:
                # for cells in sur.cells:
                # for cells in cam.cells:
            slot_create =  SlotCreate(
                    cell_id=cell_id, start_datetime=start, end_datetime=end)
            slot = crud.slot.create_slot_detras(db=db, obj_in=slot_create)
            db.commit()
            if start == cam.start_datetime:
                        Cardinal_pasado = 0
                        Cardinal_actual = 0
                        init = 0
                        if cam.min_samples==0:
                                result= 0
                        else:
                                result=-Cardinal_actual/cam.min_samples                         # b = max(2, cam.min_samples - int(Cardinal_pasado))
                        # a = max(2, cam.min_samples - int(Cardinal_actual))
                        # result = math.log(a) * math.log(b, int(Cardinal_actual) + 2)
                        trendy = 0.0
                        Cell_priority = PriorityCreate(
                            slot_id=slot.id, datetime=start, temporal_priority=result, trend_priority=trendy)  # ,cell_id=cells.id)
                        priority = crud.priority.create_priority_detras(
                            db=db, obj_in=Cell_priority)
                        db.commit()

@api_router_cell.put("/{cell_id}", status_code=201, response_model=Cell)
def update_cell(
    *,
    recipe_in: CellUpdate,
    hive_id:int,
    campaign_id:int,
    surface_id:int,
    cell_id:int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update cell 
    """
    hive = crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(status_code=404, detail=f"Hive with id=={hive_id} not found"  )
    
    Campaign = crud.campaign.get_campaign(db=db, campaign_id=campaign_id, hive_id=hive_id)
    if Campaign is None:
        raise HTTPException(
            status_code=404, detail=f"Campaign with id=={campaign_id} not found"
        )
    surface = crud.surface.get_surface_by_ids(db=db, surface_id=surface_id,campaign_id=campaign_id)
    if  surface is None:
        raise HTTPException(
            status_code=404, detail=f"Surface with IDs id=={surface_id}  not found"
        )

    cell = crud.cell.get_Cell(db=db,cell_id=cell_id)
    if  cell is None:
        raise HTTPException(
            status_code=400, detail=f"Cell with id=={cell_id} not found."
        )
    # if recipe.submitter_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail=f"You can only update your recipes."
    #     )
    centro=surface.boundary.centre
    point=recipe_in.centre
    distancia= math.sqrt((centro['Longitude'] - point['Longitude'])**2+(centro['Latitude']-point['Latitude'])**2)
    if distancia<=surface.boundary.radius:
        updated_recipe = crud.cell.update(db=db, db_obj=cell, obj_in=recipe_in)
        db.commit()
        return updated_recipe
    else:
        raise HTTPException(
            status_code=400, detail=f"Invalid request."
        )


# @api_router_cell.patch("/{cell_id}", status_code=201, response_model=Cell)
# def update_parcially_cell(
#     *,
#     recipe_in: Union[CellUpdate,Dict[str, Any]],
#     hive_id:int,
#     campaign_id:int,
#     surface_id:int,
#     cell_id:int,
#     db: Session = Depends(deps.get_db)
# ) -> dict:
#     """
#      Partially Update Campaign with campaign_id 
#     """
#     cell = crud.cell.get_Cell(db=db,cell_id=cell_id)
#     # .get_campaign(db=db,hive_id=hive_id,campaign_id=campaign_id)
#     if not cell:
#         raise HTTPException(
#             status_code=400, detail=f"Recipe with hive_id=={hive_id} and campaign_id=={campaign_id} and surface_id={surface_id} not found."
#         )
#     # if recipe.submitter_id != current_user.id:
#     #     raise HTTPException(
#     #         status_code=403, detail=f"You can only update your recipes."
#     #     )

#     updated_recipe = crud.cell.update(db=db, db_obj=cell, obj_in=recipe_in)
#     db.commit()
#     return updated_recipe

