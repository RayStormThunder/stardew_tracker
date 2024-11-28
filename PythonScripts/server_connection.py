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
all_locations_path = "../JSONStore/all_locations.json"
current_items_path = "../JSONStore/current_items.json"
all_data_path = "../JSONPull/all_data.json"
data_path = "../JSONStore/data.json"
log_file_path = "../serverlog.txt"
hollow_knight_item_file_path = "../JSONPull/hollow_knight_item_table.json"
hollow_knight_location_file_path = "../JSONPull/hollow_knight_location_table.json"

# Load the Hollow Knight item and location data
with open(hollow_knight_item_file_path, 'r') as hk_item_file:
    hollow_knight_item_data = json.load(hk_item_file)["items"]

with open(hollow_knight_location_file_path, 'r') as hk_location_file:
    hollow_knight_location_data = json.load(hk_location_file)["locations"]

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

    #test_response = '[{"cmd":"PrintJSON","data":[{"text":"1","type":"player_id"},{"text":" found their "},{"text":"16777216","player":1,"flags":2,"type":"item_id"},{"text":" ("},{"text":"717001","player":1,"type":"location_id"},{"text":")"}],"type":"ItemSend","receiving":1,"item":{"item":722215,"location":719339,"player":1,"flags":2,"class":"NetworkItem"}}]'
    
    is_test = response is None  # Track if we’re using the test response
    #response = response or test_response  # Use actual response if provided, else use test_response

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
                elif cmd_type == "ReceivedItems":
                    asyncio.create_task(handle_ReceivedItems(entry))
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

async def handle_ReceivedItems(entry):
    """Process 'ReceivedItems' command to retrieve item names based on item codes and update current_items.json."""
    received_items = entry.get("items", [])
    index = entry.get("index", 0)  # Default to 0 if index is not provided
    item_names = []

    # Retrieve names for each received item based on item code
    for item in received_items:
        item_id = item.get("item")
        item_name = get_item_name(item_id)
        if item_name:
            item_names.append(item_name)
            print(f"Found item: {item_name} (ID: {item_id})")  # Log successful lookup
        else:
            item_names.append("Unknown Item")
            print(f"Warning: Item ID {item_id} not found in item table.")  # Log missing item

    # Load existing items from current_items.json
    try:
        with open(current_items_path, 'r') as current_items_file:
            current_items_data = json.load(current_items_file)
            current_items = current_items_data.get("current_items", [])
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or has errors, start with an empty list
        current_items = []

    # Decide whether to replace or add based on the index value
    if index == 0:
        # Replace the entire list
        current_items = item_names
    elif index > 0:
        # Add items to the existing list
        current_items.extend(item_names)

    # Update current_items.json with the modified list
    with open(current_items_path, 'w') as current_items_file:
        json.dump({"current_items": current_items}, current_items_file, indent=4)

    # Print or store the list of received item names
    print_to_server_console("Updated Current Items", 1)

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
                print(f"Item ID: {int(text)}")
                id = int(text)
                item_name = get_item_name(int(text))
                true_state = 0
                print("true_state = 0(Item)")
                if item_name:
                    text = item_name
                    if id > 10000000:
                        true_state = 3

                else:
                    text = "Otherworldly Item"
                    item_unknown = True
            elif item_type == "location_id":
                print(f"Location ID: {int(text)}")
                id = int(text)
                location_name = get_location_name(int(text))
                true_state = 0
                print("true_state = 0(Location)")
                if location_name:
                    text = location_name
                    if id > 10000000:
                        true_state = 2
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
    """Process 'Connected' command to save player and location information, and update all_locations.json."""
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

    # Process checked and missing locations
    game_checked_locations = entry.get("checked_locations", [])
    print(f"checked locations = {game_checked_locations}")
    missing_locations = entry.get("missing_locations", [])  # Retrieve missing locations

    # Load the location table
    try:
        with open(location_file_path, 'r') as location_file:
            location_table = json.load(location_file)["locations"]
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Could not load stardew_valley_location_table.json.")
        return

    # Load existing checked_locations.json
    try:
        with open(checked_location_path, 'r') as checked_file:
            checked_locations_data = json.load(checked_file)
    except (FileNotFoundError, json.JSONDecodeError):
        checked_locations_data = {"checked_locations": []}

    # Match checked locations by code and update checked_locations.json
    for loc_code in game_checked_locations:
        matched_location = next(
            (name for name, details in location_table.items() if details["code"] == loc_code),
            None
        )
        if matched_location and matched_location not in checked_locations_data["checked_locations"]:
            checked_locations_data["checked_locations"].append(matched_location)

    # Save updated checked_locations.json
    with open(checked_location_path, 'w') as checked_file:
        json.dump(checked_locations_data, checked_file, indent=4)
        print("Updated checked_locations.json")

    # Process all locations for all_locations.json
    all_locations = [loc for loc in checked_locations_data["checked_locations"]]
    missing_location_names = [
        loc for loc in missing_locations
        if loc not in [details["code"] for details in location_table.values()]
    ]

    # Save combined all_locations.json
    all_locations_data = {
        "all_locations": sorted(all_locations),        # Sort alphabetically
        "missing_locations": missing_location_names    # Include missing locations if needed
    }

    with open(all_locations_path, 'w') as all_locations_file:
        json.dump(all_locations_data, all_locations_file, indent=4)

    update_data_with_all_locations()


