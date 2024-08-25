from flask import Flask, render_template_string, request
import folium
import pandas as pd
import logging
import sqlite3
from pathlib import Path
import geopandas as gpd
from folium.plugins import MarkerCluster 

# Path to the GeoJSON file
file_js = Path(__file__).parent / 'Resources/California_Fire_Perimeters.geojson'

# Step 1: Load Wildfire GeoJSON Data
wildfire_gdf = gpd.read_file(file_js)

# Rename specific columns
wildfire_gdf = wildfire_gdf.rename(columns={
    'OBJECTID': 'ID',
    'YEAR_': 'Year',
    'STATE': 'State',
    'AGENCY': 'Agency',
    'UNIT_ID': 'Unit ID',
    'FIRE_NAME': 'Fire Name',
    'INC_NUM': 'Incident Number',
    'ALARM_DATE': 'Alarm Date',
    'CONT_DATE': 'Containment Date',
    'CAUSE': 'Cause',
    'C_METHOD': 'Collection Method',
    'OBJECTIVE': 'Management Objective',
    'GIS_ACRES': 'GIS Acres',
    'COMMENTS': 'Comments', 
    'COMPLEX_NAME': 'Complex Name',
    'IRWINID': 'IRWIN ID',
    'FIRE_NUM': 'Fire Number',
    'COMPLEX_ID': 'Complex ID',
    'DECADES':'Decades', 
    'geometry': 'Geometry'
})

# Keep only a subset of columns for analysis
wildfire_gdf = wildfire_gdf[['ID', 'Year', 'State', 'Agency', 'Unit ID', 'Fire Name',
    'Incident Number', 'Alarm Date', 'Containment Date', 'Cause', 'GIS Acres', 
    'Comments','Complex Name', 'Fire Number', 'Decades','Geometry']]

# Calculate the centroid of each geometry (for polygons)
wildfire_gdf['Centroid'] = wildfire_gdf['Geometry'].centroid

# Extract latitude and longitude from the centroid
wildfire_gdf['Latitude'] = wildfire_gdf['Centroid'].y
wildfire_gdf['Longitude'] = wildfire_gdf['Centroid'].x

# Convert the geometry column to WKT (Well-Known Text)
wildfire_gdf['Geometry'] = wildfire_gdf['Geometry'].apply(lambda x: x.wkt)

# Transform Date columns to datetime
wildfire_gdf['Alarm Date'] = pd.to_datetime(wildfire_gdf['Alarm Date'], errors='coerce')
wildfire_gdf['Containment Date'] = pd.to_datetime(wildfire_gdf['Containment Date'], errors='coerce')

# Extract Year Month info from Alarm Date
wildfire_gdf['Date'] = wildfire_gdf['Alarm Date'].dt.to_period('M').dt.to_timestamp()

# Keep only a subset of columns for analysis - remove geometry and centroid data which SQL can't take
wildfire_gdf = wildfire_gdf[['ID', 'Year', 'State', 'Agency', 'Unit ID', 'Fire Name',
    'Incident Number', 'Alarm Date', 'Containment Date', 'Cause', 'Date',
    'GIS Acres', 'Comments', 'Complex Name', 'Fire Number', 'Decades',
    'Latitude', 'Longitude']]

# Connect to a SQL database
conn = sqlite3.connect('ca_wildfires.db')

# Write the GeoDataFrame to the SQLite database
wildfire_gdf.to_sql('wildfires', conn, if_exists='replace', index=False)

# Query to list all tables in the database
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

# Display the tables
print("Tables in database:", tables)

# Load the wildfires data into a pandas DataFrame
df = pd.read_sql_query("SELECT * FROM wildfires", conn)

# Remove rows with NA in the 'Alarm Date' column
df = df.dropna(subset=['Alarm Date', 'Containment Date', 'Latitude', 'Longitude', 'GIS Acres'])

# Close the connection
conn.close()

# Initial data loading and processing
df['Alarm Date'] = pd.to_datetime(df['Alarm Date'])
df['duration_days'] = (pd.to_datetime(df['Containment Date']) - df['Alarm Date']).dt.days

# Ensure latitude and longitude are in float format
df['Latitude'] = df['Latitude'].astype(float)
df['Longitude'] = df['Longitude'].astype(float)

# Check for any NA values in critical columns
print("Checking for NA values:")
print(df[['Latitude', 'Longitude', 'GIS Acres', 'duration_days']].isna().sum())

# Check some latitude and longitude values to ensure they are valid
print(df[['Latitude', 'Longitude']].head())


# Flask app setup
app = Flask(__name__)

# Function to determine marker color based on duration
def color_producer(duration_days):
    if duration_days < 5:
        return 'green'
    elif 5 <= duration_days < 10:
        return 'orange'
    else:
        return 'red'

# Function to create and update the map based on the selected year
def update_map(year):
    m = folium.Map(location=[36.7783, -119.4179], zoom_start=6)
    marker_cluster = folium.plugins.MarkerCluster().add_to(m)
    
    filtered_df = df[df['Alarm Date'].dt.year == year]
    print(f"Number of records for year {year}: {len(filtered_df)}")  # Debugging output
    
    for _, row in filtered_df.iterrows():
        # Define the custom .png image you want to use:
        custom_icon = 'Images/Flame_Icon.png.png'
        custom_icon = folium.features.CustomIcon(
            icon_image=custom_icon,
            # Set the size of the icon
            icon_size=(50, 50),
            # sett the anchor point of the icon
            icon_anchor=(15, 15)
    )
        # Update the Marker creation to use the custom icon:
        marker = folium.Marker(
        location=(row['Latitude'], row['Longitude']),
        icon=custom_icon,
        popup=folium.Popup(
            f"Acres Burned: {row['GIS Acres']}<br>Duration: {row['duration_days']} days<br>Fire Name: {row['Fire Name']}",
            max_width=200
        )
    )
        # Add the marker to the marker cluster
        marker.add_to(marker_cluster)
    return m


@app.route('/', methods=['GET', 'POST'])
def index():
    # Default year
    year = 2022
    
    if request.method == 'POST':
        year = int(request.form.get('year'))
    
    m = update_map(year)
    map_html = m._repr_html_()
    
    # Generate a list of unique years for the dropdown
    unique_years = sorted(df['Alarm Date'].dt.year.unique())
    
    return render_template_string('''
        <html>
        <head>
            <title>Wildfire Map</title>
        </head>
        <body>
            <h1>Wildfire Map</h1>
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

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    app.run(debug=True, host='0.0.0.0', port=5001)
