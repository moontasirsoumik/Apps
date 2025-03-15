from flask import Flask, render_template, request, redirect, url_for, session
import folium
from folium.plugins import MarkerCluster, Fullscreen
from geopy.distance import geodesic
import requests

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong secret in production

# --- MOSQUE DATA ---
mosques = {
    "Bangladesh Islamic Cultural Center (BICC)": {
        "type": "Mosque",
        "coords": [60.250280726774456, 25.01109832122293],
        "description": "A vibrant center offering cultural and religious services.",
        "image": "images/image.png",  # Relative to static folder
        "maps_link": "https://maps.app.goo.gl/3vZq9vhDUWvVDnL1A"
    },
    "Masjid Al-Huda (Helsinki Islamic Center)": {
        "type": "Mosque",
        "coords": [60.199935497835995, 24.937680503497916],
        "description": "A welcoming place for community prayer and events.",
        "image": "images/image.png",
        "maps_link": "https://maps.app.goo.gl/hQVKt31t9xCwzDzFA"
    },
    "Hidaya Mosque": {
        "type": "Mosque",
        "coords": [60.24910140156021, 25.008836640940803],
        "description": "An important hub for spiritual guidance and community support.",
        "image": "images/image.png",
        "maps_link": "https://maps.app.goo.gl/4pksAR6XZzc5nZ3e7"
    },
    "Al-Iman Mosque": {
        "type": "Mosque",
        "coords": [60.196677300959216, 24.882916721221132],
        "description": "Known for its serene environment and educational programs.",
        "image": "images/image.png",
        "maps_link": "https://maps.app.goo.gl/yAHGFfznsHdJ9pez9"
    },
    "Ummah Moskeija": {
        "type": "Mosque",
        "coords": [60.223381342923645, 24.993431115463885],
        "description": "A modern space offering prayer services and community events.",
        "image": "images/image.png",
        "maps_link": "https://maps.app.goo.gl/JVAGcGj1xbizgYds5"
    },
    "Suomen Islamilainen Yhdyskunta": {
        "type": "Mosque",
        "coords": [60.16466031795139, 24.93424255135939],
        "description": "Fostering interfaith dialogue and community service.",
        "image": "images/image.png",
        "maps_link": "https://maps.app.goo.gl/QkDCeh2kVQPwp96P7"
    },
    "Bangladesh Kendrio Masjid": {
        "type": "Mosque",
        "coords": [60.21046822195977, 25.05075871552435],
        "description": "A center that caters to the diverse needs of the community.",
        "image": "images/image.png",
        "maps_link": "https://maps.app.goo.gl/SaUjg4tqC2qYFZMp6"
    }
}

