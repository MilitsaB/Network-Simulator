import socket
import threading
from time import gmtime, strftime
import os
from os import walk

from shared.PacketHelper import PacketHelper
from shared.PacketTypes import PacketTypes
from shared.ReceiveWindow import ReceiveWindow
from shared.UDPHelper import UDPHelper
from shared.packet import Packet

current_directory = ""
debugging_messages = ""
packet_types = PacketTypes()
peer_list = {}


def run_server(verbose, host, port, directory):
    global debugging_messages
    global current_directory

    current_directory = directory
    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    conn.settimeout(10)
    try:
        conn.bind(('', port))
        print('httpfs server is running on port ', port)
        while True:
            try:
                data, sender = conn.recvfrom(1024)
                threading.Thread(target=handle_client, args=(conn, sender, verbose, data)).start()
            except socket.timeout:
                continue
    finally:
        conn.close()


def handle_client(conn, sender, verbose, data):
    global peer_list
    global debugging_messages
    router_addr = "localhost"
    router_port = 3000
    timeout = 2

    debugging_messages = "New client from" + str(sender) + " " + str(conn) + "\n"
    # extract packet from packets
    p = Packet.from_bytes(data)
    peer = str(p.peer_ip_addr) + ":" + str(p.peer_port)

    if ((p.packet_type == packet_types.ACK and p.payload.decode() == "handshake") or p.packet_type == packet_types.SYN):
        # make a udpHelper for this peer if we don't have one already
        if peer not in peer_list:
            print("Creating new UDP helper for client")
            udp_helper = UDPHelper(timeout, conn, p.peer_ip_addr, p.peer_port, router_addr, router_port)
            peer_list[peer] = udp_helper
        else:
            print("UDP helper already exists for client")
            udp_helper = peer_list[peer]
        udp_helper.receive_handshake(p, sender)

    # now that handshake is is_done, we can receive and send packets
    elif p.packet_type == packet_types.DATA or p.packet_type == packet_types.FIN:
        udp_helper = peer_list[peer]
        #this will send all packets packets to udp_helper
        udp_helper.receive_data(p)
        if udp_helper.receive_window.payloadReady and peer in peer_list:
            print("Processing Payload")
            packets = udp_helper.receive_window.packets
            payload = PacketHelper.from_packets(packets)
            print("Clearing Window" )
            udp_helper.receive_window.clear()
            print("Payload: " + payload)
            #now we have our packets
            #we can send a response
            request_object = convert_to_request_object(payload)
            print(request_object)
            if request_object['method'] == "GET":
                debugging_messages += "GET Request\n"
                to_send = get_file_or_directory(request_object['path'])

            if request_object['method'] == "POST":
                debugging_messages += "POST Request\n"
                to_send = post_to_file(request_object['path'], request_object['body'])
            print("Sending response")
            packets_to_send = PacketHelper.to_packets(packet_types.DATA, 10, udp_helper.peer_ip_addr, udp_helper.peer_port, to_send)
            sent_success = udp_helper.send(to_send)
            if sent_success:
                print('Successfully sent request!')
            else:
                print('Communication lost.')




        #

    # print("Router: ", sender)
    # print("Packet: ", p)
    # print("Payload: ", p.payload.decode("utf-8"))

    # REMOVE FOR NOW
    # request = conn.recv(1024).decode("utf-8")
    # request_object = convert_to_request_object(request)
    #
    # if request_object['method'] == "GET":
    #     debugging_messages += "GET Request\n"
    #     to_send = get_file_or_directory(request_object['path'])
    #
    # if request_object['method'] == "POST":
    #     debugging_messages += "POST Request\n"
    #     to_send = post_to_file(request_object['path'], request_object['body'])

    # try:
    #     # lets just try to send a packet instead
    #     conn.sendto(p.to_bytes(), sender)
    #     print('hi')
    # except Exception as e:
    #     print("Error: ", e)

        # conn.sendall(to_send.encode())
        # display_response(to_send, verbose)


def convert_to_request_object(request):
    request_info = request.split("\r\n\r\n")[0].split()
    request_object = {'method': request_info[0], 'path': request_info[1],
                      'header': request_info[3:], 'body': None}

    if len(request.split("\r\n\r\n")) > 1:
        request_object['body'] = request.split("\r\n\r\n")[1]

    return request_object


def get_response(status, body, content_type):
    response = "HTTP/1.1 " + str(status) + " " + get_status_message(status) + "\r\n"
    response += "Connection: close\r\n"
    response += "Server: httpfs/1.0.0\r\n"
    response += "Date: " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " GMT\r\n"
    response += "Content-Type: " + content_type + "\r\n"
    response += "Content-Length " + str(len(body)) + "\r\n"
    response += "\r\n\r\n" + body
    return response


def get_status_message(status):
    return {
        200: 'OK',
        201: 'CREATED',
        400: 'BAD REQUEST',
        403: 'FORBIDDEN',
        404: 'NOT FOUND',
        500: 'INTERNAL SERVER ERROR'
    }.get(status, 'UNKNOWN')


def display_response(response, verbose):
    if verbose:
        print("Debug:")
        print(debugging_messages)
    print(response + "\n")


# File Management
def get_file_or_directory(path):
    if os.path.isdir("." + current_directory + path):
        return get_directory(path)
    else:
        return get_file(path)


def get_directory(path):
    global debugging_messages
    f = []
    print("." + current_directory + path)
    for (dirpath, dirnames, filenames) in walk("." + current_directory + path):
        f.extend(filenames)
        f.extend(dirnames)
        break

    debugging_messages += "Sending directory info \n"
    return get_response(200, " ".join(f), "text/plain")


def get_file(path):
    global debugging_messages
    try:
        if "../" in path:
            raise ValueError('Forbidden route')

        f = open("." + current_directory + path, 'r')
        fileData = f.read()
        f.close()
    except ValueError:
        debugging_messages += "403: route is forbidden \n"
        return get_response(403, "Forbidden route", '')

    except FileNotFoundError:
        debugging_messages += "404: file or file path wrong \n"
        return get_response(404, "Wrong file or file path", '')

    debugging_messages += "Sending file content \n"
    return get_response(200, fileData, "text/plain")


def post_to_file(path, body):
    global debugging_messages
    status = ''

    try:
        if "../" in path:
            raise ValueError('Forbidden route')

        print("." + current_directory + path)
        if os.path.isfile("." + current_directory + path):
            status = 200
        else:
            status = 201

        f = open("." + current_directory + path, 'w')
        f.write(body)
        f.close()

    except ValueError:
        debugging_messages += "403: route is forbidden \n"
        return get_response(403, "Forbidden route", '')
    except IOError:
        debugging_messages += "404: Wrong file or file path \n"
        return get_response(404, "Wrong file or file path", '')
    except:
        debugging_messages += "500: error in server \n"
        return get_response(500, "Server error", '')

    debugging_messages += "Posting file \n"
    return get_response(status, body, "text/plain")
