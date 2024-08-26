from flask import Flask, render_template_string, request
import folium
import pandas as pd
import sqlite3
from pathlib import Path
import logging  # Import the logging module
from folium.plugins import HeatMap

app = Flask(__name__)

# Load data from the SQLite database
def load_data():
    conn = sqlite3.connect('ca_wildfires.db')
    df = pd.read_sql_query("SELECT * FROM merged_table", conn)  # Using merged_table as you mentioned earlier
    df['Alarm Date'] = pd.to_datetime(df['Alarm Date'], errors='coerce')
    
    df = df.dropna(subset=['Alarm Date', 'Containment Date', 'Latitude', 'Longitude', 'GIS Acres', 'Temperature'])
    conn.close()
    return df

# Update the map based on the selected year
def update_heatmap(year):
    df = load_data()
    # Filter data for the selected year
    filtered_df = df[df['Alarm Date'].dt.year == year]
    
    # Prepare the data for the heatmap, using temperature as a weight
    heat_data = [
        [row['Latitude'], row['Longitude'], row['Temperature']]
        for index, row in filtered_df.iterrows()
    ]
    
    # Create a base map centered around California
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6)
    
    # Add the heatmap layer to the map
    HeatMap(heat_data).add_to(m)
    
    return m

@app.route('/', methods=['GET', 'POST'])
def index():
    df = load_data()
    year = 2022  # Default year
    if request.method == 'POST':
        year = int(request.form.get('year'))
    
    m = update_heatmap(year)
    map_html = m._repr_html_()
    
    unique_years = sorted(df['Alarm Date'].dt.year.unique())
    
    return render_template_string('''
        <html>
        <head>
            <title>Wildfire Heatmap</title>
        </head>
        <body>
            <h1>Wildfire Heatmap</h1>
            <form method="post">
                <label for="year">Select Year:</label>
                <select name="year" id="year">
                    {% for y in unique_years %}
                        <option value="{{ y }}" {% if y == year %}selected{% endif %}>{{ y }}</option>
                    {% endfor %}
                </select>
                <input type="submit" value="Update Map">
            </form>
            <div>{{ map_html|safe }}</div>
        </body>
        </html>
    ''', map_html=map_html, unique_years=unique_years, year=year)

# if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG)
#     app.run(debug=True)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0', port=5002)