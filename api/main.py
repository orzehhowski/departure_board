import datetime
import zipfile
import requests
from .lib import *
from . import sqlite
from dotenv import load_dotenv
import os

def save_data_in_db(db_dir, db_name) -> None:
    os.makedirs(db_dir, exist_ok=True)

    # clear db before saving new data - just in case
    if os.path.exists(db_name):
      print("pruning database...")
      sqlite.prune_db(db_name)

    sqlite.init_db(db_name)

    # read calendar from file and save it to db
    print("Reading calendar from file...")
    calendar = read_data(os.path.join(data_dir, "calendar.txt"))

    print("Saving calendar to db...")
    sqlite.create_calendar(db_name, calendar)

    # read trips from file and save it to db
    print("Reading trips from file...")
    trips = read_data(os.path.join(data_dir, "trips.txt"))

    print("Saving trips to db...")
    sqlite.create_trips(db_name, trips)

    # read stop_times from file and save it to db
    print("Reading stop times from file...")
    stop_times_h, stop_times = read_stop_times(os.path.join(data_dir, "stop_times.txt"), "60")
    
    print("Saving stop times to db...")
    sqlite.create_stop_times(db_name, stop_times)

if (__name__=="__main__"):
  load_dotenv(override=True)
  url = os.environ["GTFS_URL"]
  output_filename = "gtfs.zip"
  data_dir = "gtfs"
  db_dir = "db"

  now_weekday = datetime.datetime.now().strftime("%w")
  now = datetime.datetime.now().strftime("%H:%M:%S")
  today = datetime.datetime.now().strftime("%Y%m%d")

  # data processing flags - for testing
  flag_download_new_data = False
  flag_save_data_in_db = False


  # 1. get data from ztm api
  if flag_download_new_data:
    print(f"fetching data from {url}...")
    response = requests.get(url, headers={
      "Content-Type": "application/x-www-form-urlencoded", 
      "Accept": "application/octet-stream"
    })

    if (response.status_code != 200):
      print(f"Response failed: {response.status_code}")
      exit()

    with open(output_filename, "wb") as output_file:
      output_file.write(response.content)
    
    # unzip data

    print("unzipping file...")

    os.makedirs(data_dir, exist_ok=True)
    
    with zipfile.ZipFile(output_filename, "r") as zip_ref:
      zip_ref.extractall(data_dir)

  else:
    print("skipping new data fetch")

  # save data to sqlite

  # get start and end date
  start_date, end_date =  read_feed_dates(os.path.join(data_dir, "feed_info.txt"))
  
  db_name = f"{start_date}_{end_date}.db"

  # search for existing databases and check if the new one overrides other
  print("checking if the new database overrides old ones...")
  for file in os.listdir(db_dir):
    if not file == db_name:
      [files_start_date, files_end_date] = file.split(".")[0].split("_")
      # if yes, update the old file's name
      if files_end_date > start_date:
        new_end_date = (datetime.datetime.strptime(start_date, "%Y%m%d") - datetime.timedelta(days=1)).strftime("%Y%m%d")
        new_filename = f"{files_start_date}_{new_end_date}.db"
        print(f"renaming db {file} to {new_filename}")
        os.rename(os.path.join(db_dir, file), os.path.join(db_dir, new_filename))

  if flag_save_data_in_db:
    save_data_in_db(db_dir, os.path.join(db_dir, db_name))
  else:
    print("skipping saving data to database")


  # 4. search db applying for today
  todays_db = ""
  for file in os.listdir(db_dir):
    [files_start_date, files_end_date] = file.split(".")[0].split("_")
    if today >= files_start_date and today <= files_end_date:
      todays_db = os.path.join(db_dir, file)

  if todays_db == "":
    print("Today's database not found : (")
    exit()

  print(f"Today's database: {todays_db}")

  #read todays service
  todays_service = sqlite.get_todays_service(todays_db, WEEKDAYS[int(now_weekday)])

  today_departures = sqlite.get_todays_stop_departures(todays_db, "60", todays_service)

  today_departures = [x for x in today_departures if x[2] > now]

  for data in today_departures[:20]:
    data = list(data)
    data[1] = f"{data[1]:28}"
    print(*data, sep="\t")