# UCB-Project3-Group3

Wildfire Visualization with Flask and Folium

This project is a Flask-based web application that visualizes wildfire data in California using an interactive map. The map allows users to filter and view wildfire information by year, with markers representing the location, size, and duration of wildfires. The application utilizes Folium to create the map and display wildfire data with custom icons.

Features

Interactive Map: View wildfire locations in California, filtered by year.
Custom Markers: Each wildfire is represented by a custom marker on the map, with an icon indicating the fire's presence.
Popup Information: Markers display detailed information about each wildfire, including acres burned, fire duration, and fire name.
Year Selection: Users can select a year to filter the wildfire data displayed on the map.
Installation

Prerequisites
- Python 3.x
- pip (Python package installer)
- A virtual environment is recommended

Setup
1. Clone the Repository
2. Create and Activate a Virtual Environment
3. Install the Required Packages
4. Setup the Database
5. Run the Application
6. Access the Web Application

Usage
1. Select a Year: Use the dropdown menu to select the year you want to explore. The map will update to show wildfires from the selected year.
2. View Wildfire Details: Click on any marker to view details about the wildfire, including the acres burned, duration, and fire name.

Project Structure

app.py: The main Flask application file that sets up the web server and defines the routes for the application.
templates/: Directory containing HTML templates for rendering the web pages.
static/: Directory for storing static files such as CSS, JavaScript, and images.
ca_wildfires.db: The SQLite database file containing wildfire data.
requirements.txt: Lists the Python packages required to run the application.
Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgments

Folium - For creating interactive maps.
Flask - For building the web application framework.
