import socket
from urllib.parse import urlparse
import ipaddress
import re

from shared.PacketHelper import PacketHelper
from shared.PacketTypes import PacketTypes
from shared.UDPHelper import UDPHelper
from shared.packet import Packet
packet_types = PacketTypes()

def run_client(method, verbose, headers, inlineData, fileInput, url, fileOutput):
    default_port = 80
    router_addr = "localhost"
    router_port = 3000
    server_addr = "localhost"
    server_port = 8007
    timeout = 5
    peer_ip = ipaddress.ip_address(socket.gethostbyname(server_addr))

    conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:

        url_parsed = urlparse(url)
        scheme = url_parsed.scheme
        host = url_parsed.hostname
        path = url_parsed.path
        query = "" if url_parsed.query == "" else "?" + url_parsed.query
        if method == 'get':
            request = get_request(host, path, query, headers)

        if method == 'post':
            request = post_request(host, path, query, headers, inlineData, fileInput)

        #try to initiate handshake
        udp_helper = UDPHelper(timeout, conn, peer_ip, server_port, router_addr, router_port)
        udp_helper.initiate_handshake(peer_ip, server_port)
        print("Handshake successful")
        print('Splitting request into packets')
        packets = PacketHelper.to_packets(packet_types.DATA, 10, peer_ip, server_port, request)
        udp_helper.send_data(packets)

        p = udp_helper.receive_response()

        print("".join(p))

    except socket.timeout:
        print('No response after {}s'.format(timeout))
        # CODE TO ADD AFTER
        # conn.connect((host, default_port))
        # # 1. Open connection with ACK NACK 3 way handshake stuff (Later)
        #
        # # connection established
        #
        # # 2. here we need to break request into packets and send each packet individually
        # conn.sendall(request.encode())
        # # here we need to wait for responses
        # response = conn.recv(4096).decode("utf-8")
        #
        # display_response(response, verbose, fileOutput)
        #
        # redirect_url = redirect(response)
        # if redirect_url:
        #     parsed_redirect = urlparse(redirect_url)
        #     if not bool(parsed_redirect.hostname):
        #         redirect_url = scheme + "://" + host + redirect_url
        #     print("Redirecting to " + redirect_url)
        #     run_client(method, verbose, headers, inlineData, fileInput, redirect_url, fileOutput)

    finally:
        conn.close()


def get_request(host, path, query, headers):
    request = "GET " + path + query + " HTTP/1.1\r\nHost: " + host + "\r\nUser-Agent: Concordia-HTTP/1.1"
    if headers:
        for header in headers:
            request += "\r\n" + header

    request += "\r\n\r\n"
    return request


def post_request(host, path, query, headers, inlineData, fileInput):
    request = "POST " + path + query + " HTTP/1.1\r\nHost: " + host + "\r\nUser-Agent: Concordia-HTTP/1.1"
    if headers:
        for header in headers:
            request += "\r\n" + header

    if inlineData:
        request += "\r\nContent-Length:" + str(len(inlineData)) + "\r\n\r\n" + inlineData
    elif fileInput:
        f = open(fileInput, 'r')
        fileData = f.read()
        f.close()
        request += "\r\nContent-Length:" + str(len(fileData)) + "\r\n\r\n" + fileData

    request += "\r\n\r\n"
    return request


def display_response(response, verbose, fileOutput):
    if verbose:
        output = response
    else:
        output = response.split("\n\r")[1]

    if fileOutput is not None:
        # write output to file
        write_file(output, fileOutput)
    else:
        # print output to terminal
        print(output)


def write_file(output, fileOutput):
    f = open(fileOutput, "w")
    f.write(output)
    f.close()


def redirect(response):
    if response.split()[1] == '302':
        redirectLocation = re.findall(r"(?<=Location\: )(.*)", response)[0].rstrip()

        return redirectLocation
    else:
        return None
