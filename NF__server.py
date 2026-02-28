import socket
import threading
import time

# Core Settings
HOST = '192.168.49.1'
PORT = 5554
MAX_PLAYERS = 3
GRID_SIZE = 100



# Game State
# Every index in this list will now represent a real human player
players = [] 
current_turn = 0

def get_map_string():
    """Creates a text-based visual of the game area"""
    display_size = 10
    grid = [[" . " for _ in range(display_size)] for _ in range(display_size)]
    
    for p in players:
        px, py = p["pos"][0] % display_size, p["pos"][1] % display_size
        grid[py][px] = f"[{p['name'][0].upper()}]"
        
    map_render = "\n--- ESCAPE ROOM LAYOUT ---\n"
    for row in grid:
        map_render += "".join(row) + "\n"
    return map_render

def broadcast(msg):
    """Sends a message to all connected human players"""
    for p in players:
        try:
            p["conn"].send(msg.encode('utf-8'))
        except:
            pass

def broadcast_turn_status():
    """Notifies players of the map and identifies whose turn it is"""
    global current_turn
    layout = get_map_string()
    active_player = players[current_turn]
    
    for i, p in enumerate(players):
        try:
            # Clear screen effect for a better layout view
            p["conn"].send("\033[H\033[J".encode('utf-8')) 
            p["conn"].send(layout.encode('utf-8'))
            
            if i == current_turn:
                p["conn"].send("\n*** YOUR TURN! Enter move (w/a/s/d) or chat:msg ***\n".encode('utf-8'))
            else:
                p["conn"].send(f"\nWaiting for {active_player['name']} to move...\n".encode('utf-8'))
        except:
            pass

def handle_client(conn, index):
    global current_turn
    try:
        conn.send("WELCOME TO ESCAPE ROOM! Enter Name: ".encode('utf-8'))
        name = conn.recv(1024).decode('utf-8').strip()
        
        # Initialize player at a starting position
        players.append({"conn": conn, "name": name, "pos": [index*2, index*2]})
        print(f"Player {index + 1} connected: {name}")

        # Wait for all group members to join before starting
        while len(players) < MAX_PLAYERS:
            conn.send(f"Waiting for {MAX_PLAYERS - len(players)} more players...\n".encode('utf-8'))
            import time
            time.sleep(2)

        broadcast(f"\nSYSTEM: {name} has joined. The game begins!")
        broadcast_turn_status()

        while True:
            msg = conn.recv(1024).decode('utf-8').strip().lower()
            if not msg: break

            if current_turn == index:
                if msg in ['w', 'a', 's', 'd']:
                    p_pos = players[index]["pos"]
                    if msg == 'w': p_pos[1] = (p_pos[1] - 1) % GRID_SIZE
                    if msg == 's': p_pos[1] = (p_pos[1] + 1) % GRID_SIZE
                    if msg == 'a': p_pos[0] = (p_pos[0] - 1) % GRID_SIZE
                    if msg == 'd': p_pos[0] = (p_pos[0] + 1) % GRID_SIZE
                    
                    # Update turn to the next human player
                    current_turn = (current_turn + 1) % MAX_PLAYERS
                    broadcast_turn_status()
                elif msg.startswith("chat:"):
                    broadcast(f"CHAT [{name}]: {msg[5:]}")
            else:
                conn.send("WAIT: It is not your turn!\n".encode('utf-8'))
    except:
        pass

# Server Initialization
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_PLAYERS)
print(f"Server Ready on {HOST}:{PORT}. Waiting for {MAX_PLAYERS} members...")

conn_count = 0
while conn_count < MAX_PLAYERS:
    c, addr = server.accept()
    threading.Thread(target=handle_client, args=(c, conn_count)).start()
    conn_count += 1
