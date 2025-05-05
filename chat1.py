import socket
from _thread import *
import time

check_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ### create socket 
chat_active = None
userchat = None
chat_socket = None    ### create many global variables
def check_server_connection(socket):  ### Function for checking if server is turned on
    try:
        socket.send(b'PING')   ### send PING 
        return True  ### success sending
    except socket.error:
        print("Server is down")  ### if not sending fail checked
        return False
def ansver_to_server_check(socket):  ###  Function for getting messages from server
    global chat_active
    global userchat
    while True:
        try:
            message = socket.recv(1024).decode('utf-8')
            parts = message.split(" ")
            if len(parts) == 1:
                if parts[0] == "PING": ### if message is PING, send PONG
                    socket.send("PONG".encode('utf-8'))
            elif parts[0] == "want_chat_with_you":  ### if message want_chat_with_you start begin of chat
                chat_active = True
                userchat = socket.recv(1024).decode('utf-8')   ### get username of chat partner
                print(f"{userchat} want chat with you\n want begin chat? yes/no")
            elif parts[0] == "chat_ended":
                chat_active = False
            else:
                print(f"{message}")
        except socket.error:
            print("Server is down")
            break



def handler(chat_socket):  ### Function for handling client
    print("Enter Command:\n/chat username - for start chat with username \n/exit - for exit for application")
    global chat_active
    global check_socket
    global userchat
    while True:
        try:
            if not check_server_connection(check_socket):  ### checking if server is turned on
                print("Connection to server lost")
                break
            else:
                command = input()  ### get command from client
                parts = command.split(" ")
                if len(parts) == 2: ### checking command
                    action = parts[0]
                    username = parts[1]
                    if action == "/chat": ### if command is chat
                        chat_socket.send(f"{action} {username}".encode('utf-8'))  ### send to server command
                        message = chat_socket.recv(1024).decode('utf-8')  ### get message from server if partner ansver yes
                        print(message)
                        if message == "start_chat":  ### check if message is start_chat
                            print(f"Chat started with {username}")
                            chat_active = True   ### change variable for chat
                            send_messages(chat_socket)  ### start chat
                        else:
                            print(message)
                elif len(parts) == 1:
                    action = parts[0]
                    if action == "/exit":  ### check if client want exit
                        exit()
                    elif action == "yes":  ### for ansver for chat
                        if chat_active:  ### if variable for chat is true
                            print(userchat)
                            chat_socket.send("yes".encode('utf-8'))  ### send to server 2 times yes with delay
                            time.sleep(2)
                            chat_socket.send("yes".encode('utf-8'))
                            time.sleep(2)
                            chat_socket.send(userchat.encode('utf-8'))  ### send server nickname of partner
                            print(f"Chat started with {userchat}")
                            time.sleep(2)
                            send_messages(chat_socket)  ### start chat
                        else:
                            chat_active = False  ### if response is no
                            print("chat decline")
                    else:
                        print("use correct command")
                else:
                    print("use correct command")
        except socket.error:
            print("Lost connection to server.")
            break
            
def send_messages(chat_socket):  ### Function for chat
    global chat_active
    while chat_active: ### chat active when variable is True
        try:
            if not check_server_connection(check_socket):   ### if server is turn off
                chat_active = False 
                print("Connection to server lost.")
                break
            
            message = input()  ### get message
            if message == "/quit":  ### if message is quit leave from chat
                chat_socket.send("/quit".encode('utf-8'))
                print("Disconnected from chat.")
                chat_active = False
                break
            else:
                chat_socket.send(message.encode('utf-8'))  ### send message if all OK
        except socket.error:
            print("Error sending message or server disconnected.")
            break

def login_to_server():   ### Function for login to server
    global check_socket
    while True:
        while True:
            try:
                login_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ###trying to connect to server
                login_socket.connect(('127.0.0.1', 12345))
                print("connected to server")
                break
            except socket.error:  ### if server is offline 
                print("server is down")
                print("try another? yes/no")
                user_input = input()
                if user_input != "yes":   ### if want another connect to server
                    print("Exiting")
                    exit()
                else:
                    print("Retrying")
                    
        while True:
            try:
                nickname = input("Enter your nickname: ")   ### write nickname
                login_socket.send("login_socket".encode('utf-8'))  ### send to server type of socket
                login_socket.send(f"{nickname}".encode('utf-8'))   ### send to server nickname
                response = login_socket.recv(1024).decode('utf-8')
                if response == "AUTH_SUCCESS":   ### if client is registered server send AUTH_SUCCESS
                    ip, port = login_socket.getsockname()  ### get ip and port from login socket
                    print("Successfully logged in!")
                    chat_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  ### create chat socket 
                    chat_socket.bind((ip, port+1))  ### binding socket with port+1 for easy checkin in server
                    chat_socket.connect(('127.0.0.1', 12345))   ### connect socket
                    chat_socket.send("chat_socket".encode('utf-8'))  ### send to server type of socket
                    check_socket.bind((ip, port+2))  ### binding socket with port+2 for easy checkin in server
                    check_socket.connect(('127.0.0.1', 12345))   ### connect socket
                    check_socket.send("check_socket".encode('utf-8'))   ### send to server type of socket
                    start_new_thread(ansver_to_server_check, (login_socket,))   ### start new thread for cheking messages from server
                    return chat_socket
                    
                else:
                    print("Login failed. Please try again.")   ### if login failed, try another
                    retry = input("Do you want to try again? (yes/no): ").strip().lower()
                    if retry != "yes":
                        print("Exiting") 
                        exit()
            except socket.error:
                print("Lost connection to server during login.")
                break

def main():   ### main function
    global chat_active
    chat_socket = login_to_server()  ### start login to server and return chat socket
    time.sleep(2)
    while True:  ### cycle for handle when not in chat
        if not chat_active:
            handler(chat_socket)

main()