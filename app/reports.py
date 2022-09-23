# Build charts for google charts to display and report tables
# Author: David Norris (22690264), Joel Phillips (22967051)

from typing import Any, Optional
from sqlalchemy.orm.scoping import scoped_session
from app.models import *
from app import db
import random
import contextlib
from sqlalchemy import MetaData

# 500 Random names
names_list = ["Brandon Bell", "Victoria Little", "Samuel Wilkinson", "Charles Taylor", "Stephen Hopkins", "Justin Chan", "Matthew Hobbs", "George Morgan", "Donald Ritter", "Margaret Hamilton", "William Mullen", "Keith Simmons", "Roberta Boyle", "Tammy Matthews", "Ryan Stephens", "Helen Thompson", "Judith Smith", "Timothy Mack", "Lisa Hernandez", "Gabriel Willis", "Zachary Smith", "Sylvia Chen", "Sydney Johnson", "Cheryl Miller", "Casey Green", "Justin Miller", "Robert Welch", "Jesse Farley", "Courtney Wilson", "Craig Brown", "Christine Mendoza", "Danielle Juarez", "Bridget Blake", "Bailey Brown", "Juan Shannon", "Eric Mcclure", "Rachel Hudson", "Melissa Garcia", "Andrew Tran", "James Gonzalez", "Rachel Smith", "Christopher Morrow", "Shane Stark", "Earl Johnson", "Larry Moss", "Laurie Case", "Jennifer Garner", "Robert Ramos", "Chris Wilkins", "Maria Rice", "Margaret Jenkins", "Charles Ferguson", "Seth Jones", "Alex Thompson", "James Mcbride", "Annette Brown", "Jennifer Orozco", "Daniel Cannon", "Caleb Christensen", "Kathleen Smith", "Laura Hernandez", "Douglas Johnson", "Theresa Taylor", "Cynthia Mann", "Angelica Spencer", "Eileen Patel", "Elizabeth Thompson", "Richard Lee", "Sierra Daniels", "Christine Perez", "Barry Daniel", "Justin Bates", "Edwin Stone", "Paul Garner", "Randy Chapman", "Jamie Jones", "Alex Rose", "Melissa Williams", "Michelle Reed", "John Salinas", "Debra Michael", "Donna Hendricks", "Thomas Romero", "Robert Cochran", "Ryan Grant", "Terry Hunter", "Micheal Brooks", "Tricia Mathis", "Leslie House", "Andrew Davis", "Belinda Wade", "Nicole Wiggins", "Lisa Ferguson", "Taylor Hanson", "Mrs. Pamela Fleming", "Matthew Miles", "Toni Small", "Jordan Davis", "Tyler Drake", "Ralph Barber", "Paige Cook", "Penny Santos", "Amy King", "Anthony Smith", "Sarah Munoz", "Amy Howard", "Paul Butler", "Joshua Matthews", "Robin Phillips", "Angela Horton", "Michele Arnold", "Emily White", "David Bishop", "William Lewis", "Alison Klein", "Cory Jenkins", "Brian Moore", "John Ryan", "Clarence Ruiz", "Angel Holland", "Justin Schneider", "Matthew Jones", "James Acosta", "Miguel Walker", "Kathleen Long", "Megan Armstrong", "Sheena Mcdaniel", "Matthew Parker", "Benjamin Carter", "Ariel Vasquez", "Brett Kidd", "Suzanne Powers", "Justin Little", "Maxwell Meza", "Erica Vega", "Kimberly Miller", "Brittany Kelly", "Trevor Osborne", "John Hester", "Eric Baldwin", "Danielle Mccoy", "Evan Bailey", "Stephen Anderson", "Brian Hill", "Dustin Smith", "Dennis Melton", "Misty Jimenez", "Duane Rodriguez", "Andrew Silva", "Casey Collins", "Sarah Hines", "Laura Bradford", "Heather Myers", "Andrew Soto", "Jennifer Mendoza", "Amanda Wolf", "Mr. Cory Morrison MD", "Emily James", "Jennifer Gonzalez", "Stephanie Miller", "Jeffery Jones", "Danielle George", "Antonio Yang", "John Harris", "Linda Garcia", "Richard Flynn", "Allen Wright", "Michael Williams", "Joshua Kelley", "Samantha Rojas", "Christopher Ewing", "Andrew Li", "Madeline Davenport", "Roy Myers", "George Martin", "Michael Kelley", "Kristin Patterson", "Christopher Flores", "Michael Phillips", "Mrs. Julie Hudson", "Claire Baker", "Jeffrey Palmer DDS", "Arthur Hanna", "Richard King", "Wendy Wilson", "Jo Cooper", "Tara Brown", "Brett Pitts", "Matthew Butler", "Benjamin Johnson", "Paul Fox", "Michael Richard", "Jennifer Smith", "Bonnie Chase", "Sara Mcknight", "Robert Short", "Michelle Tanner", "Karen Villanueva", "Eric Walters", "Allen Weber", "Robin Parrish", "Julie Hutchinson DVM", "Veronica Russell", "Sarah Weaver", "Ronnie Griffith", "Brenda Ramirez", "John Goodman", "Tiffany Wagner", "Michael Richardson", "Samuel Williams", "Christopher Hill", "Nathan Lynch", "Michael Powers", "Patricia Banks", "Deanna Baldwin", "Joshua Torres", "Earl Dalton", "Charles Munoz", "Douglas Evans", "Matthew Garcia", "Julia Hubbard", "Andrea White", "Jerry Dodson", "Angela Morris", "Sherri Reid", "Nicole Jones DVM", "Gloria James", "Steven Blake", "Paul Bradley", "Mary Guerrero", "Andrew Cruz", "Paul Scott", "Misty Hicks", "Tracy Hunter", "Mackenzie Carroll", "Amy Collins", "Shannon Vargas", "Katrina Anderson", "David Anderson", "Natalie Brown DDS", "Ashley Hughes", "Brian Richardson", "Lisa Bentley", "Colton Fernandez", "Susan Singh", "John Leonard", "Mark Turner", "Jeremy Garcia", "Sydney Richard", "Shannon Cooper", "Willie Briggs",
              "Denise Knight", "Mark Moses", "Daniel Freeman", "Glen Romero", "Tiffany Villarreal", "Robert Morris", "Amber Thomas", "Phillip Henson", "Michelle Miller", "James Ross", "Samantha Kelley", "Joshua Brown", "Joseph Walker", "Laurie Shaw", "Ashley Hill", "Brian Wallace", "Richard Morrison", "Ronald Arnold MD", "Jane Bennett", "Whitney Hurst", "Samantha Phillips", "Daniel Pena", "Sharon Greene", "Anne Cain", "Kyle Huff", "Dawn Sanchez", "Richard Orr", "Angela Hayes", "Courtney Ferguson", "Jason Myers", "Ashley Hansen", "Sarah White", "Katie Kirby", "Kimberly Mitchell", "Ronnie Bailey", "Veronica Grant", "Kevin Gonzalez", "Pamela Wheeler", "Eddie Ramirez", "Shelly Perry", "Bailey Callahan", "Stacey Thomas", "Isabel Berger", "James Knight", "Kevin Reynolds", "Susan Gordon", "Brittany Banks", "Roy Small", "Deanna Sharp", "William Cox", "Linda Burnett", "Cathy Kennedy", "Jennifer Smith", "Pam Black", "Tonya Hughes", "Alex Nguyen", "Rachel Carroll", "Keith Murray", "Colleen Martin", "Kelly Edwards", "Michael David", "Corey Ortiz", "Alyssa Harrell", "Sharon Salazar", "Gabriela Williams", "Mark Reynolds", "Kimberly Butler", "Alicia Stephenson", "Mr. Jeremy Moon DDS", "Loretta Edwards", "Lisa Dickson", "Janice Brewer", "Tracey Douglas", "Anthony Miller", "Jennifer Jones MD", "Bethany Holden", "Mary Mclean", "John Chapman", "Regina Johnson", "Daniel Evans", "Lori Lyons", "Anthony Thomas", "Jesse Ware", "Christopher Steele", "Jenny Scott", "Christopher Jones", "Angela Lopez", "Andrew Daugherty", "Daniel Calhoun", "Oscar Mckenzie", "Abigail Anderson", "Jesus Cooper", "Stacie Ponce", "Stephen Lewis", "Jessica Fitzgerald", "Mary Roberts", "Thomas Rasmussen", "Larry Rodgers", "Debra Carter", "John Day", "Carrie Lee", "Rachel Bell", "Patrick Mejia", "Brandon Roberts", "Donna Mcdonald", "Sandra Perez", "Katherine Hunt", "Lisa Valencia", "Danielle Murphy", "Cynthia Carter", "Danielle Young", "Nicole Miles", "Henry Spencer", "Steven Barker DDS", "Lawrence Reynolds", "Mary Larson", "Brian Mcmillan", "Laura Day", "Brandon Gonzalez", "James Gonzalez", "Christopher Rodriguez", "Hunter Edwards", "Alison Williams", "Shelby Gonzalez", "Edward Lambert", "Julie Peterson", "Michael Brown", "Virginia Stuart", "William Chen", "Cassandra Kelly", "Jennifer Lambert", "Ms. Tara Gonzalez", "Steven Sosa", "Lindsay Rivera", "Jesse Black", "Jessica Mendoza", "Jay Rogers", "Justin Mcdonald", "Kelli Bowen", "Mr. Brian Williamson", "Ronald Jackson", "Laurie Mccullough", "Alexis Delgado", "Robert Burnett III", "Priscilla Adams", "Gwendolyn Horton", "Melissa Lewis", "Diana Watson", "Marissa Thompson", "Sheila Hunter", "Mr. Shane Gregory", "Lisa Oconnor", "Kelly Allen", "Carrie Lopez", "Kenneth Anderson", "Ruben Collier", "Mark Odom", "Joel Snow", "Andrew Johns", "Taylor Campbell", "Terri Ayala", "Miss Rebecca Montgomery", "Kristen Gomez", "April Barnett", "Annette Santos", "Thomas Ortiz", "Mr. Matthew Collins", "Michele Hale", "Melissa Diaz", "Pamela Gilmore", "Michael Murphy", "Elizabeth Moreno", "Travis Becker", "Allen Cantrell", "Tracy Cook", "Kyle Mcclain", "Jeremy Clark", "Ashley Weber", "Jennifer Roberts", "Robert Reynolds", "Gary Smith", "Lindsey West", "Charles Stevenson", "Julie Travis", "Mallory Potter", "Cindy Lewis", "Eric Williams", "Jeremiah Snyder", "Shane Smith", "Janice Bass", "Holly Weiss", "Sarah Duncan", "Javier Smith", "Monica Fitzpatrick", "Sandra Rasmussen", "Emily Little", "Corey Rice MD", "Robin Brown", "Bryan Wilson", "Rachel Whitney", "Daniel Pena", "Tammy Santana", "Paul Levy", "Wendy Burke", "Brenda Summers", "Jillian Payne", "Gary Brown", "Jennifer Gonzalez", "Leslie Cole", "Amanda Alvarado", "Benjamin Macias", "Steven Black", "Pamela Patterson", "Shannon Wright", "Eric Williams", "Nicholas Miranda", "Robert Graham", "Savannah Adams", "Ronald Mills", "Ashley Freeman", "Ryan Key", "Manuel Shelton", "Wesley Hopkins", "Ashley Christensen", "Madeline Floyd", "Joshua Perry", "Anthony Mcclain", "Michelle Hall", "Brian Perry", "Philip Rogers", "Crystal Smith", "Monica Smith", "Ryan Edwards", "Mary Coleman", "Aaron Dorsey", "Charles Campbell", "Gary Stevenson", "Mackenzie Ryan", "Wanda Santana", "Anthony Johnson", "Deanna Mcknight", "Gregory Hernandez", "David Guzman", "Amanda Harper", "Wanda Rich", "Crystal Jones", "Mary Rodriguez", "Kelsey Rodriguez", "Mary White"]

