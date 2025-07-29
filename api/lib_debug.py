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