# departure_board

I wan't to create home live departure board for trams on my nearest station, on my ESP8266. Unfortunately I've got only 0,96" 128*64 Px LCD right now, so it may be little bit small, but it doesn't matter.

This file describes API server, for client details visit `readme` files in `/client` directory.

## how to run

```
docker compose up
```

## purpose

I just hope I'll find it useful, and I wan't to move on with micropython

## deploy

You can find the API on https://bimba.orzehhowski.pl

It is hosted on my https://mikr.us VPS server - I strongly recommend these : )

## what does it do

`api.server` module starts `aiohttp` HTTP server and registers `aiocron` task. This task fetches data from ZTM API and saves it to sqlite database daily at 23:50.

Server has only one endpoint on `/`, which accepts 2 query params: `n` - numeric (default 10, max 100), and `stop` - stop_id (default 60 - my stop).
This endpoint serves `n` next departures for given stop in JSON format:
```
{
  "departures": [
    [
      "bus line number",
      "bus line destination",
      "departure time in HH:MM:SS"
    ],
    {...}
  ]
}
``` 

It returns data only from today and tommorow, so if departures from this time range doesn't reach the `n` limit, response will be shorter.

## data source

I'll be fetching and using data shared by ZTM Poznan: 

https://www.ztm.poznan.pl/otwarte-dane/dla-deweloperow/

## note

for more details visit `notes/readme.md`

created with human intelligence only (why the hell would you do that? - just to keep my brain cells going :)