from server.parser import get_input, ServerParameters
from server.server import run_server

server_params = get_input()

run_server(server_params.verbose, '', server_params.port, server_params.directory)
