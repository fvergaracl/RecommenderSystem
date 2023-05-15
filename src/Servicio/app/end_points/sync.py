from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends

from typing import Optional, Any, List
from pathlib import Path
from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate,CampaignSing
from schemas.Slot import Slot, SlotCreate,SlotSearchResults
from schemas.Hive import Hive, HiveCreate, HiveSearchResults
from schemas.Member import Member,MemberCreate,MemberSearchResults
from end_points.funtionalities import create_cells_for_a_surface,  create_slots_campaign
from schemas.Campaign_Member import Campaign_Member,Campaign_MemberCreate,Campaign_MemberSearchResults
from schemas.newMember import NewMemberBase
from datetime import datetime, timedelta
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from datetime import timezone
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from schemas.Recommendation import Recommendation, RecommendationCreate, RecommendationSearchResults, RecommendationUpdate
from crud import crud_cell
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
import deps
import crud
from datetime import datetime
import math
import numpy as np
from io import BytesIO
from typing_extensions import TypedDict
from fastapi import FastAPI, APIRouter, Query, HTTPException, Request, Depends
from fastapi.templating import Jinja2Templates
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from sqlalchemy.orm import Session
from schemas.Measurement import Measurement, MeasurementCreate, MeasurementSearchResults
from schemas.Boundary import Boundary, BoundaryCreate, BoundarySearchResults,BoundaryBase_points
from schemas.Device import Device, DeviceCreate, DeviceUpdate
from schemas.Campaign import CampaignSearchResults, Campaign, CampaignCreate, CampaignUpdate
from schemas.Slot import Slot, SlotCreate, SlotSearchResults
from schemas.Campaign_Member import Campaign_Member, Campaign_MemberCreate
from schemas.BeeKeeper import BeeKeeper,BeeKeeperUpdate, BeeKeeperCreate
from schemas.Hive_Member import Hive_MemberSearchResults, Hive_MemberBase, Hive_MemberCreate
from schemas.Recommendation import Recommendation, RecommendationCreate
from schemas.Member import Member, NewMembers, MemberUpdate
from schemas.Hive import HiveUpdate
from schemas.Priority import Priority, PriorityCreate, PrioritySearchResults
from schemas.Cell import Cell, CellCreate, CellSearchResults, Point
from schemas.Surface import SurfaceSearchResults, Surface, SurfaceCreate
from schemas.Member_Device import Member_DeviceCreate
import deps
import crud
from datetime import datetime, timedelta
import math 
from vincenty import vincenty
import numpy as np
from numpy import sin, cos, arccos, pi, round
from end_points.funtionalities import create_List_of_points_for_a_boundary

from math import sin, cos, atan2, sqrt, radians, degrees, asin


api_router_sync = APIRouter(prefix="/sync")

@api_router_sync.post("/points/", status_code=201, response_model=List)
def create_points_of_campaign(
    *,
    boundary: BoundaryBase_points,
    # db: Session = Depends(deps.get_db),
) -> dict:
    """
    Generate the points of a campaign.
    """
    centre = boundary.centre
    radius = boundary.radius
    cells_distance=boundary.cells_distance
    return create_List_of_points_for_a_boundary(cells_distance=cells_distance,centre=centre, radius=radius)
   
    
@api_router_sync.put("/hives/{hive_id}", status_code=201, response_model=Hive)
def update_hive(*,
                recipe_in: HiveUpdate,
                hive_id: int,
                db: Session = Depends(deps.get_db),
                ) -> dict:
    """
    Update Hive in the database.
    """
    hive = crud.hive.get(db, id=hive_id)
    
    if hive is None:
            hiveCreate=HiveCreate(city=recipe_in.city, beekeeper_id=recipe_in.beekeeper_id,name=recipe_in.name)
            return crud.hive.create_hive(db=db, obj_in=hiveCreate,id=hive_id)
    updated_hive = crud.hive.update(db=db, db_obj=hive, obj_in=recipe_in)
    return updated_hive
                            

