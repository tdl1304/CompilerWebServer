from http.server import HTTPServer, BaseHTTPRequestHandler
import docker
import subprocess


class Compiler:
    def __init__(self):
        # route to currently working directory formatted after linux
        self.cd = "//c/Users/pRIVAT/PycharmProjects/CompilerWebServer"
        self.wd = "/usr/src/app"
        self.client = docker.from_env()
        self.file = "script.py"

    def run_docker_cli(self):
        cmd = ['docker', 'run',
               '-v', self.cd + ':' + self.wd,
               '-t',
               '-w', self.wd,
               '--rm', 'python:3.7', 'python', self.file]
        result = subprocess.run(cmd, stdout=subprocess.PIPE)
        return result.stdout

    # Not really needed
    def run_docker(self):
        container = self.client.containers.run(image="python:3.7",
                                               command="python " + self.file,
                                               auto_remove=True,
                                               volumes={self.cd: {'bind': '/home/usr/app', 'mode': 'ro'}},
                                               working_dir='/home/usr/app',
                                               tty=False,
                                               stderr=True,
                                               stdout=True
                                               )
        return container

    def create(self, code):
        with open(self.file, 'wb') as outfile:
            outfile.write(code)

    def compile(self, code):
        self.create(code=code)
        return self.run_docker_cli()


class Handler(BaseHTTPRequestHandler):
    compiler_ = Compiler()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open('public/index.html', 'rb') as index:
                self.wfile.write(index.read())
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            with open('public/style.css', 'rb') as style:
                self.wfile.write(style.read())
        elif self.path == '/favicon.ico':
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            with open('public/favicon.ico', 'rb') as icon:
                self.wfile.write(icon.read())

    # handles post requests to server
    def do_POST(self):
        if self.headers.get('Content-Length') is not None:
            content_len = int(self.headers.get('Content-Length'))
        else:
            content_len = -1
        if content_len > 0:
            body = self.rfile.read(content_len)
            output = self.compiler_.compile(code=body)
        else:
            output = b''

        # Response
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        if self.headers.get('Origin') is not None:
            self.send_header('Access-Control-Allow-Origin', self.headers.get('Origin'))
            self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        self.wfile.write(output)


def main():
    PORT = 8000
    server = HTTPServer(('', PORT), Handler)
    print('server running on port', PORT)
    server.serve_forever()


if __name__ == "__main__":
    main()
