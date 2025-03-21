import json

mosques = {
    "Bangladesh Islamic Cultural Center (BICC)": {
        "type": "Mosque",
        "coords": [60.250280726774456, 25.01109832122293],
        "description": "A vibrant center offering cultural and religious services.",
        "image": "https://via.placeholder.com/120?text=BICC",
        "maps_link": "https://maps.app.goo.gl/3vZq9vhDUWvVDnL1A",
        "location": "Helsinki AF"
    },
    "Masjid Al-Huda (Helsinki Islamic Center)": {
        "type": "Mosque",
        "coords": [60.199935497835995, 24.937680503497916],
        "description": "A welcoming place for community prayer and events.",
        "image": "https://via.placeholder.com/120?text=Al-Huda",
        "maps_link": "https://maps.app.goo.gl/hQVKt31t9xCwzDzFA",
        "location": "Helsinki AF"
    },
    "Hidaya Mosque": {
        "type": "Mosque",
        "coords": [60.24910140156021, 25.008836640940803],
        "description": "An important hub for spiritual guidance and community support.",
        "image": "https://via.placeholder.com/120?text=Hidaya",
        "maps_link": "https://maps.app.goo.gl/4pksAR6XZzc5nZ3e7",
        "location": "Helsinki AF"
    },
    "Al-Iman Mosque": {
        "type": "Mosque",
        "coords": [60.196677300959216, 24.882916721221132],
        "description": "Known for its serene environment and educational programs.",
        "image": "https://via.placeholder.com/120?text=Al-Iman",
        "maps_link": "https://maps.app.goo.gl/yAHGFfznsHdJ9pez9",
        "location": "Helsinki AF"
    },
    "Ummah Moskeija": {
        "type": "Mosque",
        "coords": [60.223381342923645, 24.993431115463885],
        "description": "A modern space offering prayer services and community events.",
        "image": "https://via.placeholder.com/120?text=Ummah",
        "maps_link": "https://maps.app.goo.gl/JVAGcGj1xbizgYds5",
        "location": "Helsinki AF"
    },
    "Suomen Islamilainen Yhdyskunta": {
        "type": "Mosque",
        "coords": [60.16466031795139, 24.93424255135939],
        "description": "Fostering interfaith dialogue and community service.",
        "image": "https://via.placeholder.com/120?text=Yhdyskunta",
        "maps_link": "https://maps.app.goo.gl/QkDCeh2kVQPwp96P7",
        "location": "Helsinki AF"
    },
    "Bangladesh Kendrio Masjid": {
        "type": "Mosque",
        "coords": [60.21046822195977, 25.05075871552435],
        "description": "A center that caters to the diverse needs of the community.",
        "image": "https://via.placeholder.com/120?text=Kendrio",
        "maps_link": "https://maps.app.goo.gl/SaUjg4tqC2qYFZMp6",
        "location": "Helsinki AF"
    },
}

# Convert the dictionary to a JSON string
mosques_json = json.dumps(mosques, indent=4)

# Save the JSON string to a file
with open("mosques.json", "w") as json_file:
    json_file.write(mosques_json)

print("JSON database created and saved as 'mosques.json'")
