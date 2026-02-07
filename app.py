import sys, os, json, csv, datetime, calendar
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableView, QHeaderView, QFrame, QSizePolicy, 
    QAbstractItemView, QPushButton, QMenu, QFileDialog, QMessageBox, 
    QGraphicsDropShadowEffect, QScrollArea, QDialog, QLineEdit, 
    QFormLayout, QDialogButtonBox, QTabWidget, QAbstractScrollArea, QStyle,
    QProgressBar, QStyledItemDelegate, QTextEdit
)
from PySide6.QtCore import (
    Qt, QAbstractTableModel, QTimer, QRect, QPoint, Signal, 
    QPropertyAnimation, QEasingCurve, QObject, QSize, QByteArray
)
from PySide6.QtGui import QColor, QFont, QAction, QIcon, QPainter, QPolygonF

# --- CONFIGURATION ---
DATA_FILE = "habit_data.json"
ICON_NAME = "icon.ico" 
DEFAULT_HABITS = ["Workout", "Meditation", "Reading", "Coding", "Sleep 8h"]
DEFAULT_TIMES = ["07:00 AM", "08:00 AM", "09:00 PM", "10:00 PM", "11:00 PM"]

# --- THEMES ---
THEME_LIGHT = {
    "bg": "#F0F2F5", 
    "card": "#FFFFFF", "border": "#DDE2E7",
    "text_primary": "#1C1F26", "text_secondary": "#64748B",
    "shadow": "#15000000", 
    "today_bg": "#FFF9C4", "today_text": "#F57F17",
    "future_bg": "#F1F5F9", "completed": "#4CAF50",
    "chart_bg": "#FFFFFF", "chart_line": "#3B82F6", "chart_fill": "#3B82F6", "chart_bar": "#8B5CF6", "chart_grid": "#E2E8F0",
    "btn_add": "#10B981", "btn_export": "#6366F1", 
    "date_badge_bg": "#FFFFFF", "date_badge_text": "#3B82F6", "date_badge_border": "#DDE2E7",
    "btn_nav_bg": "#FFFFFF", "btn_nav_text": "#334155", "btn_nav_border": "#CBD5E1",
    "btn_filter_bg": "#0EA5E9", "btn_filter_text": "#FFFFFF",
    "row_even": "#FFFFFF", "row_odd": "#F8FAFB",
    "weekend_text": "#D32F2F", "day_text": "#64748B", "date_text": "#1C1F26",
    "undo_text": "#1C1F26", "undo_btn": "#2E7D32",
    "clock_text": "#6366F1", "clock_bg": "#EEF2FF", "clock_border": "#E0E7FF",
    "note_indicator": "#FF5252",  # Bright Red for visibility
    "tooltip_bg": "#FFFFFF", "tooltip_text": "#1C1F26", "tooltip_border": "#7E3AF2"
}

THEME_DARK = {
    "bg": "#0D1117", 
    "card": "#161B22", "border": "#30363D",
    "text_primary": "#F0F6FC", "text_secondary": "#8B949E",
    "shadow": "#80000000",
    "today_bg": "#3E2C00", "today_text": "#D29922", 
    "future_bg": "#101318", "completed": "#2EA043", 
    "chart_bg": "#161B22", "chart_line": "#58A6FF", "chart_fill": "#58A6FF", "chart_bar": "#A371F7", "chart_grid": "#30363D",
    "btn_add": "#238636", "btn_export": "#8957E5", 
    "date_badge_bg": "#161B22", "date_badge_text": "#58A6FF", "date_badge_border": "#30363D",
    "btn_nav_bg": "#21262D", "btn_nav_text": "#C9D1D9", "btn_nav_border": "#30363D",
    "btn_filter_bg": "#1F6FEB", "btn_filter_text": "#FFFFFF",
    "row_even": "#161B22", "row_odd": "#0D1117",
    "weekend_text": "#FF5252", "day_text": "#8B949E", "date_text": "#C9D1D9",
    "undo_text": "#FFFFFF", "undo_btn": "#58A6FF",
    "clock_text": "#A5B4FC", "clock_bg": "#1F2937", "clock_border": "#374151",
    "note_indicator": "#FF8A80",
    "tooltip_bg": "#21262D", "tooltip_text": "#F0F6FC", "tooltip_border": "#8957E5"
}

KPI_STYLES_LIGHT = {
    "Today":   {"bg": "#E3F2FD", "text": "#1976D2", "border": "#BBDEFB"},
    "Streak":  {"bg": "#FFEBEE", "text": "#D32F2F", "border": "#FFCDD2"},
    "Weekly":  {"bg": "#E8F5E9", "text": "#388E3C", "border": "#C8E6C9"},
    "Monthly": {"bg": "#F3E5F5", "text": "#7B1FA2", "border": "#E1BEE7"},
    "Total":   {"bg": "#FFF8E1", "text": "#F57F17", "border": "#FFE082"}
}

KPI_STYLES_DARK = {
    "Today":   {"text": "#79C0FF"},
    "Streak":  {"text": "#FFA198"},
    "Weekly":  {"text": "#56D364"},
    "Monthly": {"text": "#D2A8FF"},
    "Total":   {"text": "#FFD54F"}
}

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except Exception: base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def apply_shadow(widget, blur=15, offset=4, color="#50000000"):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setXOffset(0)
    shadow.setYOffset(offset)
    shadow.setColor(QColor(color))
    widget.setGraphicsEffect(shadow)

# --- COMPONENTS ---

