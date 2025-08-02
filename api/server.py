import datetime
from aiohttp import web
import asyncio
from .ztm_data_handler import *
from .globals import *

def get_departures(stop_id: str, current_datetime: datetime.datetime) -> list:
  weekday = current_datetime.strftime("%w")
  day = current_datetime.strftime("%Y%m%d")

  current_day_db = ""
  for file in os.listdir(DB_DIR):
    [files_start_date, files_end_date] = file.split(".")[0].split("_")
    if day >= files_start_date and day <= files_end_date:
      current_day_db = os.path.join(DB_DIR, file)

  if current_day_db == "":
    print("Today's database not found : (")
    return []

  print(f"Today's database: {current_day_db}")

  #read service for given day
  service = sqlite.get_todays_service(current_day_db, WEEKDAYS[int(weekday)])

  departures = sqlite.get_todays_stop_departures(current_day_db, stop_id, service)

  return departures

async def handle(request: web.Request):
  limit = request.query.get("n", "10")
  # we don't validate stop_id - if it's wrong, there just will be 0 records returned
  stop_id = request.query.get("stop", "60")

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

  return web.json_response({"stop": stop_id, "departures": today_departures[:limit]}, status=200)

if __name__ == "__main__":
  app = web.Application()
  app.add_routes([web.get("/", handle)])
  web.run_app(app, host="0.0.0.0", port=8080)