💬 Python Chat Application (Client-Server)
This is a simple two-user chat application built with Python, supporting TCP sockets, threaded connections, and a basic authentication system. The server manages user states and routing, while clients can initiate or receive chat requests.

⚙️ Architecture Overview
The application consists of two parts:

Server – handles authentication, message relaying, and client state.

Client – connects to the server, authenticates, and communicates with another user.

🧠 Client-Side Logic
🔌 Sockets
The client creates 3 separate sockets:

Login socket – for authentication and receiving server messages.

Chat socket – for sending messages and commands to the server.

Check socket – for sending PING signals to check server availability.

🌐 Global Variables
chat_active – synchronizes state across chat functions.

userchat – stores the username of the current chat partner.

check_socket – reference used in all functions to check server availability.

📚 Libraries Used
socket – for TCP communication

_thread – for multithreading

time – for delays

🛠️ Functions
Login_to_server()
Authenticates the user and connects all sockets. Handles server downtime and prompts the user to retry. Launches a thread for Ansver_to_server_check.

Handler(socket)
Handles user commands:

/exit – exits the app.

/chat <username> – attempts to start a chat.

yes – accepts incoming chat.

Check_server_connection(socket)
Sends a PING and expects a reply to confirm server is online.

Ansver_to_server_check(socket)
Listens for server signals:

PING → respond with PONG

want_chat_with_you → set chat_active = True

start_ended → set chat_active = False

Send_messages(chat_socket)
Sends messages in active chat. If the user sends /quit, the chat ends.

🧠 Server-Side Logic
📚 Libraries Used
socket – for TCP communication

_thread – for multithreading

pandas – for user and connection tables

time – for delays

📊 Data Structures
users_table – registered users (clientID)

connection_table – connected users with:

clientAddress

client_nickname

login_socket

chat_socket

check_socket

in_chat

🛠️ Functions
check_for_inactive_clients()
Continuously checks client activity via check_socket.

login_client(socket, address)
Authenticates clients, receives additional sockets, and stores in connection_table. Starts handle_client and check_from_client.

check_from_client(socket)
Listens for PING from clients on a separate thread.

handle_client(chat_socket)
Receives commands:

/exit → disconnects user.

/chat <username> → initiates chat if target user is online and accepts.

yes → accepts chat request.

rellay_message(socket1, socket2)
Relays messages between two clients. Ends on /quit or disconnection.

disconnect_client(socket)
Safely disconnects a client and cleans up from connection_table.

🚀 How to Use
🖥️ Server
Just run the server script:

python server.py


💻 Client
Run the client script:

python client.py


Then:

Enter your nickname.

Use commands:

/chat <username> to start a chat.

/exit to exit the app.

/quit to leave a chat.

🧩 Features
Multi-threaded communication

Basic authentication

Direct chat between two users

Server-client heartbeat check via PING/PONG
