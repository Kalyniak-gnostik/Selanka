import sys
import json
import base64
import copy
import math
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPixmapItem,
                             QGraphicsItem, QGraphicsPathItem, QColorDialog, QLabel, QCheckBox, QFileDialog,
                             QMessageBox, QScrollArea, QGridLayout, QSpinBox, QGroupBox, 
                             QComboBox, QSlider, QDialog, QRadioButton, QDialogButtonBox, 
                             QMenu, QDoubleSpinBox, QGraphicsLineItem, QTabWidget,
                             QListWidget, QListWidgetItem, QToolBar, QLineEdit,
                             QFormLayout, QInputDialog, QSizePolicy, QFrame)
from PyQt6.QtGui import (QColor, QPen, QBrush, QPainter, QImage, QKeySequence, QShortcut, QAction,
                         QPixmap, QPainterPath, QPainterPathStroker, QTransform, QCursor, QPageLayout, QIcon, QFont, QFontMetrics)
from PyQt6.QtCore import Qt, QRectF, QBuffer, QIODevice, QPointF, pyqtSignal, QSettings, QTimer, QSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

try:
    from PyQt6.QtSvg import QSvgGenerator
except ImportError:
    QSvgGenerator = None

# Фікс для іконки на панелі завдань Windows
if os.name == 'nt':
    import ctypes
    try:
        myappid = 'sashadev.selankaeditor.pro.6'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

# Функція для правильного пошуку файлів (іконки) після компіляції в .exe
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

UI_TEXT = {
    "uk": {
        "app": "Редактор Силянок", "new": "Новий проєкт", "open": "Відкрити", "recent": "Останній проєкт",
        "save": "Зберегти", "undo": "Скасувати", "redo": "Повторити", "pdf": "Експорт PDF",
        "clear": "Очистити полотно", "zoom": "Масштаб", "dark": "Темна тема", "light": "Світла тема",
        "fullscreen": "На весь екран", "language": "Мова інтерфейсу", "drawing": "Малювання",
        "pencil": "Пензель", "eraser": "Гумка", "fill": "Заливка", "eyedropper": "Піпетка",
        "line": "Лінія", "shape": "Фігура", "text": "Текст у сітку", "select": "Виділення", "shift_row": "Зсув одного рядка",
        "thickness": "Товщина", "symmetry": "Симетрія", "horizontal": "Горизонтальна", "vertical": "Вертикальна",
        "selected_fragment": "Виділений фрагмент", "mirror_h": "Дзеркало ліво/право", "mirror_v": "Дзеркало верх/низ",
        "rotate": "Повернути 90°", "bulk_shift": "Масовий зсув рядків", "generator": "Генератор орнаменту",
        "product": "Виріб", "colors": "Кольори", "layers": "Шари", "export": "Експорт",
        "pick_color": "Вибрати свій колір", "quick_palette": "Швидка палітра", "canvas_bg": "Колір фону полотна",
        "sketch": "Ескіз", "load_image": "Завантажити зображення", "fit_image": "Вписати зображення у сітку",
        "convert_image": "Перетворити зображення у схему", "lock": "Зафіксувати", "opacity": "Прозорість",
        "remove_sketch": "Видалити ескіз", "no_sketch": "Ескіз не завантажено", "help": "Пробіл + перетягування — рух · колесо — масштаб · Ctrl+C / Ctrl+V — фрагмент · 1…9 — колір",
        "add_layer": "Додати шар", "duplicate_layer": "Дублювати шар", "rename_layer": "Перейменувати шар",
        "delete_layer": "Видалити шар", "visibility": "Видимість шару", "locking": "Блокування шару",
        "resize": "Застосувати розмір", "hide_grid": "Приховати лінії сітки", "ready": "Готово",
        "title": "Назва", "author": "Автор", "type": "Тип", "grid": "Сітка", "form": "Форма", "rows": "Рядків", "columns": "Стовпців",
        "visible": "Видимий", "hidden": "Прихований", "locked": "заблокований", "filled_shape": "Суцільна заливка",
        "export_info": "Експорт містить назву, автора, дату, нумерацію сторінок і легенду кольорів.", "pdf_print": "PDF для друку",
        "image_export": "PNG / JPG", "svg_export": "SVG", "text_export": "Текстова схема", "print_preview": "Попередній перегляд друку",
        "bead_calc": "Калькулятор бісеру", "empty": "Поки пусто",
    },
    "en": {
        "app": "Selanka Editor", "new": "New project", "open": "Open", "recent": "Open recent project",
        "save": "Save", "undo": "Undo", "redo": "Redo", "pdf": "Export PDF",
        "clear": "Clear canvas", "zoom": "Zoom", "dark": "Dark theme", "light": "Light theme",
        "fullscreen": "Full screen", "language": "Interface language", "drawing": "Drawing",
        "pencil": "Brush", "eraser": "Eraser", "fill": "Flood fill", "eyedropper": "Eyedropper",
        "line": "Line", "shape": "Shape", "text": "Text on grid", "select": "Selection", "shift_row": "Shift one row",
        "thickness": "Brush size", "symmetry": "Symmetry", "horizontal": "Horizontal", "vertical": "Vertical",
        "selected_fragment": "Selected fragment", "mirror_h": "Mirror left/right", "mirror_v": "Mirror top/bottom",
        "rotate": "Rotate 90°", "bulk_shift": "Bulk row shift", "generator": "Pattern generator",
        "product": "Product", "colors": "Colors", "layers": "Layers", "export": "Export",
        "pick_color": "Choose custom color", "quick_palette": "Quick palette", "canvas_bg": "Canvas background",
        "sketch": "Reference image", "load_image": "Load image", "fit_image": "Fit image to grid",
        "convert_image": "Convert image to pattern", "lock": "Lock image", "opacity": "Opacity",
        "remove_sketch": "Remove image", "no_sketch": "No image loaded", "help": "Space + drag — pan · wheel — zoom · Ctrl+C / Ctrl+V — fragment · 1…9 — color",
        "add_layer": "Add layer", "duplicate_layer": "Duplicate layer", "rename_layer": "Rename layer",
        "delete_layer": "Delete layer", "visibility": "Layer visibility", "locking": "Lock layer",
        "resize": "Apply size", "hide_grid": "Hide grid lines", "ready": "Ready",
        "title": "Title", "author": "Author", "type": "Type", "grid": "Grid", "form": "Shape", "rows": "Rows", "columns": "Columns",
        "visible": "Visible", "hidden": "Hidden", "locked": "locked", "filled_shape": "Filled shape",
        "export_info": "The export includes title, author, date, page numbers, and a color legend.", "pdf_print": "Print-ready PDF",
        "image_export": "PNG / JPG", "svg_export": "SVG", "text_export": "Row-by-row text pattern", "print_preview": "Print preview",
        "bead_calc": "Bead calculator", "empty": "No beads yet",
    },
}

def make_icon(name, color="#818cf8"):
    """Create consistent vector-like toolbar icons without external asset files."""
    pixmap = QPixmap(36, 36); pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap); painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    pen = QPen(QColor(color), 2.6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pen); painter.setBrush(Qt.BrushStyle.NoBrush)
    if name in ("pencil", "line"):
        painter.drawLine(9, 27, 27, 9)
        if name == "pencil": painter.drawLine(8, 28, 13, 27); painter.drawLine(26, 8, 29, 11)
    elif name == "eraser":
        path = QPainterPath(); path.moveTo(8, 23); path.lineTo(20, 9); path.lineTo(29, 17); path.lineTo(18, 28); path.lineTo(8, 23); painter.drawPath(path)
    elif name == "fill":
        painter.drawRect(9, 10, 15, 15); painter.drawLine(9, 10, 24, 25); painter.setBrush(QColor(color)); painter.drawEllipse(QRectF(26, 23, 5, 7))
    elif name == "eyedropper":
        painter.drawEllipse(QRectF(22, 7, 7, 7)); painter.drawLine(25, 13, 11, 27); painter.drawLine(9, 25, 13, 29)
    elif name == "shape":
        painter.drawRoundedRect(QRectF(7, 8, 15, 15), 2, 2); painter.drawEllipse(QRectF(17, 17, 12, 12))
    elif name == "text":
        font = painter.font(); font.setPixelSize(25); font.setBold(True); painter.setFont(font); painter.drawText(QRectF(4, 3, 28, 30), Qt.AlignmentFlag.AlignCenter, "T")
    elif name == "select":
        painter.setPen(QPen(QColor(color), 2.2, Qt.PenStyle.DashLine)); painter.drawRect(7, 7, 22, 22)
    elif name in ("shift_row", "bulk"):
        for y, offset in ((10, 0), (18, 5 if name == "bulk" else 0), (26, 0)): painter.drawLine(7 + offset, y, 28 + offset, y)
        painter.drawLine(24, 14, 29, 18); painter.drawLine(29, 18, 24, 22)
    elif name in ("mirror_h", "mirror_v"):
        painter.setPen(QPen(QColor(color), 1.8, Qt.PenStyle.DashLine))
        if name == "mirror_h": painter.drawLine(18, 5, 18, 31); painter.setPen(pen); painter.drawRect(6, 11, 8, 14); painter.drawRect(22, 11, 8, 14)
        else: painter.drawLine(5, 18, 31, 18); painter.setPen(pen); painter.drawRect(11, 6, 14, 8); painter.drawRect(11, 22, 14, 8)
    elif name in ("undo", "redo"):
        path = QPainterPath(); path.moveTo(9 if name == "undo" else 27, 13); path.cubicTo(16, 5, 29, 10, 28 if name == "undo" else 8, 25); painter.drawPath(path)
        if name == "undo": painter.drawLine(9, 13, 15, 9); painter.drawLine(9, 13, 15, 17)
        else: painter.drawLine(27, 13, 21, 9); painter.drawLine(27, 13, 21, 17)
    elif name == "clear":
        painter.drawRoundedRect(QRectF(10, 11, 16, 20), 2, 2); painter.drawLine(8, 10, 28, 10); painter.drawLine(14, 6, 22, 6); painter.drawLine(15, 16, 15, 26); painter.drawLine(21, 16, 21, 26)
    elif name == "open":
        path = QPainterPath(); path.moveTo(6, 13); path.lineTo(15, 13); path.lineTo(18, 9); path.lineTo(30, 9); path.lineTo(27, 28); path.lineTo(6, 28); path.closeSubpath(); painter.drawPath(path)
    elif name == "save":
        painter.drawRoundedRect(QRectF(7, 6, 22, 24), 2, 2); painter.drawRect(11, 7, 13, 8); painter.drawRect(11, 20, 14, 9)
    elif name == "new":
        painter.drawRoundedRect(QRectF(7, 7, 22, 22), 3, 3); painter.drawLine(18, 12, 18, 24); painter.drawLine(12, 18, 24, 18)
    elif name == "recent":
        painter.drawEllipse(QRectF(7, 7, 22, 22)); painter.drawLine(18, 11, 18, 19); painter.drawLine(18, 19, 24, 22)
    elif name == "pdf":
        font = painter.font(); font.setPixelSize(10); font.setBold(True); painter.setFont(font); painter.drawRoundedRect(QRectF(6, 5, 24, 27), 2, 2); painter.drawText(QRectF(7, 10, 22, 16), Qt.AlignmentFlag.AlignCenter, "PDF")
    elif name == "rotate":
        painter.drawArc(QRectF(7, 7, 22, 22), 25 * 16, 285 * 16); painter.drawLine(27, 7, 29, 14); painter.drawLine(27, 7, 20, 9)
    elif name == "theme":
        painter.setBrush(QColor(color)); painter.drawEllipse(QRectF(7, 7, 22, 22)); painter.setBrush(QColor("#111827")); painter.drawEllipse(QRectF(15, 4, 18, 25))
    elif name == "fullscreen":
        painter.drawLine(7, 14, 7, 7); painter.drawLine(7, 7, 14, 7); painter.drawLine(22, 7, 29, 7); painter.drawLine(29, 7, 29, 14)
        painter.drawLine(7, 22, 7, 29); painter.drawLine(7, 29, 14, 29); painter.drawLine(22, 29, 29, 29); painter.drawLine(29, 29, 29, 22)
    elif name == "generator":
        painter.setPen(QPen(QColor(color), 1.8))
        for pos in (8, 14, 20, 26): painter.drawLine(pos, 7, pos, 29); painter.drawLine(7, pos, 29, pos)
        painter.setBrush(QColor(color)); painter.drawEllipse(QRectF(12, 12, 5, 5)); painter.drawEllipse(QRectF(24, 24, 5, 5))
    elif name == "duplicate":
        painter.drawRoundedRect(QRectF(7, 7, 17, 17), 2, 2); painter.drawRoundedRect(QRectF(13, 13, 17, 17), 2, 2)
    elif name == "visibility":
        path = QPainterPath(); path.moveTo(5, 18); path.cubicTo(11, 8, 25, 8, 31, 18); path.cubicTo(25, 28, 11, 28, 5, 18); painter.drawPath(path)
        painter.setBrush(QColor(color)); painter.drawEllipse(QRectF(14, 14, 8, 8))
    elif name == "lock":
        painter.drawRoundedRect(QRectF(9, 15, 18, 15), 2, 2); painter.drawArc(QRectF(12, 6, 12, 16), 0, 180 * 16)
    else:
        painter.drawRoundedRect(QRectF(7, 7, 22, 22), 3, 3); painter.drawEllipse(QRectF(15, 15, 6, 6))
    painter.end(); return QIcon(pixmap)

# ==============================================================================
# --- ВІДЖЕТИ ДОПОМІЖНІ ---
# ==============================================================================
class ColorPaletteButton(QPushButton):
    rightClicked = pyqtSignal()
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit()

class PrintSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        en = getattr(parent, "language", "uk") == "en"
        self.setWindowTitle("Print / PDF settings" if en else "Налаштування друку / PDF")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)

        group_scale = QGroupBox("Pattern scale" if en else "Масштаб малюнка")
        scale_layout = QVBoxLayout()
        self.radio_fit = QRadioButton("Fit on one page (automatic scale)" if en else "Вмістити на 1 сторінку (Авто-масштаб)")
        self.radio_fit.setChecked(True)
        self.radio_custom = QRadioButton("Custom size (may span multiple pages)" if en else "Свій розмір (Може розділити на сторінки)")
        
        scale_layout.addWidget(self.radio_fit)
        scale_layout.addWidget(self.radio_custom)
        
        custom_size_layout = QHBoxLayout()
        custom_size_layout.addWidget(QLabel("   Cell size:" if en else "   Розмір клітинки:"))
        self.spin_scale = QSpinBox()
        self.spin_scale.setRange(2, 50)
        self.spin_scale.setValue(5)
        self.spin_scale.setSuffix(" mm" if en else " мм")
        self.spin_scale.setEnabled(False)
        custom_size_layout.addWidget(self.spin_scale)
        custom_size_layout.addStretch()
        scale_layout.addLayout(custom_size_layout)
        group_scale.setLayout(scale_layout)
        self.radio_custom.toggled.connect(self.spin_scale.setEnabled)
        
        self.chk_calc = QCheckBox("Add bead calculator below the pattern" if en else "Додати калькулятор бісеру під малюнком")
        self.chk_calc.setChecked(True)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(group_scale)
        layout.addWidget(self.chk_calc)
        layout.addWidget(buttons)

    def get_settings(self):
        return {
            "fit_page": self.radio_fit.isChecked(),
            "cell_size_mm": self.spin_scale.value(),
            "show_calc": self.chk_calc.isChecked()
        }

