import datetime
import zipfile
import requests
from .lib import *
from dotenv import load_dotenv
import os


if (__name__=="__main__"):
  load_dotenv()

  url = os.environ["GTFS_URL"]
  output_filename = "gtfs.zip"
  data_dir = "gtfs"

  # get data from ztm api
  response = requests.get(url, headers={
    "Content-Type": "application/x-www-form-urlencoded", 
    "Accept": "application/octet-stream"
  })

  if (response.status_code != 200):
    print(f"Response failed: {response.status_code}")
    quit()

  with open(output_filename, "wb") as output_file:
    output_file.write(response.content)

  # unzip data
  os.makedirs(data_dir, exist_ok=True)
  
  with zipfile.ZipFile(output_file, "r") as zip_ref:
    zip_ref.extractall(data_dir)

  # save data to sqlite
  now = datetime.datetime.now().strftime("%H:%M:%S")
  now_weekday = datetime.datetime.now().strftime("%w")

  # there's no need to save calendars to db - it is needed only once a day, after data fetch
  todays_calendar = read_todays_calendar(data_dir + "/calendar.txt", now_weekday)

  # current_calendar = read_todays_calendar("./data/calendar.txt", WEEKDAYS[int(now_weekday)])

  # trip_h, trips = read_trips("./data/trips.txt", current_calendar)

  # stop_times_h, stop_times = read_stop_times("./data/stop_times.txt")

  
  
  
  # join trips and stop_times 
  # final_data = []
  # for stop_time in stop_times:
  #   for trip in trips:
  #     if stop_time["trip_id"] == trip["trip_id"]:
  #       final_data.append({
  #         "route_id": trip["route_id"],
  #         "trip_headsign": stop_time["stop_headsign"] or trip["trip_headsign"],
  #         "departure_time": stop_time["departure_time"]
  #       })

  # final_data.sort(key= lambda x: x["departure_time"])

  # for data in final_data[:20]:
  #   print(*data.values(), sep="\t")
