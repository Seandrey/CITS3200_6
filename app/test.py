from datetime import datetime

def convert_date_string(date_string):
    date_formats = ["%d/%m/%Y", "%d,%m,%y", "%d/%m/%Y"]
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_string, date_format)
            return date_obj.strftime("%d/%m/%Y")
        except ValueError:
            pass
    raise ValueError("Invalid date format: " + date_string)

