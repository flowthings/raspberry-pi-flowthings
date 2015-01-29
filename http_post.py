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
        "elems": {
            "cpu_temp": {
                "type": "float",
                "value": cpu_temp()
            },
            "ram": {
                "type": "map",
                "value": {}
            },
            "disk": {
                "type": "map",
                "value": {}
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

# a simple loop to create a drop in the telemetry flow, once per minute
# for an hour
for i in range(60):
    new_drop = api.drop(flow_id).create(drop())
    sleep(60)
