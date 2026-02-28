import socket
import threading
import os
SERVER_IP = '192.168.49.1' # Replace with actual IP
PORT = 5554
MAX_PLAYERS = 3




def show_welcome_screen():
    # Clear terminal for a professional look
    os.system('cls' if os.name == 'nt' else 'clear')
    
    print("="*50)
    print("       WELCOME TO THE TERMINAL ESCAPE ROOM")
    print("          Networking Fundamentals Project")
    print("="*50)
    print("\nOVERVIEW:")
    print("This is a 4-player turn-based co-op game built using")
    print("Python Socket Programming. If players are missing,")
    print("the server will automatically assign AI Bots.")
    
    print("\nHOW TO PLAY & CONTROLS:")
    print("-" * 30)
    print("  W : Move Up (North)")
    print("  A : Move Left (West)")
    print("  S : Move Down (South)")
    print("  D : Move Right (East)")
    print("  CHAT:message : Talk to your teammates")
    print("-" * 30)
    print("\nRULES:")
    print("1. Commands only work when it is YOUR turn.")
    print("2. Coordinate with your team via chat to 'escape'!")
    print("="*50)
    input("\nPress ENTER to join the game server...")





# Game State
players = [] # List of {"conn": conn, "name": name, "pos": [x,y]}
current_turn = 0

def broadcast(msg):
    for p in players:
        try:
            p["conn"].send(msg.encode('utf-8'))
        except: pass

def handle_client(conn, index):
    global current_turn
    try:
        conn.send("WELCOME TO ESCAPE ROOM! Enter Name: ".encode('utf-8'))
        name = conn.recv(1024).decode('utf-8').strip()
        
        # Store human player data
        players.append({"conn": conn, "name": name, "pos": [index*5, index*5]})
        broadcast(f"\nSYSTEM: {name} joined the game!")

        # Wait until all 4 members join before starting turn logic
        while len(players) < MAX_PLAYERS:
            pass

        while True:
            msg = conn.recv(1024).decode('utf-8').strip().lower()
            
            if current_turn == index:
                if msg in ['w', 'a', 's', 'd']:
                    # Update Position Logic
                    p_pos = players[index]["pos"]
                    if msg == 'w': p_pos[1] -= 1
                    if msg == 's': p_pos[1] += 1
                    if msg == 'a': p_pos[0] -= 1
                    if msg == 'd': p_pos[0] += 1
                    
                    # Switch Turn
                    current_turn = (current_turn + 1) % MAX_PLAYERS
                    broadcast(f"\n{name} moved to {p_pos}")
                    players[current_turn]["conn"].send("\n*** YOUR TURN! ***\n".encode('utf-8'))
                elif msg.startswith("chat:"):
                    broadcast(f"CHAT [{name}]: {msg[5:]}")
            else:
                conn.send("WAIT: It is not your turn!\n".encode('utf-8'))
    except: pass

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_PLAYERS)
print("Server Ready. Waiting for 4 group members...")

conn_idx = 0
while conn_idx < MAX_PLAYERS:
    c, addr = server.accept()
    threading.Thread(target=handle_client, args=(c, conn_idx)).start()
    conn_idx += 1