def create_map(user_location, tile_choice, filtered_mosques, distances, route=None, target_mosque=None):
    map_center = [60.1699, 24.9384]
    m = folium.Map(location=map_center, zoom_start=12, control_scale=True, tiles=tile_choice)
    Fullscreen().add_to(m)
    marker_cluster = MarkerCluster().add_to(m)
    
    for name, data in filtered_mosques.items():
        directions_url = f"https://www.google.com/maps/dir/?api=1&origin={user_location[0]},{user_location[1]}&destination={data['coords'][0]},{data['coords'][1]}"
        view_url = f"https://www.google.com/maps/search/?api=1&query={data['coords'][0]},{data['coords'][1]}"
        popup_html = f'''
        <div style="width:260px; font-family: 'Roboto', sans-serif; font-size: 0.85rem; color: #333;">
            <div style="padding:10px; border-radius:6px; background:#fff; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="margin:0 0 5px; font-size:1rem; font-weight:500; color:#333;">{name}</h4>
                <p style="margin:0; color:#555;">{data["description"]}</p>
                <p style="margin:5px 0 10px; color:#777;">Distance: {distances[name]:.2f} km</p>
                <div style="display:flex; justify-content:space-between;">
                    <a href="{directions_url}" target="_blank" style="text-decoration:none; font-size:0.8rem; color:#d9534f;">Directions</a>
                    <a href="{view_url}" target="_blank" style="text-decoration:none; font-size:0.8rem; color:#d9534f;">View</a>
                </div>
            </div>
        </div>
        '''
        folium.Marker(
            location=data["coords"],
            popup=popup_html,
            tooltip=name,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(marker_cluster)
    
    folium.Marker(
        location=user_location,
        tooltip="Your Location",
        icon=folium.Icon(color="green", icon="user")
    ).add_to(m)
    
    if route and target_mosque:
        folium.PolyLine(route, color="blue", weight=4, opacity=0.7).add_to(m)
    return m

@app.route("/", methods=["GET", "POST"])
def index():
    user_lat = 60.1699
    user_lon = 24.9384
    tile_choice = "OpenStreetMap"
    selected_mosque = "None"
    filter_types = ["Mosque", "Multi Faith Room", "Suggested Place"]
    action = None

    if request.method == "POST":
        try:
            user_lat = float(request.form.get("latitude", 60.1699))
            user_lon = float(request.form.get("longitude", 24.9384))
        except:
            user_lat, user_lon = 60.1699, 24.9384
        tile_choice = request.form.get("tile_choice", "OpenStreetMap")
        selected_mosque = request.form.get("selected_mosque", "None")
        filter_types = request.form.getlist("filter_types")
        action = request.form.get("action")
        session["user_lat"] = user_lat
        session["user_lon"] = user_lon
        session["tile_choice"] = tile_choice
        session["selected_mosque"] = selected_mosque
        session["filter_types"] = filter_types
        session["action"] = action
        return redirect(url_for("index"))
    else:
        user_lat = session.get("user_lat", user_lat)
        user_lon = session.get("user_lon", user_lon)
        tile_choice = session.get("tile_choice", tile_choice)
        selected_mosque = session.get("selected_mosque", selected_mosque)
        filter_types = session.get("filter_types", filter_types)
        action = session.get("action", None)
    
    user_location = [user_lat, user_lon]
    filtered_mosques = {name: data for name, data in mosques.items() if data["type"] in filter_types}
    distances = {name: geodesic(user_location, data["coords"]).km for name, data in filtered_mosques.items()}

    if selected_mosque == "None":
        chosen_mosque = min(distances, key=distances.get) if distances else None
        chosen_distance = distances[chosen_mosque] if chosen_mosque else None
    else:
        chosen_mosque = selected_mosque
        chosen_distance = distances.get(chosen_mosque, None)

    route = None
    if action == "get_direction" and chosen_mosque:
        data = filtered_mosques[chosen_mosque]
        start_lon, start_lat = user_lon, user_lat
        end_lon, end_lat = data["coords"][1], data["coords"][0]
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        response = requests.get(osrm_url)
        if response.status_code == 200:
            route_data = response.json()["routes"][0]["geometry"]["coordinates"]
            route = [[coord[1], coord[0]] for coord in route_data]
        else:
            route = None

    folium_map = create_map(user_location, tile_choice, filtered_mosques, distances, route, chosen_mosque)
    map_html = folium_map._repr_html_()

    mosque_cards = ""
    if not filtered_mosques:
        mosque_cards = "<p>No mosques found under the current filter selection.</p>"
    else:
        sorted_mosques = sorted(filtered_mosques.items(), key=lambda x: distances[x[0]])
        for name, data in sorted_mosques:
            dist_km = distances[name]
            image_url = url_for('static', filename=data["image"])
            mosque_cards += f'''
            <div class="mosque-tile clearfix">
                <div class="mosque-info">
                    <h4>{name}</h4>
                    <p>{data["description"]}</p>
                    <p><strong>{dist_km:.2f} km</strong></p>
                    <p>
                        <a href="https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={data["coords"][0]},{data["coords"][1]}" target="_blank">Directions</a>
                        <a href="https://www.google.com/maps/search/?api=1&query={data["coords"][0]},{data["coords"][1]}" target="_blank">View</a>
                    </p>
                </div>
                <div class="mosque-image">
                    <div class="image-container">
                        <img src="{image_url}" alt="{name}">
                    </div>
                </div>
            </div>
            '''
    mosque_options = sorted(filtered_mosques.keys())

    return render_template("index.html",
                           map_html=map_html,
                           mosque_cards=mosque_cards,
                           user_lat=user_lat,
                           user_lon=user_lon,
                           tile_choice=tile_choice,
                           selected_mosque=selected_mosque,
                           filter_types=filter_types,
                           chosen_mosque=chosen_mosque,
                           chosen_distance=chosen_distance,
                           mosque_options=mosque_options,
                           mosques=mosques)

if __name__ == "__main__":
    app.run(debug=True)
