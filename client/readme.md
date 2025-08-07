## setup

This is a setup for (as directory name indicates) ESP8266 microcontroller and SSD1306 screen.

## how to run it

When you have ESP connected to computer and micropython firmware flashed, connect your screen to the board and set variables in main.py file to chosen pins numbers.

Then you can use these commands to run client on the board (at least on linux):

```
cd ./client/esp8266_ssd1306
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
cp ./my_secrets_example.py ./my_secrets.py
# fill required fields in my_secrets.py with your WLAN info
rshell --port [your_device_port] cp ./main.py /pyboard
rshell --port [your_device_port] cp ./my_secrets.py /pyboard
```

Then restart device, and app should run when device boots.

## problem with HTTPS

In ESP8266 Documentation I found that:

>ESP8266 uses axTLS library, which is one of the smallest TLS libraries with compatible licensing. However, it also has some known issues/limitations:
>
> 1. No support for Diffie-Hellman (DH) key exchange and Elliptic-curve cryptography (ECC). This means it can’t work with sites which require the use of these features (it works ok with the typical sites that use RSA certificates).

(https://docs.micropython.org/en/latest/esp8266/general.html#ssl-tls-limitations)

My domain uses IP tunneling in cloudflare cloud. Unfortunately, cloudflare signs my domain (subseqent certificates doesn't matter, as ESP doesn't check the chain of trust) with ECDSA, which uses ECC:

```
0 s:CN = orzehhowski.pl
   i:C = US, O = Google Trust Services, CN = WE1
   a:PKEY: id-ecPublicKey, 256 (bit); sigalg: ecdsa-with-SHA256
```

And it is not possible to change the algorithm for plans cheaper than business. I also cannot bypass cloudflare tunnel, because my VPS has only public IPv6, and my router doesn't support IPv6

So I'm left with 2 options:

1. change TLS library on ESP - it would be little overcomplicating
2. just leave encryption and connect using HTTP

And at this point, I'll choose the latter and set HTTPS implementation as todo.