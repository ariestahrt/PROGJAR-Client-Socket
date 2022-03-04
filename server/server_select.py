import socket
import select
import sys
import os
from os import path

BUFFER_SIZE = 1024*4

server_address = ('127.0.0.1', 5000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind(server_address)
server_socket.listen(5)

input_socket = [server_socket]

try:
    while True:
        read_ready, write_ready, exception = select.select(input_socket, [], [])
        
        for sock in read_ready:
            if sock == server_socket:
                client_socket, client_address = server_socket.accept()
                print(f"[+] New client {client_address} is connected.")
                input_socket.append(client_socket)
            else:            	
                data = sock.recv(BUFFER_SIZE)
                print(f"[!] {sock.getpeername()} << {data.decode().rstrip()}")

                data_split = f"{data.decode().rstrip()} ".split(" ")

                if data_split[0] == "unduh":
                    # check if file exist
                    filename = data.decode().split("unduh ")[1].rstrip()
                    if path.exists(f"dataset/{filename}"):
                        sock.send(bytes("CONFIRMATION::FILE_EXIST\n", 'utf-8'))                        
                        filesize = os.path.getsize(f"dataset/{filename}")

                        # initiate headers
                        header = f"file-name: {filename}\n"
                        header += f"file-size: {filesize}\n\n\n"
                        sock.send(bytes(header, 'utf-8'))

                        # start sending the file
                        total_data_sent = 0
                        with open(f"dataset/{filename}", "rb") as f:
                            while True:
                                # read the bytes from the file
                                bytes_read = f.read(BUFFER_SIZE)
                                total_data_sent += len(bytes_read)
                                #update the progress status
                                print(f"[!] File transfer {filename} : {total_data_sent}B/{filesize}B ({int((total_data_sent/filesize)*100)}%)                 \r", end="")

                                if not bytes_read:
                                    print("[!] Transfer fle is done!")
                                    # file transmitting is done
                                    break

                                # send to client
                                sock.sendall(bytes_read)
                    else:
                        sock.send(bytes("filenya gaada bos\n", 'utf-8'))
                elif data_split[0] == "dataset":
                    # get file list
                    dir_list = os.listdir("dataset")
                    # Send message file list available
                    temp_msg = "List available file:"
                    for file in dir_list:
                        # check file size
                        filesize = os.path.getsize(f"dataset/{file}")

                        temp_msg += f"\n\t[~] {file} \t {filesize} B"
                    sock.send(f"\n{temp_msg}\n".encode())
                elif data_split[0] == "REQUEST::DISCONNECT":
                    print(f"[-] Client {sock.getpeername()} just disconnected.")
                    sock.close()
                    input_socket.remove(sock)
                    None
                else:
                    if data:
                        sock.send(data)
                    else:
                        print(f"[-] Client {sock.getpeername()} just disconnected.")
                        sock.close()
                        input_socket.remove(sock)
            

except KeyboardInterrupt:
    server_socket.close()
    sys.exit(0)