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
import ctypes.wintypes
import threading

class BrightnessMonitor:
    def __init__(self):
        self.running = False
        self.hwnd = None

    def start(self):
        self.running = True
        threading.Thread(target=self._monitor_brightness).start()

    def stop(self):
        self.running = False
        if self.hwnd:
            ctypes.windll.user32.DestroyWindow(self.hwnd)

    def _monitor_brightness(self):
        WNDPROCTYPE = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.c_uint, ctypes.c_int, ctypes.c_int)
        self.hwnd = ctypes.windll.user32.CreateWindowExW(0, "STATIC", "BrightnessMonitor", 0, 0, 0, 0, 0, 0, 0, 0, 0)
        ctypes.windll.user32.UpdateWindow(self.hwnd)

        def window_proc(hwnd, msg, wparam, lparam):
            if msg == ctypes.windll.user32.RegisterPowerSettingNotification:
                print("Brightness changed")
            return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

        wndproc = WNDPROCTYPE(window_proc)
        ctypes.windll.user32.SetWindowLongPtrW(self.hwnd, -4, wndproc)

        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", ctypes.wintypes.DWORD),
                ("Data2", ctypes.wintypes.WORD),
                ("Data3", ctypes.wintypes.WORD),
                ("Data4", ctypes.c_byte * 8)
            ]

        power_setting_guid = GUID(0xaded5e82, 0xb909, 0x4619, (0x99, 0x49, 0xf5, 0xd7, 0x1d, 0xac, 0x0b, 0xcb))
        ctypes.windll.user32.RegisterPowerSettingNotification(self.hwnd, ctypes.byref(power_setting_guid), 0)

        msg = ctypes.wintypes.MSG()
        while self.running:
            if ctypes.windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))

if __name__ == "__main__":
    monitor = BrightnessMonitor()
    monitor.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        monitor.stop()

