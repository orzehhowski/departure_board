import csv

WEEKDAYS = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
  
# reads data in csv format and saves it to list of dictionaries
def read_data(filename: str) -> list[dict]:
  # utf-8-sig is for deleting BOM char (\ufeff) at the beggining of file
  with open(filename, "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=",", quotechar="\"")
    return list(reader)

# same as above but in chunks 
# for situations when file is too big to fit into host's working memory at once
def read_data_in_chunks(filename: str, chunk_size: int):
  with open(filename, "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file, delimiter=",", quotechar="\"")
    chunk = []
    for row in reader:
      chunk.append(row)
      if len(chunk) >= chunk_size:
        yield chunk
        chunk = []
    if chunk:
      yield chunk
    
# reads from calendar.txt service_id that is active today
def read_todays_calendar(filename: str, today: str) -> str:
  with open(filename, "r", encoding="utf-8-sig") as calendar_file:
    reader = csv.DictReader(calendar_file, delimiter=",", quotechar="\"")
    for row in reader:
      if row[today] == "1":
        return row["service_id"]
  raise Exception("No today's service in calendar table")

# reads start and end date of current feed
def read_feed_dates(filename: str) -> tuple[str, str]:
  with open(filename, "r", encoding="utf-8-sig") as feed_file:
    for (index, line) in enumerate(feed_file):
      if index == 1:
        # you may ask why [1:-1] - we're trimming "" signs :)
        return line[:-1].split(",")[3][1:-1], line[:-1].split(",")[4][1:-1]
      
