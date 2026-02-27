import socket
import threading
import os
SERVER_IP = '192.168.49.1' # Replace with actual IP
PORT = 5555




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



def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(2048).decode('utf-8')
            if not message: break
            print(message)
        except:
            print("\n[CONNECTION LOST]")
            break

def start_client():
    show_welcome_screen()
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, PORT))
    except Exception as e:
        print(f"Error: Could not connect to {SERVER_IP}. {e}")
        return

    # Start thread to receive live feedback while user types
    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        user_input = input()
        client.send(user_input.encode('utf-8'))

if __name__ == "__main__":
    start_client()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, PORT))

def receive():
    while True:
        try:
            print(client.recv(2048).decode('utf-8'))
        except: break

threading.Thread(target=receive, daemon=True).start()

while True:
    cmd = input()
    client.send(cmd.encode('utf-8'))
# ... (Keep the show_welcome_screen from previous step)

def receive_thread(client_socket):
    while True:
        try:
            # Receive layout, turn notifications, and chat
            data = client_socket.recv(4096).decode('utf-8')
            if data:
                # Use a simple clear screen to keep the UI clean
                print("\033[H\033[J", end="") 
                print(data)
        except:
            break