class NoteDialog(QDialog):
    def __init__(self, parent=None, current_note="", is_dark=False):
        super().__init__(parent)
        self.setWindowTitle("Edit Note")
        self.setFixedWidth(350)
        theme = THEME_DARK if is_dark else THEME_LIGHT
        self.setStyleSheet(f"""
            QDialog {{ background-color: {theme['card']}; }}
            QLabel {{ color: {theme['text_primary']}; font-weight: 600; font-size: 13px; }}
            QTextEdit {{ background: {theme['bg']}; color: {theme['text_primary']}; border: 1px solid {theme['border']}; padding: 8px; border-radius: 6px; font-size: 13px; }}
            QPushButton {{ padding: 8px 16px; border-radius: 6px; border: none; font-weight: bold; }}
            QPushButton[text="Save"] {{ background: {theme['btn_add']}; color: white; }}
            QPushButton[text="Cancel"] {{ background: {theme['border']}; color: {theme['text_primary']}; }}
        """)
        layout = QVBoxLayout(self)
        self.lbl = QLabel("Add a note for this day:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(current_note)
        self.text_edit.setFixedHeight(120)
        
        btns = QHBoxLayout()
        btn_cancel = QPushButton("Cancel"); btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton("Save"); btn_save.clicked.connect(self.accept)
        btns.addStretch(); btns.addWidget(btn_cancel); btns.addWidget(btn_save)
        
        layout.addWidget(self.lbl)
        layout.addWidget(self.text_edit)
        layout.addLayout(btns)

    def get_text(self):
        return self.text_edit.toPlainText().strip()

class NoteDelegate(QStyledItemDelegate):
    """Draws a small triangle indicator if a note exists."""
    def __init__(self, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.is_dark = is_dark_mode

    def set_theme_mode(self, is_dark):
        self.is_dark = is_dark

    def paint(self, painter, option, index):
        # 1. Draw the standard background/checkbox
        super().paint(painter, option, index)
        
        # 2. Check for Note flag (UserRole + 1)
        has_note = index.data(Qt.UserRole + 1)
        
        if has_note:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Setup Color - uses Theme 'note_indicator' (Red)
            theme = THEME_DARK if self.is_dark else THEME_LIGHT
            color = QColor(theme['note_indicator'])
            
            # Define Triangle in Top-Right Corner
            size = 7 # Slightly larger for better visibility
            rect = option.rect
            points = [
                QPoint(rect.right(), rect.top()),          # Top-Right absolute corner
                QPoint(rect.right() - size, rect.top()),   # Left of corner
                QPoint(rect.right(), rect.top() + size)    # Below corner
            ]
            
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawPolygon(QPolygonF(points))
            
            painter.restore()

class UndoBar(QWidget):
    undoClicked = Signal()
    def __init__(self, parent=None):
        super().__init__(parent); self.setFixedHeight(60); self.setFixedWidth(350); self.hide()
        layout = QHBoxLayout(self); layout.setContentsMargins(0, 0, 20, 0)
        self.lbl_text = QLabel("Habit deleted."); self.btn_undo = QPushButton("UNDO")
        self.btn_undo.setCursor(Qt.PointingHandCursor); self.btn_undo.clicked.connect(self.undoClicked.emit)
        layout.addStretch(); layout.addWidget(self.lbl_text); layout.addWidget(self.btn_undo)
        self.timer = QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.hide_animated)
    def show_message(self, text="Item deleted", duration=4000, is_dark=False):
        theme = THEME_DARK if is_dark else THEME_LIGHT
        self.setStyleSheet(f"QWidget {{ background: transparent; }} QLabel {{ color: {theme['undo_text']}; font-weight: bold; font-size: 14px; margin-right: 15px; }} QPushButton {{ color: {theme['undo_btn']}; font-weight: 900; font-size: 14px; border: none; background: transparent; text-align: right; }} QPushButton:hover {{ text-decoration: underline; }}")
        self.lbl_text.setText(text); self.show(); self.anim = QPropertyAnimation(self, b"pos"); parent_rect = self.parent().rect()
        x_pos = parent_rect.width() - self.width() - 40; start_pos = QPoint(x_pos, parent_rect.height()); end_pos = QPoint(x_pos, parent_rect.height() - 80)
        self.anim.setDuration(300); self.anim.setStartValue(start_pos); self.anim.setEndValue(end_pos); self.anim.setEasingCurve(QEasingCurve.OutCubic); self.anim.start(); self.timer.start(duration)
    def hide_animated(self):
        self.anim_hide = QPropertyAnimation(self, b"pos"); current_pos = self.pos(); end_pos = QPoint(current_pos.x(), self.parent().height())
        self.anim_hide.setDuration(300); self.anim_hide.setStartValue(current_pos); self.anim_hide.setEndValue(end_pos); self.anim_hide.setEasingCurve(QEasingCurve.InCubic); self.anim_hide.finished.connect(self.hide); self.anim_hide.start()

class HoverHeader(QHeaderView):
    editRequested = Signal(int)
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent); self.setMouseTracking(True); self.hover_row = -1; self.setSectionsClickable(True); self.setSectionsMovable(False) 
    def mouseMoveEvent(self, event):
        row = self.logicalIndexAt(event.position().toPoint())
        if row != self.hover_row: self.hover_row = row; self.viewport().update()
        super().mouseMoveEvent(event)
    def leaveEvent(self, event): self.hover_row = -1; self.viewport().update(); super().leaveEvent(event)
    def mousePressEvent(self, event):
        row = self.logicalIndexAt(event.position().toPoint())
        if row >= 2 and event.position().toPoint().x() > self.width() - 35: self.editRequested.emit(row); return
        super().mousePressEvent(event)
    def paintSection(self, painter, rect, logicalIndex):
        painter.save(); super().paintSection(painter, rect, logicalIndex); painter.restore()
        if logicalIndex >= 2 and logicalIndex == self.hover_row:
            painter.save(); icon_rect = QRect(rect.right() - 25, rect.top(), 20, rect.height()); font = painter.font(); font.setPointSize(10); painter.setFont(font); painter.setPen(QColor("#7F8C8D")); painter.drawText(icon_rect, Qt.AlignCenter, "✏️"); painter.restore()

class AnimatedButton(QPushButton):
    def __init__(self, text, bg_color, text_color="#FFFFFF", is_dropdown=False):
        super().__init__(text); self.bg_color = bg_color; self.text_color = text_color; self.is_dropdown = is_dropdown; self.setCursor(Qt.PointingHandCursor); self.update_style()
    def update_colors(self, bg, text): self.bg_color = bg; self.text_color = text; self.update_style()
    def update_style(self):
        padding = "10px 35px 10px 20px" if self.is_dropdown else "10px 20px"
        self.setStyleSheet(f"QPushButton {{ background-color: {self.bg_color}; color: {self.text_color}; border-radius: 8px; padding: {padding}; font-weight: 600; font-size: 13px; border: none; text-align: center; }} QPushButton:hover {{ background-color: {self.bg_color}; border: 2px solid #FFFFFF50; padding: { '8px 33px 8px 18px' if self.is_dropdown else '8px 18px' }; }} QPushButton::menu-indicator {{ subcontrol-origin: padding; subcontrol-position: center right; right: 12px; width: 8px; height: 8px; }}")

class KPICard(QFrame):
    def __init__(self, key, title, icon):
        super().__init__()
        self.key = key; self.icon_label = QLabel(icon); self.lbl_title = QLabel(title.upper()); self.lbl_value = QLabel("0")
        layout = QVBoxLayout(self); layout.setSpacing(5); layout.setContentsMargins(15, 15, 15, 15)
        header_layout = QHBoxLayout(); header_layout.addStretch(); header_layout.addWidget(self.icon_label); header_layout.addWidget(self.lbl_title); header_layout.addStretch()
        layout.addLayout(header_layout); self.lbl_value.setAlignment(Qt.AlignCenter); layout.addWidget(self.lbl_value); self.setFixedHeight(100) 
        self._current_val = 0; self._target_val = 0; self.anim_timer = QTimer(self); self.anim_timer.timeout.connect(self._animate_step)
    def apply_theme(self, is_dark):
        theme = THEME_DARK if is_dark else THEME_LIGHT
        style_data = KPI_STYLES_DARK.get(self.key, {"text": "#FFFFFF"}) if is_dark else KPI_STYLES_LIGHT.get(self.key, {"bg": "#FFFFFF", "text": "#000000", "border": "#E0E0E0"})
        bg_style = f"background-color: {theme['card']};" if is_dark else f"background-color: {style_data['bg']}; border: 1px solid {style_data['border']};"
        self.setStyleSheet(f"QFrame {{ {bg_style} border-radius: 12px; }} QLabel {{ border: none; background: transparent; }}")
        text_color = style_data['text']
        self.icon_label.setStyleSheet(f"color: {text_color}; font-size: 20px;")
        self.lbl_title.setStyleSheet(f"color: {text_color}; font-size: 13px; font-weight: 800; opacity: 0.9;") 
        self.lbl_value.setStyleSheet(f"color: {text_color}; font-size: 24px; font-weight: 800;")
    def set_value(self, text_val):
        try: val = int(''.join(filter(str.isdigit, str(text_val))))
        except: val = 0
        self.suffix = "%" if "%" in str(text_val) else ""; self._target_val = val; self.anim_timer.start(15)
    def _animate_step(self):
        if self._current_val < self._target_val: self._current_val += 1
        elif self._current_val > self._target_val: self._current_val -= 1
        else: self.anim_timer.stop()
        self.lbl_value.setText(f"{self._current_val}{self.suffix}")

