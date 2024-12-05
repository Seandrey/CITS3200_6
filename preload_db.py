# Script to preload data into the DB that cannot be gained from the survey (e.g. the number of hours required for each unit)# Author: Joel Phillips (22967051)
from app import app
from typing import Optional
from app import db
from sqlalchemy.orm.scoping import scoped_session
from app.models import Unit, Student, Location, Activity, ActivityLog, User, Domain

def get_or_add_unit(name: str, required_min: int, counts_prev: bool) -> Unit:
    unit: Optional[Unit] = Unit.query.filter_by(unit=name).one_or_none()
    if unit is None:
        unit = Unit(unit=name, required_minutes=required_min, counts_prev=counts_prev)
        db.session.add(unit)
    assert unit.required_minutes == required_min, f"Unit {name} says required min of {unit.required_minutes} in DB but {required_min} desired!" 
    assert unit.counts_prev == counts_prev, f"Unit {name} says counts previous is {unit.counts_prev} in DB, but {counts_prev} desired!"
    return unit

def clear_database():
    ActivityLog.query.delete()
    return

def import_units():
    # Create Function that Gets or Adds Units to Website
    # Reset Database Clears all database Content
    # Warn User: Database Empty No Units have been Declared, Please Declare Units with Time
    # Adds Unit Feature
    # Add Unit Edit Feature, Change Hours or Name    
    # TODO: Keep them temporarily existing but remove Later    
    # Added prac units, later have website add and make changes to db backend    
    get_or_add_unit("Practicum 1", 40, False)
    get_or_add_unit("Practicum 2", 40, False)
    get_or_add_unit("Practicum 3", 40, False)
    get_or_add_unit("Practicum 4", 40, False)

    
    # note that some units do not have cumulative hours from previous units counted. for example,    """        Units as described by Jo:        SSEH2295: 40. "definitely". 40 hours in that unit only.        SSEH3345: 25 (2298 doesn't count). 25 in that unit only.        SSEH3385: 25 (2298 doesn't count)        SSEH3393: 140 (earlier hours count towards it)        SSEH3394: 140 (earlier hours count towards it)        Apparently students can, but shouldn't, do units out of order (e.g. 2298 after 3345)        DOn't worry about 4th year.        She notes 45 and 85 are incompatible, and 93 and 94 are incompatible.    """    
    db.session.commit()
def import_data():
    with app.app_context():
        import_units()
    
if __name__ == "__main__":
    import_data()