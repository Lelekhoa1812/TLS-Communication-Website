import os
import ssl
import argparse
import socket
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Lock

# Usage to start server: python3 server.py fullchain_host1.crt host1.key rootCA.crt

# Flask App and Flask-SocketIO initialization
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
thread_lock = Lock()

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")
    emit('response', {'from_user': 'Server', 'message': f"Message received: {data['message']}"}, broadcast=True)

def run_server(certfile, keyfile, cafile, port):
    """
    Run the WebSocket server with TLS.
    """
    # Create SSL context for WebSocket secure connection
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=certfile, keyfile=keyfile)
    context.load_verify_locations(cafile=cafile)
    context.verify_mode = ssl.CERT_REQUIRED

    # Flask App Configuration with TLS
    socketio.run(app, ssl_context=('fullchain_host1.crt', 'host1.key'), host='0.0.0.0', port=5050)

# Parse CLI for the certificate files
def parse_cli():
    parser = argparse.ArgumentParser(description='WebSocket Secure Server', allow_abbrev=False)
    parser.add_argument('cert', help='Server certificate (full chain)')
    parser.add_argument('key', help='Server private key')
    parser.add_argument('cafile', help='Root CA file')
    parser.add_argument('-p', '--port', default=5050, help='Port to run the server on (default=5050)')
    return parser.parse_args()

# Main function
def main():
    args = parse_cli()
    run_server(args.cert, args.key, args.cafile, args.port)

if __name__ == "__main__":
    main()
