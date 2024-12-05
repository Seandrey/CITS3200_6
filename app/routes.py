# Routes for app
# Author: David Norris (22690264), Joel Phillips (22967051), Sean Ledesma (22752771), Lara Posel (22972221)

import os
from typing import Any, Optional
import flask
from flask import Flask, Response, redirect, render_template, request, make_response, jsonify, url_for
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import func
from app import app, db, qualtrics_import
from datetime import datetime
from app.login import signuprender, loginrender, logoutredirect
from flask_login import login_required, current_user
import json
from datetime import date, timedelta
from app.reports import *
from app.models import Activity, ActivityLog, Domain, Location, Supervisor, User
import pdfkit
from typing import List

#Chaning survey data based on Survery reference
API_KEY = "3g99BHNjmZBe03puBM8gwx2WqptsJNfiTXyJW3Aa"
API_KEY_2 = "YThuWnPU1PYJwJUQuf0rWYqPJvdTaeGrELNbPZPK"
DATA_CENTRE = "yul1"
SURVEY_ID = "SV_e2MzVI6odZyLabs"
SURVEY_NAME = "2023 Activity Log Practicum"
HOURS_FOR_PASS = 140

# SV_e2MzVI6odZyLabs
# 2023 Activity Log Practicum




from flask import Flask, request, redirect, url_for
from preload_db import get_or_add_unit
@app.route('/addPrac', methods=['POST'])
def addunit():
    unit_name = request.form.get('unit_name')

    if  (Unit.query.filter_by(unit=unit_name).first() is not None):
        get_or_add_unit(unit_name, 40, False)
        #print(Unit.query.all())
        return jsonify({'message': 'Form submitted! Added Unit'})
    
    #print(Unit.query.all())

    # allow redirection: designed to be used to reload page on AJAX POST
    return jsonify({'message': 'Form submitted! Unit Already Exists!'})

@app.route('/submit', methods=['GET','POST'])
def submit():
    # Do something with the form data
    if request.method == 'POST':
        form_data = request.form.getlist('vehicle')
        #print('Form data:', form_data)
        return redirect(url_for('run', form_data=form_data))
    return render_template('reports/new_template.html')

@app.route('/')
def redirects():
    return redirect(url_for('home'))

@app.route('/home')
# @login_required
def home():
    return render_template('home.html')


@app.route('/edit')
# @login_required
def edit():
    return render_template('edit.html')


@app.route('/library') 
# @login_required
def library():
    #students = studentRep()
    return render_template('library.html', students=[])

@app.route('/reports/student/')

# @login_required
def reportStudents():
    students = db.session.query(Student.student_number.label('id'), Student.name).all()
    return render_template('reports/student_search.html', students=students)





@app.route('/reports/student/<int:student_number>/<unit_values>')
# @login_required
def reportStudent(student_number, unit_values):
    #print("unitid", unit_values) # <----- unitid's in Local DB
    new_list = [int(x) for x in unit_values.split('-')]
    #print("student_number", student_number)

    # Move Unit_names to new_data
    data = get_student_info(student_number, new_list)
    new_data = get_unit_student_report(student_number, new_list)
    max_hours = HOURS_FOR_PASS

    return render_template('reports/student_multitable.html', data=data, student_number=student_number, unit_values=unit_values, new_data=new_data, max_hours = HOURS_FOR_PASS)

@app.route('/reports/student/<int:student_number>/', methods=["GET","POST"])
def students_units(student_number):
    if request.method == 'POST':
        unit_values = request.form.getlist('units')
        #print('Form data:', unit_values)
        # for i in unit_values:
            #print("id:", i)
        return redirect(url_for('reportStudent', student_number=student_number, unit_values='-'.join(unit_values)))
        # Convert list of unit_values to a string with '-' as separator
        
    result = db.session.query(Unit.unitid, Unit.unit).\
            join(ActivityLog).\
            join(Student).\
            filter(Student.student_number==student_number).\
            distinct().all()

    data = {
        "units": result
    }
    return render_template('reports/selectunits.html', data=data, student_number=student_number)

