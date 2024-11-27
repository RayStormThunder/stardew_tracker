import sys
import json
import re
import socket
import time
from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication, QSizeGrip, QSizePolicy, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLineEdit, QLabel, QScrollArea, QGroupBox, QPushButton, QListWidget,
    QSpinBox, QComboBox, QGridLayout, QTextEdit, QListWidgetItem,QToolTip, 
)
from PyQt5.QtCore import QFileSystemWatcher, Qt, QObject, QThread, pyqtSignal, QEvent, QPoint
import PyQt5.QtCore
PyQt5.QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
PyQt5.QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)


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
        padding: 8px;
        border: 1px solid #555555;
        border-bottom: none;
    }

    QTabBar::tab:selected {
        background-color: #4c4f51;
        font-weight: bold;
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

    # Determine which function to call based on the first condition
    if required_items and "item" in required_items[0]:
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
    Generate tooltip text for standard requirements with detailed item needs.
    """
    tooltip_text = "Required Items:\n"
    unmet_requirements = []
    relevant_items = []

    for condition in conditions:
        # Handle individual item requirements
        if "item" in condition:
            item_name = condition["item"]
            required_count = condition.get("count", 1)
            item_count = checked_items.count(item_name)

            if item_count >= required_count:
                # Requirement fully met, add the entire requirement to relevant items
                relevant_items.append(f"{required_count}x {item_name}")
            else:
                # Requirement partially met or unmet
                if item_count > 0:
                    relevant_items.append(f"{item_count}x {item_name}")
                unmet_count = required_count - item_count
                unmet_requirements.append(f"{unmet_count}x {item_name}")

        # Handle "or_items" requirements
        elif "or_items" in condition:
            or_items_text_list = []
            condition_met = False

            for or_item in condition["or_items"]:
                or_item_name = or_item["item"]
                or_item_count = or_item.get("count", 1)
                or_item_actual_count = checked_items.count(or_item_name)

                # Add individual or_item requirements
                or_item_text = f"{or_item_count}x {or_item_name}"
                if or_item_actual_count >= or_item_count:
                    condition_met = True
                    relevant_items.append(or_item_text)  # Add fully met or_items to relevant items
                or_items_text_list.append(or_item_text)

            # Display "One of: ..." if no or_item requirements were fully met
            if not condition_met:
                unmet_requirements.append(f"One of: ({', '.join(or_items_text_list)})")

    # Format the unmet requirements section
    if unmet_requirements:
        tooltip_text += "\n".join(unmet_requirements)
    else:
        tooltip_text += "All requirements met."

    # Display relevant items the user currently has
    tooltip_text += f"\n\nCurrent Relevant Items:\n{', '.join(relevant_items) if relevant_items else 'None'}"

    return tooltip_text

def get_complete_requirements_text(conditions, checked_items, item_widgets):
    """
    Generate tooltip text for complete_X_out_of_Y requirements.
    """
    # Print each widget's `text_input` content for debugging
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

# Define a mapping from tab display names to data keys
tab_name_mapping = {
    "Bundles": "Bundles",
    "Crops": "Cropsanity",
    "Fish": "Fishsanity",
    "Special Orders": "Ordersanity",
    "Monster Kills": "Monstersanity",
    "Quests": "Questsanity",
    "Travelling Cart": "Cartsanity",
    "Books": "Booksanity",
    "Robin's Blueprints": "Blueprintsanity",
    "Clint's Upgrades": "Upgradesanity",
    "Gus' Recipes": "Chefsanity",
    "Festivals": "Festivalsanity", 
    "Misc": "Misc"
}

tab_display_names = {
    "Bundles": "Bundles", 
    "Cropsanity": "Crops", 
    "Fishsanity": "Fish",
    "Ordersanity": "Special Orders", 
    "Questsanity": "Quests", 
    "Cartsanity": "Travelling Cart",
    "Booksanity": "Books",
    "Monstersanity": "Monster Kills",
    "Blueprintsanity": "Robin's Blueprints",
    "Upgradesanity": "Clint's Upgrades", 
    "Chefsanity": "Gus' Recipes", 
    "Festivalsanity": "Festivals", 
    "Misc": "Misc"
}

data_file_path = "../JSONStore/data.json"
config_file_path = "../JSONStore/config.json"
hint_file_path = "../JSONStore/hints.json"
checked_location_file_path = "../JSONStore/checked_location.json"
current_items_file_path = "../JSONStore/current_items.json"
requirements_file_path = "../JSONPull/requirements.json"
note_file_path = "../JSONStore/note.json"  # Path to note.json

# Load the data from the JSON file
data_file = data_file_path
all_major_data = load_data(data_file_path)

# Load config data from config.json
config_file = config_file_path
with open(config_file, 'r') as f:
    config_data = json.load(f)

from server_connection import connect_to_server, message_emitter,send_message_to_server  # Import from server_connection.py
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
        self.setGeometry(400, 200, 850, 980)  # Adjusted width for two-column layout

        # Load hints data from JSON
        self.hints_data = self.load_hints_data()

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

        # Populate tabs from JSON
        self.load_hints()

        self.items_tab.setReadOnly(True)
        self.locations_tab.setReadOnly(True)

        # Add tabs to the widget
        self.tab_widget.addTab(self.locations_tab, "Locations for others to do")
        self.tab_widget.addTab(self.items_tab, "Locations for me to do")
        self.tab_widget.addTab(self.notes_tab, "Notes")
        right_layout.addWidget(self.tab_widget)

        # Button to send info
        self.send_info_button = QPushButton("Send info")
        self.send_info_button.clicked.connect(lambda: asyncio.run(self.send_info()))
        right_layout.addWidget(self.send_info_button)

        # Main layout combining left and right layouts
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        # Connect message signal from server_connection.py to the output display
        message_emitter.message_signal.connect(self.print_to_server_console)

        # Enable Send button only if there’s text in message_input
        self.message_input.textChanged.connect(self.toggle_send_button)

    def clear_hints(self):
        """Clear the items in hints.json."""
        self.hints_data = {
            "Locations for checks": [],
            "Hinted Items": [],
            "Notes": [{"notes": ""}]
        }
        self.save_hints_data()  # Save the cleared hints data to hints.json
        self.load_hints()  # Reload the hints in the UI to reflect the cleared state

    def load_hints(self):
        """Load hints from the JSON file and populate the tabs."""
        try:
            with open(hint_file_path, "r") as file:
                hints_data = json.load(file)

            # Populate Locations for checks tab
            locations_text = "\n".join(
                f"{hint['hint']} ({'found' if hint['obtained_status'] == 'True' else 'not found'})"+"\n"
                for hint in hints_data["Locations for checks"]
            )
            self.locations_tab.setPlainText(locations_text)

            # Populate Hinted Items tab
            items_text = "\n".join(
                f"{hint['hint']} ({'found' if hint['obtained_status'] == 'True' else 'not found'})"+"\n"
                for hint in hints_data["Hinted Items"]
            )
            self.items_tab.setPlainText(items_text)

            # Populate Notes tab
            notes_text = hints_data["Notes"][0]["notes"] if hints_data["Notes"] else ""
            self.notes_tab.setPlainText(notes_text)

        except FileNotFoundError:
            print("Hints file not found.")
        except json.JSONDecodeError:
            print("Error decoding hints JSON.")

    def load_hints_data(self):
        """Load hints from the JSON file."""
        try:
            with open(hint_file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print("Hints file not found.")
            return {}
        except json.JSONDecodeError:
            print("Error decoding hints JSON.")
            return {}

    def save_hints_data(self):
        """Save the updated hints data back to the JSON file."""
        with open(hint_file_path, "w") as file:
            json.dump(self.hints_data, file, indent=4)


    def save_hints(self):
        """Save the current state of hints to the JSON file."""
        hints_data = {
            "Locations for checks": [
                {"hint": line.split(" (")[0], "obtained_status": "True" if "(found)" in line else "False"}
                for line in self.locations_tab.toPlainText().splitlines() if line
            ],
            "Hinted Items": [
                {"hint": line.split(" (")[0], "obtained_status": "True" if "(found)" in line else "False"}
                for line in self.items_tab.toPlainText().splitlines() if line
            ],
            "Notes": [{"notes": self.notes_tab.toPlainText()}]
        }

        with open(hint_file_path, "w") as file:
            json.dump(hints_data, file, indent=4)


    async def send_info(self):
        """Send the content of the selected tab to the server using the 'say' command."""
        current_tab_index = self.tab_widget.currentIndex()
        if current_tab_index == 0:  # Locations for checks tab
            text_to_send = self.locations_tab.toPlainText()
        elif current_tab_index == 1:  # Hinted Items tab
            text_to_send = self.items_tab.toPlainText()
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

    def print_to_server_console(self, text, state):
        """Display parsed text on the server console, auto-track, and update hints."""

        # Append to the main output display if not a hint
        if "[Hint]" not in text:
            self.output_display.append("\n" + text)
            self.output_display.moveCursor(QtGui.QTextCursor.End)
            self.output_display.ensureCursorVisible()

        # Determine found status from the text
        found_status = "True" if "(found)" in text else "False"
        clean_text = text.replace(" (found)", "").replace(" (not found)", "")

        if "[Hint]" in text:
            # If found_status is False, add the hint if not already in hints_data
            if found_status == "False":
                if state in (1, 0):
                    if not self.check_and_update_hint(clean_text, "Hinted Items"):
                        # Append to the items tab and add to hints_data
                        self.items_tab.append("\n" + clean_text + " (not found)")
                        self.hints_data["Hinted Items"].append({
                            "hint": clean_text,
                            "obtained_status": found_status
                        })
                        self.save_hints_data()

                if state in (2, 0):
                    if not self.check_and_update_hint(clean_text, "Locations for checks"):
                        # Append to the locations tab and add to hints_data
                        self.locations_tab.append("\n" + clean_text + " (not found)")
                        self.hints_data["Locations for checks"].append({
                            "hint": clean_text,
                            "obtained_status": found_status
                        })
                        self.save_hints_data()

            # If found_status is True, remove the hint if it exists in hints_data and reload tabs
            if found_status == "True":
                if state in (1, 0):
                    if self.check_and_update_hint(clean_text, "Hinted Items", remove_if_found=True):
                        # Clear and reload the items tab after removing the hint
                        self.items_tab.clear()
                        self.load_hints()

                if state in (2, 0):
                    if self.check_and_update_hint(clean_text, "Locations for checks", remove_if_found=True):
                        # Clear and reload the locations tab after removing the hint
                        self.locations_tab.clear()
                        self.load_hints()

        # Call auto_track unless state is 3
        if state != 3:
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
        
        # Print the number of updated fields
        print(f"Auto-track completed: {data_updated_count} fields changed to 1.")

    def check_and_update_hint(self, hint_text, hint_category, remove_if_found=False):
        """
        Check if a hint exists in hints_data and update its obtained_status if needed.
        If remove_if_found is True and the hint is found, it will be removed from hints_data.
        """
        for hint in self.hints_data.get(hint_category, []):
            if hint["hint"] == hint_text:
                if remove_if_found:
                    self.hints_data[hint_category].remove(hint)
                    self.save_hints_data()
                return True
        return False

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
        self.all_item_widgets = {}
        self.season = None
        self.tooltip = HoverTooltip("")  # Initialize tooltip overlay
        
        # Initialize attributes for secondary windows
        self.server_window = None  # Track the server window instance

        # Initialize QFileSystemWatcher to monitor file changes
        self.file_watcher = QFileSystemWatcher(self)
        self.file_watcher.addPath(checked_location_file_path)
        self.file_watcher.addPath(current_items_file_path)
        
        # Connect file change signal to the update function
        self.file_watcher.fileChanged.connect(self.update_all_background_colors)

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
        season_layout = QHBoxLayout()
        season_state = ""
        for season in ["Spring", "Summer", "Fall", "Winter"]:
            button = QPushButton(season)
            button.setCheckable(True)
            button.setStyleSheet("background-color: #4c5052;")  # Default color when not selected
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

        # Sort widgets after updating their background color
        self.main_tabs.currentChanged.connect(self.sort_widgets_by_background_color)
        
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

        # Set maximum height for Skills, Mines, and Friends tabs
        max_height = 300  # Set this to the desired max height in pixels
        self.skills_tabs.setMaximumHeight(max_height)
        self.mines_tabs.setMaximumHeight(max_height)
        self.friends_tabs.setMaximumHeight(max_height)

        # Create a horizontal layout for Skills, Mines, and Friends
        side_tab_layout = QHBoxLayout()
        side_tab_layout.addWidget(self.skills_tabs)
        side_tab_layout.addWidget(self.mines_tabs)
        side_tab_layout.addWidget(self.friends_tabs)

        # Add main and side tabs to the main layout
        main_layout.addWidget(self.main_tabs)
        main_layout.addLayout(side_tab_layout)
        self.setLayout(main_layout)

        # Initialize the global counter label
        self.update_global_counter()

    def closeEvent(self, event):
        """Override closeEvent to handle shutdown behavior for all windows and threads."""

        # Close the Server Window if it's open and ensure hints are saved
        if self.server_window is not None:
            if hasattr(self.server_window, 'save_hints'):
                self.server_window.save_hints()  # Explicitly save hints before closing
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
                print(f"Array '{array_name}' was added.")
                continue

            if previous_array != current_array:  # Check if the array has changed
                print(f"Changes detected in '{array_name}' array:")

                # Loop through each entry in the array and compare fields
                for index, current_entry in enumerate(current_array):
                    if index >= len(previous_array):
                        # New entry was added
                        entry_name = current_entry[0] if current_entry else f"Entry {index}"
                        print(f"  {entry_name} was added: {current_entry}")
                        continue

                    previous_entry = previous_array[index]
                    entry_name = previous_entry[0] if previous_entry else f"Entry {index}"

                    # Compare each field within the entry
                    for field_index, (current_field, previous_field) in enumerate(zip(current_entry, previous_entry)):
                        if current_field != previous_field:
                            print(f"  {entry_name}'s field {field_index} changed from '{previous_field}' to '{current_field}'")

                            self.update_all(array_name, entry_name, field_index, previous_field, current_field)

                    # Check for extra fields in the current entry if it has more fields than the previous entry
                    if len(current_entry) > len(previous_entry):
                        extra_fields = current_entry[len(previous_entry):]
                        for extra_field in extra_fields:
                            print(f"  {entry_name} has a new field: {extra_field}")

                # Check for removed entries if previous_array is longer than current_array
                if len(previous_array) > len(current_array):
                    for index in range(len(current_array), len(previous_array)):
                        entry_name = previous_array[index][0] if previous_array[index] else f"Entry {index}"
                        print(f"  {entry_name} was removed: {previous_array[index]}")

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
        """Create a special tab for mines with Floor and Treasure controls."""
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

        tab.setLayout(layout)

        # Initialize Mines counter display
        self.update_mines_counter()
        return tab

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
        """Create a special tab for skills with level controls from 0 to 10."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setAlignment(Qt.AlignTop)  # Ensure the main layout aligns everything at the top

        # Counter Label for Skills tab
        self.skills_counter_label = QLabel()
        layout.addWidget(self.skills_counter_label)  # Add the counter label at the top of the tab

        # Grid layout for skill labels and level selectors
        skills_layout = QGridLayout()
        skills_layout.setAlignment(Qt.AlignTop)  # Align grid items to the top
        skills_layout.setVerticalSpacing(10)  # Add some spacing between rows for better readability

        skills = ["Combat", "Farming", "Fishing", "Foraging", "Mining"]

        for i, skill in enumerate(skills):
            skill_label = QLabel(f"{skill}:")
            level_selector = QSpinBox()
            level_selector.setRange(0, 10)
            level_selector.setValue(self.get_skill_level_from_data(tab_name, skill))
            
            # Connect each SpinBox to update JSON and the counter when changed
            level_selector.valueChanged.connect(lambda value, s=skill: self.update_skill_level(tab_name, s, value))
            level_selector.valueChanged.connect(self.update_skills_counter)  # Update the counter

            skills_layout.addWidget(skill_label, i, 0, Qt.AlignTop)  # Align labels to the top
            skills_layout.addWidget(level_selector, i, 1, Qt.AlignTop)  # Align selectors to the top

        layout.addLayout(skills_layout)
        tab.setLayout(layout)

        # Initialize the skills counter display
        self.update_skills_counter()
        return tab

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
        notes_array = self.load_notes()

        # Counter Label for this tab
        counter_label = QLabel()
        self.counter_labels[tab_name] = counter_label
        layout.addWidget(counter_label)

        # User Search Bar
        user_search_bar = QLineEdit()
        user_search_bar.setPlaceholderText("User Search...")
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

            # Connect the textChanged signal to update the third field in JSON
            text_input.textChanged.connect(lambda new_text, t=tab_name, i=index: self.update_third_field_in_json(t, i, new_text))

            hint_input = QLineEdit()
            hint_input.setPlaceholderText("Insert Item on Check")
            hint_input.setFixedWidth(140)

            matching_note = next((note for note in notes_array if note["checkbox_text"] == item_name), None)
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
            hint_input.textChanged.connect(lambda _, cb_text=checkbox_text.text(), hint=hint_input: 
                                        self.update_notes_array(cb_text, hint.text()))
            # Connect checkbox and hint_input changes to update background color
            checkbox.stateChanged.connect(lambda state, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text: 
                                        self.update_background_color(state, ct, ro, ti, hi, st))
            hint_input.textChanged.connect(lambda _, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text:
                                        self.update_background_color(cb.checkState(), ct, ro, ti, hi, st))

            # Connect text_input changes to update background color
            text_input.textChanged.connect(lambda _, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text:
                                        self.update_background_color(cb.checkState(), ct, ro, ti, hi, st))

            item_widgets.append({
                'widget': item_widget,
                'checkbox_text': checkbox_text,
                'read_only_input': read_only_input,
                'text_input': text_input,
                'hint_input': hint_input,
                'checkbox': checkbox
            })

            # Connect checkbox state change to update functions
            checkbox.stateChanged.connect(lambda state, c=checkbox, t=tab_name, i=index, sb=user_search_bar: self.update_checkbox(c, scroll_layout, checkboxes, t, i, sb))
            self.update_background_color(checkbox.checkState(), checkbox_text, read_only_input, text_input, hint_input, season_text)

        self.all_item_widgets[tab_name] = item_widgets
        layout.addWidget(scroll_area)
        self.update_counter(checkboxes, tab_name)
        counter_label.setText(f"{len([cb for cb in checkboxes if cb.isChecked()])} / {len(checkboxes)} items checked")

        return tab
    
    def load_notes(self):
        """Load notes from note.json or return an empty list if the file doesn't exist."""
        try:
            with open(note_file_path, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_notes_to_file(self, notes_array):
        """Save the notes array to note.json."""
        with open(note_file_path, "w") as file:
            json.dump(notes_array, file, indent=4)

    def update_notes_array(self, checkbox_text, hint_text):
        """Update or add an entry in notes.json based on checkbox_text."""
        notes_array = self.load_notes()
        
        # Check if the note already exists, and update it if so
        for note in notes_array:
            if note["checkbox_text"] == checkbox_text:
                note["hint_input"] = hint_text  # Overwrite the existing entry
                break
        else:
            # Add new entry if no match is found
            notes_array.append({
                "checkbox_text": checkbox_text,
                "hint_input": hint_text
            })

        # Save the updated notes array
        self.save_notes_to_file(notes_array)

    def update_third_field_in_json(self, tab_name, index, new_text):
        """Update the third field in data.json with the new text from text_input."""
        # Update the third field for the specified item in the JSON data
        new_all_major_data = load_data(data_file_path)
        new_all_major_data[tab_name][index][2] = new_text
        
        # Save the updated data back to the JSON file
        save_data(data_file, new_all_major_data)
        print(f"Updated third field in {tab_name}[{index}] to '{new_text}'")
    
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
                    print("Skills test")
                    # Remove and recreate the Skills tab
                    self.skills_tabs.removeTab(0)
                    self.skills_tabs.addTab(self.create_skills_tab("Skillsanity"), "Skills")
                elif array_name == "Elevatorsanity":
                    print("Mines test")
                    # Remove and recreate the Mines tab
                    self.mines_tabs.removeTab(0)
                    self.mines_tabs.addTab(self.create_mines_tab("Elevatorsanity"), "Mines")
                elif array_name == "Friendsanity":
                    print("Friends test")
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
            "background-color: #344534; color: black;": 3, # Spring
            "background-color: #4f4300; color: black;": 4, # Summer
            "background-color: #633700; color: black;": 5, # Fall
            "background-color: #0a3054; color: black;": 6, # Winter
            "background-color: #58adb8; color: black;": 7, # Default color
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
        Filters and shows/hides item_widgets based on whether the search_text is found
        in either the checkbox_text or text_input of each item.
        """
        for item in item_widgets:
            # Retrieve the text from checkbox_text and text_input QLineEdit widgets
            checkbox_text_value = item['checkbox_text'].text().lower() if item['checkbox_text'] else ""
            text_input_value = item['text_input'].text().lower() if item['text_input'] else ""
            
            # Check if search_text is found in either checkbox_text or text_input
            is_visible = search_text in checkbox_text_value or search_text in text_input_value
            
            # Show or hide the item_widget based on the search match
            item['widget'].setVisible(is_visible)

    def update_checkbox(self, checkbox, layout, checkboxes, tab_name, index, search_bar):
        # Update the JSON data with the new state
        item_state = 1 if checkbox.isChecked() else 0
        all_major_data[tab_name][index][4] = item_state  # Update state in data

        # Save the updated state to the JSON file
        save_data(data_file, all_major_data)

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
            "Ordersanity": [],
            "Questsanity": [],
            "Fishsanity": [],
            "Chefsanity": [],
            "Friendsanity": [],
            "Cartsanity": [],
            "Booksanity": [],
            "Monstersanity": [],
            "Blueprintsanity": [],
            "Upgradesanity": [],
            "Festivalsanity": [],
            "Misc": []
        }

        # Step 1: Reset all JSON fields to 0
        for tab_name, items in new_all_major_data.items():
            for item in items:
                item[4] = 0  # Set every item's 'state' to 0 initially

        # Step 2: Set specific friends' state to 1
        for item in new_all_major_data.get("Friendsanity", []):
            if any(friend in item[3] for friend in friends_to_keep_checked):
                item[4] = 1

        if self.server_window is not None:
            self.server_window.clear_hints()  # Clear the hints if the ServerWindow is open

        # Reset notes in note.json
        self.save_notes_to_file([])  # Clear notes by saving an empty list to note.json

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
        # Count the total number of items in the JSON and those with `1` in the last field
        total_items = sum(len(items) for items in all_major_data.values())
        checked_items = sum(1 for items in all_major_data.values() for item in items if item[4] == 1)
        
        # Update the global counter label with the new values
        self.global_counter_label.setText(f"{checked_items} / {total_items} items checked")

    def filter_by_season(self, season, button):
        """Update button colors and filter checkboxes based on selected season."""
        # Unselect other season buttons and reset their colors
        for btn in self.season_buttons:
            if btn != button:
                btn.setChecked(False)
                btn.setStyleSheet("background-color: #4c5052;")  # Default color
            else:
                # Set selected season button color
                btn.setStyleSheet(season_colors[season] if btn.isChecked() else "background-color: #4c5052;")

        # Set the selected season
        self.selected_season = season if button.isChecked() else None
        self.season = season if button.isChecked() else None
        self.update_all_background_colors()

# Run the application
app = QApplication(sys.argv)
app.setStyleSheet(dark_theme)
window = MainWindow()
window.show()
sys.exit(app.exec_())