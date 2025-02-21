# server_connection.py

import asyncio
import bisect
from glob import glob
import yaml
import os
import re
import threading
import websockets
import json
import uuid
import socket
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from NetUtils import encode
import Utils
from functools import lru_cache

# Paths for item and location tables in JSONPull
item_file_path = "../JSONPull/item_name_to_id.json"
location_file_path = "../JSONPull/location_name_to_id.json"
player_table_path = "../JSONStore/player_table.json"
checked_location_path = "../JSONStore/checked_location.json"
all_locations_path = "../JSONStore/all_locations.json"
current_items_path = "../JSONStore/current_items.json"
hint_my_location_file_path = "../JSONStore/hint_my_location.json"
requirements_goals_file_path = "../JSONPull/requirements"
hint_my_item_file_path = "../JSONStore/hint_my_item.json"
all_data_path = "../JSONPull/all_data.json"
data_path = "../JSONStore/data.json"
config_path = "../JSONStore/config.json"
log_file_path = "../Logs/serverlog.txt"

# Dictionary to track file modification times
file_timestamps = {}


@lru_cache(maxsize=None)
def extract_items_from_json(folder_path):
    """Extracts unique items from all JSON files in a given folder."""
    
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory.")
        return []
    
    items_set = set()
    
    def extract_items(data):
        if isinstance(data, dict):
            if "item" in data:
                items_set.add(data["item"])  # Add to set to ensure uniqueness
            for value in data.values():
                extract_items(value)
        elif isinstance(data, list):
            for item in data:
                extract_items(item)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    extract_items(data)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error reading JSON file {file_path}: {e}")
    
    return sorted(items_set)  # Return a sorted list for consistency


# Load the JSON files into lists
with open(item_file_path, 'r') as item_file:
    item_data = json.load(item_file)  # Flat list of objects

with open(location_file_path, 'r') as location_file:
    location_data = json.load(location_file)  # Flat list of objects

# Preprocess the data into sorted lists and dictionaries for efficient lookups
item_ids = [entry["id"] for entry in item_data]
item_names = {entry["id"]: entry["name"] for entry in item_data}

location_ids = [entry["id"] for entry in location_data]
location_names = {entry["id"]: entry["name"] for entry in location_data}

def get_item_name(item_id):
    """Retrieve the item name by item ID using binary search."""
    index = bisect.bisect_left(item_ids, item_id)
    if index < len(item_ids) and item_ids[index] == item_id:
        return item_names[item_id]
    return "Unknown Item"

def get_location_name(location_id):
    """Retrieve the location name by location ID using binary search."""
    index = bisect.bisect_left(location_ids, location_id)
    if index < len(location_ids) and location_ids[index] == location_id:
        return location_names[location_id]
    return "Unknown Location"

# Define a global websocket variable
global_websocket = None
# Track the player's name
global_player_name = None


class MessageEmitter(QObject):
    message_signal = pyqtSignal(str)  # For messages
    connection_signal = pyqtSignal(bool)  # For connection status


# Instantiate a global emitter object
message_emitter = MessageEmitter()

async def connect_to_server(server_address, player_slot):
    """Establish WebSocket connection and start listening."""
    global global_websocket, global_connection_status  # Use global variables
    try:
        async with websockets.connect(server_address) as websocket:
            global_websocket = websocket  # Assign the websocket instance
            global_connection_status = True  # Mark as connected
            print(f"Connected to server at {server_address}")
            
            # Start the connection status checker in the background
            asyncio.create_task(check_connection_status())

            await send_initial_connect(global_websocket, player_slot)

            # Listen for server messages and process them
            await listen_to_server(global_websocket)

    except Exception as e:
        global_connection_status = False  # Mark as disconnected
        print_to_server_console(f"The server address: {server_address} is unresponsive. Try refreshing the Archipelago Page and try again.")
        print("An error occurred:", e)