# Change Where Description row is on logs. Make Sure JS works use getRow different row
# Qualtrics Update Response type beat

@app.route('/reports/logs/<int:student_number>/')
# @login_required
def studentLogs(student_number):
    s: Student = Student.query.filter_by(student_number=student_number).one()
    studentid = s.studentid
    logs = ActivityLog.query.filter_by(studentid=studentid).order_by(ActivityLog.record_date.desc()).all()

    #Get Queries   
    units: list[Unit] = Unit.query.order_by(
        Unit.unitid).all()
    locations: list[Location] = Location.query.order_by(
        Location.locationid).all()
    supervisors: list[Supervisor] = Supervisor.query.order_by(
        Supervisor.supervisorid).all()
    domains: list[Domain] = Domain.query.order_by(
        Domain.domainid).all()
    activities: list[Activity] = Activity.query.order_by(
        Activity.activityid).all()

    subst_data = {
        "student_db_id": studentid
    }

    data = {
        "student": s,
        "locations": locations,
        "supervisors": supervisors,
        "domains": domains,
        "units": units,
        "activities": activities
    }

    return render_template('reports/logs.html', logs=logs, subst_data=subst_data, data=data)

@app.route("/reports/submit_edit", methods=['POST'])
# @login_required
def submit_edit():
    """Send Post Request to that page, on the client has JSON file. Extracts json file from body"""
    data = request.get_json()

    print(f'JSON Data: {data}\n')
    
    #Update Row with new Data
    new_log: ActivityLog = ActivityLog.query.filter_by(logid=data['logid']).one()
    assert new_log.studentid == data["studentid"], f"DB has edit request for {data['logid']} with student {new_log.studentid}, while request has {data['studentid']}"
    new_log.locationid = data["locationid"]
    new_log.supervisorid = data["supervisorid"]
    new_log.activityid = data["activityid"]
    new_log.domainid =  data["domainid"]
    new_log.minutes_spent = data["minutes_spent"]
    # Why disabled?
    # new_log.record_date = data["record_date"]
    new_log.unitid = data["unitid"]
    new_log.activitydesc= data["activitydesc"]
    new_log.is_edited = True

    # Datetime No change Depreciated Datetime?
    service_date_datetime: datetime = 0
    try:
        #service_date_datetime = datetime.strptime(data["record_date"], "%Y-%m-%d")
        # strip weird "Z" character
        processed_date = data["record_date"].replace("Z", "")
        service_date_datetime = datetime.fromisoformat(processed_date)
        service_date_date = service_date_datetime.date()
        new_log.record_date = service_date_date
    except ValueError:
        print(f"failed to parse '{data['record_date']}' to datetime (record date). ignoring any changes")

    session: scoped_session = db.session
    session.commit()

    student: Student=Student.query.filter_by(studentid=data["studentid"]).one()
    # redirect_to = request.args.get("next")
    # if redirect_to is None:
    #     redirect_to = "/reports/logs/"  + f'{student.student_number}/'
    return redirect(url_for('home'))
    # return redirect(url_for('studentLogs', student_number=student.student_number))


# Mind Melted overwhelmed, TODO: fix the entire Layout or Querying
# TODO: Removed Supervisor Row and Unit Row to fit Description in.
@app.route('/reports/student/pdf/<int:student_number>/<unit_values>')
# @login_required
def reportStudentPdf(student_number, unit_values):
    # #print(request.args.get('units'))
    # #print("touched")
    new_list = [int(x) for x in unit_values.split('-')]
    # #print(new_list)
    data = get_student_info(student_number, new_list)
    new_data = get_unit_student_report(student_number, new_list)
    max_hours = HOURS_FOR_PASS

    s: Student = Student.query.filter_by(student_number=student_number).one()
    studentid = s.studentid

    logs = ActivityLog.query.filter_by(studentid=studentid).options(db.joinedload(ActivityLog.unit)).all()

    #Get Queries   
    units: list[Unit] = Unit.query.order_by(
        Unit.unitid).all()
    locations: list[Location] = Location.query.order_by(
        Location.locationid).all()
    supervisors: list[Supervisor] = Supervisor.query.order_by(
        Supervisor.supervisorid).all()
    domains: list[Domain] = Domain.query.order_by(
        Domain.domainid).all()
    activities: list[Activity] = Activity.query.order_by(
        Activity.activityid).all()

    subst_data = {
        "student_db_id": studentid
    }
    # Create Report
    note_data = {
        "student": s,
        "locations": locations,
        "supervisors": supervisors,
        "domains": domains,
        "units": units,
        "activities": activities
    }

    return render_template('reports/student_pdf_multitable.jinja', data=data, new_data=new_data, max_hours=HOURS_FOR_PASS, note_data=note_data, logs=logs)


