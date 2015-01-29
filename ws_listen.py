#!env python
from flowthings import API, Token

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
    print "Error:", e

ws = api.websocket.connect(on_open=on_open,
                           on_message=on_message,
                           on_close=on_close,
                           on_error=on_error)
ws.run()
