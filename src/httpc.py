from client.client import run_client
from client.parser import getInput

arguments = getInput()
if arguments:
    run_client(arguments[0], arguments[1], arguments[2], arguments[3], arguments[4], arguments[5], arguments[6])
