from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import folium
from folium.plugins import MarkerCluster, Fullscreen
from geopy.distance import geodesic
import requests
from geopy.geocoders import Nominatim
import math
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize a geolocator for reverse geocoding
geolocator = Nominatim(user_agent="my_app")

# --- LOAD MOSQUE DATA FROM JSON FILE ---
mosque_file = "mosques.json"
with open(mosque_file, "r", encoding="utf-8") as f:
    mosques = json.load(f)

# For each mosque, if there is no "address" field or its value is empty, fetch the address.
updated = False
for name, data in mosques.items():
    if not data.get("address"):
        try:
            address = geolocator.reverse(data["coords"], language="en").address
        except Exception as e:
            print(f"Error getting address for {name}: {e}")
            address = "No address found"
        data["address"] = address
        updated = True

if updated:
    with open(mosque_file, "w", encoding="utf-8") as f:
        json.dump(mosques, f, ensure_ascii=False, indent=4)
    print("mosque.json file updated with location data.")


def bounding_box(lat, lon, dist_km=3.0):
    """Simple bounding box around (lat, lon)."""
    d_lat = dist_km / 111.0
    d_lon = dist_km / (111.0 * math.cos(math.radians(lat)))
    return (lat - d_lat, lon - d_lon, lat + d_lat, lon + d_lon)


@app.route("/")
def landing():
    """Landing page that loads 'landing.html' and then transitions to /app in an iframe."""
    return render_template("landing.html")


@app.route("/app", methods=["GET", "POST"])
def main_app():
    """
    Main route for the UI.
    Dropdown now includes "None", "Closest", and specific mosque names.
    """
    # Defaults
    user_lat = 60.1699
    user_lon = 24.9384
    tile_choice = "OpenStreetMap"
    selected_mosque = "None"  # initial value in dropdown
    filter_types = ["Mosque", "Multi Faith Room", "Suggested Place"]
    action = None

    if request.method == "POST":
        try:
            user_lat = float(request.form.get("latitude", 60.1699))
            user_lon = float(request.form.get("longitude", 24.9384))
        except ValueError:
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

        return redirect(url_for("main_app"))
    else:
        user_lat = session.get("user_lat", user_lat)
        user_lon = session.get("user_lon", user_lon)
        tile_choice = session.get("tile_choice", tile_choice)
        selected_mosque = session.get("selected_mosque", selected_mosque)
        filter_types = session.get("filter_types", filter_types)
        action = session.get("action", None)

    # Filter mosques by type
    user_location = [user_lat, user_lon]
    filtered_mosques = {
        name: data for name, data in mosques.items() if data["type"] in filter_types
    }
    distances = {
        name: geodesic(user_location, data["coords"]).km
        for name, data in filtered_mosques.items()
    }

    # Determine chosen_mosque based on dropdown selection:
    if selected_mosque == "None":
        chosen_mosque = None
    elif selected_mosque == "Closest":
        chosen_mosque = min(distances, key=distances.get) if distances else None
    else:
        chosen_mosque = selected_mosque if selected_mosque in filtered_mosques else None

    # Optionally build route if requested
    route = None
    if action == "get_direction" and chosen_mosque:
        data = filtered_mosques[chosen_mosque]
        start_lon, start_lat = user_lon, user_lat
        end_lon, end_lat = data["coords"][1], data["coords"][0]
        osrm_url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        )
        response = requests.get(osrm_url)
        if response.status_code == 200:
            route_data = response.json()["routes"][0]["geometry"]["coordinates"]
            route = [[coord[1], coord[0]] for coord in route_data]

    folium_map = create_map(
        user_location=user_location,
        tile_choice=tile_choice,
        filtered_mosques=filtered_mosques,
        distances=distances,
        route=route,
        target_mosque=chosen_mosque,
    )
    map_html = folium_map._repr_html_()

    # Build sample mosque listing (cards)
    mosque_cards = ""
    if not filtered_mosques:
        mosque_cards = "<p>No mosques found under the current filter selection.</p>"
    else:
        sorted_mosques = sorted(filtered_mosques.items(), key=lambda x: distances[x[0]])
        for name, data in sorted_mosques:
            # Prepare fields with fallbacks.
            short_desc = data.get("short description", "").strip()
            description = (
                data.get("description", "").strip() or "Description not available"
            )
            dist_km = distances[name]
            image_url = url_for("static", filename=data["image"])

            # Build mosque tile content.
            mosque_cards += f"""
            <div class="mosque-tile clearfix" style="border: 1px solid #ddd; border-radius: 6px; padding: 10px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div class="mosque-image" style="width: 60px; height: 60px; border-radius: 6px; overflow: hidden; margin-right: 10px; flex-shrink: 0;">
                    <img src="{image_url}" alt="{name}" style="width: 100%; height: 100%; object-fit: cover;">
                </div>
                <div class="mosque-info" style="flex: 1;">
                    <h4 style="margin: 0; font-size: 1rem; font-weight: 600; color: #333;">{name}</h4>
                    {f'<p style="margin: 2px 0; font-size: 0.85rem; color: #555;">{short_desc}</p>' if short_desc else ""}
                    <p style="margin: 2px 0; font-size: 0.8rem; color: #777;">{description}</p>
                    <p style="margin: 2px 0; font-size: 0.8rem; color: #007bff;"><strong>{dist_km:.2f} km</strong></p>
                    <div style="margin-top: 4px;">
                        <a href="https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={data["coords"][0]},{data["coords"][1]}" 
                           target="_blank" style="text-decoration: none; font-size: 0.8rem; color: #007bff;">Directions</a>
                        |
                        <a href="https://www.google.com/maps/search/?api=1&query={data["coords"][0]},{data["coords"][1]}" 
                           target="_blank" style="text-decoration: none; font-size: 0.8rem; color: #28a745;">View</a>
                    </div>
                </div>
            </div>
            """

    mosque_options = sorted(filtered_mosques.keys())

    return render_template(
        "index.html",
        map_html=map_html,
        mosque_cards=mosque_cards,
        user_lat=user_lat,
        user_lon=user_lon,
        tile_choice=tile_choice,
        selected_mosque=selected_mosque,
        filter_types=filter_types,
        mosque_options=["Closest"] + sorted(filtered_mosques.keys()),
    )


