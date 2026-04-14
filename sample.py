"""
The purpose of this code snippet is to actually practice scraping the information and organzing the output for how I want it to be

Q69 Bus Tracker
Fetches real-time arrival times for the Q69 bus at
21 St / Ditmars Blvd using the MTA BusTime API.
"""

import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
import os

load_dotenv()

#Keep API key hidden, thats why theres a .env
API_KEY = os.getenv("MTA_API_KEY")
#MTA stop ID for 21 St / Ditmars Blvd, heading towards steinway
STOP_ID = "553077"

url = "https://bustime.mta.info/api/siri/stop-monitoring.json"

params = {
    "key": API_KEY,
    #transit agency ie MTA for the buses
    "OperatorRef": "MTA",
    #the actual stop were monitoring - the id of saif stop
    "MonitoringRef": STOP_ID,
    #only getting info for this route in particular: Q69
    "LineRef": "MTABC_Q69"
}

#Get request from MTA API
response = requests.get(url, params=params)
#parsing the response into a dict
data = response.json()

#API returns nested structure —  extract from it to get the list of buses.
visits = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0].get("MonitoredStopVisit", [])

if not visits:
    print("No buses right now.")
else:
    print("HEY THE Q69's next arrival at 21 St / Ditmars Blvd IS:\n")
    #only doing it for the next three buses
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
        #However, show neg minutes if its passed
        mins = max(0, int((eta - now).total_seconds() // 60))
        
        #PresentableDistance is a string which tells us the distance from stop
        distance = call["Extensions"]["Distances"]["PresentableDistance"]
        
        print(f" IT'S {mins} min away  ({distance})")