"""
The purpose of this code snippet is to actually practice scraping the information and organzing the output for how I want it to be

Q69 Bus Tracker
Fetches real-time arrival times for the Q69 bus at
21 St / Ditmars Blvd using the MTA BusTime API.
"""

import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from twilio.rest import Client
import os

load_dotenv()

# Keep API key hidden, thats why theres a .env
API_KEY = os.getenv("MTA_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# Twilio number
TWILIO_FROM = os.getenv("TWILIO_FROM")
# my num
TWILIO_TO = os.getenv("TWILIO_TO")

# MTA stop ID for 21 St / Ditmars Blvd, heading towards steinway
STOP_ID = "553077"
URL = "https://bustime.mta.info/api/siri/stop-monitoring.json"
PARAMS = {
    "key": API_KEY,
    # transit agency ie MTA for the buses
    "OperatorRef": "MTA",
    # the actual stop were monitoring - the id of said stop
    "MonitoringRef": STOP_ID,
    # only getting info for this route in particular: Q69
    "LineRef": "MTABC_Q69"
}


def get_q69_arrivals() -> str:
    # Get request from MTA API
    response = requests.get(URL, params=PARAMS)
    # throw if the request failed
    response.raise_for_status()
    # parsing the response into a dict
    data = response.json()
    # API returns nested structure — extract from it to get the list of buses
    visits = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0].get("MonitoredStopVisit", [])

    if not visits:
        return "No buses right now."

    lines = ["HEY THE Q69's next arrival at 21 St / Ditmars Blvd IS:\n"]

    # only doing it for the next three buses
    for bus in visits[:3]:
        # MonitoredCall contains arrival info for this specific stop
        call = bus["MonitoredVehicleJourney"]["MonitoredCall"]
        # ExpectedArrivalTime is real-time — use AimedArrivalTime as backup plan
        eta_str = call.get("ExpectedArrivalTime") or call.get("AimedArrivalTime")
        # convert the ISO timestamp string into a datetime object
        eta = datetime.fromisoformat(eta_str)
        # get the current time in UTC so we can compare with the ETA
        now = datetime.now(timezone.utc)

        # calculate how many minutes until the bus arrives
        # However, show neg minutes if its passed
        #mins = max(0, int((eta - now).total_seconds() // 60))

        mins = max(0, round((eta - now).total_seconds() / 60)) # new formula, trying to see if its more accurate for the first sotp
        # PresentableDistance is a string which tells us the distance from stop
        distance = call["Extensions"]["Distances"]["PresentableDistance"]
        lines.append(f" IT'S {mins} min away  ({distance})\n")


    return "\n".join(lines)


def send_sms(message: str):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    #trying to verify why im not getting any numbers
    msg = client.messages.create(
    to=TWILIO_TO,
    from_=TWILIO_FROM,
    body=message
)

    print(f"SID: {msg.sid}")
    #print status to determine where im actually getting stuck
    #From terminal: Status: queued ie the script is working, but somethinfg on twilio end now
    print(f"Status: {msg.status}")


if __name__ == "__main__":
    try:
        arrival_message = get_q69_arrivals()
        # still prints locally too
        print(arrival_message)
        send_sms(arrival_message)
    except requests.RequestException as e:
        print(f"MTA API error: {e}")
    except Exception as e:
        print(f"Something went wrong: {e}")