class HabitDialog(QDialog):
    def __init__(self, parent=None, name="", time="", is_dark=False):
        super().__init__(parent); self.setWindowTitle("Habit Details"); self.setFixedWidth(380)
        theme = THEME_DARK if is_dark else THEME_LIGHT
        self.setStyleSheet(f"QDialog {{ background-color: {theme['card']}; }} QLabel {{ color: {theme['text_primary']}; font-weight: 600; font-size: 13px; }} QLineEdit {{ background: {theme['bg']}; color: {theme['text_primary']}; border: 1px solid {theme['border']}; padding: 8px; border-radius: 6px; }} QPushButton {{ background: {theme['btn_add']}; color: white; padding: 8px 16px; border-radius: 6px; border: none; font-weight: bold; }}")
        layout = QVBoxLayout(self)
        self.name_input = QLineEdit(name); self.name_input.setPlaceholderText("Habit Name")
        self.time_input = QLineEdit(time); self.time_input.setPlaceholderText("Time")
        form = QFormLayout(); form.addRow("Name:", self.name_input); form.addRow("Time:", self.time_input); layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)
    def get_data(self): return self.name_input.text(), self.time_input.text()

# --- MODEL ---
class HabitModel(QAbstractTableModel):
    dataToggled = Signal(int, int)

    def __init__(self, month_data, habit_names, habit_times, year, month, notes_data, is_dark=False):
        super().__init__()
        self._month_data = month_data; self._habit_names = habit_names; self._habit_times = habit_times
        self._year = year; self._month = month; self.is_dark = is_dark
        self._notes_data = notes_data
        self.update_month_properties()

    def update_month_properties(self):
        self.start_date = datetime.date(self._year, self._month, 1)
        self.days_in_month = len(self._month_data[0]) if self._month_data else 0
        self.start_day_of_year_idx = self.start_date.timetuple().tm_yday - 1
        self.today_idx = -1; today = datetime.date.today()
        if today.year == self._year and today.month == self._month: self.today_idx = today.day - 1

    def update_view(self, year, month, month_slice):
        self.layoutAboutToBeChanged.emit()
        self._year = year; self._month = month; self._month_data = month_slice
        self.update_month_properties(); self.layoutChanged.emit()

    def set_theme_mode(self, is_dark): self.is_dark = is_dark; self.layoutChanged.emit()
    def rowCount(self, parent=None): return len(self._habit_names) + 2
    def columnCount(self, parent=None): return self.days_in_month
    
    def data(self, index, role=Qt.DisplayRole):
        r, c = index.row(), index.column()
        theme = THEME_DARK if self.is_dark else THEME_LIGHT
        
        # --- NOTE LOGIC ---
        if r >= 2:
            habit_idx = r - 2
            global_day_idx = self.start_day_of_year_idx + c
            
            note_text = None
            y_str = str(self._year)
            if y_str in self._notes_data:
                if habit_idx in self._notes_data[y_str]:
                    if global_day_idx in self._notes_data[y_str][habit_idx]:
                        note_text = self._notes_data[y_str][habit_idx][global_day_idx]

            if role == Qt.ToolTipRole and note_text:
                return f"📝 Note:\n{note_text}"
            
            if role == Qt.UserRole + 1:
                return bool(note_text)

        # --- STANDARD DRAWING ---
        if r < 2:
            is_today = (c == self.today_idx)
            if role == Qt.BackgroundRole: return QColor(theme['today_bg']) if is_today else QColor(theme['bg'])
            if role == Qt.TextAlignmentRole: return Qt.AlignCenter
            d_date = self.start_date + datetime.timedelta(days=c)
            if r == 0: 
                if role == Qt.DisplayRole: return str(d_date.day).zfill(2)
                if role == Qt.ForegroundRole: return QColor(theme['today_text']) if is_today else QColor(theme['date_text'])
                if role == Qt.FontRole: return QFont("Segoe UI", 9, QFont.Bold)
            else: 
                if role == Qt.DisplayRole: return d_date.strftime("%a")
                if role == Qt.ForegroundRole: 
                    if is_today: return QColor(theme['today_text'])
                    return QColor(theme['weekend_text']) if d_date.weekday() >= 5 else QColor(theme['day_text'])
                if role == Qt.FontRole: return QFont("Segoe UI", 8)
            return None
        habit_idx = r - 2
        if habit_idx >= len(self._month_data): return None
        val = self._month_data[habit_idx][c]
        if role == Qt.BackgroundRole:
            if val == 1: return QColor(theme['completed'])
            if c == self.today_idx: return QColor(theme['today_bg'])
            is_future = False; today = datetime.date.today()
            if self._year > today.year or (self._year == today.year and self._month > today.month): is_future = True
            elif self._year == today.year and self._month == today.month and c > self.today_idx: is_future = True
            if is_future: return QColor(theme['future_bg'])
            return QColor(theme['row_even']) if habit_idx % 2 == 0 else QColor(theme['row_odd'])
        return None

    def headerData(self, section, orientation, role):
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            if section < 2: return ["DATE", "DAY"][section]
            habit_idx = section - 2
            if 0 <= habit_idx < len(self._habit_names): return f"{self._habit_names[habit_idx]}\n{self._habit_times[habit_idx]}"
        if orientation == Qt.Vertical and role == Qt.FontRole and section >= 2: return QFont("Segoe UI", 9, QFont.Bold)
        return None

    def toggle(self, index):
        r, c = index.row(), index.column()
        if r < 2: return
        today = datetime.date.today()
        if self._year > today.year or (self._year == today.year and self._month > today.month): return
        if self._year == today.year and self._month == today.month and c > self.today_idx: return
        habit_idx = r - 2
        new_val = 1 - self._month_data[habit_idx][c]
        self._month_data[habit_idx][c] = new_val
        self.dataChanged.emit(index, index); self.dataToggled.emit(habit_idx, c)

