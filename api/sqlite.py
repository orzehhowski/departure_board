import sqlite3
import os

def get_connection():
  return sqlite3.connect(os.environ["DB_FILENAME"])

def init_db():
  with get_connection() as conn:
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
    conn.commit()

def create_trips(trips: list[dict]):
  with get_connection() as conn:
    cursor = conn.cursor()
    data = [(trip["trip_id"], trip["route_id"], trip["trip_headsign"]) for trip in trips]
    cursor.executemany("INSERT INTO trips (trip_id, route_id, trip_headsign) VALUES (?, ?, ?)", 
                    data)
    conn.commit()

def create_stop_times(stop_times: list[dict]):
  with get_connection() as conn:
    cursor = conn.cursor()
    data = [(st["trip_id"], st["stop_id"], st["departure_time"], st["stop_headsign"]) for st in stop_times]
    cursor.executemany("INSERT INTO stop_times (trip_id, stop_id, departure_time, stop_headsign) VALUES (?, ?, ?, ?)",
                  data)
    conn.commit()

def get_todays_stop_departures(stop_id, current_calendar):
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""SELECT trips.route_id, stop_times.stop_headsign, stop_times.departure_time
                   from stop_times
                   inner join trips on trips.trip_id = stop_times.trip_id
                   where stop_times.stop_id = ? and stop_times.trip_id like ?
                   order by stop_times.departure_time
                   """, (stop_id, f"\"{current_calendar}%"))
    return cursor.fetchall()
  
def get_trips_sample(limit=10):
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("select * from trips limit ?", (str(limit),))
    return cursor.fetchall()
  
def get_stop_times_sample(limit=10):
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("select * from stop_times limit ?", (str(limit),))
    return cursor.fetchall()
  
def prune_db():
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("delete from trips")
    cursor.execute("delete from stop_times")
    conn.commit()