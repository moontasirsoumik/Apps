import streamlit as st
import folium
from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import st_folium
from geopy.distance import geodesic
import requests
import base64

# For GPS location retrieval
from streamlit_javascript import st_javascript

# --- HELPER FUNCTION TO EMBED IMAGES ---
def get_image_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode('utf-8')
            return f"data:image/png;base64,{b64}"
    except Exception as e:
        return ""  # Return empty string if file not found

# --- PAGE CONFIG ---
st.set_page_config(page_title="Helsinki Mosques", layout="centered")

# --- GLOBAL STYLES ---
st.markdown("""
    <style>
    /* Page background & font */
    body {
        background-color: #f5f5f5;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    /* Button: white with red accent */
    .stButton button {
        background: #fff;
        color: #d9534f;
        border: 2px solid #d9534f;
        border-radius: 8px;
        height: 3rem;
        font-size: 1rem;
        font-weight: 600;
        margin-top: 10px;
        transition: background 0.3s ease;
        cursor: pointer;
    }
    .stButton button:hover {
        background: #d9534f;
        color: #fff;
    }
    /* Titles and general text */
    h1, h2, h3, h4 {
        color: #333;
    }
    .css-1lcbmhc, .css-18e3th9 {
        color: #444;
    }
    /* Mosque tile style (for lower details section) */
    .mosque-tile {
        background-color: #fff;
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
        box-shadow: 0 0 6px rgba(0,0,0,0.05);
        overflow: auto;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA ---
mosques = {
    "Bangladesh Islamic Cultural Center (BICC)": {
        "type": "Mosque",
        "coords": [60.250280726774456, 25.01109832122293],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/3vZq9vhDUWvVDnL1A"
    },
    "Masjid Al-Huda (Helsinki Islamic Center)": {
        "type": "Mosque",
        "coords": [60.199935497835995, 24.937680503497916],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/hQVKt31t9xCwzDzFA"
    },
    "Hidaya Mosque": {
        "type": "Mosque",
        "coords": [60.24910140156021, 25.008836640940803],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/4pksAR6XZzc5nZ3e7"
    },
    "Al-Iman Mosque": {
        "type": "Mosque",
        "coords": [60.196677300959216, 24.882916721221132],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/yAHGFfznsHdJ9pez9"
    },
    "Ummah Moskeija": {
        "type": "Mosque",
        "coords": [60.223381342923645, 24.993431115463885],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/JVAGcGj1xbizgYds5"
    },
    "Suomen Islamilainen Yhdyskunta": {
        "type": "Mosque",
        "coords": [60.16466031795139, 24.93424255135939],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/QkDCeh2kVQPwp96P7"
    },
    "Bangladesh Kendrio Masjid": {
        "type": "Mosque",
        "coords": [60.21046822195977, 25.05075871552435],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/SaUjg4tqC2qYFZMp6"
    },
    "Al-Iman Mosque": {
        "type": "Mosque",
        "coords": [60.196677300959216, 24.882916721221132],
        "description": "Mosque",
        "image": "image.png",
        "maps_link": "https://maps.app.goo.gl/yAHGFfznsHdJ9pez9"
    }
}

# --- SIDEBAR ---
st.sidebar.title("Helsinki Mosques Finder")

# Map Style
st.sidebar.subheader("Map Style")
tile_options = ["OpenStreetMap", "CartoDB positron", "CartoDB dark_matter"]
tile_choice = st.sidebar.selectbox("Choose Map Style", tile_options, index=0)

# Location Input
st.sidebar.subheader("Your Current Location")
user_lat = st.sidebar.number_input("Latitude", value=60.1699, format="%.6f")
user_lon = st.sidebar.number_input("Longitude", value=24.9384, format="%.6f")

# Session state for user location
if "user_location" not in st.session_state:
    st.session_state.user_location = None

# Button to get GPS location
if st.sidebar.button("Get My GPS Location"):
    coords = st_javascript(
        "navigator.geolocation.getCurrentPosition((pos)=>{return [pos.coords.latitude, pos.coords.longitude];});"
    )
    if coords:
        st.session_state.user_location = (coords[0], coords[1])
        st.sidebar.success(f"GPS Location Acquired: {st.session_state.user_location}")
    else:
        st.sidebar.error("Unable to retrieve GPS location. Please enter manually.")

# Determine user location
if st.session_state.user_location is not None:
    user_location = st.session_state.user_location
else:
    user_location = (user_lat, user_lon)
st.sidebar.write("Using Location:", user_location)

# Filter by Mosque Type
filter_types = st.sidebar.multiselect(
    "Filter by mosque type",
    ["Mosque", "Multi Faith Room", "Suggested Place"],
    default=["Mosque", "Multi Faith Room", "Suggested Place"]
)
filtered_mosques = {name: data for name, data in mosques.items() if data["type"] in filter_types}

# Mosque selection
filtered_names = sorted(filtered_mosques.keys())
selected_mosque = st.sidebar.selectbox(
    "Search for a mosque (or select 'None' for closest)",
    ["None"] + filtered_names
)

# Calculate distances for each mosque
distances = {}
for name, data in filtered_mosques.items():
    distances[name] = geodesic(user_location, data["coords"]).km

# Determine chosen mosque (or closest if "None")
if selected_mosque == "None":
    if distances:
        direction_mosque = min(distances, key=distances.get)
        st.sidebar.markdown("### Closest Mosque")
        st.sidebar.write(f"**{direction_mosque}** is about **{distances[direction_mosque]:.2f} km** away.")
    else:
        st.sidebar.write("No mosques found under current filters.")
        direction_mosque = None
else:
    direction_mosque = selected_mosque
    st.sidebar.markdown("### Selected Mosque")
    st.sidebar.write(f"**{direction_mosque}** is about **{distances[direction_mosque]:.2f} km** away.")

# --- ROUTE / DIRECTIONS ---
if "route" not in st.session_state:
    st.session_state.route = None
    st.session_state.target_mosque = None

direction_clicked = st.sidebar.button("Get Direction")
if direction_clicked and direction_mosque:
    lib_data = filtered_mosques[direction_mosque]
    start_lon, start_lat = user_location[1], user_location[0]
    end_lon, end_lat = lib_data["coords"][1], lib_data["coords"][0]
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
    response = requests.get(osrm_url)
    if response.status_code == 200:
        route_data = response.json()["routes"][0]["geometry"]["coordinates"]
        route_latlon = [[coord[1], coord[0]] for coord in route_data]
        st.session_state.route = route_latlon
        st.session_state.target_mosque = direction_mosque
    else:
        st.sidebar.error("Failed to retrieve route directions.")

# --- MAIN CONTENT ---
st.title("Helsinki Mosques")

# Center container (same fixed width for map and cards)
st.markdown("<div style='width:1000px; margin:0 auto;'>", unsafe_allow_html=True)

# Create Folium map
map_center = [60.1699, 24.9384]
m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles=tile_choice)
Fullscreen().add_to(m)
marker_cluster = MarkerCluster().add_to(m)

# Add markers with updated popup HTML (name, details, distance, and 2 buttons)
for name, data in filtered_mosques.items():
    directions_url = f"https://www.google.com/maps/dir/?api=1&origin={user_location[0]},{user_location[1]}&destination={data['coords'][0]},{data['coords'][1]}"
    view_url = f"https://www.google.com/maps/search/?api=1&query={data['coords'][0]},{data['coords'][1]}"
    popup_html = f"""
    <div style="width:250px;">
        <h4 style="margin-bottom:5px; color:#333;">{name}</h4>
        <p style="font-size:12px; color:#555;">{data['description']}</p>
        <p style="font-size:12px; color:#555;">Distance: {distances[name]:.2f} km</p>
        <div style="display:flex; justify-content:space-between;">
            <a href="{directions_url}" target="_blank" 
               style="text-decoration:none; color:#d9534f; font-weight:600; border:1px solid #d9534f; padding:4px 8px; border-radius:4px;">
               Get Directions
            </a>
            <a href="{view_url}" target="_blank" 
               style="text-decoration:none; color:#d9534f; font-weight:600; border:1px solid #d9534f; padding:4px 8px; border-radius:4px;">
               View on Maps
            </a>
        </div>
    </div>
    """
    folium.Marker(
        location=data["coords"],
        popup=popup_html,
        tooltip=name,
        icon=folium.Icon(color='blue', icon='mosque', prefix='fa')
    ).add_to(marker_cluster)

# Add marker for user location
folium.Marker(
    location=user_location,
    tooltip="Your Location",
    icon=folium.Icon(color="green", icon="user", prefix="fa")
).add_to(m)

# Draw route if available
if st.session_state.route is not None and st.session_state.target_mosque == direction_mosque:
    folium.PolyLine(st.session_state.route, color="blue", weight=4, opacity=0.7).add_to(m)

# Display the map (fixed width 1000px)
st_folium(m, width=1000, height=500)

# Mosque details (cards)
if not filtered_mosques:
    st.info("No mosques found under the current filter selection.")
else:
    st.subheader("Mosque Details")
    sorted_mosques = sorted(filtered_mosques.items(), key=lambda x: distances[x[0]])
    for name, data in sorted_mosques:
        dist_km = distances[name]
        tile_html = f"""
        <div class="mosque-tile">
            <div style="float:left; width:65%;">
                <h4 style="margin-top:0;">{name}</h4>
                <p>{data['description']}</p>
                <p><strong>Distance:</strong> {dist_km:.2f} km</p>
                <p>
                    <a href="https://www.google.com/maps/dir/?api=1&origin={user_location[0]},{user_location[1]}&destination={data['coords'][0]},{data['coords'][1]}" target="_blank" style="color:#d9534f; text-decoration:none;">
                        Get Directions
                    </a>
                    &nbsp;&nbsp;
                    <a href="https://www.google.com/maps/search/?api=1&query={data['coords'][0]},{data['coords'][1]}" target="_blank" style="color:#d9534f; text-decoration:none;">
                        View on Maps
                    </a>
                </p>
            </div>
            <div style="float:right; width:35%; text-align:center;">
                <img src="{get_image_base64(data['image'])}" style="width:200px; height:200px; object-fit: cover; border-radius:6px;" />
            </div>
            <div style="clear: both;"></div>
        </div>
        """
        st.markdown(tile_html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
