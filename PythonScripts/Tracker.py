import sys
import json
import re
import os
import socket
import threading
import time
from PyQt5 import QtCore
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
from PyQt5.QtWidgets import QTabBar
from PyQt5.QtWidgets import (
    QApplication, QSizeGrip, QSizePolicy, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLineEdit, QLabel, QScrollArea, QGroupBox, QPushButton, QListWidget,
    QSpinBox, QComboBox, QGridLayout, QTextEdit, QListWidgetItem,QToolTip, 
)
from PyQt5.QtCore import QFileSystemWatcher, Qt, QObject, QTimer, QThread, pyqtSignal, QEvent, QPoint
import PyQt5.QtCore
PyQt5.QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
PyQt5.QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

# Define a mapping from tab display names to data keys
tab_name_mapping = {
    "Bundles": "Bundles",
    "Crops": "Cropsanity",
    "Fish": "Fishsanity",
    "Monsters": "Monstersanity",
    "Quests": "Questsanity",
    "Travelling Cart": "Cartsanity",
    "Books": "Booksanity",
    "Library": "Librarysanity",
    "Robin's Shop": "Blueprintsanity",
    "Clint's Shop": "Upgradesanity",
    "Gus' Shop": "Chefsanity",
    "Raccoons": "Raccoonsanity", 
    "Festivals": "Festivalsanity", 
    "Misc": "Misc"
}

tab_display_names = {
    "Bundles": "Bundles", 
    "Cropsanity": "Crops", 
    "Fishsanity": "Fish",
    "Questsanity": "Quests", 
    "Cartsanity": "Travelling Cart",
    "Booksanity": "Books",
    "Librarysanity": "Library",
    "Monstersanity": "Monsters",
    "Blueprintsanity": "Robin's Shop",
    "Upgradesanity": "Clint's Shop", 
    "Chefsanity": "Gus' Shop", 
    "Raccoonsanity": "Raccoons", 
    "Festivalsanity": "Festivals", 
    "Misc": "Misc"
}

data_file_path = "../JSONStore/data.json"
config_file_path = "../JSONStore/config.json"
notes_file_path = "../JSONStore/notes.json"
checked_location_file_path = "../JSONStore/checked_location.json"
current_items_file_path = "../JSONStore/current_items.json"
requirements_file_path = "../JSONPull/requirements.json"
requirements_group_file_path = "../JSONPull/requirements_group.json"
hint_my_location_file_path = "../JSONStore/hint_my_location.json"
hint_my_item_file_path = "../JSONStore/hint_my_item.json"
extra_info_file_path = "../JSONStore/extra_info.json"


dark_theme = """
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
        font-family: Consolas, monospace;
        font-size: 8pt;
    }

    QLineEdit, QTextEdit, QComboBox, QSpinBox, QCheckBox, QPushButton {
        background-color: #3c3f41;
        color: #ffffff;
        border: 1px solid #555555;
        padding: 2px;
        border-radius: 4px;
    }

    QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QCheckBox:disabled, QPushButton:disabled {
        background-color: #2a2a2a;  /* Darker background for disabled state */
        color: #555555;             /* Darker text color for disabled elements */
        border: 1px solid #444444;
    }

    QLineEdit:hover, QTextEdit:hover, QComboBox:hover, QSpinBox:hover, QPushButton:hover, QCheckBox:hover {
        background-color: #4c4f51;
    }

    QPushButton {
        background-color: #4c5052;
        color: #ffffff;
        font-weight: bold;
    }

    QPushButton:pressed {
        background-color: #5a5e60;
    }

    QTabWidget::pane {
        background-color: #3c3f41;
        border: 1px solid #555555;
    }

    QTabBar::tab {
        background-color: #3c3f41;
        color: #ffffff;
        font-size: 8pt;
        padding: 2px;
        border: 1px solid #555555;
        border-bottom: none;
        text-align: center; /* Center the text */
    }

    QTabBar::tab:selected {
        background-color: #4c4f51;
        font-weight: bold;
    }

    QTabBar QLabel {
        background-color: transparent; /* Make QLabel transparent to inherit tab color */
        color: #ffffff; /* Ensure text color matches tab color */
        font-size: 1pt;
        padding: 0px; /* Adjust padding for alignment */
        text-align: center; /* Center the text */
        white-space: pre-wrap; /* Allow multi-line text */
    }

    QLabel {
        color: #ffffff;
    }

    QScrollArea {
        border: none;
    }

    QScrollBar:vertical {
        background-color: #0f0f0f;
        width: 8px;
        margin: 22px 0 22px 0;
    }

    QScrollBar::handle:vertical {
        background-color: #cca1ff;  /* White scroll handle */
        min-height: 20px;
        border-radius: 4px;
    }

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        background-color: #0f0f0f;
        background: none;
    }

    QScrollBar::horizontal {
        background-color: #0f0f0f;
        height: 8px;
        margin: 0 22px 0 22px;
    }

    QScrollBar::handle:horizontal {
        background-color: #cca1ff;  /* White scroll handle */
        min-width: 20px;
        border-radius: 4px;
    }

    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
        background-color: #0f0f0f;
        background: none;
    }

    QGroupBox {
        border: 1px solid #555555;
        border-radius: 4px;
        margin-top: 10px;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 5px;
        color: #ffffff;
    }
"""

def update_tab_background(self, tab_widget, tab_index):
    """Set tab background to black if all checkboxes are checked, otherwise reset to default."""
    tab = tab_widget.widget(tab_index)
    checkboxes = tab.findChildren(QCheckBox)
    all_checked = all(checkbox.isChecked() for checkbox in checkboxes)

    # Set background color based on whether all checkboxes are checked
    if all_checked:
        tab_widget.tabBar().setTabBackgroundColor(tab_index, QColor("black"))
    else:
        tab_widget.tabBar().setTabBackgroundColor(tab_index, QColor("#3c3f41"))  # Default dark gray

season_state = "a"

# Define season colors
season_colors = {
    "Spring": "background-color: #344534;",  # Green
    "Summer": "background-color: #4f4300;",  # Yellow
    "Fall": "background-color: #633700;",    # Orange
    "Winter": "background-color: #0a3054;"   # Blue
}

# Load data from an external JSON file
def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Save data to an external JSON file
def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_config(file_path):
    """Load configuration data from a JSON file."""
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    return {}  # Return an empty dictionary if the file doesn't exist or is invalid

def save_config(file_path, config_data):
    """Save configuration data to a JSON file."""
    with open(file_path, "w") as file:
        json.dump(config_data, file, indent=4)

def get_requirements_text(item_name, item_widgets):
    # Fetch requirements and current items
    requirements_data = load_data(requirements_file_path)
    current_items_data = load_data(current_items_file_path)
    checked_items = current_items_data.get("current_items", [])
    
    # Retrieve requirements for the specific item
    required_items = []
    for category, items in requirements_data.items():
        for item in items:
            if item[0] == item_name:
                required_items = item[1]
                break

    if required_items and "or_items" in required_items[0]:
        # If the first item contains "or_items", handle it as an or_items requirement
        return get_standard_requirements_text(required_items, checked_items)
    elif required_items and "item" in required_items[0]:
        # If the first item contains "item", it's a standard requirement
        return get_standard_requirements_text(required_items, checked_items)
    elif required_items and any(key.startswith("complete_") for key in required_items[0]):
        # If it starts with "complete_X_out_of_Y", it's a completion requirement
        return get_complete_requirements_text(required_items, checked_items, item_widgets)
    else:
        # Handle unexpected formats gracefully
        return f"No Required Items"

def get_standard_requirements_text(conditions, checked_items):
    """
    Generate tooltip text for standard requirements with detailed item needs,
    handling both 'or_items' and nested 'and_items' logic.
    """
    tooltip_text = "Required Items:\n"
    unmet_requirements = []
    relevant_items = set()  # Use a set to avoid duplicates

    for condition in conditions:
        if "item" in condition:
            # Handle individual item requirements
            item_name = condition["item"]
            required_count = condition.get("count", 1)
            item_count = checked_items.count(item_name)

            if item_count >= required_count:
                relevant_items.add(f"{required_count}x {item_name}")
            else:
                unmet_requirements.append(f"{required_count}x {item_name}")

        elif "or_items" in condition:
            # Handle "or_items" block
            or_items_text_list = []
            condition_met = False

            for or_item in condition["or_items"]:
                if "item" in or_item:
                    # Handle single item within or_items
                    item_name = or_item["item"]
                    required_count = or_item.get("count", 1)
                    item_count = checked_items.count(item_name)

                    if item_count >= required_count:
                        condition_met = True
                        relevant_items.add(f"{required_count}x {item_name}")

                    or_items_text_list.append(f"{required_count}x {item_name}")

                elif "and_items" in or_item:
                    # Handle "and_items" within "or_items"
                    and_items_text_list = []
                    and_condition_met = True

                    for and_item in or_item["and_items"]:
                        item_name = and_item["item"]
                        required_count = and_item.get("count", 1)
                        item_count = checked_items.count(item_name)

                        # Add to relevant items even if not all are met
                        if item_count > 0:
                            relevant_items.add(f"{item_count}x {item_name}")
                        if item_count < required_count:
                            and_condition_met = False
                            and_items_text_list.append(f"{required_count}x {item_name}")
                        else:
                            # Fully satisfied items are not included in unmet requirements
                            relevant_items.add(f"{required_count}x {item_name}")

                    if and_items_text_list:
                        or_items_text_list.append(" AND ".join(and_items_text_list))

                    if and_condition_met:
                        condition_met = True

            # If no condition is met, show unmet requirements
            if not condition_met:
                unmet_requirements.append(f"One of: ({', '.join(or_items_text_list)})")

    # Remove items from unmet_requirements if they are fully satisfied
    relevant_item_names = {item.split("x ", 1)[1] for item in relevant_items}
    unmet_requirements = [
        req for req in unmet_requirements if all(
            part.strip() not in relevant_item_names for part in req.split(" AND ")
        )
    ]

    # Format the unmet requirements section
    if unmet_requirements:
        tooltip_text += "\n".join(unmet_requirements)
    else:
        tooltip_text += "All requirements met."

    # Display relevant items the user currently has
    tooltip_text += f"\n\nCurrent Relevant Items:\n{', '.join(sorted(relevant_items)) if relevant_items else 'None'}"

    return tooltip_text


