import json
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib
import mimetypes
import datetime
import socket
from threading import Thread
BASE_DIR=pathlib.Path()

def send_socket(data):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(data, ('127.0.0.1', 5000))
    client_socket.close()

class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body=self.rfile.read(int(self.headers['Content-Length']))
        send_socket(body)
        self.send_response(302)
        self.send_header('Location','/')
        self.end_headers()
    def do_GET(self):
        route=urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/message.html':
                self.send_html('message.html')
            case _:
                file= BASE_DIR / route.path[1:]
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html',404)

    def send_html(self,filename,status=200):
        self.send_response(status)
        self.send_header('Content-type','text/html')
        self.end_headers()
        with open(filename,'rb') as f:
            self.wfile.write(f.read())
    def send_static(self,filename):
        self.send_response(200)
        mime_type,*rest = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-type',mime_type)
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())
def save_data(data):
    data = urllib.parse.unquote_plus(data.decode())
    payload= {key:value for key,value in [el.split('=') for el in data.encode.split('&')]}
    s={str(datetime.datetime.now()):payload}
    print(s)
    with open(BASE_DIR.joinpath('storage/data.json'),'w',encoding='utf-8') as f:
        json.dump(s,f,ensure_ascii=False)


def run_socket():
    host='127.0.0.1'
    port=5000
    server_socket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_socket.bind((host,port))
    while True:
        data=server_socket.recv(1024)
        save_data(data)


def run(server=HTTPServer,handler=HttpHandler):
    adress=('',3000)
    http_server=server(adress,handler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        http_server.server_close()
if __name__=='__main__':
    server1=Thread(target=run())
    server1.start()
    server2=Thread(target=run_socket())
    server2.start()