# --- MAIN APP ---
class HabitApp(QWidget):
    def __init__(self):
        super().__init__()
        icon_path = resource_path(ICON_NAME)
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        self.is_dark_mode = False 
        self.row_height = 50; self.col_width = 45
        today = datetime.date.today(); self.view_year = today.year; self.view_month = today.month
        self.selected_habit_idx = None; self._last_deleted_habit = None  
        self.chart_update_timer = QTimer(); self.chart_update_timer.setSingleShot(True); self.chart_update_timer.timeout.connect(self.update_charts_data_only)
        
        self.saved_geometry = None; self.saved_maximized = False
        
        self.init_data()
        self.setup_ui_core()
        self.apply_theme()
        
        if self.saved_geometry:
            try: self.restoreGeometry(QByteArray.fromBase64(self.saved_geometry.encode()))
            except: pass
        if self.saved_maximized: self.setWindowState(Qt.WindowMaximized)
            
        QTimer.singleShot(100, self.scroll_to_today_column)
        QTimer.singleShot(200, self.load_secondary_ui)
        QTimer.singleShot(500, self.lazy_load_charts)
        QTimer.singleShot(800, self.start_clock_timer)
        QTimer.singleShot(1000, self.apply_delayed_effects)

    def init_data(self):
        self.habit_names = []; self.habit_times = []; self.history_data = {} 
        self.notes_data = {} 
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f: 
                    d = json.load(f)
                    self.habit_names = d.get("names", DEFAULT_HABITS.copy())
                    self.habit_times = d.get("times", [])
                    self.is_dark_mode = d.get("theme", False)
                    self.saved_geometry = d.get("window_geometry")
                    self.saved_maximized = d.get("window_maximized", False)
                    raw_data = d.get("data", [])
                    if raw_data and isinstance(raw_data[0], list): self.history_data["2026"] = raw_data
                    else: self.history_data = d.get("history", {})
                    
                    # LOAD NOTES
                    raw_notes = d.get("notes", {})
                    for y, y_data in raw_notes.items():
                        self.notes_data[y] = {}
                        for h_idx, h_data in y_data.items():
                            self.notes_data[y][int(h_idx)] = {}
                            for d_idx, text in h_data.items():
                                self.notes_data[y][int(h_idx)][int(d_idx)] = text
            except: pass
        if not self.habit_names: self.habit_names = DEFAULT_HABITS.copy()
        while len(self.habit_times) < len(self.habit_names): self.habit_times.append("Any Time")
        self.sanitize_data(self.view_year)

    def sanitize_data(self, year):
        str_year = str(year); days_in_year = 366 if calendar.isleap(year) else 365
        target_rows = len(self.habit_names)
        if str_year in self.history_data:
            current_data = self.history_data[str_year]
            if len(current_data) == target_rows:
                if target_rows > 0 and len(current_data[0]) == days_in_year: return
        else: self.history_data[str_year] = []
        current_data = self.history_data[str_year]
        if len(current_data) < target_rows:
            for _ in range(target_rows - len(current_data)): current_data.append([0]*days_in_year)
        if len(current_data) > target_rows: self.history_data[str_year] = current_data[:target_rows]
        for i in range(len(self.history_data[str_year])):
            row = self.history_data[str_year][i]
            if len(row) < days_in_year: row.extend([0] * (days_in_year - len(row)))
            elif len(row) > days_in_year: self.history_data[str_year][i] = row[:days_in_year]

    def get_month_slice(self, year, month):
        days_in_month = calendar.monthrange(year, month)[1]
        start_idx = datetime.date(year, month, 1).timetuple().tm_yday - 1
        current_year_data = self.history_data[str(year)]
        data_to_slice = current_year_data[:len(self.habit_names)]
        return [row[start_idx : start_idx + days_in_month] for row in data_to_slice]

    def setup_ui_core(self):
        self.setWindowTitle(f"Habit Dashboard"); self.resize(1350, 950)
        self.main_scroll = QScrollArea(self); self.main_scroll.setWidgetResizable(True)
        self.container = QWidget(); self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(40, 40, 40, 40); self.layout.setSpacing(35)
        self.main_scroll.setWidget(self.container)
        root_layout = QVBoxLayout(self); root_layout.setContentsMargins(0, 0, 0, 0); root_layout.addWidget(self.main_scroll)

        header_frame = QFrame(); header_layout = QHBoxLayout(header_frame); header_layout.setContentsMargins(0, 0, 0, 0)
        title_box = QVBoxLayout(); title_box.setSpacing(5)
        self.title_lbl = QLabel(f"🎯 Habit Dashboard"); self.subtitle_lbl = QLabel(f"Consistency is key.")
        title_box.addWidget(self.title_lbl); title_box.addWidget(self.subtitle_lbl)
        
        controls_layout = QHBoxLayout(); controls_layout.setSpacing(12)
        self.btn_prev_month = QPushButton("◀"); self.btn_prev_month.setFixedSize(40, 38); self.btn_prev_month.setCursor(Qt.PointingHandCursor)
        self.btn_prev_month.clicked.connect(lambda: self.change_month(-1))
        self.lbl_month_display = QLabel(f"{calendar.month_name[self.view_month]} {self.view_year}")
        self.lbl_month_display.setAlignment(Qt.AlignCenter); self.lbl_month_display.setFixedSize(160, 38)
        self.btn_next_month = QPushButton("▶"); self.btn_next_month.setFixedSize(40, 38); self.btn_next_month.setCursor(Qt.PointingHandCursor)
        self.btn_next_month.clicked.connect(lambda: self.change_month(1))
        
        self.lbl_clock = QLabel("00:00:00"); self.lbl_clock.setAlignment(Qt.AlignCenter); self.lbl_clock.setFixedSize(120, 38)

        self.btn_add = AnimatedButton(" + Habit ", "#28A745", is_dropdown=False); self.btn_add.clicked.connect(self.add_habit)
        self.btn_export = AnimatedButton("Export", "#7E3AF2", is_dropdown=True)
        self.menu = QMenu(self); self.menu.addAction("📄 CSV", self.export_csv); self.menu.addAction("📕 PDF", self.export_pdf)
        self.menu.addSeparator(); self.menu.addAction("💾 Backup", self.backup_data); self.menu.addAction("🔄 Restore", self.restore_data)
        self.btn_export.setMenu(self.menu)
        self.btn_theme = QPushButton(""); self.btn_theme.setFixedSize(38, 38); self.btn_theme.setCursor(Qt.PointingHandCursor); self.btn_theme.clicked.connect(self.toggle_theme)
        
        controls_layout.addWidget(self.btn_prev_month); controls_layout.addWidget(self.lbl_month_display); controls_layout.addWidget(self.btn_next_month)
        controls_layout.addWidget(self.lbl_clock); controls_layout.addSpacing(20); controls_layout.addWidget(self.btn_add); controls_layout.addWidget(self.btn_export); controls_layout.addWidget(self.btn_theme)
        header_layout.addLayout(title_box); header_layout.addStretch(); header_layout.addLayout(controls_layout)
        self.layout.addWidget(header_frame)

        self.grid_container = QFrame(); grid_layout_inner = QVBoxLayout(self.grid_container); grid_layout_inner.setContentsMargins(0, 0, 0, 0)
        self.table = QTableView()
        month_slice = self.get_month_slice(self.view_year, self.view_month)
        
        # PASS NOTES DATA TO MODEL
        self.model = HabitModel(month_slice, self.habit_names, self.habit_times, self.view_year, self.view_month, self.notes_data, self.is_dark_mode)
        self.model.dataToggled.connect(self.on_data_toggled)
        self.table.setModel(self.model)
        
        # SET CUSTOM DELEGATE FOR NOTES
        self.note_delegate = NoteDelegate(self.is_dark_mode, self.table)
        self.table.setItemDelegate(self.note_delegate)
        
        self.hover_header = HoverHeader(Qt.Vertical, self.table); self.table.setVerticalHeader(self.hover_header); self.hover_header.editRequested.connect(self.edit_habit_by_row)
        v_header = self.table.verticalHeader(); v_header.setVisible(True); v_header.setFixedWidth(160); v_header.setDefaultSectionSize(self.row_height); v_header.setSectionResizeMode(QHeaderView.Fixed)
        self.table.horizontalHeader().setVisible(False); self.table.horizontalHeader().setDefaultSectionSize(self.col_width); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed); self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents); self.table.setFrameShape(QFrame.NoFrame)
        self.table.setFocusPolicy(Qt.NoFocus); self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.verticalHeader().setContextMenuPolicy(Qt.CustomContextMenu); self.table.verticalHeader().customContextMenuRequested.connect(self.handle_header_menu)
        self.table.clicked.connect(self.on_cell_clicked)
        
        # ENABLE TABLE CONTEXT MENU FOR NOTES
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.on_table_context_menu)
        
        self.update_table_height(); grid_layout_inner.addWidget(self.table); self.layout.addWidget(self.grid_container)
        self.stats_control_layout = QHBoxLayout(); self.layout.addLayout(self.stats_control_layout)
        self.kpi_layout = QHBoxLayout(); self.kpi_layout.setSpacing(24); self.layout.addLayout(self.kpi_layout)
        self.chart_container = QFrame(); self.chart_container.setMinimumHeight(450); self.chart_main_layout = QVBoxLayout(self.chart_container); self.layout.addWidget(self.chart_container)
        self.update_clock()

    def load_secondary_ui(self):
        self.stats_title = QLabel("Performance Overview"); self.stats_title.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.btn_habit_filter = AnimatedButton("Global Overview", "#0EA5E9", is_dropdown=True); self.habit_menu = QMenu(self); self.btn_habit_filter.setMenu(self.habit_menu)
        self.stats_control_layout.addWidget(self.stats_title); self.stats_control_layout.addWidget(self.btn_habit_filter); self.stats_control_layout.addStretch(); self.refresh_habit_menu()
        self.card_today = KPICard("Today", "Today", "🎯"); self.card_streak = KPICard("Streak", "Best Streak", "🔥"); self.card_weekly = KPICard("Weekly", "Weekly Avg", "📈"); self.card_monthly = KPICard("Monthly", "Monthly Avg", "📊"); self.card_total = KPICard("Total", "Total Days", "✅")
        self.kpi_cards = [self.card_today, self.card_streak, self.card_weekly, self.card_monthly, self.card_total]
        for c in self.kpi_cards: self.kpi_layout.addWidget(c); c.apply_theme(self.is_dark_mode)
        self.undo_bar = UndoBar(self); self.undo_bar.undoClicked.connect(self.restore_last_deleted)
        theme = THEME_DARK if self.is_dark_mode else THEME_LIGHT; self.stats_title.setStyleSheet(f"color: {theme['text_primary']}; font-size: 26px; font-weight: 800;"); self.btn_habit_filter.update_colors(theme['btn_filter_bg'], theme['btn_filter_text'])

    def lazy_load_charts(self):
        self.tabs = QTabWidget(); self.tabs.setStyleSheet("QTabWidget::pane { border: 0; }")
        self.tab_annual = QWidget(); self.lay_annual = QVBoxLayout(self.tab_annual)
        self.tab_monthly = QWidget(); self.lay_monthly = QVBoxLayout(self.tab_monthly)
        self.tabs.addTab(self.tab_annual, "Annual Trend"); self.tabs.addTab(self.tab_monthly, "Monthly Breakdown")
        self.chart_main_layout.addWidget(self.tabs)
        theme = THEME_DARK if self.is_dark_mode else THEME_LIGHT; self.chart_container.setStyleSheet(f"background: {theme['card']}; border: 1px solid {theme['border']}; border-radius: 12px;")
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg; from matplotlib.figure import Figure
        self.fig_annual = Figure(figsize=(8, 3), dpi=100); self.canvas_annual = FigureCanvasQTAgg(self.fig_annual); self.lay_annual.addWidget(self.canvas_annual)
        self.fig_monthly = Figure(figsize=(8, 3), dpi=100); self.canvas_monthly = FigureCanvasQTAgg(self.fig_monthly); self.lay_monthly.addWidget(self.canvas_monthly)
        self.ax_annual = self.fig_annual.add_subplot(111); self.line_annual, = self.ax_annual.plot([], [], linewidth=2); self.fill_annual = None
        self.ax_monthly = self.fig_monthly.add_subplot(111); self.bars_monthly = self.ax_monthly.bar(range(12), [0]*12); self.bar_labels = []
        for i in range(12): lbl = self.ax_monthly.text(i, 0, "", ha='center', va='bottom', fontsize=8, fontweight='bold'); self.bar_labels.append(lbl)
        self.ax_annual.spines['top'].set_visible(False); self.ax_annual.spines['right'].set_visible(False); self.ax_monthly.spines['top'].set_visible(False); self.ax_monthly.spines['right'].set_visible(False); self.ax_monthly.spines['left'].set_visible(False)
        self.trigger_full_update()

    def start_clock_timer(self): self.clock_timer = QTimer(self); self.clock_timer.timeout.connect(self.update_clock); self.clock_timer.start(1000)
    def apply_delayed_effects(self):
        theme = THEME_DARK if self.is_dark_mode else THEME_LIGHT
        if hasattr(self, 'kpi_cards'):
            for card in self.kpi_cards: apply_shadow(card, blur=10, offset=4, color=theme['shadow'])
        apply_shadow(self.chart_container, blur=10, offset=4, color=theme['shadow']); apply_shadow(self.grid_container, blur=10, offset=4, color=theme['shadow'])

    def update_clock(self): self.lbl_clock.setText(datetime.datetime.now().strftime("%H:%M:%S"))
    def resizeEvent(self, event):
        if hasattr(self, 'undo_bar') and self.undo_bar.isVisible(): self.undo_bar.move((self.width() - self.undo_bar.width()) - 40, self.height() - 80)
        super().resizeEvent(event)

    def change_month(self, delta):
        new_month = self.view_month + delta; new_year = self.view_year
        if new_month > 12: new_month = 1; new_year += 1
        elif new_month < 1: new_month = 12; new_year -= 1
        self.view_month = new_month; self.view_year = new_year
        self.sanitize_data(self.view_year); self.lbl_month_display.setText(f"{calendar.month_name[self.view_month]} {self.view_year}")
        new_slice = self.get_month_slice(self.view_year, self.view_month); self.model.update_view(self.view_year, self.view_month, new_slice)
        self.table.horizontalHeader().setDefaultSectionSize(self.col_width); self.scroll_to_today_column(); self.trigger_full_update()

    def refresh_habit_menu(self):
        if not hasattr(self, 'habit_menu'): return
        self.habit_menu.clear()
        def make_action(text, idx): action = QAction(text, self); action.triggered.connect(lambda: self.set_habit_view(idx, text)); return action
        self.habit_menu.addAction(make_action("Global Overview", None)); self.habit_menu.addSeparator()
        for i, name in enumerate(self.habit_names): self.habit_menu.addAction(make_action(name, i))

    def set_habit_view(self, idx, text): self.selected_habit_idx = idx; self.btn_habit_filter.setText(text); self.trigger_full_update()
    def toggle_theme(self): self.is_dark_mode = not self.is_dark_mode; self.apply_theme(); self.save_data(); self.trigger_full_update() 

    def apply_theme(self):
        theme = THEME_DARK if self.is_dark_mode else THEME_LIGHT
        # FIXED: Global QToolTip stylesheet ensures high visibility regardless of system theme
        self.setStyleSheet(f"""
            * {{ font-family: 'Segoe UI', sans-serif; }}
            QToolTip {{ 
                color: {theme['tooltip_text']}; 
                background-color: {theme['tooltip_bg']}; 
                border: 1px solid {theme['tooltip_border']}; 
                padding: 4px;
                font-weight: bold;
            }}
            QMenu {{ background: {theme['card']}; border: 1px solid {theme['border']}; }}
            QMenu::item {{ color: {theme['text_primary']}; padding: 6px 20px; }}
            QMenu::item:selected {{ background: {theme.get('row_odd', '#EEE')}; }}
            QTabWidget::pane {{ border: 1px solid {theme['border']}; background: {theme['card']}; border-radius: 8px; }}
            QTabBar::tab {{ background: {theme['bg']}; color: {theme['text_secondary']}; padding: 10px 20px; margin-right: 4px; border-top-left-radius: 6px; border-top-right-radius: 6px; }}
            QTabBar::tab:selected {{ background: {theme['card']}; color: {theme['text_primary']}; font-weight: bold; }}
        """)
        self.container.setStyleSheet(f"background-color: {theme['bg']};"); self.main_scroll.setStyleSheet(f"background-color: {theme['bg']}; border: none;")
        self.title_lbl.setStyleSheet(f"color: {theme['text_primary']}; font-size: 34px; font-weight: 800;"); self.subtitle_lbl.setStyleSheet(f"color: {theme['text_secondary']}; font-size: 18px;")
        if hasattr(self, 'stats_title'): self.stats_title.setStyleSheet(f"color: {theme['text_primary']}; font-size: 26px; font-weight: 800;")
        nav_style = f"background-color: {theme['btn_nav_bg']}; color: {theme['btn_nav_text']}; border: 1px solid {theme['btn_nav_border']}; border-radius: 8px; font-weight: bold; font-size: 16px;"
        self.btn_prev_month.setStyleSheet(f"QPushButton {{ {nav_style} }} QPushButton:hover {{ border-color: {theme['text_primary']}; }}"); self.btn_next_month.setStyleSheet(f"QPushButton {{ {nav_style} }} QPushButton:hover {{ border-color: {theme['text_primary']}; }}")
        self.lbl_month_display.setStyleSheet(f"background-color: {theme['date_badge_bg']}; color: {theme['date_badge_text']}; border: 1px solid {theme['date_badge_border']}; border-radius: 8px; font-weight: 700; font-size: 15px;")
        self.lbl_clock.setStyleSheet(f"background-color: {theme['clock_bg']}; color: {theme['clock_text']}; border: 1px solid {theme['clock_border']}; border-radius: 8px; font-weight: 700; font-size: 15px;")
        self.btn_add.update_colors(theme['btn_add'], "#FFFFFF"); self.btn_export.update_colors(theme['btn_export'], "#FFFFFF")
        if hasattr(self, 'btn_habit_filter'): self.btn_habit_filter.update_colors(theme['btn_filter_bg'], theme['btn_filter_text'])
        self.btn_theme.setText("☀️" if self.is_dark_mode else "🌙"); self.btn_theme.setStyleSheet(f"QPushButton {{ background-color: {theme['card']}; border: 1px solid {theme['border']}; border-radius: 19px; font-size: 16px; }} QPushButton:hover {{ border: 1px solid {theme['text_secondary']}; }}")
        for c in [self.grid_container, self.chart_container]: c.setStyleSheet(f"background: {theme['card']}; border: 1px solid {theme['border']}; border-radius: 12px;")
        self.table.setStyleSheet(f"QTableView {{ border: none; background: {theme['card']}; gridline-color: transparent; border-radius: 12px; }} QHeaderView::section {{ background: {theme['card']}; color: {theme['text_primary']}; border: none; border-bottom: 1px solid {theme['border']}; border-right: 1px solid {theme['border']}; padding-left: 10px; }}")
        self.model.set_theme_mode(self.is_dark_mode)
        if hasattr(self, 'note_delegate'): self.note_delegate.set_theme_mode(self.is_dark_mode)
        if hasattr(self, 'kpi_cards'): 
            for card in self.kpi_cards: card.apply_theme(self.is_dark_mode)
        if hasattr(self, 'clock_timer'): self.apply_delayed_effects()

    def scroll_to_today_column(self):
        today = datetime.date.today()
        if today.year == self.view_year and today.month == self.view_month: col = today.day - 1; self.table.scrollTo(self.model.index(0, col), QAbstractItemView.PositionAtCenter)

    def edit_habit_by_row(self, row):
        if row < 2: return
        habit_idx = row - 2
        d = HabitDialog(self, self.habit_names[habit_idx], self.habit_times[habit_idx], self.is_dark_mode)
        if d.exec_() == QDialog.Accepted:
            n, t = d.get_data()
            if n:
                self.habit_names[habit_idx] = n; self.habit_times[habit_idx] = t; self.save_data()
                self.model.headerDataChanged.emit(Qt.Vertical, row, row); self.refresh_habit_menu()

    def on_table_context_menu(self, pos):
        """Right-click menu for Table Cells to add/edit notes."""
        index = self.table.indexAt(pos)
        if not index.isValid(): return
        
        row, col = index.row(), index.column()
        if row < 2: return # Ignore date headers
        
        habit_idx = row - 2
        global_day_idx = datetime.date(self.view_year, self.view_month, 1).timetuple().tm_yday - 1 + col
        
        # Check current note
        current_note = ""
        y_str = str(self.view_year)
        if y_str in self.notes_data and habit_idx in self.notes_data[y_str]:
            current_note = self.notes_data[y_str][habit_idx].get(global_day_idx, "")

        menu = QMenu(self)
        action_note = menu.addAction("📝 Add/Edit Note")
        
        action = menu.exec_(self.table.viewport().mapToGlobal(pos))
        
        if action == action_note:
            dlg = NoteDialog(self, current_note, self.is_dark_mode)
            if dlg.exec_() == QDialog.Accepted:
                new_text = dlg.get_text()
                
                # Update Data Structure
                if y_str not in self.notes_data: self.notes_data[y_str] = {}
                if habit_idx not in self.notes_data[y_str]: self.notes_data[y_str][habit_idx] = {}
                
                if new_text:
                    self.notes_data[y_str][habit_idx][global_day_idx] = new_text
                else:
                    # Remove empty note
                    if global_day_idx in self.notes_data[y_str][habit_idx]:
                        del self.notes_data[y_str][habit_idx][global_day_idx]
                
                self.save_data()
                self.model.dataChanged.emit(index, index)

    def handle_header_menu(self, pos):
        row = self.table.verticalHeader().logicalIndexAt(pos)
        if row < 2: return
        habit_idx = row - 2
        menu = QMenu(self); edit = menu.addAction(f"✏️ Edit"); delete = menu.addAction(f"🗑️ Delete")
        action = menu.exec_(self.table.verticalHeader().mapToGlobal(pos))
        if action == edit: self.edit_habit_by_row(row)
        elif action == delete:
            reply = QMessageBox.question(self, 'Delete Habit', f"Are you sure you want to delete '{self.habit_names[habit_idx]}'?\nThis cannot be fully undone once you close the app.", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes: self.delete_habit(habit_idx)

    def delete_habit(self, habit_idx):
        name = self.habit_names[habit_idx]
        
        # 1. Capture History
        history_snapshot = {y: self.history_data[y][habit_idx] for y in self.history_data}
        
        # 2. Capture Notes Snapshot & Clean Notes Data
        notes_snapshot = {}
        for y, y_data in self.notes_data.items():
            if habit_idx in y_data:
                notes_snapshot[y] = y_data[habit_idx]
        
        self._last_deleted_habit = { 
            "index": habit_idx, "name": name, "time": self.habit_times[habit_idx], 
            "history": history_snapshot, "notes": notes_snapshot 
        }

        # 3. Modify Core Lists
        if self.selected_habit_idx == habit_idx: self.selected_habit_idx = None; self.btn_habit_filter.setText("Global Overview")
        self.habit_names.pop(habit_idx); self.habit_times.pop(habit_idx)
        for y in self.history_data: self.history_data[y].pop(habit_idx)

        # 4. Shift Notes Indices (Crucial for integrity)
        for y in self.notes_data:
            if habit_idx in self.notes_data[y]: del self.notes_data[y][habit_idx]
            new_y_notes = {}
            for h_id, notes in self.notes_data[y].items():
                if h_id > habit_idx: new_y_notes[h_id - 1] = notes
                elif h_id < habit_idx: new_y_notes[h_id] = notes
            self.notes_data[y] = new_y_notes

        self.save_data(); new_slice = self.get_month_slice(self.view_year, self.view_month); self.model.update_view(self.view_year, self.view_month, new_slice)
        self.update_table_height(); self.refresh_habit_menu(); self.trigger_full_update(); self.undo_bar.show_message(f"Deleted '{name}'", is_dark=self.is_dark_mode)

    def restore_last_deleted(self):
        if not self._last_deleted_habit: return
        data = self._last_deleted_habit; idx = data["index"]
        if idx > len(self.habit_names): idx = len(self.habit_names)
        
        # 1. Restore Core Data
        self.habit_names.insert(idx, data["name"]); self.habit_times.insert(idx, data["time"])
        for y in self.history_data: 
            row_data = data["history"].get(y, [0] * (366 if calendar.isleap(int(y)) else 365))
            self.history_data[y].insert(idx, row_data)
        
        # 2. Shift Notes Up & Restore
        for y in self.notes_data:
            new_y_notes = {}
            for h_id, notes in self.notes_data[y].items():
                if h_id >= idx: new_y_notes[h_id + 1] = notes
                else: new_y_notes[h_id] = notes
            self.notes_data[y] = new_y_notes
            
        # 3. Restore deleted notes
        for y, notes in data["notes"].items():
            if y not in self.notes_data: self.notes_data[y] = {}
            self.notes_data[y][idx] = notes

        self._last_deleted_habit = None; self.undo_bar.hide(); self.save_data(); self.sanitize_data(self.view_year)
        new_slice = self.get_month_slice(self.view_year, self.view_month); self.model.update_view(self.view_year, self.view_month, new_slice)
        self.update_table_height(); self.refresh_habit_menu(); self.trigger_full_update()

    def add_habit(self):
        d = HabitDialog(self, is_dark=self.is_dark_mode)
        if d.exec_() == QDialog.Accepted:
            n, t = d.get_data()
            if n:
                self.habit_names.append(n); self.habit_times.append(t)
                self.sanitize_data(self.view_year) 
                self.save_data(); new_slice = self.get_month_slice(self.view_year, self.view_month); self.model.update_view(self.view_year, self.view_month, new_slice)
                self.update_table_height(); self.refresh_habit_menu(); self.trigger_full_update()

    def update_table_height(self):
        total_rows = len(self.habit_names) + 2
        scrollbar_height = self.style().pixelMetric(QStyle.PM_ScrollBarExtent)
        h = (total_rows * self.row_height) + scrollbar_height + 2
        self.table.setFixedHeight(h)

    def on_cell_clicked(self, index): self.model.toggle(index)
    def on_data_toggled(self, habit_idx, col_in_month):
        start_of_month_idx = datetime.date(self.view_year, self.view_month, 1).timetuple().tm_yday - 1; global_idx = start_of_month_idx + col_in_month
        val = self.model._month_data[habit_idx][col_in_month]; self.history_data[str(self.view_year)][habit_idx][global_idx] = val
        self.save_data(); self.update_kpis(); self.chart_update_timer.start(300)

    def save_data(self):
        geo = self.saveGeometry().toBase64().data().decode(); is_max = self.isMaximized()
        data = { "names": self.habit_names, "times": self.habit_times, "history": self.history_data, "notes": self.notes_data, "theme": self.is_dark_mode, "window_geometry": geo, "window_maximized": is_max }
        with open(DATA_FILE, "w") as f: json.dump(data, f)

    def closeEvent(self, event): self.save_data(); event.accept()
    def backup_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Backup", f"Habit_Backup_{datetime.date.today()}.json", "JSON (*.json)")
        if path: self.save_data(); 
        with open(DATA_FILE, "r") as src, open(path, "w") as dst: dst.write(src.read())
    def restore_data(self):
        path, _ = QFileDialog.getOpenFileName(self, "Restore", "", "JSON (*.json)")
        if path:
            try:
                with open(path, "r") as f:
                    d = json.load(f); self.habit_names = d.get("names", []); self.habit_times = d.get("times", []); self.is_dark_mode = d.get("theme", False)
                    raw = d.get("data", []); self.history_data = {"2026": raw} if raw and isinstance(raw[0], list) else d.get("history", {})
                    self.notes_data = {}; raw_notes = d.get("notes", {})
                    for y, y_data in raw_notes.items():
                        self.notes_data[y] = {}
                        for h_idx, h_data in y_data.items():
                            self.notes_data[y][int(h_idx)] = {int(k):v for k,v in h_data.items()}
                    self.sanitize_data(self.view_year); self.model.update_view(self.view_year, self.view_month, self.get_month_slice(self.view_year, self.view_month))
                    self.update_table_height(); self.apply_theme(); self.save_data(); self.refresh_habit_menu()
            except: pass

    def calculate_stats(self, habit_idx=None):
        n = len(self.habit_names)
        if n == 0: return {}
        real_today = datetime.date.today()
        if self.view_year == real_today.year and self.view_month == real_today.month: ref_date = real_today
        else: last_day = calendar.monthrange(self.view_year, self.view_month)[1]; ref_date = datetime.date(self.view_year, self.view_month, last_day)
        def get_val_on_date(d, h_idx):
            y_str = str(d.year)
            if y_str not in self.history_data: self.sanitize_data(d.year)
            day_idx = d.timetuple().tm_yday - 1; year_data = self.history_data[y_str]
            if day_idx < 0 or day_idx >= len(year_data[0]): return 0
            if h_idx is None: return sum(year_data[r][day_idx] for r in range(n)) / n if n > 0 else 0
            return year_data[h_idx][day_idx]
        today_score = get_val_on_date(real_today, habit_idx); today_display = f"{int(today_score * 100)}%"
        days_since_monday = real_today.weekday(); current_week_vals = []
        for i in range(days_since_monday + 1): check_date = real_today - datetime.timedelta(days=days_since_monday - i); current_week_vals.append(get_val_on_date(check_date, habit_idx))
        weekly_avg = int((sum(current_week_vals) / len(current_week_vals)) * 100) if current_week_vals else 0
        monthly_vals = []
        for i in range(1, ref_date.day + 1): check_date = datetime.date(self.view_year, self.view_month, i); monthly_vals.append(get_val_on_date(check_date, habit_idx))
        monthly_avg = int((sum(monthly_vals) / len(monthly_vals)) * 100) if monthly_vals else 0
        self.sanitize_data(self.view_year); curr_year_data = self.history_data[str(self.view_year)]
        if habit_idx is None: total_count = sum(sum(row) for row in curr_year_data)
        else: total_count = sum(curr_year_data[habit_idx])
        streak = 0; curr = 0; ref_idx_limit = ref_date.timetuple().tm_yday
        for c in range(ref_idx_limit):
            success = all(curr_year_data[r][c] == 1 for r in range(n)) if habit_idx is None else curr_year_data[habit_idx][c] == 1
            if success: curr += 1; streak = max(streak, curr)
            else: curr = 0
        return { "today": today_display, "streak": f"{streak} Days", "weekly": f"{weekly_avg}%", "monthly": f"{monthly_avg}%", "total": str(total_count) }
    
    def trigger_full_update(self): self.update_kpis(); self.update_charts_data_only()
    def update_kpis(self):
        if not hasattr(self, 'kpi_cards'): return
        stats = self.calculate_stats(self.selected_habit_idx)
        if not stats: return
        self.card_total.lbl_title.setText("TOTAL TASKS" if self.selected_habit_idx is None else "TOTAL DAYS")
        self.card_today.set_value(stats["today"]); self.card_streak.set_value(stats["streak"]); self.card_weekly.set_value(stats["weekly"]); self.card_monthly.set_value(stats["monthly"]); self.card_total.set_value(stats["total"])
    def update_charts_data_only(self):
        if not hasattr(self, 'ax_annual'): return
        target_habit_idx = self.selected_habit_idx; n = len(self.habit_names); theme = THEME_DARK if self.is_dark_mode else THEME_LIGHT
        self.sanitize_data(self.view_year); current_data = self.history_data[str(self.view_year)]; days_in_year = len(current_data[0])
        if target_habit_idx is not None:
            if target_habit_idx >= len(current_data): return 
            daily_avgs = [current_data[target_habit_idx][c] * 100 for c in range(days_in_year)]; chart_title = f"Consistency Trend: {self.habit_names[target_habit_idx]} ({self.view_year})"
        else: daily_avgs = [sum(current_data[r][c] for r in range(n))/n*100 if n > 0 else 0 for c in range(days_in_year)]; chart_title = f"Consistency Trend: Global ({self.view_year})"
        self.line_annual.set_data(range(days_in_year), daily_avgs); self.line_annual.set_color(theme['chart_line'])
        self.ax_annual.set_title(chart_title, color=theme['text_primary'], fontsize=10, weight='bold', pad=10)
        self.ax_annual.set_ylim(0, 105); self.ax_annual.set_xlim(0, days_in_year)
        self.ax_annual.set_ylabel("Completion Rate (%)", color=theme['text_secondary'], fontsize=9)
        self.ax_annual.tick_params(axis='x', colors=theme['text_secondary']); self.ax_annual.tick_params(axis='y', colors=theme['text_secondary'])
        self.ax_annual.spines['bottom'].set_color(theme['border']); self.ax_annual.spines['left'].set_color(theme['border'])
        self.fig_annual.patch.set_facecolor(theme['chart_bg']); self.ax_annual.set_facecolor(theme['chart_bg'])
        if self.fill_annual: self.fill_annual.remove()
        fill_rgba = tuple(int(theme['chart_fill'].lstrip('#')[i:i+2], 16)/255. for i in (0, 2, 4)) + (0.15,)
        self.fill_annual = self.ax_annual.fill_between(range(days_in_year), daily_avgs, color=fill_rgba)
        month_starts = [datetime.date(self.view_year, m, 1).timetuple().tm_yday - 1 for m in range(1, 13)]
        self.ax_annual.set_xticks(month_starts); self.ax_annual.set_xticklabels([calendar.month_abbr[m] for m in range(1, 13)], rotation=0, fontsize=8); self.canvas_annual.draw_idle()
        monthly_data = {}
        for c in range(days_in_year):
            d_date = datetime.date(self.view_year, 1, 1) + datetime.timedelta(days=c); m = d_date.month
            if m not in monthly_data: monthly_data[m] = []
            if target_habit_idx is not None: monthly_data[m].append(current_data[target_habit_idx][c] * 100)
            else: monthly_data[m].append(sum(current_data[r][c] for r in range(n))/n*100 if n > 0 else 0)
        month_avgs = [sum(monthly_data[m])/len(monthly_data[m]) if m in monthly_data else 0 for m in range(1, 13)]
        for bar, h, lbl in zip(self.bars_monthly, month_avgs, self.bar_labels):
            bar.set_height(h); bar.set_color(theme['chart_bar'])
            if h > 1: lbl.set_text(f"{int(h)}%"); lbl.set_y(h + 2); lbl.set_color(theme['text_primary']); lbl.set_visible(True)
            else: lbl.set_visible(False)
        self.ax_monthly.set_title(f"Success Rate by Month ({self.view_year})", color=theme['text_primary'], fontsize=10, weight='bold', pad=10)
        self.ax_monthly.set_ylabel("Average (%)", color=theme['text_secondary'], fontsize=9)
        self.ax_monthly.tick_params(axis='x', colors=theme['text_secondary']); self.ax_monthly.tick_params(axis='y', colors=theme['text_secondary'])
        self.ax_monthly.spines['bottom'].set_color(theme['border']); self.fig_monthly.patch.set_facecolor(theme['chart_bg']); self.ax_monthly.set_facecolor(theme['chart_bg'])
        self.ax_monthly.set_xticks(range(12)); self.ax_monthly.set_xticklabels([calendar.month_abbr[m] for m in range(1, 13)]); self.ax_monthly.set_ylim(0, 115); self.canvas_monthly.draw_idle()

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", f"Habits_{self.view_year}.csv", "CSV (*.csv)")
        if path:
            current_data = self.history_data[str(self.view_year)]
            with open(path, "w", newline="") as f:
                writer = csv.writer(f); writer.writerow(["--- HABIT DATA ---"]); writer.writerow(["Date"] + [f"{n}" for n in self.habit_names]); start = datetime.date(self.view_year, 1, 1)
                for i in range(len(current_data[0])): d = start + datetime.timedelta(days=i); row = [d.strftime("%Y-%m-%d")] + ["Yes" if current_data[r][i] else "No" for r in range(len(self.habit_names))]; writer.writerow(row)
            QMessageBox.information(self, "Export", "CSV saved successfully!")
    def export_pdf(self):
        from reportlab.lib.pagesizes import letter; from reportlab.pdfgen import canvas
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"Habit_Report_{self.view_year}.pdf", "PDF (*.pdf)")
        if not path: return
        try:
            stats = self.calculate_stats(self.selected_habit_idx)
            self.fig_annual.savefig("temp_annual.png", facecolor=self.fig_annual.get_facecolor(), dpi=150)
            self.fig_monthly.savefig("temp_monthly.png", facecolor=self.fig_monthly.get_facecolor(), dpi=150)
            c = canvas.Canvas(path, pagesize=letter); w, h = letter
            c.setFont("Helvetica-Bold", 24); c.drawString(50, h-50, f"Habit Report {self.view_year}")
            subtitle = "Global Overview" if self.selected_habit_idx is None else self.habit_names[self.selected_habit_idx]
            c.setFont("Helvetica", 12); y_text = h - 90; c.drawString(50, y_text, f"• Report: {subtitle}")
            y_start = h - 120; c.drawString(50, y_start, f"• Today's Completion: {stats.get('today', 'N/A')}"); c.drawString(300, y_start, f"• Best Streak: {stats.get('streak', 'N/A')}")
            y_start -= 25; c.drawString(50, y_start, f"• Weekly Average: {stats.get('weekly', 'N/A')}"); c.drawString(300, y_start, f"• Monthly Average: {stats.get('monthly', 'N/A')}")
            y_start -= 25; c.drawString(50, y_start, f"• Total Completions: {stats.get('total', 'N/A')}")
            c.drawImage("temp_annual.png", 50, h-400, width=500, height=200, preserveAspectRatio=True); c.drawImage("temp_monthly.png", 50, h-650, width=500, height=200, preserveAspectRatio=True)
            c.save(); os.remove("temp_annual.png"); os.remove("temp_monthly.png")
            QMessageBox.information(self, "Export", "PDF saved successfully!")
        except Exception as e: QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv); app.setFont(QFont("Segoe UI", 10))
    window = HabitApp(); window.show(); sys.exit(app.exec())