class NewProjectDialog(QDialog):
    PRODUCT_TYPES = [
        ("Силянка / гердан", "loom"),
        ("Браслет на станку", "bracelet"),
        ("Пейот (мозаїка)", "peyote"),
        ("Цегляне плетіння", "brick"),
        ("Жгут (розгортка)", "rope"),
        ("Сережки", "earrings"),
        ("Кулон", "pendant"),
        ("Бахрома", "fringe"),
    ]
    GRID_TYPES = [
        ("Рівна", "regular"),
        ("Пейот — парний", "peyote_even"),
        ("Пейот — непарний", "peyote_odd"),
        ("Brick stitch", "brick"),
        ("Власний / масовий зсув", "custom"),
    ]
    SHAPES = [
        ("Прямокутник", "rectangle"),
        ("Трикутник", "triangle"),
        ("Ромб", "diamond"),
        ("Коло / овал", "circle"),
        ("Пара сережок", "earrings_pair"),
        ("Підвіска", "pendant"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.language = getattr(parent, "language", "uk"); en = self.language == "en"
        self.setWindowTitle("New project" if en else "Новий проєкт")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title_edit = QLineEdit("New beadwork" if en else "Нова силянка")
        self.product_combo = QComboBox()
        self.grid_combo = QComboBox()
        self.shape_combo = QComboBox()
        product_en = {"loom": "Silianka / gerdan", "bracelet": "Loom bracelet", "peyote": "Peyote stitch", "brick": "Brick stitch", "rope": "Beaded rope", "earrings": "Earrings", "pendant": "Pendant", "fringe": "Fringe"}
        grid_en = {"regular": "Regular", "peyote_even": "Even-count peyote", "peyote_odd": "Odd-count peyote", "brick": "Brick stitch", "custom": "Custom / bulk shift"}
        shape_en = {"rectangle": "Rectangle", "triangle": "Triangle", "diamond": "Diamond", "circle": "Circle / ellipse", "earrings_pair": "Earring pair", "pendant": "Pendant"}
        for label, value in self.PRODUCT_TYPES: self.product_combo.addItem(product_en.get(value, label) if en else label, value)
        for label, value in self.GRID_TYPES: self.grid_combo.addItem(grid_en.get(value, label) if en else label, value)
        for label, value in self.SHAPES: self.shape_combo.addItem(shape_en.get(value, label) if en else label, value)
        self.rows_spin = QSpinBox(); self.rows_spin.setRange(3, 500); self.rows_spin.setValue(50)
        self.cols_spin = QSpinBox(); self.cols_spin.setRange(3, 500); self.cols_spin.setValue(70)
        form.addRow("Title:" if en else "Назва:", self.title_edit)
        form.addRow("Product type:" if en else "Тип виробу:", self.product_combo)
        form.addRow("Grid type:" if en else "Тип сітки:", self.grid_combo)
        form.addRow("Shape:" if en else "Форма:", self.shape_combo)
        form.addRow("Rows:" if en else "Рядків:", self.rows_spin)
        form.addRow("Columns:" if en else "Стовпців:", self.cols_spin)
        layout.addLayout(form)
        hint = QLabel("The grid type can be changed later in the Product tab." if en else "Тип сітки можна змінити пізніше у вкладці «Виріб».")
        hint.setWordWrap(True); hint.setObjectName("mutedLabel")
        layout.addWidget(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.product_combo.currentIndexChanged.connect(self._suggest_grid)

    def _suggest_grid(self):
        product = self.product_combo.currentData()
        grid = "peyote_even" if product == "peyote" else "brick" if product == "brick" else "regular"
        index = self.grid_combo.findData(grid)
        if index >= 0: self.grid_combo.setCurrentIndex(index)
        shape = "earrings_pair" if product == "earrings" else "pendant" if product == "pendant" else "rectangle"
        index = self.shape_combo.findData(shape)
        if index >= 0: self.shape_combo.setCurrentIndex(index)

    def values(self):
        return {
            "title": self.title_edit.text().strip() or ("Untitled" if self.language == "en" else "Без назви"),
            "product_type": self.product_combo.currentData(),
            "grid_mode": self.grid_combo.currentData(),
            "shape": self.shape_combo.currentData(),
            "rows": self.rows_spin.value(),
            "cols": self.cols_spin.value(),
        }

class MaterialDialog(QDialog):
    def __init__(self, color, data=None, parent=None):
        super().__init__(parent); data = data or {}; en = getattr(parent, "language", "uk") == "en"
        self.setWindowTitle(f"Material {color}" if en else f"Матеріал {color}"); self.setMinimumWidth(380)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.code = QLineEdit(data.get("code", color)); self.name = QLineEdit(data.get("name", ""))
        self.price = QDoubleSpinBox(); self.price.setRange(0, 1_000_000); self.price.setDecimals(2); self.price.setSuffix(" UAH" if en else " грн"); self.price.setValue(float(data.get("price", 0) or 0))
        self.stock = QSpinBox(); self.stock.setRange(0, 10_000_000); self.stock.setSuffix(" pcs" if en else " шт."); self.stock.setValue(int(data.get("stock", 0) or 0))
        self.note = QLineEdit(data.get("note", ""))
        form.addRow("Code" if en else "Код", self.code); form.addRow("Name" if en else "Назва", self.name); form.addRow("Price" if en else "Ціна", self.price); form.addRow("In stock" if en else "Є в запасі", self.stock); form.addRow("Note" if en else "Нотатка", self.note); layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def values(self):
        return {"code": self.code.text().strip(), "name": self.name.text().strip(), "price": self.price.value(), "stock": self.stock.value(), "note": self.note.text().strip()}

class TextPatternDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.language = getattr(parent, "language", "uk"); en = self.language == "en"
        self.setWindowTitle("Text on grid" if en else "Текст у сітку")
        self.setMinimumWidth(390)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.text_edit = QLineEdit(); self.text_edit.setPlaceholderText("For example: UKRAINE" if en else "Наприклад: УКРАЇНА")
        self.font_combo = QComboBox(); self.font_combo.addItems(["Arial", "Segoe UI", "Consolas", "Times New Roman"])
        self.height_spin = QSpinBox(); self.height_spin.setRange(5, 50); self.height_spin.setValue(11); self.height_spin.setSuffix(" cells" if en else " клітинок")
        self.bold_check = QCheckBox("Bold text" if en else "Жирний текст"); self.bold_check.setChecked(True)
        form.addRow("Text:" if en else "Текст:", self.text_edit); form.addRow("Font:" if en else "Шрифт:", self.font_combo); form.addRow("Height:" if en else "Висота:", self.height_spin); form.addRow("", self.bold_check)
        layout.addLayout(form)
        hint = QLabel("Letters will be converted to colored cells starting from the selected point." if en else "Літери будуть перетворені на кольорові клітинки, починаючи з вибраної точки.")
        hint.setWordWrap(True); hint.setObjectName("mutedLabel"); layout.addWidget(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def accept(self):
        if not self.text_edit.text():
            QMessageBox.warning(self, "Text" if self.language == "en" else "Текст", "Enter text." if self.language == "en" else "Введіть текст."); return
        super().accept()

    def values(self):
        return {"text": self.text_edit.text(), "family": self.font_combo.currentText(),
                "height": self.height_spin.value(), "bold": self.bold_check.isChecked()}

class BulkShiftDialog(QDialog):
    def __init__(self, max_rows, parent=None):
        super().__init__(parent); self.language = getattr(parent, "language", "uk"); en = self.language == "en"
        self.setWindowTitle("Bulk row shift" if en else "Масовий зсув рядків"); self.setMinimumWidth(430)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.first_row = QSpinBox(); self.first_row.setRange(1, max_rows); self.first_row.setValue(2)
        self.skip_rows = QSpinBox(); self.skip_rows.setRange(0, max(0, max_rows - 1)); self.skip_rows.setValue(1)
        self.reset_existing = QCheckBox("Clear existing shifts first" if en else "Спочатку прибрати попередні зсуви"); self.reset_existing.setChecked(True)
        form.addRow("First shifted row:" if en else "Перший зсунутий рядок:", self.first_row)
        form.addRow("Rows to skip between shifts:" if en else "Пропускати рядків між зсунутими:", self.skip_rows)
        form.addRow("", self.reset_existing); layout.addLayout(form)
        self.example = QLabel(); self.example.setWordWrap(True); self.example.setObjectName("mutedLabel"); layout.addWidget(self.example)
        self.first_row.valueChanged.connect(self.update_example); self.skip_rows.valueChanged.connect(self.update_example); self.update_example()
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def update_example(self):
        first, step = self.first_row.value(), self.skip_rows.value() + 1
        rows = [str(first + index * step) for index in range(5)]
        if self.language == "en":
            self.example.setText("Shifted rows: " + ", ".join(rows) + "…  " + ("Skip 1 = every second row." if self.skip_rows.value() == 1 else ""))
        else:
            self.example.setText("Будуть зсунуті рядки: " + ", ".join(rows) + "…  " + ("Через 1 = кожен другий рядок." if self.skip_rows.value() == 1 else ""))

    def values(self):
        return self.first_row.value() - 1, self.skip_rows.value(), self.reset_existing.isChecked()

class ImageConversionDialog(QDialog):
    """Налаштування квантування фото з живим попереднім переглядом."""
    def __init__(self, samples, rows, cols, quick_palette, parent=None):
        super().__init__(parent)
        self.language = getattr(parent, "language", "uk"); en = self.language == "en"
        self.samples = samples; self.rows = rows; self.cols = cols
        self.quick_palette = list(dict.fromkeys(QColor(value).name() for value in quick_palette if QColor(value).isValid()))
        self.palette_cache = {}; self.result = {}; self.result_palette = []
        self.setWindowTitle("Convert image to pattern" if en else "Перетворення зображення у схему")
        self.resize(900, 680)
        root = QVBoxLayout(self)
        settings = QGroupBox("Color settings" if en else "Налаштування кольорів"); form = QFormLayout(settings)
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Automatic approximate colors from image" if en else "Автокольори з фото (наближені)", "auto")
        self.mode_combo.addItem("Nearest colors from quick palette" if en else "Найближчі зі швидкої палітри", "palette")
        count_row = QHBoxLayout()
        less = QPushButton("− Fewer" if en else "− Менше"); more = QPushButton("More +" if en else "Більше +")
        self.count_spin = QSpinBox(); self.count_spin.setRange(2, 32); self.count_spin.setValue(min(10, max(2, len(self.quick_palette))))
        self.count_slider = QSlider(Qt.Orientation.Horizontal); self.count_slider.setRange(2, 32); self.count_slider.setValue(self.count_spin.value())
        less.clicked.connect(lambda: self.count_spin.setValue(self.count_spin.value() - 1))
        more.clicked.connect(lambda: self.count_spin.setValue(self.count_spin.value() + 1))
        self.count_spin.valueChanged.connect(self.count_slider.setValue); self.count_slider.valueChanged.connect(self.count_spin.setValue)
        count_row.addWidget(less); count_row.addWidget(self.count_spin); count_row.addWidget(more); count_row.addWidget(self.count_slider, 1)
        form.addRow("Mode:" if en else "Режим:", self.mode_combo); form.addRow("Number of colors:" if en else "Кількість кольорів:", count_row); root.addWidget(settings)
        self.preview_label = QLabel(); self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter); self.preview_label.setMinimumSize(700, 390)
        preview_scroll = QScrollArea(); preview_scroll.setWidgetResizable(True); preview_scroll.setWidget(self.preview_label); root.addWidget(preview_scroll, 1)
        self.info_label = QLabel(); self.info_label.setWordWrap(True); root.addWidget(self.info_label)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Create pattern" if en else "Створити схему")
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); root.addWidget(buttons)
        self.mode_combo.currentIndexChanged.connect(self.mode_changed); self.count_spin.valueChanged.connect(self.update_preview)
        self.mode_changed()

    def mode_changed(self):
        maximum = max(2, len(self.quick_palette)) if self.mode_combo.currentData() == "palette" else 32
        self.count_spin.setMaximum(maximum); self.count_slider.setMaximum(maximum)
        if self.count_spin.value() > maximum: self.count_spin.setValue(maximum)
        self.update_preview()

    @staticmethod
    def distance(color, center):
        return .30 * (color[0] - center[0]) ** 2 + .59 * (color[1] - center[1]) ** 2 + .11 * (color[2] - center[2]) ** 2

    def automatic_palette(self, count):
        histogram = {}
        for _, _, red, green, blue in self.samples:
            key = (red, green, blue); histogram[key] = histogram.get(key, 0) + 1
        points = sorted(histogram.items(), key=lambda item: item[1], reverse=True)[:4096]
        if not points: return []
        centers = [points[0][0]]
        while len(centers) < min(count, len(points)):
            candidate = max(points, key=lambda item: min(self.distance(item[0], center) for center in centers) * math.log2(item[1] + 1))[0]
            if candidate in centers: break
            centers.append(candidate)
        for _ in range(7):
            totals = [[0.0, 0.0, 0.0, 0] for _ in centers]
            for color, weight in points:
                index = min(range(len(centers)), key=lambda idx: self.distance(color, centers[idx]))
                totals[index][0] += color[0] * weight; totals[index][1] += color[1] * weight
                totals[index][2] += color[2] * weight; totals[index][3] += weight
            updated = [tuple(round(total[channel] / total[3]) for channel in range(3)) if total[3] else centers[index]
                       for index, total in enumerate(totals)]
            if updated == centers: break
            centers = updated
        return [QColor(*center).name() for center in centers]

    def nearest_quick_palette(self, count):
        candidates = [(QColor(value).red(), QColor(value).green(), QColor(value).blue(), value) for value in self.quick_palette]
        usage = {value: 0 for value in self.quick_palette}
        for _, _, red, green, blue in self.samples:
            nearest = min(candidates, key=lambda color: self.distance((red, green, blue), color))[3]; usage[nearest] += 1
        return sorted(self.quick_palette, key=lambda value: usage[value], reverse=True)[:count]

    def update_preview(self):
        if not self.samples: return
        mode, count = self.mode_combo.currentData(), self.count_spin.value(); cache_key = (mode, count)
        if cache_key not in self.palette_cache:
            self.palette_cache[cache_key] = self.automatic_palette(count) if mode == "auto" else self.nearest_quick_palette(count)
        palette = self.palette_cache[cache_key]
        centers = [(QColor(value).red(), QColor(value).green(), QColor(value).blue(), value) for value in palette]
        self.result = {}
        for row, col, red, green, blue in self.samples:
            nearest = min(centers, key=lambda color: self.distance((red, green, blue), color))
            self.result[(row, col)] = nearest[3]
        self.result_palette = palette
        cell = max(1, min(10, 720 // max(1, self.cols), 440 // max(1, self.rows)))
        image = QImage(max(1, self.cols * cell), max(1, self.rows * cell), QImage.Format.Format_RGB32); image.fill(QColor("#f8fafc"))
        painter = QPainter(image); painter.setPen(Qt.PenStyle.NoPen)
        for (row, col), color in self.result.items(): painter.fillRect(col * cell, row * cell, cell, cell, QColor(color))
        if cell >= 5:
            painter.setPen(QPen(QColor(80, 80, 80, 90), 1))
            for row in range(self.rows + 1): painter.drawLine(0, row * cell, self.cols * cell, row * cell)
            for col in range(self.cols + 1): painter.drawLine(col * cell, 0, col * cell, self.rows * cell)
        painter.end()
        pixmap = QPixmap.fromImage(image).scaled(760, 460, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        self.preview_label.setPixmap(pixmap)
        if self.language == "en":
            self.info_label.setText(f"Preview: {len(self.result)} cells · {len(palette)} colors\nPalette: " + "  ".join(value.upper() for value in palette))
        else:
            self.info_label.setText(f"Попередній результат: {len(self.result)} клітинок · {len(palette)} кольорів\nПалітра: " + "  ".join(value.upper() for value in palette))

class GridGeneratorDialog(QDialog):
    def __init__(self, current_color, parent=None):
        super().__init__(parent)
        en = getattr(parent, "language", "uk") == "en"
        self.setWindowTitle("Grid / pattern generator" if en else "Генератор сітки / Орнаменту")
        layout = QVBoxLayout(self)

        grid_layout = QGridLayout()
        self.spin_step_x = QSpinBox(); self.spin_step_x.setRange(1, 100); self.spin_step_x.setValue(5)
        self.spin_step_y = QSpinBox(); self.spin_step_y.setRange(1, 100); self.spin_step_y.setValue(5)
        self.spin_off_x = QSpinBox(); self.spin_off_x.setRange(0, 100)
        self.spin_off_y = QSpinBox(); self.spin_off_y.setRange(0, 100)
        
        # ДОДАНО: Кут та товщина
        self.spin_angle = QSpinBox(); self.spin_angle.setRange(-360, 360); self.spin_angle.setValue(0); self.spin_angle.setSuffix(" °")
        self.spin_thick = QDoubleSpinBox(); self.spin_thick.setRange(0.05, 1.0); self.spin_thick.setValue(0.15); self.spin_thick.setSingleStep(0.05)
        
        grid_layout.addWidget(QLabel("X step (cells):" if en else "Крок по X (клітинок):"), 0, 0); grid_layout.addWidget(self.spin_step_x, 0, 1)
        grid_layout.addWidget(QLabel("Y step (cells):" if en else "Крок по Y (клітинок):"), 1, 0); grid_layout.addWidget(self.spin_step_y, 1, 1)
        grid_layout.addWidget(QLabel("X offset:" if en else "Зсув по X:"), 2, 0); grid_layout.addWidget(self.spin_off_x, 2, 1)
        grid_layout.addWidget(QLabel("Y offset:" if en else "Зсув по Y:"), 3, 0); grid_layout.addWidget(self.spin_off_y, 3, 1)
        grid_layout.addWidget(QLabel("Angle:" if en else "Кут нахилу:"), 4, 0); grid_layout.addWidget(self.spin_angle, 4, 1)
        grid_layout.addWidget(QLabel("Line thickness:" if en else "Товщина ліній:"), 5, 0); grid_layout.addWidget(self.spin_thick, 5, 1)

        self.chk_horiz = QCheckBox("Draw horizontal lines" if en else "Малювати горизонтальні (січні) лінії")
        self.chk_horiz.setChecked(True)
        self.chk_vert = QCheckBox("Draw vertical lines" if en else "Малювати вертикальні (основні) лінії")
        self.chk_vert.setChecked(True)

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Line color:" if en else "Колір ліній:"))
        self.btn_color = QPushButton()
        self.grid_color = QColor(current_color)
        self.btn_color.setStyleSheet(f"background-color: {self.grid_color.name()}; width: 40px; height: 25px;")
        self.btn_color.clicked.connect(self.pick_color)
        color_layout.addWidget(self.btn_color)
        color_layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(grid_layout)
        layout.addWidget(self.chk_horiz)
        layout.addWidget(self.chk_vert)
        layout.addLayout(color_layout)
        layout.addWidget(buttons)

    def pick_color(self):
        c = QColorDialog.getColor(self.grid_color)
        if c.isValid():
            self.grid_color = c
            self.btn_color.setStyleSheet(f"background-color: {self.grid_color.name()}; width: 40px; height: 25px;")

    def get_settings(self):
        return {
            "step_x": self.spin_step_x.value(), "step_y": self.spin_step_y.value(),
            "off_x": self.spin_off_x.value(), "off_y": self.spin_off_y.value(),
            "angle": self.spin_angle.value(), "thick": self.spin_thick.value(),
            "color": self.grid_color, "horiz": self.chk_horiz.isChecked(), "vert": self.chk_vert.isChecked()
        }

# ==============================================================================
# --- ІНШІ КЛАСИ ---
# ==============================================================================
class SymLine(QGraphicsLineItem):
    def __init__(self, is_horizontal, canvas):
        super().__init__()
        self.is_horizontal = is_horizontal
        self.canvas = canvas
        self.setPen(QPen(QColor(255, 0, 0, 150), 6, Qt.PenStyle.SolidLine)) 
        self.setCursor(Qt.CursorShape.SizeVerCursor if is_horizontal else Qt.CursorShape.SizeHorCursor)
        self.setZValue(100)

    def mousePressEvent(self, event):
        self.drag_start = event.scenePos()
        self.start_pos = self.pos()
        event.accept()

    def mouseMoveEvent(self, event):
        delta = event.scenePos() - self.drag_start
        if self.is_horizontal:
            new_y = self.start_pos.y() + delta.y()
            new_y = max(0, min(new_y, self.canvas.rows * self.canvas.cell_size))
            self.setPos(0, new_y)
        else:
            new_x = self.start_pos.x() + delta.x()
            new_x = max(0, min(new_x, self.canvas.cols * self.canvas.cell_size))
            self.setPos(new_x, 0)
        self.scene().update()

class TransformHandle(QGraphicsEllipseItem):
    HANDLE_SIZE = 12
    TYPE_ROTATE = 1
    TYPE_SCALE = 2
    def __init__(self, parent, handle_type, pos_offset, cursor_type):
        super().__init__(-self.HANDLE_SIZE/2, -self.HANDLE_SIZE/2, self.HANDLE_SIZE, self.HANDLE_SIZE, parent)
        self.parent_pixmap = parent
        self.handle_type = handle_type
        self.setBrush(QBrush(QColor("white")))
        self.setPen(QPen(QColor("red"), 2))
        self.setCursor(QCursor(cursor_type))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations, True)
        p_rect = parent.boundingRect()
        self.setPos(p_rect.x() + p_rect.width() * pos_offset.x(), p_rect.y() + p_rect.height() * pos_offset.y())
    def mousePressEvent(self, event): event.accept() 
    def mouseMoveEvent(self, event):
        if not self.parent_pixmap.is_locked: self.parent_pixmap.on_handle_move(self, event.scenePos())

class TransformablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap, main_window):
        super().__init__(pixmap)
        self.main_window = main_window
        self.setAcceptHoverEvents(True)
        self.is_selected = False
        self.is_locked = False 
        self.setTransformOriginPoint(self.boundingRect().center())
        self.handles = [
            TransformHandle(self, TransformHandle.TYPE_ROTATE, QPointF(0.5, -0.1), Qt.CursorShape.PointingHandCursor),
            TransformHandle(self, TransformHandle.TYPE_SCALE, QPointF(1.0, 1.0), Qt.CursorShape.SizeFDiagCursor)
        ]
        self.set_handles_visible(False)
        self.set_locked(False) 

    def set_locked(self, locked):
        self.is_locked = locked
        self.set_handles_visible(not locked)
        self.setZValue(-1 if locked else 1)  
        self.update_transform_ui()
        if self.scene(): self.scene().update()

    def set_handles_visible(self, visible):
        for h in self.handles: h.setVisible(visible)

    def mousePressEvent(self, event):
        if self.is_locked: return 
        if event.button() == Qt.MouseButton.LeftButton:
            self.set_handles_visible(True)
            self.is_selected = True
            self.drag_start_pos = event.scenePos()
            self.item_start_pos = self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_locked: return
        if event.buttons() == Qt.MouseButton.LeftButton and self.is_selected:
            self.setPos(self.item_start_pos + (event.scenePos() - self.drag_start_pos))
            if self.scene(): self.scene().update()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.is_selected and not self.is_locked:
            painter.setPen(QPen(QColor("red"), 2, Qt.PenStyle.DashLine))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect().adjusted(1, 1, -1, -1))

    def on_handle_move(self, handle, scene_pos):
        if self.is_locked: return
        center = self.mapToScene(self.transformOriginPoint())
        if handle.handle_type == TransformHandle.TYPE_SCALE:
            base_dist = math.hypot(self.boundingRect().width()/2, self.boundingRect().height()/2)
            current_dist = math.hypot(scene_pos.x() - center.x(), scene_pos.y() - center.y())
            self.setScale(max(0.1, current_dist / base_dist))
        elif handle.handle_type == TransformHandle.TYPE_ROTATE:
            self.setRotation(math.degrees(math.atan2(scene_pos.y() - center.y(), scene_pos.x() - center.x())) + 90)
        self.update_transform_ui()
        if self.scene(): self.scene().update()

    def update_transform_ui(self):
        if self.main_window and self.isVisible():
            self.main_window.slider_op.setValue(int(self.opacity() * 100))
            if getattr(self.main_window, "language", "uk") == "en":
                self.main_window.lbl_ref_info.setText(f"Angle: {int(self.rotation())}°, Scale: {int(self.scale() * 100)}%")
            else:
                self.main_window.lbl_ref_info.setText(f"Кут: {int(self.rotation())}°, Масштаб: {int(self.scale() * 100)}%")

class Cell(QGraphicsRectItem):
    def __init__(self, x, y, size, row, col, main_canvas):
        super().__init__(x, y, size, size)
        self.main_canvas = main_canvas
        self.row = row
        self.col = col
        self.default_color = QColor(255, 255, 255, 0) 
        self.current_color = self.default_color
        self.setBrush(QBrush(self.current_color))
        self.base_x = x
        self.base_y = y
        self.is_selected = False
        self.update_pen()

    def update_pen(self):
        if self.is_selected: self.setPen(QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine))
        elif self.main_canvas.hide_grid: self.setPen(QPen(Qt.PenStyle.NoPen))
        else: self.setPen(QPen(QColor(130, 130, 130, 220)))

    def setColor(self, color):
        self.current_color = color
        self.setBrush(QBrush(self.current_color))

    def set_selected(self, state):
        self.is_selected = state
        self.update_pen()

# ==============================================================================
# --- ПОЛОТНО ЗІ СІТКОЮ ---
# ==============================================================================
class GridCanvas(QGraphicsView):
    def __init__(self, rows, cols, cell_size, main_window):
        super().__init__()
        self.main_window = main_window
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.space_pressed = False
        self.pan_active = False
        self.pan_last_pos = None
        
        self.bg_color = "#FFFFFF"
        self.scene.setBackgroundBrush(QColor(self.bg_color))
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.cells = {} 
        self.row_shifts = {}
        self.hide_grid = False
        self.grid_mode = "regular"
        self.product_shape = "rectangle"
        self.active_mask = None
        self.layers = self.default_layers()
        self.active_layer_index = 1
        
        self.current_draw_color = QColor(Qt.GlobalColor.black)
        self.current_tool = "pencil"
        
        self.sym_h = False
        self.sym_v = False
        self.sym_axis_v = None
        self.sym_axis_h = None

        self.undo_stack = []
        self.redo_stack = []
        self.selection_start = None
        self.clipboard = []
        
        self.preview_shape = None
        self.ref_image_item = None
        
        self.line_start = None
        self.preview_line_items = []

        self.init_grid()
        self._push_undo()

    @staticmethod
    def default_layers():
        return [
            {"name": "Фон", "visible": True, "locked": False, "colors": {}},
            {"name": "Орнамент", "visible": True, "locked": False, "colors": {}},
            {"name": "Контур", "visible": True, "locked": False, "colors": {}},
            {"name": "Підказка / ескіз", "visible": True, "locked": False, "colors": {}},
        ]

    def active_layer(self):
        if not self.layers:
            self.layers = self.default_layers()
        self.active_layer_index = max(0, min(self.active_layer_index, len(self.layers) - 1))
        return self.layers[self.active_layer_index]

    def composite_color(self, row, col):
        for layer in reversed(self.layers):
            if layer["visible"] and (row, col) in layer["colors"]:
                return QColor(layer["colors"][(row, col)])
        return QColor(255, 255, 255, 0)

    def refresh_cell(self, row, col):
        cell = self.cells.get((row, col))
        if cell:
            cell.setColor(self.composite_color(row, col))

    def refresh_all_cells(self):
        for row, col in self.cells:
            self.refresh_cell(row, col)
        self.scene.update()
        if hasattr(self.main_window, "canvas") and hasattr(self.main_window, "update_calculator"):
            self.main_window.update_calculator()

    def set_cell_color(self, row, col, color):
        if (row, col) not in self.cells or (self.active_mask is not None and (row, col) not in self.active_mask):
            return
        layer = self.active_layer()
        if layer["locked"]:
            return
        color = QColor(color)
        if color.alpha() == 0:
            layer["colors"].pop((row, col), None)
        else:
            layer["colors"][(row, col)] = color.name()
        self.refresh_cell(row, col)

    def add_layer(self, name=None):
        self.layers.append({"name": name or f"Шар {len(self.layers) + 1}", "visible": True, "locked": False, "colors": {}})
        self.active_layer_index = len(self.layers) - 1

    def duplicate_active_layer(self):
        layer = self.active_layer()
        clone = copy.deepcopy(layer); clone["name"] = f"{layer['name']} — копія"; clone["locked"] = False
        self.layers.insert(self.active_layer_index + 1, clone)
        self.active_layer_index += 1
        self.refresh_all_cells()

    def remove_active_layer(self):
        if len(self.layers) <= 1:
            return False
        self.layers.pop(self.active_layer_index)
        self.active_layer_index = min(self.active_layer_index, len(self.layers) - 1)
        self.refresh_all_cells()
        return True

    def set_grid_mode(self, mode):
        self.grid_mode = mode
        if mode == "custom":
            for row in range(self.rows): self.update_row_positions(row)
            return
        for row in range(self.rows):
            self.row_shifts[row] = mode in ("peyote_even", "peyote_odd", "brick") and row % 2 == 1
            self.update_row_positions(row)

    def set_product_shape(self, shape):
        self.product_shape = shape
        mask = set()
        cy, cx = (self.rows - 1) / 2, (self.cols - 1) / 2
        for r in range(self.rows):
            for c in range(self.cols):
                keep = True
                if shape == "triangle":
                    half = ((r + 1) / self.rows) * self.cols / 2
                    keep = abs(c - cx) <= half
                elif shape == "diamond":
                    keep = abs((r - cy) / max(1, cy + .5)) + abs((c - cx) / max(1, cx + .5)) <= 1
                elif shape == "circle":
                    keep = ((r - cy) / max(1, cy + .5)) ** 2 + ((c - cx) / max(1, cx + .5)) ** 2 <= 1
                elif shape == "earrings_pair":
                    local_c = c if c < self.cols / 2 else self.cols - 1 - c
                    pair_cx = (self.cols / 2 - 1) / 2
                    half = ((r + 1) / self.rows) * max(1, self.cols / 4)
                    keep = abs(local_c - pair_cx) <= half
                elif shape == "pendant":
                    keep = abs((r - cy) / max(1, cy + .5)) + abs((c - cx) / max(1, cx + .5)) <= 1
                if keep: mask.add((r, c))
        self.active_mask = None if shape == "rectangle" else mask
        for pos, cell in self.cells.items():
            cell.setVisible(self.active_mask is None or pos in self.active_mask)
        self.scene.update()

    def get_symmetric_cells(self, r, c):
        cells = [(r, c)]
        mc, mr = -1, -1
        if self.sym_h: 
            mc = int((2 * self.sym_axis_v.x() - (c + 0.5) * self.cell_size) / self.cell_size)
            cells.append((r, mc))
        if self.sym_v: 
            mr = int((2 * self.sym_axis_h.y() - (r + 0.5) * self.cell_size) / self.cell_size)
            cells.append((mr, c))
        if self.sym_h and self.sym_v:
            cells.append((mr, mc))
        return cells

    def color_cell_with_symmetry(self, r, c, color_to_apply):
        for tr, tc in self.get_symmetric_cells(r, c):
            if (tr, tc) in self.cells:
                self.set_cell_color(tr, tc, color_to_apply)

    def update_sym_lines(self):
        if self.sym_axis_v and self.sym_axis_h:
            self.sym_axis_v.setLine(0, 0, 0, self.rows * self.cell_size)
            self.sym_axis_h.setLine(0, 0, self.cols * self.cell_size, 0)

    def set_grid_hidden(self, hidden):
        self.hide_grid = hidden
        for cell in self.cells.values(): cell.update_pen()
        self.scene.update()

    def set_bg_color(self, hex_color):
        self.bg_color = hex_color
        self.scene.setBackgroundBrush(QColor(self.bg_color))

    def init_grid(self):
        # Визначаємо центр екрану АБО беремо старі координати
        old_v_x = self.sym_axis_v.x() if self.sym_axis_v else (self.cols * self.cell_size) / 2
        old_h_y = self.sym_axis_h.y() if self.sym_axis_h else (self.rows * self.cell_size) / 2

        if self.ref_image_item and self.ref_image_item.scene() is self.scene:
            self.scene.removeItem(self.ref_image_item)
        self.scene.clear() 
        self.cells.clear()
        
        self.sym_axis_v = SymLine(is_horizontal=False, canvas=self)
        self.sym_axis_h = SymLine(is_horizontal=True, canvas=self)
        self.scene.addItem(self.sym_axis_v)
        self.scene.addItem(self.sym_axis_h)
        
        # Ставимо лінії туди, де вони були (або по центру при першому запуску)
        self.sym_axis_v.setPos(old_v_x, 0)
        self.sym_axis_h.setPos(0, old_h_y)
        
        self.sym_axis_v.setVisible(self.sym_h)
        self.sym_axis_h.setVisible(self.sym_v)
        
        if self.ref_image_item: 
            self.scene.addItem(self.ref_image_item)
            
        for row in range(self.rows):
            if row not in self.row_shifts:
                self.row_shifts[row] = False
            for col in range(self.cols):
                cell = Cell(col * self.cell_size, row * self.cell_size, self.cell_size, row, col, self)
                self.scene.addItem(cell)
                self.cells[(row, col)] = cell
        for row in range(self.rows):
            self.update_row_positions(row)
        self.refresh_all_cells()
        self.set_product_shape(self.product_shape)
        self.update_sym_lines()

    def resize_grid(self, new_rows, new_cols):
        self._push_undo()
        old_state = self.get_current_state()
        self.rows = new_rows
        self.cols = new_cols
        self.init_grid()
        self.apply_state(old_state)
        self.main_window.update_calculator()

    def update_row_positions(self, row):
        is_shifted = self.row_shifts.get(row, False)
        for col in range(self.cols):
            cell = self.cells.get((row, col))
            if cell: 
                cell.setRect((col * self.cell_size) + (self.cell_size / 2 if is_shifted else 0), cell.base_y, self.cell_size, self.cell_size)

    def is_drawing_allowed(self):
        return not (self.ref_image_item and not self.ref_image_item.is_locked)

    def get_cell_at_pos(self, scene_pos):
        row = int(scene_pos.y() // self.cell_size)
        col = int((scene_pos.x() - (self.cell_size / 2 if self.row_shifts.get(row, False) else 0)) // self.cell_size)
        if 0 <= row < self.rows and 0 <= col < self.cols: return self.cells.get((row, col))
        return None

    def wheelEvent(self, event):
        z = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        self.scale(z, z)
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                self.space_pressed = True; self.viewport().setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept(); return
        elif event.matches(QKeySequence.StandardKey.Copy): self.copy_selection()
        elif event.matches(QKeySequence.StandardKey.Paste): self.paste_selection()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            if not event.isAutoRepeat():
                self.space_pressed = False
                if not self.pan_active: self.viewport().unsetCursor()
            event.accept(); return
        super().keyReleaseEvent(event)

    def focusOutEvent(self, event):
        self.space_pressed = False; self.pan_active = False; self.pan_last_pos = None; self.viewport().unsetCursor()
        super().focusOutEvent(event)

    def apply_tool(self, item):
        if not isinstance(item, Cell) or not self.is_drawing_allowed(): return 
        if self.active_layer()["locked"] and self.current_tool not in ("eyedropper", "select"):
            return
        if self.current_tool == "shift_row":
            self._push_undo()
            self.row_shifts[item.row] = not self.row_shifts.get(item.row, False)
            self.update_row_positions(item.row)
            return
        if self.current_tool in ["select", "line", "shape"]: return
        if self.current_tool == "fill":
            self.flood_fill(item.row, item.col)
            self.main_window.update_calculator()
            return
        if self.current_tool == "eyedropper":
            if item.current_color.alpha() != 0:
                self.main_window.set_drawing_color(QColor(item.current_color))
            self.main_window.change_tool("pencil")
            return

        c_apply = self.current_draw_color if self.current_tool == "pencil" else item.default_color
        brush_size = self.main_window.spin_brush.value() if self.current_tool in ("pencil", "eraser") else 1
        radius = brush_size - 1
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                if dr * dr + dc * dc <= radius * radius + radius:
                    self.color_cell_with_symmetry(item.row + dr, item.col + dc, c_apply)
        self.main_window.update_calculator()

    def flood_fill(self, row, col):
        if (row, col) not in self.cells:
            return
        target = self.composite_color(row, col)
        replacement = QColor(self.current_draw_color)
        if target.rgba() == replacement.rgba():
            return
        pending = [(row, col)]; visited = set()
        while pending:
            r, c = pending.pop()
            if (r, c) in visited or (r, c) not in self.cells:
                continue
            if self.active_mask is not None and (r, c) not in self.active_mask:
                continue
            current = self.composite_color(r, c)
            if current.rgba() != target.rgba():
                continue
            visited.add((r, c))
            self.set_cell_color(r, c, replacement)
            pending.extend(((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)))

    def get_line_cells(self, r0, c0, r1, c1):
        cells = []
        dx = abs(c1 - c0); dy = abs(r1 - r0)
        sx = 1 if c0 < c1 else -1; sy = 1 if r0 < r1 else -1
        err = dx - dy
        while True:
            cells.append((r0, c0))
            if r0 == r1 and c0 == c1: break
            e2 = 2 * err
            if e2 > -dy: err -= dy; c0 += sx
            if e2 < dx: err += dx; r0 += sy
        return cells

    def mousePressEvent(self, event):
        self.setFocus()
        if event.button() == Qt.MouseButton.MiddleButton or (self.space_pressed and event.button() == Qt.MouseButton.LeftButton):
            self.pan_active = True; self.pan_last_pos = event.position().toPoint(); self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept(); return
        if self.ref_image_item and not self.ref_image_item.is_locked:
            clicked_item = self.itemAt(event.pos())
            if clicked_item != self.ref_image_item and not isinstance(clicked_item, (TransformHandle, SymLine)):
                self.ref_image_item.is_selected = False
                self.ref_image_item.set_handles_visible(False)
                self.scene.update()
            super().mousePressEvent(event); return 

        if event.button() == Qt.MouseButton.LeftButton and self.isInteractive():
            self._push_undo()
            pos = self.mapToScene(event.pos())
            item = self.get_cell_at_pos(pos) 
            
            if self.current_tool == "select":
                self.clear_selection()
                if item: self.selection_start = (item.row, item.col)
            elif self.current_tool == "line" and item:
                self.line_start = (item.row, item.col)
            elif self.current_tool == "shape" and item:
                self.selection_start = pos
                self.preview_shape = QGraphicsPathItem()
                self.preview_shape.setPen(QPen(self.current_draw_color, 2, Qt.PenStyle.DashLine))
                if self.main_window.chk_shape_filled.isChecked():
                    c = QColor(self.current_draw_color); c.setAlpha(100)
                    self.preview_shape.setBrush(QBrush(c))
                self.scene.addItem(self.preview_shape)
            elif self.current_tool == "text" and item:
                self.main_window.add_text_to_grid(item.row, item.col)
            elif self.current_tool not in ("fill", "eyedropper"):
                self.apply_tool(item)
            else:
                self.apply_tool(item)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.pan_active and self.pan_last_pos is not None:
            current = event.position().toPoint(); delta = current - self.pan_last_pos; self.pan_last_pos = current
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept(); return
        if self.ref_image_item and not self.ref_image_item.is_locked: super().mouseMoveEvent(event); return
        if event.buttons() == Qt.MouseButton.LeftButton and self.isInteractive():
            pos = self.mapToScene(event.pos())
            item = self.get_cell_at_pos(pos) 

            if self.current_tool == "select" and self.selection_start and item:
                self.update_selection(self.selection_start, (item.row, item.col))
            elif self.current_tool == "shape" and self.preview_shape:
                rect = QRectF(self.selection_start, pos).normalized()
                self.preview_shape.setPath(self.shape_path(rect, self.main_window.combo_shape.currentData()))
            elif self.current_tool == "line" and self.line_start and item:
                for p in self.preview_line_items: self.scene.removeItem(p)
                self.preview_line_items.clear()
                
                cells = self.get_line_cells(self.line_start[0], self.line_start[1], item.row, item.col)
                c_alpha = QColor(self.current_draw_color); c_alpha.setAlpha(150)
                
                for r, c in cells:
                    for tr, tc in self.get_symmetric_cells(r, c):
                        cell = self.cells.get((tr,tc))
                        if cell:
                            rect = QGraphicsRectItem(cell.sceneBoundingRect())
                            rect.setBrush(QBrush(c_alpha)); rect.setPen(QPen(Qt.PenStyle.NoPen))
                            self.scene.addItem(rect); self.preview_line_items.append(rect)
            elif self.current_tool not in ("fill", "eyedropper", "text"): self.apply_tool(item)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.pan_active and event.button() in (Qt.MouseButton.LeftButton, Qt.MouseButton.MiddleButton):
            self.pan_active = False; self.pan_last_pos = None
            self.viewport().setCursor(Qt.CursorShape.OpenHandCursor if self.space_pressed else Qt.CursorShape.ArrowCursor)
            event.accept(); return
        super().mouseReleaseEvent(event) 
        if event.button() == Qt.MouseButton.LeftButton and self.isInteractive() and self.is_drawing_allowed():
            if self.current_tool == "shape" and self.preview_shape:
                self.apply_shape(QRectF(self.selection_start, self.mapToScene(event.pos())).normalized())
                self.scene.removeItem(self.preview_shape); self.preview_shape = None
            elif self.current_tool == "line" and self.line_start:
                for p in self.preview_line_items: self.scene.removeItem(p)
                self.preview_line_items.clear()
                item = self.get_cell_at_pos(self.mapToScene(event.pos()))
                if item:
                    for r, c in self.get_line_cells(self.line_start[0], self.line_start[1], item.row, item.col):
                        self.color_cell_with_symmetry(r, c, self.current_draw_color)
                    self.main_window.update_calculator()
                self.line_start = None

    def shape_path(self, rect, shape):
        path = QPainterPath()
        cx, cy, left, right, top, bottom = rect.center().x(), rect.center().y(), rect.left(), rect.right(), rect.top(), rect.bottom()
        if shape == "rect": path.addRect(rect)
        elif shape == "rounded": path.addRoundedRect(rect, min(rect.width(), rect.height()) * .18, min(rect.width(), rect.height()) * .18)
        elif shape == "ellipse": path.addEllipse(rect)
        elif shape == "triangle":
            path.moveTo(cx, top); path.lineTo(right, bottom); path.lineTo(left, bottom); path.closeSubpath()
        elif shape == "diamond":
            path.moveTo(cx, top); path.lineTo(right, cy); path.lineTo(cx, bottom); path.lineTo(left, cy); path.closeSubpath()
        elif shape == "hexagon":
            path.moveTo(left + rect.width() * .25, top); path.lineTo(right - rect.width() * .25, top)
            path.lineTo(right, cy); path.lineTo(right - rect.width() * .25, bottom)
            path.lineTo(left + rect.width() * .25, bottom); path.lineTo(left, cy); path.closeSubpath()
        elif shape == "star":
            outer, inner = min(rect.width(), rect.height()) / 2, min(rect.width(), rect.height()) / 4.3
            for index in range(10):
                angle = -math.pi / 2 + index * math.pi / 5; radius = outer if index % 2 == 0 else inner
                point = QPointF(cx + math.cos(angle) * radius, cy + math.sin(angle) * radius)
                path.moveTo(point) if index == 0 else path.lineTo(point)
            path.closeSubpath()
        else:  # Хрест
            x1, x2, y1, y2 = left + rect.width() / 3, right - rect.width() / 3, top + rect.height() / 3, bottom - rect.height() / 3
            path.moveTo(x1, top); path.lineTo(x2, top); path.lineTo(x2, y1); path.lineTo(right, y1)
            path.lineTo(right, y2); path.lineTo(x2, y2); path.lineTo(x2, bottom); path.lineTo(x1, bottom)
            path.lineTo(x1, y2); path.lineTo(left, y2); path.lineTo(left, y1); path.lineTo(x1, y1); path.closeSubpath()
        return path

    def apply_shape(self, rect):
        path = self.shape_path(rect, self.main_window.combo_shape.currentData())
        stroker = QPainterPathStroker(); stroker.setWidth(self.cell_size * 1.2)
        stroke_path = stroker.createStroke(path)
        
        affected_cells = []
        for cell in self.cells.values():
            if self.main_window.chk_shape_filled.isChecked():
                if path.intersects(cell.sceneBoundingRect()): affected_cells.append((cell.row, cell.col))
            else:
                if stroke_path.intersects(cell.sceneBoundingRect()): affected_cells.append((cell.row, cell.col))
                
        for r, c in affected_cells:
            self.color_cell_with_symmetry(r, c, self.current_draw_color)
            
        self.main_window.update_calculator()

    def update_selection(self, start, end):
        for cell in self.cells.values():
            if cell.is_selected: cell.set_selected(False)
        r1, c1, r2, c2 = min(start[0], end[0]), min(start[1], end[1]), max(start[0], end[0]), max(start[1], end[1])
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                if (r, c) in self.cells: self.cells[(r, c)].set_selected(True)

    def clear_selection(self):
        for cell in self.cells.values(): cell.set_selected(False)
        self.selection_start = None

    def copy_selection(self):
        self.clipboard = []
        sc = [c for c in self.cells.values() if c.is_selected]
        if not sc: QMessageBox.warning(self.main_window, "Помилка", "Спочатку виділіть область інструментом 'Виділення'!"); return
        mr, mc = min(c.row for c in sc), min(c.col for c in sc)
        for c in sc:
            if c.current_color != c.default_color: self.clipboard.append((c.row - mr, c.col - mc, c.current_color.name()))
        QMessageBox.information(self.main_window, "Копіювання", f"Скопійовано {len(self.clipboard)} клітинок!")

    def paste_selection(self):
        if not self.clipboard: QMessageBox.warning(self.main_window, "Помилка", "Буфер обміну порожній!"); return
        if not self.is_drawing_allowed(): return
        sc = [c for c in self.cells.values() if c.is_selected]
        if not sc: QMessageBox.warning(self.main_window, "Помилка", "Клікніть інструментом 'Виділення' куди вставити!"); return
        self._push_undo()
        sr, sc_col = min(c.row for c in sc), min(c.col for c in sc)
        for dr, dc, col in self.clipboard:
            if (sr + dr, sc_col + dc) in self.cells: self.set_cell_color(sr + dr, sc_col + dc, QColor(col))
        self.main_window.update_calculator()

    def draw_text_pattern(self, start_row, start_col, settings):
        font = QFont(settings["family"]); font.setPixelSize(settings["height"]); font.setBold(settings["bold"])
        metrics = QFontMetrics(font)
        image = QImage(max(1, metrics.horizontalAdvance(settings["text"]) + 4), max(1, metrics.height() + 4), QImage.Format.Format_ARGB32)
        image.fill(QColor(0, 0, 0, 0))
        painter = QPainter(image); painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setFont(font); painter.setPen(Qt.GlobalColor.white)
        painter.drawText(QRectF(2, 2, image.width() - 4, image.height() - 4),
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, settings["text"]); painter.end()
        painted = 0
        for y in range(image.height()):
            for x in range(image.width()):
                if image.pixelColor(x, y).red() < 96: continue
                row, col = start_row + y, start_col + x
                if (row, col) in self.cells:
                    self.set_cell_color(row, col, self.current_draw_color); painted += 1
        self.main_window.update_calculator()
        return painted

    def get_current_state(self):
        return {"layers": copy.deepcopy(self.layers), "active_layer": self.active_layer_index,
                "shifts": self.row_shifts.copy(), "grid_mode": self.grid_mode,
                "product_shape": self.product_shape}
        
    def apply_state(self, state):
        if "layers" in state:
            self.layers = copy.deepcopy(state["layers"])
            self.active_layer_index = state.get("active_layer", 0)
        elif "colors" in state:
            self.layers = self.default_layers()
            self.layers[1]["colors"] = copy.deepcopy(state["colors"])
            self.active_layer_index = 1
        saved_shifts = state.get("shifts", {})
        for row in range(self.rows):
            self.row_shifts[row] = saved_shifts.get(row, False)
            self.update_row_positions(row)
        self.grid_mode = state.get("grid_mode", self.grid_mode)
        self.product_shape = state.get("product_shape", self.product_shape)
        self.set_product_shape(self.product_shape)
        self.refresh_all_cells()
        if hasattr(self.main_window, "refresh_layers_ui"):
            self.main_window.refresh_layers_ui()

    def _push_undo(self):
        self.undo_stack.append(self.get_current_state())
        if len(self.undo_stack) > 30: self.undo_stack.pop(0)
        self.redo_stack.clear()
        
    def do_undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.get_current_state())
            self.apply_state(self.undo_stack.pop()); self.main_window.update_calculator()
            
    def do_redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.get_current_state())
            self.apply_state(self.redo_stack.pop()); self.main_window.update_calculator()

    def clear_grid(self):
        if not self.is_drawing_allowed(): return
        self._push_undo()
        for layer in self.layers:
            if not layer["locked"]:
                layer["colors"].clear()
        self.set_grid_mode(self.grid_mode)
        self.refresh_all_cells()

    def transform_selection(self, mode):
        selected = [cell for cell in self.cells.values() if cell.is_selected]
        if not selected or self.active_layer()["locked"]:
            QMessageBox.information(self.main_window, "Виділення", "Спочатку виділіть фрагмент на незаблокованому шарі.")
            return
        self._push_undo()
        r0, r1 = min(c.row for c in selected), max(c.row for c in selected)
        c0, c1 = min(c.col for c in selected), max(c.col for c in selected)
        layer = self.active_layer()
        source = {(r, c): layer["colors"].get((r, c)) for r in range(r0, r1 + 1) for c in range(c0, c1 + 1)}
        for pos in source: layer["colors"].pop(pos, None)
        for (r, c), color in source.items():
            if not color: continue
            if mode == "mirror_h": nr, nc = r, c1 - (c - c0)
            elif mode == "mirror_v": nr, nc = r1 - (r - r0), c
            else:
                nr, nc = r0 + (c - c0), c0 + (r1 - r)
            if (nr, nc) in self.cells: layer["colors"][(nr, nc)] = color
        self.refresh_all_cells()

# ==============================================================================
# --- ГОЛОВНЕ ВІКНО ---
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор Силянок — Studio 8")
        self.setMinimumSize(1100, 700)
        self.resize(1500, 900)
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))

        self.settings = QSettings("SashaDev", "SelankaEditor")
        self.language = self.settings.value("language", "uk")
        if self.language not in UI_TEXT: self.language = "uk"
        self.current_print_settings = None
        self.current_file = None
        self.project_title = "Нова силянка" if self.language == "uk" else "New beadwork"
        self.project_author = self.settings.value("author", "")
        self.product_type = "loom"
        self.materials = {}
        self.calc_colors = []
        self.dark_theme = self.settings.value("dark_theme", False, type=bool)

        self.canvas = GridCanvas(rows=50, cols=70, cell_size=15, main_window=self)
        self._build_toolbar()

        central = QWidget(); self.setCentralWidget(central)
        root = QHBoxLayout(central); root.setContentsMargins(10, 10, 10, 10); root.setSpacing(10)
        root.addWidget(self._build_tools_panel())

        center = QVBoxLayout(); center.setSpacing(6)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        center.addWidget(self.canvas)
        self.help_label = QLabel(self.tx("help"))
        self.help_label.setObjectName("mutedLabel"); center.addWidget(self.help_label)
        root.addLayout(center, 1)
        root.addWidget(self._build_right_tabs())

        self.change_tool("pencil")
        self.refresh_layers_ui()
        self.setup_shortcuts()
        self.apply_theme()
        self.apply_language()
        self.statusBar().showMessage(self.tx("ready"))

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave_project)
        self.autosave_timer.start(120_000)

    def tx(self, key):
        return UI_TEXT.get(self.language, UI_TEXT["uk"]).get(key, UI_TEXT["uk"].get(key, key))

    def _build_toolbar(self):
        self.main_toolbar = QToolBar("Main toolbar", self)
        self.main_toolbar.setMovable(False); self.main_toolbar.setIconSize(QSize(28, 28)); self.main_toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.main_toolbar)
        actions = [
            ("new", self.new_project, "Ctrl+N", "new"), ("open", self.load_project, "Ctrl+O", "open"),
            ("recent", self.open_last_project, "Ctrl+Alt+O", "recent"),
            ("save", self.save_project, "Ctrl+S", "save"), ("undo", self.canvas.do_undo, "Ctrl+Z", "undo"),
            ("redo", self.canvas.do_redo, "Ctrl+Y", "redo"), ("pdf", self.export_pdf, "Ctrl+Shift+S", "pdf"),
        ]
        self.toolbar_actions = {}
        for key, slot, shortcut, icon_name in actions:
            action = QAction(make_icon(icon_name), self.tx(key), self); action.setShortcut(QKeySequence(shortcut)); action.triggered.connect(slot)
            action.setToolTip(f"{self.tx(key)} ({shortcut})"); self.main_toolbar.addAction(action); self.toolbar_actions[key] = action
        self.clear_button = QPushButton(); self.clear_button.setProperty("iconOnly", True); self.clear_button.setFixedSize(42, 42); self.clear_button.setIconSize(QSize(28, 28)); self.clear_button.setIcon(make_icon("clear", "#ef4444"))
        self.clear_button.clicked.connect(self.confirm_clear_canvas); self.main_toolbar.addWidget(self.clear_button)
        self.main_toolbar.addSeparator(); self.zoom_label = QLabel(self.tx("zoom")); self.main_toolbar.addWidget(self.zoom_label)
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal); self.zoom_slider.setRange(25, 300); self.zoom_slider.setValue(100); self.zoom_slider.setFixedWidth(130)
        self.zoom_slider.valueChanged.connect(self.set_zoom); self.main_toolbar.addWidget(self.zoom_slider)
        self.main_toolbar.addSeparator()
        self.theme_action = QAction(make_icon("theme"), self.tx("dark"), self); self.theme_action.setCheckable(True); self.theme_action.setChecked(self.dark_theme); self.theme_action.triggered.connect(self.toggle_theme); self.main_toolbar.addAction(self.theme_action)
        self.full_action = QAction(make_icon("fullscreen"), self.tx("fullscreen"), self); self.full_action.setShortcut(QKeySequence("F11")); self.full_action.triggered.connect(self.toggle_fullscreen); self.main_toolbar.addAction(self.full_action)
        self.main_toolbar.addSeparator()
        self.language_combo = QComboBox(); self.language_combo.setToolTip(self.tx("language")); self.language_combo.addItem("Українська", "uk"); self.language_combo.addItem("English", "en")
        language_index = self.language_combo.findData(self.language)
        if language_index >= 0: self.language_combo.setCurrentIndex(language_index)
        self.language_combo.currentIndexChanged.connect(self.change_language); self.main_toolbar.addWidget(self.language_combo)

    def _build_tools_panel(self):
        panel = QFrame(); panel.setObjectName("sidePanel"); panel.setFixedWidth(196)
        layout = QVBoxLayout(panel); layout.setContentsMargins(12, 12, 12, 12)
        self.tools_title = QLabel(self.tx("drawing")); self.tools_title.setObjectName("panelTitle"); layout.addWidget(self.tools_title)
        grid = QGridLayout(); grid.setSpacing(6)
        specs = ["pencil", "eraser", "fill", "eyedropper", "line", "shape", "text", "select", "shift_row"]
        self.tool_buttons = {}
        for i, tool_id in enumerate(specs):
            button = QPushButton(); button.setProperty("iconOnly", True); button.setFixedSize(50, 48); button.setIconSize(QSize(30, 30)); button.setIcon(make_icon(tool_id))
            button.setToolTip(self.tx(tool_id)); button.setCheckable(True); button.clicked.connect(lambda checked, t=tool_id: self.change_tool(t))
            self.tool_buttons[tool_id] = button; grid.addWidget(button, i // 3, i % 3)
        layout.addLayout(grid)
        self.btn_pencil = self.tool_buttons["pencil"]; self.btn_line = self.tool_buttons["line"]
        self.btn_eraser = self.tool_buttons["eraser"]; self.btn_shape = self.tool_buttons["shape"]
        self.btn_select = self.tool_buttons["select"]; self.btn_shift = self.tool_buttons["shift_row"]

        brush_row = QHBoxLayout(); self.brush_label = QLabel(self.tx("thickness")); brush_row.addWidget(self.brush_label)
        self.spin_brush = QSpinBox(); self.spin_brush.setRange(1, 8); self.spin_brush.setValue(1); brush_row.addWidget(self.spin_brush)
        layout.addLayout(brush_row)
        self.group_shapes = QGroupBox(self.tx("shape")); shape_layout = QVBoxLayout(self.group_shapes)
        self.combo_shape = QComboBox()
        for label, value in (("Прямокутник", "rect"), ("Заокруглений прямокутник", "rounded"),
                             ("Коло / овал", "ellipse"), ("Трикутник", "triangle"), ("Ромб", "diamond"),
                             ("Шестикутник", "hexagon"), ("Зірка", "star"), ("Хрест", "cross")):
            self.combo_shape.addItem(label, value)
        self.chk_shape_filled = QCheckBox("Суцільна заливка"); shape_layout.addWidget(self.combo_shape); shape_layout.addWidget(self.chk_shape_filled); layout.addWidget(self.group_shapes)
        self.sym_group = QGroupBox(self.tx("symmetry")); sym_layout = QVBoxLayout(self.sym_group)
        self.chk_sym_h = QCheckBox(self.tx("horizontal")); self.chk_sym_h.stateChanged.connect(self.toggle_sym_h)
        self.chk_sym_v = QCheckBox(self.tx("vertical")); self.chk_sym_v.stateChanged.connect(self.toggle_sym_v)
        sym_layout.addWidget(self.chk_sym_h); sym_layout.addWidget(self.chk_sym_v); layout.addWidget(self.sym_group)
        self.select_group = QGroupBox(self.tx("selected_fragment")); select_layout = QHBoxLayout(self.select_group)
        self.transform_buttons = {}
        for mode, icon_name in (("mirror_h", "mirror_h"), ("mirror_v", "mirror_v"), ("rotate", "rotate")):
            btn = QPushButton(); btn.setProperty("iconOnly", True); btn.setFixedSize(48, 44); btn.setIconSize(QSize(29, 29)); btn.setIcon(make_icon(icon_name)); btn.setToolTip(self.tx(mode))
            btn.clicked.connect(lambda checked, m=mode: self.canvas.transform_selection(m)); select_layout.addWidget(btn); self.transform_buttons[mode] = btn
        layout.addWidget(self.select_group)
        extra_actions = QHBoxLayout()
        self.btn_bulk_shift = QPushButton(); self.btn_bulk_shift.setProperty("iconOnly", True); self.btn_bulk_shift.setFixedSize(72, 48); self.btn_bulk_shift.setIconSize(QSize(30, 30)); self.btn_bulk_shift.setIcon(make_icon("bulk")); self.btn_bulk_shift.setToolTip(self.tx("bulk_shift")); self.btn_bulk_shift.clicked.connect(self.open_bulk_shift_dialog)
        self.btn_gen_grid = QPushButton(); self.btn_gen_grid.setProperty("iconOnly", True); self.btn_gen_grid.setFixedSize(72, 48); self.btn_gen_grid.setIconSize(QSize(30, 30)); self.btn_gen_grid.setIcon(make_icon("generator")); self.btn_gen_grid.setToolTip(self.tx("generator")); self.btn_gen_grid.clicked.connect(self.open_grid_generator)
        extra_actions.addWidget(self.btn_bulk_shift); extra_actions.addWidget(self.btn_gen_grid); layout.addLayout(extra_actions)
        layout.addStretch()
        return panel

    def _build_right_tabs(self):
        self.property_tabs = QTabWidget(); self.property_tabs.setObjectName("propertyTabs"); self.property_tabs.setFixedWidth(390)
        self.property_tabs.tabBar().setUsesScrollButtons(False); self.property_tabs.tabBar().setExpanding(True)
        self.property_tabs.addTab(self._build_drawing_tab(), self.tx("drawing"))
        self.property_tabs.addTab(self._build_product_tab(), self.tx("product"))
        self.property_tabs.addTab(self._build_colors_tab(), self.tx("colors"))
        self.property_tabs.addTab(self._build_layers_tab(), self.tx("layers"))
        self.property_tabs.addTab(self._build_export_tab(), self.tx("export"))
        return self.property_tabs

    def _scroll_tab(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); body = QWidget(); layout = QVBoxLayout(body); layout.setAlignment(Qt.AlignmentFlag.AlignTop); scroll.setWidget(body)
        return scroll, layout

    def _build_drawing_tab(self):
        scroll, layout = self._scroll_tab()
        self.lbl_current_color = QLabel("Поточний колір"); self.lbl_current_color.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.lbl_current_color)
        self.color_button = QPushButton(self.tx("pick_color")); self.color_button.clicked.connect(self.choose_custom_color); layout.addWidget(self.color_button)
        self.quick_palette_label = QLabel(self.tx("quick_palette")); layout.addWidget(self.quick_palette_label); palette_grid = QGridLayout()
        defaults = ["#111827", "#FFFFFF", "#DC2626", "#16A34A", "#2563EB", "#FACC15", "#EA580C", "#7C3AED", "#6B7280", "#EC4899"]
        self.palette_colors = self.settings.value("palette", defaults)
        if not isinstance(self.palette_colors, list) or len(self.palette_colors) < 10: self.palette_colors = defaults.copy()
        self.palette_buttons = []
        for i in range(10):
            btn = ColorPaletteButton(); btn.setFixedSize(42, 42); btn.setStyleSheet(f"background:{self.palette_colors[i]}; border:2px solid #d1d5db; border-radius:10px")
            btn.clicked.connect(lambda checked, idx=i: self.set_drawing_color(QColor(self.palette_colors[idx])))
            btn.rightClicked.connect(lambda idx=i: self.edit_palette_color(idx)); self.palette_buttons.append(btn); palette_grid.addWidget(btn, i // 5, i % 5)
        layout.addLayout(palette_grid)
        self.bg_button = QPushButton(self.tx("canvas_bg")); self.bg_button.clicked.connect(self.choose_bg_color); layout.addWidget(self.bg_button)
        self.ref_group = QGroupBox(self.tx("sketch")); ref_layout = QVBoxLayout(self.ref_group)
        self.load_ref_button = QPushButton(self.tx("load_image")); self.load_ref_button.clicked.connect(self.load_reference)
        self.fit_ref_button = QPushButton(self.tx("fit_image")); self.fit_ref_button.clicked.connect(self.fit_reference_to_grid)
        self.convert_ref_button = QPushButton(self.tx("convert_image")); self.convert_ref_button.clicked.connect(self.convert_reference_to_pattern)
        self.chk_ref_lock = QCheckBox("Зафіксувати"); self.chk_ref_lock.stateChanged.connect(self.toggle_ref_lock)
        self.lbl_ref_info = QLabel("Ескіз не завантажено"); self.lbl_ref_info.setObjectName("mutedLabel")
        self.slider_op = QSlider(Qt.Orientation.Horizontal); self.slider_op.setRange(10, 100); self.slider_op.setValue(100); self.slider_op.valueChanged.connect(self.update_ref_opacity)
        self.opacity_label = QLabel(self.tx("opacity")); self.clear_ref_button = QPushButton(self.tx("remove_sketch")); self.clear_ref_button.clicked.connect(self.clear_reference)
        for widget in (self.load_ref_button, self.fit_ref_button, self.convert_ref_button, self.chk_ref_lock, self.lbl_ref_info, self.opacity_label, self.slider_op, self.clear_ref_button): ref_layout.addWidget(widget)
        layout.addWidget(self.ref_group)
        return scroll

    def _build_product_tab(self):
        scroll, layout = self._scroll_tab(); form = QFormLayout()
        self.title_edit = QLineEdit(self.project_title); self.title_edit.textChanged.connect(lambda text: setattr(self, "project_title", text))
        self.author_edit = QLineEdit(self.project_author); self.author_edit.textChanged.connect(self.set_author)
        self.product_combo = QComboBox()
        for label, value in NewProjectDialog.PRODUCT_TYPES: self.product_combo.addItem(label, value)
        self.product_combo.currentIndexChanged.connect(self.change_product_type)
        self.grid_mode_combo = QComboBox()
        for label, value in NewProjectDialog.GRID_TYPES: self.grid_mode_combo.addItem(label, value)
        self.grid_mode_combo.currentIndexChanged.connect(lambda: self.canvas.set_grid_mode(self.grid_mode_combo.currentData()))
        self.product_shape_combo = QComboBox()
        for label, value in NewProjectDialog.SHAPES: self.product_shape_combo.addItem(label, value)
        self.product_shape_combo.currentIndexChanged.connect(lambda: self.canvas.set_product_shape(self.product_shape_combo.currentData()))
        self.spin_rows = QSpinBox(); self.spin_rows.setRange(3, 500); self.spin_rows.setValue(50)
        self.spin_cols = QSpinBox(); self.spin_cols.setRange(3, 500); self.spin_cols.setValue(70)
        self.product_form_labels = {key: QLabel(self.tx(key)) for key in ("title", "author", "type", "grid", "form", "rows", "columns")}
        form.addRow(self.product_form_labels["title"], self.title_edit); form.addRow(self.product_form_labels["author"], self.author_edit); form.addRow(self.product_form_labels["type"], self.product_combo)
        form.addRow(self.product_form_labels["grid"], self.grid_mode_combo); form.addRow(self.product_form_labels["form"], self.product_shape_combo); form.addRow(self.product_form_labels["rows"], self.spin_rows); form.addRow(self.product_form_labels["columns"], self.spin_cols)
        layout.addLayout(form)
        self.resize_button = QPushButton(self.tx("resize")); self.resize_button.clicked.connect(lambda: self.canvas.resize_grid(self.spin_rows.value(), self.spin_cols.value())); layout.addWidget(self.resize_button)
        self.chk_hide_grid = QCheckBox("Приховати лінії сітки"); self.chk_hide_grid.stateChanged.connect(lambda state: self.canvas.set_grid_hidden(bool(state))); layout.addWidget(self.chk_hide_grid)
        self.product_clear_button = QPushButton(self.tx("clear")); self.product_clear_button.setObjectName("dangerButton"); self.product_clear_button.clicked.connect(self.confirm_clear_canvas); layout.addWidget(self.product_clear_button)
        return scroll

    def _build_colors_tab(self):
        scroll, layout = self._scroll_tab(); self.stats_container = QWidget(); self.stats_layout = QVBoxLayout(self.stats_container); self.stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.stats_container); self.update_calculator(); return scroll

    def _build_layers_tab(self):
        scroll, layout = self._scroll_tab(); self.layers_list = QListWidget(); self.layers_list.currentRowChanged.connect(self.select_layer); layout.addWidget(self.layers_list)
        buttons = QGridLayout(); self.layer_buttons = {}
        specs = (("add_layer", self.add_layer, "new"), ("duplicate_layer", self.duplicate_layer, "duplicate"),
                 ("rename_layer", self.rename_layer, "pencil"), ("delete_layer", self.delete_layer, "clear"),
                 ("visibility", self.toggle_layer_visibility, "visibility"), ("locking", self.toggle_layer_lock, "lock"))
        for i, (key, slot, icon_name) in enumerate(specs):
            btn = QPushButton(); btn.setProperty("iconOnly", True); btn.setFixedHeight(48); btn.setIconSize(QSize(28, 28)); btn.setIcon(make_icon(icon_name)); btn.setToolTip(self.tx(key)); btn.clicked.connect(slot)
            buttons.addWidget(btn, i // 3, i % 3); self.layer_buttons[key] = btn
        layout.addLayout(buttons); return scroll

    def _build_export_tab(self):
        scroll, layout = self._scroll_tab()
        self.export_info = QLabel(self.tx("export_info")); self.export_info.setWordWrap(True); self.export_info.setObjectName("mutedLabel"); layout.addWidget(self.export_info)
        self.export_buttons = {}
        for key, slot in (("pdf_print", self.export_pdf), ("image_export", self.export_image), ("svg_export", self.export_svg), ("text_export", self.export_text_pattern), ("print_preview", self.print_project)):
            btn = QPushButton(self.tx(key)); btn.clicked.connect(slot); layout.addWidget(btn); self.export_buttons[key] = btn
        return scroll

    def change_language(self):
        language = self.language_combo.currentData()
        if language not in UI_TEXT or language == self.language: return
        self.language = language; self.settings.setValue("language", language); self.apply_language()

    @staticmethod
    def _translate_combo(combo, labels):
        combo.blockSignals(True)
        for index in range(combo.count()):
            value = combo.itemData(index)
            if value in labels: combo.setItemText(index, labels[value])
        combo.blockSignals(False)

    def apply_language(self):
        shortcuts = {"new": "Ctrl+N", "open": "Ctrl+O", "recent": "Ctrl+Alt+O", "save": "Ctrl+S", "undo": "Ctrl+Z", "redo": "Ctrl+Y", "pdf": "Ctrl+Shift+S"}
        for key, action in self.toolbar_actions.items():
            action.setText(self.tx(key)); action.setToolTip(f"{self.tx(key)} ({shortcuts[key]})"); action.setStatusTip(self.tx(key))
        self.clear_button.setToolTip(self.tx("clear")); self.zoom_label.setText(self.tx("zoom"))
        self.theme_action.setText(self.tx("light") if self.dark_theme else self.tx("dark")); self.theme_action.setToolTip(self.theme_action.text())
        self.full_action.setText(self.tx("fullscreen")); self.full_action.setToolTip(f"{self.tx('fullscreen')} (F11)")
        self.language_combo.setToolTip(self.tx("language")); self.tools_title.setText(self.tx("drawing")); self.help_label.setText(self.tx("help"))
        for key, button in self.tool_buttons.items(): button.setToolTip(self.tx(key))
        self.brush_label.setText(self.tx("thickness")); self.group_shapes.setTitle(self.tx("shape")); self.chk_shape_filled.setText(self.tx("filled_shape"))
        self.sym_group.setTitle(self.tx("symmetry")); self.chk_sym_h.setText(self.tx("horizontal")); self.chk_sym_v.setText(self.tx("vertical"))
        self.select_group.setTitle(self.tx("selected_fragment"))
        for key, button in self.transform_buttons.items(): button.setToolTip(self.tx(key))
        self.btn_bulk_shift.setToolTip(self.tx("bulk_shift")); self.btn_gen_grid.setToolTip(self.tx("generator"))
        for index, key in enumerate(("drawing", "product", "colors", "layers", "export")): self.property_tabs.setTabText(index, self.tx(key))
        self.color_button.setText(self.tx("pick_color")); self.quick_palette_label.setText(self.tx("quick_palette")); self.bg_button.setText(self.tx("canvas_bg"))
        self.ref_group.setTitle(self.tx("sketch")); self.load_ref_button.setText(self.tx("load_image")); self.fit_ref_button.setText(self.tx("fit_image")); self.convert_ref_button.setText(self.tx("convert_image"))
        self.chk_ref_lock.setText(self.tx("lock")); self.opacity_label.setText(self.tx("opacity")); self.clear_ref_button.setText(self.tx("remove_sketch"))
        if not self.canvas.ref_image_item: self.lbl_ref_info.setText(self.tx("no_sketch"))
        for key, label in self.product_form_labels.items(): label.setText(self.tx(key))
        self.resize_button.setText(self.tx("resize")); self.chk_hide_grid.setText(self.tx("hide_grid")); self.product_clear_button.setText(self.tx("clear"))
        for key, button in self.layer_buttons.items(): button.setToolTip(self.tx(key))
        self.export_info.setText(self.tx("export_info"))
        for key, button in self.export_buttons.items(): button.setText(self.tx(key))
        shape_labels = {
            "uk": {"rect": "Прямокутник", "rounded": "Заокруглений прямокутник", "ellipse": "Коло / овал", "triangle": "Трикутник", "diamond": "Ромб", "hexagon": "Шестикутник", "star": "Зірка", "cross": "Хрест"},
            "en": {"rect": "Rectangle", "rounded": "Rounded rectangle", "ellipse": "Circle / ellipse", "triangle": "Triangle", "diamond": "Diamond", "hexagon": "Hexagon", "star": "Star", "cross": "Cross"},
        }
        product_labels = {
            "uk": {value: label for label, value in NewProjectDialog.PRODUCT_TYPES},
            "en": {"loom": "Silianka / gerdan", "bracelet": "Loom bracelet", "peyote": "Peyote stitch", "brick": "Brick stitch", "rope": "Beaded rope", "earrings": "Earrings", "pendant": "Pendant", "fringe": "Fringe"},
        }
        grid_labels = {
            "uk": {value: label for label, value in NewProjectDialog.GRID_TYPES},
            "en": {"regular": "Regular", "peyote_even": "Even-count peyote", "peyote_odd": "Odd-count peyote", "brick": "Brick stitch", "custom": "Custom / bulk shift"},
        }
        project_shape_labels = {
            "uk": {value: label for label, value in NewProjectDialog.SHAPES},
            "en": {"rectangle": "Rectangle", "triangle": "Triangle", "diamond": "Diamond", "circle": "Circle / ellipse", "earrings_pair": "Earring pair", "pendant": "Pendant"},
        }
        self._translate_combo(self.combo_shape, shape_labels[self.language]); self._translate_combo(self.product_combo, product_labels[self.language])
        self._translate_combo(self.grid_mode_combo, grid_labels[self.language]); self._translate_combo(self.product_shape_combo, project_shape_labels[self.language])
        layer_names = {
            "uk": ["Фон", "Орнамент", "Контур", "Підказка / ескіз"],
            "en": ["Background", "Pattern", "Outline", "Guide / reference"],
        }
        known_layer_names = layer_names["en" if self.language == "uk" else "uk"]
        for layer in self.canvas.layers:
            if layer["name"] in known_layer_names:
                layer["name"] = layer_names[self.language][known_layer_names.index(layer["name"])]
        self.refresh_layers_ui(); self.update_calculator(); self.update_window_title()

    def apply_theme(self):
        if self.dark_theme:
            colors = {"bg": "#111827", "panel": "#1f2937", "card": "#273449", "text": "#f3f4f6", "muted": "#9ca3af", "border": "#374151", "input": "#111827"}
        else:
            colors = {"bg": "#f5f7fb", "panel": "#ffffff", "card": "#f8faff", "text": "#172033", "muted": "#667085", "border": "#dfe4ee", "input": "#ffffff"}
        self.setStyleSheet(f"""
            QMainWindow, QWidget {{ background: {colors['bg']}; color: {colors['text']}; font-family: 'Segoe UI'; font-size: 10pt; }}
            QFrame#sidePanel, QScrollArea, QScrollArea > QWidget > QWidget, QTabWidget::pane {{ background: {colors['panel']}; border: 1px solid {colors['border']}; border-radius: 14px; }}
            QToolBar {{ background: {colors['panel']}; border: none; border-bottom: 1px solid {colors['border']}; spacing: 5px; padding: 7px; }}
            QToolButton, QPushButton {{ background: {colors['card']}; border: 1px solid {colors['border']}; border-radius: 9px; padding: 7px 10px; }}
            QToolButton {{ min-width: 34px; min-height: 34px; padding: 4px; }}
            QPushButton[iconOnly="true"] {{ padding: 3px; background: {colors['card']}; border: 1px solid {colors['border']}; border-radius: 11px; }}
            QToolButton:hover, QPushButton:hover {{ border-color: #6366f1; background: #eef2ff; color: #312e81; }}
            QPushButton[iconOnly="true"]:hover {{ background: #e0e7ff; border: 2px solid #6366f1; }}
            QPushButton:checked {{ background: #5b5ce2; color: white; border-color: #4f46e5; }}
            QPushButton#dangerButton {{ color: #b42318; }}
            QLabel#panelTitle {{ font-size: 16pt; font-weight: 700; color: #5b5ce2; padding: 4px; }}
            QLabel#mutedLabel {{ color: {colors['muted']}; }}
            QGroupBox {{ border: 1px solid {colors['border']}; border-radius: 10px; margin-top: 10px; padding-top: 8px; font-weight: 600; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
            QLineEdit, QComboBox, QSpinBox, QListWidget {{ background: {colors['input']}; border: 1px solid {colors['border']}; border-radius: 7px; padding: 6px; }}
            QTabBar::tab {{ padding: 8px 5px; min-width: 52px; border-bottom: 2px solid transparent; }}
            QTabBar::tab:selected {{ color: #5b5ce2; border-bottom-color: #5b5ce2; font-weight: 700; }}
            QScrollBar:vertical {{ width: 10px; background: transparent; }} QScrollBar::handle:vertical {{ background: #a5b4fc; border-radius: 5px; min-height: 24px; }}
        """)
        self.set_drawing_color(self.canvas.current_draw_color)

    def toggle_theme(self, checked):
        self.dark_theme = checked; self.settings.setValue("dark_theme", checked); self.apply_theme(); self.apply_language()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def set_zoom(self, value):
        self.canvas.resetTransform(); factor = value / 100.0; self.canvas.scale(factor, factor)

    def set_author(self, text):
        self.project_author = text; self.settings.setValue("author", text)

    def change_product_type(self):
        self.product_type = self.product_combo.currentData()

    def confirm_clear_canvas(self):
        en = self.language == "en"
        if not any(layer["colors"] for layer in self.canvas.layers) and not self.canvas.ref_image_item:
            QMessageBox.information(self, "Clear canvas" if en else "Очистити полотно", "The canvas is already empty." if en else "Полотно вже порожнє."); return
        answer = QMessageBox.question(
            self, "Clear the entire canvas?" if en else "Очистити все полотно?",
            ("All painted beads on every layer, including locked layers, and the loaded reference image will be removed.\n\n"
             "The grid size will remain. Beads can be restored with Ctrl+Z, but the image must be loaded again.") if en else
            ("Буде видалено всі намальовані намистини з усіх шарів, включно із заблокованими, а також завантажене зображення-ескіз.\n\n"
             "Розміри сітки залишаться. Намистини можна повернути через Ctrl+Z, але зображення доведеться завантажити знову."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes: return
        self.canvas._push_undo()
        for layer in self.canvas.layers: layer["colors"].clear()
        if self.canvas.ref_image_item: self.clear_reference()
        self.canvas.refresh_all_cells(); self.statusBar().showMessage("Canvas cleared" if en else "Полотно очищено", 4000)

    def add_text_to_grid(self, row, col):
        if self.canvas.active_layer()["locked"]:
            QMessageBox.warning(self, "Текст", "Поточний шар заблокований. Розблокуйте його або виберіть інший шар."); return
        dialog = TextPatternDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        count = self.canvas.draw_text_pattern(row, col, dialog.values())
        if count:
            self.statusBar().showMessage(f"Текст додано: {count} зафарбованих клітинок", 5000)
        else:
            QMessageBox.warning(self, "Текст", "Текст не помістився у вибраній частині сітки.")

    def new_project(self):
        dialog = NewProjectDialog(self)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        data = dialog.values(); self.current_file = None; self.project_title = data["title"]; self.product_type = data["product_type"]
        self.canvas.rows = data["rows"]; self.canvas.cols = data["cols"]; self.canvas.layers = self.canvas.default_layers(); self.canvas.active_layer_index = 1
        self.canvas.row_shifts = {}; self.canvas.grid_mode = data["grid_mode"]; self.canvas.product_shape = data["shape"]; self.canvas.ref_image_item = None; self.canvas.init_grid(); self.canvas.set_grid_mode(data["grid_mode"]); self.canvas.set_product_shape(data["shape"])
        self.title_edit.setText(self.project_title); self.spin_rows.setValue(data["rows"]); self.spin_cols.setValue(data["cols"])
        for combo, value in ((self.product_combo, data["product_type"]), (self.grid_mode_combo, data["grid_mode"]), (self.product_shape_combo, data["shape"])):
            index = combo.findData(value)
            if index >= 0: combo.setCurrentIndex(index)
        self.canvas.undo_stack.clear(); self.canvas.redo_stack.clear(); self.canvas._push_undo(); self.refresh_layers_ui(); self.update_calculator(); self.update_window_title()

    def update_window_title(self):
        suffix = f" — {os.path.basename(self.current_file)}" if self.current_file else ""
        self.setWindowTitle(f"{self.tx('app')} — {self.project_title}{suffix}")

    def refresh_layers_ui(self):
        if not hasattr(self, "layers_list"): return
        self.layers_list.blockSignals(True); self.layers_list.clear()
        for layer in reversed(self.canvas.layers):
            visibility = self.tx("visible") if layer["visible"] else self.tx("hidden")
            lock = f" · {self.tx('locked')}" if layer["locked"] else ""
            item = QListWidgetItem(f"{visibility} — {layer['name']}{lock}")
            item.setToolTip("Select a layer, then use the icon buttons below" if self.language == "en" else "Виберіть шар, а потім скористайтеся кнопками нижче")
            self.layers_list.addItem(item)
        self.layers_list.setCurrentRow(len(self.canvas.layers) - 1 - self.canvas.active_layer_index)
        self.layers_list.blockSignals(False)

    def select_layer(self, row):
        if row >= 0: self.canvas.active_layer_index = len(self.canvas.layers) - 1 - row

    def add_layer(self):
        name, ok = QInputDialog.getText(self, "Новий шар", "Назва шару:", text=f"Шар {len(self.canvas.layers) + 1}")
        if ok and name.strip(): self.canvas._push_undo(); self.canvas.add_layer(name.strip()); self.refresh_layers_ui()

    def duplicate_layer(self):
        self.canvas._push_undo(); self.canvas.duplicate_active_layer(); self.refresh_layers_ui()

    def rename_layer(self):
        layer = self.canvas.active_layer(); name, ok = QInputDialog.getText(self, "Назва шару", "Нова назва:", text=layer["name"])
        if ok and name.strip(): layer["name"] = name.strip(); self.refresh_layers_ui()

    def delete_layer(self):
        self.canvas._push_undo()
        if not self.canvas.remove_active_layer(): QMessageBox.information(self, "Шари", "У проєкті має залишитися хоча б один шар.")
        self.refresh_layers_ui()

    def toggle_layer_visibility(self):
        layer = self.canvas.active_layer(); layer["visible"] = not layer["visible"]; self.canvas.refresh_all_cells(); self.refresh_layers_ui()

    def toggle_layer_lock(self):
        layer = self.canvas.active_layer(); layer["locked"] = not layer["locked"]; self.refresh_layers_ui()

    def toggle_sym_h(self, state):
        self.canvas.sym_h = bool(state)
        self.canvas.sym_axis_v.setVisible(bool(state))

    def toggle_sym_v(self, state):
        self.canvas.sym_v = bool(state)
        self.canvas.sym_axis_h.setVisible(bool(state))

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self).activated.connect(self.canvas.do_redo)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.print_project)
        QShortcut(QKeySequence("Ctrl+Alt+S"), self).activated.connect(lambda: self.save_project(save_as=True))
        for i in range(1, 10): QShortcut(QKeySequence(str(i)), self).activated.connect(lambda idx=i: self.quick_select_calc_color(idx))

    def quick_select_calc_color(self, idx):
        if idx - 1 < len(self.calc_colors): self.set_drawing_color(QColor(self.calc_colors[idx - 1]))

    def open_bulk_shift_dialog(self):
        dialog = BulkShiftDialog(self.canvas.rows, self)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        self.apply_bulk_shift(*dialog.values())

    def apply_bulk_shift(self, first_row, skip_rows, reset_existing=True):
        self.canvas._push_undo()
        if reset_existing:
            self.canvas.row_shifts = {row: False for row in range(self.canvas.rows)}
        step = skip_rows + 1
        for row in range(first_row, self.canvas.rows, step): self.canvas.row_shifts[row] = True
        self.canvas.grid_mode = "custom"
        index = self.grid_mode_combo.findData("custom")
        if index >= 0:
            self.grid_mode_combo.blockSignals(True); self.grid_mode_combo.setCurrentIndex(index); self.grid_mode_combo.blockSignals(False)
        for row in range(self.canvas.rows): self.canvas.update_row_positions(row)
        shifted = sum(1 for value in self.canvas.row_shifts.values() if value)
        self.canvas.scene.update(); self.statusBar().showMessage(f"Масовий зсув застосовано: {shifted} рядків", 5000)

    def open_grid_generator(self):
        dlg = GridGeneratorDialog(self.canvas.current_draw_color.name(), self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            s = dlg.get_settings()
            self.canvas._push_undo()
            
            angle = s["angle"]
            rad = math.radians(angle)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            
            for r in range(self.canvas.rows):
                for c in range(self.canvas.cols):
                    # Повертаємо координати клітинки
                    rx = c * cos_a - r * sin_a
                    ry = c * sin_a + r * cos_a
                    
                    draw = False
                    if s["vert"]:
                        val = (rx - s["off_x"]) / s["step_x"]
                        if abs(val - round(val)) <= s["thick"]:
                            draw = True
                    if s["horiz"] and not draw:
                        val = (ry - s["off_y"]) / s["step_y"]
                        if abs(val - round(val)) <= s["thick"]:
                            draw = True
                            
                    if draw:
                        self.canvas.color_cell_with_symmetry(r, c, s["color"])
            self.update_calculator()

    def edit_palette_color(self, idx):
        c = QColorDialog.getColor(QColor(self.palette_colors[idx]), self, "Змінити колір палітри")
        if c.isValid():
            self.palette_colors[idx] = c.name()
            self.settings.setValue("palette", self.palette_colors)
            self.palette_buttons[idx].setStyleSheet(f"background:{c.name()}; border:2px solid #d1d5db; border-radius:10px")
            self.set_drawing_color(c)

    def update_recent_menu(self):
        if not hasattr(self, "menu_recent"):
            return
        self.menu_recent.clear()
        recent = self.settings.value("recent_files", [])
        if not isinstance(recent, list): recent = []
        for path in recent:
            if os.path.exists(path):
                action = QAction(os.path.basename(path), self)
                action.triggered.connect(lambda checked, p=path: self.load_project_file(p))
                self.menu_recent.addAction(action)
        if not self.menu_recent.actions(): self.menu_recent.addAction("Порожньо").setEnabled(False)

    def add_recent_file(self, path):
        recent = self.settings.value("recent_files", [])
        if not isinstance(recent, list): recent = []
        if path in recent: recent.remove(path)
        recent.insert(0, path)
        self.settings.setValue("recent_files", recent[:10])
        self.update_recent_menu()

    def open_last_project(self):
        recent = self.settings.value("recent_files", [])
        if not isinstance(recent, list): recent = []
        existing = next((path for path in recent if os.path.exists(path)), None)
        if existing: self.load_project_file(existing)
        else: QMessageBox.information(self, "Останній проєкт", "Список останніх проєктів порожній.")

    def change_tool(self, tool_id):
        if not self.canvas.is_drawing_allowed(): return
        if self.canvas.current_tool == "select" and tool_id != "select": self.canvas.clear_selection()
        self.canvas.current_tool = tool_id
        for t_id, btn in self.tool_buttons.items():
            btn.setChecked(t_id == tool_id)
        self.group_shapes.setVisible(tool_id == "shape")
        self.canvas.setFocus()

    def set_drawing_color(self, color):
        self.canvas.current_draw_color = color
        self.lbl_current_color.setStyleSheet(f"background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'}; padding: 15px; border-radius: 5px; font-weight: bold;")
        self.lbl_current_color.setText(color.name().upper())
        if self.canvas.is_drawing_allowed() and self.canvas.current_tool in ["eraser", "eyedropper"]: self.change_tool("pencil")
        self.canvas.setFocus()

    def choose_custom_color(self):
        c = QColorDialog.getColor(); self.set_drawing_color(c) if c.isValid() else None; self.canvas.setFocus()
    def choose_bg_color(self):
        c = QColorDialog.getColor(QColor(self.canvas.bg_color)); self.canvas.set_bg_color(c.name()) if c.isValid() else None; self.canvas.setFocus()

    def update_calculator(self):
        stats = {}
        for position, cell in self.canvas.cells.items():
            if self.canvas.active_mask is not None and position not in self.canvas.active_mask: continue
            if cell.current_color != cell.default_color: stats[cell.current_color.name()] = stats.get(cell.current_color.name(), 0) + 1
        
        while self.stats_layout.count():
            child = self.stats_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())
        
        self.stats_layout.addWidget(QLabel(f"<b>{self.tx('bead_calc')}:</b>"))
        if not stats: self.stats_layout.addWidget(QLabel(self.tx("empty"))); self.calc_colors = []; return

        self.calc_colors = []
        for i, (color_hex, count) in enumerate(stats.items()):
            row = QHBoxLayout(); idx = i + 1
            if idx <= 9: self.calc_colors.append(color_hex)
            
            btn_pick = QPushButton(); btn_pick.setFixedSize(20, 20); btn_pick.setStyleSheet(f"background-color: {color_hex}; border: 1px solid gray;")
            btn_pick.clicked.connect(lambda ch, c=color_hex: self.set_drawing_color(QColor(c)))
            
            material = self.materials.get(color_hex, {})
            code = material.get("code", color_hex) if isinstance(material, dict) else color_hex
            stock = int(material.get("stock", 0) or 0) if isinstance(material, dict) else 0
            shortage = stock < math.ceil(count * 1.1)
            if self.language == "en":
                info_text = f"<b>{idx}. {code}</b><br>{count} pcs · with reserve {math.ceil(count * 1.1)}" + ("<br><span style='color:#dc2626'>Insufficient stock</span>" if shortage else "")
            else:
                info_text = f"<b>{idx}. {code}</b><br>{count} шт. · із запасом {math.ceil(count * 1.1)}" + ("<br><span style='color:#dc2626'>Немає в запасі</span>" if shortage else "")
            lbl_info = QLabel(info_text)
            
            btn_meta = QPushButton("⋯"); btn_meta.setFixedSize(30, 30); btn_meta.setToolTip("Код, назва, ціна, запас і нотатка"); btn_meta.clicked.connect(lambda ch, c=color_hex: self.edit_material(c))
            btn_rep = QPushButton("↻"); btn_rep.setFixedSize(30, 30); btn_rep.setToolTip("Замінити колір"); btn_rep.clicked.connect(lambda ch, c=color_hex: self.replace_color_on_canvas(c))
            row.addWidget(btn_pick); row.addWidget(lbl_info); row.addStretch(); row.addWidget(btn_meta); row.addWidget(btn_rep)
            self.stats_layout.addLayout(row)

    def edit_material(self, color_hex):
        dialog = MaterialDialog(color_hex, self.materials.get(color_hex, {}), self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.materials[color_hex] = dialog.values(); self.update_calculator()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            elif child.layout(): self._clear_layout(child.layout())

    def replace_color_on_canvas(self, old_c):
        new_c = QColorDialog.getColor(QColor(old_c), self, "Виберіть новий колір")
        if new_c.isValid():
            self.canvas._push_undo() 
            replaced_count = 0
            for layer in self.canvas.layers:
                for position, color in list(layer["colors"].items()):
                    if QColor(color).name() == old_c:
                        layer["colors"][position] = new_c.name(); replaced_count += 1
            
            if old_c in self.materials and new_c.name() not in self.materials:
                self.materials[new_c.name()] = self.materials.pop(old_c)
            self.canvas.refresh_all_cells()
            
            if replaced_count == 0:
                QMessageBox.information(self, "Інфо", "Жодної зафарбованої клітинки не знайдено.")

    def load_reference(self):
        f, _ = QFileDialog.getOpenFileName(self, "Вибрати зображення", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if f:
            if self.canvas.ref_image_item: self.canvas.scene.removeItem(self.canvas.ref_image_item)
            self.canvas.ref_image_item = TransformablePixmapItem(QPixmap(f), self)
            self.canvas.scene.addItem(self.canvas.ref_image_item)
            self.chk_ref_lock.setChecked(False); self.canvas.ref_image_item.set_locked(False); self.slider_op.setValue(100)
            self.fit_reference_to_grid()
            for btn in self.tool_buttons.values(): btn.setChecked(False)

    def fit_reference_to_grid(self):
        item = self.canvas.ref_image_item
        if not item or item.pixmap().isNull():
            QMessageBox.information(self, "Ескіз", "Спочатку завантажте зображення."); return
        item.setRotation(0); item.setTransform(QTransform())
        width, height = item.boundingRect().width(), item.boundingRect().height()
        grid_width, grid_height = self.canvas.cols * self.canvas.cell_size, self.canvas.rows * self.canvas.cell_size
        scale = min(grid_width / max(1, width), grid_height / max(1, height))
        item.setScale(scale); item.setPos((grid_width - width * scale) / 2, (grid_height - height * scale) / 2)
        item.update_transform_ui(); self.canvas.scene.update()

    def convert_reference_to_pattern(self):
        item = self.canvas.ref_image_item
        if not item or item.pixmap().isNull():
            QMessageBox.warning(self, "Зображення у схему", "Спочатку завантажте зображення у блоці «Ескіз»."); return
        layer = self.canvas.active_layer()
        if layer["locked"]:
            QMessageBox.warning(self, "Зображення у схему", "Поточний шар заблокований. Виберіть або створіть незаблокований шар."); return
        if not any(QColor(value).isValid() for value in self.palette_colors):
            QMessageBox.warning(self, "Зображення у схему", "Швидка палітра не містить придатних кольорів."); return
        image = item.pixmap().toImage(); bounds = item.boundingRect(); samples = []
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            for (row, col), cell in self.canvas.cells.items():
                if self.canvas.active_mask is not None and (row, col) not in self.canvas.active_mask: continue
                local = item.mapFromScene(cell.sceneBoundingRect().center())
                if not bounds.contains(local): continue
                px = min(image.width() - 1, max(0, int(local.x() / max(1, bounds.width()) * image.width())))
                py = min(image.height() - 1, max(0, int(local.y() / max(1, bounds.height()) * image.height())))
                source = image.pixelColor(px, py)
                if source.alpha() < 20: continue
                samples.append((row, col, source.red(), source.green(), source.blue()))
        finally:
            QApplication.restoreOverrideCursor()
        if not samples:
            QMessageBox.warning(self, "Зображення у схему", "Зображення не перетинається із клітинками сітки."); return
        dialog = ImageConversionDialog(samples, self.canvas.rows, self.canvas.cols, self.palette_colors, self)
        if dialog.exec() != QDialog.DialogCode.Accepted: return
        self.canvas._push_undo()
        for position, color in dialog.result.items(): self.canvas.set_cell_color(position[0], position[1], QColor(color))
        self.chk_ref_lock.setChecked(True); self.slider_op.setValue(25)
        self.canvas.refresh_all_cells()
        self.statusBar().showMessage(f"Зображення перетворено: {len(dialog.result)} клітинок, {len(dialog.result_palette)} кольорів", 6000)

    def update_ref_opacity(self):
        if self.canvas.ref_image_item: self.canvas.ref_image_item.setOpacity(self.slider_op.value() / 100.0)
    def toggle_ref_lock(self, state):
        if self.canvas.ref_image_item:
            self.canvas.ref_image_item.set_locked(state)
            if state: self.change_tool("pencil")
            else: 
                for btn in self.tool_buttons.values(): btn.setChecked(False)
    def clear_reference(self):
        if self.canvas.ref_image_item:
            self.canvas.scene.removeItem(self.canvas.ref_image_item); self.canvas.ref_image_item = None
            self.chk_ref_lock.blockSignals(True); self.chk_ref_lock.setChecked(False); self.chk_ref_lock.blockSignals(False)
            self.slider_op.setValue(100); self.lbl_ref_info.setText("Ескіз не завантажено"); self.change_tool("pencil")

    def print_project(self):
        dlg = PrintSettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.current_print_settings = dlg.get_settings()
            p = QPrinter(QPrinter.PrinterMode.HighResolution); p.setPageOrientation(QPageLayout.Orientation.Landscape)
            preview = QPrintPreviewDialog(p, self); preview.paintRequested.connect(self.render_pages); preview.exec()

    def export_pdf(self):
        dlg = PrintSettingsDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.current_print_settings = dlg.get_settings()
            f, _ = QFileDialog.getSaveFileName(self, "Зберегти як PDF", "", "PDF Files (*.pdf)")
            if f:
                if not f.endswith('.pdf'): f += '.pdf'
                p = QPrinter(QPrinter.PrinterMode.HighResolution); p.setOutputFormat(QPrinter.OutputFormat.PdfFormat); p.setOutputFileName(f); p.setPageOrientation(QPageLayout.Orientation.Landscape)
                self.render_pages(p); QMessageBox.information(self, "Успіх", "PDF збережено!")

    def export_image(self):
        path, selected = QFileDialog.getSaveFileName(self, "Експорт зображення", f"{self.project_title}.png", "PNG (*.png);;JPEG (*.jpg *.jpeg)")
        if not path: return
        fmt = "JPG" if "JPEG" in selected else "PNG"
        extension = ".jpg" if fmt == "JPG" else ".png"
        if not path.lower().endswith((".png", ".jpg", ".jpeg")): path += extension
        width, height = self.canvas.cols * self.canvas.cell_size, self.canvas.rows * self.canvas.cell_size
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(QColor("white") if fmt == "JPG" else QColor(self.canvas.bg_color))
        painter = QPainter(image); self._render_clean_scene(painter, QRectF(0, 0, width, height)); painter.end()
        if image.save(path, fmt): self.statusBar().showMessage(f"Зображення збережено: {path}", 5000)
        else: QMessageBox.critical(self, "Експорт", "Не вдалося зберегти зображення.")

    def export_svg(self):
        if QSvgGenerator is None:
            QMessageBox.warning(self, "SVG", "Модуль QtSvg недоступний у цій збірці PyQt6."); return
        path, _ = QFileDialog.getSaveFileName(self, "Експорт SVG", f"{self.project_title}.svg", "SVG (*.svg)")
        if not path: return
        if not path.lower().endswith(".svg"): path += ".svg"
        width, height = self.canvas.cols * self.canvas.cell_size, self.canvas.rows * self.canvas.cell_size
        generator = QSvgGenerator(); generator.setFileName(path); generator.setSize(QSize(width, height)); generator.setViewBox(QRectF(0, 0, width, height)); generator.setTitle(self.project_title); generator.setDescription("Схема бісероплетіння, створена у Редакторі Силянок")
        painter = QPainter(generator); self._render_clean_scene(painter, QRectF(0, 0, width, height)); painter.end()
        self.statusBar().showMessage(f"SVG збережено: {path}", 5000)

    def _render_clean_scene(self, painter, target_rect):
        sym_visibility = (self.canvas.sym_axis_v.isVisible(), self.canvas.sym_axis_h.isVisible())
        self.canvas.sym_axis_v.setVisible(False); self.canvas.sym_axis_h.setVisible(False)
        source = QRectF(0, 0, self.canvas.cols * self.canvas.cell_size, self.canvas.rows * self.canvas.cell_size)
        self.canvas.scene.render(painter, target_rect, source)
        self.canvas.sym_axis_v.setVisible(sym_visibility[0]); self.canvas.sym_axis_h.setVisible(sym_visibility[1])

    def export_text_pattern(self):
        path, _ = QFileDialog.getSaveFileName(self, "Текстова схема", f"{self.project_title}.txt", "Text (*.txt)")
        if not path: return
        if not path.lower().endswith(".txt"): path += ".txt"
        colors = []
        for row in range(self.canvas.rows):
            for col in range(self.canvas.cols):
                color = self.canvas.composite_color(row, col)
                key = color.name() if color.alpha() else None
                if key and key not in colors: colors.append(key)
        symbols = {color: self._color_symbol(i) for i, color in enumerate(colors)}
        lines = [self.project_title, f"Автор: {self.project_author or '—'}", f"Тип: {self.product_combo.currentText()}", ""]
        lines.append("Легенда: " + ", ".join(f"{symbols[c]} = {c}" for c in colors)); lines.append("")
        for row in range(self.canvas.rows):
            sequence = []
            for col in range(self.canvas.cols):
                if self.canvas.active_mask is not None and (row, col) not in self.canvas.active_mask: continue
                color = self.canvas.composite_color(row, col); sequence.append(symbols.get(color.name(), "·") if color.alpha() else "·")
            runs = []
            for symbol in sequence:
                if runs and runs[-1][1] == symbol: runs[-1] = (runs[-1][0] + 1, symbol)
                else: runs.append((1, symbol))
            lines.append(f"Ряд {row + 1}: " + ", ".join(f"{count}×{symbol}" for count, symbol in runs))
        try:
            with open(path, "w", encoding="utf-8") as file: file.write("\n".join(lines))
            self.statusBar().showMessage(f"Текстову схему збережено: {path}", 5000)
        except OSError as error:
            QMessageBox.critical(self, "Експорт", f"Не вдалося записати файл:\n{error}")

    @staticmethod
    def _color_symbol(index):
        result = ""; index += 1
        while index:
            index, remainder = divmod(index - 1, 26); result = chr(65 + remainder) + result
        return result

    def render_pages(self, printer):
        if not self.current_print_settings: return
        settings = self.current_print_settings
        painter = QPainter(printer)
        pr = printer.pageRect(QPrinter.Unit.DevicePixel)
        dx, dy = printer.logicalDpiX(), printer.logicalDpiY()
        
        mx, mt = int(dx * 0.5), int(dy * 1.0)
        mb = int(dy * 2.0) if settings["show_calc"] else int(dy * 0.5)
        aw, ah = pr.width() - mx * 2, pr.height() - mt - mb

        if settings["fit_page"]: pcs = min(aw / self.canvas.cols, ah / self.canvas.rows)
        else: pcs = settings["cell_size_mm"] * (dx / 25.4)
            
        c_pp, r_pp = max(1, int(aw / pcs)), max(1, int(ah / pcs))
        tp_x, tp_y = math.ceil(self.canvas.cols / c_pp), math.ceil(self.canvas.rows / r_pp)
        cp = 1
        
        ft, fs = painter.font(), painter.font(); ft.setPointSize(16); ft.setBold(True); fs.setPointSize(11)
        
        for py in range(tp_y):
            for px in range(tp_x):
                if cp > 1: printer.newPage()
                sc, sr = px * c_pp, py * r_pp
                ec, er = min(sc + c_pp, self.canvas.cols), min(sr + r_pp, self.canvas.rows)
                s_rect = QRectF(sc * self.canvas.cell_size, sr * self.canvas.cell_size, (ec - sc) * self.canvas.cell_size, (er - sr) * self.canvas.cell_size)
                t_rect = QRectF(mx + (aw - (ec - sc) * pcs) / 2, mt, (ec - sc) * pcs, (er - sr) * pcs)
                
                painter.setFont(ft); painter.drawText(mx, int(pr.top() + dy * 0.35), self.project_title or "Схема бісероплетіння")
                painter.setFont(fs); painter.drawText(mx, int(pr.top() + dy * 0.62), f"Автор: {self.project_author or '—'} · {datetime.now().strftime('%d.%m.%Y')} · {self.product_combo.currentText()}")
                painter.drawText(mx, int(pr.top() + dy * 0.82), f"Рядки: {sr+1}–{er} | Стовпці: {sc+1}–{ec}")
                pt = f"Сторінка {cp} з {tp_x * tp_y}"; painter.drawText(int(pr.right() - mx - painter.fontMetrics().horizontalAdvance(pt)), int(pr.top() + dy * 0.7), pt)
                
                sym_visibility = (self.canvas.sym_axis_v.isVisible(), self.canvas.sym_axis_h.isVisible())
                self.canvas.sym_axis_v.setVisible(False); self.canvas.sym_axis_h.setVisible(False)
                self.canvas.scene.render(painter, t_rect, s_rect)
                self.canvas.sym_axis_v.setVisible(sym_visibility[0]); self.canvas.sym_axis_h.setVisible(sym_visibility[1])
                if settings["show_calc"]: self.draw_calc_printer(painter, t_rect.bottom() + int(dy * 0.3), mx, dx, dy, pr)
                cp += 1
        painter.end()

    def draw_calc_printer(self, painter, sy, mx, dx, dy, pr):
        stats = {}
        for position, c in self.canvas.cells.items():
            if self.canvas.active_mask is not None and position not in self.canvas.active_mask: continue
            if c.current_color != c.default_color: stats[c.current_color.name()] = stats.get(c.current_color.name(), 0) + 1
        if not stats: return
        f = painter.font(); f.setPointSize(11); f.setBold(True); painter.setFont(f); painter.drawText(int(mx), int(sy), "Легенда кольорів і список бісеру (+10% запасу):")
        f.setBold(False); painter.setFont(f)
        yo, xo, cw, rs = sy + int(dy * 0.2), int(mx), int(dx * 1.8), int(dy * 0.15)
        for index, (hex_c, count) in enumerate(stats.items()):
            painter.setBrush(QColor(hex_c)); painter.setPen(QPen(Qt.GlobalColor.black, 1))
            code = self.materials.get(hex_c, {}).get("code", hex_c) if isinstance(self.materials.get(hex_c, {}), dict) else hex_c
            reserve = math.ceil(count * 1.10)
            painter.drawRect(xo, int(yo - rs * 0.8), rs, rs); painter.drawText(int(xo + rs + dx * 0.1), int(yo), f"{self._color_symbol(index)} · {code}: {count} шт. / із запасом {reserve}")
            xo += cw
            if xo > pr.right() - mx - cw: xo = int(mx); yo += int(dy * 0.25)

    def project_data(self):
        layers = []
        for layer in self.canvas.layers:
            layers.append({"name": layer["name"], "visible": layer["visible"], "locked": layer["locked"],
                           "cells": [{"r": r, "c": c, "color": color} for (r, c), color in layer["colors"].items()]})
        data = {
            "format": "selanka", "format_version": 2, "app_version": "8.0",
            "metadata": {"title": self.project_title, "author": self.project_author, "modified": datetime.now().isoformat(timespec="seconds")},
            "product": {"type": self.product_type, "shape": self.canvas.product_shape},
            "grid": {"rows": self.canvas.rows, "cols": self.canvas.cols, "cell_size": self.canvas.cell_size,
                     "mode": self.canvas.grid_mode, "background": self.canvas.bg_color,
                     "shifts": {str(key): value for key, value in self.canvas.row_shifts.items()}},
            "layers": layers, "active_layer": self.canvas.active_layer_index,
            "materials": self.materials, "palette": self.palette_colors,
            # Поля першої версії залишені для сумісності зі старими збірками.
            "rows": self.canvas.rows, "cols": self.canvas.cols, "bg_color": self.canvas.bg_color,
            "shifts": self.canvas.row_shifts,
            "cells": [{"r": r, "c": c, "color": cell.current_color.name()} for (r, c), cell in self.canvas.cells.items() if cell.current_color.alpha() != 0],
        }
        if self.canvas.ref_image_item:
            buf = QBuffer(); buf.open(QIODevice.OpenModeFlag.WriteOnly); self.canvas.ref_image_item.pixmap().save(buf, "PNG")
            data["ref"] = {"b64": bytes(buf.data().toBase64()).decode("ascii"), "x": self.canvas.ref_image_item.x(), "y": self.canvas.ref_image_item.y(),
                           "op": self.slider_op.value(), "rot": self.canvas.ref_image_item.rotation(), "sc": self.canvas.ref_image_item.scale(), "lock": self.chk_ref_lock.isChecked()}
        return data

    def _write_project(self, path):
        with open(path, "w", encoding="utf-8") as file:
            json.dump(self.project_data(), file, ensure_ascii=False, indent=2)

    def save_project(self, checked=False, save_as=False):
        path = None if save_as else self.current_file
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Зберегти проєкт", f"{self.project_title}.syl", "Selanka Files (*.syl)")
        if not path: return
        if not path.lower().endswith(".syl"): path += ".syl"
        try:
            self._write_project(path); self.current_file = path; self.add_recent_file(path); self.update_window_title()
            self.statusBar().showMessage("Проєкт збережено", 4000)
        except OSError as error:
            QMessageBox.critical(self, "Збереження", f"Не вдалося зберегти проєкт:\n{error}")

    def autosave_project(self):
        if not self.current_file: return
        try:
            self._write_project(self.current_file + ".autosave")
            self.statusBar().showMessage("Створено автоматичну резервну копію", 2500)
        except OSError:
            self.statusBar().showMessage("Не вдалося створити резервну копію", 3000)

    def load_project(self):
        f, _ = QFileDialog.getOpenFileName(self, "Відкрити проєкт", "", "Selanka Files (*.syl)")
        if f: self.load_project_file(f)

    def load_project_file(self, f):
        """Завантажує проект із файлу, повністю очищаючи попередній стан."""
        try:
            with open(f, 'r', encoding='utf-8') as file:
                d = json.load(file)
            
            # 1. Примусово видаляємо старий ескіз, якщо він був
            self.clear_reference()
            
            # 2. Читаємо як новий версійний формат, так і старі .syl.
            grid = d.get("grid", {})
            metadata = d.get("metadata", {})
            product = d.get("product", {})
            new_rows = grid.get("rows", d.get("rows", 40))
            new_cols = grid.get("cols", d.get("cols", 60))
            self.project_title = metadata.get("title", os.path.splitext(os.path.basename(f))[0])
            self.project_author = metadata.get("author", "")
            self.product_type = product.get("type", "loom")
            self.spin_rows.setValue(new_rows)
            self.spin_cols.setValue(new_cols)
            
            self.canvas.rows = new_rows
            self.canvas.cols = new_cols
            
            # 3. Встановлюємо зсуви ДО створення сітки, щоб клітинки одразу стали правильно
            self.canvas.row_shifts = {int(k): v for k, v in grid.get("shifts", d.get("shifts", {})).items()}
            self.canvas.grid_mode = grid.get("mode", "regular")
            self.canvas.product_shape = product.get("shape", "rectangle")

            if d.get("format_version", 1) >= 2 and d.get("layers"):
                self.canvas.layers = []
                for saved_layer in d["layers"]:
                    colors = {(int(cell["r"]), int(cell["c"])): cell["color"] for cell in saved_layer.get("cells", [])}
                    self.canvas.layers.append({"name": saved_layer.get("name", "Шар"), "visible": saved_layer.get("visible", True),
                                               "locked": saved_layer.get("locked", False), "colors": colors})
                self.canvas.active_layer_index = min(d.get("active_layer", 0), len(self.canvas.layers) - 1)
            else:
                self.canvas.layers = self.canvas.default_layers()
                self.canvas.layers[1]["colors"] = {(int(cell["r"]), int(cell["c"])): cell["color"] for cell in d.get("cells", [])}
                self.canvas.active_layer_index = 1
            
            # 4. ПОВНІСТЮ перестворюємо сітку (це знищить старий малюнок і попередить накладання)
            self.canvas.init_grid()
            
            # 5. Відновлюємо фон та кольори
            self.canvas.set_bg_color(grid.get("background", d.get("bg_color", "#FFFFFF")))
            self.canvas.set_product_shape(self.canvas.product_shape)
            self.canvas.refresh_all_cells()
            
            # 6. Відновлюємо ескіз (референс)
            if "ref" in d:
                try:
                    p = QPixmap()
                    if p.loadFromData(base64.b64decode(d["ref"]["b64"])):
                        self.canvas.ref_image_item = TransformablePixmapItem(p, self)
                        self.canvas.scene.addItem(self.canvas.ref_image_item)
                        self.canvas.ref_image_item.setPos(d["ref"]["x"], d["ref"]["y"])
                        self.canvas.ref_image_item.setRotation(d["ref"].get("rot", 0.0))
                        self.canvas.ref_image_item.setScale(d["ref"].get("sc", 1.0))
                        
                        opacity = d["ref"].get("op", 100)
                        self.slider_op.setValue(opacity)
                        self.canvas.ref_image_item.setOpacity(opacity / 100.0)
                        
                        is_locked = d["ref"].get("lock", False)
                        self.chk_ref_lock.setChecked(is_locked)
                        self.canvas.ref_image_item.set_locked(is_locked)
                except Exception as e:
                    print(f"Помилка ескізу: {e}")

            # 7. Фінальні оновлення
            for r in range(self.canvas.rows):
                self.canvas.update_row_positions(r)
                
            self.materials = d.get("materials", {})
            self.update_calculator()
            if isinstance(d.get("palette"), list) and len(d["palette"]) >= 10:
                self.palette_colors = d["palette"]
                for index, button in enumerate(self.palette_buttons):
                    button.setStyleSheet(f"background:{self.palette_colors[index]}; border:2px solid #d1d5db; border-radius:10px")
            self.title_edit.setText(self.project_title); self.author_edit.setText(self.project_author)
            for combo, value in ((self.product_combo, self.product_type), (self.grid_mode_combo, self.canvas.grid_mode), (self.product_shape_combo, self.canvas.product_shape)):
                index = combo.findData(value)
                if index >= 0:
                    combo.blockSignals(True); combo.setCurrentIndex(index); combo.blockSignals(False)
            self.refresh_layers_ui()
            self.canvas.undo_stack.clear()
            self.canvas.redo_stack.clear()
            self.canvas._push_undo()
            self.current_file = f
            self.update_window_title()
            self.add_recent_file(f)
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити файл:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
