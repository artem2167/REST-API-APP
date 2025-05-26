from typing import List
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .database import engine, Base
from .deps import get_db, verify_api_key
from . import models, schemas, crud
from typing import List, Optional

models.Base.metadata.create_all(bind=engine)
# Создаем все таблицы при старте (если не существуют)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Directory API",
    description="REST API для справочника организаций, зданий и видов деятельности",
    version="1.0.0",
    swagger_ui_parameters={
        "docExpansion": "none",             # не разворачивать схемы по умолчанию
        "defaultModelsExpandDepth": -1,     # не показывать модель внизу
    },
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Эндпоинты ---

@app.get("/buildings", response_model=List[schemas.Building], dependencies=[Depends(verify_api_key)], )
def list_buildings(db: Session = Depends(get_db)):
    """Список всех зданий"""
    # Получаем сессию напрямую через Depends внутри функции

    return crud.list_buildings(db)

@app.get("/buildings/{building_id}/orgs", response_model=List[schemas.Organization], dependencies=[Depends(verify_api_key)], )
def orgs_by_building(
    building_id: int,
    db: Session = Depends(get_db),
):
    """Список организаций в указанном здании"""
    return crud.get_organizations_by_building(db, building_id)


@app.get("/activities/{activity_id}/orgs",
    response_model=List[schemas.Organization],
    dependencies=[Depends(verify_api_key)],
)
def orgs_by_activity(
    activity_id: int,
    db: Session = Depends(get_db),
):
    """Список организаций по виду деятельности по ID (включая вложенные)"""
    return crud.get_organizations_by_activity(db, activity_id)

@app.get(
    "/orgs/geo/radius",
    response_model=List[schemas.Organization],
    dependencies=[Depends(verify_api_key)],
)
def orgs_by_geo(
    lat: float = Query(..., description="Центр: широта"),
    lon: float = Query(..., description="Центр: долгота"),
    radius_km: Optional[float] = Query(None, description="Радиус (км)"),
    lat_min: Optional[float] = Query(None, description="BBox: мин. широта"),
    lon_min: Optional[float] = Query(None, description="BBox: мин. долгота"),
    lat_max: Optional[float] = Query(None, description="BBox: макс. широта"),
    lon_max: Optional[float] = Query(None, description="BBox: макс. долгота"),
    db: Session = Depends(get_db),
):
    """
    Если задан radius_km — ищет все организации в этот радиус от (lat,lon).
    Иначе, если указаны все четыре lat_min/lon_min/lat_max/lon_max —
    ищет организации внутри прямоугольника.
    """
    if radius_km is not None:
        return crud.get_organizations_by_geo_radius(db, lat, lon, radius_km)

    if None not in (lat_min, lon_min, lat_max, lon_max):
        return crud.get_organizations_by_geo_bbox(db, lat_min, lon_min, lat_max, lon_max)

    raise HTTPException(
        status_code=400,
        detail="Нужно указать либо radius_km, либо все четыре bbox-параметра"
    )

@app.get(
    "/orgs/by_activity",
    response_model=List[schemas.Organization],
    dependencies=[Depends(verify_api_key)],
    summary="Поиск организаций по названию вида деятельности по Name (с учётом вложений)",
)
def orgs_by_activity_name(
    activity: str = Query(..., description="Название вида деятельности, например 'Еда'"),
    db: Session = Depends(get_db),
):
    """
    Возвращает все организации, у которых в списке activity_ids
    присутствует указанный вид деятельности или любой из его потомков до 3-го уровня.
    """
    orgs = crud.get_organizations_by_activity_name(db, activity)
    return orgs



@app.get(
    "/orgs/search",
    response_model=List[schemas.Organization],
    dependencies=[Depends(verify_api_key)],
)
def search_orgs(
    name: str = Query(..., description="Часть названия организации для поиска"),
    db: Session = Depends(get_db),
):
    """Поиск организаций по названию"""
    return crud.search_organizations(db, name)

@app.get(
    "/orgs/{org_id}",
    response_model=schemas.Organization,
    dependencies=[Depends(verify_api_key)],
)
def get_org(
    org_id: int,
    db: Session = Depends(get_db),
):
    """Получить информацию об организации по ID"""
    org = crud.get_organization(db, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org
