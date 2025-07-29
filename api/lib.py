WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
  
# reads data in csv format and saves it to list of dictionaries
def read_data(filename: str) -> list[dict]:
  with open(filename, "r", encoding="utf8") as file:
    header = []
    values_list = []

    for line in file:
      if len(header) == 0:
        # skip \n and weird sign on the beginning
        header = line[1:-1].split(",")
        continue

      values = {header_val: value for (header_val, value) in zip(header, line[:-1].split(","))}
      values_list.append(values)
    return values_list
    
# reads all records for given stop_id from stop_times.txt file 
def read_stop_times(filename: str, stop_id) -> tuple[list[str], list[dict]]:
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

# reads from calendar.txt service_id that is active today
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
  raise Exception("No today's service in calendar table")

# reads start and end date of current feed
def read_feed_dates(filename: str) -> tuple[str, str]:
  with open(filename, "r", encoding="utf8") as feed_file:
    for (index, line) in enumerate(feed_file):
      if index == 1:
        # you may ask why [1:-1] - we're trimming "" signs :)
        return line[:-1].split(",")[3][1:-1], line[:-1].split(",")[4][1:-1]
      