async def check_connection_status():
    """Continuously check if the WebSocket is still connected."""

    while True:
        # If connection is still active
        if global_connection_status:
            print("Status: Connected to server.")  # Debugging
            message_emitter.connection_signal.emit(True)  # Emit connected status
        else:
            print("Status: Not Connected to the server.")  # Debugging
            message_emitter.connection_signal.emit(False)  # Emit disconnected status
        await asyncio.sleep(1)  # Check every second

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
    global global_connection_status
    try:
        while True:
            response = await websocket.recv()
            await log_to_file(response)
            parse_server_response(response)

    except websockets.exceptions.ConnectionClosed as e:
        global_connection_status = False  # Mark as disconnected
        message_emitter.connection_signal.emit(False)  # Emit disconnection status
        print(f"Connection closed: {e}")



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
    items = extract_items_from_json(requirements_goals_file_path)

    # Retrieve names for each received item based on item code
    for item in received_items:
        item_id = item.get("item")
        item_name = get_item_name(item_id)
        
        if item_name:
            if (item_name in items) or (item_name == "Progressive Mine Elevator") or (item_name == "Combat Level")  or (item_name == "Farming Level") or (item_name == "Fishing Level") or (item_name == "Foraging Level") or (item_name == "Mining Level"):
                item_names.append(item_name)
                print(f"Found item: {item_name} (ID: {item_id})")  # Log successful lookup

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
        
        else:
            print(f"Warning: Item ID {item_id} not found in item table.")  # Log missing item



def handle_print_json(entry):
    """Process 'PrintJSON' command to interpret and display text fields."""
    item_referenced_player = "null"
    players = load_player_data()  # Load players from JSON file

    try:
        with open(checked_location_path, 'r') as location_file:
            checked_locations_data = json.load(location_file)
    except (FileNotFoundError, json.JSONDecodeError):
        checked_locations_data = {"checked_locations": []}

    if "data" in entry and isinstance(entry["data"], list):
        # Check for "[Hint]: " at the start of the first text field
        is_hint_message = entry["data"][0].get("text", "").startswith("[Hint]: ")

        #The will build the message
        message_parts = []
        my_location = True
        my_item = True
        flag_detail = "null"

        for item in entry["data"]:
            # Process text field and additional information if present
            text = item.get("text", "")
            flag = item.get("flags", "")
            color = item.get("color", "")
            # color returns red (not found) or green (found)
            type = item.get("type")

            if color == "green":
                found = "found"
            else:
                found = "not found"

            if flag == 0:
                flag_detail = "filler"
            elif flag == 2:
                flag_detail = "useful"
            elif flag == 1:
                flag_detail = "progressive"

            if type == "player_id":
                player_name = get_player_name_by_slot(int(text), players)
                text = player_name if player_name else "Unknown Player"

            #{"text":"16777216","player":1,"flags":2,"type":"item_id"}
            elif type == "item_id":
                #Using the item id given to find the item associated with that id
                item_name = get_item_name(int(text))
                text = item_name
                item_referenced_player = get_player_name_by_slot(item.get("player", ""), players)

                #If the player name matches the player name of the client, then assume this is my item
                print(f"Item Check: Does {item_referenced_player} = {global_player_name}")
                if item_referenced_player == global_player_name:
                    my_item = True
                else:
                    my_item = False

            #{"text":"717001","player":1,"type":"location_id"}        
            elif type == "location_id":
                #Using the location id given to find the location associated with that id
                location_name = get_location_name(int(text))
                text = location_name
                location_referenced_player = get_player_name_by_slot(item.get("player", ""), players)

                #If this is a location name then add that location as a checked location in the json file to track it.
                if location_name:
                    # Only update checked_location.json if it's not a hint message
                    if not is_hint_message and location_name not in checked_locations_data["checked_locations"]:
                        checked_locations_data["checked_locations"].append(location_name)
                        # Save the updated list back to the file
                        with open(checked_location_path, 'w') as location_file:
                            json.dump(checked_locations_data, location_file, indent=4)

                #If the player name matches the player name of the client, then assume this is my location
                print(f"Location Check: Does {location_referenced_player} = {global_player_name}")
                if location_referenced_player == global_player_name:
                    my_location = True
                else:
                    my_location = False

            # Add interpreted text to message parts
            message_parts.append(text)

        if is_hint_message:
            if my_location:
                player_clean = re.sub(r"\{['\"]|['\"]\}", "", str(item_referenced_player))
                itemname_clean = re.sub(r"\{['\"]|['\"]\}", "", str(item_name))
                location_clean = re.sub(r"\{['\"]|['\"]\}", "", str(location_name))

                itemname_clean = f"{player_clean}'s {itemname_clean}"
                process_hint(player_clean, itemname_clean, location_clean, flag_detail, found, hint_my_location_file_path)
            else:
                if my_item:
                    player_clean = re.sub(r"\{['\"]|['\"]\}", "", str(location_referenced_player))
                    itemname_clean = re.sub(r"\{['\"]|['\"]\}", "", str(item_name))
                    location_clean = re.sub(r"\{['\"]|['\"]\}", "", str(location_name))

                    location_clean = f"{player_clean}'s {location_clean}"
                    process_hint(player_clean, itemname_clean, location_clean, flag_detail, found, hint_my_item_file_path)
        else:
            if my_location or my_item:
                if not flag == 0:
                    full_message = "".join(message_parts)
                    print_to_server_console(full_message)

