import sys
import ctypes
import screen_brightness_control as sbc
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QLabel,
    QSlider,
    QWidget,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import (
    QFont,
    QPainter,
    QColor,
    QPainterPath,
    QLinearGradient,
    QIcon,
    QBrush,
    QPalette,
    QRadialGradient,
)
from PyQt5.QtWidgets import QProxyStyle, QStyle, QStyleOptionSlider


class HollowHandleStyle(QProxyStyle):
    def __init__(self, accent_color: QColor, config: dict = None):
        super().__init__()
        self.config = {
            "groove.height": 4,
            "sub-page.color": accent_color,
            "add-page.color": QColor(200, 200, 200, 50),
            "handle.color": accent_color,
            "handle.ring-width": 3,
            "handle.hollow-radius": 5,
            "handle.margin": 3,
            "groove.radius": 2,
        }
        if config:
            self.config.update(config)
        w = (
            self.config["handle.margin"]
            + self.config["handle.ring-width"]
            + self.config["handle.hollow-radius"]
        )
        self.config["handle.size"] = QSize(2 * w, 2 * w)

    def subControlRect(self, cc, opt, sc, widget):
        if (
            cc != self.CC_Slider
            or opt.orientation != Qt.Horizontal
            or sc == self.SC_SliderTickmarks
        ):
            return super().subControlRect(cc, opt, sc, widget)

        rect = opt.rect

        if sc == self.SC_SliderGroove:
            h = self.config["groove.height"]
            grooveRect = QRectF(0, (rect.height() - h) // 2, rect.width(), h)
            return grooveRect.toRect()

        if sc == self.SC_SliderHandle:
            size = self.config["handle.size"]
            x = self.sliderPositionFromValue(
                opt.minimum, opt.maximum, opt.sliderPosition, rect.width()
            )
            x *= (rect.width() - size.width()) / rect.width()
            y = (rect.height() - size.height()) // 2
            sliderRect = QRectF(x, y, size.width(), size.height())
            return sliderRect.toRect()

    def drawComplexControl(self, cc, opt, painter, widget):
        if cc != self.CC_Slider or opt.orientation != Qt.Horizontal:
            return super().drawComplexControl(cc, opt, painter, widget)

        grooveRect = self.subControlRect(cc, opt, self.SC_SliderGroove, widget)
        handleRect = self.subControlRect(cc, opt, self.SC_SliderHandle, widget)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        # Draw groove
        painter.save()
        painter.translate(grooveRect.topLeft())
        groove_path = QPainterPath()
        groove_path.addRoundedRect(
            0,
            0,
            grooveRect.width(),
            self.config["groove.height"],
            self.config["groove.radius"],
            self.config["groove.radius"],
        )

        # Groove background
        painter.setBrush(self.config["add-page.color"])
        painter.drawPath(groove_path)

        # Filled groove
        filled_width = handleRect.x() - grooveRect.x() + handleRect.width() / 2
        filled_groove = QPainterPath()
        filled_groove.addRoundedRect(
            0,
            0,
            filled_width,
            self.config["groove.height"],
            self.config["groove.radius"],
            self.config["groove.radius"],
        )

        # Gradient fill
        gradient = QLinearGradient(0, 0, filled_width, 0)
        gradient.setColorAt(0, self.config["sub-page.color"].lighter(120))
        gradient.setColorAt(1, self.config["sub-page.color"])
        painter.setBrush(gradient)
        painter.drawPath(filled_groove)
        painter.restore()

        # Draw handle
        ringWidth = self.config["handle.ring-width"]
        hollowRadius = self.config["handle.hollow-radius"]
        radius = ringWidth + hollowRadius

        path = QPainterPath()
        center = handleRect.center()
        path.addEllipse(center, radius, radius)
        path.addEllipse(center, hollowRadius, hollowRadius)

        handleColor = self.config["handle.color"]
        handleColor.setAlpha(
            255 if opt.activeSubControls != self.SC_SliderHandle else 200
        )

        # Handle shadow
        painter.setPen(Qt.NoPen)
        shadow = QRadialGradient(center, radius, center)
        shadow.setColorAt(0, handleColor.lighter(150))
        shadow.setColorAt(1, handleColor)
        painter.setBrush(QBrush(shadow))
        painter.drawEllipse(center, radius + 1, radius + 1)

        # Handle main
        painter.setBrush(handleColor)
        painter.drawPath(path)


class StyledSlider(QSlider):
    def __init__(self, orientation, accent_color, parent=None):
        super().__init__(orientation, parent)
        self.setStyle(HollowHandleStyle(accent_color))
        self.setCursor(Qt.PointingHandCursor)


class BrightnessControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.accent_color = self.get_accent_color()
        self.is_dark_mode = self.get_dark_mode_status()
        self.transparency_enabled = self.get_transparency_status()

        self.setWindowTitle("Brightness Control")
        self.setGeometry(100, 100, 400, 300)
        self.setMinimumSize(350, 200)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.displays = []
        self.old_displays = []
        self.is_refreshing = False

        self.init_ui()
        self.setup_animations()
        self.refresh_displays()  # Initial load
        self.update_stylesheet()

        # Keep timer for brightness sync only (once every 1s)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_brightness_values)
        self.timer.start(1000)

    # --------------------------
    # OS/Theme/Accent utilities
    # --------------------------
    def get_transparency_status(self):
        """Check if Windows transparency effects are enabled."""
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "EnableTransparency")
            return value == 1
        except Exception:
            return True

    def get_dark_mode_status(self):
        """Check if Windows apps are in dark mode or not."""
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception as e:
            print(f"Error accessing dark mode status: {e}")
            return False

    def get_accent_color(self):
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\DWM"
            )
            value, _ = winreg.QueryValueEx(key, "AccentColor")

            # Windows typically stores this as 0xAABBGGRR.
            # Extract R, G, B in the correct order:
            r = value & 0xFF
            g = (value >> 8) & 0xFF
            b = (value >> 16) & 0xFF

            return QColor(r, g, b)
        except Exception:
            # Fallback if registry call fails
            return QColor(0, 120, 215)

    # ---------------------
    # UI Setup
    # ---------------------
    def init_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)

        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        self.title_label = QLabel("Brightness")
        self.title_label.setFont(QFont("Segoe UI Semibold", 16, QFont.Bold))

        self.refresh_button = QPushButton("⟳ Refresh")
        self.refresh_button.setFont(QFont("Segoe UI", 10))
        self.refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.refresh_displays)
        self.refresh_button.setObjectName("RefreshButton")

        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.refresh_button)
        layout.addLayout(header_layout)

        # Sliders container
        self.sliders_container = QWidget()
        self.sliders_layout = QVBoxLayout(self.sliders_container)
        self.sliders_layout.setContentsMargins(0, 3, 0, 3)
        self.sliders_layout.setSpacing(6)

        layout.addWidget(self.sliders_container)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.main_widget.setGraphicsEffect(shadow)

    def setup_animations(self):
        # Fade-in animation
        self.opacity_anim = QPropertyAnimation(self.main_widget, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.start()

    # ---------------------
    # Refresh logic
    # ---------------------
    def refresh_displays(self):
        """Refresh button handler.
        1) Checks system theme/blur/accent changes
        2) Checks added/removed monitors
        3) Updates the UI accordingly.
        """
        if self.is_refreshing:
            return

        update_geometry = False
        self.is_refreshing = True
        self.refresh_button.setText("⟳ Refreshing...")
        QTimer.singleShot(500, lambda: self.refresh_button.setText("⟳ Refresh"))

        # Restore the button text after a short delay
        QTimer.singleShot(500, lambda: self.refresh_button.setText("⟳ Refresh"))

        try:
            # 1. Check theme changes
            new_dark_mode = self.get_dark_mode_status()
            new_transparency = self.get_transparency_status()
            new_accent_color = self.get_accent_color()

            if (
                new_dark_mode != self.is_dark_mode
                or new_transparency != self.transparency_enabled
                or new_accent_color != self.accent_color
            ):
                self.is_dark_mode = new_dark_mode
                self.transparency_enabled = new_transparency
                self.accent_color = new_accent_color
                self.update_stylesheet()

                update_geometry = True

            # 2. Clear old sliders
            while self.sliders_layout.count():
                item = self.sliders_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            # 3. Get display list
            try:
                all_displays = sbc.list_monitors()
                valid_displays = []
                for d in all_displays:
                    try:
                        sbc.get_brightness(display=d)
                        valid_displays.append(d)
                    except Exception as exc:
                        print(f"Skipping display {d}: {exc}")
                self.displays = valid_displays
            except Exception as e:
                print(f"Error listing monitors: {e}")
                self.displays = []

            # Re-add sliders for each valid display
            for display in self.displays:
                try:
                    self.add_display_slider(display)
                except Exception as e:
                    print(f"Error adding slider for display {display}: {e}")

            self.sliders_container.layout().activate()
            self.main_widget.layout().activate()

            if self.old_displays != valid_displays or update_geometry == True:
                self.old_displays = valid_displays
                update_geometry = False
                try:
                    # 2) Process any pending events (ensures the above layout changes apply)
                    QApplication.processEvents()

                    # 3) Finally adjust the main window size
                    self.adjustSize()

                    # 4) Optionally schedule a final adjust in case the layout needs a second pass
                    QTimer.singleShot(0, self.adjustSize)
                except:
                    print("Failed to update size")

        finally:
            # Mark refresh done
            self.is_refreshing = False

    def add_display_slider(self, display):
        """Creates a QFrame holding a label + brightness slider."""
        frame = QFrame()
        frame.setObjectName("SliderFrame")
        # Make each frame a constant height so they won't shrink/grow
        frame.setMinimumHeight(80)
        frame.setMaximumHeight(80)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(8, 4, 8, 4)
        frame_layout.setSpacing(4)

        # Display label
        display_label = QLabel(display)
        display_label.setFont(QFont("Segoe UI Semibold", 10))
        display_label.setContentsMargins(2, 0, 0, 0)

        # Slider row
        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(0, 0, 0, 0)
        slider_row.setSpacing(5)

        brightness_slider = StyledSlider(Qt.Horizontal, self.accent_color)
        brightness_slider.setRange(0, 100)
        brightness_slider.setValue(self.get_brightness(display))
        brightness_slider.valueChanged.connect(
            lambda v, d=display: self.change_brightness(d, v)
        )

        value_label = QLabel(f"{self.get_brightness(display)}%")
        value_label.setFont(QFont("Segoe UI", 9))
        value_label.setFixedWidth(35)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        slider_row.addWidget(brightness_slider)
        slider_row.addWidget(value_label)

        frame_layout.addWidget(display_label)
        frame_layout.addLayout(slider_row)

        # Optional subtle hover effect
        # frame.enterEvent = lambda e: frame.setStyleSheet(
        #     f"background-color: {self.accent_color.lighter(150).name()};"
        # )
        # frame.leaveEvent = lambda e: frame.setStyleSheet("background-color: transparent;")

        self.sliders_layout.addWidget(frame)

        # Keep value label in sync
        brightness_slider.valueChanged.connect(lambda v: value_label.setText(f"{v}%"))

    # ---------------------
    # Brightness handling
    # ---------------------
    def change_brightness(self, display, brightness):
        try:
            sbc.set_brightness(brightness, display=display)
        except Exception as e:
            print(f"Error setting brightness for {display}: {e}")

    def update_brightness_values(self):
        """Periodically update each slider with the actual current brightness
        in case it was changed by another tool or hotkey.
        """
        try:
            for i in range(self.sliders_layout.count()):
                frame = self.sliders_layout.itemAt(i).widget()
                if frame:
                    layout = frame.layout()
                    display_label = layout.itemAt(0).widget()
                    slider_row = layout.itemAt(1).layout()
                    brightness_slider = slider_row.itemAt(0).widget()
                    brightness_value_label = slider_row.itemAt(1).widget()

                    current_brightness = self.get_brightness(display_label.text())
                    brightness_slider.blockSignals(True)
                    brightness_slider.setValue(current_brightness)
                    brightness_slider.blockSignals(False)
                    brightness_value_label.setText(f"{current_brightness}%")
        except Exception as e:
            print(f"Error updating brightness values: {e}")

    def get_brightness(self, display):
        """Safely get brightness from a display, fallback to 50% on error."""
        try:
            return sbc.get_brightness(display=display)[0]
        except Exception as e:
            print(f"Error getting brightness for {display}: {e}")

            try:
                self.refresh_displays()
            except:
                return 50  # fallback

    # ---------------------
    # Theming
    # ---------------------
    def update_stylesheet(self):
        """Re-apply dark/light theme and accent color to the entire UI."""
        text_color = "#ffffff" if self.is_dark_mode else "#333333"
        base_alpha = 240 if self.transparency_enabled else 255
        bg_color = (
            QColor(45, 45, 45, base_alpha)
            if self.is_dark_mode
            else QColor(255, 255, 255, base_alpha)
        )
        frame_color = (
            QColor(70, 70, 70, base_alpha - 40)
            if self.is_dark_mode
            else QColor(240, 240, 240, base_alpha - 40)
        )

        self.setStyleSheet(
            f"""
            #MainWidget {{
                background-color: {bg_color.name(QColor.HexArgb)};
                color: {text_color};
                border-radius: 12px;
            }}
            #SliderFrame {{
                border-radius: 6px;
                border: 1px solid {self.accent_color.darker(120).name()};
                background-color: {frame_color.name(QColor.HexArgb)};
            }}
            #RefreshButton {{
                background-color: {self.accent_color.name()};
                color: {text_color};
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 500;
            }}
            #RefreshButton:hover {{
                background-color: {self.accent_color.lighter(120).name()};
            }}
            #RefreshButton:pressed {{
                background-color: {self.accent_color.darker(120).name()};
            }}
            QLabel {{
                color: {text_color};
                font-family: 'Segoe UI';
            }}
        """
        )

    # ---------------------
    # Window moving
    # ---------------------
    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()


# -------------------------
# Main Execution
# -------------------------
if __name__ == "__main__":
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # logging.debug("App starting...")

    # try:
    #     app = QApplication(sys.argv)
    #     window = BrightnessControlApp()
    #     window.show()
    #     logging.debug("Window shown...")
    #     sys.exit(app.exec_())
    # except Exception as e:
    #     logging.error(f"Fatal error: {e}")
    app = QApplication(sys.argv)
    window = BrightnessControlApp()
    window.show()
    # logging.debug("Window shown...")
    sys.exit(app.exec_())
