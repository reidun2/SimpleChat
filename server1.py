import socket
from _thread import *
import pandas as pd
import time


users_table = pd.DataFrame(columns=['clientID']) ### Dataframe of registered users

for i in range(1, 11):   ### cycle for fill out the registered users
    new_row = pd.DataFrame({'clientID': [f'user{i}']})
    users_table = pd.concat([users_table, new_row], ignore_index=True)

connection_table = pd.DataFrame(columns=['clientAddress', 'client_nickname', 'login_socket', 'chat_socket', 'check_socket', 'in_chat']) ### Dataframe for tracking client connection

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   ###trying turn on server with that address
try:
    server_socket.bind(('127.0.0.1', 12345))
except socket.error as e:
    print(str(e))
print(f'Server is listing on the port {12345}...')
server_socket.listen()

print("Server started. Waiting for connections...")


def handle_client(chat_socket): ### Function for handling client and get command from him
    global connection_table
    while True:
        try:
            message = chat_socket.recv(1024).decode('utf-8')  ### get command
            parts = message.split(" ")
            if parts[0] == '/exit':   ### if command is exit go out from cycle
                print("Client disconnected.")
                break
            print(f"Received message: {message}")
            if parts[0] == "/chat":  ### if command is chat, start process begin chat
                username = parts[1]
                if username in users_table['clientID'].tolist():  ### check if client is registered
                    partner_row = connection_table[connection_table['client_nickname'] == username]   ### get all information of partner
                    iam_row = connection_table[connection_table['chat_socket'] == chat_socket]
                    if not partner_row.empty and not iam_row.empty:  ### check if information exist
                        partner_login_socket = partner_row.iloc[0]['login_socket']  
                        partner_chat_socket = partner_row.iloc[0]['chat_socket']
                        partner_chat_status = partner_row.iloc[0]['in_chat']
                        my_username = iam_row.iloc[0]['client_nickname']
                        if not partner_chat_status:  ### if partner in chat send to client what partner is not available
                            if partner_chat_socket != None and partner_login_socket != None:
                                try:
                                    partner_login_socket.send(f"want_chat_with_you {my_username}".encode('utf-8')) ### send to login socket of partner what client want begin chat
                                    partner_login_socket.send(my_username.encode('utf-8'))   ### and client username
                                    response = partner_chat_socket.recv(1024).decode('utf-8')  ### get response
                                    if response == "yes":  ### if response if yes, begin chat, else send to client what partner decline chat
                                        chat_socket.send("start_chat".encode('utf-8'))  ### send start chat to client
                                        connection_table.loc[connection_table['client_nickname'] == username, 'in_chat'] = True   ### variable for checking if client in chat now True
                                        connection_table.loc[connection_table['chat_socket'] == chat_socket, 'in_chat'] = True
                                        print(f"{chat_socket}\n")
                                        print(partner_login_socket)
                                        print("\n")
                                        rellay_message(chat_socket,partner_login_socket)  ### start function of chating and exit from handle
                                        return
                        
                                    else:
                                        chat_socket.send(f"{username} decline chat".encode('utf-8'))
                                except socket.error:
                                    print(f"Partner {username} is not active.")
                                    chat_socket.send(f"{username} is offline.".encode('utf-8'))
                            else:
                                print(f"Error: partner_socket is not a valid socket. Type: {type(partner_chat_socket)}")
                                chat_socket.send(f"{username} is offline.".encode('utf-8'))
                        else:
                            chat_socket.send(f"{username} is not available".encode('utf-8'))
                    else:
                        chat_socket.send(f"{username} is offline".encode('utf-8'))
                else:
                    chat_socket.send(f"{username} doesn't exist".encode('utf-8'))   
            elif parts[0] == "yes":    ### part of partner geting only yes from him
                username = chat_socket.recv(1024).decode('utf-8')  ### geting username of client
                print(f"{chat_socket}\n")
                partner_row = connection_table[connection_table['client_nickname'] == username] ### getting all information of client
                if not partner_row.empty:
                    partner_login_socket = partner_row.iloc[0]['login_socket']
                    partner_chat_socket = partner_row.iloc[0]['chat_socket']
                    if partner_chat_socket != None and partner_login_socket != None:
                        print(partner_login_socket)
                        print("\n")
                        rellay_message(chat_socket,partner_login_socket)  ### start function symmetrically
                        return
        except ConnectionResetError:
            print("Client forcefully closed the connection.")   ### exception if client close programm or lose connection
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    disconnect_client(chat_socket)

