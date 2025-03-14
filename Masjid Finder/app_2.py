import streamlit as st
import streamlit.components.v1 as components

st.title("Get Current Location App")

if st.button("Get current location"):
    components.html(
        """
        <html>
          <body>
            <h3>Your Current Coordinates:</h3>
            <div id="location">Loading...</div>
            <script>
              if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                  const lat = position.coords.latitude;
                  const lon = position.coords.longitude;
                  document.getElementById("location").innerHTML =
                    "Latitude: " + lat + "<br>" +
                    "Longitude: " + lon;
                  // Reverse geocode using Nominatim
                  fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`)
                    .then(response => response.json())
                    .then(data => {
                      document.getElementById("location").innerHTML += "<br>Area: " + data.display_name;
                    })
                    .catch(error => {
                      document.getElementById("location").innerHTML += "<br>Error fetching area name: " + error.message;
                    });
                }, function(error) {
                  document.getElementById("location").innerHTML = "Error: " + error.message;
                });
              } else {
                document.getElementById("location").innerHTML = "Geolocation is not supported by this browser.";
              }
            </script>
          </body>
        </html>
        """,
        height=200,
    )
