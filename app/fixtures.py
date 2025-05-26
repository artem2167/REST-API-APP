# app/fixtures.py

from .database import SessionLocal, engine, Base
from . import models

Base.metadata.create_all(bind=engine)

def run():
    db = SessionLocal()

    # Очистка таблиц
    db.execute(models.organization_activities.delete())
    db.query(models.OrganizationPhone).delete()
    db.query(models.Organization).delete()
    db.query(models.Activity).delete()
    db.query(models.Building).delete()
    db.commit()

    # Новая, более глубокая иерархия видов деятельности
    food      = models.Activity(name="Еда")
    meat      = models.Activity(name="Мясная продукция", parent=food)
    dairy     = models.Activity(name="Молочная продукция", parent=food)
    cheese    = models.Activity(name="Сыры", parent=dairy)          # уровень 3
    artisan   = models.Activity(name="Авторские сыры", parent=cheese) # уровень 4 – _не попадёт_, т.к. max_depth=3

    cars      = models.Activity(name="Автомобили")
    trucks    = models.Activity(name="Грузовые", parent=cars)
    spare     = models.Activity(name="Запчасти", parent=trucks)       # уровень 3
    acc       = models.Activity(name="Аксессуары", parent=trucks)
    passenger = models.Activity(name="Легковые", parent=cars)
    spare2    = models.Activity(name="Запчасти легковые", parent=passenger)
    acc2      = models.Activity(name="Аксессуары легковые", parent=passenger)

    db.add_all([food, meat, dairy, cheese, artisan,
                cars, trucks, spare, acc, passenger, spare2, acc2])
    db.commit()

    # Здания
    b1 = models.Building(address="г. Москва, ул. Пушкина, д. 10", latitude=55.75, longitude=37.61)
    b2 = models.Building(address="г. Казань, ул. Баумана, д. 15", latitude=55.79, longitude=49.12)
    db.add_all([b1, b2])
    db.commit()

    # Организации
    o1 = models.Organization(name="Молочный рай", building=b1)
    o1.phones = [
        models.OrganizationPhone(phone_number="8-800-123-45-67"),
        models.OrganizationPhone(phone_number="8-800-123-45-68"),
        models.OrganizationPhone(phone_number="8-800-123-45-69"),
    ]
    o1.activities = [dairy]

    o2 = models.Organization(name="Сыроварня Art", building=b1)
    o2.phones = [
        models.OrganizationPhone(phone_number="8-800-765-43-21"),
        models.OrganizationPhone(phone_number="8-800-765-43-22"),
    ]
    o2.activities = [artisan]  # уровень 4 — не найдётся при поиске корня “Еда”

    o3 = models.Organization(name="ProАвто", building=b2)
    o3.phones = [
        models.OrganizationPhone(phone_number="8-800-111-22-33"),
        models.OrganizationPhone(phone_number="8-800-111-22-34"),
    ]

    o4 = models.Organization(name="ProМясо", building=b2)
    o4.phones = [
        models.OrganizationPhone(phone_number="8-800-111-22-33"),
        models.OrganizationPhone(phone_number="8-800-111-22-34"),
    ]
    o4.activities = [meat]

    db.add_all([o1, o2, o3, o4])
    db.commit()
    db.close()
if __name__ == "__main__":
    run()
    print("Fixtures loaded.")