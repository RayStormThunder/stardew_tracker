import sys
import json
import re
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLineEdit, QLabel, QScrollArea, QGroupBox, QPushButton, QListWidget,
    QSpinBox, QComboBox, QGridLayout, QTextEdit, QListWidgetItem
)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal

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

# Define a mapping from tab display names to data keys
tab_name_mapping = {
    "Bundles": "Bundles",
    "Crops": "Cropsanity",
    "Fish": "Fishsanity",
    "Special Orders": "Ordersanity",
    "Quests": "Questsanity",
    "Travelling Cart": "Cartsanity",
    "Robin's Blueprints": "Blueprintsanity",
    "Clint's Upgrades": "Upgradesanity",
    "Gus' Recipes": "Chefsanity",
    "Misc": "Misc"
}

data_file_path = "../JSONStore/data.json"
config_file_path = "../JSONStore/config.json"
hint_file_path = "../JSONStore/hints.json"
checked_location_file_path = "../JSONStore/checked_location.json"
bundle_list_file_path = "../JSONPull/bundle_list.json"

# Load the data from the JSON file
data_file = data_file_path
data = load_data(data_file)

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
        self.tab_widget.addTab(self.locations_tab, "Locations for checks")
        self.tab_widget.addTab(self.items_tab, "Hinted Items")
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

    def auto_track(self):
        """Automatically track checked locations and update data.json."""
        # Load checked locations from JSON
        try:
            with open(checked_location_file_path, 'r') as checked_file:
                checked_data = json.load(checked_file)["checked_locations"]
        except (FileNotFoundError, json.JSONDecodeError):
            print("Error: checked_location.json file not found or could not be decoded.")
            return
        
        # Load data.json
        data_updated_count = 0
        for tab_name, items in data.items():
            for item in items:
                # Check if the 4th field matches any location in checked_data
                if item[3] in checked_data:
                    if item[4] != 1:  # Only update if it's not already set
                        item[4] = 1
                        data_updated_count += 1
        
        # Save updated data.json
        save_data(data_file, data)
        
        # Print the number of updated fields
        print(f"Auto-track completed: {data_updated_count} fields changed to 1.")

        # Call update_all to refresh UI components and counters in MainWindow
        self.main_window.update_all()

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

