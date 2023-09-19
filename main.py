from flask import Flask, jsonify
from flask_cors import CORS
import socket
import webbrowser
import http.server
import socketserver
import threading

host = '0.0.0.0'
app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def home():
    return jsonify({
        "ok": True,
        "message": "Hello world"
    })

def get_saved_port(port_name): 
    with open(port_name, 'r') as doc:
        active_port = doc.read()
        doc.close()
        return active_port

def is_port_open(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((host, int(port)))
        return True
    except (OSError, socket.error):
        return False

def get_port(port_name=''):
    saved_port = get_saved_port(port_name)
    if saved_port != '' and saved_port is not None and is_port_open(saved_port):
        print(f"Re-using port {saved_port} for {port_name}" )
        return int(saved_port)
    print(f"Creating new port")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, 0))
    _, port = sock.getsockname()
    with open(port_name, 'wb') as doc:
        doc.write(str(port).encode("utf-8"))
        doc.close()
    return port

def run_server():
    port = get_port('ui_port')
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Html webserver will run on {port}")
        webbrowser.open(f"http://{host}:{port}/index.html")
        httpd.serve_forever()

def run_api():
    port = get_port('api_port')
    print(f"API will run on port {port}")
    app.run(host=host, port=port)

if __name__ == '__main__':
    api_server = threading.Thread(target=run_api)
    file_server = threading.Thread(target=run_server)

    file_server.start()
    api_server.start()

    api_server.join()
    file_server.join()