@app.route("/update", methods=["POST"])
def update():
    """
    AJAX endpoint to update the map and mosque list.
    The dropdown includes "None", "Closest", and specific mosque names.
    """
    try:
        user_lat = float(request.form.get("latitude", 60.1699))
        user_lon = float(request.form.get("longitude", 24.9384))
    except ValueError:
        user_lat, user_lon = 60.1699, 24.9384

    tile_choice = request.form.get("tile_choice", "OpenStreetMap")
    selected_mosque = request.form.get("selected_mosque", "None")
    filter_types = request.form.getlist("filter_types")
    action = request.form.get("action", None)

    user_location = [user_lat, user_lon]
    filtered_mosques = {
        name: data for name, data in mosques.items() if data["type"] in filter_types
    }
    distances = {
        name: geodesic(user_location, data["coords"]).km
        for name, data in filtered_mosques.items()
    }

    if selected_mosque == "None":
        chosen_mosque = None
        chosen_distance = None
    elif selected_mosque == "Closest":
        chosen_mosque = min(distances, key=distances.get) if distances else None
        chosen_distance = distances.get(chosen_mosque, None) if chosen_mosque else None
    else:
        chosen_mosque = selected_mosque if selected_mosque in filtered_mosques else None
        chosen_distance = distances.get(chosen_mosque, None) if chosen_mosque else None

    route = None
    if action == "get_direction" and chosen_mosque:
        data = filtered_mosques[chosen_mosque]
        start_lon, start_lat = user_lon, user_lat
        end_lon, end_lat = data["coords"][1], data["coords"][0]
        osrm_url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson"
        )
        resp = requests.get(osrm_url)
        if resp.status_code == 200:
            rd = resp.json()["routes"][0]["geometry"]["coordinates"]
            route = [[c[1], c[0]] for c in rd]

    folium_map = create_map(
        user_location=user_location,
        tile_choice=tile_choice,
        filtered_mosques=filtered_mosques,
        distances=distances,
        route=route,
        target_mosque=chosen_mosque,
    )
    map_html = folium_map._repr_html_()

    mosque_cards = ""
    if not filtered_mosques:
        mosque_cards = "<p>No mosques found under the current filter selection.</p>"
    else:
        sorted_m = sorted(filtered_mosques.items(), key=lambda x: distances[x[0]])
        for name, data in sorted_m:
            dist_km = distances[name]
            short_desc = data.get("short description", "").strip()
            desc = data.get("description", "").strip() or "Description not available"
            image = data.get("image", "placeholder.jpg")
            image_url = url_for("static", filename=image)
            mosque_cards += f"""
             <div class="mosque-tile clearfix" style="border: 1px solid #ddd; border-radius: 6px; padding: 10px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                 <div class="mosque-image" style="width: 60px; height: 60px; border-radius: 6px; overflow: hidden; margin-right: 10px; flex-shrink: 0;">
                     <img src="{image_url}" alt="{name}" style="width: 100%; height: 100%; object-fit: cover;">
                 </div>
                 <div class="mosque-info" style="flex: 1;">
                     <h4 style="margin: 0; font-size: 1rem; font-weight: 600; color: #333;">{name}</h4>
                     {f'<p style="margin: 2px 0; font-size: 0.85rem; color: #555;">{short_desc}</p>' if short_desc else ""}
                     <p style="margin: 2px 0; font-size: 0.8rem; color: #777;">{description}</p>
                     <p style="margin: 2px 0; font-size: 0.8rem; color: #007bff;"><strong>{dist_km:.2f} km</strong></p>
                     <div style="margin-top: 4px;">
                         <a href="https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={data["coords"][0]},{data["coords"][1]}" 
                            target="_blank" style="text-decoration: none; font-size: 0.8rem; color: #007bff;">Directions</a>
                         |
                         <a href="https://www.google.com/maps/search/?api=1&query={data["coords"][0]},{data["coords"][1]}" 
                            target="_blank" style="text-decoration: none; font-size: 0.8rem; color: #28a745;">View</a>
                     </div>
                 </div>
             </div>
             """

    chosen_info = ""
    if chosen_mosque:
        title = "Closest Mosque" if selected_mosque == "Closest" else "Selected Mosque"
        chosen_info = f"""
        <hr />
        <h6>{title}</h6>
        <p>
          <span>{chosen_mosque}</span> – <strong>{chosen_distance:.2f} km</strong>
        </p>
        """
    else:
        chosen_info = ""

    return jsonify(
        {"map_html": map_html, "mosque_cards": mosque_cards, "chosen_info": chosen_info}
    )