# Lock for thread-safe file operations
file_lock = threading.Lock()

def get_tab(location_clean, data_path):
    try:
        with open(data_path, "r") as file:
            data = json.load(file)
            for header, entries in data.items():
                for entry in entries:
                    # Check if entry is a list and location_clean matches the 4th element
                    if isinstance(entry, list) and len(entry) > 3 and location_clean == entry[3]:
                        return header
        print(f"Location '{location_clean}' not found in {data_path}.")
        return None
    except Exception as e:
        print(f"An error occurred while reading {data_path}: {e}")
        return None


def process_hint(player_clean, itemname_clean, location_clean, flag_detail, found, filepath):
    try:
        tab = get_tab(location_clean, data_path)  # Get the tab based on location_clean

        if tab is None:
            print(f"Tab could not be determined for location: {location_clean}. Defaulting to 'Unknown'.")
            tab = "Unknown"

        with file_lock:
            # Load the JSON data from the file
            if os.path.exists(filepath):
                with open(filepath, "r") as file:
                    try:
                        notes = json.load(file)
                    except json.JSONDecodeError:
                        print(f"Error decoding JSON from file: {filepath}. Reinitializing.")
                        notes = []
            else:
                notes = []

            # Ensure notes is a list
            if not isinstance(notes, list):
                print(f"Unexpected JSON structure in {filepath}. Reinitializing.")
                notes = []

            # Find the matching entry by 'checkbox_text'
            match_found = False
            for entry in notes:
                if entry["checkbox_text"] == location_clean:
                    # Update the 'hint_input' for the matching entry
                    entry["hint_input"] = itemname_clean
                    entry["class"] = flag_detail
                    entry["state"] = found
                    entry["tab"] = tab
                    match_found = True
                    print(f"Updated hint for location '{location_clean}' to: {entry['hint_input']}")
                    break

            # If no match is found, add a new entry
            if not match_found:
                new_entry = {
                    "checkbox_text": location_clean,
                    "hint_input": itemname_clean,
                    "class": flag_detail,
                    "state": found,
                    "tab": tab
                }
                notes.append(new_entry)
                print(f"Added new entry: {new_entry}")

            # Write updates to a temporary file first
            temp_path = filepath + ".tmp"
            with open(temp_path, "w") as temp_file:
                json.dump(notes, temp_file, indent=4)

            # Replace the original file with the temp file
            os.replace(temp_path, filepath)

    except Exception as e:
        print(f"An error occurred: {e}")

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

    # Load existing checked_locations.json
    try:
        with open(checked_location_path, 'r') as checked_file:
            checked_locations_data = json.load(checked_file)
    except (FileNotFoundError, json.JSONDecodeError):
        checked_locations_data = {"checked_locations": []}

    # Match checked locations by code and update checked_locations.json
    for loc_code in game_checked_locations:
        matched_location = location_names.get(loc_code)
        if matched_location and matched_location not in checked_locations_data["checked_locations"]:
            checked_locations_data["checked_locations"].append(matched_location)

    # Save updated checked_locations.json
    with open(checked_location_path, 'w') as checked_file:
        json.dump(checked_locations_data, checked_file, indent=4)
        print("Updated checked_locations.json")

    # Combine all valid locations (checked and missing) for all_locations.json
    all_locations = set(checked_locations_data["checked_locations"])  # Start with checked locations

    for loc_code in game_checked_locations + missing_locations:
        matched_location = location_names.get(loc_code)
        if matched_location:
            all_locations.add(matched_location)

    # Save combined all_locations.json
    all_locations_data = {
        "all_locations": sorted(all_locations),  # Sort alphabetically
        "missing_locations": missing_locations   # Include missing locations if needed
    }

    with open(all_locations_path, 'w') as all_locations_file:
        json.dump(all_locations_data, all_locations_file, indent=4)
        print("Updated all_locations.json")

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
    respect_excluded(data)

    # Write the updated data.json safely
    try:
        with open(data_path, 'w') as data_file:
            json.dump(data, data_file, indent=4)
    except Exception as e:
        print(f"Error occurred while saving data.json: {e}")
        return
    

    print("Updated data.json successfully.")