@app.route('/reports/staff')
# @login_required
def reportStaff():
    return render_template('reports/staff.html')


@app.route('/reports/location')
# @login_required
def reportLocationsSearch():
    locations = db.session.query(Location.locationid.label('id'), Location.location).all()
    return render_template('reports/location_search.html', locations=locations)

@app.route('/reports/location/<int:locationid>')
# @login_required
def reportLocations(locationid):
    # TODO: also filter based on year/semester if relevant
    data = get_location_info(locationid)

    return render_template('reports/location.html', data=data)

@app.route('/reports/location/pdf/<int:locationid>')
# @login_required
def reportLocationPdf(locationid):
    # TODO: also filter based on year/semester if relevant
    data = get_location_info(locationid)

    return render_template('reports/location_pdf.jinja', data=data)


@app.route('/reports/cohort')
# @login_required
def reportCohortsSearch():
    #years = db.session.query(func.year(ActivityLog.record_date)).group_by(func.year(ActivityLog.record_date)).all()
    cohorts = db.session.query(ActivityLog.year, ActivityLog.unitid, Unit.unit).join(Unit).group_by(ActivityLog.year, ActivityLog.unitid).all()
    return render_template('reports/cohort_search.html', cohorts=cohorts)

@app.route('/reports/cohort/<int:cohort_unit>/<int:cohort_year>')
# @login_required
def reportCohorts(cohort_unit, cohort_year):
    data = get_cohort_info(cohort_unit, cohort_year)
    return render_template('reports/cohort.html', data=data)

@app.route('/reports/cohort/pdf/<int:cohort_unit>/<int:cohort_year>')
# @login_required
def reportCohortPdf(cohort_unit, cohort_year):
    data = get_cohort_info(cohort_unit, cohort_year)
    return render_template('reports/cohort_pdf.jinja', data=data)


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

def lookup_manual():
    "Gets the QID for the Domain Descriptions Since All Domain Descriptions contain the same value we only need to find one"
    manual_lookup = {}

    questionText = "'Assessment' activity?"
    for sub in map:
        if(sub[questionText] == "'Assessment' activity?"):
            # get question name
            manual_lookup[DomainDescription] = sub["questionName"]
            break
    return manual_lookup
    # Use Export Questions Map to get QID for values

    # Temporary Solution: Manual Lookup

def update_db_qualtrics():
    """TODO: move to another .py file. Updates DB from Qualtrics"""
    # api key, data centre, and survey ID for Joel test survey
    api_key = API_KEY_2
    data_centre = DATA_CENTRE
    survey_id = SURVEY_ID

    format = qualtrics_import.get_survey_format(survey_id, api_key, data_centre)
    # Get Survey Format
    label_lookup = qualtrics_import.get_label_lookup(format)
    #print(f'LABEL LOOKUP:{label_lookup}')
    # Sample
    """LABEL LOOKUP:{'Name': 'QID1', 'Student Number': 'QID89', 'Unit Code': 'QID90', 'Service Date': 'QID44', 'Location': 'QID2', 'Supervisor': 'QID86', 'Number of Logs': 'QID41', 'Activity Type': 'QID9', 'Domain': 'QID3', 'Minutes': 'QID6'}"""


    qualtrics_import.add_known_choices(label_lookup, format)

    qualtrics_import.download_zip(survey_id, api_key, data_centre)

    # Where is the downloaded csv File?

    json_path = f"MyQualtricsDownload/{SURVEY_NAME}.json"
    assert os.path.isfile(json_path), "failed to find downloaded .json"



    # Using lookup ids to find specified rows and add them to the system
    json = qualtrics_import.load_json(json_path)
    # JSON STUFF IS ALREADY FIXED LOADED SO LOOK INTO LOAD JSON
    # DICTIONARY QUERY SET
    # #print(json['{"ImportId":"1_QID10"}'])
    qualtrics_import.test_parse_json(json, label_lookup, format)

    # remove generated files
    os.remove(json_path)
    os.rmdir("MyQualtricsDownload")

