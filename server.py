#!env python
import json
import random

import socketserver

# Simple python TCP server wiht JSON messaging, using the socketserver api
# https://docs.python.org/3.4/library/socketserver.html


def database(query):
    entity_type = query.get('type', None)

    response = {'success': False}

    if entity_type == 'user':
        users = []
        for i in range(query.get('count', 10)):
            users.append({'user': 'Bob_%d' % i, 'balance': random.randint(10, 100)})
        response['users'] = users
        response['success'] = True

    elif entity_type:
        response['error'] = 'Type "%s" is not supported' % entity_type

    else:
        response['error'] = "Please specify \"type\" in the query"

    return response


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client. The socket is passed to this method in self.request
    """

    def handle(self):
        client = self.client_address[0]
        print("Connected client from %s" % client)
        while True:
            f = self.request.makefile()
            query_string = f.readline()
            if query_string == '':
                print("Client [%s] closed the connection" % client)
                return

            print("[%s] query: %s" % (client, query_string), end='')
            try:
                # Trying to parse the query
                query = json.loads(query_string)
            except ValueError:
                self.request.sendall(b'Query should be a one line JSON with a key "type"\n')
                continue

            response_object = database(query)
            self.request.sendall(json.dumps(response_object).encode())
            self.request.send(b"\n")


class ReuseAddressTcpServer(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = ReuseAddressTcpServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you interrupt the program with Ctrl-C
    server.serve_forever()


