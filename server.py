from socket import socket, AF_INET, SOCK_STREAM
from pathlib import Path
import sys

# argumentos cli
args = sys.argv
if len(args) < 3:
    print('Usage: python3 server.py <port> <folder>')
    sys.exit(1)

HOST = 'localhost'
PORT = int(args[1])
FOLDER = args[2]

base_dir = Path(__file__).parent / FOLDER

s = socket(AF_INET, SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

print('Server listening on port', PORT)

while True:
    conn, addr = s.accept()
    print('Connected to', addr)
    req = conn.recv(1024)
    path = req.split()[1].decode()
    file = base_dir / path[1:]

    data = ''
    status_code = 200
    status_message = 'OK'
    content_type = 'text/html'
    content_length = 0
    moved = ''

    # bad request
    if path[0] != '/':
        status_code = 400
        status_message = 'Bad Request'
        data = 'ERROR 400'
    # I'm a teapot
    elif req.split()[0].decode() == 'BREW':
        status_code = 418
        status_message = "I'm a teapot"
        content_type = 'text/plain'
        data = '<h1>ERROR 418</h1>'
    # not allowed
    elif req.split()[0].decode() != 'GET':
        status_code = 405
        status_message = 'Method Not Allowed'
        data = 'ERROR 405'
    # http version not supported
    elif req.split()[2].decode() != 'HTTP/1.1':
        status_code = 505
        status_message = 'HTTP Version Not Supported'
        data = 'ERROR 505'
    else:
        # archivo es un directorio
        if file.is_dir():
            status_code = 301
            status_message = 'Moved Permanently'
            moved = f'\nLocation: http://localhost:{PORT}/{file}/index.html'
            file = file / 'index.html'
        # archivo existe
        if file.exists():
            content_length = file.stat().st_size
            data = file.read_text()
            extension = file.suffix
            if extension == '.html' or extension == '.htm':
                content_type = 'text/html'
            elif extension == '.css':
                content_type = 'text/css'
            elif extension == '.js':
                content_type = 'text/javascript'
            elif extension == '.jpg' or extension == '.jpeg':
                content_type = 'image/jpeg'
            elif extension == '.png':
                content_type = 'image/png'
        # archivo no existe
        else:
            status_code = 404
            status_message = 'Not Found'
            data = 'ERROR 404'
    
    response = f'HTTP/1.1 {status_code} {status_message}\nContent-Type: {content_type}\nContent-Length: {content_length}{moved if moved else ""}\n\n{data}'
    # print(response) # DEBUG
    conn.sendall(response.encode())
    conn.close()
