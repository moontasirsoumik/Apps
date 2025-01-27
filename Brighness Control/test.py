import screen_brightness_control as sbc

try:
    monitors = sbc.list_monitors()
    print(f"Detected monitors: {monitors}")
    for monitor in monitors:
        try:
            brightness = sbc.get_brightness(display=monitor)
            print(f"Monitor: {monitor}, Brightness: {brightness}")
        except Exception as e:
            print(f"Error getting brightness for {monitor}: {e}")
except Exception as e:
    print(f"Error listing monitors: {e}")
