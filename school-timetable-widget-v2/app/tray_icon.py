from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
import os

from infra.paths import resource_path


class TrayIcon(QSystemTrayIcon):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self._setup()

    def _setup(self):
        icon_path = resource_path(os.path.join('assets', 'app_icon.ico'))
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            self.setIcon(QIcon())
        menu = QMenu()

        self.show_action = QAction("시간표 보기", menu)
        self.show_action.triggered.connect(self.widget.show)
        menu.addAction(self.show_action)

        # Settings entries
        settings_menu = menu.addMenu("설정")

        edit_action = QAction("요일/교시/시간 편집", settings_menu)
        edit_action.triggered.connect(self.widget.open_edit_config)
        settings_menu.addAction(edit_action)

        theme_action = QAction("디자인 설정", settings_menu)
        theme_action.triggered.connect(self.widget.open_theme_settings)
        settings_menu.addAction(theme_action)

        # Toggle: 위치 고정
        lock_action = QAction("위치 고정", settings_menu)
        lock_action.setCheckable(True)
        try:
            lock_action.setChecked(bool(self.widget.config.ui.position.lock))
        except Exception:
            lock_action.setChecked(False)
        lock_action.toggled.connect(self.widget.toggle_position_lock_from_tray)
        settings_menu.addAction(lock_action)

        # Reset settings
        reset_action = QAction("설정 초기화", settings_menu)
        reset_action.triggered.connect(self.widget.reset_settings_from_tray)
        settings_menu.addAction(reset_action)

        menu.addSeparator()

        self.exit_action = QAction("종료", menu)
        self.exit_action.triggered.connect(QCoreApplication.instance().quit)
        menu.addAction(self.exit_action)

        self.setContextMenu(menu)