d = (
    'Health/Fitness',
    'Sport & Performance',
    'Healthy Aging',
    'Paediatrics & Young People',
    'Mental Health & Wellness',
    'Community Wellness',
    'Employment Health & Wellness',
    'Clinical Case'
)
a = (
    'Exercise Assessment',
    'Exercise Prescription',
    'Exercise Delivery',
    'Other'
)
l = (
    'UWA Exercise & Performance Centre',
    'WACRH (Geraldton)',
    'Agility Rehabilitation',
    'Curtin Stadium'
    'Fiona Stanley Hospital',
    'Guardian Exercise Rehabilitation',
    'Health Care WA',
    'HFRC',
    'Made to Move Rehabilitation Gym',
    'Neuromoves',
    'O2 Active',
    'Redimed',
    'Reps Movement',
    'The Exercise Therapist',
    'Other/Self Directed',
    'Shenton College'
)
# 20 random names from the list = 20 supervisors
s = [random.choice(names_list) for _ in range(1, 20)]


def teardown_db():
    """removes all db table entries except user table"""
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        if '%s' % table != 'user':
            print('Clear table %s' % table)
            db.session.execute(table.delete())
    db.session.commit()


def fill_db_multiple_students(num):
    """fill the db with n students equal to param num. 
    student id start at 2200000 and increment by 1 to 22000000 + num"""
    count = 0
    for domain in d:
        if count < 3:
            i = Domain(domain=domain, core=True)
        else:
            i = Domain(domain=domain, core=False)
        db.session.add(i)
        count += 1

    for activity in a:
        i = Activity(activity=activity)
        db.session.add(i)

    for location in l:
        i = Location(location=location)
        db.session.add(i)

    for supervisor in s:
        i = Supervisor(name=supervisor)
        db.session.add(i)

    db.session.commit()

    for i in range(0, num):
        fill_db_student_random_hours(22000000 + i, random.choice(names_list))


