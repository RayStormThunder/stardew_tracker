# server_connection.py

import asyncio
import os
import websockets
import json
import uuid
import socket
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from NetUtils import encode
import Utils

# Paths for item and location tables in JSONPull
item_file_path = "../JSONPull/stardew_valley_item_table.json"
location_file_path = "../JSONPull/stardew_valley_location_table.json"
player_table_path = "../JSONStore/player_table.json"
checked_location_path = "../JSONStore/checked_location.json"
log_file_path = "../serverlog.txt"

# Define a global websocket variable
global_websocket = None

class MessageEmitter(QObject):
    message_signal = pyqtSignal(str, int)  # Emit both text and state


# Instantiate a global emitter object
message_emitter = MessageEmitter()

async def connect_to_server(server_address, player_slot):
    """Establish WebSocket connection and start listening."""
    global global_websocket  # Use global variable to store the websocket instance
    try:
        async with websockets.connect(server_address) as websocket:
            global_websocket = websocket  # Assign the websocket instance
            print(f"Connected to server at {server_address}")
            await send_initial_connect(global_websocket, player_slot)

            # Listen for server messages and process them
            await listen_to_server(global_websocket)

    except Exception as e:
        print("An error occurred:", e)

async def handle_server_message(message, send_to_main_program):
    """Extracts and processes text from server messages, sending it to the main program."""
    try:
        data = json.loads(message)
        if "data" in data and isinstance(data["data"], list) and "text" in data["data"][0]:
            extracted_text = data["data"][0]["text"]
            send_to_main_program(extracted_text)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"Error processing message: {e}")

async def listen_to_server(websocket):
    """Constantly listen to the server and emit each message."""
    try:
        while True:
            response = await websocket.recv()
            await log_to_file(response)  # Log each message to the log file

            # Parse the response and handle the parsed data
            parse_server_response(response)

    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None, None

with open(item_file_path, 'r') as item_file:
    item_data = json.load(item_file)["items"]

with open(location_file_path, 'r') as location_file:
    location_data = json.load(location_file)["locations"]

if os.path.exists(player_table_path):
    with open(player_table_path, 'r') as player_file:
        try:
            data = json.load(player_file)
        except json.JSONDecodeError:
            print("Error: Could not decode JSON in player_table.json.")

if os.path.exists(checked_location_path):
    with open(checked_location_path, 'r') as checked_file:
        try:
            data = json.load(checked_file)
        except json.JSONDecodeError:
            print("Error: Could not decode JSON in checked_location.json.")

def get_item_name(item_id):
    """Retrieve the item name by item ID."""
    for name, info in item_data.items():
        if info["code"] == item_id:
            return name
    return None  # Return None if item ID is not found

def get_location_name(location_id):
    """Retrieve the location name by location ID."""
    for name, info in location_data.items():
        if info["code"] == location_id:
            return name
    return None  # Return None if location ID is not found

# Load player data from player_table.json
def load_player_data():
    try:
        with open(player_table_path, 'r') as player_file:
            data = json.load(player_file)
            return data.get("players", [])
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: player_table.json file not found or could not be decoded.")
        return []

# Get player name by slot from the loaded player data
def get_player_name_by_slot(slot, players):
    for player in players:
        if player["slot"] == slot:
            return player["name"]
    return None  # Return None if the slot is not found

def parse_server_response(response=None):
    """Parse the server response and perform actions based on the 'cmd' field."""

    # Test Both Correct
    #test_response = '[{"cmd":"PrintJSON","data":[{"text":"1","type":"player_id"},{"text":" found their "},{"text":"722215","player":1,"flags":2,"type":"item_id"},{"text":" ("},{"text":"719339","player":1,"type":"location_id"},{"text":")"}],"type":"ItemSend","receiving":1,"item":{"item":722215,"location":719339,"player":1,"flags":2,"class":"NetworkItem"}}]'
    # Test Item Only Correct
    #test_response = '[{"cmd":"PrintJSON","data":[{"text":"1","type":"player_id"},{"text":" found their "},{"text":"722215","player":1,"flags":2,"type":"item_id"},{"text":" ("},{"text":"339","player":1,"type":"location_id"},{"text":")"}],"type":"ItemSend","receiving":1,"item":{"item":722215,"location":719339,"player":1,"flags":2,"class":"NetworkItem"}}]'
    # Test Location Only Correct
    #test_response = '[{"cmd":"PrintJSON","data":[{"text":"1","type":"player_id"},{"text":" found their "},{"text":"215","player":1,"flags":2,"type":"item_id"},{"text":" ("},{"text":"719339","player":1,"type":"location_id"},{"text":")"}],"type":"ItemSend","receiving":1,"item":{"item":722215,"location":719339,"player":1,"flags":2,"class":"NetworkItem"}}]'
    # Test Neither Correct
    test_response = '[{"cmd":"PrintJSON","data":[{"text":"1","type":"player_id"},{"text":" found their "},{"text":"215","player":1,"flags":2,"type":"item_id"},{"text":" ("},{"text":"339","player":1,"type":"location_id"},{"text":")"}],"type":"ItemSend","receiving":1,"item":{"item":722215,"location":719339,"player":1,"flags":2,"class":"NetworkItem"}}]'
    
    is_test = response is None  # Track if we’re using the test response
    response = response or test_response  # Use actual response if provided, else use test_response

    try:
        data = json.loads(response)

        # Check if the response is a list of dictionaries
        if isinstance(data, list):
            for entry in data:
                cmd_type = entry.get("cmd")
                
                # Call different functions based on the command type
                if cmd_type == "PrintJSON":
                    handle_print_json(entry)
                elif cmd_type == "Connected":
                    asyncio.create_task(handle_connected(entry))
                else:
                    print(f"Unknown command: {cmd_type}")

        else:
            print("Unexpected data format. Expected a list of dictionaries.")

    except json.JSONDecodeError:
        print("Failed to decode JSON from server response.")
    except Exception as e:
        print(f"An error occurred while parsing the response: {e}")

    # Only call the function with the test response if it's actually a test
    if not is_test:
        parse_server_response()

