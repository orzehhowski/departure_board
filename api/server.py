from http.server import BaseHTTPRequestHandler, HTTPServer
import datetime
import json
from urllib.parse import parse_qs, urlparse
from aiohttp import web
import asyncio
from .ztm_data_handler import *
from .globals import *

def get_today_departures(stop_id: str) -> list:
  now_weekday = datetime.datetime.now().strftime("%w")
  today = datetime.datetime.now().strftime("%Y%m%d")

  todays_db = ""
  for file in os.listdir(DB_DIR):
    [files_start_date, files_end_date] = file.split(".")[0].split("_")
    if today >= files_start_date and today <= files_end_date:
      todays_db = os.path.join(DB_DIR, file)

  if todays_db == "":
    print("Today's database not found : (")
    return []

  print(f"Today's database: {todays_db}")

  #read todays service
  todays_service = sqlite.get_todays_service(todays_db, WEEKDAYS[int(now_weekday)])

  today_departures = sqlite.get_todays_stop_departures(todays_db, stop_id, todays_service)

  return today_departures

async def handle(request: web.Request):
  limit = int(request.query.get("n", "10"))
  stop_id = request.query.get("stop", "60")

  today_departures = await asyncio.to_thread(get_today_departures, stop_id)

  now = datetime.datetime.now().strftime("%H:%M:%S")
  today_departures = [x for x in today_departures if x[2] > now]

  for data in today_departures[:limit]:
    data = list(data)
    data[1] = f"{data[1]:28}"
    print(*data, sep="\t")

  return web.json_response({"departures": today_departures[:limit]}, status=200)

if __name__ == "__main__":
  app = web.Application()
  app.add_routes([web.get("/", handle)])
  web.run_app(app, host="0.0.0.0", port=8080)