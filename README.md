# Network-Simulator

UDP-ifying httpc and httpfs library. 

This project reimplements an HTTP client and server to use UDP instead of TCP by implementing selective repeat ARQ for reliability over an unreliable network in a simulated environment. The goal is to ensure reliable data transfer when using the connectionless UDP protocol.

## Setting Up


### Router Terminal:

Go to your OS relevant router folder `cd /path/to/router/[mac|linux]/router`

Run: `./router_x64 --port=3000 --drop-rate=0 --max-delay=10ms --seed=1`

### Server Terminal:

`cd /path/to/Network-Simulator/src/`

Run: `python httpfs.py -v -d /server/data -p 8007`

### Client Terminal:

`cd /path/to/COMP445_A3/src/`

Run any of the following to test out basic functionality: 

### HELP
- `python httpc.py help` 

### GET  
- `python httpc.py get -v -url 'http://localhost:8007/test.txt'`
- `python httpc.py post -h Content-Type:application/json -f test.txt -url http://httpbin.org/post`
- `python httpc.py post -h Content-Type:application/json -f sample.txt -url http://localhost:8007/post`
- `python httpc.py get -url  'http://localhost:8007/sample-folder/test.txt'`

### POST 
- `python httpc.py post -h Content-Type:application/json -d '{"Assignment": 77}' -url http://localhost:8088/sample-folder/test.py`
- `python httpc.py post -h Content-Type:application/json -d '{"Assignment": 3}' -url http://localhost:80/test.py`
- `python httpc.py post -h Content-Type:application/json -d '{"Assignment": 2}' -url http://localhost:80/test.txt`