def update_data_with_all_locations():

    # Load all_data.json
    try:
        with open(all_data_path, 'r') as all_data_file:
            all_data = json.load(all_data_file)
    except FileNotFoundError:
        print("Error: all_data.json file not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode all_data.json.")
        return

    # Load data.json
    try:
        with open(data_path, 'r') as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        print("Error: data.json file not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode data.json.")
        return

    # Load all_locations.json to get the list of valid locations
    try:
        with open(all_locations_path, 'r') as all_locations_file:
            all_locations_data = json.load(all_locations_file)
            all_locations = set(all_locations_data["all_locations"])  # Convert to set for fast lookups
    except FileNotFoundError:
        print("Error: all_locations.json file not found.")
        return
    except json.JSONDecodeError:
        print("Error: Could not decode all_locations.json.")
        return

    # Track missing locations in both directions
    missing_locations_from_data = []
    missing_locations_from_locations = []

    # Forward Check: Loop through each section in all_data.json
    for key, entries in all_data.items():
        # Ensure the section exists in data.json
        if key not in data:
            data[key] = []

        # Append entries that match locations in all_locations
        for entry in entries:
            location_name = entry[3]  # The 4th field is the location name
            if location_name in all_locations:
                # Check if an entry with the same location name already exists in data[key]
                if any(existing_entry[3] == location_name for existing_entry in data[key]):
                    print(f"Duplicate entry for '{location_name}' found in '{key}', skipping.")
                else:
                    data[key].append(entry)
            else:
                if location_name not in missing_locations_from_data:
                    missing_locations_from_data.append(location_name)
                    print(f"Location '{location_name}' not found in all_locations.json, adding to missing list.")

    # Reverse Check: Ensure all_locations are in all_data
    all_data_locations = {entry[3] for entries in all_data.values() for entry in entries}
    for location in all_locations:
        if location not in all_data_locations:
            missing_locations_from_locations.append(location)
            print(f"Location '{location}' is in all_locations.json but missing from all_data.json.")


    # Print out the entire `data` structure for inspection before saving
    #print("\nData structure before saving to data.json:")
    #print(json.dumps(data, indent=4))

    # Check if the data.json file has write permissions
    if os.access(data_path, os.W_OK):
        print("data.json has write permissions.")
    else:
        print("data.json does NOT have write permissions.")

    # Write the updated data.json safely
    try:
        with open(data_path, 'w') as data_file:
            json.dump(data, data_file, indent=4)
            data_file.flush()  # Ensure data is written to the file
            os.fsync(data_file.fileno())  # Ensure data is written to disk
    except Exception as e:
        print(f"Error occurred while saving data.json: {e}")
        return

    # Confirm changes by reloading data.json
    try:
        with open(data_path, 'r') as data_file:
            saved_data = json.load(data_file)
            print(json.dumps(saved_data, indent=4))
            if saved_data == data:
                print("Changes confirmed in data.json.")
            else:
                print("Warning: Changes not reflected in reloaded data.json.")
    except Exception as e:
        print(f"Error occurred while reloading data.json for confirmation: {e}")

    print_to_server_console("Updated All Locations", 4)
        

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
