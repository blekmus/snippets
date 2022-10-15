# needs to be run as root for some reason
# and now it doesn't need root for some reason... how?

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import argparse


def main(username, password, location, port):
    authorizer = DummyAuthorizer()
    authorizer.add_user(username, password, location, perm='elr')
    authorizer.add_anonymous(location)
    handler = FTPHandler
    handler.authorizer = authorizer
    address = ('0.0.0.0', port)
    server = FTPServer(address, handler)
    server.max_cons = 256
    server.max_cons_per_ip = 5
    server.serve_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='FTP Server')

    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-P', '--password', required=True)
    parser.add_argument('-p', '--port', required=True)
    parser.add_argument('-l', '--location', required=True)
    args = parser.parse_args()

    main(args.username, args.password, args.location, args.port)