def handle_print_json(entry):
    """Process 'PrintJSON' command to interpret and display text fields."""
    players = load_player_data()  # Load players from JSON file

    try:
        with open(checked_location_path, 'r') as location_file:
            checked_locations_data = json.load(location_file)
    except (FileNotFoundError, json.JSONDecodeError):
        checked_locations_data = {"checked_locations": []}

    if "data" in entry and isinstance(entry["data"], list):
        # Check for "[Hint]: " at the start of the first text field
        is_hint_message = entry["data"][0].get("text", "").startswith("[Hint]: ")

        message_parts = []
        item_unknown = False
        location_unknown = False
        state = not is_hint_message  # Set state to False if it's a hint message
        true_state = 3
        print("true_state = 3")

        for item in entry["data"]:
            # Process text field and additional information if present
            text = item.get("text", "")
            item_type = item.get("type")

            # Interpret player, item, and location codes using JSON lookup
            if item_type == "player_id":
                player_name = get_player_name_by_slot(int(text), players)
                text = player_name if player_name else "Unknown Player"
            elif item_type == "item_id":
                item_name = get_item_name(int(text))
                true_state = 0
                print("true_state = 0(Item)")
                if item_name:
                    text = item_name
                else:
                    text = "Otherworldly Item"
                    item_unknown = True
            elif item_type == "location_id":
                location_name = get_location_name(int(text))
                true_state = 0
                print("true_state = 0(Location)")
                if location_name:
                    text = location_name
                    # Only update checked_location.json if it's not a hint message
                    if not is_hint_message and location_name not in checked_locations_data["checked_locations"]:
                        checked_locations_data["checked_locations"].append(location_name)
                        # Save the updated list back to the file
                        with open(checked_location_path, 'w') as location_file:
                            json.dump(checked_locations_data, location_file, indent=4)
                else:
                    text = "Otherworldly Location"
                    location_unknown = True

            # Add interpreted text to message parts
            message_parts.append(text)


        if item_unknown == True:
            true_state = 1
            print("true_state = 1")
        if location_unknown == True:
            true_state = 2
            print("true_state = 2")
        if (item_unknown and location_unknown) == True:
            true_state = 3
            print("true_state = 3")

        if not (item_unknown and location_unknown):
            full_message = "".join(message_parts)
            print(f"Final True State = {true_state}")
            print_to_server_console(full_message, true_state)

async def handle_connected(entry):
    """Process 'Connected' command to save player and location information."""
    # Extract and save player data to 'player_table.json'
    player_info = entry.get("players", [])
    player_table = [
        {
            "team": player["team"],
            "slot": player["slot"],
            "alias": player["alias"],
            "name": player["name"],
            "class": player["class"]
        }
        for player in player_info
    ]
    
    with open(player_table_path, 'w') as player_file:
        json.dump({"players": player_table}, player_file, indent=4)

    # Extract, convert to names, and sort checked locations alphabetically
    game_checked_locations = entry.get("checked_locations", [])
    checked_locations = sorted(
        [get_location_name(loc) for loc in game_checked_locations if get_location_name(loc)]
    )

    with open(checked_location_path, 'w') as location_file:
        json.dump({"checked_locations": checked_locations}, location_file, indent=4)

    print_to_server_console("Updated Checked Locations", 3)

def print_to_server_console(text, state):
    """Emit the parsed text to the server console output in Tracker.py."""
    # Emit the text to the connected GUI console in Tracker.py
    message_emitter.message_signal.emit(text, state)

async def log_to_file(message):
    """Append a message to the log file."""
    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")

async def send_initial_connect(websocket, player_name):
    """Send the initial Connect packet to the server."""
    connect_packet = [{
        'cmd': 'Connect',
        'password': None,
        'name': player_name,
        'version': Utils.version_tuple,
        'tags': ['AP', 'TextOnly'],
        'items_handling': 7,
        'uuid': str(uuid.uuid4()),
        'game': '',
        'slot_data': False
    }]

    await websocket.send(encode(connect_packet))
    print(f"Sending at: {websocket}")
    print("Sent initial Connect packet to the server.")

    # Start listening to the server for incoming messages
    await listen_to_server(websocket)

async def send_message_to_server(message_text):
    """Format and send the message JSON to the server using the global WebSocket connection."""
    if global_websocket is None:
        print("WebSocket connection is not established.")
        return

    # Construct the message JSON
    message_json = [{
        "cmd": "Say",
        "text": f"{message_text}"
    }]

    # Send the encoded JSON message to the server
    print(f"Sending: {encode(message_json)}")
    print(f"Sending at: {global_websocket}")
    await global_websocket.send(encode(message_json))