def fill_db_student_random_hours(studentid, name):
    """fill db with a student entry with id of param student id and name name, also generate 50 activity entries"""
    st = Student(studentid=studentid, name=name)
    db.session.add(st)
    for i in range(0, 50):
        al = ActivityLog(studentid=studentid, domainid=random.randint(1, len(d)), activityid=random.randint(1, len(
            a)), locationid=random.randint(1, len(l)), supervisorid=random.randint(1, len(s)), minutes_spent=random.randint(40, 200), record_date=date.today())
        db.session.add(al)

    db.session.commit()


def gen_total_row(domains: list, activity_names: list[Activity], core: Optional[bool] = None) -> dict:
    """Sums activities and AEP domain/activity table to generate a total row"""
    total_row = {"domain": "Total"}
    total: int = 0
    for activity in activity_names:
        sum: int = 0
        for row in domains:
            if core is None or row.core == core:
                sum += row[f"{activity.activityid}"]
        total_row[activity.activityid] = sum
        total += sum
    total_row["total"] = total
    return total_row


def build_chart_from_table(title: str, domain_table: list, activities: list[Activity], core: Optional[bool] = None) -> dict[str, Any]:
    """Populate chart from AEP domain/activity table data"""
    # category info
    domain_names: list = ["Category"]
    # number of domains that are core, or not core, or whatever was desired
    num_domains_of_type: int = 0

    weird_activity_map: list[list] = [domain_names]
    for activity in activities:
        weird_activity_map.append([activity.activity])

    for domain in domain_table:
        if core is None or domain.core == core:
            domain_names.append(domain.domain)
            num_domains_of_type += 1

            for activity in activities:
                weird_activity_map[activity.activityid].append(
                    round(domain[activity.activityid], 2))

    # generate desired type of total row
    total_row = gen_total_row(domain_table, activities, core)

    # add totals and annotation end quote to end of each
    for activity in activities:
        weird_activity_map[activity.activityid].append(
            round(total_row[activity.activityid], 2))
        weird_activity_map[activity.activityid].append("")

    # this is for google charts annotations
    domain_names.append({'role': 'annotation'})
    domain_names.append({'role': 'annotation'})

    type_title = ""
    if core is not None:
        type_title = " Core" if core else " Additional"
    data = {
        'title': title + type_title,
        'graph': weird_activity_map,
        'len': num_domains_of_type,
        "activities": [activity.activity for activity in activities],
        "total": round(total_row["total"], 2)
    }
    return data