class BundlesWindow(QWidget):
    bundles_selected = pyqtSignal(dict)  # Signal to send selected bundles to main window

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bundles")
        self.setGeometry(200, 100, 600, 400)
        self.setFixedSize(1200, 900)  # Set a fixed maximum size for the window
        
        self.room_selections = {}  # Track selections per room
        main_layout = QVBoxLayout(self)

        # Load the bundle data
        bundle_data = load_data(bundle_list_file_path)

        # Create a "Pick Bundles" button, initially disabled
        self.pick_bundles_button = QPushButton("Pick Bundles")
        self.pick_bundles_button.setEnabled(False)
        self.pick_bundles_button.clicked.connect(self.pick_bundles)
        main_layout.addWidget(self.pick_bundles_button)

        # Create scroll area for the room checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        # Create checkboxes and track selection per room
        for room_name, bundles in bundle_data.items():
            match = re.search(r'(\d+)$', room_name)
            max_selectable = int(match.group(1)) if match else 0
            room_name_clean = re.sub(r'_\d+$', '', room_name).replace('_', ' ')

            self.room_selections[room_name_clean] = {
                'max': max_selectable,
                'selected': 0,
                'checkboxes': []
            }

            room_label = QLabel(f"<b>{room_name_clean} (Max {max_selectable})</b>")
            scroll_layout.addWidget(room_label)

            selected_count = 0
            for index, bundle in enumerate(bundles):
                checkbox = QCheckBox(f"{bundle[0]}: {bundle[2]}")
                scroll_layout.addWidget(checkbox)

                # Select initial checkboxes up to max
                if selected_count < max_selectable:
                    checkbox.setChecked(True)
                    selected_count += 1
                    self.room_selections[room_name_clean]['selected'] += 1

                # Connect the checkbox state change
                checkbox.stateChanged.connect(lambda state, rn=room_name_clean, cb=checkbox: self.update_selection(rn, cb, state))
                self.room_selections[room_name_clean]['checkboxes'].append(checkbox)

            if selected_count >= max_selectable:
                for cb in self.room_selections[room_name_clean]['checkboxes'][max_selectable:]:
                    cb.setEnabled(False)

        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        self.check_pick_bundles_enabled()

    def update_selection(self, room_name, checkbox, state):
        room_data = self.room_selections[room_name]
        if state == Qt.Checked:
            if room_data['selected'] < room_data['max']:
                room_data['selected'] += 1
            if room_data['selected'] >= room_data['max']:
                for cb in room_data['checkboxes']:
                    if not cb.isChecked():
                        cb.setEnabled(False)
        else:
            room_data['selected'] -= 1
            for cb in room_data['checkboxes']:
                cb.setEnabled(True)

        self.check_pick_bundles_enabled()

    def check_pick_bundles_enabled(self):
        """Enable 'Pick Bundles' if all rooms meet their max selection requirements."""
        all_rooms_selected = all(
            room_data['selected'] == room_data['max'] for room_data in self.room_selections.values()
        )
        self.pick_bundles_button.setEnabled(all_rooms_selected)

    def pick_bundles(self):
        """Gather selections, emit signal, and close window."""
        selected_bundles = {}
        for room_name, room_data in self.room_selections.items():
            selected_bundles[room_name] = [
                cb.text().split(":")[0] for cb in room_data['checkboxes'] if cb.isChecked()
            ]
        self.bundles_selected.emit(selected_bundles)
        self.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize attributes for secondary windows
        self.server_window = None  # Track the server window instance
        self.bundles_window = None  # Initialize bundles_window to None to avoid AttributeError
        
        # Set up the main layout
        self.setWindowTitle("Stardew Check Tracker")
        self.setGeometry(300, 100, 1600, 800)
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
        for season in ["Spring", "Summer", "Fall", "Winter"]:
            button = QPushButton(season)
            button.setCheckable(True)
            button.setStyleSheet("background-color: #4c5052;")  # Default color when not selected
            button.clicked.connect(lambda _, s=season, b=button: self.filter_by_season(s, b))
            self.season_buttons.append(button)
            season_layout.addWidget(button)
        main_layout.addLayout(season_layout)

        # Bundles Button
        bundles_button = QPushButton("Bundles")
        bundles_button.clicked.connect(self.open_bundles_window)
        top_bar_layout.addWidget(bundles_button)

        # Create tab widgets for Main, Skills, Mines, and Friends sections
        self.main_tabs = QTabWidget()
        self.skills_tabs = QTabWidget()
        self.mines_tabs = QTabWidget()
        self.friends_tabs = QTabWidget()
        
        # Counter labels for each tab set
        self.counter_labels = {}
        self.total_checkboxes = 0
        self.total_checked = 0

        # Define tab groups
        tab_display_names = {
            "Bundles": "Bundles", "Cropsanity": "Crops", "Fishsanity": "Fish",
            "Ordersanity": "Special Orders", "Questsanity": "Quests", 
            "Cartsanity": "Travelling Cart", "Blueprintsanity": "Robin's Blueprints",
            "Upgradesanity": "Clint's Upgrades", "Chefsanity": "Gus' Recipes", "Festivalsanity": "Festivals", "Misc": "Misc"
        }
        skills_tab_name = "Skillsanity"
        mines_tab_name = "Elevatorsanity"
        friends_tab_name = "Friendsanity"

        # Add main tabs dynamically
        for tab_name, display_name in tab_display_names.items():
            items = data.get(tab_name, [])
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

        # Close the Bundles Window if it's open
        if self.bundles_window is not None:
            self.bundles_window.close()

        # Ensure the server thread is terminated if it's still running
        if self.server_window and hasattr(self.server_window, 'server_thread') and self.server_window.server_thread:
            self.server_window.server_thread.terminate()
            self.server_window.server_thread.wait()

        event.accept()  # Accept the close event to proceed with window closing

    def update_all(self):
        """Call all update functions to refresh counters and UI components."""

        # Define tab names for easy reference
        skills_tab_name = "Skillsanity"
        mines_tab_name = "Elevatorsanity"
        friends_tab_name = "Friendsanity"

        # Define tab groups
        tab_display_names = {
            "Bundles": "Bundles", "Cropsanity": "Crops", "Fishsanity": "Fish",
            "Ordersanity": "Special Orders", "Questsanity": "Quests", 
            "Cartsanity": "Travelling Cart", "Blueprintsanity": "Robin's Blueprints",
            "Upgradesanity": "Clint's Upgrades", "Chefsanity": "Gus' Recipes", "Festivalsanity": "Festivals", "Misc": "Misc"
        }

        # Update the global counter
        self.update_global_counter()

        # Remove old tabs from the main tabs
        while self.main_tabs.count() > 0:
            self.main_tabs.removeTab(0)

        # Remove old tabs if they exist
        if self.skills_tabs.count() > 0:
            self.skills_tabs.removeTab(0)
        if self.mines_tabs.count() > 0:
            self.mines_tabs.removeTab(0)
        if self.friends_tabs.count() > 0:
            self.friends_tabs.removeTab(0)

        # Recreate and add new tabs
        self.skills_tabs.addTab(self.create_skills_tab(skills_tab_name), "Skills")
        self.mines_tabs.addTab(self.create_mines_tab(mines_tab_name), "Mines")
        self.friends_tabs.addTab(self.create_friends_tab(friends_tab_name), "Friends")
        for tab_name, display_name in tab_display_names.items():
            items = data.get(tab_name, [])
            self.total_checkboxes += len(items)
            self.main_tabs.addTab(self.create_tab(tab_name, items), display_name)

    def open_server_window(self):
        """Open a separate window for server connection and console."""
        if self.server_window is None:
            self.server_window = ServerWindow(self)  # Pass self to ServerWindow
        self.server_window.show()

    def open_bundles_window(self):
        """ Open the bundles selection window and connect signal """
        self.bundles_window = BundlesWindow()
        self.bundles_window.bundles_selected.connect(self.update_bundles_data)
        self.bundles_window.show()

    def update_bundles_data(self, selected_bundles):
        """Update data.json with selected bundles in the correct order and refresh the Bundles tab UI."""
        # Load existing data and bundle list
        data = load_data(data_file)
        with open(bundle_list_file_path, 'r') as f:
            bundle_list = json.load(f)

        # Define main completion items and initialize a dictionary for organized insertion
        main_completion_items = {
            "Boiler Room": "Complete Boiler Room",
            "Bulletin Board": "Complete Bulletin Board",
            "Crafts Room": "Complete Crafts Room",
            "Fish Tank": "Complete Fish Tank",
            "Pantry": "Complete Pantry",
            "Vault": "Complete Vault"
        }
        
        # Start fresh with only the main completion items in the Bundles list
        data['Bundles'] = [[name, [], "", name, 0] for name in main_completion_items.values()]

        # Organize bundles under their corresponding completion items
        for room_name, bundle_names in selected_bundles.items():
            # Find the correct key in bundle_list.json that matches the room name
            matched_room_key = None
            for key in bundle_list.keys():
                if room_name.replace(" ", "_") in key:
                    matched_room_key = key
                    break

            if not matched_room_key:
                print(f"Warning: Room name '{room_name}' not found in bundle_list.json")
                continue

            main_item_name = main_completion_items.get(room_name)
            
            # Find index of the main completion item in data['Bundles']
            for i, item in enumerate(data['Bundles']):
                if item[0] == main_item_name:
                    # Insert each selected bundle with all fields from bundle_list.json
                    for bundle_name in bundle_names:
                        # Find the full bundle data in bundle_list.json
                        for bundle_data in bundle_list[matched_room_key]:
                            if bundle_data[0] == bundle_name:
                                # Insert the complete bundle data from bundle_list
                                data['Bundles'].insert(i + 1, bundle_data)
                                break
                    break

        # Save the updated data back to data.json
        save_data(data_file, data)

        # Refresh the Bundles tab UI to reflect the updated data
        self.refresh_bundles_tab()


    def refresh_bundles_tab(self):
        """Reloads the Bundles tab UI based on the updated JSON data."""
        # Clear the existing Bundles tab content
        self.main_tabs.removeTab(0)  # Assuming Bundles tab is the first one

        # Reload data and create a fresh Bundles tab
        updated_data = load_data(data_file)
        bundles_items = updated_data.get("Bundles", [])
        new_bundles_tab = self.create_tab("Bundles", bundles_items)

        # Add the refreshed Bundles tab at the original position
        self.main_tabs.insertTab(0, new_bundles_tab, "Bundles")


    def create_friends_tab(self, tab_name):
        """Create a special tab for friends with relationship level controls from 0 to 8."""
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

        # List of friend names
        friends = ["Emily (Winter 11)", "Abigail (Fall 13)", "Penny (Fall 2)", "Leah (Winter 23)", "Maru (Summer 10)", "Haley (Spring 14)"]

        for i, friend in enumerate(friends):
            friend_label = QLabel(f"{friend}:")
            level_selector = QComboBox()
            level_options = [0, 2, 4, 6, 8]  # Relationship levels
            level_selector.addItems(map(str, level_options))
            level_selector.setCurrentText(str(self.get_friends_data(friend, tab_name)))
            level_selector.currentTextChanged.connect(lambda value, f=friend: self.update_friends_data(f, tab_name, int(value)))
            level_selector.currentTextChanged.connect(self.update_friends_counter)

            friends_layout.addWidget(friend_label, i, 0, Qt.AlignTop)
            friends_layout.addWidget(level_selector, i, 1, Qt.AlignTop)

        layout.addLayout(friends_layout)
        tab.setLayout(layout)

        # Initialize the friends counter display
        self.update_friends_counter()
        return tab

    def update_friends_counter(self):
        """Update the Friends tab counter label to show the checked items count."""
        total_checked = 0
        total_items = 48  # Total number of friends

        # Count the total checked levels for each friend in JSON data
        for item in data["Friendsanity"]:
            if item[4] > 0:  # Check if relationship level is greater than 0
                total_checked += 1

        # Update the counter label in the Friends tab
        self.friends_counter_label.setText(f"{total_checked} / {total_items} items checked")

    def get_friends_data(self, friend, tab_name):
        """Retrieve the highest relationship level for each friend from the data on load."""
        highest_level = 0
        for item in data[tab_name]:
            if friend in item[0] and item[4] == 1:  # Check if friend matches and is set to 1
                level_num = int(item[0].split()[1])  # Extract the level from the format "Friend Level <3"
                if level_num > highest_level:
                    highest_level = level_num
        return highest_level

    def update_friends_data(self, friend, tab_name, level):
        """Update JSON data to reflect relationship levels for each friend."""
        for item in data[tab_name]:
            if friend in item[0]:
                # Set the relationship level as 1 if it's <= selected level, else 0
                level_num = int(item[0].split()[1])
                item[4] = 1 if level_num <= level else 0

        save_data(data_file, data)
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
        for item in data.get(tab_name, []):
            if "Floor" in item[0] and "Treasure" not in item[0] and item[4] == 1:
                floor_level = int(item[0].split(" ")[1])  # Extract floor number
                if floor_level > highest_floor:
                    highest_floor = floor_level
        return highest_floor

    def get_last_checked_treasure(self, tab_name):
        """Retrieve the highest checked treasure value specifically for treasures."""
        highest_treasure = 0
        for item in data.get(tab_name, []):
            if "Floor" in item[0] and "Treasure" in item[0] and item[4] == 1:
                treasure_level = int(item[0].split(" ")[1])  # Extract treasure level
                if treasure_level > highest_treasure:
                    highest_treasure = treasure_level
        return highest_treasure

    def update_mines_counter(self):
        """Update the Mines tab counter label to show the checked items count."""
        total_checked = 0
        total_items = 36  # 1 for Entrance Cutscene, 25 for Floors, 11 for Treasures

        # Count checked levels in JSON for Mines
        for item in data["Elevatorsanity"]:
            if item[4] == 1:
                total_checked += 1

        # Update the counter label in the Mines tab
        self.mines_counter_label.setText(f"{total_checked} / {total_items} items checked")
        self.update_global_counter()

    def get_mines_data(self, key, tab_name):
        """Retrieve stored value for Mines tab components based on JSON data."""
        for item in data.get(tab_name, []):
            if key in item[0]:  # Find the item matching the key
                return item[4]
        return 0
        
    def update_mines_data(self, key, tab_name, value):
        """Update JSON data with Mines tab values and save."""
        for item in data.get(tab_name, []):
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
        save_data(data_file, data)
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

        # Count the total checked levels for each skill in JSON data
        for skill in ["Combat", "Farming", "Fishing", "Foraging", "Mining"]:
            for item in data["Skillsanity"]:
                if skill in item[0] and item[4] == 1:  # Check if level is set to 1
                    total_checked += 1

        # Update the counter label in the Skills tab
        self.update_global_counter()
        self.skills_counter_label.setText(f"{total_checked} / {total_items} items checked")


    def get_skill_level_from_data(self, tab_name, skill):
        """Retrieve the highest checked level for each skill from the data on load."""
        highest_level = 0
        for item in data[tab_name]:
            if skill in item[0] and item[4] == 1:
                level_num = int(item[0].split()[-1])
                if level_num > highest_level:
                    highest_level = level_num
        return highest_level

    def update_skill_level(self, tab_name, skill, level):
        """Update JSON data to reflect skill levels up to the selected level."""
        for item in data[tab_name]:
            if skill in item[0]:
                level_num = int(item[0].split()[-1])
                item[4] = 1 if level_num <= level else 0

        save_data(data_file, data)
        self.update_global_counter()

    def create_tab(self, tab_name, items):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Counter Label for this tab
        counter_label = QLabel()
        self.counter_labels[tab_name] = counter_label
        layout.addWidget(counter_label)

        # User Search Bar
        user_search_bar = QLineEdit()
        user_search_bar.setPlaceholderText("User Search...")
        user_search_bar.textChanged.connect(lambda: self.apply_filters(checkboxes, user_search_bar.text().lower()))

        layout.addWidget(user_search_bar)

        # Scroll Area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)
        scroll_content = QGroupBox()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)
        scroll_layout.setSpacing(10)
        scroll_area.setWidget(scroll_content)

        # Add checkboxes
        checkboxes = []
        tab_checked_count = 0

        for index, item in enumerate(items):
            item_name, item_seasons, item_info, item_id, item_state = item
            checkbox_label = f"{item_name:<30} {', '.join(item_seasons):<40} {item_info}"
            checkbox = QCheckBox(checkbox_label)
            checkbox.seasons = item_seasons
            checkbox.setChecked(item_state == 1)
            checkbox.original_index = index

            if item_state == 1:
                tab_checked_count += 1
                self.total_checked += 1

            # Pass user_search_bar to update_checkbox in the connection
            checkbox.stateChanged.connect(lambda state, c=checkbox, t=tab_name, i=index: self.update_checkbox(c, scroll_layout, checkboxes, t, i, user_search_bar))
            checkboxes.append(checkbox)

        for checkbox in checkboxes:
            scroll_layout.addWidget(checkbox)

        # Apply initial sorting based on the selected season and checked status
        self.apply_filters(checkboxes)

        layout.addWidget(scroll_area)
        user_search_bar.textChanged.connect(lambda: self.apply_filters(checkboxes, user_search_bar.text().lower()))
        self.update_counter(checkboxes, tab_name)
        counter_label.setText(f"{tab_checked_count} / {len(checkboxes)} items checked")
        
        return tab

    def apply_filters(self, checkboxes, search_text=""):
        # Sort checkboxes by checked status, season match, and search text
        sorted_checkboxes = sorted(
            checkboxes,
            key=lambda checkbox: (
                checkbox.isChecked(),  # Checked items at the bottom
                not (self.selected_season in getattr(checkbox, 'seasons', [])),  # Season matches at the top
                search_text not in checkbox.text().lower(),  # Search matches at the top
                checkbox.original_index  # Preserve original order for non-matches
            )
        )

        # Re-add checkboxes in sorted order and apply styling
        visible_count = 0
        for checkbox in sorted_checkboxes:
            is_visible = search_text in checkbox.text().lower()
            checkbox.setVisible(is_visible)  # Show only matching checkboxes
            if is_visible:
                visible_count += 1
            checkbox.parent().layout().removeWidget(checkbox)
            checkbox.parent().layout().addWidget(checkbox)

            # Ensure black background remains for checked items
            if checkbox.isChecked():
                checkbox.setStyleSheet("background-color: black; color: white;")
            elif self.selected_season in getattr(checkbox, 'seasons', []):
                checkbox.setStyleSheet(season_colors[self.selected_season])
            else:
                checkbox.setStyleSheet("background-color: #3c3f41;")  # Default color

        # Check if there are no visible items after filtering
        if visible_count == 0:
            # Find the current tab and search for matches in the next tab
            current_index = self.main_tabs.currentIndex()
            total_tabs = self.main_tabs.count()

            # Loop to find a tab with matches
            for i in range(1, total_tabs):  # Check remaining tabs
                next_tab_index = (current_index + i) % total_tabs
                next_tab = self.main_tabs.widget(next_tab_index)
                next_checkboxes = next_tab.findChildren(QCheckBox)

                # Check if there are any matches in the next tab
                match_found = any(search_text in cb.text().lower() for cb in next_checkboxes)
                if match_found:
                    # Switch to the next tab with matches
                    self.main_tabs.setCurrentIndex(next_tab_index)
                    
                    # Set the search term in the new tab's search bar and clear the old one
                    current_search_bar = self.main_tabs.widget(current_index).findChild(QLineEdit)
                    if current_search_bar:
                        current_search_bar.clear()

                    next_search_bar = next_tab.findChild(QLineEdit)
                    if next_search_bar:
                        next_search_bar.setText(search_text)
                    
                    # Apply filters to the new tab with the search text
                    self.apply_filters(next_checkboxes, search_text)
                    break

    def update_checkbox(self, checkbox, layout, checkboxes, tab_name, index, search_bar):
        # Update the JSON data with the new state
        item_state = 1 if checkbox.isChecked() else 0
        data[tab_name][index][4] = item_state  # Update state in data

        # Save the updated state to the JSON file
        save_data(data_file, data)

        # Update counters and styles for completed items
        if checkbox.isChecked():
            self.total_checked += 1
            checkbox.setStyleSheet("background-color: black; color: white;")  # Black background for completed items
        else:
            self.total_checked -= 1
            # Apply season color or default background based on current filter
            if self.selected_season in getattr(checkbox, 'seasons', []):
                checkbox.setStyleSheet(season_colors[self.selected_season])
            else:
                checkbox.setStyleSheet("background-color: #3c3f41;")  # Default color

        # Apply the current filter and sorting based on the search and season filter
        search_text = search_bar.text().lower()
        self.apply_filters(checkboxes, search_text)

        # Update the global and tab counters
        self.update_counter(checkboxes, tab_name)
        self.update_global_counter()


    def reset_all_checkboxes(self):
        # Friends whose states should remain checked at level 8
        friends_to_keep_checked = ["Alex", "Elliott", "Harvey", "Sam", "Sebastian", "Shane"]

        # Step 1: Reset all JSON fields to 0
        for tab_name, items in data.items():
            for item in items:
                item[4] = 0  # Set every item's 'state' to 0 initially

        # Step 2: Set specific friends' state to 1
        for item in data.get("Friendsanity", []):
            if any(friend in item[3] for friend in friends_to_keep_checked):
                item[4] = 1

        if self.server_window is not None:
            self.server_window.clear_hints()  # Clear the hints if the ServerWindow is open


        # Step 3: Update UI checkboxes to match JSON data for each tab
        for i in range(self.main_tabs.count()):
            # Use mapped data key
            tab_name = self.main_tabs.tabText(i)
            data_key = tab_name_mapping.get(tab_name, "")
            items = data.get(data_key, [])

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
            skill_items = data.get(skill_tab_name, [])
            
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

        # Step 5: Reset Friends Tab ComboBoxes to 0, except specific friends at 8
        for i in range(self.friends_tabs.count()):
            friend_tab_name = self.friends_tabs.tabText(i)
            friend_items = data.get(friend_tab_name, [])
            
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
        save_data(data_file, data)

        # Step 8: Update the global counter
        self.total_checked = sum(1 for tab in data.values() for item in tab if item[4] == 1)
        self.update_global_counter()
        self.update_all()



    def update_counter(self, checkboxes, tab_name):
        total = len(checkboxes)
        checked = sum(1 for checkbox in checkboxes if checkbox.isChecked())
        self.counter_labels[tab_name].setText(f"{checked} / {total} items checked")

    def update_global_counter(self):
        # Count the total number of items in the JSON and those with `1` in the last field
        total_items = sum(len(items) for items in data.values())
        checked_items = sum(1 for items in data.values() for item in items if item[4] == 1)
        
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

        # Apply colors and sorting to checkboxes in the tabs based on the selected season
        for i in range(self.main_tabs.count()):
            tab_widget = self.main_tabs.widget(i)
            if tab_widget:
                checkboxes = tab_widget.findChildren(QCheckBox)
                sorted_checkboxes = self.sort_checkboxes(checkboxes)

                for checkbox in sorted_checkboxes:
                    checkbox.setVisible(True)
                    checkbox.parent().layout().removeWidget(checkbox)
                    checkbox.parent().layout().addWidget(checkbox)

                    # Apply black background to completed items
                    if checkbox.isChecked():
                        checkbox.setStyleSheet("background-color: black; color: white;")
                    elif self.selected_season in getattr(checkbox, 'seasons', []):
                        # Apply season color to checkboxes that match the selected season
                        checkbox.setStyleSheet(season_colors[self.selected_season])
                    else:
                        checkbox.setStyleSheet("background-color: #3c3f41;")  # Default checkbox background

    def sort_checkboxes(self, checkboxes):
        """Sort checkboxes by checked status, season match, and search text."""
        return sorted(
            checkboxes,
            key=lambda checkbox: (
                checkbox.isChecked(),  # Checked items at the bottom
                not (self.selected_season in getattr(checkbox, 'seasons', [])),  # Season matches at the top
                checkbox.original_index  # Preserve original order for non-matches
            )
        )


# Run the application
app = QApplication(sys.argv)
app.setStyleSheet(dark_theme)
window = MainWindow()
window.show()
sys.exit(app.exec_())