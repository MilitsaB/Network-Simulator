import argparse

parser = argparse.ArgumentParser(add_help=False)

parser.add_argument("-v", dest='verbose', action='store_true', default=False)
parser.add_argument('-p', dest='port')
parser.add_argument('-d', dest="directory")
parser.add_argument('-h', dest="help", action='store_true', default=False)


class ServerParameters():
    def __init__(self, verbose, port, directory):
        self.verbose = verbose
        self.port = int(port)
        self.directory = directory


def get_input():
    args = parser.parse_args()

    if args.help:
        help_menu = """******WELCOME******
httpfs is a simple file server.
usage: httpfs [-v] [-p PORT] [-d PATH-TO-DIR]
    -v Prints debugging messages.
    -p Specifies the port number that the server will listen and serve at. Default is 8080.
    -d Specifies the directory that the server will use to read/write requested files. Default is the current directory when launching the application."""
        print(help_menu)

    else:
        # check arguments

        server_params = ServerParameters(args.verbose, args.port, args.directory)

        return server_params;