def build_chart(key: str, value: int, core: bool = True) -> dict[str, Any]:
    """format some queries to populate a dictionary the way google charts expects, this passed after using json.dumps() into a jinja macro data structure"""
    title: str = ''
    if key == 'student':
        q = db.session.query(ActivityLog).filter_by(
            studentid=value).order_by("domainid").all()
        title = db.session.query(Student).filter_by(
            studentid=value).first().name
    elif key == 'location':
        q = db.session.query(ActivityLog).filter_by(
            locationid=value).order_by("domainid").all()
        title = db.session.query(Location).filter_by(
            locationid=value).first().location

    q: list[Domain] = db.session.query(Domain).filter_by(core=core).all()
    domains: list = [domain.domain for domain in q]
    length = len(domains)
    domains.insert(0, 'Category')
    # this is for google charts annotations
    domains.append({'role': 'annotation'})
    # this is for google charts annotations
    domains.append({'role': 'annotation'})

    data = {
        'title': title + ' Core' if core else title + ' Additional',
        'graph': [domains],
        'total': 0,
        'len': length
    }

    q: list[Activity] = db.session.query(Activity).all()
    data['activities'] = [act.activity for act in q]
    for activity in q:
        activityHours: list = [0] * data['len']
        activityHours.insert(0, activity.activity)
        p = db.session.query(
            ActivityLog.domainid,
            func.sum(ActivityLog.minutes_spent).label('total'),
            Domain.core,
        ).join(Activity.logs
               ).filter(Domain.core == core, Domain.domainid == ActivityLog.domainid
                        ).filter(ActivityLog.activityid == activity.activityid
                                 ).group_by(ActivityLog.domainid
                                            ).all()

        total = 0
        for domain in p:
            activityHours[domain[0] if core else domain[0] -
                          3] = round(domain[1] / 60, 2)
            total += round(domain[1] / 60, 2)
        data['total'] += round(total, 2)
        activityHours.append(total)  # this is for google charts annotations
        activityHours.append('')  # this is for google charts annotations

        data['graph'].append(activityHours)

    return data


