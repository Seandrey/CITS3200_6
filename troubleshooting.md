# TROUBLESHOOTING


* virtual ENV no permissions allowed
- set execution policy allow 
- https://stackoverflow.com/questions/18713086/virtualenv-wont-activate-on-windows
Set-ExecutionPolicy Unrestricted -Scope Process
.venv/scripts/activate

* Failed to find downloaded JSON
- error is based on what the Survery Title is called you must call it exactly its name so that it can find its path
- json_path = "MyQualtricsDownload/{NAME}.json"


* Adding Hosts or New Practicum Placements
- Add the New Units on local db before changing and updating the qualtrics data
- Add the New Locations in qualtrics and the data will be updated later in the database.

stack overflow set execution