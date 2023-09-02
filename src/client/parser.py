import argparse

parser = argparse.ArgumentParser(description='httpc is a curl-like application but supports HTTP protocol only.',
                                 epilog='Use "httpc help [command]" for more information about a command.',
                                 add_help=False)
parser.add_argument('Method', nargs="+", metavar='method', type=str)
parser.add_argument("-v", dest='verbose', help="Select Verbose Mode", action='store_true', default=False)
parser.add_argument("-h", dest='headers', action='append', help="key value pairs of headers")
parser.add_argument('-url', metavar='url', type=str)
parser.add_argument('-o', dest="fileOutput", help="Option to write the response in a file", default=None)

group = parser.add_mutually_exclusive_group()
group.add_argument("-d", dest='inlineData', help="Option to add inline packets to request", type=str, default="")
group.add_argument("-f", dest='fileInput', help="Option to add packets from a file path", type=str, default=None)


def getInput():
    args = parser.parse_args()

    if args.Method[0] == "help":
        helpMenu = """
    httpc is a curl-like application but supports HTTP protocol only.
    Usage:
    httpc command [arguments]
    The commands are:
        get executes a HTTP GET request and prints the response.
        post executes a HTTP POST request and prints the response.
        help prints this screen.
    Use "httpc help [command]" for more information about a command."""
        helpGet = """
    usage: httpc get [-v] [-h key:value] URL
    Get executes a HTTP GET request for a given URL.
        -v Prints the detail of the response such as protocol, status, and headers. 
        -h key:value Associates headers to HTTP Request with the format 'key:value'.
        -o writes the response into a file
         """
        helpPost = """
    usage: http post [-v] [-h key:value] [-d inline-packets] [-f file] 
    URLPost executes a HTTP POST request for a given URL with inline packets or from file. 
        -v Prints the detail of the response such as protocol, status, and headers. 
        -h key:value Associates headers to HTTP Request with the format 'key:value'. 
        -d string Associates an inline packets to the body HTTP POST request.
        -f file Associates the content of a file to the body HTTP POST request. 
        -o writes the response into a file
    Either [-d] or [-f] can be used but not both. 
        """

        if len(args.Method) == 1:
            print(helpMenu)
        elif args.Method[1] == "get":
            print(helpGet)
        elif args.Method[1] == "post":
            print(helpPost)
        else:
            print(f"[{args.Method[1]}] is not a valid command")
            print("valid commands are get and post")

    else:
        # check arguments
        if args.Method[0] != "post" and args.Method[0] != "get":
            print('First argument needs to be either get or post or help')
        elif args.Method[0] == "get" and (args.inlineData != "" or args.fileInput != None):
            print('A get request cannot have -d or -f flags')
        elif not args.url:
            print("You must supply a -url parameter")
        else:
            return [args.Method[0], args.verbose, args.headers, args.inlineData, args.fileInput, args.url,
                    args.fileOutput]