@api_router_sync.put("/beekeepers/{beekeeper_id}", status_code=201, response_model=BeeKeeper)
def put_a_beekeeper(
    *,
    beekeeper_id: int,
    recipe_in: BeeKeeperUpdate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    Update a BeeKeeper
    """
    beekeeper = crud.beekeeper.get_by_id(db=db, id=beekeeper_id)
    
    if beekeeper is None:
        beecreater=BeeKeeperCreate(name=recipe_in.name, surname=recipe_in.surname, age=recipe_in.age, gender=recipe_in.gender,birthday=recipe_in.birthday,city=recipe_in.city,mail=recipe_in.mail,real_user=recipe_in.real_user )
        return crud.beekeeper.create_beekeeper(db=db,obj_in=beecreater,id=beekeeper_id)
    updated_beekeeper = crud.beekeeper.update(
            db=db, db_obj=beekeeper, obj_in=recipe_in)
    db.commit()
    return updated_beekeeper
                            
@api_router_sync.put("/devices", status_code=201, response_model=List[Device])
def update_devices(
    *,
    recipe_in: List[Device],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    synchronization the devices
    """
    result=[]
    for element in recipe_in:
        device_id=element.id
        device_db= crud.device.get(db=db, id=device_id)
        if device_db is None:
            device_create=DeviceCreate(description=element.description,year=element.year, brand=element.brand,model=element.model)
            device_db_new=crud.device.create_device(db=db, obj_in=device_create,id=device_id)
        
            result.append(device_db_new)
        else:
            device_update=DeviceUpdate(description=element.description,year=element.year, brand=element.brand,model=element.model)
            device_db_new=crud.member.update(db=db,db_obj=device_db,obj_in=device_update)
            
            result.append(device_db_new)
    return result


                
@api_router_sync.put("/hives/{hive_id}/members/", status_code=201, response_model=List[NewMembers])
def update_members(
    hive_id:int,
    recipe_in: List[NewMembers],
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    synchronization members 
    """
    result=[]
    hive= crud.hive.get(db=db, id=hive_id)
    if hive is None:
        raise HTTPException(
                status_code=404, detail=f"Hive with id=={hive_id} not found"
            )
    for element in recipe_in:
        role=element.role
        member=element.member
        member_db= crud.member.get_by_id(db=db, id=member.id)
        if member_db is None:
            member_create=MemberCreate(name=member.name, surname=member.surname,age=member.age, gender=member.gender,city=member.city,mail=member.mail, birthday=member.birthday,real_user=member.real_user)
            member_db_new=crud.member.create_member(db=db, obj_in=member_create,id=member.id)
            
            hiveCreate=Hive_MemberCreate(hive_id=hive_id,member_id=member_db_new.id)
            hive_member=crud.hive_member.create_hiveMember(db=db,obj_in=hiveCreate,role=role)
            result.append(NewMembers(member=member_db_new,role=role))
        else:
            member_update=MemberUpdate(name=member.name, surname=member.surname,age=member.age, gender=member.gender,city=member.city,mail=member.mail, birthday=member.birthday,real_user=member.real_user)
            member_db_new=crud.member.update(db=db,db_obj=member_db,obj_in=member_update)
            
            hive_member=crud.hive_member.get_by_member_hive_id(db=db, hive_id=hive_id,member_id=member_db_new.id)
            if hive_member is None:
                hiveCreate=Hive_MemberCreate(hive_id=hive_id,member_id=member_db_new.id)
                hive_member=crud.hive_member.create_hiveMember(db=db,obj_in=hiveCreate,role=role)
                result.append(NewMembers(member=member_db_new,role=role))
            else:
                if(hive_member.role!=role):
                    crud.hive_member.update(db=db, db_obj=hive_member,obj_in={"role":role})
                
                result.append(NewMembers(member=member_db_new,role=role))
    return result


                
            
@api_router_sync.put("/hives/{hive_id}/campaigns/{campaign_id}/devices",  status_code=201, response_model=Device)   
def post_members_devices(
    hive_id:int,
    campaign_id:int,
    memberDevice:Member_DeviceCreate,
    db: Session = Depends(deps.get_db),
) -> dict:
    """
    synchronization the member devices. 
    """ 
    member_device_=crud.member_device.get_by_member_id(db=db, member_id=memberDevice.member_id)
    #member_id no existe en la tabla
    if member_device_ is None:
        MEmber_of_device= crud.member_device.get_by_device_id(db=db, device_id=memberDevice.device_id)
        if MEmber_of_device is None:
            #member_id and device_id not in the table
            crud.member_device.create(db=db, obj_in=memberDevice)
            return crud.device.get(db=db, id=memberDevice.device_id)
        else:
            #member_id not in the table and device_id yes
            crud.member_device.remove(db=db,Member_device=MEmber_of_device)
            db.commit()
            crud.member_device.create(db=db, obj_in=memberDevice)
            return crud.device.get(db=db, id=memberDevice.device_id)

    else:
            #member_id in the table. 
            MEmber_of_device= crud.member_device.get_by_device_id(db=db, device_id=memberDevice.device_id)
            if MEmber_of_device is None:
                    crud.member_device.update(db=db, db_obj=member_device_, obj_in=memberDevice)
                    return crud.device.get(db=db, id=memberDevice.device_id)
                
            else:
                if member_device_.device_id==memberDevice.device_id:
                    return crud.device.get(db=db, id=memberDevice.device_id)
                else: 
                    crud.member_device.remove(db=db,Member_device=MEmber_of_device)
                    crud.member_device.update(db=db, db_obj=member_device_, obj_in=memberDevice)
                    return crud.device.get(db=db, id=memberDevice.device_id)


                
                



######  PUT Endpoint ######
@api_router_sync.put("/hives/{hive_id}/campaigns/{campaign_id}", status_code=201, response_model=Campaign)
def update_campaign(
    *,
    recipe_in: CampaignSing,
    hive_id: int,
    campaign_id: int,
    db: Session = Depends(deps.get_db)
) -> dict:
    """
    Update Campaign 
    """
    campaign_metadata=recipe_in.campaignMetadata
    boundary_campaign=recipe_in.boundary_metadata
    
    #Get the hive
    hive = crud.hive.get(db=db, id=hive_id)
    #Verify if the hive exist
    if hive is None:
        raise HTTPException(
            status_code=404, detail=f"Hive with id=={hive_id} not found"
        )
    #Get the campaign
    campaign = crud.campaign.get_campaign(
        db=db, hive_id=hive_id, campaign_id=campaign_id)
    #Verify if the campaign exist
    if (campaign is None):  
            campaign_metadata= recipe_in.campaignMetadata     
                #Change the timezone of the start and end date
            campaign_metadata.start_datetime = campaign_metadata.start_datetime.replace(
                tzinfo=timezone.utc)
            campaign_metadata.end_datetime = campaign_metadata.end_datetime.replace(
                tzinfo=timezone.utc)
            
            #Obtein the hive of the campaign and verify if the hive exists
            hive = crud.hive.get(db=db, id=hive_id)
            if hive is None:
                raise HTTPException(
                    status_code=404, detail=f"Hive with id=={hive_id} not found"
                )

            #Obtein the QueenBee of the hive and verify if the hive has a QueenBee
            QueenBee = crud.hive_member.get_by_role_hive(
                db=db, hive_id=hive_id, role="QueenBee")
            if QueenBee is None:
                raise HTTPException(
                    status_code=404, detail=f"This Hive haven`t a QueenBee"
                )
            
            """
            Verify if the sampling period is 0 -> This means that you only want one slot per all campaign 
            and the users has to take as much measurements as they can in this period. I recomended that the 
            duration of this type of campaigns was short. 
            In this case the sampling_peirod ha to be the all campaing duration!!!! -> that its only one slot. 
            """
            if campaign_metadata.sampling_period == 0:
                duration = campaign_metadata.end_datetime - campaign_metadata.start_datetime        
                campaign_metadata.sampling_period = duration.total_seconds()
            
            """
            Verify all case related with the start and end datetime of the campaign
                - The end time cannot be earlier or same than the initial time. (corect: start < end)
                - The sampling period cannot be longer than the campaign duration. (Correct: start + sampling_period <= end) 
            (In this comparation i can not to change the time zone because the start and end time are already in UTC, and  plus a timedelta  not change the timezone)
            """
            if campaign_metadata.end_datetime <= campaign_metadata.start_datetime:
                raise HTTPException(
                    status_code=400, detail=f"the end time cannot be earlier or same than the initial time."
                )
            if campaign_metadata.start_datetime + timedelta(seconds=campaign_metadata.sampling_period) > campaign_metadata.end_datetime:
                raise HTTPException(
                    status_code=400, detail=f"Error with the sampling period"
                )
            
            """
            Create the campaign, the Campaign_member table, athe boundary and the Surface
                NOTE: Add the members of the hive to the Campaign_member table to create a register. This table are 
                    a temporal register of the member of the campaign, so we can find if a concrete member was in a
                    campaign even when this member go out of this hive. 
            """
            #Create the campaign
            Campaign = crud.campaign.create_cam(
                db=db, obj_in=campaign_metadata, hive_id=hive_id, id=campaign_id)
            
            #Add the QueenBee to the campaign in the Campaign_Member table
            role = Campaign_MemberCreate(role="QueenBee")
            role_queenBee = crud.campaign_member.create_Campaign_Member(
                db=db, obj_in=role, campaign_id=Campaign.id, member_id=QueenBee.member_id)
            #Obtain the Hive_Members of a hive -> obtain the members of the hive! 
            hive_members = crud.hive_member.get_by_hive_id(db=db, hive_id=Campaign.hive_id)
            for i in hive_members:
                #Verify that I dont register the queen bee again
                if i.member_id != QueenBee.member_id:
                    #Add the member with the role that this member has in the hive. 
                    role = Campaign_MemberCreate(role=i.role)
                    role_WB = crud.campaign_member.create_Campaign_Member(
                        db=db, obj_in=role, campaign_id=Campaign.id, member_id=i.member_id)
            if boundary_campaign is None:
                raise HTTPException(
                    status_code=400, detail=f"boundary is needed"
                )
            # Create the boundary
            boundary_campaign = crud.boundary.create_boundary(
                db=db, obj_in=boundary_campaign)
            #Create surface
            surface_create = SurfaceCreate(boundary_id=boundary_campaign.id)
            Surface = crud.surface.create_sur(
                db=db, campaign_id=Campaign.id, obj_in=surface_create)

        
            #General variables
            centre = boundary_campaign.centre
            radius = boundary_campaign.radius    
            create_cells_for_a_surface(db=db,surface=Surface, campaign=Campaign,centre=centre, radius=radius) 
            
            """
            When the Cells are created we create the slots of each cell in the background due to a campaign can have too much slots.
                EXAMPLE: If we have 2 hour of campaign duration and a sampling period of 1 hour -> then per 1 cell we have 2 slots. 
            """
            create_slots_campaign(db=db, cam=Campaign)
            return Campaign

    if campaign_metadata.start_datetime != campaign.start_datetime or campaign_metadata.end_datetime != campaign.end_datetime or campaign_metadata.cells_distance != campaign.cells_distance or campaign_metadata.sampling_period != campaign.sampling_period or campaign_metadata.min_samples != campaign.min_samples:
        #Verify if the campaign is active (time)
        if datetime.utcnow() > campaign.start_datetime:
            raise HTTPException(
                status_code=401, detail=f"An active campaign cannot be modified."
            )
        else:
            #Change the timezone of the start and end date
            campaign_metadata.start_datetime = campaign_metadata.start_datetime.replace(
                tzinfo=timezone.utc)
            #Change the timezone of the start and end date
            campaign_metadata.end_datetime = campaign_metadata.end_datetime.replace(
                tzinfo=timezone.utc)
            #Update the campaign
            campaign = crud.campaign.update(
                db=db, db_obj=campaign, obj_in=campaign_metadata)
            #Remove the cells, slot, boundary and surface
            if boundary_campaign is not None:
                raise HTTPException(
                    status_code=400, detail=f"boundary is not needed"
                )
            list_of_surfaces=campaign.surfaces
            for i in list_of_surfaces:
                centre = i.boundary.centre
                radius = i.boundary.radius
                #Remove the surface -> implicity this remove the boundary and the cells and slots.
                crud.surface.remove(db=db, surface=i)
                db.commit()
                #Create the surface, boundary and cells
                boundary_create = BoundaryCreate(centre=centre, radius=radius)
                boundary = crud.boundary.create_boundary(db=db, obj_in=boundary_create)
                surface_create = SurfaceCreate(boundary_id=boundary.id)
                Surface = crud.surface.create_sur(
                    db=db, campaign_id=campaign.id, obj_in=surface_create)
                #Create the cells
                create_cells_for_a_surface(db=db,surface=Surface, campaign=campaign,centre=centre, radius=radius) 

                
                """
                When the Cells are created we create the slots of each cell in the background due to a campaign can have too much slots.
                    EXAMPLE: If we have 2 hour of campaign duration and a sampling period of 1 hour -> then per 1 cell we have 2 slots. 
                """
                create_slots_campaign(db=db, cam=campaign)
            return campaign
    else:
        campaign = crud.campaign.update(db=db, db_obj=campaign, obj_in=campaign_metadata)
    db.commit()
    return campaign