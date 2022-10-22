# https://icalendar.org/validator.html
# https://www.kanzaki.com/docs/ical/

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import icalendar
import datetime
import os.path
import requests
from dotenv import load_dotenv


def get_contacts():
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('people', 'v1', credentials=creds)

        # Call the People API and get birthdays of all connections
        results = service.people().connections().list(
            resourceName='people/me',
            personFields='names,birthdays',
            pageSize=1000,
            sortOrder='FIRST_NAME_ASCENDING').execute()
        connections = results.get('connections', [])
        return connections

    except HttpError as err:
        print(err)


def format_contacts(contacts):
    formatted_contacts = []
    for contact in contacts:
        name = contact['names'][0]['displayName']

        if 'birthdays' in contact:
            birthday = contact['birthdays'][0]['date']
            formatted_contacts.append({'name': name, 'birthday': birthday})

    return formatted_contacts


def create_ical(contacts):
    # create ical file with birthday events for each contact for the next 3 years with timezon Asia/Colombo
    cal = icalendar.Calendar()
    cal.add('prodid', '-//Birthday Calendar//The Lonely Lands//EN')
    cal.add('version', '2.0')
    cal.add('X-WR-CALNAME', 'Birthday Calendar')
    cal.add('NAME', 'Birthday Calendar')

    # loop through contacts and add events to calendar
    for contact in contacts:
        name = contact['name']
        birthday = contact['birthday']

        # list of years to add events for
        current_year = datetime.datetime.now().year
        years = [current_year, current_year + 1, current_year + 2]

        for index, year in enumerate(years):
            # create event
            event = icalendar.Event()
            event.add('DTSTAMP', datetime.datetime.now())

            uid = f"{index}-{''.join(name.split())}-{datetime.date(year, int(birthday['month']),int(birthday['day']))}-{year}"

            event.add('uid', uid)
            event.add('categories', ['Birthday'])
            event.add('sequence', year)

            # set event name
            if ('year' in contact['birthday']):
                event.add(
                    'summary',
                    f"{name}'s Birthday ({year - int(birthday['year'])})")
            else:
                event.add('summary', f"{name}'s Birthday")

            # set event date
            event.add(
                'dtstart',
                datetime.date(year, int(birthday['month']),
                              int(birthday['day'])))

            # end is a day after start
            event.add(
                'dtend',
                datetime.date(year, int(birthday['month']), int(
                    birthday['day'])) + datetime.timedelta(days=1))

            # add event to calendar
            cal.add_component(event)

    return cal.to_ical()


def main():
    requests.get(f"{os.environ['HEALTH_CHECK_URL']}/start")

    contacts = format_contacts(get_contacts())
    calendar = create_ical(contacts)

    with open('birthday.ics', 'wb') as file:
        file.write(calendar)

    requests.get(os.environ["HEALTH_CHECK_URL"])


load_dotenv()

if __name__ == '__main__':
    main()
