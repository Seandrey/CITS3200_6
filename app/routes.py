# Routes for app, adapted from drtnf/cits3403-pair-up
# Author: Joel Phillips (22967051), David Norris (22690264)

from typing import Any, Optional
import flask
from flask import Flask, Response, redirect, render_template, request, jsonify, url_for
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import func
from app import app, db
from datetime import datetime
from app.login import signuprender, loginrender, logoutredirect
from flask_login import login_required, current_user
import json
from datetime import date, timedelta
from app.reports import *

from app.models import Activity, ActivityLog, Domain, Location, Supervisor


@app.route('/home')
@login_required
def home():
    return render_template('home.html')


@app.route('/edit')
@login_required
def edit():
    return render_template('edit.html')


@app.route('/library')
@login_required
def library():
    return render_template('library.html')


@app.route('/reports/student')
# @login_required
def reportStudents():
    teardown_db()
    # this fill db starts at 22000000, for testing navigate to /reports/student/22000000 as we only populate one
    fill_db_multiple_students(1)
    data = get_student_info(22000000)
    teardown_db()
    return render_template('reports/student.html', data=data)


@app.route('/reports/student/<studentid>')
# @login_required
def reportStudent(studentid):
    teardown_db()
    # this fill db starts at 22000000, for testing navigate to /reports/student/22000000 as we only populate one
    fill_db_multiple_students(1)
    data = get_student_info(studentid)
    teardown_db()
    return render_template('reports/student.html', data=data)


@app.route('/reports/staff')
@login_required
def reportStaff():
    return render_template('reports/staff.html')


def get_domain_col(activity: Optional[str], flist: list):
    """Gets the single AEP domain/activity type table column specified as a partial query"""
    session: scoped_session = db.session

    boilerplate = session.query(
        ActivityLog, Activity).join(Activity).filter(*flist)
    # if no activity, don't include in subquery (assume any activity)
    col_activity_subq = boilerplate.filter(Activity.activity == activity).subquery(
    ) if activity is not None else boilerplate.subquery()
    cols = session.query(Domain.domainid, Domain.domain, (func.coalesce(func.sum(col_activity_subq.c.minutes_spent), 0) / 60.0).label(
        "hours"), Domain.core).join(col_activity_subq, col_activity_subq.c.domainid == Domain.domainid, isouter=True).group_by(Domain.domainid).subquery()

    return cols


def get_domain_table(flist: Optional[list]) -> list:
    """Gets AEP domain/activity type table and number of activity columns"""
    session: scoped_session = db.session
    if flist is None:
        flist = []

    # find activity-domain table based on hardcoded activity types. due to how group by works, probably have to do this piecewise

    # TODO: notes for me tomorrow
    #domains: list[Domain] = Domain.query.all()

    # ensure this is in desired order
    activities: list[Activity] = Activity.query.order_by(Activity.activityid).all()
    # list of subqueries for each column (i.e. each activity type)
    col_subqs: list = []
    for activity in activities:
        col = get_domain_col(activity.activity, flist)
        col_subqs.append(col)
    total = get_domain_col(None, flist)

    table = session.query(total.c.domain.label("domain"), *[col_subqs[i].c.hours.label(f"{activities[i].activityid}") for i in range(0, len(col_subqs))], total.c.hours.label("total"), total.c.core.label("core"))
    # join each col_subq
    for col_subq in col_subqs:
        table = table.join(col_subq, col_subq.c.domainid == total.c.domainid)
    # ensure ordered by domainid
    table = table.order_by(total.c.domainid).all()

    """assessments = get_domain_col("Exercise Assessment", flist)
    prescriptions = get_domain_col("Exercise Prescription", flist)
    deliveries = get_domain_col("Exercise Delivery", flist)
    others = get_domain_col("Other", flist)
    total = get_domain_col(None, flist)

    table = session.query(total.c.domain.label("domain"), assessments.c.hours.label("assessment"), prescriptions.c.hours.label("prescription"), deliveries.c.hours.label("delivery"), others.c.hours.label("other"), total.c.hours.label("total")).join(
        assessments, assessments.c.domainid == total.c.domainid).join(prescriptions, prescriptions.c.domainid == total.c.domainid).join(deliveries, deliveries.c.domainid == total.c.domainid).join(others, others.c.domainid == total.c.domainid).all()
    """
    return table


@app.route('/reports/location')
# @login_required
def reportLocations():
    teardown_db()
    # this fill db starts at 22000000, for testing navigate to /reports/student/22000000 as we only populate one
    fill_db_multiple_students(10)
    # hardcoded location for now: whatever "1" is
    location_id = 1

    # TODO: also filter based on year/semester if relevant

    session: scoped_session = db.session

    # DEBUG find everything in DB with that location
    loc_data = session.query(ActivityLog, Domain, Activity, Supervisor, Location).join(
        Domain).join(Activity).join(Supervisor).join(Location).all()
    # print(loc_data)

    # find location name
    loc_name = Location.query.filter_by(locationid=location_id).one().location
    print(loc_name)

    # find hours by supervisor for that location
    sup_hours: list = session.query(Supervisor.name.label("supervisor"), (func.sum(ActivityLog.minutes_spent) / 60.0).label(
        "hours")).join(ActivityLog).filter_by(locationid=location_id).group_by(ActivityLog.supervisorid).all()
    print(sup_hours)

    data = {
        "location": loc_name,
        "date_generated": date.today().isoformat(),
        "sup_hours": sup_hours,
        "core": build_chart('location', location_id, True),
        "additional": build_chart('location', location_id, False)
    }

    teardown_db()
    return render_template('reports/location.html', data=data)

def get_year_flist(year: int) -> list:
    """Returns an flist for the year given, to pass into get_domain_table()"""
    return [ActivityLog.record_date.between(date(year, 1, 1), date(year, 12, 31))]

def get_cohort_info() -> dict[str, Any]:
    """Generates data used for cohort page"""
    # hardcoded cohort for now: 2022
    domains = get_domain_table(get_year_flist(date.today().year))

    activity_names: list[Activity] = Activity.query.order_by(Activity.activityid).all()

    # add "total" row at bottom
    total_row = gen_total_row(domains, activity_names)

    from_table = build_chart_from_table("Chart name", domains, activity_names)
    print(from_table)
    print("DEBUG: printing graph")
    print(build_chart('location', 1, True))
    print("DEBUG: end print graph")

    data = {
        "year": date.today().year,
        "domains": domains,
        "activity_names": activity_names,
        "total_row": total_row,
        "core": build_chart_from_table("Chart name", domains, activity_names, True),
        "additional": build_chart_from_table("Chart name", domains, activity_names, False)
    }
    return data

@app.route('/reports/cohort')
@login_required
def reportCohorts():
    # DEBUG
    teardown_db()
    # this fill db starts at 22000000, for testing navigate to /reports/student/22000000 as we only populate one
    fill_db_multiple_students(10)

    data = get_cohort_info()
    return render_template('reports/cohort.html', data=data)

# login.py routes


@app.route('/signup', methods=['GET', 'POST'])
def signuproute():
    return signuprender()


@app.route('/login', methods=['GET', 'POST'])
def loginroute():
    # check if url contains next query, and if so, pass it through
    next_page = request.args.get("next")
    return loginrender(next_page)


@app.route('/logout')
def logoutroute():
    return logoutredirect()
