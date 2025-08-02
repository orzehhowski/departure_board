import sqlite3

def get_connection(db_filename: str) -> sqlite3.Connection:
  return sqlite3.connect(db_filename)

def init_db(db_filename: str) -> None:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    cursor.execute("""
                    create table if not exists trips (
                    trip_id text primary key,
                    route_id text not null,
                    trip_headsign text not null
                    )
                   """)
    cursor.execute("""
                    create table if not exists stop_times (
                      id integer primary key autoincrement,
                      trip_id text not null,
                      stop_id text not null,
                      departure_time text not null,
                      stop_headsign text
                    )
                   """)
    cursor.execute("""
                    create table if not exists calendar (
                      service_id text primary key,
                      monday text not null,
                      tuesday text not null,
                      wednesday text not null,
                      thursday text not null,
                      friday text not null,
                      saturday text not null,
                      sunday text not null
                    )
                   """)
    conn.commit()

def create_trips(db_filename: str, trips: list[dict]) -> None:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    data = [(trip["trip_id"], trip["route_id"], trip["trip_headsign"]) for trip in trips]
    cursor.executemany("insert into trips (trip_id, route_id, trip_headsign) values (?, ?, ?)", 
                    data)
    conn.commit()

def create_stop_times(db_filename: str, stop_times: list[dict]) -> None:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    data = [(st["trip_id"], st["stop_id"], st["departure_time"], st["stop_headsign"]) for st in stop_times]
    cursor.executemany("insert into stop_times (trip_id, stop_id, departure_time, stop_headsign) values (?, ?, ?, ?)",
                  data)
    conn.commit()

def create_calendar(db_filename: str, calendar: list[dict]) -> None:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    data = [(service["service_id"], service["monday"], service["tuesday"], service["wednesday"], 
             service["thursday"], service["friday"], service["saturday"], service["sunday"]) for service in calendar]
    cursor.executemany("insert into calendar (service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday) values (?, ?, ?, ?, ?, ?, ?, ?)",
                  data)
    conn.commit()

def get_todays_stop_departures(db_filename: str, stop_id: str, current_service: str) -> list:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    cursor.execute("""select trips.route_id, stop_times.stop_headsign, stop_times.departure_time
                   from stop_times
                   inner join trips on trips.trip_id = stop_times.trip_id
                   where stop_times.stop_id = ? and stop_times.trip_id like ?
                   order by stop_times.departure_time
                   """, (stop_id, f"{current_service}%"))
    return cursor.fetchall()
  
def get_todays_service(db_filename: str, today: str) -> str:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    # today is selected from list in code so there's no sql injection risk
    query = f"select service_id from calendar where {today} = '1'"
    cursor.execute(query)
    return cursor.fetchone()[0]
  
def get_trips_sample(db_filename: str, limit=10) -> list:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    cursor.execute("select * from trips limit ?", (str(limit),))
    return cursor.fetchall()
  
def get_stop_times_sample(db_filename: str, limit=10) -> list:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    cursor.execute("select * from stop_times limit ?", (str(limit),))
    return cursor.fetchall()
  
def get_calendar(db_filename: str) -> list:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    cursor.execute("select * from calendar")
    return cursor.fetchall()
  
def prune_db(db_filename: str) -> None:
  with get_connection(db_filename) as conn:
    cursor = conn.cursor()
    cursor.execute("delete from trips")
    cursor.execute("delete from stop_times")
    cursor.execute("delete from calendar")
    conn.commit()