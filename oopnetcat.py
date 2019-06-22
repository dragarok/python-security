import argparse
import threading
import socket
import subprocess
import sys


class Netcat:
    def __init__(self, ip=None, port=None,command=None, upload=None, shell=None):
        self.ip = ip
        self.port = port
        self.command = command
        self.upload = upload
        self.shell = shell
        self.client_socket = None
        self.addr = None

    def listen(self):
        if self.ip is None:
            self.ip = "0.0.0.0"
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.ip, self.port))
        server.listen(5)
        print('[+] Listening on %s:%d' % (self.ip,self.port))
        while True:
            self.client_socket, self.addr = server.accept()
            print("[+]Accepted connection from the client ")
            client_thread = threading.Thread(target=self.client_handler, args=(self.client_socket,))
            client_thread.start()

    def client_handler(self):
        if self.shell is True:
            while True:
                self.client_socket.send("<c0d3:#>")
                cmd_buffer = ""
                while "\n" not in cmd_buffer:
                    cmd_buffer += self.client_socket.recv(1024)
                    response = self.run_command(cmd_buffer)
                    self.client_socket.send(response)

        if self.command is not None:
            output = self.run_command(self.command)
            self.client_socket.send(output)
        if self.upload is not None:
            file_buffer = ""
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                else:
                    file_buffer += data
            try:
                file_descriptor = open(self.upload, "wb")
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                self.client_socket.send("Successfully saved file")
            except:
                self.client_socket.send("Failed to save file")

    def run_command(self, command):
        try:
            result = subprocess.check_output(command,stderr=subprocess.STDOUT, shell=True)
        except:
            result = "Failed to execute command \r\n"
        return result

    def client_sender(self,buffer):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.ip, self.port))
            if len(buffer):
                client.send(buffer)
            while True:
                recv_len = 1
                response = ""

                while recv_len:
                    data =  client.recv(4096)
                    recv_len = len(data)
                    response += data

                    if recv_len >4096:
                        break

                print(response)

                buffer = input("")
                buffer += "\n"

                client.send(buffer)
        except:
            print("[+] Exception! Exiting")
            client.close()

def main():
    parserObj = argparse.ArgumentParser(description="The best ntcat listener")
    parserObj.add_argument('--listen','-l',dest='listen',help='listen on host:port',action='store_true')
    parserObj.add_argument('--target','-t',dest='ip',help='ip to listen to')
    parserObj.add_argument('--port','-p',type=int,dest='port',help='port to listen to')
    parserObj.add_argument('--execute','-e',dest='exec',help='execute a file upon gaining access')
    parserObj.add_argument('--upload','-u',dest='toupload',help='upload a file upon getting connection')
    parserObj.add_argument('--shell','-s',dest='shell',help='invoke a shell on the client',action='store_true')
    args = parserObj.parse_args()

    mynetcat = Netcat(args.ip, args.port,args.exec,args.toupload,args.shell)
    if not len(sys.argv[1:]):
        print(parserObj.print_help())
    if args.listen is True:
        mynetcat.listen()
    if args.listen is False and len(args.ip) and args.port > 0:
        buffer = sys.stdin.read()
        mynetcat.client_sender(buffer)

main()
