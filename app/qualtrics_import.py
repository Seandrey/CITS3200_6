# Python code to import survey data from Qualtrics
# Author: Joel Phillips (22967051)

from datetime import date, datetime
import io
import json
import os
import re
import sys
from typing import Any, Optional, Type, TypeVar
import zipfile
import requests

from sqlalchemy.orm.scoping import scoped_session
from app import db
from app.models import Activity, ActivityLog, Domain, Location, Student, Supervisor, Unit

# constants: question names (exact website match) as strings
STUDENT_NAME = "Name"
STUDENT_NUMBER = "Student Number"
UNIT_CODE = "Unit Code"
SERVICE_DATE = "Service Date"
PLACEMENT_LOCATION = "Location"
PLACEMENT_SUPERVISOR = "Supervisor"
NUM_ACTIVITY_LOGS = "Number of Logs"
CATEGORY = "Activity Type"
AEP_DOMAIN = "Domain"
MINUTES_SPENT = "Minutes"


def download_zip(survey_id: str, api_token: str, data_centre: str):
    """
    Code based on Qualtrics API example: https://api.qualtrics.com/ZG9jOjg3NzY3Nw-new-survey-response-export-guide
    Downloads a CSV file. This is not intended behaviour
    """

    # set static params
    request_check_progress = 0.0
    progress_status = "inProgress"
    url = f"https://{data_centre}.qualtrics.com/API/v3/surveys/{survey_id}/export-responses/"
    headers = {
        "content-type": "application/json",
        "x-api-token": api_token
    }

    # 1: create data export
    data = {
        "format": "json", # JSON seems more difficult to use. See if can parse CSV adequately
        #"seenUnansweredRecode": 2, # converts questions that weren't answered to "2", can't be used for JSON
        "startDate": "2019-04-30T07:31:43Z", # only export after given date, inclusive
        #"useLabels": True # shows text shown to user instead of internal numbers. can't use for JSON
        #"compress": False # can not make it a zip file
    }

    download_req_response = requests.request("POST", url, json=data, headers=headers)
    print(download_req_response.json())

    try:
        progress_id = download_req_response.json()["result"]["progressId"]
    except KeyError:
        print(download_req_response.json())
        sys.exit(2)
    assert progress_id is not None, "progress_id is none!"
    
    isFile = None

    # 2: check on data export progress and wait until export ready
    while progress_status != "complete" and progress_status != "failed" and isFile is None:
        if isFile is None:
            print("file not ready")
        else:
            print("progress_status=", progress_status)
        request_check_url = url + progress_id
        request_check_response = requests.request("GET", request_check_url, headers=headers)
        try:
            isFile = request_check_response.json()["result"]["fileId"]
        except KeyError:
            1 == 1
        print(request_check_response.json())
        request_check_progress = request_check_response.json()["result"]["percentComplete"]
        print("Download is " + str(request_check_progress) + " complete")
        progress_status = request_check_response.json()["result"]["status"]
    
    # check for error
    if progress_status == "failed":
        raise Exception("export failed")

    file_id = request_check_response.json()["result"]["fileId"]

    # 3: download file
    request_download_url = url + file_id + "/file"
    request_download = requests.request("GET", request_download_url, headers=headers, stream=True)

    # 4: unzip file
    zipfile.ZipFile(io.BytesIO(request_download.content)).extractall("MyQualtricsDownload")
    print("complete")

def load_json(filename: str) -> dict[str, list[dict]]:
    """Loads JSON file to python dictionary"""
    with open(filename) as file:
        data: dict[str, list[dict]] = json.load(file)
        
        # sanity checks
        assert isinstance(data, dict), "json not dict!"
        assert "responses" in data, "no responses in data!"
        assert isinstance(data["responses"], list), "responses not list!"
        assert len(data["responses"]) == 0 or isinstance(data["responses"][0], dict), "individual response not dict!"

        return data
    # TODO: delete JSON file

class DummyLogModel:
    """Temporary class to act as model for log book main - has some fields required"""

    def __init__(self, student: str, supervisor: str, location: str, activity: str, domain: str, min_spent: int):
        self.student = student
        self.supervisor = supervisor
        self.location = location
        self.activity = activity
        self.domain = domain
        self.min_spent = min_spent
    
    def __repr__(self) -> str:
        return f"<{self.student}, {self.supervisor}, {self.location}, {self.activity}, {self.domain}, {self.min_spent}>"

