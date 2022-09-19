# Routes for app, adapted from drtnf/cits3403-pair-up
# Author: Joel Phillips (22967051), David Norris (22690264)

import os
from typing import Optional
from flask import Flask, Response, redirect, render_template, request, jsonify, url_for
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy import func
from app import app, qualtrics_import
from datetime import datetime
from app.login import signuprender, loginrender, logoutredirect
from flask_login import login_required, current_user
import json
from datetime import date, timedelta

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
@login_required
def reportStudents():
    data = {
    'domains': (
        'Cardiovascular',
        'Musculoskeletal',
        'Metabolic',
        'Mental Health',
        'Cancer',
        'Kidney',
        'Neurological',
        'Respiratory/Pulmonary',
        'Other'
    ), ## list of available domains
    'charts': [
    {
        'title': 'Core Domains',
        'id': 'test1',
        'yMax': '200',
        'style': 'core',
        'domains': (1, 1, 1, 0, 0, 0, 0, 0, 0), ## if the index is one, the domain will be shown
        'hours': [
            ('Referrals, Screening or Assessmnts', (32, 8, 12)), ## three tuple as we are showing three domains
            ('Excercise Prescription', (9, 19, 49)),
            ('Excercise Delivery', (10, 2, 24)),
            ('Other', (13, 28, 9)),
        ]
    },
    {
        'title': 'Additional Domains',
        'id': 'test2',
        'yMax': '70',
        'domains': (0, 0, 0, 1, 1, 1, 1, 1, 1),
        'hours': [
            ('Referrals, Screening or Assessmnts', (3, 8, 12, 6, 6, 12)),
            ('Excercise Prescription', (3, 8, 1, 6, 6, 12)),
            ('Excercise Delivery', (5, 3, 1, 6, 6, 12)),
            ('Other', (3, 8, 12, 5, 3, 1)),
        ]
    }]
    }
    return render_template('reports/student.html', data=data)

@app.route('/reports/staff')
@login_required
def reportStaff():
    return render_template('reports/staff.html')

@app.route('/reports/location')
@login_required
def reportLocations():
    return render_template('reports/location.html')

@app.route('/reports/cohort')
@login_required
def reportCohorts():
    return render_template('reports/cohort.html')

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

def update_db_qualtrics():
    """TODO: move to another .py file. Updates DB from Qualtrics"""
    # api key, data centre, and survey ID for Joel test survey
    api_key = "3g99BHNjmZBe03puBM8gwx2WqptsJNfiTXyJW3Aa"
    data_centre = "ca1"
    survey_id = "SV_9XIDg01qrekuOWi"

    format = qualtrics_import.get_survey_format(survey_id, api_key, data_centre)
    label_lookup = qualtrics_import.get_label_lookup(format)

    qualtrics_import.download_zip(survey_id, api_key, data_centre)

    json_path = "MyQualtricsDownload/Computer Science - Exercise Science Logbook TRIAL - Copy 2.json"
    assert os.path.isfile(json_path), "failed to find downloaded .json"
    json = qualtrics_import.load_json(json_path)
    qualtrics_import.test_parse_json(json, label_lookup, format)

    # remove generated files
    os.remove(json_path)
    os.rmdir("MyQualtricsDownload")

@app.route('/update', methods=['GET', 'POST'])
def updateroute():
    """Temporary route: to manually update DB from Qualtrics. Remove GET later as not idempotent"""
    update_db_qualtrics()

    # allow redirection: designed to be used to reload page on AJAX POST
    redirect_to = request.args.get("next")
    if redirect_to is None:
        redirect_to = "home"

    return redirect(url_for(redirect_to))
