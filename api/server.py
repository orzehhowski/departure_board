import datetime
from aiohttp import web
import asyncio
import aiocron
import os
from .ztm_data_handler import *
from .globals import *

def get_departures(stop_id: str, current_datetime: datetime.datetime) -> list:
  weekday = current_datetime.strftime("%w")
  day = current_datetime.strftime("%Y%m%d")

  current_day_db = ""
  for file in os.listdir("db"):
    [files_start_date, files_end_date] = file.split(".")[0].split("_")
    if day >= files_start_date and day <= files_end_date:
      current_day_db = os.path.join("db", file)

  if current_day_db == "":
    print(f"Database for {day} not found : (")
    return []

  #read service for given day
  service = sqlite.get_todays_service(current_day_db, WEEKDAYS[int(weekday)])

  departures = sqlite.get_todays_stop_departures(current_day_db, stop_id, service)

  return departures

# GET / handler
async def handle(request: web.Request):
  limit = request.query.get("n", "10")
  # we don't validate stop_id - if it's wrong, there just will be 0 records returned
  stop_id = request.query.get("stop", "60")
  print(f"GET / ? n={limit} stop={stop_id}")


  if not limit.isnumeric():
    return web.json_response({"message": "n shoud be numeric!"}, status=400)
  
  limit = int(limit)

  # maximum value will be 100
  if limit > 100:
    limit = 100

  current_datetime = datetime.datetime.now()

  today_departures = await asyncio.to_thread(get_departures, stop_id, current_datetime)

  now = current_datetime.strftime("%H:%M:%S")
  after_midnight_departures = [list(x) for x in today_departures if x[2] >= "24:00:00"]
  today_departures = [x for x in today_departures if x[2] > now and x[2] < "24:00:00"]

  # for data in today_departures[:limit]:
  #   data = list(data)
  #   data[1] = f"{data[1]:28}"
  #   print(*data, sep="\t")

  if len(today_departures) < limit:
    # swap after midnight times to next day
    for departure in after_midnight_departures:
      departure[2] = f"{int(departure[2][:2]) - 24:02}{departure[2][2:]}"

    tommorow_datetime = current_datetime + datetime.timedelta(days=1)
    tommorow_departures = await asyncio.to_thread(get_departures, stop_id, tommorow_datetime)
    tommorow_departures_merged = [*after_midnight_departures, *list(tommorow_departures)]
    tommorow_departures_merged.sort(key= lambda x: x[2])

    for i in range(limit - len(today_departures)):
      if (i >= len(tommorow_departures_merged)):
        break
      today_departures.append(tommorow_departures_merged[i])

  return web.json_response({"departures": today_departures[:limit]}, status=200)

# task that will run once every day - on 23:50
async def fetch_data_task():
  print(f"[{datetime.datetime.now()}] Running data fetch")
  await asyncio.to_thread(fetch_data)
  print("Data fetch completed")

# we're defining cron running once a day data fetch on app startup
async def on_startup(app: web.Application):
  print(f"Setting daily data fetch schedule for \"{DATA_FETCH_CRON}\"")
  cron = aiocron.crontab(DATA_FETCH_CRON, func=fetch_data_task, start=True)
  app["cron"] = cron

# when server stops, cron is stopped
async def on_cleanup(app: web.Application):
  cron = app.get("cron")
  if cron:
    cron.stop()
    print("Data fetch schedule stopped")

if __name__ == "__main__":
  fetch_data()

  app = web.Application()
  app.add_routes([web.get("/", handle)])
  app.on_startup.append(on_startup)
  app.on_cleanup.append(on_cleanup)

  web.run_app(app, host="0.0.0.0", port=8080)