class LabelLookup:
    """Class to lookup labels in more intelligent way"""

    def __init__(self, dict: dict[str, str]):
        """TODO: make this generate from scratch eventually"""
        self.dict = dict

    def __repr__(self) -> str:
        return repr(self.dict)
    
    def __getitem__(self, key: str) -> str:
        """Overload [] operator for accesses"""
        return self.dict[key]
    
    def get_text(self, key: str) -> str:
        """Based on JSON having '_TEXT' suffix for text"""
        return f'{self[key]}_TEXT'

def get_answer_label(json_response: dict[str, dict[str, str]], key: str) -> str:
    """Gets answer label for given question name key"""
    print("DEBUG: looking up in labels: ", key)
    return json_response["labels"][key]

def make_n_text(text: str, iteration: int) -> str:
    """Returns text in format required for a given iteration"""
    return f"{iteration}_{text}"

def get_answer_label_n(json_response: dict[str, dict[str, str]], key: str, iteration: int) -> str:
    """Gets answer label for a given question name key of a given iteration"""
    return get_answer_label(json_response, make_n_text(key, iteration))

def lookup_embedded_text(response_val: dict[str, str], label_lookup: LabelLookup, label_name: str) -> str:
    """Lookup text embedded in JSON (with _TEXT suffix)"""

    print("DEBUG---")
    print("Key: ", label_lookup.get_text(label_name))
    print("Response_val:", response_val)
    print("END DEBUG---")

    return response_val[label_lookup.get_text(label_name)]

def get_multi_label(json_response: dict[str, dict[str, str]], multi_lookup: list[str], original_lookup: str) -> str:
    """Lookup answer label for a multi-label question (i.e. many mutually-exclusive questions sharing same label)"""
    labels = json_response["labels"]
    for qid in multi_lookup:
        if qid in labels:
            return labels[qid]
    raise Exception(f"failed to find key '{original_lookup}' in labels")
    return ""

dbModel = TypeVar("dbModel", bound=db.Model)
def get_or_add_db(type: Type[dbModel], fdict: dict[str, Any]) -> dbModel:
    """Get row of DB or add if doesn't exist. Intended for use with supervisors, students, placement locations, etc. when adding new rows"""
    assert fdict is not None, "fdict cannot be none in get_or_add_db!"

    db_row: Optional[type] = type.query.filter_by(**fdict).one_or_none()
    if db_row is None:
        db_row = type(**fdict)
        db.session.add(db_row)
    return db_row

def add_known_choices_from_q(question_id: str, questions_map: dict, type: Type[dbModel], fdict_key: str):
    """Adds all known values from a 'choice' question, if values aren't added already"""
    choices: dict = questions_map[question_id]["choices"]
    for key, value in choices.items():
        get_or_add_db(type, {fdict_key: value["description"]})
        # TODO: is there a difference between "description" and "choiceText"?

def add_known_choices(label_lookup: LabelLookup, format: dict[str, dict]):
    """Adds all known activities, AEP domains, regardless of whether used in response"""

    questions_map: dict = format["result"]["questions"]

    # activity
    """activity_data = questions_map[label_lookup[CATEGORY]]
    activity_choices: dict = activity_data["choices"]
    for key, value in activity_choices.items():
        get_or_add_db(Activity, {"activity": value["description"]})
        # TODO: is there a difference between "description" and "choiceText"?"""
    add_known_choices_from_q(label_lookup[CATEGORY], questions_map, Activity, "activity")

    add_known_choices_from_q(label_lookup[AEP_DOMAIN], questions_map, Domain, "domain")

