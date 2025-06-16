import sqlite3

def get_connection():
  return sqlite3.connect("schedules.db")

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

def create_trip(trip_id, route_id, trip_headsign):
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trips (trip_id, route_id, trip_headsign) VALUES (?, ?, ?)", 
                    (trip_id, route_id, trip_headsign))
    conn.commit()

def create_stop_time(trip_id, stop_id, departure_time, stop_headsign):
   with get_connection() as conn:
     cursor = conn.cursor()
     cursor.execute("INSERT INTO trips (trip_id, stop_id, departure_time, stop_headsign) VALUES (?, ?, ?, ?)",
                    (trip_id, stop_id, departure_time, stop_headsign))
     conn.commit()

def get_todays_stop_departures(stop_id, current_calendar):
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("""SELECT trips.route_id, trips.trip_headsign, stop_times.stop_headsign, stop_times.departure_time
                   from stop_times
                   inner join trips on trips.trip_id = stop_times.trip_id
                   where stop_times.stop_id = ? and stop_times.trip_id like ?
                   """, (stop_id, f"{current_calendar}%"))
    return cursor.fetchall()
  
def prune_db():
  with get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("delete from calendar")
    cursor.execute("delete from trips")
    cursor.execute("delete from stop_times")
    conn.commit()