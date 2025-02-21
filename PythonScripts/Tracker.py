import shutil
import sys
import json
import re
import os
import socket
import threading
import time
import yaml
from PyQt5.QtGui import QFont, QPainter, QPixmap, QIcon
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
from PyQt5 import QtCore
from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor, QPixmap, QIcon
from PyQt5.QtWidgets import QTabBar
from PyQt5.QtWidgets import (
    QApplication, QSizeGrip, QSizePolicy, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLineEdit, QLabel, QScrollArea, QGroupBox, QPushButton, QListWidget,
    QSpinBox, QComboBox, QGridLayout, QTextEdit, QListWidgetItem,QToolTip,
)
from PyQt5.QtCore import QFileSystemWatcher,  QSize, Qt, QObject, QTimer, QThread, pyqtSignal, QEvent, QPoint
import PyQt5.QtCore
PyQt5.QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
PyQt5.QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps)

# Define a mapping from tab display names to data keys
tab_name_mapping = {
    "Crafts Room": "Crafts Room",
    "Pantry": "Pantry",
    "Fish Tank": "Fish Tank",
    "Bulletin Board": "Bulletin Board",
    "Vault": "Vault",
    "Boiler Room": "Boiler Room",
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
    "Crafts Room": "Crafts Room",
    "Pantry": "Pantry",
    "Fish Tank": "Fish Tank",
    "Bulletin Board": "Bulletin Board",
    "Vault": "Vault",
    "Boiler Room": "Boiler Room",
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


#Store
all_locations_file_path = "../JSONStore/all_locations.json"
bundle_items_file_path = "../JSONStore/bundle_items.json"
checked_location_file_path = "../JSONStore/checked_location.json"
checked_location_detailed_file_path = "../JSONStore/checked_location_detailed.json"
current_items_file_path = "../JSONStore/current_items.json"
config_file_path = "../JSONStore/config.json"
data_file_path = "../JSONStore/data.json"
extra_info_file_path = "../JSONStore/extra_info.json"
hint_my_item_file_path = "../JSONStore/hint_my_item.json"
hint_my_location_file_path = "../JSONStore/hint_my_location.json"
notes_file_path = "../JSONStore/notes.json"
player_table_file_path = "../JSONStore/player_table.json"

#Pull
all_data_file_path = "../JSONPull/all_data.json"
requirements_file_path = "../JSONPull/requirements.json"
requirements_goals_file_path = "../JSONPull/requirements"
bundle_items_vanilla_file_path = "../JSONPull/bundle_items_vanilla.json"
settings_folder = "../Settings"


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

import json
import os
import keyboard
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import json
from collections import Counter
from functools import lru_cache

# Cache dictionaries
extra_info_cache = {}
goals_cache = {}
expand_goals_cache = {}
wrap_requirements_cache = {}
remove_completed_requirements_cache = {}
all_requirements_met_cache = {}
parse_requirements_cache = {}
requirements_cache = None

def get_requirements(item_name, return_type):
    count = get_extra_info(item_name, "count", 0)
    if item_name == "The Missing Bundle":
        print(count)
    if count == 0:
        return {"text": "No Requirements", "color": "Blue"}[return_type]
    
    return_results = []
    return_next_results = []
        
    return_results.append(get_requirements_main(item_name, return_type, 0, count - 1))
    
    if count == 2:
        if return_type == "text":
            return_results.append(get_requirements_main(item_name, return_type, 1, count - 1))
        if return_type == "color":
            return_next_results.append(get_requirements_main(item_name, return_type, 1, count - 1))

    if return_type == "text":
        return "\n\n".join(map(str, return_results))
    
    if return_type == "color":
        # Merge results from both lists
        all_colors = return_results + return_next_results

        # Define priority order
        priority = {"Pink": 3, "Red": 2, "Blue": 1}

        # Find the highest priority color
        highest_priority_color = max(all_colors, key=lambda c: priority.get(c, 0))

        return highest_priority_color

    return "Failed: " + return_type


def get_requirements_main(item_name, return_type, skip, skip_compare):
    """Get all requirements formatted properly, count completed goals, and update logic tracking only if needed."""
    
    # Detect if Shift is being held
    shift_held = keyboard.is_pressed("shift")

    # Load bundle_items.json to track "IN LOGIC" and "CHECKED" status
    with open(bundle_items_file_path, "r", encoding="utf-8") as file:
        bundle_data = json.load(file)

    in_logic_key = f"{item_name} | IN LOGIC"
    checked_key = f"{item_name} | CHECKED"
    
    current_in_logic = set(bundle_data.get(in_logic_key, []))  # Convert to set for comparison
    manually_checked = set(bundle_data.get(checked_key, []))  # Goals manually checked off

    # Get extra info
    type = get_extra_info(item_name, "type", skip)
    goals_to_complete = get_extra_info(item_name, "goals_to_complete", skip)
    amount_of_goals = get_extra_info(item_name, "amount_of_goals", skip)

    # Check if the bundle settings are properly configured
    if type == "Bundle" or type == "Setting":
        bundle_goals = get_bundle_list(item_name)
        if len(bundle_goals) != amount_of_goals:
            return {"text": "Please click the bundle icon and select what possible goals you can get", "color": "Pink"}[return_type]

    # Get goals and forced goals
    goals, forced_goals = get_goals(item_name, skip)
    if goals == ["No Requirements"] and not forced_goals:
        return {"text": "No Requirements", "color": "Blue"}[return_type]
    
    if item_name == "The Missing Bundle":
        print("===================================\n Extra Info for " + item_name + ": \n   -Type: " + type + "\n   -Goals to Complete: " + str(goals_to_complete) + "\n   -Amount of Goals: " + str(amount_of_goals) + "\n\n")

    # Filter goals for bundles
    if type == "Bundle" or type == "Setting":
        goals = [goal for goal in bundle_goals if goal in goals]

    requirements_data = get_requirements_from_folder()

    # Load the current items data
    with open(current_items_file_path, "r") as f:
        current_items_data = json.load(f)
        current_items = Counter(current_items_data["current_items"])  # Use Counter for quantity tracking

    completed_count = 0
    text_output = [f"Complete {goals_to_complete} goals. Currently {completed_count} out of {amount_of_goals} Completed:\n"]
    text_output_shift = [f"Complete {goals_to_complete} goals. Currently {completed_count} out of {amount_of_goals} Completed:\n"]

    # Track in-logic goals
    updated_in_logic = set()  # Use set for easy comparison

    # Process each goal
    for goal in goals:
        if item_name == "The Missing Bundle":
            print("===================================\n Goals for " + goal + "\n\n")

        if goal in manually_checked:
            # ✅ Manually checked goals are always in logic
            text_output.append(f"      ✅Requirements for <b><u>{goal}</u></b>:\n           Manually Checked Off\n")
            completed_count += 1
            updated_in_logic.add(goal)  # Add to IN LOGIC
            continue  # Skip logic checks

        if goal in requirements_data:
            expanded_requirements = expand_goals(requirements_data[goal], requirements_data)

            # Remove completed requirements
            wrapped_requirements = wrap_requirements(expanded_requirements, current_items)
            filtered_requirements = remove_completed_requirements(wrapped_requirements, current_items)

            if not filtered_requirements:  # ✅ All requirements met
                text_output.append(f"      ✅Requirements for <b><u>{goal}</u></b>:\n           All Requirements Met\n")
                completed_count += 1
                updated_in_logic.add(goal)  # Mark as in logic
            else:  # ❌ Missing requirements
                text_output.append(f"      ❌Requirements for <b><u>{goal}</u></b>:\n")
                for requirement in filtered_requirements:
                    text_output.append(parse_requirements(requirement, 10, True, current_items))

            if not expanded_requirements:
                text_output_shift.append(f"      Requirements for <b><u>{goal}</u></b>:\n           All Requirements Met\n")
                completed_count += 1
            else:
                text_output_shift.append(f"      Requirements for <b><u>{goal}</u></b>:\n")
                for requirement in expanded_requirements:
                    text_output_shift.append(parse_requirements(requirement, 10, True, current_items))

    # Update completion count
    text_output[0] = f"Complete {goals_to_complete} goals. Currently {completed_count} out of {amount_of_goals} Completed:\n"
    text_output_shift[0] = f"Complete {goals_to_complete} goals. Currently {completed_count} out of {amount_of_goals} Completed:\n"

    # Append Shift instruction
    if skip == skip_compare:
        text_output.append("\nHold SHIFT and REHOVER to see all requirements")
    else:
        text_output.append("\n")


    # Determine logic color
    color = "Blue" if completed_count >= goals_to_complete else "Red"

    # Choose correct output based on Shift key state
    final_text = text_output_shift if shift_held else text_output

    # **Update IN LOGIC Goals in bundle_items.json ONLY IF CHANGED**
    if type == "Bundle":
        if current_in_logic != updated_in_logic:
            bundle_data[in_logic_key] = list(updated_in_logic)  # Convert back to list for JSON storage

            with open(bundle_items_file_path, "w", encoding="utf-8") as file:
                json.dump(bundle_data, file, indent=4)

    # Return formatted output
    return {
        "text": "".join(final_text)
            .replace("\n", "<br>")
            .replace(" ", "&nbsp;"),  # Convert spaces for indentation
        "color": color
    }[return_type]

def get_requirements_from_folder():
    global requirements_cache

    # Return cached result if it exists and is not empty
    if requirements_cache:
        return requirements_cache  # Works only if cache has data

    combined_requirements = {}  # Store everything in a single dictionary

    # Iterate through all files in the folder
    for filename in os.listdir(requirements_goals_file_path):
        file_path = os.path.join(requirements_goals_file_path, filename)

        # Ensure it's a JSON file before opening
        if filename.endswith(".json") and os.path.isfile(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    
                    # Ensure it's a dictionary before merging
                    if isinstance(data, dict):
                        combined_requirements.update(data)

                except json.JSONDecodeError:
                    print(f"Error decoding JSON in file: {filename}")

    # Cache the result for future calls
    requirements_cache = combined_requirements if combined_requirements else None  # Keep None if empty
    return requirements_cache

def wrap_requirements(requirements, current_items):
    """Wraps the first and last bracket of the JSON with an AND condition."""
    key = json.dumps(requirements, sort_keys=True)  # Cache key based on input data
    if key in wrap_requirements_cache:
        return wrap_requirements_cache[key]

    if not requirements:
        return requirements

    wrapped = {"and_items": requirements}
    wrap_requirements_cache[key] = [wrapped]
    return [wrapped]


def print_json(goal, requirements):
    """Prints expanded requirements in formatted JSON."""
    print(f"\nExpanded Requirements for {goal}:\n")
    print(json.dumps(requirements, indent=4))

def expand_goals(requirements, requirements_data):
    """Cached version of expand_goals"""
    global expand_goals_cache

    key = json.dumps(requirements, sort_keys=True)  # Cache key based on input data
    if key in expand_goals_cache:
        return expand_goals_cache[key]

    expanded = []

    for requirement in requirements:
        new_requirement = {}

        for k, v in requirement.items():
            if isinstance(v, list):
                new_requirement[k] = []
                for item in v:
                    if isinstance(item, dict) and "goal" in item:
                        goal_name = item["goal"]
                        if goal_name in requirements_data:
                            new_requirement[k].extend(expand_goals(requirements_data[goal_name], requirements_data))
                        else:
                            new_requirement[k].append(item)
                    elif isinstance(item, dict):
                        new_requirement[k].append(expand_goals([item], requirements_data)[0])
                    else:
                        new_requirement[k].append(item)
            else:
                new_requirement[k] = v

        expanded.append(new_requirement)

    expand_goals_cache[key] = expanded
    return expanded

def remove_completed_requirements(requirements, current_items):
    """Removes fully completed AND/OR conditions and items, ensuring all keys in a requirement are checked."""
    key = json.dumps(requirements, sort_keys=True) + json.dumps(current_items, sort_keys=True)
    if key in remove_completed_requirements_cache:
        return remove_completed_requirements_cache[key]

    filtered_requirements = []
    for requirement in requirements:
        new_requirement = {}

        if "and_items" in requirement:
            filtered_and_items = remove_completed_requirements(requirement["and_items"], current_items)
            if filtered_and_items:
                new_requirement["and_items"] = filtered_and_items

        if "or_items" in requirement:
            if any(all_requirements_met([item], current_items) for item in requirement["or_items"]):
                pass
            else:
                filtered_or_items = remove_completed_requirements(requirement["or_items"], current_items)
                if filtered_or_items:
                    new_requirement["or_items"] = filtered_or_items

        if "item" in requirement:
            item_name = requirement["item"]
            required_count = requirement.get("count", 1)
            if current_items.get(item_name, 0) < required_count:
                new_requirement["item"] = item_name
                new_requirement["count"] = required_count

        if new_requirement:
            filtered_requirements.append(new_requirement)

    remove_completed_requirements_cache[key] = filtered_requirements
    return filtered_requirements

def all_requirements_met(requirements, current_items):
    """Checks if ALL requirements are met, considering quantity."""
    key = json.dumps(requirements, sort_keys=True) + json.dumps(current_items, sort_keys=True)
    if key in all_requirements_met_cache:
        return all_requirements_met_cache[key]

    for requirement in requirements:
        if "and_items" in requirement:
            if not all(all_requirements_met([item], current_items) for item in requirement["and_items"]):
                all_requirements_met_cache[key] = False
                return False
        if "or_items" in requirement:
            if not any(all_requirements_met([item], current_items) for item in requirement["or_items"]):
                all_requirements_met_cache[key] = False
                return False
        if "item" in requirement:
            item_name = requirement["item"]
            required_count = requirement.get("count", 1)
            if current_items.get(item_name, 0) < required_count:
                all_requirements_met_cache[key] = False
                return False

    all_requirements_met_cache[key] = True
    return True

def parse_requirements(requirement, indent_level, use_dash, current_items):
    """Recursively parse and return formatted requirements, handling nested AND/OR conditions properly."""
    key = json.dumps(requirement, sort_keys=True) + json.dumps(current_items, sort_keys=True) + str(indent_level) + str(use_dash)
    if key in parse_requirements_cache:
        return parse_requirements_cache[key]

    indent = " " * indent_level
    symbol = "-" if use_dash else "="
    output = []

    if "and_items" in requirement:
        flattened_items = []
        for item in requirement["and_items"]:
            if "and_items" in item and len(item) == 1:
                flattened_items.extend(item["and_items"])
            else:
                flattened_items.append(item)

        if len(flattened_items) == 1:
            output.append(parse_requirements(flattened_items[0], indent_level, use_dash, current_items))
        else:
            output.append(f"{indent}{symbol} AND:\n")
            for item in flattened_items:
                output.append(parse_requirements(item, indent_level + 4, not use_dash, current_items))

    if "or_items" in requirement:
        flattened_items = []
        for item in requirement["or_items"]:
            if "or_items" in item and len(item) == 1:
                flattened_items.extend(item["or_items"])
            else:
                flattened_items.append(item)

        if len(flattened_items) == 1:
            output.append(parse_requirements(flattened_items[0], indent_level, use_dash, current_items))
        else:
            output.append(f"{indent}{symbol} OR:\n")
            for item in flattened_items:
                output.append(parse_requirements(item, indent_level + 4, not use_dash, current_items))

    if "item" in requirement:
        item_name = requirement["item"].replace("<", "&lt;").replace(">", "&gt;")
        required_count = requirement.get("count", 1)
        output.append(f"{indent}{symbol} ⭐️ {item_name} (x{required_count})\n")

    parsed_output = "".join(output)
    parse_requirements_cache[key] = parsed_output
    return parsed_output

def get_bundle_list(item_name):
    try:
        # Load the JSON data
        with open(bundle_items_file_path, 'r', encoding='utf-8') as file:
            bundle_data = json.load(file)

        # Return the list if the item exists, otherwise return an empty list
        return bundle_data.get(item_name, [])

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON: {e}")
        return []

def get_extra_info(item_name, info, skip):
    """Cached version of get_extra_info"""
    global extra_info_cache

    key = (item_name, info, skip)
    if key in extra_info_cache:
        return extra_info_cache[key]

    try:
        with open(requirements_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for category in data.values():
            if isinstance(category, list):
                for entry in category:
                    if isinstance(entry, list) and len(entry) > 1:
                        name, details = entry[0], entry[1]

                        if name == item_name and isinstance(details, list):
                            extra_info_list = []
                            for detail in details:
                                if isinstance(detail, dict) and "extra_info" in detail:
                                    extra_info_list.extend(detail["extra_info"])

                            if info == "count":
                                result = len(extra_info_list)
                            elif 0 <= skip < len(extra_info_list):
                                result = extra_info_list[skip].get(info, "Info not found")
                            else:
                                result = 0

                            extra_info_cache[key] = result
                            return result
    except (FileNotFoundError, json.JSONDecodeError):
        return "Requirements file not found"

    return 0

def get_goals(item_name, skip):
    """Cached version of get_goals"""
    global goals_cache

    key = (item_name, skip)
    if key in goals_cache:
        return goals_cache[key]

    try:
        with open(requirements_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        goals_list = []
        forced_goals_list = []
        goal_entries = []

        for category in data.values():
            if isinstance(category, list):
                for entry in category:
                    if isinstance(entry, list) and len(entry) > 1:
                        name, details = entry[0], entry[1]
                        if name == item_name and isinstance(details, list):
                            for detail in details:
                                if isinstance(detail, dict) and "goals" in detail:
                                    goal_entries.append([goal_entry["goal"] for goal_entry in detail["goals"] if "goal" in goal_entry])

        if 0 <= skip < len(goal_entries):
            goals_list = goal_entries[skip]
        else:
            goals_list = ["No Requirements"] if not goal_entries else goal_entries[0]

        goals_cache[key] = (goals_list, forced_goals_list)
        return goals_cache[key]

    except (FileNotFoundError, json.JSONDecodeError):
        return (["Error loading requirements"], [])





class BundleItem(QWidget):
    def __init__(self, main_window, item_name):
        super().__init__()
        self.main_window = main_window
        self.item_name = item_name
        self.setWindowTitle("Bundle Selector")

        # Parse JSON and get the goals and number of slots
        goals, num_slots = self.find_goals_in_json(requirements_file_path, item_name)

        # Determine grid size
        num_pictures = len(goals)
        columns = min(6, num_pictures)  # Maximum of 6 columns
        rows = -(-num_pictures // columns)  # Ceiling division for rows
        second_row = 1

        if num_slots > 6:
            second_row = 2

        # Adjust window size based on the grid and overlay slots
        width = columns * 54
        height = (rows * 54 + 100 + second_row * 54 + 50)  # Extra height for the Submit button
        self.setGeometry(300, 300, width, height)

        # Main layout
        main_layout = QVBoxLayout()

        # Item name label at the top
        item_name_label = QLabel(item_name)
        item_name_label.setAlignment(Qt.AlignHCenter)  # Center horizontally
        item_name_label.setStyleSheet("font-size: 18px; font-weight: bold;")  # Bigger and bold text
        main_layout.addWidget(item_name_label, alignment=Qt.AlignTop)

        # Scroll area for buttons
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        grid_layout = QGridLayout(scroll_content)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)

        # Add buttons for pictures
        for index, goal in enumerate(goals):
            row = index // columns
            col = index % columns

            # Create button with picture
            picture_path = f"../Pictures/{goal.replace(' ', '_')}.png"
            button = QPushButton()
            button.setFixedSize(48, 48)
            button.setStyleSheet("border: none; margin: 3px;")  # Center with padding
            if os.path.exists(picture_path):
                pixmap = QPixmap(picture_path).scaled(48, 48, Qt.KeepAspectRatio)
                icon = QIcon(pixmap)
                button.setIcon(icon)
                button.setIconSize(QSize(48, 48))
            else:
                button.setText("")  # Fallback if image is missing

            # Connect button click to overlay functionality
            button.clicked.connect(lambda _, g=goal: self.add_to_overlay(g))

            grid_layout.addWidget(button, row, col)

        scroll_content.setLayout(grid_layout)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Overlay layout for selected pictures with support for up to 12 slots in two rows
        overlay_widget = QWidget()
        overlay_layout = QGridLayout(overlay_widget)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)

        # Determine the number of rows needed
        overlay_columns = 6
        overlay_rows = -(-num_slots // overlay_columns)  # Ceiling division for rows

        # Adjust window height for overlay rows
        height += (overlay_rows - 1) * 54  # Add extra height for additional rows beyond 1

        # Create slots dynamically
        self.overlay_slots = []
        self.selected_names = []  # To store the names of selected pictures

        for i in range(num_slots):
            row = i // overlay_columns
            col = i % overlay_columns

            slot_label = QLabel()
            slot_label.setFixedSize(54, 54)
            slot_label.setStyleSheet(f"border-image: url('../Pictures/Bundle_Background.png');")
            slot_label.setAlignment(Qt.AlignCenter)  # Center the image within the slot

            # Install event filter for right-click functionality
            slot_label.installEventFilter(self)

            self.overlay_slots.append(slot_label)
            overlay_layout.addWidget(slot_label, row, col)

        main_layout.addWidget(overlay_widget)

        # Submit button at the bottom
        submit_button = QPushButton("Submit")
        submit_button.setFixedHeight(40)
        submit_button.clicked.connect(self.submit_selection)
        main_layout.addWidget(submit_button)

        self.setLayout(main_layout)

        # Load previous selection if available
        self.load_previous_selection()

    def find_goals_in_json(self, file_path, item_name):
        """Search for item_name in the JSON file and return the list of goals and the number of slots."""
        goals = []
        num_slots = 6  # Default to 6 if not specified in JSON

        try:
            with open(file_path, 'r') as file:
                data = json.load(file)

            for category, entries in data.items():
                for entry in entries:
                    if entry[0] == item_name:
                        for condition in entry[1]:  # Iterate through conditions
                            is_bundle = any(extra.get("type") == "Bundle" for extra in condition.get("extra_info", []))
                            
                            if is_bundle:
                                for extra in condition.get("extra_info", []):
                                    if "goals_to_complete" in extra and "amount_of_goals" in extra:
                                        num_slots = extra["amount_of_goals"]  # Set slots to 'amount_of_goals'

                                if "goals" in condition:
                                    for goal_data in condition["goals"]:
                                        if "goal" in goal_data:
                                            goals.append(goal_data["goal"])  # Extract 'goal' names

        except Exception as e:
            print(f"Error reading JSON: {e}")

        return goals, num_slots

    def add_to_overlay(self, goal):
        """Add a picture corresponding to the goal to the overlay."""
        picture_path = f"../Pictures/{goal.replace(' ', '_')}.png"
        for slot in self.overlay_slots:
            if slot.pixmap() is None:  # Find the first empty slot
                if os.path.exists(picture_path):
                    pixmap = QPixmap(picture_path).scaled(42, 42, Qt.KeepAspectRatio)
                    slot.setPixmap(pixmap)
                    slot.setAlignment(Qt.AlignCenter)
                else:
                    slot.setText("No Image")
                # Add the goal name (without underscores and .png) to the list
                formatted_name = goal.replace('_', ' ')
                self.selected_names.append(formatted_name)
                break

    def load_previous_selection(self):
        """Load previously saved selection for the item_name."""
        try:
            with open(bundle_items_file_path, 'r') as file:
                data = json.load(file)
            if self.item_name in data:
                previous_selection = data[self.item_name]
                for goal in previous_selection:
                    self.add_to_overlay(goal)
        except Exception as e:
            print(f"Error loading previous selection: {e}")

    def submit_selection(self):
        """Save the selected items to the JSON file and close the window."""
        try:
            # Load existing data
            data = {}
            if os.path.exists(bundle_items_file_path):
                with open(bundle_items_file_path, 'r') as file:
                    data = json.load(file)

            # Update data with current selection
            data[self.item_name] = self.selected_names

            # Save updated data
            with open(bundle_items_file_path, 'w') as file:
                json.dump(data, file, indent=4)

        except Exception as e:
            print(f"Error saving selection: {e}")

        self.close()

    def eventFilter(self, source, event):
        """Handle right-click events for removing pictures."""
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                if source in self.overlay_slots:
                    slot_index = self.overlay_slots.index(source)
                    
                    if source.pixmap() is not None and slot_index < len(self.selected_names):
                        # Remove the corresponding name at the correct slot index
                        removed_name = self.selected_names.pop(slot_index)
                        
                        # Clear the slot's image
                        source.clear()

        return super().eventFilter(source, event)


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

# Load the data from the JSON file
data_file = data_file_path
all_major_data = load_data(data_file_path)

# Load config data from config.json
config_file = config_file_path
with open(config_file, 'r') as f:
    config_data = json.load(f)

from server_connection import connect_to_server, message_emitter, send_message_to_server
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

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QTabWidget
from PyQt5.QtCore import QTimer, QFileSystemWatcher
from PyQt5.QtGui import QPixmap
import asyncio

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

        # Connection Status Image & Connect Button
        connection_layout = QHBoxLayout()
        self.status_label = QLabel(self)
        connection_path = "../Pictures/Disconnected.png"
        pixmap = QPixmap(connection_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.status_label.setPixmap(QPixmap(pixmap))  # Default to Disconnected
        self.status_label.setFixedSize(16, 16)  # Adjust size as needed
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.start_server_connection)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(self.status_label)
        left_layout.addLayout(connection_layout)

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
        # Connect the connection status signal to update the UI
        message_emitter.connection_signal.connect(self.update_connection_status)



        # Enable Send button only if there’s text in message_input
        self.message_input.textChanged.connect(self.toggle_send_button)

    def update_connection_status(self, is_connected):
        """Updates the connection status image and button state."""

        # Update the connection status image
        image_path = "../Pictures/Connected.png" if is_connected else "../Pictures/Disconnected.png"
        pixmap = QPixmap(image_path).scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.status_label.setPixmap(pixmap)  # Update UI

        # Update button text and state
        if is_connected:
            self.connect_button.setText("Connected")
            self.connect_button.setEnabled(False)  # Disable button when connected
        else:
            self.connect_button.setText("Connect")
            self.connect_button.setEnabled(True)  # Enable button when disconnected

    def handle_file_change(self, changed_file):
        """
        Handle changes to watched files with a global QTimer debounce mechanism.
        """
        # Add the changed file to the pending actions set
        self.pending_server_file_actions.add(changed_file)

        if self.debounce_timer.isActive():
            remaining_time = self.debounce_timer.remainingTime()

        # Restart the timer
        self.debounce_timer.start(1000)

    def run_file_change_actions(self):
        """
        Execute actions for all pending files after debounce delay.
        """
        for changed_file in self.pending_server_file_actions:
            if changed_file == hint_my_location_file_path:
                self.populate_tabs_from_json()

            elif changed_file == hint_my_item_file_path:
                self.populate_tabs_from_json()

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
        """Save server address and slot name to config.json without removing existing 'season' key."""
        config_data = {}

        # Check if the file exists and load existing data
        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as f:
                try:
                    config_data = json.load(f)
                except json.JSONDecodeError:
                    pass  # Handle corrupted or empty JSON files gracefully

        # Update only the necessary fields
        config_data.update({"server_address": server_address, "slot_name": slot_name})

        # Write back the modified config
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

from PyQt5.QtWidgets import QLabel, QSizePolicy, QApplication
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QGuiApplication, QTextDocument

class HoverTooltip(QLabel):
    """Tooltip overlay widget for displaying information over other widgets."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: #444444; color: white; padding: 5px; font-size: 10pt;")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setTextFormat(Qt.RichText)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 

        # Force proper size calculation for long tooltips
        doc = QTextDocument()
        doc.setHtml(text)
        doc.setTextWidth(400)  # Set reasonable width
        self.resize(int(doc.idealWidth()), int(doc.size().height()))

        self.hide()

    def show_tooltip(self, pos):
        self.adjustSize()  # Ensure correct tooltip size before positioning
        self.resize(self.sizeHint())  # Explicitly resize to fit text

        # Find the screen that contains the tooltip position
        screen = QGuiApplication.screenAt(pos)
        if screen is None:
            screen = QGuiApplication.primaryScreen()  # Fallback to primary if detection fails
        screen_rect = screen.availableGeometry()

        tooltip_rect = self.frameGeometry()

        # Calculate how much it goes off the bottom
        overflow = (pos.y() + tooltip_rect.height()) - screen_rect.bottom()

        # If it goes off the bottom, move it up by that amount
        if overflow > 0:
            pos.setY(pos.y() - overflow)

        # Ensure tooltip does not go off the top of the screen
        if pos.y() < screen_rect.top():
            pos.setY(screen_rect.top())

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
        self.file_watcher.addPath(bundle_items_file_path)
        self.file_watcher.addPath(current_items_file_path)
        self.file_watcher.addPath(data_file_path)
        self.file_watcher.addPath(hint_my_location_file_path)

        # Call the setting_check method
        self.setting_check()

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

        self.update_friends()
        self.process_data_file_for_checked_locations()
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

        # Restart the timer
        self.debounce_timer.start(250)

    def run_file_change_actions(self):
        """
        Execute actions for all pending files after debounce delay.
        """
        for changed_file in self.pending_file_actions:
            if changed_file == current_items_file_path:
                self.update_recent_items()
                self.update_tab_names()
                self.update_elevator_floor_label()
                self.update_season_button_texts()
                self.update_all_background_colors()
                for skill in ["Combat", "Farming", "Fishing", "Foraging", "Mining"]:
                    self.refresh_skill_level(skill)

            elif changed_file == data_file_path:
                self.update_tab_names()
                self.process_data_file_for_checked_locations()

            elif changed_file == bundle_items_file_path:
                self.update_bundle_pictures()
                self.update_tab_names()
                self.update_all_background_colors()
                

            elif changed_file == hint_my_location_file_path:
                self.update_note_tab("t")
                self.update_tab_names()

        # Clear pending actions after execution
        self.pending_file_actions.clear()

    def setting_check(self):
        # Get the first YAML file in the folder
        yaml_files = [f for f in os.listdir(settings_folder) if f.endswith(".yaml")]
        if not yaml_files:
            return None

        first_yaml_file = os.path.join(settings_folder, yaml_files[0])

        # Read the YAML file
        with open(first_yaml_file, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        # Extract bundle_randomization value
        if "Stardew Valley" in data and "bundle_randomization" in data["Stardew Valley"]:
            bundle_randomization_value = data["Stardew Valley"]["bundle_randomization"]

            if bundle_randomization_value == "vanilla":
                # Load the vanilla bundle data (source)
                if os.path.exists(bundle_items_vanilla_file_path):
                    with open(bundle_items_vanilla_file_path, "r", encoding="utf-8") as file:
                        try:
                            new_data = json.load(file)
                        except json.JSONDecodeError:
                            print(f"Error loading JSON from {bundle_items_vanilla_file_path}. Aborting update.")
                            return
                else:
                    return

                # Load the existing bundle data (destination)
                if os.path.exists(bundle_items_file_path):
                    with open(bundle_items_file_path, "r", encoding="utf-8") as file:
                        try:
                            bundle_data = json.load(file)
                        except json.JSONDecodeError:
                            print(f"Error loading JSON from {bundle_items_file_path}. Resetting file.")
                            bundle_data = {}
                else:
                    bundle_data = {}

                # Update or add headers in the existing bundle data
                for key, value in new_data.items():
                    bundle_data[key] = value  # Replace if exists, add if missing

                # Write the modified JSON data back to the file
                with open(bundle_items_file_path, "w", encoding="utf-8") as file:
                    json.dump(bundle_data, file, indent=4)

    def process_data_file_for_checked_locations(self):
        """
        Process the data file, check the 5th field, and save the 4th field of matching entries
        to 'checked_location_detailed_file_path'. Additionally, include unmatched 4th fields
        from 'all_data.json'.
        """
        try:
            # Load the primary data file
            with open(data_file_path, 'r') as data_file:
                data = json.load(data_file)

            # Load the all_data file
            with open(all_data_file_path, 'r') as all_data_file:
                all_data = json.load(all_data_file)

            # Collect all matching 4th fields
            checked_locations = []
            data_fields = set(entry[3] for category in data.values() for entry in category if len(entry) >= 4) 
            
            # Add entries from data with 5th field equal to 1
            for category, items in data.items():
                for entry in items:
                    if len(entry) >= 5 and entry[4] == 1:
                        checked_locations.append(entry[3])  # Add 4th field to the list

            # Add unmatched fields from all_data
            for category, items in all_data.items():
                for entry in items:
                    if len(entry) >= 4 and entry[3] not in data_fields:
                        checked_locations.append(entry[3])

            # Prepare the JSON structure for detailed checked locations
            detailed_data = {"checked_locations": checked_locations}

            # Write the updated data to the file, replacing any previous content
            with open(checked_location_detailed_file_path, 'w') as json_file:
                json.dump(detailed_data, json_file, indent=4)

        except Exception as e:
            print(f"Error processing {data_file_path}: {e}")




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

    def create_friends_tab(self, tab_name, category_filter, spacing=0):
        """Create a special tab for friends with relationship level controls and separate birthday labels."""
        # Load the data from data.json
        with open(data_file_path, 'r') as f:
            data = json.load(f)
        
        # Parse unique friend names, birthdays, and their category
        friendsanity_data = data.get("Friendsanity", [])
        friends_with_birthdays = {}
        
        # Map category filter input
        if category_filter == "v":
            category_filter = "Villagers"
        elif category_filter == "b":
            category_filter = "Bachelor(ette)s"

        for entry in friendsanity_data:
            if len(entry) >= 3:  # Ensure the entry has enough fields
                name_with_level = entry[0]  # Example: "Pam 10 <3"
                birthday_info = entry[2]    # Example: "(Birthday: Spring 18)"
                name = name_with_level.split()[0]  # Extract the first word as the name
                
                # Check if this friend is already processed
                if name not in friends_with_birthdays:
                    # Add to the dictionary with default category and birthday
                    friends_with_birthdays[name] = {
                        "Birthday": birthday_info,
                        "Category": "Bachelor(ette)s"
                    }
                
                # Update the category to "Villagers" if any entry has a "10"
                if "10" in name_with_level:
                    friends_with_birthdays[name]["Category"] = "Villagers"

        # Filter friends based on the category_filter
        filtered_friends_with_birthdays = [
            (name, data["Birthday"], data["Category"])
            for name, data in friends_with_birthdays.items()
            if data["Category"] == category_filter or category_filter == "c"
        ]

        # Helper function to convert season and day to a sortable format
        def birthday_sort_key(birthday):
            season_order = {"Spring": 1, "Summer": 2, "Fall": 3, "Winter": 4}
            for season, order in season_order.items():
                if season in birthday:
                    day = int(''.join(filter(str.isdigit, birthday)))
                    return order * 100 + day
            return 1000000  # Default value if no season is found

        # Sort the friends by their birthday
        filtered_friends_with_birthdays.sort(key=lambda x: birthday_sort_key(x[1]))

        # Define birthday color mapping
        birthday_colors = {
            "Spring": "background-color: #344534; color: white;",
            "Summer": "background-color: #4f4300; color: white;",
            "Fall": "background-color: #633700; color: white;",
            "Winter": "background-color: #0a3054; color: white;"
        }

        # Create the main tab layout
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setAlignment(Qt.AlignTop)

        # Counter Label for Friends tab
        self.friends_counter_label = QLabel()
        main_layout.addWidget(self.friends_counter_label)

        # Create a scrollable area for the friends list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a widget for the scroll area
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignTop)

        # Grid layout for each friend
        friends_layout = QGridLayout()
        friends_layout.setAlignment(Qt.AlignTop)
        friends_layout.setVerticalSpacing(spacing)  # Set custom spacing

        for i, (friend, birthday, category) in enumerate(filtered_friends_with_birthdays):
            # Friend label
            friend_label = QLabel(f"{friend}:")
            
            # Birthday label with styling based on season
            season = next((key for key in birthday_colors if key in birthday), "Cat")
            birthday_label = QLabel(f"{birthday}")
            birthday_label.setStyleSheet(birthday_colors.get(season, "background-color: gray; color: white;"))

            # Retrieve the highest relationship level for the friend
            highest_level = self.get_friends_data(friend, tab_name)
            
            # Level label with styling
            level_label = QLabel(str(highest_level))
            level_font = level_label.font()
            level_font.setBold(True)
            level_label.setFont(level_font)
            
            completed_tab = False

            # Set color for level label
            if (category == "Bachelor(ette)s" and highest_level == 8) or (category == "Villagers" and highest_level == 10):
                level_label.setStyleSheet("background-color: #58adb8; color: black;")
                completed_tab = True
            else:
                level_label.setStyleSheet("color: white;")

            if friend == "Pet" and highest_level == 5:
                level_label.setStyleSheet("background-color: #58adb8; color: black;")
                completed_tab = True

            # Arrange the labels and level in the grid layout
            if completed_tab == True:
                if category_filter == "c":
                    friends_layout.addWidget(friend_label, i, 0, Qt.AlignTop)
                    friends_layout.addWidget(birthday_label, i, 1, Qt.AlignTop)
                    friends_layout.addWidget(level_label, i, 2, Qt.AlignTop)
            else:
                if category_filter != "c":
                    friends_layout.addWidget(friend_label, i, 0, Qt.AlignTop)
                    friends_layout.addWidget(birthday_label, i, 1, Qt.AlignTop)
                    friends_layout.addWidget(level_label, i, 2, Qt.AlignTop)

        scroll_layout.addLayout(friends_layout)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)
        tab.setLayout(main_layout)

        # Initialize the friends counter display
        self.update_friends_counter()

            # Check if the friends_layout is empty
        if friends_layout.count() == 0:
            return None  # Return None if the layout is empty (tab is blank)
        
        return tab


    def update_friends_counter(self):
        """Update the Friends tab counter label to show the checked items count."""
        total_checked = 0
        with open(data_file_path, 'r') as f:
            data = json.load(f)
        
        # Parse unique friend names and birthdays from the JSON data
        friendsanity_data = data.get("Friendsanity", [])
        total_entries = len(friendsanity_data)
        total_items = total_entries  # Total number of friends
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

            # Create a layout to hold the season images
            season_layout = QHBoxLayout()
            season_layout.setContentsMargins(0, 0, 0, 0)
            season_layout.setSpacing(2)

            # If no seasons are selected, consider it as all seasons
            if not item_seasons:
                item_seasons = ["Spring", "Summer", "Fall", "Winter"]

            # Define the order of seasons and corresponding images
            all_seasons = ["Spring", "Summer", "Fall", "Winter"]
            for season in all_seasons:
                season_label = QLabel()
                season_label.setFixedSize(24, 24)
                # Determine the image path
                if season in item_seasons:
                    season_image_path = f"../Pictures/{season}.png"
                else:
                    season_image_path = "../Pictures/Blank.png"
                # Set the image or fallback text
                if os.path.exists(season_image_path):
                    pixmap = QPixmap(season_image_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    season_label.setPixmap(pixmap)
                else:
                    season_label.setText("No Img")
                    season_label.setAlignment(Qt.AlignCenter)
                # Add the season label to the layout
                season_layout.addWidget(season_label)

            text_input = QLineEdit()
            text_input.setPlaceholderText(f"{item_info}")
            text_input.setText(f"{item_info}")

            fish = False

            def parse_time_ranges(time_text):
                # Define the hours from 6 AM to 2 AM
                hours = [f"{h}am" for h in range(6, 12)] + ["12pm"] + [f"{h}pm" for h in range(1, 12)] + ["12am", "1am", "2am"]

                # Initialize an array of zeros for each hour
                time_array = [0] * len(hours)

                # Extract individual times from input
                time_matches = re.findall(r'(\d{1,2})(am|pm)', time_text)
                time_pattern = tuple(f"{hour}{period}" for hour, period in time_matches)

                # Iterate through the hours and mark the array
                i = 0
                while i < len(time_pattern):
                    if i + 1 < len(time_pattern):
                        start_time, end_time = time_pattern[i], time_pattern[i + 1]
                        found_start = False

                        for j, hour in enumerate(hours):
                            if hour == start_time:
                                time_array[j] = 1  # Mark the start
                                found_start = True
                            elif found_start:
                                if hour == end_time:  # Stop marking before `end_time`
                                    break
                                time_array[j] = 1  # Mark everything between 1 and 2

                    i += 2  # Move to the next time range

                return time_array

            # **New Block: Add 21 images for "Fishsanity" with Time Filtering**
            if tab_name == "Fishsanity":
                time_sequence = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1]  # Defined sequence

                # Extract ordered time array from `text_input`
                ordered_time_array = parse_time_ranges(text_input.text())

                # Perform bitwise operation: replace time with 0 if ordered_time_array is 0
                masked_time_sequence = [time_sequence[i] if ordered_time_array[i] == 1 else 0 for i in range(len(time_sequence))]

                fishsanity_layout = QHBoxLayout()
                fishsanity_layout.setContentsMargins(0, 0, 0, 0)
                fishsanity_layout.setSpacing(0)

                for i, number in enumerate(masked_time_sequence):  # Use the masked sequence
                    # Determine correct image path based on time range
                    if number == 0:
                        image_path = "../Pictures/Blank.png"
                    elif 1 <= number and 6 <= i <= 17:  # 1PM - 12PM range
                        image_path = f"../Pictures/Time_{number}_PM.png"
                    else:
                        image_path = f"../Pictures/Time_{number}.png"

                    fish_image_label = QLabel()
                    fish_image_label.setFixedSize(18, 18)  # Keep consistent size

                    if os.path.exists(image_path):
                        pixmap = QPixmap(image_path).scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        fish_image_label.setPixmap(pixmap)
                    else:
                        fish_image_label.setText(f"{number}")  # Fallback: Display number if image is missing
                        fish_image_label.setAlignment(Qt.AlignCenter)

                    fishsanity_layout.addWidget(fish_image_label)

                fish = True

                weather_paths = {
                    "Sun": "../Pictures/StatusSun.png",
                    "Rain": "../Pictures/StatusRain.png",
                    "Blank": "../Pictures/Blank.png"
                }

                weather_conditions = text_input.text()
                is_sunny = "Sun" in weather_conditions
                is_rainy = "Rain" in weather_conditions

                for condition in ["Sun", "Rain"]:
                    weather_image_label = QLabel()
                    weather_image_label.setFixedSize(34, 24)

                    image_path = weather_paths["Blank"]
                    if (condition == "Sun" and is_sunny) or (condition == "Rain" and is_rainy):
                        image_path = weather_paths[condition]

                    if os.path.exists(image_path):
                        pixmap = QPixmap(image_path).scaled(34, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        weather_image_label.setPixmap(pixmap)

                    fishsanity_layout.addWidget(weather_image_label)

                def extract_final_part(text_input):
                    # Remove everything between the first and second sets of parentheses
                    cleaned_text = re.sub(r"^\(.*?\) \(.*?\) ", "", text_input)
                    return cleaned_text
                
                item_info = extract_final_part(item_info)

                text_input = QLineEdit()
                text_input.setPlaceholderText(f"{item_info}")
                text_input.setText(f"{item_info}")


            else:
                matching_extra_info = next((extra_info for extra_info in extra_info_array if extra_info["checkbox_text"] == item_id), None)
                if matching_extra_info:
                    text_input.setText(matching_extra_info["extra_info_input"])

                text_input.textChanged.connect(lambda _, cb_text=item_id, text=text_input: 
                                                self.update_extra_info_array(cb_text, text.text()))

            hint_input = QLineEdit()
            hint_input.setPlaceholderText("Insert Item on Check")
            hint_input.setFixedWidth(220)
            
            with open(requirements_file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Get extra_info for the current item_name
            extra_info = self.get_extra_info_for_item(requirements_file_path, item_name, "extra_info")
            all_goals = self.get_extra_info_for_item(requirements_file_path, item_name, "goals")

            # Check if the item is of type "Bundle"
            is_setting = any(info.get("type") == "Setting" for info in extra_info)

            # Button for opening the new window with an image
            open_window_button = QPushButton()
            open_window_button.setFixedSize(24, 24)  # Adjust button size to fit the image
            if is_setting:
                picture_path = "../Pictures/Advanced_Options_Button.png"
            else:
                picture_path = "../Pictures/Golden_Scroll.png"

            if os.path.exists(picture_path):
                pixmap = QPixmap(picture_path).scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon = QIcon(pixmap)
                open_window_button.setIcon(icon)
                open_window_button.setIconSize(QSize(24, 24))
            else:
                open_window_button.setText("[!]")  # Fallback if image is missing

            # Connect the button to open the new window
            open_window_button.clicked.connect(lambda _, name=item_name: self.open_new_window(name))

            matching_note = next((note for note in notes_array if note["checkbox_text"] == item_id), None)
            if matching_note:
                hint_input.setText(matching_note["hint_input"])
                
            is_bundle = any(info.get("type") == "Bundle" for info in extra_info)
            amount_of_goals = next((info.get("amount_of_goals") for info in extra_info if "amount_of_goals" in info), None)
            current_goals_return = len([info.get("goal") for info in all_goals if "goal" in info])

            # Add checkbox to the list of checkboxes
            checkboxes.append(checkbox)
            bundle_pictures = []
            
            with open(bundle_items_file_path, "r", encoding="utf-8") as file:
                bundle_data = json.load(file)

            if item_name in bundle_data:
                bundle_pictures = [f"../Pictures/{item.replace(' ', '_')}.png" for item in bundle_data[item_name]]

            picture_layout = QHBoxLayout()
            picture_layout.setContentsMargins(0, 0, 0, 0)
            picture_layout.setSpacing(0)

            if is_bundle:
                # Load bundle_items.json
                with open(bundle_items_file_path, "r") as file:
                    bundle_items = json.load(file)

                # Check if amount_of_goals == current_goals_return
                if amount_of_goals == current_goals_return:
                    # Extract all goals correctly
                    goals_list = [goal_info["goal"] for goal_info in all_goals]

                    # Replace the entry in bundle_items.json under the item_name header
                    bundle_items[item_name] = goals_list  # Overwrites the previous value

                    # Save the updated JSON
                    with open(bundle_items_file_path, "w") as file:
                        json.dump(bundle_items, file, indent=4)



                self.update_bundle_pictures()


                item_entry = {
                    'widget': item_widget,
                    'checkbox_text': checkbox_text,
                    'read_only_input': read_only_input,
                    'text_input': text_input,
                    'hint_input': hint_input,
                    'checkbox': checkbox,
                    'item_id': item_id,
                    'picture_layout': picture_layout
                }

                item_widgets.append(item_entry)

                spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

            # Add all widgets to layout
            item_layout.addWidget(checkbox)
            item_layout.addWidget(checkbox_text)
            item_layout.addLayout(season_layout)
            if fish:
                item_layout.addLayout(fishsanity_layout)
            if is_bundle:
                item_layout.addWidget(open_window_button)
                item_layout.addLayout(picture_layout)
                item_layout.addItem(spacer)
            if is_setting:
                item_layout.addWidget(open_window_button)
            if not is_bundle:
                item_layout.addWidget(text_input)
            item_layout.addWidget(hint_input)
            scroll_layout.addWidget(item_widget)

            hint_input.textChanged.connect(lambda text, sa=scroll_area, cb_widget=checkbox_text:
                                            self.adjust_scroll_position(sa, cb_widget))

            hint_input.editingFinished.connect(lambda cb_text=item_id, hint=hint_input, tab=tab_name: 
                                            self.update_notes_array(cb_text, hint.text(), tab))


            checkbox.stateChanged.connect(lambda state, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text: 
                                        self.update_background_color(state, ct, ro, ti, hi, st))
            hint_input.textChanged.connect(lambda _, cb=checkbox, ct=checkbox_text, ro=read_only_input, ti=text_input, hi=hint_input, st=season_text:
                                        self.update_background_color(cb.checkState(), ct, ro, ti, hi, st))

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
                'item_id': item_id,
                'picture_layout': picture_layout
            })

        self.all_item_widgets[tab_name] = item_widgets
        layout.addWidget(scroll_area)
        self.update_counter(checkboxes, tab_name)
        counter_label.setText(f"{len([cb for cb in checkboxes if cb.isChecked()])} / {len(checkboxes)} items checked")

        return tab
    
    def update_bundle_pictures(self):
        """
        Refreshes all bundle pictures across all tabs.
        Each picture becomes a button that toggles its goal in bundle_items.json.
        If a goal is in logic, its background is #58adb8 and the image is grayed out.
        If a goal is not in logic, its background is #b85858 and the image is normal.
        """

        # Set size variables
        ICON_SIZE = 32  # Size of the main image
        CHECKMARK_SIZE = 32  # Size of the checkmark
        BUTTON_SIZE = ICON_SIZE  # Button should match icon size

        # Load the latest bundle_items.json data
        with open(bundle_items_file_path, "r", encoding="utf-8") as file:
            bundle_data = json.load(file)

        # Checkmark overlay icon path
        checkmark_path = "../Pictures/Check_Mark.png"

        def toggle_goal(item_name, goal, button):
            """Function to toggle goal in bundle_items.json"""
            with open(bundle_items_file_path, "r", encoding="utf-8") as file:
                bundle_data = json.load(file)

            checked_key = f"{item_name} | CHECKED"
            if checked_key not in bundle_data:
                bundle_data[checked_key] = []

            if goal in bundle_data[checked_key]:
                bundle_data[checked_key].remove(goal)  # Remove if exists
            else:
                bundle_data[checked_key].append(goal)  # Add if not exists

            # Save back to JSON
            with open(bundle_items_file_path, "w", encoding="utf-8") as file:
                json.dump(bundle_data, file, indent=4)

            # Update button icon
            update_button_icon(button, goal, item_name)

        def update_button_icon(button, goal, item_name):
            """Updates the button icon with the checkmark if checked and applies background color + grayscale."""
            checked_key = f"{item_name} | CHECKED"
            in_logic_key = f"{item_name} | IN LOGIC"
            
            checked_goals = bundle_data.get(checked_key, [])
            in_logic_goals = bundle_data.get(in_logic_key, [])

            picture_path = f"../Pictures/{goal.replace(' ', '_')}.png"

            # Set background color based on logic status
            if goal in in_logic_goals:
                button.setStyleSheet("background-color: #58adb8; border: none;")  # In logic (teal)
            else:
                button.setStyleSheet("background-color: #b85858; border: none;")  # Not in logic (red)

            if os.path.exists(picture_path):
                pixmap = QPixmap(picture_path).scaled(ICON_SIZE, ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                pixmap = QPixmap(ICON_SIZE, ICON_SIZE)  # Placeholder if image doesn't exist

            # Apply grayscale if the goal is in logic
            if goal not in in_logic_goals:
                gray_pixmap = QPixmap(pixmap.size())
                gray_pixmap.fill(Qt.transparent)

                painter = QPainter(gray_pixmap)
                painter.setOpacity(0.5)  # Reduce opacity (grayscale effect)
                painter.drawPixmap(0, 0, pixmap)
                painter.end()

                pixmap = gray_pixmap  # Replace with grayed-out version

            # If goal is checked, overlay the checkmark
            if goal in checked_goals and os.path.exists(checkmark_path):
                checkmark = QPixmap(checkmark_path).scaled(CHECKMARK_SIZE, CHECKMARK_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                # Overlay the checkmark onto the image
                combined_pixmap = QPixmap(ICON_SIZE, ICON_SIZE)
                combined_pixmap.fill(Qt.transparent)

                painter = QPainter(combined_pixmap)
                painter.drawPixmap(0, 0, pixmap)  # Draw main image
                painter.drawPixmap(ICON_SIZE - CHECKMARK_SIZE, ICON_SIZE - CHECKMARK_SIZE, checkmark)  # Position bottom-right
                painter.end()

                button.setIcon(QIcon(combined_pixmap))
            else:
                button.setIcon(QIcon(pixmap))

            button.setIconSize(QSize(ICON_SIZE, ICON_SIZE))

        # Iterate through all items in all tabs
        for tab_name, item_widgets in self.all_item_widgets.items():
            for item in item_widgets:
                if not isinstance(item, dict):
                    continue  # Skip invalid items

                item_name = item["checkbox_text"].text()

                # Ensure the item exists in bundle_items.json and has a picture layout
                if item_name in bundle_data and "picture_layout" in item:
                    picture_layout = item["picture_layout"]

                    # Remove existing buttons
                    while picture_layout.count():
                        widget = picture_layout.takeAt(0).widget()
                        if widget:
                            widget.deleteLater()

                    # Get updated picture paths
                    bundle_pictures = [(goal, f"../Pictures/{goal.replace(' ', '_')}.png") for goal in bundle_data.get(item_name, [])]

                    # Create buttons for each picture
                    for goal, picture_path in bundle_pictures:
                        button = QPushButton()
                        button.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)  # Ensure button matches icon size

                        update_button_icon(button, goal, item_name)  # Set initial icon

                        button.clicked.connect(lambda _, i=item_name, g=goal, b=button: toggle_goal(i, g, b))  # Bind click event
                        picture_layout.addWidget(button)

                    # Force UI update
                    picture_layout.update()

                with open(requirements_file_path, "r", encoding="utf-8") as req_file:
                    requirements_data = json.load(req_file)
                    
                TEXT_FONT_SIZE = 14  # User can change this value to adjust the text size
                TEXT_FONT_FAMILY = "Stardew Valley Stonks"  # Pixelated font choice
                TEXT_BACKGROUND_IMAGE = "../Pictures/label_background.png"  # Path to the background image
                BACKGROUND_IMAGE_WIDTH = 56  # Editable width of the background image
                BACKGROUND_IMAGE_HEIGHT = 100  # Editable height of the background image
                
                item_name = item["checkbox_text"].text()
                if item_name in bundle_data and "picture_layout" in item:
                    picture_layout = item["picture_layout"]

                    checked_items = len(bundle_data.get(f"{item_name} | CHECKED", []))

                    goals_to_complete = 0
                    for category, items in requirements_data.items():
                        for entry in items:
                            if entry[0] == item_name:
                                # Iterate through ALL conditions in entry[1], not just the first one
                                for condition in entry[1]:
                                    extra_info = condition.get("extra_info", [])
                                    
                                    # Find the first 'Bundle' type and get its 'goals_to_complete'
                                    for info in extra_info:
                                        if isinstance(info, dict) and info.get("type") == "Bundle" and "goals_to_complete" in info:
                                            goals_to_complete = info["goals_to_complete"]
                                            break  # Stop once we find the correct 'Bundle' entry


                    # Create a QLabel with a background pixmap
                    label = QLabel()
                    pixmap = QPixmap(TEXT_BACKGROUND_IMAGE).scaled(BACKGROUND_IMAGE_WIDTH, BACKGROUND_IMAGE_HEIGHT, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                    painter = QPainter(pixmap)
                    painter.setFont(QFont(TEXT_FONT_FAMILY, TEXT_FONT_SIZE, QFont.Bold))
                    painter.setPen(QColor(0, 0, 0))

                    rect = pixmap.rect()
                    rect.moveTop(rect.top() + 1)  # Move text down by offset
                    painter.drawText(rect, Qt.AlignCenter, f"{checked_items}/{goals_to_complete}")
                    painter.end()

                    label.setPixmap(pixmap)
                    picture_layout.addWidget(label)

        self.update()
    
    def get_extra_info_for_item(self, file_path, item_name, word):
        """Searches the JSON file for the given item_name and returns all extra_info fields."""
        try:
            with open(file_path, 'r', encoding="utf-8") as file:
                data = json.load(file)

            extra_info_list = []  # List to store all extra_info entries

            # Iterate through all categories
            for category, entries in data.items():
                for entry in entries:
                    if entry[0] == item_name:  # Check if the item_name matches
                        for condition in entry[1]:  # Iterate through conditions
                            if word in condition:
                                extra_info_list.extend(condition[word])  # Collect all extra_info

            return extra_info_list

        except Exception as e:
            print(f"Error reading JSON: {e}")
            return []
    
    def open_new_window(self, item_name):
        """Create a new BundleItem window for the given item_name."""
        # Keep track of multiple windows
        if not hasattr(self, "bundle_windows"):
            self.bundle_windows = []

        new_window = BundleItem(self, item_name)
        self.bundle_windows.append(new_window)
        new_window.show()
        new_window.raise_()


    
    def print_modified_checkbox(self, checkbox_text):
        """
        Print the checkbox text of the modified hint_input.
        Args:
            checkbox_text: The text of the associated checkbox.
        """
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

    from PyQt5.QtCore import QTimer

    def update_tab_names(self):
        """Update the tab names with the count of in-logic items in a non-blocking manner."""
        global tab_name_mapping
        tab_name_mapping = {}  # Clear the mapping

        current_tab_names = [self.main_tabs.tabText(i).split("\n")[0] for i in range(self.main_tabs.count())]

        ordered_internal_names = [
            internal_name
            for display_name in current_tab_names
            for internal_name, mapped_name in tab_display_names.items()
            if mapped_name == display_name
        ]

        self._tab_update_queue = list(enumerate(ordered_internal_names))  # Store tabs in a queue
        self._update_timer = QTimer()
        self._update_timer.setInterval(50)  # Adjust delay (e.g., 50ms per tab)
        self._update_timer.timeout.connect(self._update_next_tab)
        self._update_timer.start()

    def _update_next_tab(self):
        """Process one tab per timer cycle to avoid UI lag."""
        if not self._tab_update_queue:
            self._update_timer.stop()
            self.update_all_background_colors()
            return  # Stop timer when all tabs are updated

        i, internal_tab_name = self._tab_update_queue.pop(0)  # Get next tab to update

        tab_widget_page = self.main_tabs.widget(i)
        if not tab_widget_page:
            return

        display_name = tab_display_names.get(internal_tab_name, internal_tab_name)

        # Fetch counts once per tab
        """Count the items that are in logic and not yet completed."""
        in_logic_count = 0
        items = all_major_data.get(internal_tab_name, [])

        all_completed = True
        for item in items:
            item_state = item[4]  # Check the completed state
            item_name = item[0]  # Get Item Name

            if item_state == 0:
                all_completed = False

            #item_in_logic = self.cached_get_requirements(item_name)
            item_in_logic = get_requirements(item_name, "color")
            if item_in_logic not in {"Red", "Pink"} and item_state == 0:
                in_logic_count += 1
            
            self._update_timer.setInterval(50)

        hinted_count = self.count_hinted_items(internal_tab_name)
        new_display_name = f"{display_name}\n({in_logic_count}|{hinted_count})"

        if all_completed == True:
            new_display_name = f"{display_name}\nDONE"

        # Only update if the name has changed
        if self.main_tabs.tabText(i) != new_display_name:
            self.main_tabs.setTabText(i, new_display_name)
            self.main_tabs.tabBar().setTabButton(i, QTabBar.RightSide, QLabel(f"\n"))

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

    def update_notes_array(self, checkbox_text, hint_text, explicit_tab_name=None):
        """Update or add an entry in notes.json based on checkbox_text."""
        notes_array = self.load_hint_my_location()

        check_found = self.is_found(checkbox_text)

        # Check if the note already exists, and update it if so
        for note in notes_array:
            if note["checkbox_text"] == checkbox_text:
                note["hint_input"] = hint_text
                note["class"] = "Unknown"
                note["state"] = check_found
                note["tab"] = explicit_tab_name  # Use the explicitly passed tab
                break
        else:
            # Add new entry if no match is found
            notes_array.append({
                "checkbox_text": checkbox_text,
                "hint_input": hint_text,
                "class": "Unknown",
                "state": check_found,
                "tab": explicit_tab_name  # Use the explicitly passed tab
            })

        # Save the updated notes array
        self.save_hint_my_location_to_file(notes_array)


    def is_found(self, checkbox_text):
        """Check if the checkbox_text exists in the file and return 'found' or 'not found'."""
        # Load data from file
        with open(data_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Iterate through all sections of the data
        for category, entries in data.items():
            for entry in entries:
                # The first field (entry[0]) is the name we are searching for
                if entry[0] == checkbox_text:
                    # Check the fifth field (index 4)
                    return "found" if entry[4] == 1 else "not found"

        # If not found, return "not found"
        return "not found"
         

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
                    self.update_friends()
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

    def update_friends(self):
                # Store the currently selected tab index and scroll positions
        current_tab_index = self.friends_tabs.currentIndex()
        tab_names = ["Bachelor(ette)s", "Villagers", "Completed"]
        scroll_positions = {
            tab_names[i]: self.friends_tabs.widget(i).findChild(QScrollArea).verticalScrollBar().value()
            for i in range(self.friends_tabs.count())
        }

        # Remove and recreate the Friends tabs
        self.friends_tabs.clear()  # Clear all tabs to reset
        for tab_type, tab_name in zip(["b", "v", "c"], tab_names):
            # Create the tab content
            new_tab_content = self.create_friends_tab("Friendsanity", tab_type)

            # Check if the tab is blank (no children or items)
            if new_tab_content is None:
                continue

            # Add non-blank tabs
            self.friends_tabs.addTab(new_tab_content, tab_name)

        # Restore the previously selected tab and scroll positions if the tab still exists
        if current_tab_index < self.friends_tabs.count():
            self.friends_tabs.setCurrentIndex(current_tab_index)
        for i in range(self.friends_tabs.count()):
            tab_name = tab_names[i]
            new_scroll_area = self.friends_tabs.widget(i).findChild(QScrollArea)
            if new_scroll_area and tab_name in scroll_positions:
                new_scroll_area.verticalScrollBar().setValue(scroll_positions[tab_name])


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
                
                tooltip_text = get_requirements(item_name, "text")
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

        not_in_logic = get_requirements(checkbox_text.text(), "color")
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

        if data_key in self.all_item_widgets:
            for item in self.all_item_widgets[data_key]:

                checkbox = item['checkbox']
                checkbox_text = item['checkbox_text']
                read_only_input = item['read_only_input']
                text_input = item['text_input']
                hint_input = item['hint_input']
                season_text = read_only_input.text()

                self.update_background_color(
                    checkbox.checkState(), checkbox_text, read_only_input, text_input, hint_input, season_text
                )


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
        new_all_major_data = load_data(data_file_path)

            # Step 1: Define the reset structure for data.json
        reset_data_structure = {
            "Crafts Room": [],
            "Pantry": [],
            "Fish Tank": [],
            "Bulletin Board": [],
            "Vault": [],
            "Boiler Room": [],
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

        self.write_to_file(all_locations_file_path, "{\"all_locations\": [],\"missing_locations\": []}")
        self.write_to_file(bundle_items_file_path, "{}")
        self.write_to_file(checked_location_file_path, "{\"checked_locations\": []}")
        self.write_to_file(checked_location_detailed_file_path, "{\"checked_locations\": []}")
        self.write_to_file(current_items_file_path, "{\"current_items\": []}")
        self.write_to_file(extra_info_file_path, "[]")
        self.write_to_file(hint_my_item_file_path, "[]")
        self.write_to_file(hint_my_location_file_path, "[]")
        self.write_to_file(notes_file_path, "\"\"")
        self.write_to_file(player_table_file_path, "{\"players\": []}")

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

        
    def write_to_file(self, file_path: str, content: str) -> None:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)


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