def respect_excluded(data):
    print("Starting respect_excluded function...")

    # Log current working directory
    print(f"Current working directory: {os.getcwd()}")

    # Locate the first YAML file in ../Settings
    yaml_path = glob("../Settings/*.yaml")
    print(f"Searching for YAML files in: {os.path.abspath('../Settings')}")

    if not yaml_path:
        print("Error: No YAML file found in ../Settings.")
        return

    yaml_path = yaml_path[0]  # Use the first YAML file found
    print(f"Using YAML file: {yaml_path}")

    try:
        with open(yaml_path, 'r') as yaml_file:
            yaml_data = yaml.safe_load(yaml_file)
            print(f"YAML data loaded successfully: {yaml_data.keys()}")

            # Navigate to the nested 'Stardew Valley' section
            stardew_valley_data = yaml_data.get("Stardew Valley", {})
            print(f"'Stardew Valley' section loaded: {stardew_valley_data.keys()}")

            # Extract the exclude_locations list
            excluded_locations = stardew_valley_data.get("exclude_locations", [])
            print(f"Excluded locations extracted: {excluded_locations}")
    except FileNotFoundError:
        print(f"Error: File {yaml_path} not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error reading YAML file {yaml_path}: {e}")
        return

    if not excluded_locations:
        print("Warning: No excluded locations found in the YAML file.")
        return

    # Process excluded locations
    print("Processing excluded locations...")
    for section, entries in data.items():
        print(f"Checking section: {section} with {len(entries)} entries.")
        for entry in entries:
            location_name = entry[3]  # The 4th field is the location name
            if location_name.strip("'") in excluded_locations:
                print(f"Match found: {location_name} in section {section}. Updating entry.")
                entry[4] = 1  # Update the 5th field
            else:
                print(f"No match for: {location_name} in excluded locations.")

    print("Completed processing excluded locations.")


def print_to_server_console(text):
    """Emit the parsed text to the server console output in Tracker.py."""
    # Emit the text to the connected GUI console in Tracker.py
    message_emitter.message_signal.emit(text)

def get_server_address_suffix():
    """Retrieve the server address from config.json and extract the last 5 characters."""
    try:
        with open("../JSONStore/config.json", "r") as config_file:
            config = json.load(config_file)
            server_address = config.get("server_address", "")
            return server_address[-5:]
    except (FileNotFoundError, json.JSONDecodeError):
        print("Error: Unable to read server address from config.json.")
        return "error"

async def log_to_file(message):
    """Append a message to the log file with a unique filename based on the server address."""
    address_suffix = get_server_address_suffix()
    log_file_path = f"../Logs/serverlog_{address_suffix}.txt"

    with open(log_file_path, "a") as log_file:
        log_file.write(message + "\n")


async def send_initial_connect(websocket, player_name):
    """Send the initial Connect packet to the server."""
    global global_player_name  # Declare that we are using the global variable
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

    global_player_name = player_name
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
