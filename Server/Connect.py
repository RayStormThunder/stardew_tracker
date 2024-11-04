import asyncio
import websockets
import json
import uuid
import os
from NetUtils import encode

# Constants
SERVER_URI = "wss://archipelago.gg"  # Fixed server URI
CONFIG_FILE = "config.json"  # Config file to store server port and player name
LOG_FILE = "server_log.txt"  # Log file for server messages

def save_config(port, player_name):
    """Save the server port and player name to config.json."""
    with open(CONFIG_FILE, "w") as file:
        json.dump({"server_port": port, "player_name": player_name}, file)

def load_config():
    """Load the server port and player name from config.json if it exists."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            config = json.load(file)
            return config.get("server_port"), config.get("player_name")
    return None, None

async def log_to_file(message):
    """Append a message to the log file."""
    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")

async def send_initial_connect(websocket, player_name):
    """Send the initial Connect packet to the server."""
    connect_packet = {
        'cmd': 'Connect',
        'password': None,
        'name': player_name,
        'version': 'Version(major=0, minor=5, build=0)',
        'tags': ['AP', 'TextOnly'],
        'items_handling': 7,
        'uuid': str(uuid.uuid4()),
        'game': '',
        'slot_data': False
    }

    # Convert to JSON string and send
    await websocket.send(encode(connect_packet))
    print("Sent initial Connect packet to the server:", connect_packet)
    print("Sent encoded Connect packet to the server:", encode(connect_packet))

    # Start listening to the server for incoming messages
    await listen_to_server(websocket)

async def listen_to_server(websocket):
    """Constantly listen to the server and log each message."""
    try:
        while True:
            response = await websocket.recv()
            print("Server response:", response)
            await log_to_file(response)  # Log each message to the log file
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

async def connect_to_server(server_port, player_name):
    uri = f"{SERVER_URI}:{server_port}"
    try:
        # Connect to the server via WebSocket
        async with websockets.connect(uri) as websocket:
            print(f"Connected to server at {uri}")

            # Start listening to the server for incoming messages
            response = await websocket.recv()
            print("Server response:", response)
            await log_to_file(response)  # Log each message to the log file
            print(f"Waiting...")

            # Wait a bit for the server to respond before entering the listening loop
            await asyncio.sleep(2)
            print(f"Connecting...")

            # Send the initial Connect packet
            await send_initial_connect(websocket, player_name)


    except Exception as e:
        print("An error occurred:", e)

if __name__ == "__main__":
    # Load stored configuration if available
    stored_port, stored_player_name = load_config()

    # Prompt user for input with defaults
    server_port = input(f"Enter the server port (leave blank for {stored_port}): ") or stored_port
    if server_port is None:
        server_port = input("No stored port found. Please enter the server port: ")
    
    player_name = input(f"Enter your player name (leave blank for {stored_player_name}): ") or stored_player_name
    if player_name is None:
        player_name = input("No stored player name found. Please enter your player name: ")

    # Save the updated config
    save_config(server_port, player_name)

    # Run the connection asynchronously
    asyncio.run(connect_to_server(server_port, player_name))
