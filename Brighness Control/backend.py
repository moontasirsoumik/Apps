import screen_brightness_control as sbc
import winreg

def get_transparency_status():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "EnableTransparency")
        return value == 1
    except Exception:
        return True

def get_dark_mode_status():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return value == 0
    except Exception:
        return False

def get_accent_color():
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, 
            r"Software\Microsoft\Windows\DWM"
        )
        value, _ = winreg.QueryValueEx(key, "AccentColor")
        r = value & 0xFF
        g = (value >> 8) & 0xFF
        b = (value >> 16) & 0xFF
        return (r, g, b)
    except Exception:
        return (0, 120, 215)

def get_brightness(display):
    try:
        return sbc.get_brightness(display=display)[0]
    except Exception:
        return 50

def set_brightness(display, value):
    try:
        sbc.set_brightness(value, display=display)
    except Exception as e:
        print(f"Error setting brightness: {e}")

def list_displays():
    try:
        return sbc.list_monitors()
    except Exception:
        return []