# departure_board

I wan't to create home live departure board for trams on my nearest station, on my ESP8266. Unfortunately I've got only 0,96" 128*64 Px LCD right now, so it may be little bit small, but it doesn't matter

## how to run
Linux:
```
cp .env.example .env
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python3 -m api.main
```

## purpose

I just hope I'll find it useful, and I wan't to move on with micropython

## data source

I'll be fetching and using data shared by ZTM Poznan: 

https://www.ztm.poznan.pl/otwarte-dane/dla-deweloperow/