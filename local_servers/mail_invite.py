import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import pytz
from typing import Literal
from fastmcp import FastMCP
from mcp.shared.exceptions import McpError
import sys
import uuid
import calendar
mcp = FastMCP(name="send-mail-invite")
load_dotenv()

tech_call = ["khajamdajmeer@gmail.com","junaidfaizan024@gmail.com"]
rec_call = ["dm2001mypc@gmail.com","khajamdajmeer@gmail.com","junaidfaizan024@gmail.com","saiteja001r@gmail.com","jashu1150@gmail.com","kadarisumanth7674@gmail.com"]


from datetime import datetime, timedelta

def get_timestamp_and_plus1hr_ms(date_str, time_str):
    """
    Takes date (YYYY-MM-DD) and time (HH:MM AM/PM) as strings.
    Returns:
        - Original timestamp in milliseconds
        - Timestamp + 1 hour in milliseconds
    """
    datetime_str = f"{date_str} {time_str}"
    dt = datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")

    # Format as YYYYMMDDTHHMMSS
    dt_compact = dt.strftime("%Y%m%dT%H%M%S")

    dt_plus1hr = dt + timedelta(hours=1)
    dt_plus1hr_compact = dt_plus1hr.strftime("%Y%m%dT%H%M%S")

    return dt_compact, dt_plus1hr_compact



@mcp.tool()
def send_calendar_invite(interview_type: Literal["recruiter","technical"], subject: str, title: str, date: str, time: str,discription : str) -> str:

    """
    Sends the Calender invite.

    This tool will send the callender invite for the users.

    Args:
        interview_type: The type of interview "recruiter" or "technical"
        subject: The subject or topic of the invite with name of the candidate.
        title: The title of the email.
        date: The date of interview in format (YYYY-MM-DD)
        time: The Time of the interivew (12 Hour format).
        discription: The discription about the invite with the client , candiate name,and will formated details available.
    Returns:
        A formatted string with response from the email sent.
    
    Example:
        send_calendar_invite("recruiter","The recrutier call is scheduled for Ramani","this is the invite for a recruiter call ",'2025-09-25',"12:30 PM","you ar invited to attend the recruter call for the Ramani on date at time from client meta the intervier linkedin profile or the url proviede is URL")
    
    """

    from_email = os.getenv('EMAIL_USER',"ajukhaja786@gmail.com")
    password = os.getenv("EMAIL_PASS","khenmdosprdmztuu")
    if not from_email or not password:
        return f"The from email or password not found"
    

    
    start_ts,end_ts = get_timestamp_and_plus1hr_ms(date,time)
    # end_ts = int(end_dt.astimezone(pytz.UTC).timestamp())

    try:
        to_mail = rec_call if interview_type == "recruiter" else tech_call
    except McpError as me:
        return f"McpError faced when sending the invite {e}"
    except Exception as e:
        return f"The {interview_type} is invalid"
    
    pst = pytz.timezone('US/Pacific')

    # Get current time in PST (will adjust for daylight saving automatically if in effect)
    now_pst = datetime.now(pst)

    # Format like DTSTAMP but without the trailing 'Z' (since it's not UTC)
    dtstamp_pst = now_pst.strftime('%Y%m%dT%H%M%S')
    
        
    # Generate a random UUID and append a domain (best practice for uniqueness)
    uid = f"{uuid.uuid4()}@gmail.com"
    def wrap_every_n_chars(s, n=75):
        return '\n'.join(s[i:i+n] for i in range(0, len(s), n))
    discriptions = wrap_every_n_chars(f"DESCRIPTION:{discription[-1]}")

    ics_content = f"""BEGIN:VCALENDAR
PRODID:-//Google Inc//Google Calendar 70.9054//EN
VERSION:2.0
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VTIMEZONE
TZID:America/Los_Angeles
X-LIC-LOCATION:America/Los_Angeles
BEGIN:STANDARD
TZOFFSETFROM:-0800
TZOFFSETTO:-0800
TZNAME:PST
DTSTART:{start_ts}
END:STANDARD
END:VTIMEZONE
BEGIN:VEVENT
DTSTART;TZID=America/Los_Angeles:{start_ts}
DTEND;TZID=America/Los_Angeles:{end_ts}
DTSTAMP:{dtstamp_pst}
ORGANIZER;CN=Ajmeer khaja:mailto:{from_email}
UID:{uid}"""

    for email in to_mail:
        txt = f"ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP= TRUE;X-NUM-GUESTS=0:mailto:{email}"
        ics_content += txt
    
    ics_one = f"""CREATED:{dtstamp_pst}
{discriptions}
LAST-MODIFIED:{dtstamp_pst}
LOCATION:
SEQUENCE:0
STATUS:CONFIRMED
{wrap_every_n_chars(f"SUMMARY:{subject}")}
TRANSP:OPAQUE
END:VEVENT
END:VCALENDAR
"""

    ics_content += ics_one
    
     # Main message container
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ",".join(to_mail)
    # msg.set_content(discription)

    # Alternative part for text
    alternative = MIMEMultipart('alternative')
    msg.attach(alternative)

    # Plain text content
    part_email = MIMEText(f"You have been invited to: {title} \n {discription}", "plain")
    alternative.attach(part_email)

    # Calendar content
    part_calendar = MIMEText(ics_content, "calendar;method=REQUEST;name=invite.ics", _charset="utf-8")
    part_calendar.add_header('Content-Disposition', 'inline; filename="invite.ics"')
    part_calendar.add_header('Content-Class', "urn:content-classes:calendarmessage")
    alternative.attach(part_calendar)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(from_email, password)
            smtp.sendmail(from_email, to_mail, msg.as_string())
            smtp.quit()
        print("Invite sent successfully.",file=sys.stderr)
        return f"The invite has been send successfully to {to_mail}"
    except McpError as me:
        print(me,file=sys.stderr)
        return f"McpError faced when sending the invite {me}"
    except Exception as e:
        print(e,file=sys.stderr)
        return f"Error faced when sending the invite {e}"



if __name__ == "__main__":
    # mcp.run(transport="streamable-http")
    mcp.run(transport="stdio")