def test_parse_json(json_file: dict[str, list[dict]], label_lookup: LabelLookup, format: dict[str, dict]) -> None:
    """Try to parse JSON representation of dict? Assumed format below"""

    for response in json_file["responses"]:
        response_id = response["responseId"]
        response_val = response["values"]

        session: scoped_session = db.session

        # if already seen a response with same ID in database, skip
        same_response_id: list[ActivityLog] = ActivityLog.query.filter_by(responseid=response_id).all()
        if len(same_response_id) != 0:
            print(f"Found response ID {response_id} in DB already! Skipping response")
            continue

        student_name = lookup_embedded_text(response_val, label_lookup, STUDENT_NAME)
        student_number = lookup_embedded_text(response_val, label_lookup, STUDENT_NUMBER)
        student_number_int: int = 0
        try:
            student_number_int = int(student_number, base=10)
        except ValueError:
            print(f"failed to parse '{student_number}' to int (student number). skipping response")
            continue
        student: Optional[Student] = Student.query.filter_by(student_number=student_number_int).one_or_none()
        if student is None:
            student = Student(student_number=student_number_int, name=student_name)
            db.session.add(student)
        # TODO changes in how differing student names for same ID are handled? currently just ignores name change
        if student.name != student_name:
            print(f"Warning: student ID {student.student_number} previously named as '{student.name}', new response names as '{student_name}'")

        service_date = lookup_embedded_text(response_val, label_lookup, SERVICE_DATE)
        service_date_datetime: datetime = 0
        try:
            service_date_datetime = datetime.strptime(service_date, "%d/%m/%Y")
        except ValueError:
            print(f"failed to parse '{service_date}' to datetime (service date). skipping response")
            continue
        service_date_date: date = service_date_datetime.date()

        placement_loc = get_answer_label(response, label_lookup[PLACEMENT_LOCATION])
        location = get_or_add_db(Location, {"location": placement_loc})

        # supervisor is more complicated as has multiple questions as implementation. so use multi lookup
        supervisor_lookup = get_multi_lookup(format, PLACEMENT_SUPERVISOR)
        supervisor_name = get_multi_label(response, supervisor_lookup, PLACEMENT_SUPERVISOR)
        supervisor = get_or_add_db(Supervisor, {"name": supervisor_name})

        unit_code = get_answer_label(response, label_lookup[UNIT_CODE])
        # ensure unit already exists, otherwise ignore with warning
        unit: Unit = Unit.query.filter_by(unit=unit_code).one_or_none()
        if unit is None:
            print(f"Unknown unit '{unit_code}'! Skipping response")
            continue

        num_logs = lookup_embedded_text(response_val, label_lookup, NUM_ACTIVITY_LOGS) 
        num_logs_int: int = 0
        try:
            num_logs_int = int(num_logs)
        except ValueError:
            print(f"failed to parse '{num_logs}' to int (num logs). skipping response")
            continue

        # commit any added rows
        session.commit()

        # TODO: alternatively, could just start with "1" and keep going if finds more
        for i in range(1, num_logs_int + 1):
            # FIXME: to preserve order (important for tables later), modify "Activity" and "Domain" to instead be imported from export questions map (or similar). only allow lookup here

            # note inconsistent spacing of "- " vs " - "
            category = get_answer_label_n(response, label_lookup[CATEGORY], i)
            activity: Optional[Activity] = Activity.query.filter_by(activity=category).one_or_none()
            if activity is None:
                activity = Activity(activity=category)
                session.add(activity)
                session.commit()
                session = db.session
            # TODO: probably don't need this anymore

            aep_domain = get_answer_label_n(response, label_lookup[AEP_DOMAIN], i)
            domain: Optional[Domain] = Domain.query.filter_by(domain=aep_domain).one_or_none()
            if domain is None:
                domain = Domain(domain=aep_domain)
                session.add(domain)
                session.commit()
                session = db.session
            # TODO: probably don't need this anymore

            minutes = response_val[make_n_text(label_lookup.get_text(MINUTES_SPENT), i)]
            minutes_int: int = 0
            try:
                minutes_int = int(minutes)
            except ValueError:
                print(f"Failed to parse '{minutes}' (minutes) to int! Ignoring log")
                continue

            log_row = ActivityLog(studentid=student.studentid, locationid=location.locationid, supervisorid=supervisor.supervisorid, activityid=activity.activityid, domainid=domain.domainid, minutes_spent=minutes_int, record_date=service_date_date, unitid=unit.unitid, responseid=response_id)
            session.add(log_row)
        session.commit()

