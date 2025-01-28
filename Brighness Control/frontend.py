import sys
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QSlider, QWidget, QFrame,
    QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QSizePolicy,
    QProxyStyle, QSystemTrayIcon, QMenu, QStyle, QStyleOptionSlider,
    QApplication  # Add this line
)
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer, QPropertyAnimation, QEvent
from PyQt5.QtGui import (
    QColor, QPainter, QPainterPath, QLinearGradient, QIcon,
    QBrush, QRadialGradient, QFont, QPalette, QCursor
)
from backend import *


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
        if cc != self.CC_Slider or opt.orientation != Qt.Horizontal or sc == self.SC_SliderTickmarks:
            return super().subControlRect(cc, opt, sc, widget)

        rect = opt.rect
        if sc == self.SC_SliderGroove:
            h = self.config["groove.height"]
            return QRectF(0, (rect.height() - h) // 2, rect.width(), h).toRect()
            
        if sc == self.SC_SliderHandle:
            size = self.config["handle.size"]
            x = self.sliderPositionFromValue(opt.minimum, opt.maximum, opt.sliderPosition, rect.width())
            x *= (rect.width() - size.width()) / rect.width()
            y = (rect.height() - size.height()) // 2
            return QRectF(x, y, size.width(), size.height()).toRect()

    def drawComplexControl(self, cc, opt, painter, widget):
        if cc != self.CC_Slider or opt.orientation != Qt.Horizontal:
            return super().drawComplexControl(cc, opt, painter, widget)

        grooveRect = self.subControlRect(cc, opt, self.SC_SliderGroove, widget)
        handleRect = self.subControlRect(cc, opt, self.SC_SliderHandle, widget)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        painter.save()
        painter.translate(grooveRect.topLeft())
        groove_path = QPainterPath()
        groove_path.addRoundedRect(0, 0, grooveRect.width(), self.config["groove.height"], 
                                 self.config["groove.radius"], self.config["groove.radius"])

        painter.setBrush(self.config["add-page.color"])
        painter.drawPath(groove_path)

        filled_width = handleRect.x() - grooveRect.x() + handleRect.width() / 2
        filled_groove = QPainterPath()
        filled_groove.addRoundedRect(0, 0, filled_width, self.config["groove.height"],
                                   self.config["groove.radius"], self.config["groove.radius"])

        gradient = QLinearGradient(0, 0, filled_width, 0)
        gradient.setColorAt(0, self.config["sub-page.color"].lighter(120))
        gradient.setColorAt(1, self.config["sub-page.color"])
        painter.setBrush(gradient)
        painter.drawPath(filled_groove)
        painter.restore()

        ringWidth = self.config["handle.ring-width"]
        hollowRadius = self.config["handle.hollow-radius"]
        radius = ringWidth + hollowRadius
        path = QPainterPath()
        center = handleRect.center()
        path.addEllipse(center, radius, radius)
        path.addEllipse(center, hollowRadius, hollowRadius)

        handleColor = self.config["handle.color"]
        handleColor.setAlpha(255 if opt.activeSubControls != self.SC_SliderHandle else 200)

        painter.setPen(Qt.NoPen)
        shadow = QRadialGradient(center, radius, center)
        shadow.setColorAt(0, handleColor.lighter(150))
        shadow.setColorAt(1, handleColor)
        painter.setBrush(QBrush(shadow))
        painter.drawEllipse(center, radius + 1, radius + 1)

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
        self.accent_color = QColor(*get_accent_color())
        self.is_dark_mode = get_dark_mode_status()
        self.transparency_enabled = get_transparency_status()

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
        self.refresh_displays()
        self.update_stylesheet()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_brightness_values)
        self.timer.start(1000)
        
        self.tray_menu_visible = False
        self.tray_icon = QSystemTrayIcon(self)
        self.update_tray_icon()
        self.tray_icon.setToolTip("Brightness Control")
        tray_menu = QMenu()
        tray_menu.aboutToShow.connect(lambda: setattr(self, 'tray_menu_visible', True))
        tray_menu.aboutToHide.connect(lambda: setattr(self, 'tray_menu_visible', False))
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.close)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()
        self.hide()
        QApplication.instance().installEventFilter(self)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isHidden():
                self.show_window_in_tray_area()
            else:
                self.hide()

    def reposition_window(self):
        screen = QApplication.screenAt(QCursor.pos())
        if screen and self.isVisible():
            screen_geo = screen.availableGeometry()
            x = screen_geo.right() - self.width() - 10
            y = screen_geo.bottom() - self.height() - 10
            self.move(x, y)

    def show_window_in_tray_area(self):
        self.show()
        self.reposition_window()
        self.raise_()
        self.activateWindow()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.reposition_window()
        QTimer.singleShot(10, self.reposition_window)

    def init_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("MainWidget")
        self.setCentralWidget(self.main_widget)
        self.main_widget.setMinimumHeight(100)

        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        self.header_layout = QHBoxLayout()
        self.header_layout.setContentsMargins(0, 0, 0, 0)
        self.header_layout.setSpacing(10)

        self.title_label = QLabel("Brightness")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        self.refresh_button = QPushButton("⟳ Refresh")
        self.refresh_button.setFont(QFont("Segoe UI", 10))
        self.refresh_button.setMinimumWidth(85)
        self.refresh_button.setMaximumWidth(85)
        self.refresh_button.setIcon(QIcon.fromTheme("view-refresh"))
        self.refresh_button.setIconSize(QSize(16, 16))
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.refresh_displays)
        self.refresh_button.setObjectName("RefreshButton")

        self.header_layout.addWidget(self.title_label)
        self.header_layout.addWidget(self.refresh_button)
        layout.addLayout(self.header_layout)

        self.sliders_container = QWidget()
        self.sliders_layout = QVBoxLayout(self.sliders_container)
        self.sliders_layout.setContentsMargins(0, 3, 0, 3)
        self.sliders_layout.setSpacing(6)
        layout.addWidget(self.sliders_container)

        # shadow = QGraphicsDropShadowEffect()
        # shadow.setBlurRadius(20)
        # shadow.setColor(QColor(0, 0, 0, 80))
        # shadow.setOffset(0, 4)
        # self.main_widget.setGraphicsEffect(shadow)

    def calculate_min_height(self):
        self.sliders_container.updateGeometry()
        self.main_widget.updateGeometry()
        header_height = self.header_layout.sizeHint().height()
        sliders_height = self.sliders_container.sizeHint().height()
        margins = self.main_widget.layout().contentsMargins()
        spacing = self.main_widget.layout().spacing()
        total_height = header_height + sliders_height + margins.top() + margins.bottom() + spacing
        self.main_widget.setMinimumHeight(total_height)
        self.setMinimumHeight(total_height)

    def setup_animations(self):
        self.opacity_anim = QPropertyAnimation(self.main_widget, b"windowOpacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.start()

    def refresh_displays(self):
        if self.is_refreshing:
            return

        update_geometry = False
        self.is_refreshing = True
        self.refresh_button.setText("Refreshing")
        QTimer.singleShot(500, lambda: self.refresh_button.setText("⟳ Refresh"))

        try:
            new_dark_mode = get_dark_mode_status()
            new_transparency = get_transparency_status()
            new_accent_color = QColor(*get_accent_color())
            
            if (new_dark_mode != self.is_dark_mode or 
                new_transparency != self.transparency_enabled or 
                new_accent_color != self.accent_color):
                self.is_dark_mode = new_dark_mode
                self.transparency_enabled = new_transparency
                self.accent_color = new_accent_color
                self.update_stylesheet()
                update_geometry = True
                self.update_tray_icon() 


                
            while self.sliders_layout.count():
                item = self.sliders_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            try:
                all_displays = list_displays()
                valid_displays = []
                for d in all_displays:
                    try:
                        get_brightness(d)
                        valid_displays.append(d)
                    except Exception:
                        pass
                self.displays = valid_displays
            except Exception:
                self.displays = []

            for display in self.displays:
                try:
                    self.add_display_slider(display)
                except Exception:
                    pass

            if self.old_displays != self.displays or update_geometry:
                self.old_displays = self.displays
                QApplication.processEvents()
                self.calculate_min_height()
                self.reposition_window()
                QTimer.singleShot(10, self.reposition_window)
                self.adjustSize()
                QTimer.singleShot(0, self.adjustSize)

        finally:
            self.is_refreshing = False

    def add_display_slider(self, display):
        frame = QFrame()
        frame.setObjectName("SliderFrame")
        if self.is_dark_mode:
            border_color = "rgba(255, 255, 255, 15)"
        else:
            border_color = "rgba(0, 0, 0, 15)"

        frame.setStyleSheet(f"""
            #SliderFrame {{
                background-color: transparent;
                border-radius: 6px;
                border: 1px solid {border_color};
            }}
        """)
        frame.setMinimumHeight(60)
        frame.setMaximumHeight(60)
        frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(8, 4, 8, 4)
        frame_layout.setSpacing(4)

        display_label = QLabel(display)
        display_label.setObjectName("DisplayLabel")
        display_label.setFont(QFont("Segoe UI", 10))
        display_label.setContentsMargins(2, 0, 0, 0)

        slider_row = QHBoxLayout()
        slider_row.setContentsMargins(0, 0, 0, 0)
        slider_row.setSpacing(5)

        brightness_slider = StyledSlider(Qt.Horizontal, self.accent_color)
        brightness_slider.setRange(0, 100)
        brightness_slider.setValue(get_brightness(display))
        brightness_slider.valueChanged.connect(
            lambda v, d=display: set_brightness(d, v)
        )

        value_label = QLabel(f"{get_brightness(display)}%")
        value_label.setObjectName("ValueLabel")
        value_label.setFont(QFont("Segoe UI", 10))
        value_label.setFixedWidth(35)
        value_label.setAlignment(Qt.AlignRight | Qt.AlignHCenter)

        slider_row.addWidget(brightness_slider)
        slider_row.addWidget(value_label)

        frame_layout.addWidget(display_label)
        frame_layout.addLayout(slider_row)

        frame.enterEvent = lambda e, f=frame: f.setStyleSheet(
            f"""
            #SliderFrame {{
                background-color: rgba({self.accent_color.red()}, {self.accent_color.green()}, {self.accent_color.blue()}, 13);
                border: 1px solid rgba({self.accent_color.red()}, {self.accent_color.green()}, {self.accent_color.blue()}, 30);
            }}
            """
        )
        if self.is_dark_mode:
            border_color = "rgba(255, 255, 255, 15)"
        else:
            border_color = "rgba(0, 0, 0, 15)"
        
        frame.leaveEvent = lambda e, f=frame: f.setStyleSheet(f"""
            #SliderFrame {{
                background-color: transparent;
                border: 1px solid {border_color};
            }}
        """)

        self.sliders_layout.addWidget(frame)
        brightness_slider.valueChanged.connect(lambda v: value_label.setText(f"{v}%"))

    def update_brightness_values(self):
        try:
            for i in range(self.sliders_layout.count()):
                frame = self.sliders_layout.itemAt(i).widget()
                if frame:
                    layout = frame.layout()
                    display_label = layout.itemAt(0).widget()
                    slider_row = layout.itemAt(1).layout()
                    brightness_slider = slider_row.itemAt(0).widget()
                    brightness_value_label = slider_row.itemAt(1).widget()

                    current_brightness = get_brightness(display_label.text())
                    brightness_slider.blockSignals(True)
                    brightness_slider.setValue(current_brightness)
                    brightness_slider.blockSignals(False)
                    brightness_value_label.setText(f"{current_brightness}%")
        except Exception as e:
            print(f"Update error: {e}")

    def update_stylesheet(self):
        text_color = "#ffffff" if self.is_dark_mode else "#333333"
        base_alpha = 240 if self.transparency_enabled else 255
        bg_color = QColor(45, 45, 45, base_alpha) if self.is_dark_mode else QColor(255, 255, 255, base_alpha)
        frame_color = QColor(70, 70, 70, base_alpha - 40) if self.is_dark_mode else QColor(240, 240, 240, base_alpha - 40)

        self.setStyleSheet(f"""
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
                font-weight: 500;
            }}
            #TitleLabel {{ padding-left: 8px; }}
        """)
    def update_tray_icon(self):
        """Update tray icon based on dark/light mode"""
        icon_path = "icon_light.png" if not self.is_dark_mode else "icon_dark.png"
        self.tray_icon.setIcon(QIcon(icon_path))
    
    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.old_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.WindowDeactivate:
            if self.isVisible() and not self.tray_menu_visible:
                self.hide()
                return True
        return super().eventFilter(obj, event)

    def focusOutEvent(self, event):
        if self.isVisible() and not self.tray_menu_visible:
            self.hide()
        super().focusOutEvent(event)