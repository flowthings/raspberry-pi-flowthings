# raspberry-pi-flowthings
Getting started with Flowthings &amp; Raspberry Pi - Python Client

## Introduction
---

In this tutorial, we'll use the flowthings.io python client library with the Raspberry Pi. We'll create a simple python program to send telemetry from the Raspberry Pi to flowthings.io. We’ll then demonstrate how to use WebSockets to receive realtime updates of that data on another computer.

## Setup Dependencies
---

1. Setup your Raspberry Pi
2. Get a flowthings.io account [here](https://auth.flowthings.io/register) if you don't already have one
3. Python 2.x on the computer that will be receiving updates.
4. Install the flowthings client library on both the Raspberry Pi and your local computer with pip:
```sh
pip install flowthings
```
5. install `psutil` on the Raspberry Pi
```sh
pip install psutil
```

## Setup flowthings.io
---

### Create a Flow for the Raspberry Pi's telemetry

You can login to the flowthings.io Developer Site at [https://dev.flowthings.io](https://dev.flowthings.io) and create a Flow for the Raspberry Pi's telemetry from the "Flow Browser" tab. Make note of the Flow's `path` and `id`, you'll need them later.

![Create a Flow on flowthings.io](https://res.cloudinary.com/dushgp4zq/image/upload/v1422546141/tutorial/rasberry-pi-first/create_a_flow.png)

### Prepare for Authentication

In this example we'll create a new Token to allow access only to the Flow you've just created. From within the flowthings.io Developer Site, navigate to the "Account" tab. Select "Tokens", then "New". At the dialog enter a description, an expiration, and the path you created in the previous step. Make sure that both Drop Read and Drop Write are selected. This will create a token that can be assigned to any device or program that will **only** be permitted to read and write from our tutorial Flow. Take note of the Token's value, as we'll need it below.

![Token Create Dialog](https://res.cloudinary.com/dushgp4zq/image/upload/v1422546792/tutorial/rasberry-pi-first/create_a_token.png)

For more information on tokens and authentication [check out the authentication docs](https://flowthings.io/docs/flowthings-http-api-authentication)

### Send Telemetry from the Raspberry Pi

Now you can write a short python script that will periodically write chip temperature, ram and disk usage to a Flow in the form of a Drop. Run the example below on the Raspberry Pi:

```python
#!env python
from flowthings import API, Token, mem
from subprocess import PIPE, Popen
from time import sleep
import psutil

ACCOUNT_NAME = "your account name here"
ACCOUNT_TOKEN = "your token here"
FLOW_PATH = "path of the flow you created above"

# get the cpu temperature
def cpu_temp():
  process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
  output, error = process.communicate()
  return float(output[output.index('=') + 1:output.rindex("'")])

# define a drop
def drop():
  drop = {
    "elems" : {
      "cpu_temp" : {
        "type" : "float",
        "value" : cpu_temp()
      },
      "ram" : {
        "type" : "map",
        "value" : {}
      },
      "disk" : {
        "type" : "map",
        "value" : {}
      }
    }
  }

  ram = psutil.phymem_usage()
  drop['elems']['ram']['value']['total'] = ram.total / 2 ** 20
  drop['elems']['ram']['value']['used'] = ram.used / 2 ** 20
  drop['elems']['ram']['value']['free'] = ram.free / 2 ** 20

  disk = psutil.disk_usage('/')
  drop['elems']['disk']['value']['total'] = disk.total / 2 ** 20
  drop['elems']['disk']['value']['used'] = disk.used / 2 ** 20
  drop['elems']['disk']['value']['free'] = disk.free / 2 ** 20

  return drop

# set up your credentials, with the account name and a token
creds = Token(ACCOUNT_NAME, ACCOUNT_TOKEN)

# have the api use your credentials
api = API(creds)

# here's an example of using the find api, if we already had the
# id of the Flow that we are interested in we could exclude this step
flows = api.flow.find(mem.path == FLOW_PATH)
flow_id = flows[0]['id']

# a simple loop to create a drop in the telemetry flow, once per minute for an hour
for i in range(60):
  new_drop = api.drop(flow_id).create(drop())
  sleep(60)
```

### Monitor drops in the flow via WebSockets

Run the below on any other computer connected on the internet.

```python
#!env python
from flowthings import API, Token, mem

ACCOUNT_NAME = "your account name here"
ACCOUNT_TOKEN = "your token here"
FLOW_ID = "path of the flow you created above"

# set up your credentials, with the account name and a token
creds = Token(ACCOUNT_NAME, ACCOUNT_TOKEN)

# have the api use your credentials
api = API(creds)

# define actions for events
def on_open(ws):
  ws.subscribe(FLOW_ID)

def on_message(ws, resource, data):
  print "Message received:", resource, data

def on_close(ws):
  print "Connection Closed"

def on_error(ws, e):
  print "Error:" , e

ws = api.websocket.connect(on_open=on_open,
                           on_message=on_message,
                           on_close=on_close,
                           on_error=on_error)
ws.run()
```
