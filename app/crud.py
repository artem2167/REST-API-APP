from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from . import models, schemas
from typing import List
import math

# 1) Список всех зданий
def list_buildings(db: Session) -> List[models.Building]:
    return db.query(models.Building).all()

# 2) Все организации в конкретном здании
def get_organizations_by_building(db: Session, building_id: int) -> List[models.Organization]:
    return (
        db.query(models.Organization)
        .filter(models.Organization.building_id == building_id)
        .all()
    )

# 3) Вспомогательная: рекурсивный сбор всех id видов деятельности до глубины 3
def _collect_activity_ids(db: Session, root_id: int, max_depth: int = 3) -> List[int]:
    ids = {root_id}
    frontier = {root_id}
    depth = 1
    while frontier and depth < max_depth:
        children = (
            db.query(models.Activity.id)
            .filter(models.Activity.parent_id.in_(frontier))
            .all()
        )
        frontier = {c.id for c in children}
        ids |= frontier
        depth += 1
    return list(ids)

# 4) Все организации по виду деятельности ID (включая вложенные)
def get_organizations_by_activity(db: Session, activity_id: int) -> List[models.Organization]:
    activity_ids = _collect_activity_ids(db, activity_id)
    return (
        db.query(models.Organization)
        .join(models.organization_activities)
        .filter(models.organization_activities.c.activity_id.in_(activity_ids))
        .all()
    )

#4.1) Все организации по виду деятельности NAME (включая вложенные)
def get_organizations_by_activity_name(db: Session, activity_name: str) -> list[models.Organization]:
    # 1) находим корневую активность по имени
    root = db.query(models.Activity).filter(models.Activity.name == activity_name).first()
    if not root:
        return []
    # 2) собираем её id + вложения (до 3 уровней)
    activity_ids = _collect_activity_ids(db, root.id, max_depth=3)
    # 3) возвращаем организации, у которых есть любая из этих активностей
    return (
        db.query(models.Organization)
          .join(models.organization_activities)
          .filter(models.organization_activities.c.activity_id.in_(activity_ids))
          .all()
    )

# 5) Поиск по названию (LIKE ...)
def search_organizations(db: Session, name: str) -> List[models.Organization]:
    pattern = f"%{name}%"
    return (
        db.query(models.Organization)
        .filter(models.Organization.name.ilike(pattern))
        .all()
    )

# 6) Организации в радиусе от точки (Haversine)
def get_organizations_by_geo_radius(
    db: Session, lat: float, lon: float, radius_km: float
) -> List[models.Organization]:
    # формула расстояния в километрах
    # NOTE: для больших объёмов лучше выносить это в БД через SQL-функции
    orgs = db.query(models.Organization).join(models.Building).all()
    result = []
    for org in orgs:
        dlat = math.radians(org.building.latitude - lat)
        dlon = math.radians(org.building.longitude - lon)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat))
            * math.cos(math.radians(org.building.latitude))
            * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = 6371.0 * c
        if distance <= radius_km:
            result.append(org)
    return result

# 7) Организации в прямоугольнике (bbox)
def get_organizations_by_geo_bbox(
    db: Session, lat_min: float, lon_min: float, lat_max: float, lon_max: float
) -> List[models.Organization]:
    return (
        db.query(models.Organization)
        .join(models.Building)
        .filter(
            models.Building.latitude.between(lat_min, lat_max),
            models.Building.longitude.between(lon_min, lon_max),
        )
        .all()
    )

# 8) Информация об организации по id
def get_organization(db: Session, org_id: int) -> models.Organization:
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()