# ---------------------------------------------------------------------------
# Updated create_map function (no fallback to closest mosque here)
# ---------------------------------------------------------------------------
def create_map(
    user_location,
    tile_choice,
    filtered_mosques,
    distances,
    route=None,
    target_mosque=None,
):
    # If a mosque is selected and no route is provided, center on that mosque.
    if target_mosque and not route:
        mosque_coords = filtered_mosques[target_mosque]["coords"]
        if tile_choice == "OSM Bright":
            tiles_url = "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
            attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            m = folium.Map(
                location=mosque_coords,
                zoom_start=15,  # Closer zoom when centering on the mosque
                control_scale=True,
                tiles=None,
                width="100%",
                height="100%",
            )
            folium.TileLayer(
                tiles=tiles_url, attr=attribution, name="OSM Bright"
            ).add_to(m)
        else:
            m = folium.Map(
                location=mosque_coords,
                zoom_start=15,
                control_scale=True,
                tiles=tile_choice,
                width="100%",
                height="100%",
            )
    else:
        # Existing logic: if there's a route (for directions) use the bounding box,
        # or if no mosque is selected, use the user's location.
        if target_mosque and route:
            mosque_coords = filtered_mosques[target_mosque]["coords"]
            min_lat = min(user_location[0], mosque_coords[0])
            max_lat = max(user_location[0], mosque_coords[0])
            min_lon = min(user_location[1], mosque_coords[1])
            max_lon = max(user_location[1], mosque_coords[1])
            # Expand by 10% padding
            lat_expand = (max_lat - min_lat) * 0.1
            lon_expand = (max_lon - min_lon) * 0.1
            minLat = min_lat - lat_expand
            maxLat = max_lat + lat_expand
            minLon = min_lon - lon_expand
            maxLon = max_lon + lon_expand
            if tile_choice == "OSM Bright":
                tiles_url = "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
                attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                m = folium.Map(
                    location=user_location,
                    zoom_start=13,
                    control_scale=True,
                    tiles=None,
                    width="100%",
                    height="100%",
                )
                folium.TileLayer(
                    tiles=tiles_url, attr=attribution, name="OSM Bright"
                ).add_to(m)
            else:
                m = folium.Map(
                    location=user_location,
                    zoom_start=13,
                    control_scale=True,
                    tiles=tile_choice,
                    width="100%",
                    height="100%",
                )
        else:
            minLat, minLon, maxLat, maxLon = bounding_box(
                user_location[0], user_location[1], 3.0
            )
            if tile_choice == "OSM Bright":
                tiles_url = "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
                attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                m = folium.Map(
                    location=user_location,
                    zoom_start=13,
                    control_scale=True,
                    tiles=None,
                    width="100%",
                    height="100%",
                )
                folium.TileLayer(
                    tiles=tiles_url, attr=attribution, name="OSM Bright"
                ).add_to(m)
            else:
                m = folium.Map(
                    location=user_location,
                    zoom_start=13,
                    control_scale=True,
                    tiles=tile_choice,
                    width="100%",
                    height="100%",
                )

    Fullscreen().add_to(m)
    marker_cluster = MarkerCluster().add_to(m)

    # --- Create popup markers (unchanged from previous code) ---
    for name, data in filtered_mosques.items():
        short_desc = data.get("short description", "").strip()
        location_info = data.get("address")
        if not location_info:
            location_info = "Address not available"
        popup_html = f"""
            <div style="padding: 6px 8px; margin: 0;">
                <strong style="font-size: 1.1rem; color: #333; font-family: 'Roboto', sans-serif;">{name}</strong><br>
                {f'<strong style="font-size: 1rem; color: #777; font-family: \'Roboto\', sans-serif;">{short_desc}</strong><br>' if short_desc else ""}
                <span style="font-size: 1rem; color: #555; font-family: 'Roboto', sans-serif;">{location_info}</span><br>
                <strong style="font-size: 1rem; color: #007bff; font-family: 'Roboto', sans-serif;">{distances.get(name, 0):.2f} km away</strong>
                <div style="margin-top: 6px; display: flex; gap: 6px; justify-content: center;">
                    <a href="https://www.google.com/maps/dir/?api=1&origin={user_location[0]},{user_location[1]}&destination={data['coords'][0]},{data['coords'][1]}"
                       target="_blank"
                       style="background: #007bff; color: #fff; font-size: 0.9rem; padding: 6px 8px; border-radius: 4px; text-decoration: none; font-family: 'Roboto', sans-serif;">
                        Get Direction
                    </a>
                    <a href="https://www.google.com/maps/search/?api=1&query={data['coords'][0]},{data['coords'][1]}"
                       target="_blank"
                       style="background: #28a745; color: #fff; font-size: 0.9rem; padding: 6px 8px; border-radius: 4px; text-decoration: none; font-family: 'Roboto', sans-serif;">
                        Open in GMaps
                    </a>
                </div>
            </div>
        """

        folium.Marker(
            location=data["coords"],
            tooltip=name,
            popup=folium.Popup(popup_html, max_width=200),
            icon=folium.Icon(
                color="darkpurple", icon="mosque", prefix="fa"
            ),  # More stylish color + better icon
        ).add_to(marker_cluster)

    try:
        user_address = geolocator.reverse(user_location, language="en").address
    except:
        user_address = "Your current location"
    user_popup_html = f"""
        <div style="padding: 6px 8px;">
            <strong style="font-size: 1rem; color: #333; font-family: 'Roboto', sans-serif;">Your Location</strong><br>
            <span style="font-size: 1rem; color: #555; font-family: 'Roboto', sans-serif;">{user_address}</span>
        </div>
    """
    folium.Marker(
        location=user_location,
        tooltip="Your Location",
        popup=folium.Popup(user_popup_html, max_width=200),
        icon=folium.Icon(color="green", icon="user"),
    ).add_to(m)

    if route and target_mosque:
        folium.PolyLine(route, color="blue", weight=6, opacity=0.7).add_to(m)

    # Add bounding box script only if not simply centering on a mosque without a route.
    if not (target_mosque and not route):
        bounding_box_script = f"""
        <script>
        document.addEventListener("DOMContentLoaded", function() {{
            let mapEle = document.querySelector('.folium-map');
            if (mapEle && mapEle.__folium_map) {{
                let mapObj = mapEle.__folium_map;
                let minLat = {minLat};
                let minLon = {minLon};
                let maxLat = {maxLat};
                let maxLon = {maxLon};
                let bounds = L.latLngBounds([[minLat, minLon], [maxLat, maxLon]]);
                mapObj.fitBounds(bounds);
                mapObj.setMaxBounds(bounds);
                mapObj.options.maxBoundsViscosity = 1.0;
                let currentZoom = mapObj.getZoom();
                mapObj.setMinZoom(currentZoom);
            }}
        }});
        </script>
        """
        m.get_root().html.add_child(folium.Element(bounding_box_script))

    map_script_zoom_control = """
    <script>
    document.addEventListener("DOMContentLoaded", function() {
      var bottomRight = document.querySelector("div.leaflet-bottom.leaflet-right");
      var zoomControl = document.querySelector("div.leaflet-control-zoom");
      var attributionControl = document.querySelector("div.leaflet-control-attribution");
      if (bottomRight && zoomControl && attributionControl) {
        bottomRight.insertBefore(zoomControl, attributionControl);
        zoomControl.style.right = "20px";
      }
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(map_script_zoom_control))
    return m


if __name__ == "__main__":
    app.run(debug=True)