def get_survey_format(survey_id: str, api_token: str, data_centre: str) -> dict[str, dict]:
    """Gets format of survey (question name mapping, etc.). Adapted from https://api.qualtrics.com/ZG9jOjg3NzY3Mw-managing-surveys"""
    # also see some more docs on JSON schema here: https://api.qualtrics.com/73d7e07ec68b2-get-survey

    base_url = f"https://{data_centre}.qualtrics.com/API/v3/surveys/{survey_id}"
    headers = {"x-api-token": api_token}

    response = requests.get(base_url, headers=headers)
    print("DEBUG: response start---")
    print(response.text)
    print("DEBUG: response end---")

    # should have a json form, with "result" field. Under "result", has exportColumnMap
    return response.json()

def get_label_lookup_old(survey_format_json: dict[str, dict]) -> dict[str, str]:
    """Gets label lookup map from less useful Qualtrics form.
    NOTE: this implementation abandoned. exportColumnMap seems to have less useful data than I thought - 
    does not have textual column description. Instead trying another way"""

    bad_map = survey_format_json["result"]["exportColumnMap"]

    print("DEBUG: export column map---")
    print(bad_map)
    print("DEBUG: end export column map---")

    print(type(bad_map["Q1"]))
    print(type(bad_map["Q1"]["question"]))
    
    # now, extract a str-str dictionary from that
    label_lookup: dict[str, str] = {key: value["question"] for (key, value) in bad_map.items()}
    return label_lookup

def get_label_lookup(survey_format_json: dict[str, dict]) -> LabelLookup:
    """Gets label lookup map in form: {"Student Name": "QID1"}. Will not work correctly if names are not unique."""
    questions_map: dict = survey_format_json["result"]["questions"]

    print("DEBUG: export questions map---")
    print(questions_map)
    print("DEBUG: end questions column map---")

    # now, extract a str-str dictionary from that
    #label_lookup: dict[str, str] = {value["questionText"]: key for (key, value) in questions_map.items()}
    label_lookup: dict[str, str] = {}
    for key, value in questions_map.items():
        if "questionLabel" in value and value["questionLabel"] is not None:
            label_lookup[value["questionLabel"]] = key

    # TODO: unsure how best to deal with HTML things. Current approach is just include it in text to search. Better approach could be to remove from survey altogether
    #label_lookup = {re.sub("<div>|</div>|<br>", "", key): value for (key, value) in label_lookup.items()}

    return LabelLookup(label_lookup)

def get_multi_lookup(survey_format_json: dict[str, dict], desired_key: str) -> list[str]:
    """Gets a list of all values that correspond to the desired key. Designed for use with Placement Supervisor, which is 
    modelled in Qualtrics as many separate questions with the same name."""
    questions_map: dict = survey_format_json["result"]["questions"]

    # now, list comprehend this
    #multi_lookup: list[str] = [key for (key, value) in questions_map.items() if value["questionText"] == desired_key]
    multi_lookup: list[str] = [key for (key, value) in questions_map.items() if value["questionLabel"] == desired_key]

    return multi_lookup

# JSON format (apparently):
"""
{
    "responses": [{
        "responseId": "horrible_hex_number",
        "values": {
            "startDate": "2019-05-02T14:06:49Z",
            "endDate": "2019-05-02T14:06:58Z",
            "status": 0,
            "ipAddress": "24.197.127.176",
            "progress": 100,
            "duration": 9,
            "finished": 1,
            "recordedDate": "2019-05-02T14:06:59.208Z",
            "_recordId": "R_1Cx8FIukucgqM94",
            "locationLatitude": "34.8307952880859375",
            "locationLongitude": "-82.35070037841796875",
            "distributionChannel": "anonymous",
            "userLanguage": "EN", 
            "QID2": 2,
            "QID3": 2
        },
        "labels": {
            "status": "IP Address",
            "finished": "True",
            "QID2": "fair",
            "QID3": "maybe"
        },
        "displayedFields": ["QID1", "QID3", "QID2"],
        "displayedValues: {
            "QID1": [1, 2],
            "QID3": [1, 2, 3],
            "QID2": [1, 2, 3]
        }
    }]
}

"""
