import socket
import threading
import time

# Core Settings
HOST = '192.168.49.1'
PORT = 5555
MAX_PLAYERS = 4
GRID_SIZE = 100



# Game State
players = [] # List of {"conn": conn, "name": name, "pos": [x,y], "is_bot": bool}
current_turn = 0

def get_map_string():
    """Creates a text-based visual of the game area"""
    # We display a 10x10 area for the terminal layout
    display_size = 10
    grid = [[" . " for _ in range(display_size)] for _ in range(display_size)]
    
    for p in players:
        px, py = p["pos"][0] % display_size, p["pos"][1] % display_size
        grid[py][px] = f"[{p['name'][0].upper()}]" # Show first letter of name
        
    map_render = "\n--- ESCAPE ROOM LAYOUT ---\n"
    for row in grid:
        map_render += "".join(row) + "\n"
    return map_render

def broadcast(msg):
    for p in players:
        if not p["is_bot"] and p["conn"]:
            try:
                p["conn"].send(msg.encode('utf-8'))
            except: pass

def handle_client(conn, index):
    global current_turn
    try:
        conn.send("Enter Name: ".encode('utf-8'))
        name = conn.recv(1024).decode('utf-8').strip()
        players[index] = {"conn": conn, "name": name, "pos": [index*2, index*2], "is_bot": False}
        
        broadcast(f"\nSYSTEM: {name} joined the game.")
        broadcast(get_map_string())

        while True:
            msg = conn.recv(1024).decode('utf-8').strip().lower()
            if current_turn == index:
                if msg in ['w', 'a', 's', 'd']:
                    # Update Position
                    p_pos = players[index]["pos"]
                    if msg == 'w': p_pos[1] = (p_pos[1] - 1) % GRID_SIZE
                    if msg == 's': p_pos[1] = (p_pos[1] + 1) % GRID_SIZE
                    if msg == 'a': p_pos[0] = (p_pos[0] - 1) % GRID_SIZE
                    if msg == 'd': p_pos[0] = (p_pos[0] + 1) % GRID_SIZE
                    
                    current_turn = (current_turn + 1) % MAX_PLAYERS
                    broadcast(get_map_string())
                    broadcast(f"NEXT TURN: {players[current_turn]['name']}")
                elif msg.startswith("chat:"):
                    broadcast(f"CHAT [{name}]: {msg[5:]}")
            else:
                conn.send("WAIT: It is not your turn!\n".encode('utf-8'))
    except: pass

# Init Bots
for i in range(MAX_PLAYERS):
    players.append({"conn": None, "name": f"Bot_{i+1}", "pos": [i, i], "is_bot": True})

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(MAX_PLAYERS)
print("Server Ready...")

conn_idx = 0
while conn_idx < MAX_PLAYERS:
    c, addr = server.accept()
    threading.Thread(target=handle_client, args=(c, conn_idx)).start()
    conn_idx += 1 
def broadcast_turn_status():
    """Notifies everyone of the state, but gives a special prompt to the active player."""
    global current_turn
    active_player = players[current_turn]
    
    # Redraw the layout for everyone
    layout = get_map_string()
    
    for i, p in enumerate(players):
        if p["is_bot"] or not p["conn"]:
            continue
            
        try:
            # Send the layout first
            p["conn"].send(layout.encode('utf-8'))
            
            # Send the specific turn notification
            if i == current_turn:
                p["conn"].send("\n*** YOUR TURN! Enter move (w/a/s/d) or chat:msg ***\n".encode('utf-8'))
            else:
                p["conn"].send(f"\nWaiting for {active_player['name']} to move...\n".encode('utf-8'))
        except:
            pass

# In your handle_client function, call broadcast_turn_status() after every successful move.