def rellay_message(client1_socket,client2_socket):   ### Function for getting and sending messages. Function is symmetrically
    try:
        sender_row = connection_table[connection_table['chat_socket'] == client1_socket]   ### get nickname of client
        if not sender_row.empty:
            username = sender_row.iloc[0]['client_nickname']
        while True:
            try:
                print(f"{username} send")   
                message = client1_socket.recv(1024).decode('utf-8')   ### get messages from client
                if message == "/quit":  ### exit if message is quit
                    print(f"{username} disconnected from chat.")
                    client2_socket.send("chat_ended".encode('utf-8'))
                    connection_table.loc[connection_table['login_socket'] == client2_socket, 'in_chat'] = False   ### change chat status of client
                    break
                else:
                    client2_socket.send(f"{username}: {message}".encode('utf-8'))  ### sending messages to partner
            except ConnectionResetError:   ### if connection error exit from function and start again handle for partner
                print(f"{username} disconnected from chat.")
                client2_socket.send("chat_ended".encode('utf-8'))   
                connection_table.loc[connection_table['login_socket'] == client2_socket, 'in_chat'] = False
                disconnect_client(client1_socket)
                break
    except Exception as e:
        print(f"Error in chat: {e}")
    finally:   ### start again handle for partner
        receiver_row = connection_table[connection_table['login_socket'] == client2_socket]
        if not receiver_row.empty():
            receiver_chat_socket = receiver_row.iloc[0]['chat_socket']
        print("Chat ended.")
        return handle_client(receiver_chat_socket)

def disconnect_client(socket):  ### Function for disconnect client and delete him from connection table
    global connection_table
    print(f"Client {socket} has disconnected.")
    connection_table = connection_table[connection_table['chat_socket'] != socket]
    socket.close()

def login_client(client_socket, client_address):    ### Function for login client
    global connection_table
    ip, port = client_address
    nickname = None
    try:
        while True:
            type_socket = client_socket.recv(1024).decode('utf-8')  ### client send 3 type of socket
            print(type_socket)
            if type_socket == "login_socket":  ### first socket for login and check message from server
                nickname = client_socket.recv(1024).decode('utf-8')  ###nickname of client if he registered
                if not nickname:  ### if empty canceling loop
                    print(f"Client {client_address} disconnected.")
                    break
                if nickname in users_table['clientID'].tolist():   ### check if client is registered
                    client_socket.send("AUTH_SUCCESS".encode('utf-8'))
                    new_row = pd.DataFrame({'clientAddress': [f"{ip}:{port}"],'client_nickname': [nickname], 'login_socket': [client_socket], 'chat_socket': [None], 'check_socket': [None], 'in_chat': [False]})  ### create new connection row for new client
                    connection_table = pd.concat([connection_table, new_row], ignore_index=True) 
                    break
                else:
                    client_socket.send("AUTH_DENIED".encode('utf-8'))   ### if client not registered or incorrect login
            if type_socket == "chat_socket":  ### second type of socket for chating
                connection_table.loc[connection_table['clientAddress'] == f"{ip}:{port-1}", 'chat_socket'] = client_socket
                start_new_thread(handle_client, (client_socket,))   ###start new thread for handle client
                return
            if type_socket == "check_socket":  ### third type of socket for checking if server is on
                connection_table.loc[connection_table['clientAddress'] == f"{ip}:{port-2}", 'check_socket'] = client_socket
                start_new_thread(check_from_client, (client_socket,))  ### thread for getting PING from client and ansver him what server is turned on
                return
    except ConnectionResetError:   ### if login failed
        print(f"Connection with {client_address} was reset by the client.")
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
        client_socket.close() ### closing socket if login failed
            
def check_from_client(socket):  ### Function for check from client if server is turned on
    while True:
        try:
            ping = socket.recv(1024).decode('utf-8')  ### if not get ping client disconnected
            if not ping:
                print("Client disconnected")
                break
        except ConnectionResetError:
            print("disconnected")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
        socket.close()  ### closing socket
        
def check_for_inactive_clients():  ### Function for checking inactive clients
    global connection_table
    while True:
        time.sleep(60)  # check every minute
        for idx, row in connection_table.iterrows():
            client_socket = row['login_socket']
            try:
                client_socket.send("PING".encode('utf-8'))  ### sending PING to client 
                client_socket.settimeout(5)  # 5 second timeout for response
                response = client_socket.recv(1024).decode('utf-8')
                if response != "PONG":
                    print(f"Client {row['clientAddress']} did not respond to ping.")
                    client_socket.close()  ### if getting not PONG closing socket
                    connection_table.drop(idx, inplace=True)  ### deleting client from dataframe
            except (socket.timeout, socket.error):   ### If there was a sending error or timeout, the client closed the connection
                print(f"Client {row['clientAddress']} disconnected unexpectedly.")
                client_socket.close()
                connection_table.drop(idx, inplace=True)  ### deleting client from dataframe

start_new_thread(check_for_inactive_clients, ())
# The main server loop that accepts the connection
while True:
    client_socket, client_address = server_socket.accept() ###accept new client
    print(f"Connection from {client_address} established.")
    start_new_thread(login_client, (client_socket, client_address)) ###start new thread with that client