def get_complete_requirements_text(conditions, checked_items, item_widgets):
    """
    Generate tooltip text for complete_X_out_of_Y requirements.
    """
    # Print each widget's text_input content for debugging
    for widget in item_widgets:
        text_content = widget['text_input'].text()
    tooltip_text = ""
    goal_count = 0  # Initialize goal_count outside the sub-conditions loop to accumulate across searches

    for condition in conditions:
        complete_key = next((key for key in condition if key.startswith("complete_")), None)
        if complete_key:
            x, y = map(int, re.findall(r"\d+", complete_key))
            sub_conditions = condition[complete_key]
            met_conditions = []
            unmet_conditions = []

            # Classify each sub-condition as met or unmet
            for sub_condition in sub_conditions:
                name = sub_condition.get("name", [{"goal": "Item"}])[0].get("goal", "Item")

                # Search item_widgets for occurrences of the goal
                goal_matches = [
                    widget for widget in item_widgets if name in widget['text_input'].text()
                ]
                goal_addition = len(goal_matches)
                if goal_addition > 1:
                    goal_addition = 1
                goal_count += goal_addition  # Accumulate matches across goals


                # Skip this goal if no matches were found in item_widgets
                if not goal_matches:
                    continue

                # Check for more matches than unmet_conditions
                if goal_count > y:
                    return f"Please edit the requirements field to only have {y} amount of items in it."

                # Check for always_items requirements
                if "always_items" in sub_condition:
                    always_items_text = ", ".join(
                        f"{always_item.get('count', 1)}x {always_item['item']}"
                        for always_item in sub_condition["always_items"]
                    )
                    always_items_met = all(
                        checked_items.count(always_item['item']) >= always_item.get('count', 1)
                        for always_item in sub_condition["always_items"]
                    )
                else:
                    always_items_text = ""
                    always_items_met = True  # If no always_items, treat as met

                # Check for or_items requirements
                if "or_items" in sub_condition:
                    or_items_text_list = []
                    or_condition_met = False

                    for or_item in sub_condition["or_items"]:
                        if "item" in or_item:
                            or_item_text = f"{or_item.get('count', 1)}x {or_item['item']}"
                            if checked_items.count(or_item['item']) >= or_item.get('count', 1):
                                or_condition_met = True
                            or_items_text_list.append(or_item_text)

                        elif "and_items" in or_item:
                            and_items_text_list = []
                            and_condition_met = True

                            for and_item in or_item["and_items"]:
                                and_item_text = f"{and_item.get('count', 1)}x {and_item['item']}"
                                if checked_items.count(and_item['item']) < and_item.get('count', 1):
                                    and_condition_met = False
                                and_items_text_list.append(and_item_text)

                            or_items_text_list.append(" and ".join(and_items_text_list))
                            if and_condition_met:
                                or_condition_met = True

                    # Format the or_items_text to be displayed with commas
                    or_items_text = f"({', '.join(or_items_text_list)})"
                    text = f"[{name}] {always_items_text} and One of: {or_items_text}" if always_items_text else f"[{name}] One of: {or_items_text}"
                    
                    # Determine if this condition is met or unmet based on always_items and or_items
                    if always_items_met and or_condition_met:
                        met_conditions.append(f"- {text}")
                    else:
                        unmet_conditions.append(f"- {text}")
                else:
                    # No or_items, so check always_items alone
                    if always_items_met:
                        met_conditions.append(f"- [{name}] {always_items_text}")
                    else:
                        unmet_conditions.append(f"- [{name}] {always_items_text}")

            # Format unmet and met conditions sections
            unmet_needed = max(0, x - len(met_conditions))
            tooltip_text += f"Complete {unmet_needed} more of the following:\n" + "\n".join(unmet_conditions)

            # Display the met conditions
            tooltip_text += f"\n\nCompleted {len(met_conditions)} out of {x} so far:\n" + "\n".join(met_conditions)
    
    return tooltip_text


def has_requirements(item_id, text_input):
    """
    Check if the given item ID meets the requirements specified in requirements.json.
    List missing requirements if the item is not in logic.
    """
    # Load requirements data and current items
    requirements_data = load_data(requirements_file_path)
    current_items_data = load_data(current_items_file_path)
    checked_items = current_items_data.get("current_items", [])

    # Initialize a list to keep track of missing requirements
    missing_requirements = []

    # Search for the item by ID in each category
    for category, items in requirements_data.items():
        for item in items:
            if item[0] == item_id:
                # Retrieve conditions from the second element in the item
                conditions = item[1]
                
                # Check the conditions and collect missing items
                missing_requirements = get_missing_requirements(conditions, checked_items, text_input)

                if missing_requirements == "Pink":
                    return "Pink"
                
                if not missing_requirements:
                    return "Default"  # All requirements met
                else:
                    return "Red"  # Missing requirements

    return False  # No requirements found for the item

def get_missing_requirements(conditions, checked_items, text_input):
    # Get and print the goal requirements
    goals = get_goal_requirements(conditions)
    goals_amount = 0  # Only matched goals will be counted towards this

    for goal, items in goals.items():
        
        # Check if the goal is in text_input and print the location if found
        goal_match = re.search(goal, text_input, re.IGNORECASE)
        if goal_match:
            goals_amount += 1  # Count only matched goals
        else:
            continue  # Skip unmet goals entirely in count

        # Print each item's requirements for achieving this goal
        for item in items:
            if isinstance(item, list):
                and_items = " and ".join([f"{count}x {name}" for name, count in item])
            else:
                name, count = item

    missing = []
    for condition in conditions:
        if isinstance(condition, dict) and condition:  # Only proceed if it's a dictionary and not empty
            # Handle "complete_X_out_of_Y" conditions
            complete_key = next((key for key in condition if key.startswith("complete_")), None)
            if complete_key:
                x, y = map(int, re.findall(r"\d+", complete_key))  # Extract X and Y from "complete_X_out_of_Y"
                if goals_amount > y:
                    return "Pink"
                sub_conditions = condition[complete_key]
                
                # Filter sub_conditions to include only those whose goals matched in text_input
                matched_sub_conditions = [
                    sub_condition for sub_condition in sub_conditions
                    if any(goal["goal"] == sub_condition.get("name")[0]["goal"] and re.search(goal["goal"], text_input, re.IGNORECASE)
                           for goal in sub_condition.get("name", []))
                ]

                # Count only matched sub-conditions
                met_count = sum(
                    check_conditions([sub_condition], checked_items, text_input) for sub_condition in matched_sub_conditions
                )
                
                # Only add to missing if met_count falls short of requirement x
                if met_count < x:
                    missing.append(f"Complete {x - met_count} more out of {y} total requirements")
                continue  # Skip to the next condition after processing this complete_X_out_of_Y

            # Handle "always_items" conditions
            if "always_items" in condition:
                for always_item in condition["always_items"]:
                    required_item = always_item["item"]
                    required_count = always_item.get("count", 1)
                    item_count = checked_items.count(required_item)
                    if item_count < required_count:
                        missing.append(f"{required_count - item_count}x {required_item} (mandatory)")

            # Handle individual item conditions
            if "item" in condition:
                required_item = condition["item"]
                required_count = condition.get("count", 1)
                item_count = checked_items.count(required_item)
                if item_count < required_count:
                    missing.append(f"{required_count - item_count}x {required_item}")

            # Handle "or_items" conditions
            elif "or_items" in condition:
                if not any(check_conditions([or_item], checked_items, text_input) for or_item in condition["or_items"]):
                    or_missing = []
                    for or_item in condition["or_items"]:
                        if "item" in or_item:
                            or_missing.append(f"{or_item.get('count', 1)}x {or_item['item']}")
                        elif "and_items" in or_item:
                            and_missing = [
                                f"{and_item.get('count', 1)}x {and_item['item']}"
                                for and_item in or_item["and_items"]
                            ]
                            or_missing.append(" and ".join(and_missing))
                    missing.append(f"One of: ({' or '.join(or_missing)})")
    return missing



def check_conditions(conditions, checked_items, text_input):
    for condition in conditions:
        if isinstance(condition, dict) and condition:  # Only proceed if it's a dictionary and not empty
            # Handle "complete_X_out_of_Y" conditions
            complete_key = next((key for key in condition if key.startswith("complete_")), None)
            if complete_key:
                x, y = map(int, re.findall(r"\d+", complete_key))  # Extract X and Y from "complete_X_out_of_Y"
                sub_conditions = condition[complete_key]
                met_count = sum(
                    check_conditions([sub_condition], checked_items, text_input) for sub_condition in sub_conditions
                )
                if met_count >= x:
                    return True  # Met enough sub-conditions
                return False  # Did not meet the required number of sub-conditions

            # Handle "always_items" conditions
            if "always_items" in condition:
                for always_item in condition["always_items"]:
                    required_item = always_item["item"]
                    required_count = always_item.get("count", 1)
                    if checked_items.count(required_item) < required_count:
                        return False  # Mandatory item not met

            # Handle individual item conditions
            if "item" in condition:
                if checked_items.count(condition["item"]) < condition.get("count", 1):
                    return False

            # Handle "or_items" conditions
            elif "or_items" in condition:
                if not any(check_conditions([or_item], checked_items, text_input) for or_item in condition["or_items"]):
                    return False

            # Handle "and_items" conditions
            elif "and_items" in condition:
                if not all(
                    checked_items.count(and_item["item"]) >= and_item.get("count", 1)
                    for and_item in condition["and_items"]
                ):
                    return False

    return True

def get_goal_requirements(conditions):
    """Retrieve goal requirements and their corresponding items for each goal."""
    goals = {}

    for condition in conditions:
        if isinstance(condition, dict) and condition:
            # Handle "complete_X_out_of_Y" conditions
            complete_key = next((key for key in condition if key.startswith("complete_")), None)
            if complete_key:
                sub_conditions = condition[complete_key]
                # Recursively process sub-conditions for goals
                sub_goals = get_goal_requirements(sub_conditions)
                goals.update(sub_goals)  # Merge sub-goals with the main goals
                continue

            # Detect "goal" in conditions with corresponding items
            if "name" in condition:
                for goal_info in condition["name"]:
                    goal_name = goal_info.get("goal")
                    if goal_name:
                        goals[goal_name] = []  # Initialize the goal with an empty list of items

                        # Collect items that satisfy the goal
                        if "or_items" in condition:
                            for or_item in condition["or_items"]:
                                if "item" in or_item:
                                    item_name = or_item["item"]
                                    item_count = or_item.get("count", 1)
                                    goals[goal_name].append((item_name, item_count))
                                elif "and_items" in or_item:
                                    and_items = [(and_item["item"], and_item.get("count", 1))
                                                 for and_item in or_item["and_items"]]
                                    goals[goal_name].append(and_items)  # Grouped items for "and_items"

    return goals

# Load the data from the JSON file
data_file = data_file_path
all_major_data = load_data(data_file_path)

# Load config data from config.json
config_file = config_file_path
with open(config_file, 'r') as f:
    config_data = json.load(f)

from server_connection import connect_to_server, message_emitter, send_message_to_server  # Import from server_connection.py
import asyncio
from PyQt5 import QtGui

class ServerThread(QThread):
    def __init__(self, server_address, player_slot):
        super().__init__()
        self.server_address = server_address
        self.player_slot = player_slot

    async def async_connect(self):
        await connect_to_server(self.server_address, self.player_slot)

    def run(self):
        asyncio.run(self.async_connect())

class ServerWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Server Connection")
        self.pending_server_file_actions = set()  # Store the file to act upon after debounce
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)  # Ensure it only triggers once after timeout
        self.debounce_timer.timeout.connect(self.run_file_change_actions)
        self.setGeometry(400, 200, 600, 750)  # Adjusted width for two-column layout

        # Load config data from config.json
        self.config_data = self.load_config_data()

        # Layout for server connection controls (left side)
        left_layout = QVBoxLayout()

        # Server Address input field
        server_label = QLabel("Server Address")
        left_layout.addWidget(server_label)
        self.server_input = QLineEdit()
        self.server_input.setText(self.config_data.get("server_address", ""))
        left_layout.addWidget(self.server_input)

        # Slot Name input field
        slot_label = QLabel("Slot Name")
        left_layout.addWidget(slot_label)
        self.slot_input = QLineEdit()
        self.slot_input.setText(self.config_data.get("slot_name", ""))
        left_layout.addWidget(self.slot_input)

        # Connect Button
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.start_server_connection)
        left_layout.addWidget(self.connect_button)

        # Output display for server messages
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        left_layout.addWidget(self.output_display)
        self.add_initial_padding()  # Add padding after initializing output_display

        # Message input field and send button
        send_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Enter message to send...")
        self.message_input.returnPressed.connect(lambda: asyncio.run(self.send_message()))  # Send on Enter key
        send_layout.addWidget(self.message_input)
        self.send_button = QPushButton("Send")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(lambda: asyncio.run(self.send_message()))
        send_layout.addWidget(self.send_button)
        left_layout.addLayout(send_layout)

        # Tabs layout for hints and notes (right side)
        right_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()

        # Create tabs
        self.locations_tab = QTextEdit()
        self.items_tab = QTextEdit()
        self.notes_tab = QTextEdit()

        self.items_tab.setReadOnly(True)
        self.locations_tab.setReadOnly(True)

        # Add tabs to the widget
        self.tab_widget.addTab(self.items_tab, "My Locations")
        self.tab_widget.addTab(self.locations_tab, "Other's Locations")
        self.tab_widget.addTab(self.notes_tab, "Notes")
        right_layout.addWidget(self.tab_widget)

        notes_tab_text = self.load_notes()
        self.notes_tab.setPlainText(notes_tab_text)

        # Button to send info
        self.send_info_button = QPushButton("Send info")
        self.send_info_button.clicked.connect(lambda: asyncio.run(self.send_info()))
        right_layout.addWidget(self.send_info_button)

        # Main layout combining left and right layouts
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        self.populate_tabs_from_json()
        
        # QFileSystemWatcher to monitor specific files
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.addPath(hint_my_location_file_path)
        self.file_watcher.addPath(hint_my_item_file_path)

        # Connect the `fileChanged` signals for specific files
        self.file_watcher.fileChanged.connect(self.handle_file_change)

        # Connect message signal from server_connection.py to the output display
        message_emitter.message_signal.connect(self.print_to_server_console)

        # Enable Send button only if there’s text in message_input
        self.message_input.textChanged.connect(self.toggle_send_button)

    def handle_file_change(self, changed_file):
        """
        Handle changes to watched files with a global QTimer debounce mechanism.
        """
        # Add the changed file to the pending actions set
        self.pending_server_file_actions.add(changed_file)

        if self.debounce_timer.isActive():
            remaining_time = self.debounce_timer.remainingTime()
            print(f"Timer reset. Remaining time was: {remaining_time} ms")
        else:
            print("Starting new debounce timer.")

        # Restart the timer
        self.debounce_timer.start(1000)

    def run_file_change_actions(self):
        """
        Execute actions for all pending files after debounce delay.
        """
        print(f"Running actions for files: {self.pending_server_file_actions}")
        for changed_file in self.pending_server_file_actions:
            if changed_file == hint_my_location_file_path:
                self.populate_tabs_from_json()
                print("location change")

            elif changed_file == hint_my_item_file_path:
                self.populate_tabs_from_json()
                print("item change")

        # Clear pending actions after execution
        self.pending_server_file_actions.clear()

    def populate_tabs_from_json(self):
        """Populate 'My Locations' and 'Other's Locations' tabs with data from JSON files."""
        try:
            # Load data from the JSON files
            with open(hint_my_location_file_path, 'r') as f:
                my_location_data = json.load(f)
            with open(hint_my_item_file_path, 'r') as f:
                my_item_data = json.load(f)

            # Allowed tabs
            allowed_tabs = {"Unknown", "Elevatorsanity", "Skillsanity", "Friendsanity"}

            # Helper function to process the data
            def process_data(data):
                entries = []
                for entry in data:
                    state = entry.get("state", "")
                    entry_class = entry.get("class", "")
                    tab = entry.get("tab", "Unknown")
                    if state.lower() == "found" or entry_class.lower() == "filler" or tab not in allowed_tabs:
                        continue  # Skip if state is "found", class is "filler", or tab is not allowed
                    checkbox_text = entry.get("checkbox_text", "Unknown Location")
                    hint_input = entry.get("hint_input", "Unknown Item")
                    entries.append({
                        "text": f"{hint_input} ({entry_class})\n is at \n({checkbox_text})\n",
                        "class": entry_class.lower()
                    })

                # Sort entries: progressive first
                return sorted(entries, key=lambda x: 0 if x["class"] == "progressive" else 1)
        # Apply formatted text to the tab
            def apply_text_format(tab, entries):
                tab.clear()
                cursor = tab.textCursor()
                for entry in entries:
                    fmt = QTextCharFormat()
                    fmt.setForeground(QColor("#000000"))  # Set text color to black

                    if entry["class"] == "useful":
                        fmt.setBackground(QColor("#e8f29b"))  # Yellow background for "useful"
                    elif entry["class"] == "progressive":
                        fmt.setBackground(QColor("#9bf2bf"))  # Green background for "progressive"
                    else:
                        fmt.setBackground(QColor("#cca1ff"))  # Green background for "progressive"

                    cursor.insertText(entry["text"], fmt)
                    cursor.insertBlock()

            # Process the data for each tab
            my_locations_entries = process_data(my_location_data)
            others_locations_entries = process_data(my_item_data)

            # Populate the tabs with formatted text
            apply_text_format(self.locations_tab, others_locations_entries)
            apply_text_format(self.items_tab, my_locations_entries)

        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

    async def send_info(self):
        """Send the content of the selected tab to the server using the 'say' command."""
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:  # Locations for checks tab
            text_to_send = self.items_tab.toPlainText()
        elif current_tab_index == 1:  # Hinted Items tab
            text_to_send = self.locations_tab.toPlainText()
        elif current_tab_index == 2:  # Notes tab
            text_to_send = self.notes_tab.toPlainText()
        else:
            text_to_send = ""

        # Split the text into lines and send each line as a separate message
        for line in text_to_send.splitlines():
            await send_message_to_server(line)  # Send each line individually

    def add_location_hint(self, location_name):
        """Add a location hint to the Locations for Checks tab."""
        item = QListWidgetItem(location_name)
        self.locations_list.addItem(item)

    def add_item_hint(self, item_name):
        """Add an item hint to the Hinted Items tab."""
        item = QListWidgetItem(item_name)
        self.hinted_items_list.addItem(item)

    async def send_message(self):
        """Send the input message text to the server connection function."""
        message_text = self.message_input.text()
        if not message_text:
            return  # Exit if there's no message to send

        slot_name = self.slot_input.text()  # Get the Slot Name from input
        await send_message_to_server(message_text)  # Pass message to server_connection's function

        # Clear the input field after sending
        self.message_input.clear()


    def toggle_send_button(self):
        """Enable or disable the send button based on message input."""
        self.send_button.setEnabled(bool(self.message_input.text().strip()))

    def add_initial_padding(self):
        """Add initial blank lines to push text towards the bottom."""
        padding_lines = "\n" * 90
        self.output_display.append(padding_lines)

    def print_to_server_console(self, text):
        """Display parsed text on the server console, auto-track, and update hints."""

        self.output_display.append("\n" + text)
        self.output_display.moveCursor(QtGui.QTextCursor.End)
        self.output_display.ensureCursorVisible()

        self.auto_track()

    def auto_track(self):
        """Automatically track checked locations and update data.json."""
        # Load checked locations from JSON
        try:
            with open(checked_location_file_path, 'r') as checked_file:
                checked_data = json.load(checked_file)["checked_locations"]
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: checked_location.json file not found or could not be decoded.")
            return
        
        new_all_major_data = load_data(data_file_path)
        
        # Load data.json
        data_updated_count = 0
        for tab_name, items in new_all_major_data.items():
            for item in items:
                # Check if the 4th field matches any location in checked_data
                if item[3] in checked_data:
                    if item[4] != 1:  # Only update if it's not already set
                        item[4] = 1
                        data_updated_count += 1
        
        # Save updated data.json
        save_data(data_file, new_all_major_data)

    def start_server_connection(self):
        server_address = self.server_input.text()
        player_slot = self.slot_input.text()

        # Save the config data when connecting
        self.save_config_data(server_address, player_slot)

        # Initialize and start the server connection thread
        self.server_thread = ServerThread(server_address, player_slot)
        self.server_thread.start()


    def save_config_data(self, server_address, slot_name):
        """Save server address and slot name to config.json."""
        config_data = {"server_address": server_address, "slot_name": slot_name}
        with open(config_file_path, "w") as f:
            json.dump(config_data, f, indent=4)

    def load_config_data(self):
        """Load server address and slot name from config.json."""
        try:
            with open(config_file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def load_notes(self):
        """Load hints from hint_my_location_file.json or return an empty list if the file doesn't exist."""
        try:
            with open(notes_file_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

class HoverTooltip(QLabel):
    """Tooltip overlay widget for displaying information over other widgets."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #444444; color: white; padding: 5px; font-size: 10pt;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()

    def show_tooltip(self, pos):
        self.move(pos)
        self.show()

    def hide_tooltip(self):
        self.hide()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.all_item_widgets = {}        # Global timer for debouncing file change events
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)  # Ensure it only triggers once after timeout
        self.pending_file_actions = set()  # Store the file to act upon after debounce

        # Connect the timer's timeout signal to the action handler
        self.debounce_timer.timeout.connect(self.run_file_change_actions)
        self.season = None
        self.tooltip = HoverTooltip("")  # Initialize tooltip overlay
        
        # Initialize attributes for secondary windows
        self.server_window = None  # Track the server window instance
        
        # QFileSystemWatcher to monitor specific files
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.addPath(checked_location_file_path)
        self.file_watcher.addPath(current_items_file_path)
        self.file_watcher.addPath(data_file_path)
        self.file_watcher.addPath(hint_my_location_file_path)

        # Connect the `fileChanged` signals for specific files
        self.file_watcher.fileChanged.connect(self.handle_file_change)

        # Load initial state of data.json
        self.previous_data_state = load_data(data_file_path)

        # Add data.json to the file watcher and connect to the change detection function
        self.file_watcher.addPath(data_file_path)
        self.file_watcher.fileChanged.connect(self.detect_array_changes)

        # Set up the main layout
        self.setWindowTitle("Stardew Check Tracker")
        self.setGeometry(300, 100, 1200, 500)
        self.setStyleSheet("font-family: 'Consolas', monospace; font-size: 8pt;")

        self.server_window = None  # Track the server window instance

        main_layout = QVBoxLayout()

        # Top bar layout with Server input, Connect button, and Reset button
        top_bar_layout = QHBoxLayout()

        # Open Server Window Button
        open_server_button = QPushButton("Open Server Window")
        open_server_button.clicked.connect(self.open_server_window)
        top_bar_layout.addWidget(open_server_button)

        # Reset Button
        reset_button = QPushButton("Reset All")
        reset_button.clicked.connect(self.reset_all_checkboxes)
        top_bar_layout.addWidget(reset_button)

        # More initialization code for tabs, layouts, and controls...
        self.setLayout(main_layout)

        # Add the top bar layout to the main layout
        main_layout.addLayout(top_bar_layout)

        # Global Counter Label
        self.global_counter_label = QLabel()
        main_layout.addWidget(self.global_counter_label)

        # Season filter buttons (single selection)
        self.selected_season = None
        self.season_buttons = []

        self.load_season_from_config()
        season_layout = QHBoxLayout()
        for season in ["Spring", "Summer", "Fall", "Winter"]:
            button = QPushButton(season)
            button.setCheckable(True)
            
            # Check if the current season matches the selected season
            if self.selected_season == season:
                button.setChecked(True)
                button.setStyleSheet(season_colors[season])  # Use the selected season's color
            else:
                button.setStyleSheet("background-color: #4c5052;")  # Default color for unselected
            
            # Connect button to filter_by_season
            button.clicked.connect(lambda _, s=season, b=button: self.filter_by_season(s, b))
            self.season_buttons.append(button)
            season_layout.addWidget(button)

        main_layout.addLayout(season_layout)

        # Create tab widgets for Main, Skills, Mines, and Friends sections
        self.main_tabs = QTabWidget()
        self.skills_tabs = QTabWidget()
        self.mines_tabs = QTabWidget()
        self.friends_tabs = QTabWidget()

        self.main_tabs.currentChanged.connect(self.update_all_background_colors)
        
        # Counter labels for each tab set
        self.counter_labels = {}
        self.total_checkboxes = 0
        self.total_checked = 0

        skills_tab_name = "Skillsanity"
        mines_tab_name = "Elevatorsanity"
        friends_tab_name = "Friendsanity"

        # Add main tabs dynamically
        for tab_name, display_name in tab_display_names.items():
            items = all_major_data.get(tab_name, [])
            self.total_checkboxes += len(items)
            self.main_tabs.addTab(self.create_tab(tab_name, items), display_name)

        # Add Skills, Mines, and Friends tabs to their respective tab widgets
        self.skills_tabs.addTab(self.create_skills_tab(skills_tab_name), "Skills")
        self.mines_tabs.addTab(self.create_mines_tab(mines_tab_name), "Mines")
        self.friends_tabs.addTab(self.create_friends_tab(friends_tab_name), "Friends")

        # Add the Recent Items tab
        self.recent_items_tab = QTabWidget()
        self.recent_items_display = QTextEdit()
        self.recent_items_display.setReadOnly(True)  # Make the display read-only
        self.recent_items_display.setStyleSheet("font-family: Consolas; font-size: 10pt;")
        self.recent_items_tab.addTab(self.recent_items_display, "Important Items Status")
        

        
        # Initialize recent items display
        self.update_recent_items()

        # Set maximum height for Skills, Mines, and Friends tabs
        max_height = 250  # Set this to the desired max height in pixels
        self.skills_tabs.setMaximumHeight(max_height)
        self.mines_tabs.setMaximumHeight(max_height)
        self.friends_tabs.setMaximumHeight(max_height)
        self.recent_items_tab.setMaximumHeight(max_height)
        self.skills_tabs.setMinimumHeight(max_height)
        self.mines_tabs.setMinimumHeight(max_height)
        self.friends_tabs.setMinimumHeight(max_height)
        self.recent_items_tab.setMinimumHeight(max_height)

        # Create a horizontal layout for Skills, Mines, and Friends
        side_tab_layout = QHBoxLayout()
        side_tab_layout.addWidget(self.skills_tabs)
        side_tab_layout.addWidget(self.mines_tabs)
        side_tab_layout.addWidget(self.friends_tabs)
        side_tab_layout.addWidget(self.recent_items_tab)

        # Add main and side tabs to the main layout
        main_layout.addWidget(self.main_tabs)
        main_layout.addLayout(side_tab_layout)
        self.setLayout(main_layout)
        self.main_tabs.currentChanged.connect(lambda: self.update_note_tab("t"))


        # Initialize the global counter label
        self.update_global_counter()
        self.update_tab_names()
        self.update_season_button_texts()  # Update button texts based on initial data

    def handle_file_change(self, changed_file):
        """
        Handle changes to watched files with a global QTimer debounce mechanism.
        """
        # Add the changed file to the pending actions set
        self.pending_file_actions.add(changed_file)

        if self.debounce_timer.isActive():
            remaining_time = self.debounce_timer.remainingTime()
            print(f"Timer reset. Remaining time was: {remaining_time} ms")
        else:
            print("Starting new debounce timer.")

        # Restart the timer
        self.debounce_timer.start(1000)

    def run_file_change_actions(self):
        """
        Execute actions for all pending files after debounce delay.
        """
        print(f"Running actions for files: {self.pending_file_actions}")
        for changed_file in self.pending_file_actions:
            if changed_file == current_items_file_path:
                self.update_recent_items()
                self.update_tab_names()
                self.update_elevator_floor_label()
                self.update_season_button_texts()
                for skill in ["Combat", "Farming", "Fishing", "Foraging", "Mining"]:
                    self.refresh_skill_level(skill)

            elif changed_file == data_file_path:
                self.update_tab_names()

            elif changed_file == hint_my_location_file_path:
                print("Updating Notes in Hint Text field")
                self.update_note_tab("t")
                self.update_tab_names()

        # Clear pending actions after execution
        self.pending_file_actions.clear()

    def update_recent_items(self):
        """Update the Recent Items tab with the count of specific items from current_items.json."""
        try:
            # Load current items from the JSON file
            current_items_data = load_data(current_items_file_path)
            current_items_list = current_items_data.get("current_items", [])

            # Define the specific items to track
            specific_items = [
                "Rusty Key",
                "Skull Key",
                "Desert Obelisk",
                "Bus Repair",
                "Beach Bridge",
                "Bridge Repair",
                "Dwarvish Translation Guide",
                "Dark Talisman",
                "Railroad Boulder Removed",
                "Greenhouse",
                "Progressive House",
                "Progressive Coop",
                "Progressive Barn",
            ]

            # Get the last tracked item in current_items
            last_tracked_item = None
            if current_items_list:  # Only proceed if the list is not empty
                for item in reversed(current_items_list):
                    if item in specific_items:
                        last_tracked_item = item
                        break

            # Count occurrences of each specific item
            item_counts = {
                item: current_items_list.count(item) for item in specific_items
            }

            # Format the display, marking the last tracked item with "<-- LAST ITEM"
            formatted_items = "<br>".join(
                f'<span style="color: gray; font-size: 12px;">None: {item}</span>' if count == 0
                else (
                    f'<span style="color: #58adb8; font-size: 12px;">{count}x {item} (LAST ITEM)</span>'
                    if item == last_tracked_item
                    else f'<span style="font-size: 12px;">{count}x {item}</span>'
                )
                for item, count in item_counts.items()
            )

            # Update the Recent Items tab with the formatted string
            self.recent_items_display.setText(f"<html><body>{formatted_items}</body></html>")
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            self.recent_items_display.setText("Error reading current_items.json.")
            print(f"Error: {e}")


    def closeEvent(self, event):
        """Override closeEvent to handle shutdown behavior for all windows and threads."""

        # Check if the server window exists and is open
        if self.server_window and hasattr(self.server_window, 'notes_tab'):
            # Access the notes_tab widget and get its content
            notes_data = self.server_window.notes_tab.toPlainText()
            self.save_notes_to_file(notes_data)
            self.server_window.close()

        # Ensure the server thread is terminated if it's still running
        if self.server_window and hasattr(self.server_window, 'server_thread') and self.server_window.server_thread:
            self.server_window.server_thread.terminate()
            self.server_window.server_thread.wait()

        event.accept()  # Accept the close event to proceed with window closing

    

    def open_server_window(self):
        """Open a separate window for server connection and console."""
        if self.server_window is None:
            self.server_window = ServerWindow(self)  # Pass self to ServerWindow
        self.server_window.show()

    def detect_array_changes(self):
        """Detect changes in each array, entry, and field in data.json and print detailed information on changes."""
        try:
            # Load the current state of data.json
            current_data_state = load_data(data_file_path)
        except json.JSONDecodeError:
            print("Error decoding JSON; the file may still be updating.")
            return  # Exit if the file isn't ready to be read

        # Compare each array in the current state with the previous state
        for array_name, current_array in current_data_state.items():
            previous_array = self.previous_data_state.get(array_name, None)
            
            if previous_array is None:
                # New array was added
                continue

            if previous_array != current_array:  # Check if the array has changed

                # Loop through each entry in the array and compare fields
                for index, current_entry in enumerate(current_array):
                    if index >= len(previous_array):
                        # New entry was added
                        entry_name = current_entry[0] if current_entry else f"Entry {index}"
                        continue

                    previous_entry = previous_array[index]
                    entry_name = previous_entry[0] if previous_entry else f"Entry {index}"

                    # Compare each field within the entry
                    for field_index, (current_field, previous_field) in enumerate(zip(current_entry, previous_entry)):
                        if current_field != previous_field:

                            self.update_all(array_name, entry_name, field_index, previous_field, current_field)

                    # Check for extra fields in the current entry if it has more fields than the previous entry
                    if len(current_entry) > len(previous_entry):
                        extra_fields = current_entry[len(previous_entry):]

                # Check for removed entries if previous_array is longer than current_array
                if len(previous_array) > len(current_array):
                    for index in range(len(current_array), len(previous_array)):
                        entry_name = previous_array[index][0] if previous_array[index] else f"Entry {index}"

        # Update the stored previous state to the current state after comparison
        self.previous_data_state = current_data_state


    def create_friends_tab(self, tab_name):
        """Create a special tab for friends with relationship level controls and separate birthday labels."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop)

        # Counter Label for Friends tab
        self.friends_counter_label = QLabel()
        layout.addWidget(self.friends_counter_label)

        # Grid layout for each friend
        friends_layout = QGridLayout()
        friends_layout.setAlignment(Qt.AlignTop)
        friends_layout.setVerticalSpacing(10)

        # List of friends with their birthdays
        friends_with_birthdays = [
            ("Emily", "Birthday: Spring 27"), ("Abigail", "Birthday: Fall 13"), 
            ("Penny", "Birthday: Fall 2"), ("Leah", "Birthday: Winter 23"), 
            ("Maru", "Birthday: Summer 10"), ("Haley", "Birthday: Spring 14")
        ]

        for i, (friend, birthday) in enumerate(friends_with_birthdays):
            friend_label = QLabel(f"{friend}:")
            birthday_label = QLabel(f"({birthday})")  # Separate birthday label
            birthday_label.setStyleSheet("color: gray;")  # Style the birthday label

            level_selector = QComboBox()
            level_options = [0, 2, 4, 6, 8]
            level_selector.addItems(map(str, level_options))
            level_selector.setCurrentText(str(self.get_friends_data(friend, tab_name)))
            level_selector.currentTextChanged.connect(lambda value, f=friend: self.update_friends_data(f, tab_name, int(value)))
            level_selector.currentTextChanged.connect(self.update_friends_counter)

            # Arrange the labels and selectors in the grid layout
            friends_layout.addWidget(friend_label, i, 0, Qt.AlignTop)
            friends_layout.addWidget(birthday_label, i, 1, Qt.AlignTop)
            friends_layout.addWidget(level_selector, i, 2, Qt.AlignTop)

        layout.addLayout(friends_layout)
        tab.setLayout(layout)

        # Initialize the friends counter display
        self.update_friends_counter()
        return tab


    def update_friends_counter(self):
        """Update the Friends tab counter label to show the checked items count."""
        total_checked = 0
        total_items = 48  # Total number of friends
        new_all_major_data = load_data(data_file_path)

        # Count the total checked levels for each friend in JSON data
        for item in new_all_major_data["Friendsanity"]:
            if item[4] > 0:  # Check if relationship level is greater than 0
                total_checked += 1

        # Update the counter label in the Friends tab
        self.friends_counter_label.setText(f"{total_checked} / {total_items} items checked")

    def get_friends_data(self, friend, tab_name):
        """Retrieve the highest relationship level for each friend from the data on load."""
        new_all_major_data = load_data(data_file_path)
        highest_level = 0
        for item in new_all_major_data[tab_name]:
            if friend in item[0] and item[4] == 1:  # Check if friend matches and is set to 1
                level_num = int(item[0].split()[1])  # Extract the level from the format "Friend Level <3"
                if level_num > highest_level:
                    highest_level = level_num
        return highest_level

    def update_friends_data(self, friend, tab_name, level):
        """Update JSON data to reflect relationship levels for each friend."""
        new_all_major_data = load_data(data_file_path)
        for item in new_all_major_data[tab_name]:
            if friend in item[0]:
                # Set the relationship level as 1 if it's <= selected level, else 0
                level_num = int(item[0].split()[1])
                item[4] = 1 if level_num <= level else 0

        save_data(data_file, new_all_major_data)
        self.update_global_counter()
                    
    def create_mines_tab(self, tab_name):
        """Create a special tab for mines with Floor, Treasure controls, and current elevator floor display."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop)  # Align layout to the top

        # Counter Label for Mines tab
        self.mines_counter_label = QLabel()
        layout.addWidget(self.mines_counter_label)  # Add counter at the top

        # Get the last checked values for Floor and Treasure separately
        last_checked_floor = self.get_last_checked_floor(tab_name)
        last_checked_treasure = self.get_last_checked_treasure(tab_name)
        entrance_cutscene_checked = self.get_mines_data("Entrance Cutscene", tab_name)

        # Create Floor selector (multiples of 5 from 0 to 120)
        floor_label = QLabel("Floor:")
        floor_selector = QComboBox()
        floor_selector.setObjectName("Floor")  # Set object name for findChild
        floor_levels = [str(i) for i in range(0, 125, 5)]  # Multiples of 5 from 0 to 120
        floor_selector.addItems(floor_levels)
        floor_selector.setCurrentText(str(last_checked_floor))  # Set to the last checked floor value
        floor_selector.currentTextChanged.connect(lambda value: self.update_mines_data("Floor", tab_name, int(value)))
        floor_selector.currentTextChanged.connect(self.update_mines_counter)  # Update Mines counter

        # Create Treasure selector (specific values)
        treasure_label = QLabel("Treasure:")
        treasure_selector = QComboBox()
        treasure_selector.setObjectName("Treasure")  # Set object name for findChild
        treasure_levels = [0, 10, 20, 40, 50, 60, 70, 80, 90, 100, 110, 120]
        treasure_selector.addItems(map(str, treasure_levels))
        treasure_selector.setCurrentText(str(last_checked_treasure))  # Set to the last checked treasure value
        treasure_selector.currentTextChanged.connect(lambda value: self.update_mines_data("Treasure", tab_name, int(value)))
        treasure_selector.currentTextChanged.connect(self.update_mines_counter)  # Update Mines counter

        # Entrance Cutscene Checkbox
        entrance_cutscene_checkbox = QCheckBox("Entrance Cutscene")
        entrance_cutscene_checkbox.setObjectName("Entrance Cutscene")  # Set object name for findChild
        entrance_cutscene_checkbox.setChecked(entrance_cutscene_checked == 1)
        entrance_cutscene_checkbox.stateChanged.connect(lambda state: self.update_mines_data("Entrance Cutscene", tab_name, state == Qt.Checked))
        entrance_cutscene_checkbox.stateChanged.connect(self.update_mines_counter)  # Update Mines counter

        # Add widgets to layout
        layout.addWidget(floor_label)
        layout.addWidget(floor_selector)
        layout.addWidget(treasure_label)
        layout.addWidget(treasure_selector)
        layout.addWidget(entrance_cutscene_checkbox)

        # Add the Current Elevator Floor line at the bottom
        self.elevator_floor_label = QLabel("Current Elevator Floor: 0")  # Default value
        layout.addWidget(self.elevator_floor_label)
        self.update_elevator_floor_label()  # Update the label based on current items

        tab.setLayout(layout)

        # Initialize Mines counter display
        self.update_mines_counter()
        return tab

    def update_elevator_floor_label(self):
        """Update the elevator floor label based on the number of Progressive Mine Elevator items."""
        try:
            current_items_data = load_data(current_items_file_path)
            elevator_count = current_items_data["current_items"].count("Progressive Mine Elevator")
            elevator_floor = elevator_count * 5
            self.elevator_floor_label.setText(f"Current Elevator Floor: {elevator_floor}")
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            self.elevator_floor_label.setText("Current Elevator Floor: 0")  # Default in case of error

    def get_last_checked_floor(self, tab_name):
        """Retrieve the highest checked floor value specifically for floors."""
        highest_floor = 0
        new_all_major_data = load_data(data_file_path)
        for item in new_all_major_data.get(tab_name, []):
            if "Floor" in item[0] and "Treasure" not in item[0] and item[4] == 1:
                floor_level = int(item[0].split(" ")[1])  # Extract floor number
                if floor_level > highest_floor:
                    highest_floor = floor_level
        return highest_floor

    def get_last_checked_treasure(self, tab_name):
        """Retrieve the highest checked treasure value specifically for treasures."""
        highest_treasure = 0
        new_all_major_data = load_data(data_file_path)
        for item in new_all_major_data.get(tab_name, []):
            if "Floor" in item[0] and "Treasure" in item[0] and item[4] == 1:
                treasure_level = int(item[0].split(" ")[1])  # Extract treasure level
                if treasure_level > highest_treasure:
                    highest_treasure = treasure_level
        return highest_treasure

    def update_mines_counter(self):
        """Update the Mines tab counter label to show the checked items count."""
        total_checked = 0
        total_items = 36  # 1 for Entrance Cutscene, 25 for Floors, 11 for Treasures
        new_all_major_data = load_data(data_file_path)

        # Count checked levels in JSON for Mines
        for item in new_all_major_data["Elevatorsanity"]:
            if item[4] == 1:
                total_checked += 1

        # Update the counter label in the Mines tab
        self.mines_counter_label.setText(f"{total_checked} / {total_items} items checked")
        self.update_global_counter()

    def get_mines_data(self, key, tab_name):
        """Retrieve stored value for Mines tab components based on JSON data."""
        new_all_major_data = load_data(data_file_path)
        for item in new_all_major_data.get(tab_name, []):
            if key in item[0]:  # Find the item matching the key
                return item[4]
        return 0
        
    def update_mines_data(self, key, tab_name, value):
        """Update JSON data with Mines tab values and save."""
        new_all_major_data = load_data(data_file_path)
        for item in new_all_major_data.get(tab_name, []):
            # Update Floor data
            if key == "Floor" and "Floor" in item[0] and "Treasure" not in item[0]:
                floor_level = int(item[0].split(" ")[1])
                item[4] = 1 if floor_level <= value else 0

            # Update Treasure data
            elif key == "Treasure" and "Floor" in item[0] and "Treasure" in item[0]:
                treasure_level = int(item[0].split(" ")[1])
                item[4] = 1 if treasure_level <= value else 0

            # Update Entrance Cutscene data
            elif key == "Entrance Cutscene" and "Entrance Cutscene" in item[0]:
                item[4] = 1 if value else 0  # Set to 1 if checked, 0 if unchecked

        # Save the data after updating
        save_data(data_file, new_all_major_data)
        self.update_mines_counter()  # Refresh the Mines counter

    def create_skills_tab(self, tab_name):
        """Create a special tab for skills with XP and level controls displayed on the same line."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop)  # Ensure the main layout aligns everything at the top

        # Counter Label for Skills tab
        self.skills_counter_label = QLabel()
        layout.addWidget(self.skills_counter_label)  # Add the counter label at the top of the tab

        # Grid layout for skill labels, XP number boxes, and level labels
        skills_layout = QGridLayout()
        skills_layout.setAlignment(Qt.AlignTop)  # Align grid items to the top
        skills_layout.setVerticalSpacing(10)  # Add some spacing between rows for better readability

        skills = ["Combat", "Farming", "Fishing", "Foraging", "Mining"]

        # Track the level labels for updating
        self.skill_level_labels = {}

        for i, skill in enumerate(skills):
            # Skill name label
            skill_label = QLabel(f"{skill} XP:")
            
            # XP Number Box (spin box)
            xp_selector = QSpinBox()
            xp_selector.setRange(0, 10)  # Set the range to 0-10 for XP
            print("test")
            xp_selector.setValue(self.get_skill_xp_from_data(tab_name, skill))
            
            # Connect XP selector to update JSON and refresh level
            xp_selector.valueChanged.connect(lambda value, s=skill: self.update_skill_xp(tab_name, s, value))
            xp_selector.valueChanged.connect(lambda _, s=skill: self.refresh_skill_level(s))  # Refresh level display

            # Skill level label
            level_value = self.get_skill_level_from_current_items(skill)
            max_skill_length = max(len(s) for s in skills)  # Align skill names dynamically
            padding = " " * (max_skill_length - len(skill))
            level_label = QLabel(f"{skill} Level: {padding} {level_value}")
            self.skill_level_labels[skill] = level_label  # Store reference to the label for updates

            # Arrange widgets in a single row
            skills_layout.addWidget(skill_label, i, 0, Qt.AlignLeft)
            skills_layout.addWidget(xp_selector, i, 1, Qt.AlignLeft)
            skills_layout.addWidget(level_label, i, 2, Qt.AlignLeft)

        layout.addLayout(skills_layout)
        tab.setLayout(layout)

        # Initialize the skills counter display
        self.update_skills_counter()
        return tab

    def refresh_skill_level(self, skill):
        """Refresh the skill level label based on current items with proper alignment."""
        if skill in self.skill_level_labels:
            new_level = self.get_skill_level_from_current_items(skill)
            
            # Calculate padding for alignment
            max_skill_length = max(len(s) for s in ["Combat", "Farming", "Fishing", "Foraging", "Mining"])
            padding = " " * (max_skill_length - len(skill))
            
            # Update the label with proper alignment
            self.skill_level_labels[skill].setText(f"{skill} Level: {padding} {new_level}")

    
    def get_skill_xp_from_data(self, tab_name, skill):
        """Retrieve the highest checked level for each skill from the data on load."""
        new_all_major_data = load_data(data_file_path)
        highest_level = 0
        for item in new_all_major_data[tab_name]:
            if skill in item[0] and item[4] == 1:
                level_num = int(item[0].split()[-1])
                if level_num > highest_level:
                    highest_level = level_num
        return highest_level

    
    def update_skill_xp(self, tab_name, skill, xp):
        """Update JSON data to reflect skill XP."""
        new_all_major_data = load_data(data_file_path)
        for item in new_all_major_data[tab_name]:
            if skill in item[0] and "XP" in item[0]:
                item[2] = str(xp)  # Update the XP value in the third field
                break

        save_data(data_file, new_all_major_data)

    def get_skill_level_from_current_items(self, skill):
        """Calculate the skill level based on the count of relevant items in current_items.json."""
        try:
            current_items_data = load_data(current_items_file_path)
            print(f"Skill Name: {skill}")
            level_count = sum(1 for item in current_items_data["current_items"] if (skill + " Level") in item)
            return level_count
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            return 0  # Default level if an error occurs



    def update_skills_counter(self):
        """Update the Skills tab counter label to show the checked items count."""
        total_checked = 0
        total_items = 50  # Assuming each skill has 10 levels (5 skills * 10 levels)
        new_all_major_data = load_data(data_file_path)

        # Count the total checked levels for each skill in JSON data
        for skill in ["Combat", "Farming", "Fishing", "Foraging", "Mining"]:
            for item in new_all_major_data["Skillsanity"]:
                if skill in item[0] and item[4] == 1:  # Check if level is set to 1
                    total_checked += 1

        # Update the counter label in the Skills tab
        self.update_global_counter()
        self.skills_counter_label.setText(f"{total_checked} / {total_items} items checked")

    def get_skill_level_from_data(self, tab_name, skill):
        """Retrieve the highest checked level for each skill from the data on load."""
        new_all_major_data = load_data(data_file_path)
        highest_level = 0
        for item in new_all_major_data[tab_name]:
            if skill in item[0] and item[4] == 1:
                level_num = int(item[0].split()[-1])
                if level_num > highest_level:
                    highest_level = level_num
        return highest_level

    def update_skill_level(self, tab_name, skill, level):
        """Update JSON data to reflect skill levels up to the selected level."""
        new_all_major_data = load_data(data_file_path)
        for item in new_all_major_data[tab_name]:
            if skill in item[0]:
                level_num = int(item[0].split()[-1])
                item[4] = 1 if level_num <= level else 0

        save_data(data_file, new_all_major_data)
        self.update_global_counter()

    def create_tab(self, tab_name, items):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Load existing notes from note.json
        notes_array = self.load_hint_my_location()
        extra_info_array = self.load_extra_info()

        # Counter Label for this tab
        counter_label = QLabel()
        self.counter_labels[tab_name] = counter_label
        layout.addWidget(counter_label)

        # User Search Bar
        user_search_bar = QLineEdit()
        user_search_bar.setPlaceholderText("User Search... (Use ',' for OR and ':' for AND)")
        user_search_bar.textChanged.connect(lambda text: self.apply_filters(item_widgets, text.lower()))
        layout.addWidget(user_search_bar)

        # Scroll Area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(300)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_layout.setSpacing(10)
        scroll_area.setWidget(scroll_content)

        checkboxes = []
        item_widgets = []

        for index, item in enumerate(items):
            item_name, item_seasons, item_info, item_id, item_state = item

            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setAlignment(Qt.AlignLeft)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(10)

            checkbox = QCheckBox()
            checkbox.setFixedWidth(16)
            checkbox.seasons = item_seasons
            checkbox.setChecked(item_state == 1)
            checkbox.original_index = index

            checkbox_text = QLineEdit()
            checkbox_text.setText(f"{item_name}")
            checkbox_text.setReadOnly(True)
            checkbox_text.setFixedWidth(200)
            checkbox_text.mousePressEvent = lambda event, cb=checkbox: cb.toggle()
            checkbox_text.installEventFilter(self)
            checkbox_text.setObjectName(f"checkbox_text_{index}")

            read_only_input = QLineEdit()
            season_text = (f"{', '.join(item_seasons)}")
            read_only_input.setText("All Seasons" if season_text == "Spring, Summer, Fall, Winter" else season_text)
            read_only_input.setReadOnly(True)
            read_only_input.setFixedWidth(130)

            text_input = QLineEdit()
            text_input.setPlaceholderText(f"{item_info}")
            text_input.setText(f"{item_info}")

            matching_extra_info = next((extra_info for extra_info in extra_info_array if extra_info["checkbox_text"] == item_id), None)
            if matching_extra_info:
                text_input.setText(matching_extra_info["extra_info_input"])

            text_input.textChanged.connect(lambda _, cb_text=item_id, text=text_input: 
                                            self.update_extra_info_array(cb_text, text.text()))

            hint_input = QLineEdit()
            hint_input.setPlaceholderText("Insert Item on Check")
            hint_input.setFixedWidth(220)

            matching_note = next((note for note in notes_array if note["checkbox_text"] == item_id), None)
            if matching_note:
                hint_input.setText(matching_note["hint_input"])

            # Add checkbox to the list of checkboxes
            checkboxes.append(checkbox)

            # Add all widgets to layout
            item_layout.addWidget(checkbox)
            item_layout.addWidget(checkbox_text)
            item_layout.addWidget(read_only_input)
            item_layout.addWidget(text_input)
            item_layout.addWidget(hint_input)
            scroll_layout.addWidget(item_widget)
            # Connect hint_input to update_notes_array to save changes to note.json
            hint_input.textChanged.connect(lambda text, sa=scroll_area, cb_widget=checkbox_text:
                                            self.adjust_scroll_position(sa, cb_widget))

            hint_input.editingFinished.connect(lambda cb_text=item_id, hint=hint_input: 
                                                self.update_notes_array(cb_text, hint.text()))



            # Connect checkbox and hint_input changes to update background color
            checkbox.stateChanged.connect(lambda state, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text: 
                                        self.update_background_color(state, ct, ro, ti, hi, st))
            hint_input.textChanged.connect(lambda _, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text:
                                        self.update_background_color(cb.checkState(), ct, ro, ti, hi, st))

            # Connect text_input changes to update background color
            text_input.textChanged.connect(lambda _, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text:
                                        self.update_background_color(cb.checkState(), ct, ro, ti, hi, st))
            
            checkbox.stateChanged.connect(lambda state, cb_text=item_id, c=checkbox, t=tab_name, i=index, sb=user_search_bar: self.update_checkbox(c, scroll_layout, checkboxes, t, i, sb, cb_text))

            item_widgets.append({
                'widget': item_widget,
                'checkbox_text': checkbox_text,
                'read_only_input': read_only_input,
                'text_input': text_input,
                'hint_input': hint_input,
                'checkbox': checkbox,
                'item_id': item_id  # Add the Item_ID here
            })

            # Connect checkbox state change to update functions
            self.update_background_color(checkbox.checkState(), checkbox_text, read_only_input, text_input, hint_input, season_text)

        self.all_item_widgets[tab_name] = item_widgets
        layout.addWidget(scroll_area)
        self.update_counter(checkboxes, tab_name)
        counter_label.setText(f"{len([cb for cb in checkboxes if cb.isChecked()])} / {len(checkboxes)} items checked")

        return tab
    
    def print_modified_checkbox(self, checkbox_text):
        """
        Print the checkbox text of the modified hint_input.
        Args:
            checkbox_text: The text of the associated checkbox.
        """
        print(f"Modified checkbox_text: {checkbox_text}")
        return checkbox_text

    
    def scroll_to_top_adjusted(self, scroll_area, pink_widgets_count):
        """
        Scroll to the top of the scroll area, adjusting based on the number of pink widgets.
        Args:
            scroll_area: QScrollArea instance.
            pink_widgets_count: Number of pink widgets at the top.
        """
        # Define the offset per pink widget (in pixels)
        offset_per_pink_widget = 30  # Adjust this value based on your widget height

        if pink_widgets_count == 0:
            pink_widgets_count += 1

        if pink_widgets_count == 1:
            pink_widgets_count += 1

        # Calculate the adjusted scroll position
        adjusted_position = (pink_widgets_count - 2) * offset_per_pink_widget

        # Scroll to the adjusted position
        scroll_area.verticalScrollBar().setValue(adjusted_position)

    def adjust_scroll_position(self, scroll_area, current_checkbox_text):
        """
        Adjust the scroll position of the given scroll area based on the number of pink widgets,
        unless the current checkbox text has the background color #b85858 or black.
        Args:
            scroll_area: QScrollArea instance.
            current_checkbox_text: The checkbox_text widget being modified.
        """
        # Check the background color of the current checkbox_text
        forbidden_colors = ["background-color: #b85858;", "background-color: black;"]
        if current_checkbox_text and any(color in current_checkbox_text.styleSheet() for color in forbidden_colors):
            print(f"Skipping scroll adjustment for: {current_checkbox_text.text()} (background-color matches forbidden colors)")
            return

        # Find all widgets in the scroll area
        scroll_content = scroll_area.widget()
        scroll_layout = scroll_content.layout()

        # Count pink widgets
        pink_widgets_count = 0
        for i in range(scroll_layout.count()):
            widget = scroll_layout.itemAt(i).widget()
            if widget:
                checkbox_text = widget.findChild(QLineEdit)
                if checkbox_text and "background-color: #cca1ff;" in checkbox_text.styleSheet():
                    pink_widgets_count += 1

        # Adjust the scroll position
        self.scroll_to_top_adjusted(scroll_area, pink_widgets_count)

    def count_in_logic_and_incomplete(self, tab_name):
        """Count the items that are in logic and not yet completed."""
        in_logic_count = 0
        items = all_major_data.get(tab_name, [])
        for item in items:
            item_state = item[4]  # Check the completed state
            item_in_logic = has_requirements(item[0], item[2])  # Check if in logic
            if item_in_logic != "Red" and item_in_logic != "Pink" and item_state == 0:  # In logic and not completed
                in_logic_count += 1
        return in_logic_count

    def count_hinted_items(self, tab_name):
        try:
            # Open and parse the JSON file
            with open(hint_my_location_file_path, 'r') as file:
                data = json.load(file)
            
            # Ensure data is a list
            if not isinstance(data, list):
                raise ValueError("Expected a list in the JSON file.")
            
            # Count occurrences of tab_name in the "tab" field,
            # excluding items with an empty "hint_input" and ensuring "state" is "not found"
            count = sum(
                1 for item in data
                if item.get("tab") == tab_name 
                and item.get("hint_input", "").strip()
                and item.get("state") == "not found"
                and item.get("user_state") in (0, None)
            )
            
            return count
        except FileNotFoundError:
            print(f"Error: File not found at {hint_my_location_file_path}")
            return 0
        except json.JSONDecodeError:
            print("Error: Failed to parse JSON file. Please check the file's content.")
            return 0
        except Exception as e:
            print(f"An error occurred: {e}")
            return 0


    def update_tab_names(self):
        """Update the tab names with the count of in-logic items and dynamically map the new names."""
        global tab_name_mapping
        tab_name_mapping = {}  # Clear the mapping

        # Extract the current tab names and strip any counts (e.g., "Crops (5)" -> "Crops")
        current_tab_names = [
            self.main_tabs.tabText(i).split("\n(")[0] for i in range(self.main_tabs.count())
        ]

        # Match stripped names to tab_display_names to determine the correct internal order
        ordered_internal_names = [
            internal_name
            for display_name in current_tab_names
            for internal_name, mapped_name in tab_display_names.items()
            if mapped_name == display_name
        ]

        # Iterate through the tabs and update their names
        for i, internal_tab_name in enumerate(ordered_internal_names):
            # Get the widget for the tab
            tab_widget_page = self.main_tabs.widget(i)
            if not tab_widget_page:
                continue  # Skip if no tab widget is found

            # Fetch the display name from tab_display_names
            display_name = tab_display_names.get(internal_tab_name, internal_tab_name)

            # Count in-logic items for the tab
            in_logic_count = self.count_in_logic_and_incomplete(internal_tab_name)
            hinted_count = self.count_hinted_items(internal_tab_name)

            # Create the new display name with the count
            new_display_name = f"{display_name}\n({in_logic_count}|{hinted_count})"

            # Update the tab text
            self.main_tabs.setTabText(i, new_display_name)        
            self.main_tabs.tabBar().setTabButton(i, QTabBar.RightSide, QLabel(f"\n"))  # Use RightSide for proper layout

            # Update the mapping
            tab_name_mapping[new_display_name] = internal_tab_name

    def load_hint_my_location(self):
        """Load hints from hint_my_location_file.json or return an empty list if the file doesn't exist."""
        try:
            with open(hint_my_location_file_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_hint_my_location_to_file(self, notes_array):
        """Save the notes array to note.json."""
        with open(hint_my_location_file_path, "w") as file:
            json.dump(notes_array, file, indent=4)
    
    def save_hint_my_item_to_file(self, notes_array):
        """Save the notes array to note.json."""
        with open(hint_my_item_file_path, "w") as file:
            json.dump(notes_array, file, indent=4)
    
    def save_notes_to_file(self, notes_array):
        """Save the notes array to note.json."""
        with open(notes_file_path, "w") as file:
            json.dump(notes_array, file, indent=4)

    def update_notes_array(self, checkbox_text, hint_text):
        """Update or add an entry in notes.json based on checkbox_text."""
        notes_array = self.load_hint_my_location()

        # Get the current tab index and name
        current_tab_index = self.main_tabs.currentIndex()
        current_tab_name = self.main_tabs.tabText(current_tab_index)

        # Map the tab name to its internal data key
        data_key = tab_name_mapping.get(current_tab_name, "Unknown")

        # Check if the note already exists, and update it if so
        for note in notes_array:
            if note["checkbox_text"] == checkbox_text:
                note["hint_input"] = hint_text
                note["class"] = "Unknown"
                note["state"] = "Unknown"
                note["tab"] = data_key  # Dynamically set the tab
                break
        else:
            # Add new entry if no match is found
            notes_array.append({
                "checkbox_text": checkbox_text,
                "hint_input": hint_text,
                "class": "Unknown",
                "state": "Unknown",
                "tab": data_key  # Dynamically set the tab
            })

        # Save the updated notes array
        self.save_hint_my_location_to_file(notes_array)


    def update_note_tab(self, state):
        """Update the hint_text field of every widget to match the hint_input field in note.json and set text color based on class."""
        notes_array = self.load_hint_my_location()  # Load the notes from note.json

        # Get the current tab index and tab name
        current_tab_index = self.main_tabs.currentIndex()
        current_tab_name = self.main_tabs.tabText(current_tab_index)  # Get the tab name as displayed
        data_key = tab_name_mapping.get(current_tab_name, "")  # Map the display name to internal data key

        if data_key in self.all_item_widgets:  # Check if the current tab has associated widgets
            #print(f"Updating tab: {tab_name}")  # Debug: Print the tab name being updated
            for widget in self.all_item_widgets[data_key]:
                # Use item_id for matching instead of checkbox_text
                matching_note = next(
                    (note for note in notes_array if note["checkbox_text"] == widget['item_id']), None
                )
                if matching_note:
                    # Update the hint_input field with the note's hint_input value
                    print_a = matching_note["checkbox_text"]
                    if state == "t":
                        print(f"State Test for {print_a}")
                        widget['hint_input'].setText(matching_note["hint_input"])

                    # Determine the background color based on the "class" field
                    text_class = matching_note.get("class", "").lower()
                    if text_class == "progressive":
                        background_color = "#9bf2bf"
                    elif text_class == "useful":
                        background_color = "#e8f29b"
                    elif text_class == "filler":
                        background_color = "Null"
                        widget['checkbox'].setChecked(True)
                    else:
                        background_color = "Null"
                    
                    state_check = matching_note.get("state", "").lower()
                    if state_check == "found":
                        widget['checkbox'].setChecked(True)
                        

                    # Retrieve the current background color
                    text_color = "black"

                    if not background_color == "Null":
                        widget['hint_input'].setStyleSheet(f"color: {text_color}; background-color: {background_color};")

    def load_extra_info(self):
        """Load extra_info from extra_info.json or return an empty list if the file doesn't exist."""
        try:
            with open(extra_info_file_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_extra_info_to_file(self, extra_info_array):
        """Save the extra_info array to note.json."""
        with open(extra_info_file_path, "w") as file:
            json.dump(extra_info_array, file, indent=4)

    def update_extra_info_array(self, checkbox_text, extra_info_text):
        """Update or add an entry in notes.json based on checkbox_text."""
        extra_info_array = self.load_extra_info()
        
        # Check if the note already exists, and update it if so
        for extra_info in extra_info_array:
            if extra_info["checkbox_text"] == checkbox_text:
                extra_info["extra_info_input"] = extra_info_text  # Overwrite the existing entry
                break
        else:
            # Add new entry if no match is found
            extra_info_array.append({
                "checkbox_text": checkbox_text,
                "extra_info_input": extra_info_text
            })

        # Save the updated extra_info array
        self.save_extra_info_to_file(extra_info_array)
    
    def update_all(self, array_name, entry_name, field_index, previous_field, current_field):
        """
        Update the widget checkbox based on detected changes.
        If the field index is 4 and the current field is greater than the previous field,
        update the UI accordingly.
        For 'Skillsanity', 'Elevatorsanity', and 'Friendsanity', recreate the tabs.
        """
        # Check if we're targeting the 5th field (index 4)
        if field_index == 4:
            # Ensure current_field is greater than previous_field
            if current_field > previous_field:
                if array_name == "Skillsanity":
                    # Remove and recreate the Skills tab
                    self.skills_tabs.removeTab(0)
                    self.skills_tabs.addTab(self.create_skills_tab("Skillsanity"), "Skills")
                elif array_name == "Elevatorsanity":
                    # Remove and recreate the Mines tab
                    self.mines_tabs.removeTab(0)
                    self.mines_tabs.addTab(self.create_mines_tab("Elevatorsanity"), "Mines")
                elif array_name == "Friendsanity":
                    # Remove and recreate the Friends tab
                    self.friends_tabs.removeTab(0)
                    self.friends_tabs.addTab(self.create_friends_tab("Friendsanity"), "Friends")
                elif array_name in self.all_item_widgets:
                    # For other tabs, proceed as before
                    for item in self.all_item_widgets[array_name]:
                        # Check if the widget's checkbox_text matches entry_name
                        if item['checkbox_text'].text() == entry_name:
                            # Set the checkbox to a checkmark
                            item['checkbox'].setChecked(True)
                            # Force UI to refresh to show the change
                            item['checkbox'].repaint()
                            break


    def eventFilter(self, obj, event):
        if isinstance(obj, QLineEdit) and obj.objectName().startswith("checkbox_text"):
            if event.type() == QEvent.Enter:
                # Log the current tab and display name
                display_tab_name = self.main_tabs.tabText(self.main_tabs.currentIndex())

                # Map display name to internal name
                internal_tab_name = tab_name_mapping.get(display_tab_name)

                # Fetch only the relevant widget for the tooltip based on hover
                item_widgets = self.all_item_widgets.get(internal_tab_name, [])
                relevant_widget = next(
                    (widget for widget in item_widgets if widget['checkbox_text'] is obj), None
                )
                if not relevant_widget:
                    return super().eventFilter(obj, event)

                # Extract the item name and generate tooltip for this specific widget
                item_name = obj.text()
                tooltip_text = get_requirements_text(item_name, [relevant_widget])
                self.show_tooltip(event, obj, tooltip_text)
            elif event.type() == QEvent.Leave:
                self.tooltip.hide_tooltip()
        return super().eventFilter(obj, event)

    def sort_widgets_by_background_color(self):
        """
        Sort the widgets in the current tab by background color priority.
        """

        # Get the current tab index and validate main_tabs and current tab
        if not self.main_tabs:
            return
        current_tab_index = self.main_tabs.currentIndex()

        current_tab = self.main_tabs.widget(current_tab_index)
        if not current_tab:
            return  # Exit if no current tab is found

        # Try to get the scroll area within the current tab
        scroll_area = current_tab.findChild(QScrollArea)
        if not scroll_area:
            return  # Exit if no scroll area found

        scroll_content = scroll_area.widget()
        scroll_layout = scroll_content.layout()

        if not scroll_layout:
            return  # Exit if no layout found

        color_priority = {
            "background-color: #8f0599; color: white;": 1, # Pink (highest priority)
            "background-color: #cca1ff; color: black;": 2, # Light purple (hinted items)
            "background-color: #344534; color: white;": 3, # Spring
            "background-color: #4f4300; color: white;": 3, # Summer
            "background-color: #633700; color: white;": 3, # Fall
            "background-color: #0a3054; color: white;": 3, # Winter
            "background-color: #58adb8; color: black;": 4, # Default color
            "background-color: #db708a; color: black;": 7, # Red (hinted)
            "background-color: #b85858; color: white;": 8, # Red (not in logic)
            "background-color: black; color: white;": 9,   # Checked (lowest priority)
        }


        # Gather widgets with their priority
        widgets_with_priority = []
        for i in range(scroll_layout.count()):
            widget = scroll_layout.itemAt(i).widget()
            if not widget:
                continue  # Skip if no widget found

            checkbox_text = widget.findChild(QLineEdit)
            if checkbox_text:
                style = checkbox_text.styleSheet()
                priority = color_priority.get(style, len(color_priority))
                priority = color_priority.get(style, 3)  # Default priority is 10 if no match is found

                widgets_with_priority.append((priority, widget))

        # Sort widgets by priority and reorder them in the layout
        widgets_with_priority.sort(key=lambda x: x[0])
        for i, (_, widget) in enumerate(widgets_with_priority):
            scroll_layout.removeWidget(widget)
            scroll_layout.insertWidget(i, widget)

        scroll_layout.update()
        self.update_note_tab("f")

    def show_tooltip(self, event, widget, tooltip_text):
        """Display tooltip near the widget with additional information."""
        self.tooltip.setText(tooltip_text)
        pos = widget.mapToGlobal(event.pos() + QtCore.QPoint(10, 10))
        self.tooltip.show_tooltip(pos)
        
    def update_background_color(self, state, checkbox_text, read_only_input, text_input, hint_input, season_text):
        """
        Update the background color of the text inputs based on the checkbox state.
        If the checkbox is checked, set the background color to black; otherwise, adjust based on logic and other conditions.
        """
        not_in_logic = has_requirements(checkbox_text.text(), text_input.text())
        # Apply color logic based on state and logic
        if state == Qt.Checked:
            #priority 6
            # Black background with white text when checked
            style = "background-color: black; color: white;"
        elif not_in_logic == "Red":
            #priority 5
            # Red background with white text for "NOT IN LOGIC" (overrides purple)
            style = "background-color: #b85858; color: white;"
            if hint_input.text().strip():
                #priority 2
                # Light purple background for items with hints
                style = "background-color: #db708a; color: black;"
        elif not_in_logic == "Pink":
            #priority 1
            # Red background with white text for "NOT IN LOGIC" (overrides purple)
            style = "background-color: #8f0599; color: white;"
        elif hint_input.text().strip():
            #priority 2
            # Light purple background for items with hints
            style = "background-color: #cca1ff; color: black;"
        elif self.season is not None and (season_text == "All Seasons" or self.season in season_text):
            #priority 3
            # Apply season color if in the selected season, otherwise default
            style = f"{season_colors[self.season]}; color: white;"
        else:
            # Reset to default (clear inline styles to use theme)
            #priority 4
            style = "background-color: #58adb8; color: black;"

        # Apply the style
        checkbox_text.setStyleSheet(style)
        read_only_input.setStyleSheet(style)
        text_input.setStyleSheet(style)
        hint_input.setStyleSheet(style)

        # Force UI redraw
        checkbox_text.update()
        read_only_input.update()
        text_input.update()
        hint_input.update()


        # Sort widgets after updating their background color
        self.sort_widgets_by_background_color()

    def update_all_background_colors(self):
        """Update the background color for all items in the current tab based on checkbox state and season."""
        current_tab_index = self.main_tabs.currentIndex()  # Get the current tab index
        tab_name = self.main_tabs.tabText(current_tab_index)  # Get the current tab's display name
        data_key = tab_name_mapping.get(tab_name, "")  # Map display name to internal data key

        if data_key in self.all_item_widgets:  # Check if tab data exists in widgets dictionary
            for item in self.all_item_widgets[data_key]:
                checkbox = item['checkbox']
                checkbox_text = item['checkbox_text']
                read_only_input = item['read_only_input']
                text_input = item['text_input']
                hint_input = item['hint_input']
                season_text = read_only_input.text()

                # Call update_background_color with the current state of each checkbox in the current tab
                self.update_background_color(checkbox.checkState(), checkbox_text, read_only_input, text_input, hint_input, season_text)

    def apply_filters(self, item_widgets, search_text=""):
        """
        Filters and shows/hides item_widgets based on search_text.
        - If search_text contains ',' it acts as an OR (matches any term).
        - If search_text contains ':' it acts as an AND (matches all terms).
        """
        # Normalize the search_text
        search_text = search_text.lower()

        # Determine the filtering mode based on the presence of ',' or ':'
        if ',' in search_text:
            search_terms = [term.strip() for term in search_text.split(',')]
            filter_mode = 'OR'
        elif ':' in search_text:
            search_terms = [term.strip() for term in search_text.split(':')]
            filter_mode = 'AND'
        else:
            search_terms = [search_text.strip()]
            filter_mode = 'SINGLE'

        for item in item_widgets:
            # Retrieve the text from checkbox_text and text_input QLineEdit widgets
            checkbox_text_value = item['checkbox_text'].text().lower() if item['checkbox_text'] else ""
            text_input_value = item['text_input'].text().lower() if item['text_input'] else ""

            # Check conditions based on filter_mode
            if filter_mode == 'OR':
                is_visible = any(term in checkbox_text_value or term in text_input_value for term in search_terms)
            elif filter_mode == 'AND':
                is_visible = all(term in checkbox_text_value or term in text_input_value for term in search_terms)
            else:  # SINGLE
                is_visible = search_text in checkbox_text_value or search_text in text_input_value

            # Show or hide the item_widget based on the search match
            item['widget'].setVisible(is_visible)


    def update_checkbox(self, checkbox, layout, checkboxes, tab_name, index, search_bar, item_id):
        # Update the JSON data with the new state
        item_state = 1 if checkbox.isChecked() else 0
        all_major_data[tab_name][index][4] = item_state  # Update state in data

        notes_array = self.load_hint_my_location()

        # Check if the note already exists, and update it if so
        print(f"Passed Go: {item_id}")
        for note in notes_array:
            if note["checkbox_text"] == item_id:
                note["hint_input"]
                note["class"]
                note["state"]
                note["tab"]
                note["user_state"] = item_state
                break

        # Save the updated state to the JSON file
        save_data(data_file, all_major_data)
        self.save_hint_my_location_to_file(notes_array)

        # Update the global and tab counters
        self.update_counter(checkboxes, tab_name)
        self.update_global_counter()


    def reset_all_checkboxes(self):
        # Friends whose states should remain checked at level 8
        friends_to_keep_checked = ["Alex", "Elliott", "Harvey", "Sam", "Sebastian", "Shane"]
        new_all_major_data = load_data(data_file_path)

            # Step 1: Define the reset structure for data.json
        reset_data_structure = {
            "Bundles": [],
            "Cropsanity": [],
            "Skillsanity": [],
            "Elevatorsanity": [],
            "Questsanity": [],
            "Fishsanity": [],
            "Chefsanity": [],
            "Friendsanity": [],
            "Cartsanity": [],
            "Booksanity": [],
            "Librarysanity": [],
            "Monstersanity": [],
            "Blueprintsanity": [],
            "Upgradesanity": [],
            "Raccoonsanity": [],
            "Festivalsanity": [],
            "Misc": []
        }

        # Reset season selection
        self.selected_season = None  # Clear the selected season
        for button in self.season_buttons:
            button.setText(button.text().split(" (")[0])  # Remove "(Not Found)" if present
            button.setStyleSheet("background-color: #4c5052;")  # Default color
        
        self.selected_season = None  # Clear the selected season

        self.config_data = load_config(config_file_path)
        self.selected_season = None
        self.config_data["season"] = self.selected_season
        save_config(config_file_path, self.config_data)

        # Step 1: Reset all JSON fields to 0
        for tab_name, items in new_all_major_data.items():
            for item in items:
                item[4] = 0  # Set every item's 'state' to 0 initially

        # Step 2: Set specific friends' state to 1
        for item in new_all_major_data.get("Friendsanity", []):
            if any(friend in item[3] for friend in friends_to_keep_checked):
                item[4] = 1

        # Reset notes in note.json
        self.save_hint_my_location_to_file([])  # Clear notes by saving an empty list to note.json

        # Reset notes in note.json
        self.save_hint_my_item_to_file([])  # Clear notes by saving an empty list to note.json

        # Reset notes in note.json
        self.save_extra_info_to_file([])  # Clear notes by saving an empty list to note.json

        # Reset notes in note.json
        self.save_notes_to_file("")  # Clear notes by saving an empty list to note.json
        # Update the notes_tab in the ServerWindow
        if self.server_window:  # Ensure the server_window exists
            notes_tab_text = self.server_window.load_notes()  # Call load_notes from ServerWindow
            self.server_window.notes_tab.setPlainText(notes_tab_text)  # Set the text

        # Reset current_items.json
        with open(current_items_file_path, "w") as f:
            json.dump({"current_items": []}, f, indent=4)  # Save an empty "current_items" list

        # Reset current_items.json
        with open(checked_location_file_path, "w") as f:
            json.dump({"checked_locations": []}, f, indent=4)  # Save an empty "current_items" list

        # Step 3: Update UI checkboxes to match JSON data for each tab
        for i in range(self.main_tabs.count()):
            # Use mapped data key
            tab_name = self.main_tabs.tabText(i)
            data_key = tab_name_mapping.get(tab_name, "")
            items = new_all_major_data.get(data_key, [])

            # Retrieve UI checkboxes for each tab
            tab_widget_page = self.main_tabs.widget(i)
            if tab_widget_page:
                checkboxes = tab_widget_page.findChildren(QCheckBox)

                # Update each checkbox based on JSON data
                for checkbox, item in zip(checkboxes, items):
                    checkbox.setChecked(item[4] == 1)
                    checkbox.repaint()  # Force immediate UI update

        # Step 4: Reset Skills Tab SpinBoxes and JSON entries
        for i in range(self.skills_tabs.count()):
            skill_tab_name = self.skills_tabs.tabText(i)
            skill_items = new_all_major_data.get(skill_tab_name, [])
            
            # Find each skill's SpinBox and reset to 0
            skill_widgets = self.skills_tabs.widget(i).findChildren(QSpinBox)
            
            for skill_widget in skill_widgets:
                skill_widget.setValue(0)  # Reset SpinBox to 0
                skill_name = skill_widget.objectName()  # Get the skill's name from the widget

                # Set all levels for this skill to 0 in JSON
                for level in range(1, 11):
                    for item in skill_items:
                        if f"{skill_name} Level {level}" in item[0]:
                            item[4] = 0  # Reset JSON level to 0

                skill_widget.repaint()  # Force immediate UI update

        # Step 2: Reset all fields in all_major_data to match the empty structure
        new_all_major_data.clear()
        new_all_major_data.update(reset_data_structure)

        # Step 3: Save the cleared structure to data.json
        save_data(data_file, new_all_major_data)

        # Step 5: Clear and recreate widgets for each tab
        for i in range(self.main_tabs.count()):
            tab_widget_page = self.main_tabs.widget(i)

            if tab_widget_page:
                # Remove all widgets from the tab layout
                layout = tab_widget_page.layout()
                if layout:
                    while layout.count() > 0:
                        child = layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()

                # Repopulate the tab with the initial (reset) items
                tab_name = self.main_tabs.tabText(i)
                data_key = tab_name_mapping.get(tab_name, "")
                items = new_all_major_data.get(data_key, [])
                new_tab = self.create_tab(data_key, items)
                self.main_tabs.removeTab(i)
                self.main_tabs.insertTab(i, new_tab, tab_name)

        # Step 5: Reset Friends Tab ComboBoxes to 0, except specific friends at 8
        for i in range(self.friends_tabs.count()):
            friend_tab_name = self.friends_tabs.tabText(i)
            friend_items = new_all_major_data.get(friend_tab_name, [])
            
            # Find each friend's ComboBox and reset to 0
            friend_widgets = self.friends_tabs.widget(i).findChildren(QComboBox)
            
            for friend_widget in friend_widgets:
                friend_name = friend_widget.objectName()  # Get the friend's name from the widget

                # Set friends in the keep_checked list to 8, others to 0
                if friend_name in friends_to_keep_checked:
                    friend_widget.setCurrentText("8")  # Set ComboBox to 8
                    for level in range(2, 9, 2):
                        for item in friend_items:
                            if f"{friend_name} {level} <3" in item[0]:
                                item[4] = 1 if level == 8 else 0
                else:
                    friend_widget.setCurrentIndex(0)  # Reset ComboBox to 0
                    for level in range(2, 9, 2):
                        for item in friend_items:
                            if f"{friend_name} {level} <3" in item[0]:
                                item[4] = 0

                friend_widget.repaint()  # Force immediate UI update

        # Step 6: Reset Mines Tab selections to 0 for Floor, Treasure, and Entrance Cutscene
        # Reset Floor selector to 0
        floor_selector = self.mines_tabs.findChild(QComboBox, "Floor")
        if floor_selector:
            floor_selector.setCurrentIndex(0)  # Reset ComboBox to 0
            floor_selector.repaint()

        # Reset Treasure selector to 0
        treasure_selector = self.mines_tabs.findChild(QComboBox, "Treasure")
        if treasure_selector:
            treasure_selector.setCurrentIndex(0)  # Reset ComboBox to 0
            treasure_selector.repaint()

        # Reset Entrance Cutscene checkbox to unchecked
        entrance_cutscene_checkbox = self.mines_tabs.findChild(QCheckBox, "Entrance Cutscene")
        if entrance_cutscene_checkbox:
            entrance_cutscene_checkbox.setChecked(False)
            entrance_cutscene_checkbox.repaint()

        # Step 7: Save the reset state for all tabs to the JSON file
        save_data(data_file, new_all_major_data)

        # Step 8: Update the global counter
        self.total_checked = sum(1 for tab in new_all_major_data.values() for item in tab if item[4] == 1)
        self.update_global_counter()


    def update_counter(self, checkboxes, tab_name):
        total = len(checkboxes)
        checked = sum(1 for checkbox in checkboxes if checkbox.isChecked())
        self.counter_labels[tab_name].setText(f"{checked} / {total} items checked")

    def update_global_counter(self):
        # Count the total number of items in the JSON and those with 1 in the last field
        total_items = sum(len(items) for items in all_major_data.values())
        checked_items = sum(1 for items in all_major_data.values() for item in items if item[4] == 1)
        
        # Update the global counter label with the new values
        self.global_counter_label.setText(f"{checked_items} / {total_items} items checked")

    def filter_by_season(self, season, button):
        """
        Update button colors and filter checkboxes based on selected season.
        If the season is not in current_items.json, change the button text to 'Season (Not Found)'.
        """
        # Unselect other season buttons and reset their colors
        for btn in self.season_buttons:
            if btn != button:
                btn.setChecked(False)
                btn.setStyleSheet("background-color: #4c5052;")  # Default color
            else:
                # Check if the season exists in current_items.json
                try:
                    current_items_data = load_data(current_items_file_path)
                    seasons_in_items = current_items_data.get("current_items", [])
                    if season not in seasons_in_items:
                        # Update button text to indicate 'Not Found'
                        button.setText(f"{season} (Not Found)")
                    else:
                        # Reset to just the season name
                        button.setText(season)
                except (FileNotFoundError, json.JSONDecodeError):
                    # Handle error cases gracefully
                    button.setText(f"{season} (Not Found)")

                # Set selected season button color
                btn.setStyleSheet(season_colors[season] if btn.isChecked() else "background-color: #4c5052;")

        # Update the selected season
        self.config_data = load_config(config_file_path)
        self.selected_season = season if button.isChecked() else None
        self.config_data["season"] = self.selected_season
        save_config(config_file_path, self.config_data)

        # Set the selected season
        self.selected_season = season if button.isChecked() else None
        self.season = season if button.isChecked() else None
        self.update_all_background_colors()

    def load_season_from_config(self):
        """Load the selected season from the config file and update the UI."""
        self.config_data = load_config(config_file_path)
        saved_season = self.config_data.get("season")
        if saved_season:
            self.selected_season = saved_season
            self.season = saved_season

            # Find the corresponding button and check it
            for button in self.season_buttons:
                if button.text() == saved_season:
                    button.setChecked(True)
                    button.setStyleSheet("background-color: green;")
                    break

    def update_season_button_texts(self):
        """Update the season button texts based on the presence of seasons in current_items.json."""
        try:
            current_items_data = load_data(current_items_file_path)
            current_items = current_items_data.get("current_items", [])

            for button in self.season_buttons:
                season = button.text().split(" ")[0]  # Extract the season name from the button text
                if season in current_items:
                    button.setText(season)  # Reset to plain season name
                else:
                    button.setText(f"{season} (Not Found)")  # Add "(Not Found)" if the season is missing
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: Failed to load or decode current_items.json.")

# Run the application
app = QApplication(sys.argv)
app.setStyleSheet(dark_theme)
window = MainWindow()
window.show()
sys.exit(app.exec_())