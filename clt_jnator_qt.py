import calendar
import csv
from datetime import datetime
from datetime import timedelta
import json
from pathlib import Path
import sys
import unicodedata

from PySide6.QtCore import Qt, QTime, QTimer
from PySide6.QtGui import QAction, QColor, QFont, QFontDatabase, QIcon, QLinearGradient, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QStyle,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QComboBox,
    QLineEdit,
    QSpinBox,
    QTimeEdit,
    QWidgetAction,
)
from winotify import Notification, audio


APP_NAME = "CLT-Jnator 3000"
ASSET_DIR = "assets"
FONT_AWESOME_FILE = "fa-solid-900.ttf"
MANROPE_FILE = "Manrope-Variable.ttf"
APP_ICON_FILE = "app_icon_current.ico"
SETTINGS_FILE = "ui_settings.json"
REMINDERS_FILE = "reminders.json"
ACCENT = "#5a5ff0"
ACCENT_DARK = "#393db8"
ACCENT_LIGHT = "#eef0ff"
CARD_BG = "#f7f8ff"
TEXT_DARK = "#24264a"
TEXT_MUTED = "#777cc2"


def resource_path(relative_path):
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


class GradientWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.gradient_start = "#9da3ff"
        self.gradient_end = "#4d48df"

    def set_gradient(self, start, end):
        self.gradient_start = start
        self.gradient_end = end
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, self.gradient_start)
        gradient.setColorAt(1.0, self.gradient_end)
        painter.fillRect(self.rect(), gradient)
        super().paintEvent(event)