def get_student_info(studentid: int) -> dict[str, Any]:
    """Generates data used for student page"""

    domains = get_domain_table([ActivityLog.studentid == studentid])

    activity_names: list[Activity] = Activity.query.order_by(
        Activity.activityid).all()

    total_row = gen_total_row(domains, activity_names)

    s = Student.query.filter_by(studentid=studentid).one()
    data = {
        "date_generated": date.today().isoformat(),
        "student": s,
        "domains": domains,
        "activity_names": activity_names,
        "total_row": total_row,
        "core": build_chart_from_table(f"{s.name}", domains, activity_names),
    }

    # here we should also add data for location and domain, currently only gains graphs
    return data


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

    # ensure this is in desired order
    activities: list[Activity] = Activity.query.order_by(
        Activity.activityid).all()
    # list of subqueries for each column (i.e. each activity type)
    col_subqs: list = []
    for activity in activities:
        col = get_domain_col(activity.activity, flist)
        col_subqs.append(col)
    total = get_domain_col(None, flist)

    table = session.query(total.c.domain.label("domain"), *[col_subqs[i].c.hours.label(
        f"{activities[i].activityid}") for i in range(0, len(col_subqs))], total.c.hours.label("total"), total.c.core.label("core"))
    # join each col_subq
    for col_subq in col_subqs:
        table = table.join(col_subq, col_subq.c.domainid == total.c.domainid)
    # ensure ordered by domainid
    table = table.order_by(total.c.domainid).all()

    return table


def get_year_flist(year: int) -> list:
    """Returns an flist for the year given, to pass into get_domain_table()"""
    return [ActivityLog.record_date.between(date(year, 1, 1), date(year, 12, 31))]


def get_cohort_info(year: int) -> dict[str, Any]:
    """Generates data used for cohort page"""
    domains = get_domain_table(get_year_flist(year))

    activity_names: list[Activity] = Activity.query.order_by(
        Activity.activityid).all()

    # add "total" row at bottom
    total_row = gen_total_row(domains, activity_names)

    data = {
        "year": year,
        "domains": domains,
        "activity_names": activity_names,
        "total_row": total_row,
        "core": build_chart_from_table(f"Cohort {year}", domains, activity_names, True),
        "additional": build_chart_from_table(f"Cohort {year}", domains, activity_names, False)
    }
    return data


def get_location_info(location_id: int):
    """Generates data used for location page"""
    session: scoped_session = db.session

    # find location name
    loc_name = Location.query.filter_by(locationid=location_id).one().location

    # find hours by supervisor for that location
    sup_hours: list = session.query(Supervisor.name.label("supervisor"), (func.sum(ActivityLog.minutes_spent) / 60.0).label(
        "hours")).join(ActivityLog).filter_by(locationid=location_id).group_by(ActivityLog.supervisorid).all()

    domains = get_domain_table([ActivityLog.locationid == location_id])

    activity_names: list[Activity] = Activity.query.order_by(
        Activity.activityid).all()

    # add "total" row at bottom
    total_row = gen_total_row(domains, activity_names)

    data = {
        "location": loc_name,
        "date_generated": date.today().isoformat(),
        "sup_hours": sup_hours,
        "domains": domains,
        "activity_names": activity_names,
        "total_row": total_row,
        "core": build_chart_from_table(f"{loc_name}", domains, activity_names, True),
    }
    return data
