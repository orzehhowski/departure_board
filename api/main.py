import datetime
import zipfile
import requests
from .lib import *
from . import sqlite
from dotenv import load_dotenv
import os


if (__name__=="__main__"):
  load_dotenv()
  url = os.environ["GTFS_URL"]
  output_filename = "gtfs.zip"
  data_dir = "gtfs"

  # data processing flags - for testing
  download_new_data = True
  save_data_in_db = True


  # 1. get data from ztm api
  if download_new_data:
    response = requests.get(url, headers={
      "Content-Type": "application/x-www-form-urlencoded", 
      "Accept": "application/octet-stream"
    })

    if (response.status_code != 200):
      print(f"Response failed: {response.status_code}")
      quit()

    with open(output_filename, "wb") as output_file:
      output_file.write(response.content)


  # 2. unzip data

  os.makedirs(data_dir, exist_ok=True)
  
  with zipfile.ZipFile(output_filename, "r") as zip_ref:
    zip_ref.extractall(data_dir)


  # 3. save data to sqlite

  now_weekday = datetime.datetime.now().strftime("%w")
  now = datetime.datetime.now().strftime("%H:%M:%S")

  # there's no need to save calendars to db - it is needed only once a day, after data fetch
  todays_calendar = read_todays_calendar(os.path.join(data_dir, "calendar.txt"), WEEKDAYS[int(now_weekday)])
  print(todays_calendar)

  if save_data_in_db:

    # clear db before saving new data
    if os.path.exists(os.environ["DB_FILENAME"]):
      print("pruning database...")
      sqlite.prune_db()

    sqlite.init_db()

    # read todays trips from file and save it to db
    print("Reading trips from file...")
    trips_h, trips = read_trips(os.path.join(data_dir, "trips.txt"), todays_calendar)

    print("Saving trips to db...")
    sqlite.create_trips(trips)

    # read stop_times from file and save it to db
    print("Reading stop times from file...")
    stop_times_h, stop_times = read_stop_times(os.path.join(data_dir, "stop_times.txt"))
    
    print("Saving stop times to db...")
    sqlite.create_stop_times(stop_times)


  # 4. get data from db
  today_departures = sqlite.get_todays_stop_departures("60", todays_calendar)

  today_departures = [x for x in today_departures if x[2] > now]

  for data in today_departures[:20]:
    print(*data, sep="\t")