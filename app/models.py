# Database models
# Author: Joel Phillips (22967051), Sean Ledesma (22752771)

from flask_sqlalchemy import SQLAlchemy
from datetime import date, time, datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login, db
from sqlalchemy import JSON, func, extract, Boolean
from sqlalchemy.ext.hybrid import hybrid_property

class User(UserMixin, db.Model):
    """Used for website users (authentication)"""
    userid = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    create_date = db.Column(db.Date, default=date.today)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<User {} with name {}>'.format(self.userid, self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
           return (self.userid)

@login.user_loader
def load_user(uid):
    return User.query.get(int(uid))

class Student(db.Model):
    """Used to represent student info"""

    studentid = db.Column(db.Integer, primary_key=True) 
    """The internal student ID used by DB. Not the '22552255' ID."""

    student_number = db.Column(db.Integer, unique=True, index=True)
    """The external student number, i.e. '22552525' or whatever"""

    name = db.Column(db.String(64))
    logs = db.relationship("ActivityLog")

    def __repr__(self):
        return f'<Student {self.studentid} with ID {self.student_number} and name {self.name}>'

class Location(db.Model):
    """Used to represent student location"""
    locationid = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(64))
    logs = db.relationship("ActivityLog")

    def __repr__(self):
        return f'<Location {self.locationid} with name {self.location}>'

class Supervisor(db.Model):
    """Used to represent supervisor"""
    supervisorid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    logs = db.relationship("ActivityLog")

    def __repr__(self):
        return f'<Supervisor {self.supervisorid} with name {self.name}>'

class Activity(db.Model):
    """Used to represent activity type/category"""
    activityid = db.Column(db.Integer, primary_key=True)
    activity = db.Column(db.String(64))
    logs = db.relationship("ActivityLog")

    def __repr__(self):
        return f'<Activity {self.activityid} with name {self.activity}>'

class Domain(db.Model):
    """Used to represent AEP domain"""
    domainid = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(64))
    logs = db.relationship("ActivityLog")

    def __repr__(self):
        return f'<Domain {self.domainid} with name {self.domain}>'

class Unit(db.Model):
    """Used to represent which unit hours are being calculated for"""
    unitid = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(64))
    required_minutes = db.Column(db.Integer)
    """Minutes that this unit requires to be completed."""
    counts_prev = db.Column(db.Boolean, default=False)
    """Whether the required minutes of this unit are contributed to by hours in previous units"""
    logs = db.relationship("ActivityLog")

    def __repr__(self):
        return f"<Unit {self.unitid} with name {self.unit}>"

class ActivityLog(db.Model):
    """Used to represent a single activity log entry"""
    logid = db.Column(db.Integer, primary_key=True)
    studentid = db.Column(db.Integer, db.ForeignKey(Student.studentid))
    locationid = db.Column(db.Integer, db.ForeignKey(Location.locationid))
    supervisorid = db.Column(db.Integer, db.ForeignKey(Supervisor.supervisorid))
    activityid = db.Column(db.Integer, db.ForeignKey(Activity.activityid))
    domainid = db.Column(db.Integer, db.ForeignKey(Domain.domainid))
    unitid = db.Column(db.Integer, db.ForeignKey(Unit.unitid))

    minutes_spent = db.Column(db.Integer)
    record_date = db.Column(db.Date)

    is_edited = db.Column(db.Integer,default=0)

    "Description of Notes"
    activitydesc = db.Column(db.String(255))

    """The date the service was recorded for"""
    responseid = db.Column(db.String(64))
    """ID of original Qualtrics survey response. TODO is this long enough to match?"""
    
    unit = db.relationship('Unit', lazy='joined')
    student = db.relationship('Student', lazy='joined')
    location = db.relationship('Location', lazy='joined')
    supervisor = db.relationship('Supervisor', lazy='joined')
    domain = db.relationship('Domain', lazy='joined')
    activity = db.relationship('Activity', lazy='joined')

    # Sanity Check
    def __repr__(self):
        return f'<ActivityLog {self.logid} with student {self.studentid}, supervisor {self.supervisorid}, location {self.locationid}, activity {self.activityid}, domain {self.domainid}, unit {self.unitid}, of {self.minutes_spent} m on {self.record_date} (response {self.responseid})>'

    @hybrid_property
    def year(self):
        #return func.year(self.record_date)
        return self.record_date.year

    @year.expression
    def year(cls):
        return extract("year", cls.record_date)

class LastDbUpdate(db.Model):
    """Used to store the datetime of the last update from Qualtrics. Here instead of in server to enable better concurrency"""
    updateid = db.Column(db.Integer, primary_key=True)
    updatedate = db.Column(db.DateTime, unique=True, index=True)

    def __repr__(self):
        return f'<LastDBUpdate {self.updatedate} (id {self.updateid})>'

# Description of Other, Prescription, Delivery, Assesment 
class DomainDescription(db.Model):
    "Stores the corresponding DomainDescriptions for each domain"
    domain_description = db.Column(db.String(180))
    domainid = db.Column(db.Integer, db.ForeignKey(Domain.domainid))
    domain_descid = db.Column(db.Integer, primary_key=True)
