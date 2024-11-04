import sys
import json
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, QCheckBox,
    QLineEdit, QLabel, QScrollArea, QGroupBox, QPushButton,
    QSpinBox, QComboBox, QGridLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

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

# Load the data from the JSON file
data_file = "data.json"
data = load_data(data_file)

class ServerConnectionThread(QThread):
    message_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, server_address):
        super().__init__()
        self.server_address = server_address
        self.client_socket = None

    def run(self):
        try:
            # Set up the socket and connect
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host, port = self.server_address.split(":")
            self.client_socket.connect((host, int(port)))
            self.message_received.emit(f"Connected to {self.server_address}")

            # Continuously receive data from the server
            while True:
                data = self.client_socket.recv(1024)  # Buffer size of 1024 bytes
                if not data:
                    break  # Exit the loop if the connection is closed
                received_message = data.decode("utf-8")
                self.message_received.emit("Received: " + received_message)
                
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.message_received.emit("Connection closed")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the main layout
        self.setWindowTitle("Stardew Check Tracker")
        self.setGeometry(300, 100, 1600, 800)
        self.setStyleSheet("font-family: 'Consolas', monospace; font-size: 8pt;")

        main_layout = QVBoxLayout()

        # Top bar layout with Server input, Connect button, and Reset button
        top_bar_layout = QHBoxLayout()

        # Server input
        self.server_input = QLineEdit()
        self.server_input.setText("wss://")
        top_bar_layout.addWidget(self.server_input)

        # Connect Button
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect_to_server)
        top_bar_layout.addWidget(connect_button)

        # Reset Button
        reset_button = QPushButton("Reset All")
        reset_button.clicked.connect(self.reset_all_checkboxes)
        top_bar_layout.addWidget(reset_button)

        # Add the top bar layout to the main layout
        main_layout.addLayout(top_bar_layout)

        # Output display for server messages
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        main_layout.addWidget(self.output_display)

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
            button.clicked.connect(lambda _, s=season, b=button: self.filter_by_season(s, b))
            self.season_buttons.append(button)
            season_layout.addWidget(button)
        main_layout.addLayout(season_layout)

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
            "Upgradesanity": "Clint's Upgrades", "Chefsanity": "Gus' Recipes", "Misc": "Misc"
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

    def connect_to_server(self):
        server_address = self.server_input.text().strip()
        if not server_address:
            self.output_display.append("Please enter a valid server address.")
            return

        # Start a new thread to handle the server connection
        self.server_thread = ServerConnectionThread(server_address)
        self.server_thread.message_received.connect(self.output_display.append)
        self.server_thread.error_occurred.connect(lambda e: self.output_display.append(f"Error: {e}"))
        self.server_thread.start()


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
        friends = ["Emily", "Abigail", "Penny", "Leah", "Maru", "Haley"]

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

            checkbox.stateChanged.connect(lambda state, c=checkbox, t=tab_name, i=index: self.update_checkbox(c, scroll_layout, checkboxes, t, i))
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

        # Re-add checkboxes in sorted order
        for checkbox in sorted_checkboxes:
            checkbox.setVisible(search_text in checkbox.text().lower())  # Show only matching checkboxes
            checkbox.parent().layout().removeWidget(checkbox)
            checkbox.parent().layout().addWidget(checkbox)


    def update_checkbox(self, checkbox, layout, checkboxes, tab_name, index):
        # Update the JSON data with the new state
        item_state = 1 if checkbox.isChecked() else 0
        data[tab_name][index][4] = item_state  # Update state in data

        # Save the updated state to the JSON file
        save_data(data_file, data)

        # Update counters
        if checkbox.isChecked():
            self.total_checked += 1
        else:
            self.total_checked -= 1

        # Re-apply the seasonal filter to maintain order
        self.apply_filters(checkboxes)

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
        # Unselect other season buttons and update selected season
        for btn in self.season_buttons:
            if btn != button:
                btn.setChecked(False)

        # Set selected season based on button toggle
        self.selected_season = season if button.isChecked() else None

        # Apply sorting to each tab
        for i in range(self.main_tabs.count()):
            tab_widget = self.main_tabs.widget(i)
            if tab_widget:
                checkboxes = tab_widget.findChildren(QCheckBox)

                # Sort checkboxes by visibility and checked state
                sorted_checkboxes = sorted(
                    checkboxes,
                    key=lambda checkbox: (
                        checkbox.isChecked(),  # Checked items at the bottom
                        not (self.selected_season in getattr(checkbox, 'seasons', [])),  # Season matches at the top
                        checkbox.original_index  # Preserve original order for non-matches
                    )
                )

                # Re-add checkboxes in sorted order
                for checkbox in sorted_checkboxes:
                    checkbox.setVisible(True)  # Ensure all checkboxes remain visible
                    checkbox.parent().layout().removeWidget(checkbox)
                    checkbox.parent().layout().addWidget(checkbox)



# Run the application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())