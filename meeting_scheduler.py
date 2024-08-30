import pandas as pd
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load your service account credentials
SERVICE_ACCOUNT_FILE = 'path/to/your/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('calendar', 'v3', credentials=credentials)


def create_event(name, job_id, job_name, start_time, email):
    event = {
        'summary': f'Interview for {job_name} (Job ID: {job_id})',
        'location': 'Virtual Meeting',
        'description': f'Interview with {name} for {job_name} (Job ID: {job_id})',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'America/Los_Angeles',  # Update this to your timezone
        },
        'end': {
            'dateTime': (start_time + timedelta(minutes=30)).isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'attendees': [{'email': email}],
        'conferenceData': {
            'createRequest': {
                'requestId': f"{name.replace(' ', '').lower()}-{job_id}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'},
            }
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 10},
            ],
        },
    }

    event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
    return event.get('hangoutLink')


def schedule_meetings(df, job_id, job_name):
    interview_time = datetime.strptime("09:00", "%H:%M")
    end_time = datetime.strptime("17:00", "%H:%M")
    lunch_start = datetime.strptime("12:00", "%H:%M")
    lunch_end = datetime.strptime("14:00", "%H:%M")

    for _, row in df.iterrows():
        if lunch_start <= interview_time < lunch_end:
            interview_time = lunch_end

        if interview_time >= end_time:
            break

        meeting_link = create_event(row['Name'], job_id, job_name, interview_time, row['Email'])

        email_content = f"""
        Subject: Interview Invitation for {job_name} (Job ID: {job_id})

        Dear {row['Name']},

        We are pleased to inform you that after reviewing your application, our HR team has decided to move forward with your application for the job ID {job_id}. 

        We would like to invite you to a virtual interview. Below are the details:

        Date: {interview_time.strftime('%Y-%m-%d')}
        Time: {interview_time.strftime('%I:%M %p')}
        Meeting Link: {meeting_link}

        Please be available at the scheduled time. If you need to reschedule, please let us know in advance.

        Best regards,
        HR Team
        """

        # Simulate sending email
        print(f"Email sent to {row['Email']}:\n{email_content}")

        # Increment interview time by 30 minutes
        interview_time += timedelta(minutes=30)
