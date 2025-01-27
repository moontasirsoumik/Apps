# import screen_brightness_control as sbc

# try:
#     monitors = sbc.list_monitors()
#     print(f"Detected monitors: {monitors}")
#     for monitor in monitors:
#         try:
#             brightness = sbc.get_brightness(display=monitor)
#             print(f"Monitor: {monitor}, Brightness: {brightness}")
#         except Exception as e:
#             print(f"Error getting brightness for {monitor}: {e}")
# except Exception as e:
#     print(f"Error listing monitors: {e}")

import ctypes
from ctypes import wintypes

class LOGFONTW(ctypes.Structure):
    _fields_ = [
        ("lfHeight", ctypes.c_long),
        ("lfWidth", ctypes.c_long),
        ("lfEscapement", ctypes.c_long),
        ("lfOrientation", ctypes.c_long),
        ("lfWeight", ctypes.c_long),
        ("lfItalic", ctypes.c_byte),
        ("lfUnderline", ctypes.c_byte),
        ("lfStrikeOut", ctypes.c_byte),
        ("lfCharSet", ctypes.c_byte),
        ("lfOutPrecision", ctypes.c_byte),
        ("lfClipPrecision", ctypes.c_byte),
        ("lfQuality", ctypes.c_byte),
        ("lfPitchAndFamily", ctypes.c_byte),
        ("lfFaceName", ctypes.c_wchar * 32)
    ]

class NONCLIENTMETRICS(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("iBorderWidth", ctypes.c_int),
        ("iScrollWidth", ctypes.c_int),
        ("iScrollHeight", ctypes.c_int),
        ("iCaptionWidth", ctypes.c_int),
        ("iCaptionHeight", ctypes.c_int),
        ("lfCaptionFont", LOGFONTW),
        ("iSmCaptionWidth", ctypes.c_int),
        ("iSmCaptionHeight", ctypes.c_int),
        ("lfSmCaptionFont", LOGFONTW),
        ("iMenuWidth", ctypes.c_int),
        ("iMenuHeight", ctypes.c_int),
        ("lfMenuFont", LOGFONTW),
        ("lfStatusFont", LOGFONTW),
        ("lfMessageFont", LOGFONTW),
    ]

def get_system_font():
    ncm = NONCLIENTMETRICS()
    ncm.cbSize = ctypes.sizeof(NONCLIENTMETRICS)
    ctypes.windll.user32.SystemParametersInfoW(41, ncm.cbSize, ctypes.byref(ncm), 0)
    return ncm.lfMessageFont

font_info = get_system_font()
print(f"Font Name: {font_info.lfFaceName}")
print(f"Font Height: {font_info.lfHeight}")
print(f"Font Weight: {font_info.lfWeight}")
