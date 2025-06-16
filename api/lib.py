WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]

# prints data with tabs
def print_table(header: list, values: list[dict]) -> None:
  print(*header, sep="\t")
  for el in values:
    print(*el.values(), sep="\t")

# prints coordinates for stops
def print_coords(values: list[dict], code_key="stop_code", lat_key="stop_lat", lon_key="stop_lon") -> None:
  [print(f"{val[code_key]}: ({val[lat_key]},{val[lon_key]})") for val in values]

# reads my stops from stops.txt file
def read_stops(filename: str) -> tuple[list[str], list[dict]]:
  with open(filename, "r", encoding="utf8") as stops_file:
      header = []
      stops = []
      
      for line in stops_file:
        if len(header) == 0:
          # skip \n and weird sign on the beginning
          header = line[1:-1].split(",")
          continue

        values = {header_val: value for (header_val, value) in zip(header, line[:-1].split(","))}
        if values["stop_code"].startswith("\"ZERO"):
          stops.append(values)
      return header, stops

# reads all records with given service_id (weekday) from stop_times.txt file
def read_trips(filename: str, service_id) -> tuple[list[str], list[dict]]:
  with open(filename, "r", encoding="utf8") as trips_file:
    header = []
    trips = []
    
    for line in trips_file:
      if len(header) == 0:
        # skip \n and weird sign on the beginning
        header = line[1:-1].split(",")
        continue

      values = {header_val: value for (header_val, value) in zip(header, line[:-1].split(","))}
      if values["service_id"] == service_id:
        trips.append(values)
    return header, trips
    
# reads all records for given stop_id from stop_times.txt file 
def read_stop_times(filename: str, stop_id="60") -> tuple[list[str], list[dict]]:
  with open(filename, "r", encoding="utf8") as stop_times_file:
    header = []
    stopTimes = []
    
    for line in stop_times_file:
      if len(header) == 0:
        # skip \n and weird sign on the beginning
        header = line[1:-1].split(",")
        continue

      values = {header_val: value for (header_val, value) in zip(header, line[:-1].split(","))}
      if values["stop_id"] == stop_id:
        stopTimes.append(values)
    return header, stopTimes
  

# reads from calendar.txt service_id active today
def read_todays_calendar(filename: str, today: str) -> str:
  with open(filename, "r", encoding="utf8") as calendar_file:
    header = []

    for line in calendar_file:
      if len(header) == 0:
        # skip \n and weird sign on the beginning
        header = line[1:-1].split(",")
        continue

      values = {header_val: value for (header_val, value) in zip(header, line[:-1].split(","))}
      if values[today] == "1":
        return values["service_id"]
  
  # default value
  return "1"

def filter_stop_times(stop_times, now, current_calendar):
  stop_times = [x for x in stop_times if x["trip_id"].startswith(f"\"{current_calendar}")]
  stop_times = [x for x in stop_times if x["departure_time"] > now]
  stop_times.sort(key=lambda x: x["departure_time"])
  return stop_times