def cleardb():
    try:
        Domain.query.delete()
        Location.query.delete()
        Supervisor.query.delete()
        Activity.query.delete()
        ActivityLog.query.filter(ActivityLog.is_edited == 0).delete()
        LastDbUpdate.query.delete()
        Student.query.delete()
        db.session.commit()
        return True
    except:
        #print("Error Deletion Database error")
        return False



@app.route('/reports/student/<int:student_number>/<unit_values>/notes')
def studentnotes(student_number, unit_values):
    s: Student = Student.query.filter_by(student_number=student_number).one()
    studentid = s.studentid
    logs = ActivityLog.query.filter_by(studentid=studentid).options(db.joinedload(ActivityLog.unit)).all()

    #Get Queries   
    units: list[Unit] = Unit.query.order_by(
        Unit.unitid).all()
    locations: list[Location] = Location.query.order_by(
        Location.locationid).all()
    supervisors: list[Supervisor] = Supervisor.query.order_by(
        Supervisor.supervisorid).all()
    domains: list[Domain] = Domain.query.order_by(
        Domain.domainid).all()
    activities: list[Activity] = Activity.query.order_by(
        Activity.activityid).all()

    subst_data = {
        "student_db_id": studentid
    }
    # Create Report
    data = {
        "student": s,
        "locations": locations,
        "supervisors": supervisors,
        "domains": domains,
        "units": units,
        "activities": activities
    }
    return render_template('reports/studentnotess.html', logs=logs, subst_data=subst_data, data=data, unit_val=unit_values)


@app.route('/cleardb', methods=['POST'])
def cleardatabase():
    """Clears Database of Contents except Unit Names"""
    cleardb()

    # DEBUG
    #print(Unit.query.all())

    # allow redirection: designed to be used to reload page on AJAX POST
    redirect_to = request.args.get("next")
    if redirect_to is None:
        redirect_to = "home"

    return redirect(url_for(redirect_to))




@app.route('/update', methods=['POST'])
def updateroute():
    """Temporary route: to manually update DB from Qualtrics. Remove GET later as not idempotent"""
    update_db_qualtrics()

    # DEBUG
    #print(ActivityLog.query.all())

    # allow redirection: designed to be used to reload page on AJAX POST
    redirect_to = request.args.get("next")
    if redirect_to is None:
        redirect_to = "home"

    return redirect(url_for(redirect_to))

@app.route('/makepdf', methods=['POST'])
def makePDF():
    # Using PDFKIT
    if request.method == 'POST':
        html = request.data.decode('utf-8')
        #print ("PDF POST RECEIVED")
        # Get Request Parameters, I.E.
        # .jinja file, I.e. (student.jinja, location,jinja)
        # Get student number to write in output
        # Get date from here

        # PDF options
        options = {
            "orientation": "portrait",
            "page-size": "A4",
            "encoding": "UTF-8",
            "enable-local-file-access":""
        }
        css = ['skeleton.css', 'normalize.css', 'style.css', 'reports.css', 'pdf.css']
        css = [os.path.join(app.root_path, 'static\\css\\' + c) for c in css]
        config = pdfkit.configuration(wkhtmltopdf=app.config['WKHTML_EXE'])
        # Build PDF from HTML
        pdf = pdfkit.from_string(html, False, options=options, configuration=config, css=css)
        response=make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename-output.pdf'

        return response

