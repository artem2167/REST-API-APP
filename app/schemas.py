from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict


class BuildingBase(BaseModel):
    address: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class Building(BuildingBase):
    id: int


class ActivityBase(BaseModel):
    name: str
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class Activity(ActivityBase):
    id: int
    children: List[Activity] = []

    model_config = ConfigDict(from_attributes=True)


class OrganizationPhone(BaseModel):
    phone_number: str

    model_config = ConfigDict(from_attributes=True)


class OrganizationBase(BaseModel):
    name: str
    building_id: int
    phone_numbers: List[str] = Field(default_factory=list)
    activity_ids: List[int] = Field(default_factory=list, max_items=3)  # ограничение 3

    model_config = ConfigDict(from_attributes=True)


class OrganizationCreate(OrganizationBase):
    pass


class Organization(OrganizationBase):
    id: int
    building: Building
    activities: List[Activity]

    model_config = ConfigDict(from_attributes=True)
