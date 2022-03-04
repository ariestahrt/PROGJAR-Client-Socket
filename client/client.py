import socket
import sys
from time import sleep
import os
from os import path

def get_string_between(str, sep1, sep2):
    return str.split(sep1)[1].split(sep2)[0]

BUFFER_SIZE = 1024*4
HOST = "127.0.0.1"
PORT = 5000

server_address = (HOST, PORT)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"[+] Connecting to {HOST}:{PORT}")
client_socket.connect(server_address)
print("[+] Connected.")
print("[SEND] >> ")

try:
    while True:
        message = sys.stdin.readline()
        client_socket.send(bytes(message, 'utf-8'))
        received_data = client_socket.recv(BUFFER_SIZE).decode('utf-8')

        # Special handling if we send unduh message
        if message.split(" ")[0] == "unduh":
            # check the confirmation is the file exist
            if received_data == "CONFIRMATION::FILE_EXIST\n":
                #read the header message
                received_header = client_socket.recv(BUFFER_SIZE).decode('utf-8')
                recv_filename = get_string_between(received_header, "file-name: ", "\n")
                recv_filesize = int(get_string_between(received_header, "file-size: ", "\n"))
                
                print(f"We got header ::\nFile Name : {recv_filename}\nFile Size: {recv_filesize}")
                # delete the file first,
                try:
                    os.remove(recv_filename)
                except:
                    None

                #read the file content
                with open(recv_filename, "wb") as f:
                    while True:
                        # read 1024 bytes from the socket (receive)
                        print("reading bytes ...")
                        bytes_read = client_socket.recv(BUFFER_SIZE)
                        # try encode using utf-8
                        try:
                            bytes_utf8 = bytes_read.decode('utf-8')
                            if bytes_utf8 == "CONFIRMATION::FILE_TRANSFER_DONE\n":
                                print("File transfer done ~")
                                break
                        except:
                            None

                        print(bytes_read)
                        if not bytes_read:    
                            # nothing is received
                            # file transmitting is done
                            print("File transfer done ~")
                            break
                        # write to the file the bytes we just received
                        f.write(bytes_read)
                        print("write to file is done")
                        # check is the file transfer completed
                        if path.getsize(recv_filename) == recv_filesize:
                            print("File transfer done ~")
                            break

                None
            else:
                sys.stdout.write(f"[RECV] << {received_data}[SEND] >> ")
        else:
            sys.stdout.write(f"[RECV] << {received_data}[SEND] >> ")

except KeyboardInterrupt:
    client_socket.close()
    sys.exit(0)