class NoteDialog(QDialog):
    def __init__(self, task_name, start_text, end_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar atividade")
        self.setModal(True)
        self.setMinimumSize(520, 360)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self.note = ""
        ui_family = getattr(parent, "ui_family", "Manrope")
        accent = getattr(parent, "accent", ACCENT)
        accent_dark = getattr(parent, "accent_dark", ACCENT_DARK)
        theme_text = getattr(parent, "theme_text", TEXT_DARK)
        theme_muted = getattr(parent, "theme_muted", TEXT_MUTED)
        theme_border = getattr(parent, "theme_border", "#d8dbff")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        title = QLabel(f'Encerrando "{task_name}"')
        title.setObjectName("dialogTitle")
        period = QLabel(f"{start_text} -> {end_text}")
        period.setObjectName("muted")

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Descreva o que foi feito nesta parte da tarefa.")

        self.override_check = QCheckBox("Permitir confirmar com menos de 50 caracteres")
        self.override_check.setChecked(False)

        footer = QHBoxLayout()
        self.counter_label = QLabel("0/50 caracteres")
        self.counter_label.setObjectName("muted")
        footer.addWidget(self.counter_label)
        footer.addStretch()

        self.confirm_button = QPushButton("Confirmar")
        self.confirm_button.setEnabled(False)
        footer.addWidget(self.confirm_button)

        layout.addWidget(title)
        layout.addWidget(period)
        layout.addWidget(self.text_edit, 1)
        layout.addWidget(self.override_check)
        layout.addLayout(footer)

        self.text_edit.textChanged.connect(self.refresh_state)
        self.override_check.toggled.connect(self.refresh_state)
        self.confirm_button.clicked.connect(self.confirm)

        self.setStyleSheet(
            f"""
            QDialog {{
                background: {CARD_BG};
            }}
            QLabel {{
                color: {theme_text};
                font-family: {ui_family};
                font-size: 10pt;
            }}
            QLabel#dialogTitle {{
                color: {accent_dark};
                font-size: 12pt;
                font-weight: 700;
            }}
            QLabel#muted {{
                color: {theme_muted};
            }}
            QTextEdit {{
                background: #ffffff;
                color: {theme_text};
                border: 1px solid {theme_border};
                border-radius: 14px;
                padding: 10px;
                selection-background-color: {accent};
                font-family: {ui_family};
            }}
            QCheckBox {{
                color: {theme_muted};
                font-family: {ui_family};
                font-size: 10pt;
            }}
            QPushButton {{
                background: {accent};
                color: white;
                border: 0;
                border-radius: 12px;
                padding: 9px 18px;
                font-weight: 700;
            }}
            QPushButton:disabled {{
                background: #dfe1f2;
                color: #9ca0c9;
            }}
            """
        )

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if self.confirm_button.isEnabled():
                self.confirm()
            return
        if event.key() == Qt.Key_Escape:
            return
        super().keyPressEvent(event)

    def refresh_state(self):
        text = self.text_edit.toPlainText().strip()
        self.counter_label.setText(f"{len(text)}/50 caracteres")
        self.confirm_button.setEnabled(len(text) >= 50 or self.override_check.isChecked())

    def confirm(self):
        text = self.text_edit.toPlainText().strip()
        if len(text) < 50 and not self.override_check.isChecked():
            return
        self.note = text
        self.accept()


class ReminderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Novo lembrete")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.reminder = None

        ui_family = getattr(parent, "ui_family", "Manrope")
        accent = getattr(parent, "accent", ACCENT)
        accent_dark = getattr(parent, "accent_dark", ACCENT_DARK)
        theme_text = getattr(parent, "theme_text", TEXT_DARK)
        theme_muted = getattr(parent, "theme_muted", TEXT_MUTED)
        theme_border = getattr(parent, "theme_border", "#d8dbff")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(12)

        title = QLabel("Criar lembrete")
        title.setObjectName("dialogTitle")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome do lembrete")

        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Descricao")
        self.description_input.setFixedHeight(76)

        self.mode_input = QComboBox()
        self.mode_input.addItem("Timer", "timer")
        self.mode_input.addItem("Horario fixo", "fixed")

        self.timer_minutes_input = QSpinBox()
        self.timer_minutes_input.setRange(1, 1440)
        self.timer_minutes_input.setValue(15)
        self.timer_minutes_input.setSuffix(" min")

        self.fixed_time_input = QTimeEdit()
        self.fixed_time_input.setDisplayFormat("HH:mm")
        self.fixed_time_input.setTime(QTime.currentTime().addSecs(3600))

        self.recurrence_input = QComboBox()
        self.recurrence_input.addItem("Nao recorrente", "none")
        self.recurrence_input.addItem("Diario", "daily")
        self.recurrence_input.addItem("Semanal", "weekly")
        self.recurrence_input.addItem("Mensal no dia X", "monthly")

        self.weekday_input = QComboBox()
        for index, label in enumerate(["Segunda", "Terca", "Quarta", "Quinta", "Sexta", "Sabado", "Domingo"]):
            self.weekday_input.addItem(label, index)
        self.weekday_input.setCurrentIndex(datetime.now().weekday())

        self.month_day_input = QSpinBox()
        self.month_day_input.setRange(1, 31)
        self.month_day_input.setValue(datetime.now().day)

        form.addRow("Nome", self.name_input)
        form.addRow("Descricao", self.description_input)
        form.addRow("Modo", self.mode_input)
        self.timer_label = QLabel("Timer")
        self.fixed_time_label = QLabel("Horario")
        self.recurrence_label = QLabel("Recorrencia")
        self.weekday_label = QLabel("Dia da semana")
        self.month_day_label = QLabel("Dia do mes")
        form.addRow(self.timer_label, self.timer_minutes_input)
        form.addRow(self.fixed_time_label, self.fixed_time_input)
        form.addRow(self.recurrence_label, self.recurrence_input)
        form.addRow(self.weekday_label, self.weekday_input)
        form.addRow(self.month_day_label, self.month_day_input)
        layout.addLayout(form)

        footer = QHBoxLayout()
        footer.addStretch()
        cancel_button = QPushButton("Cancelar")
        create_button = QPushButton("Criar")
        footer.addWidget(cancel_button)
        footer.addWidget(create_button)
        layout.addLayout(footer)

        self.mode_input.currentIndexChanged.connect(self.refresh_fields)
        self.recurrence_input.currentIndexChanged.connect(self.refresh_fields)
        cancel_button.clicked.connect(self.reject)
        create_button.clicked.connect(self.confirm)
        self.refresh_fields()

        self.setStyleSheet(
            f"""
            QDialog {{
                background: {CARD_BG};
            }}
            QLabel {{
                color: {theme_text};
                font-family: {ui_family};
                font-size: 10pt;
            }}
            QLabel#dialogTitle {{
                color: {accent_dark};
                font-size: 13pt;
                font-weight: 800;
            }}
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QTimeEdit {{
                background: #ffffff;
                color: {theme_text};
                border: 1px solid {theme_border};
                border-radius: 10px;
                padding: 7px 9px;
                font-family: {ui_family};
                selection-background-color: {accent};
            }}
            QComboBox::drop-down {{
                border: 0;
                width: 24px;
            }}
            QPushButton {{
                background: {accent};
                color: white;
                border: 0;
                border-radius: 12px;
                padding: 9px 18px;
                font-weight: 700;
                font-family: {ui_family};
            }}
            QPushButton:hover {{
                background: {accent_dark};
            }}
            """
        )

    def refresh_fields(self):
        mode = self.mode_input.currentData()
        recurrence = self.recurrence_input.currentData()
        timer_mode = mode == "timer"
        fixed_mode = mode == "fixed"

        self.timer_label.setVisible(timer_mode)
        self.timer_minutes_input.setVisible(timer_mode)
        self.fixed_time_label.setVisible(fixed_mode)
        self.fixed_time_input.setVisible(fixed_mode)
        self.recurrence_label.setVisible(fixed_mode)
        self.recurrence_input.setVisible(fixed_mode)

        show_weekday = fixed_mode and recurrence == "weekly"
        show_month_day = fixed_mode and recurrence == "monthly"
        self.weekday_label.setVisible(show_weekday)
        self.weekday_input.setVisible(show_weekday)
        self.month_day_label.setVisible(show_month_day)
        self.month_day_input.setVisible(show_month_day)
        self.resize_to_visible_fields()

    def resize_to_visible_fields(self):
        layout = self.layout()
        if layout is not None:
            layout.invalidate()
            layout.activate()
        self.adjustSize()
        self.resize(max(self.width(), 500), min(max(self.sizeHint().height(), 320), 620))

    def confirm(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Nome obrigatorio", "Informe um nome para o lembrete.")
            return

        mode = self.mode_input.currentData()
        recurrence = "daily" if mode == "timer" else self.recurrence_input.currentData()

        self.reminder = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            "name": name,
            "description": self.description_input.toPlainText().strip(),
            "mode": mode,
            "timer_minutes": self.timer_minutes_input.value(),
            "fixed_time": self.fixed_time_input.time().toString("HH:mm"),
            "recurrence": recurrence,
            "weekday": self.weekday_input.currentData(),
            "month_day": self.month_day_input.value(),
            "next_due": None,
            "last_triggered_minute": "",
        }
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(resource_path(Path(ASSET_DIR) / APP_ICON_FILE))))
        self.resize(820, 700)
        self.setMinimumSize(680, 560)

        self.tasks = []
        self.current_task = None
        self.task_counter = 0
        self.selected_task_id = None
        self.dirty = False
        self.has_saved = False
        self.last_saved_path = None
        self.force_exit = False
        self.context_menu_open = False
        self.reminders = self.load_reminders()

        self.icon_family = self.load_icon_font()
        self.ui_family = self.load_ui_font()
        self.setFont(QFont(self.ui_family, 10))
        self.accent = self.load_settings().get("accent", ACCENT)
        self.apply_theme_values(self.accent)

        self.build_menu()
        self.build_ui()

        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.refresh_view)
        self.timer.start()

        self.reminder_timer = QTimer(self)
        self.reminder_timer.setInterval(15000)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start()

    def load_icon_font(self):
        font_path = resource_path(Path(ASSET_DIR) / FONT_AWESOME_FILE)
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id < 0:
            return "Segoe UI"
        families = QFontDatabase.applicationFontFamilies(font_id)
        return families[0] if families else "Segoe UI"

    def load_ui_font(self):
        font_path = resource_path(Path(ASSET_DIR) / MANROPE_FILE)
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id < 0:
            return "Manrope"
        families = QFontDatabase.applicationFontFamilies(font_id)
        return families[0] if families else "Manrope"

    def load_settings(self):
        settings_path = self.get_settings_path()
        if not settings_path.exists():
            return {}
        try:
            return json.loads(settings_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

    def save_settings(self):
        settings_path = self.get_settings_path()
        settings_path.write_text(
            json.dumps({"accent": self.accent}, indent=2),
            encoding="utf-8",
        )

    @staticmethod
    def get_settings_path():
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / SETTINGS_FILE
        return Path(__file__).resolve().parent / SETTINGS_FILE

    @staticmethod
    def get_reminders_path():
        if getattr(sys, "frozen", False):
            return Path(sys.executable).resolve().parent / REMINDERS_FILE
        return Path(__file__).resolve().parent / REMINDERS_FILE

    def load_reminders(self):
        reminders_path = self.get_reminders_path()
        if not reminders_path.exists():
            return []
        try:
            raw_reminders = json.loads(reminders_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

        reminders = []
        now = datetime.now()
        for reminder in raw_reminders:
            if not isinstance(reminder, dict):
                continue
            reminder = self.normalize_loaded_reminder(reminder)
            if reminder is None:
                continue
            due = reminder.get("next_due")
            if due is None or due <= now:
                due = self.calculate_initial_reminder_due(reminder)
            reminder["next_due"] = due
            reminders.append(reminder)
        return reminders

    def save_reminders(self):
        reminders_path = self.get_reminders_path()
        serializable = []
        for reminder in self.reminders:
            stored = dict(reminder)
            due = stored.get("next_due")
            stored["next_due"] = self.format_timestamp(due) if due is not None else ""
            serializable.append(stored)
        reminders_path.write_text(
            json.dumps(serializable, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def normalize_loaded_reminder(self, reminder):
        required_defaults = {
            "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            "name": "",
            "description": "",
            "mode": "timer",
            "timer_minutes": 15,
            "fixed_time": "09:00",
            "recurrence": "daily",
            "weekday": 0,
            "month_day": 1,
            "last_triggered_minute": "",
        }
        normalized = {**required_defaults, **reminder}
        if not normalized["name"]:
            return None

        try:
            normalized["timer_minutes"] = int(normalized["timer_minutes"])
            normalized["weekday"] = int(normalized["weekday"])
            normalized["month_day"] = int(normalized["month_day"])
        except (TypeError, ValueError):
            return None

        next_due = normalized.get("next_due")
        normalized["next_due"] = self.parse_timestamp(next_due) if next_due else None
        return normalized

    def apply_theme_values(self, accent):
        self.accent = self.normalize_hex(accent) or ACCENT
        self.accent_dark = self.adjust_hex(self.accent, -0.28)
        self.accent_deep = self.adjust_hex(self.accent, -0.42)
        self.accent_light = self.mix_hex(self.accent, "#ffffff", 0.84)
        self.accent_soft = self.mix_hex(self.accent, "#ffffff", 0.94)
        self.gradient_start = self.mix_hex(self.accent, "#ffffff", 0.34)
        self.gradient_end = self.adjust_hex(self.accent, -0.22)
        self.theme_text = self.adjust_hex(self.accent, -0.58)
        self.theme_muted = self.mix_hex(self.accent, "#ffffff", 0.30)
        self.theme_border = self.mix_hex(self.accent, "#ffffff", 0.76)
        self.system_font = "Segoe UI"
        self.selection = self.accent

    def on_accent_changed(self, value):
        normalized = self.normalize_hex(value)
        if normalized is None:
            return
        self.apply_theme_values(normalized)
        self.save_settings()
        self.apply_stylesheet()

    @staticmethod
    def normalize_hex(value):
        value = value.strip()
        if not value:
            return None
        if not value.startswith("#"):
            value = f"#{value}"
        if len(value) != 7:
            return None
        try:
            int(value[1:], 16)
        except ValueError:
            return None
        return value.lower()

    @staticmethod
    def hex_to_rgb(value):
        return tuple(int(value[index:index + 2], 16) for index in (1, 3, 5))

    @staticmethod
    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*[max(0, min(255, int(channel))) for channel in rgb])

    def mix_hex(self, base, target, amount):
        base_rgb = self.hex_to_rgb(base)
        target_rgb = self.hex_to_rgb(target)
        return self.rgb_to_hex(
            base_channel + (target_channel - base_channel) * amount
            for base_channel, target_channel in zip(base_rgb, target_rgb)
        )

    def adjust_hex(self, base, amount):
        target = "#000000" if amount < 0 else "#ffffff"
        return self.mix_hex(base, target, abs(amount))

    def build_menu(self):
        file_menu = self.menuBar().addMenu("Arquivo")
        save_action = QAction("Salvar como", self)
        save_action.triggered.connect(self.save_as)
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.exit_without_saving)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        ui_menu = self.menuBar().addMenu("Interface")
        accent_action = QWidgetAction(self)
        accent_host = QWidget()
        accent_layout = QHBoxLayout(accent_host)
        accent_layout.setContentsMargins(10, 6, 10, 6)
        accent_label = QLabel("Cor")
        accent_label.setFont(QFont(self.system_font, 9))
        self.accent_input = QLineEdit(self.accent)
        self.accent_input.setFont(QFont(self.system_font, 9))
        self.accent_input.setMaxLength(7)
        self.accent_input.setPlaceholderText("#5a5ff0")
        self.accent_input.textChanged.connect(self.on_accent_changed)
        accent_layout.addWidget(accent_label)
        accent_layout.addWidget(self.accent_input)
        accent_action.setDefaultWidget(accent_host)
        ui_menu.addAction(accent_action)

        reminders_menu = self.menuBar().addMenu("Lembretes")
        new_reminder_action = QAction("Novo lembrete", self)
        new_reminder_action.triggered.connect(self.create_reminder)
        reminders_menu.addAction(new_reminder_action)

    def build_ui(self):
        self.root_widget = GradientWindow()
        self.root_widget.set_gradient(self.gradient_start, self.gradient_end)
        root_layout = QVBoxLayout(self.root_widget)
        root_layout.setContentsMargins(54, 42, 54, 42)

        shadow_host = QFrame()
        shadow_host.setObjectName("shadowHost")
        self.card_shadow = QGraphicsDropShadowEffect(self)
        self.card_shadow.setBlurRadius(46)
        self.card_shadow.setOffset(0, 18)
        card_shadow_color = QColor(self.accent_deep)
        card_shadow_color.setAlphaF(0.30)
        self.card_shadow.setColor(card_shadow_color)
        shadow_host.setGraphicsEffect(self.card_shadow)

        card = QFrame()
        card.setObjectName("card")
        shadow_layout = QVBoxLayout(shadow_host)
        shadow_layout.setContentsMargins(0, 0, 0, 0)
        shadow_layout.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(34, 30, 34, 30)
        card_layout.setSpacing(16)

        self.task_label = QLabel("Nenhuma tarefa em andamento")
        self.task_label.setObjectName("mutedTitle")
        self.task_label.setAlignment(Qt.AlignCenter)

        self.time_label = QLabel("00:00:00")
        self.time_label.setObjectName("timeLabel")
        self.time_label.setAlignment(Qt.AlignCenter)

        button_row = QHBoxLayout()
        button_row.setAlignment(Qt.AlignCenter)
        button_row.setSpacing(18)
        self.start_button = self.create_round_button("\uf04b", "Iniciar")
        self.stop_button = self.create_round_button("\uf04d", "Parar", secondary=True)
        self.stop_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_new_task)
        self.stop_button.clicked.connect(self.stop_current_task)
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)

        self.task_list = QListWidget()
        self.task_list.setObjectName("softList")
        self.task_list.itemSelectionChanged.connect(self.on_task_selected)
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_task_context_menu)

        self.parts_label = QLabel("Partes da tarefa selecionada")
        self.parts_label.setObjectName("sectionLabel")

        self.parts_list = QListWidget()
        self.parts_list.setObjectName("softList")
        self.parts_list.setMaximumHeight(118)

        card_layout.addWidget(self.task_label)
        card_layout.addWidget(self.time_label)
        card_layout.addLayout(button_row)
        card_layout.addWidget(self.task_list, 4)
        card_layout.addWidget(self.parts_label)
        card_layout.addWidget(self.parts_list, 1)

        root_layout.addWidget(shadow_host)
        self.setCentralWidget(self.root_widget)

        self.apply_stylesheet()

    def apply_stylesheet(self):
        if hasattr(self, "root_widget"):
            self.root_widget.set_gradient(self.gradient_start, self.gradient_end)
        if hasattr(self, "card_shadow"):
            shadow_color = QColor(self.accent_deep)
            shadow_color.setAlphaF(0.30)
            self.card_shadow.setColor(shadow_color)
        for button in getattr(self, "round_buttons", []):
            shadow = button.graphicsEffect()
            if isinstance(shadow, QGraphicsDropShadowEffect):
                shadow_color = QColor(self.accent_deep)
                shadow_color.setAlphaF(0.30)
                shadow.setColor(shadow_color)

        self.setStyleSheet(
            f"""
            QMenuBar {{
                background: #f8f8ff;
                color: {self.theme_text};
                font-family: {self.system_font};
            }}
            QMenuBar::item:selected {{
                background: {self.accent_light};
            }}
            QMenu {{
                background: #ffffff;
                color: {self.theme_text};
                border: 1px solid {self.theme_border};
                padding: 6px;
                font-family: {self.system_font};
            }}
            QMenu::item {{
                padding: 7px 24px;
                border-radius: 7px;
            }}
            QMenu::item:selected {{
                background: {self.accent_light};
                color: {self.accent_dark};
            }}
            QFrame#card {{
                background: {CARD_BG};
                border-radius: 34px;
                border: 1px solid rgba(255, 255, 255, 180);
            }}
            QLabel {{
                font-family: {self.ui_family};
                color: {self.theme_text};
            }}
            QLabel#mutedTitle, QLabel#sectionLabel {{
                color: {self.theme_muted};
                font-size: 11pt;
                font-weight: 700;
            }}
            QLabel#timeLabel {{
                color: {self.accent_dark};
                font-size: 42pt;
                font-weight: 800;
            }}
            QPushButton#roundPrimary, QPushButton#roundSecondary {{
                min-width: 64px;
                max-width: 64px;
                min-height: 64px;
                max-height: 64px;
                border-radius: 32px;
                border: 0;
                font-size: 20pt;
            }}
            QPushButton#roundPrimary {{
                background: {self.accent};
                color: {self.accent_light};
            }}
            QPushButton#roundPrimary:hover {{
                background: {self.accent_dark};
            }}
            QPushButton#roundSecondary {{
                background: {self.accent_light};
                color: {self.theme_muted};
            }}
            QPushButton#roundSecondary:hover {{
                background: {self.accent_soft};
            }}
            QPushButton#roundSecondary:disabled {{
                background: {self.accent_soft};
                color: {self.theme_muted};
            }}
            QListWidget#softList {{
                background: #fbfbff;
                color: {self.theme_text};
                border: 1px solid {self.theme_border};
                border-radius: 20px;
                padding: 10px;
                font-family: {self.ui_family};
                font-size: 10pt;
                outline: 0;
            }}
            QListWidget#softList::item {{
                padding: 8px 10px;
                border-radius: 10px;
            }}
            QListWidget#softList::item:selected {{
                background: {self.accent};
                color: white;
            }}
            QLineEdit {{
                background: #ffffff;
                color: {self.theme_text};
                border: 1px solid {self.theme_border};
                border-radius: 8px;
                padding: 5px 8px;
                font-family: {self.system_font};
                min-width: 86px;
            }}
            """
        )

    def create_round_button(self, icon, tooltip, secondary=False):
        button = QPushButton(icon)
        button.setToolTip(tooltip)
        button.setFont(QFont(self.icon_family, 18))
        button.setObjectName("roundSecondary" if secondary else "roundPrimary")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 9)
        shadow_color = QColor(self.accent_deep)
        shadow_color.setAlphaF(0.30)
        shadow.setColor(shadow_color)
        button.setGraphicsEffect(shadow)
        if not hasattr(self, "round_buttons"):
            self.round_buttons = []
        self.round_buttons.append(button)
        return button

    def start_new_task(self):
        if self.current_task is not None:
            self.stop_current_task()

        self.task_counter += 1
        task = {
            "id": self.task_counter,
            "name": f"Tarefa {self.task_counter}",
            "parts": [self.new_part()],
            "running": True,
        }
        self.tasks.append(task)
        self.current_task = task
        self.selected_task_id = task["id"]
        self.mark_dirty()
        self.select_task(task)
        self.refresh_view()

    def continue_selected_task(self):
        task = self.find_task(self.selected_task_id)
        if task is None or task["running"]:
            return

        if self.current_task is not None:
            self.stop_current_task()

        task["parts"].append(self.new_part())
        task["running"] = True
        self.current_task = task
        self.mark_dirty()
        self.select_task(task)
        self.refresh_view()

    def stop_current_task(self):
        if self.current_task is None:
            return

        task = self.current_task
        open_part = self.get_open_part(self.current_task)
        if open_part is not None:
            finished_at = datetime.now()
            open_part["end"] = finished_at
            task["running"] = False
            self.current_task = None
            self.refresh_view()
            dialog = NoteDialog(
                task["name"],
                self.format_timestamp(open_part["start"]),
                self.format_timestamp(finished_at),
                self,
            )
            dialog.exec()
            open_part["note"] = dialog.note
        else:
            task["running"] = False
            self.current_task = None

        self.mark_dirty()
        self.refresh_view()

    def new_part(self):
        return {"start": datetime.now(), "end": None, "note": ""}

    def get_open_part(self, task):
        for part in reversed(task["parts"]):
            if part["end"] is None:
                return part
        return None

    def refresh_view(self):
        self.stop_button.setEnabled(self.current_task is not None)

        if not self.context_menu_open:
            self.refresh_task_list()
            selected_task = self.find_task(self.selected_task_id)
            self.refresh_parts(selected_task)

        if self.current_task is None:
            self.task_label.setText("Nenhuma tarefa em andamento")
            self.time_label.setText("00:00:00")
            return

        self.task_label.setText(self.current_task["name"])
        self.time_label.setText(self.format_duration(self.get_task_elapsed(self.current_task)))

    def refresh_task_list(self):
        selected_id = self.selected_task_id
        scroll_value = self.task_list.verticalScrollBar().value()
        self.task_list.blockSignals(True)

        if self.task_list.count() != len(self.tasks):
            self.task_list.clear()
            for task in self.tasks:
                self.task_list.addItem(self.format_task_row(task))
        else:
            for row, task in enumerate(self.tasks):
                item = self.task_list.item(row)
                text = self.format_task_row(task)
                if item.text() != text:
                    item.setText(text)

        selected_row = -1
        for row, task in enumerate(self.tasks):
            if task["id"] == selected_id:
                selected_row = row
                break
        if selected_row >= 0:
            self.task_list.setCurrentRow(selected_row)

        self.task_list.verticalScrollBar().setValue(scroll_value)
        self.task_list.blockSignals(False)

    def format_task_row(self, task):
        status = "rodando" if task["running"] else "parada"
        elapsed = self.format_duration(self.get_task_elapsed(task))
        first_start = self.format_timestamp(task["parts"][0]["start"])
        return f'{task["name"]} - {elapsed} - inicio {first_start} ({status})'

    def refresh_parts(self, task):
        self.parts_list.clear()
        if task is None:
            return

        for index, part in enumerate(task["parts"], start=1):
            start = self.format_timestamp(part["start"])
            end = self.format_timestamp(part["end"]) if part["end"] is not None else "em andamento"
            note_status = "com texto" if part["note"] else "sem texto"
            self.parts_list.addItem(f"Parte {index}: {start} -> {end} ({note_status})")

    def on_task_selected(self):
        row = self.task_list.currentRow()
        if row < 0 or row >= len(self.tasks):
            return
        task = self.tasks[row]
        self.selected_task_id = task["id"]
        self.refresh_parts(task)

    def select_task(self, task):
        self.selected_task_id = task["id"]
        try:
            row = self.tasks.index(task)
        except ValueError:
            return
        self.task_list.setCurrentRow(row)

    def show_task_context_menu(self, position):
        row = self.task_list.indexAt(position).row()
        if row < 0 or row >= len(self.tasks):
            return

        task = self.tasks[row]
        self.selected_task_id = task["id"]
        self.task_list.setCurrentRow(row)

        menu = QMenu(self)
        continue_action = menu.addAction("Continuar")
        continue_action.setEnabled(not task["running"])
        rename_action = menu.addAction("Renomear")

        self.context_menu_open = True
        action = menu.exec(self.task_list.mapToGlobal(position))
        self.context_menu_open = False

        if action == continue_action:
            self.continue_selected_task()
        elif action == rename_action:
            self.rename_selected_task()
        self.refresh_view()

    def rename_selected_task(self):
        task = self.find_task(self.selected_task_id)
        if task is None:
            return

        new_name, ok = QInputDialog.getText(self, "Renomear tarefa", "Nome:", text=task["name"])
        if ok and new_name.strip():
            task["name"] = new_name.strip()
            self.mark_dirty()
            self.refresh_view()

    def create_reminder(self):
        dialog = ReminderDialog(self)
        if dialog.exec() != QDialog.Accepted or dialog.reminder is None:
            return

        reminder = dialog.reminder
        reminder["next_due"] = self.calculate_initial_reminder_due(reminder)
        self.reminders.append(reminder)
        self.save_reminders()
        due_text = self.format_timestamp(reminder["next_due"])
        QMessageBox.information(
            self,
            "Lembrete criado",
            f'Lembrete "{reminder["name"]}" criado para {due_text}.',
        )

    def check_reminders(self):
        now = datetime.now()
        for reminder in self.reminders:
            due = reminder.get("next_due")
            if due is None or now < due:
                continue

            due_minute = due.strftime("%Y%m%d_%H:%M")
            if reminder.get("last_triggered_minute") == due_minute:
                continue

            reminder["last_triggered_minute"] = due_minute
            self.show_reminder(reminder)
            reminder["next_due"] = self.calculate_next_reminder_due(reminder, due)
            self.save_reminders()

    def show_reminder(self, reminder):
        description = reminder["description"] or "Sem descricao."
        try:
            toast = Notification(
                app_id=APP_NAME,
                title=f'Lembrete: {reminder["name"]}',
                msg=description,
                icon=str(resource_path(Path(ASSET_DIR) / APP_ICON_FILE)),
                duration="long",
            )
            toast.set_audio(audio.Default, loop=False)
            toast.show()
        except Exception:
            QMessageBox.information(
                self,
                f'Lembrete: {reminder["name"]}',
                f'{reminder["name"]}\n\n{description}',
            )

    def calculate_initial_reminder_due(self, reminder):
        now = datetime.now()
        if reminder["mode"] == "timer":
            return now + timedelta(minutes=reminder["timer_minutes"])
        return self.next_fixed_due(reminder, now)

    def calculate_next_reminder_due(self, reminder, previous_due):
        recurrence = reminder["recurrence"]
        if recurrence == "none":
            return None
        if reminder["mode"] == "timer":
            return previous_due + timedelta(days=1)
        if recurrence == "daily":
            return previous_due + timedelta(days=1)
        if recurrence == "weekly":
            return previous_due + timedelta(days=7)
        if recurrence == "monthly":
            return self.next_monthly_due(reminder, previous_due)
        return None

    def next_fixed_due(self, reminder, reference):
        hour, minute = [int(part) for part in reminder["fixed_time"].split(":")]
        recurrence = reminder["recurrence"]

        if recurrence == "weekly":
            days_ahead = (reminder["weekday"] - reference.weekday()) % 7
            candidate_date = reference.date() + timedelta(days=days_ahead)
            candidate = datetime.combine(candidate_date, datetime.min.time()).replace(hour=hour, minute=minute)
            if candidate <= reference:
                candidate += timedelta(days=7)
            return candidate

        if recurrence == "monthly":
            candidate = self.monthly_datetime(reference.year, reference.month, reminder["month_day"], hour, minute)
            if candidate <= reference:
                year = reference.year + (1 if reference.month == 12 else 0)
                month = 1 if reference.month == 12 else reference.month + 1
                candidate = self.monthly_datetime(year, month, reminder["month_day"], hour, minute)
            return candidate

        candidate = reference.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= reference:
            candidate += timedelta(days=1)
        return candidate

    def next_monthly_due(self, reminder, previous_due):
        hour = previous_due.hour
        minute = previous_due.minute
        year = previous_due.year + (1 if previous_due.month == 12 else 0)
        month = 1 if previous_due.month == 12 else previous_due.month + 1
        return self.monthly_datetime(year, month, reminder["month_day"], hour, minute)

    @staticmethod
    def monthly_datetime(year, month, requested_day, hour, minute):
        last_day = calendar.monthrange(year, month)[1]
        day = min(requested_day, last_day)
        return datetime(year, month, day, hour, minute)

    def closeEvent(self, event):
        if self.force_exit:
            event.accept()
            return

        if self.current_task is not None:
            self.stop_current_task()

        if self.needs_save():
            save_path = self.ask_export_path()
            if save_path is None:
                event.ignore()
                return
            self.export_tasks(save_path)
            self.mark_saved(save_path)

        event.accept()

    def exit_without_saving(self):
        confirmed = QMessageBox.warning(
            self,
            "Sair sem salvar",
            "Sair sem salvar? Alteracoes nao salvas serao perdidas.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirmed != QMessageBox.Yes:
            return
        self.force_exit = True
        self.close()

    def save_as(self):
        save_path = self.ask_export_path()
        if save_path is None:
            return
        self.export_tasks(save_path)
        self.mark_saved(save_path)
        QMessageBox.information(self, "Arquivo salvo", f"Relatorio salvo em:\n{save_path}")

    def ask_export_path(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar relatorio de tarefas",
            str(Path.cwd() / f"relatorio_tarefas_{timestamp}.csv"),
            "CSV (*.csv);;Texto Markdown (*.txt);;Markdown (*.md)",
        )
        if not filename:
            return None

        path = Path(filename)
        if path.suffix.lower() not in {".csv", ".txt", ".md"}:
            path = path.with_suffix(".csv")
        return path

    def mark_dirty(self):
        self.dirty = True

    def mark_saved(self, path):
        self.dirty = False
        self.has_saved = True
        self.last_saved_path = path

    def needs_save(self):
        return self.dirty or not self.has_saved

    def export_tasks(self, path):
        if path.suffix.lower() == ".csv":
            self.export_csv(path)
            return
        self.export_markdown(path)

    def export_csv(self, path):
        headers = [
            "Tarefa",
            "Subtarefa",
            "Inicio geral",
            "Fim geral",
            "Inicio parte",
            "Fim parte",
            "Duracao",
            "Descricao",
        ]

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for task in self.tasks:
                writer.writerow([
                    task["name"],
                    "",
                    self.format_timestamp(self.get_task_start(task)),
                    self.format_timestamp(self.get_task_end(task)),
                    "",
                    "",
                    self.format_duration(self.get_task_elapsed(task)),
                    "",
                ])

                for index, part in enumerate(task["parts"], start=1):
                    writer.writerow([
                        "",
                        f"Parte {index}",
                        "",
                        "",
                        self.format_timestamp(part["start"]),
                        self.format_timestamp(part["end"]),
                        self.format_duration(self.get_part_elapsed(part)),
                        part["note"],
                    ])

            writer.writerow([])
            writer.writerow([])
            writer.writerow([])
            writer.writerow(["Resumo de horas"])
            writer.writerow(["Inicio", "Almoco", "Retorno Almoco", "Fim"])
            writer.writerow(self.get_csv_time_summary())

    def export_markdown(self, path):
        generated_at = self.format_timestamp(datetime.now())
        lines = [
            "# Relatorio de Tarefas",
            "",
            f"Gerado em: `{generated_at}`",
            "",
            "## Resumo",
            "",
            "| Tarefa | Inicio geral | Fim geral | Duracao | Partes |",
            "| --- | --- | --- | --- | ---: |",
        ]

        for task in self.tasks:
            lines.append(
                "| "
                f"{self.escape_markdown_table(task['name'])} | "
                f"`{self.format_timestamp(self.get_task_start(task))}` | "
                f"`{self.format_timestamp(self.get_task_end(task))}` | "
                f"`{self.format_duration(self.get_task_elapsed(task))}` | "
                f"{len(task['parts'])} |"
            )

        if not self.tasks:
            lines.append("| Nenhuma tarefa registrada |  |  | `00:00:00` | 0 |")

        lines.extend(["", "## Detalhes", ""])

        for task in self.tasks:
            lines.extend([
                f"### {task['name']}",
                "",
                f"- Inicio geral: `{self.format_timestamp(self.get_task_start(task))}`",
                f"- Fim geral: `{self.format_timestamp(self.get_task_end(task))}`",
                f"- Duracao total: `{self.format_duration(self.get_task_elapsed(task))}`",
                "",
                "| Parte | Inicio | Fim | Duracao | Descricao |",
                "| ---: | --- | --- | --- | --- |",
            ])

            for index, part in enumerate(task["parts"], start=1):
                note = self.markdown_single_line(part["note"])
                lines.append(
                    "| "
                    f"{index} | "
                    f"`{self.format_timestamp(part['start'])}` | "
                    f"`{self.format_timestamp(part['end'])}` | "
                    f"`{self.format_duration(self.get_part_elapsed(part))}` | "
                    f"{note} |"
                )

            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")

    def find_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def get_task_start(self, task):
        return task["parts"][0]["start"]

    def get_task_end(self, task):
        return task["parts"][-1]["end"] or datetime.now()

    def get_part_elapsed(self, part):
        end = part["end"] or datetime.now()
        return (end - part["start"]).total_seconds()

    def get_task_elapsed(self, task):
        return sum(self.get_part_elapsed(part) for part in task["parts"])

    def get_csv_time_summary(self):
        first_file_record = self.get_first_file_record()
        lunch_task = self.get_first_lunch_task()
        lunch_start = self.get_task_start(lunch_task) if lunch_task is not None else None
        lunch_end = self.get_task_end(lunch_task) if lunch_task is not None else None
        last_file_record = self.get_last_file_record()
        return [
            self.format_hour_minute(first_file_record),
            self.format_hour_minute(lunch_start),
            self.format_hour_minute(lunch_end),
            self.format_hour_minute(last_file_record),
        ]

    def get_first_file_record(self):
        starts = [part["start"] for task in self.tasks for part in task["parts"]]
        return min(starts) if starts else None

    def get_last_file_record(self):
        ends = [part["end"] or datetime.now() for task in self.tasks for part in task["parts"]]
        return max(ends) if ends else None

    def get_first_lunch_task(self):
        for task in self.tasks:
            if self.is_lunch_name(task["name"]):
                return task
        return None

    def is_lunch_name(self, value):
        normalized = self.normalize_task_name(value)
        if "almoco" in normalized:
            return True

        common_typos = {
            "almoco",
            "almco",
            "almooco",
            "almoso",
            "almotso",
            "almorco",
            "amoco",
            "aloco",
            "almoca",
        }
        candidates = [normalized] + self.normalize_task_name_parts(value)
        return any(
            self.levenshtein_distance(candidate, typo) <= 1
            for candidate in candidates
            for typo in common_typos
        )

    @staticmethod
    def normalize_task_name(value):
        without_accents = unicodedata.normalize("NFKD", str(value))
        ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
        return "".join(character for character in ascii_text.lower() if character.isalpha())

    @staticmethod
    def normalize_task_name_parts(value):
        without_accents = unicodedata.normalize("NFKD", str(value))
        ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
        parts = []
        current = []
        for character in ascii_text.lower():
            if character.isalpha():
                current.append(character)
            elif current:
                parts.append("".join(current))
                current = []
        if current:
            parts.append("".join(current))
        return parts

    @staticmethod
    def levenshtein_distance(left, right):
        if left == right:
            return 0
        if not left:
            return len(right)
        if not right:
            return len(left)
        previous = list(range(len(right) + 1))
        for left_index, left_character in enumerate(left, start=1):
            current = [left_index]
            for right_index, right_character in enumerate(right, start=1):
                insert_cost = current[right_index - 1] + 1
                delete_cost = previous[right_index] + 1
                replace_cost = previous[right_index - 1] + (left_character != right_character)
                current.append(min(insert_cost, delete_cost, replace_cost))
            previous = current
        return previous[-1]

    @staticmethod
    def escape_markdown_table(value):
        return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")

    def markdown_single_line(self, value):
        return self.escape_markdown_table(value).replace("\r", " ").strip()

    @staticmethod
    def format_duration(total_seconds):
        total_seconds = int(total_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def format_timestamp(value):
        return value.strftime("%Y%m%d_%H:%M:%S")

    @staticmethod
    def parse_timestamp(value):
        try:
            return datetime.strptime(value, "%Y%m%d_%H:%M:%S")
        except (TypeError, ValueError):
            return None

    @staticmethod
    def format_hour_minute(value):
        if value is None:
            return ""
        minute = value.minute
        hour = value.hour
        if value.second > 30:
            minute += 1
            if minute == 60:
                minute = 0
                hour = (hour + 1) % 24
        return f"{hour:02d}:{minute:02d}"


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
