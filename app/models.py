from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Связующая таблица организация – вид деятельности
organization_activities = Table(
    'organization_activities', Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('activity_id',     Integer, ForeignKey('activities.id'),     primary_key=True),
)

class Building(Base):
    __tablename__ = 'buildings'
    id        = Column(Integer, primary_key=True, index=True)
    address   = Column(String, nullable=False)
    latitude  = Column(Float,  nullable=False)
    longitude = Column(Float,  nullable=False)
    organizations = relationship("Organization", back_populates="building")

class Activity(Base):
    __tablename__ = 'activities'
    id        = Column(Integer, primary_key=True, index=True)
    name      = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('activities.id', ondelete='SET NULL'))
    parent    = relationship("Activity", remote_side=[id], back_populates="children")
    children  = relationship("Activity", back_populates="parent", cascade="all, delete")
    organizations = relationship("Organization", secondary=organization_activities, back_populates="activities")

class Organization(Base):
    __tablename__ = 'organizations'
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String, nullable=False, index=True)
    building_id = Column(Integer, ForeignKey('buildings.id'))
    building    = relationship("Building", back_populates="organizations")
    phones      = relationship("OrganizationPhone", back_populates="organization", cascade="all, delete")
    activities  = relationship("Activity", secondary=organization_activities, back_populates="organizations")

    @property
    def phone_numbers(self) -> list[str]:
        # Pydantic найдёт это свойство и отдаст список строк
        return [p.phone_number for p in self.phones]
class OrganizationPhone(Base):
    __tablename__ = 'organization_phone_numbers'
    id              = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'))
    phone_number    = Column(String, nullable=False)
    organization    = relationship("Organization", back_populates="phones")
