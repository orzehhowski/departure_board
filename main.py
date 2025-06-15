import datetime

WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

def printTable(header: list, values: list[dict]) -> None:
  print(*header, sep="\t")
  for el in values:
    print(*el.values(), sep="\t")

def printCoords(values: list[dict], codeKey="stop_code", latKey="stop_lat", lonKey="stop_lon") -> None:
  [print(f"{val[codeKey]}: ({val[latKey]},{val[lonKey]})") for val in values]

def readStops(filename: str) -> tuple[list[str], list[dict]]:
  with open(filename, "r", encoding="utf8") as stopsFile:
      header = []
      stops = []
      
      for line in stopsFile:
        if len(header) == 0:
          # skip \n and weird sign on the beginning
          header = line[1:-1].split(",")
          continue

        values = {headerVal: value for (headerVal, value) in zip(header, line[:-1].split(","))}
        if values["stop_code"].startswith("\"ZERO"):
          stops.append(values)
      return header, stops
  
def readTrips(filename: str, serviceId) -> tuple[list[str], list[dict]]:
  with open(filename, "r", encoding="utf8") as tripsFile:
    header = []
    trips = []
    
    for line in tripsFile:
      if len(header) == 0:
        # skip \n and weird sign on the beginning
        header = line[1:-1].split(",")
        continue

      values = {headerVal: value for (headerVal, value) in zip(header, line[:-1].split(","))}
      if values["service_id"] == serviceId:
        trips.append(values)
    return header, trips
    
def readStopTimes(filename: str) -> tuple[list[str], list[dict]]:
  with open(filename, "r", encoding="utf8") as stopTimesFile:
    header = []
    stopTimes = []
    
    for line in stopTimesFile:
      if len(header) == 0:
        # skip \n and weird sign on the beginning
        header = line[1:-1].split(",")
        continue

      values = {headerVal: value for (headerVal, value) in zip(header, line[:-1].split(","))}
      if values["stop_id"] == "60":
        stopTimes.append(values)
    return header, stopTimes
  
def readTodaysCalendar(filename: str, today: str) -> str:
  with open(filename, "r", encoding="utf8") as calendarFile:
    header = []

    for line in calendarFile:
      if len(header) == 0:
        # skip \n and weird sign on the beginning
        header = line[1:-1].split(",")
        continue

      values = {headerVal: value for (headerVal, value) in zip(header, line[:-1].split(","))}
      if values[today] == "1":
        return values["service_id"]
  
  # default value
  return "1"

if (__name__=="__main__"):
  now = datetime.datetime.now().strftime("%H:%M:%S")
  nowWeekday = datetime.datetime.now().strftime("%w")
  currentCalendar = readTodaysCalendar("./data/calendar.txt", WEEKDAYS[int(nowWeekday)])

  tripH, trips = readTrips("./data/trips.txt", currentCalendar)

  stopTimesH, stopTimes = readStopTimes("./data/stop_times.txt")

  stopTimes = [x for x in stopTimes if x["trip_id"].startswith(f"\"{currentCalendar}")]
  stopTimes = [x for x in stopTimes if x["departure_time"] > now]
  stopTimes.sort(key=lambda x: x["departure_time"])
  
  # join trips and stop_times 
  finalData = []
  for stopTime in stopTimes:
    for trip in trips:
      if stopTime["trip_id"] == trip["trip_id"]:
        finalData.append({
          "route_id": trip["route_id"],
          "trip_headsign": stopTime["stop_headsign"] or trip["trip_headsign"],
          "departure_time": stopTime["departure_time"]
        })

  finalData.sort(key= lambda x: x["departure_time"])

  for data in finalData[:20]:
    print(*data.values(), sep="\t")
