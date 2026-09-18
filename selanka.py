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
        self.setWindowTitle("Налаштування друку / PDF")
        self.setMinimumWidth(350)
        layout = QVBoxLayout(self)

        group_scale = QGroupBox("Масштаб малюнка")
        scale_layout = QVBoxLayout()
        self.radio_fit = QRadioButton("Вмістити на 1 сторінку (Авто-масштаб)")
        self.radio_fit.setChecked(True)
        self.radio_custom = QRadioButton("Свій розмір (Може розділити на сторінки)")
        
        scale_layout.addWidget(self.radio_fit)
        scale_layout.addWidget(self.radio_custom)
        
        custom_size_layout = QHBoxLayout()
        custom_size_layout.addWidget(QLabel("   Розмір клітинки:"))
        self.spin_scale = QSpinBox()
        self.spin_scale.setRange(2, 50)
        self.spin_scale.setValue(5)
        self.spin_scale.setSuffix(" мм")
        self.spin_scale.setEnabled(False)
        custom_size_layout.addWidget(self.spin_scale)
        custom_size_layout.addStretch()
        scale_layout.addLayout(custom_size_layout)
        group_scale.setLayout(scale_layout)
        self.radio_custom.toggled.connect(self.spin_scale.setEnabled)
        
        self.chk_calc = QCheckBox("Додати калькулятор бісеру під малюнком")
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
        self.setWindowTitle("Новий проєкт")
        self.setMinimumWidth(430)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.title_edit = QLineEdit("Нова силянка")
        self.product_combo = QComboBox()
        self.grid_combo = QComboBox()
        self.shape_combo = QComboBox()
        for label, value in self.PRODUCT_TYPES: self.product_combo.addItem(label, value)
        for label, value in self.GRID_TYPES: self.grid_combo.addItem(label, value)
        for label, value in self.SHAPES: self.shape_combo.addItem(label, value)
        self.rows_spin = QSpinBox(); self.rows_spin.setRange(3, 500); self.rows_spin.setValue(50)
        self.cols_spin = QSpinBox(); self.cols_spin.setRange(3, 500); self.cols_spin.setValue(70)
        form.addRow("Назва:", self.title_edit)
        form.addRow("Тип виробу:", self.product_combo)
        form.addRow("Тип сітки:", self.grid_combo)
        form.addRow("Форма:", self.shape_combo)
        form.addRow("Рядків:", self.rows_spin)
        form.addRow("Стовпців:", self.cols_spin)
        layout.addLayout(form)
        hint = QLabel("Тип сітки можна змінити пізніше у вкладці «Виріб».")
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
            "title": self.title_edit.text().strip() or "Без назви",
            "product_type": self.product_combo.currentData(),
            "grid_mode": self.grid_combo.currentData(),
            "shape": self.shape_combo.currentData(),
            "rows": self.rows_spin.value(),
            "cols": self.cols_spin.value(),
        }

class MaterialDialog(QDialog):
    def __init__(self, color, data=None, parent=None):
        super().__init__(parent); data = data or {}; self.setWindowTitle(f"Матеріал {color}"); self.setMinimumWidth(380)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.code = QLineEdit(data.get("code", color)); self.name = QLineEdit(data.get("name", ""))
        self.price = QDoubleSpinBox(); self.price.setRange(0, 1_000_000); self.price.setDecimals(2); self.price.setSuffix(" грн"); self.price.setValue(float(data.get("price", 0) or 0))
        self.stock = QSpinBox(); self.stock.setRange(0, 10_000_000); self.stock.setSuffix(" шт."); self.stock.setValue(int(data.get("stock", 0) or 0))
        self.note = QLineEdit(data.get("note", ""))
        form.addRow("Код", self.code); form.addRow("Назва", self.name); form.addRow("Ціна", self.price); form.addRow("Є в запасі", self.stock); form.addRow("Нотатка", self.note); layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def values(self):
        return {"code": self.code.text().strip(), "name": self.name.text().strip(), "price": self.price.value(), "stock": self.stock.value(), "note": self.note.text().strip()}

class TextPatternDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Текст у сітку")
        self.setMinimumWidth(390)
        layout = QVBoxLayout(self); form = QFormLayout()
        self.text_edit = QLineEdit(); self.text_edit.setPlaceholderText("Наприклад: УКРАЇНА")
        self.font_combo = QComboBox(); self.font_combo.addItems(["Arial", "Segoe UI", "Consolas", "Times New Roman"])
        self.height_spin = QSpinBox(); self.height_spin.setRange(5, 50); self.height_spin.setValue(11); self.height_spin.setSuffix(" клітинок")
        self.bold_check = QCheckBox("Жирний текст"); self.bold_check.setChecked(True)
        form.addRow("Текст:", self.text_edit); form.addRow("Шрифт:", self.font_combo); form.addRow("Висота:", self.height_spin); form.addRow("", self.bold_check)
        layout.addLayout(form)
        hint = QLabel("Літери будуть перетворені на кольорові клітинки, починаючи з вибраної точки.")
        hint.setWordWrap(True); hint.setObjectName("mutedLabel"); layout.addWidget(hint)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept); buttons.rejected.connect(self.reject); layout.addWidget(buttons)

    def accept(self):
        if not self.text_edit.text():
            QMessageBox.warning(self, "Текст", "Введіть текст."); return
        super().accept()

    def values(self):
        return {"text": self.text_edit.text(), "family": self.font_combo.currentText(),
                "height": self.height_spin.value(), "bold": self.bold_check.isChecked()}

class GridGeneratorDialog(QDialog):
    def __init__(self, current_color, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Генератор сітки / Орнаменту")
        layout = QVBoxLayout(self)

        grid_layout = QGridLayout()
        self.spin_step_x = QSpinBox(); self.spin_step_x.setRange(1, 100); self.spin_step_x.setValue(5)
        self.spin_step_y = QSpinBox(); self.spin_step_y.setRange(1, 100); self.spin_step_y.setValue(5)
        self.spin_off_x = QSpinBox(); self.spin_off_x.setRange(0, 100)
        self.spin_off_y = QSpinBox(); self.spin_off_y.setRange(0, 100)
        
        # ДОДАНО: Кут та товщина
        self.spin_angle = QSpinBox(); self.spin_angle.setRange(-360, 360); self.spin_angle.setValue(0); self.spin_angle.setSuffix(" °")
        self.spin_thick = QDoubleSpinBox(); self.spin_thick.setRange(0.05, 1.0); self.spin_thick.setValue(0.15); self.spin_thick.setSingleStep(0.05)
        
        grid_layout.addWidget(QLabel("Крок по X (клітинок):"), 0, 0); grid_layout.addWidget(self.spin_step_x, 0, 1)
        grid_layout.addWidget(QLabel("Крок по Y (клітинок):"), 1, 0); grid_layout.addWidget(self.spin_step_y, 1, 1)
        grid_layout.addWidget(QLabel("Зсув по X:"), 2, 0); grid_layout.addWidget(self.spin_off_x, 2, 1)
        grid_layout.addWidget(QLabel("Зсув по Y:"), 3, 0); grid_layout.addWidget(self.spin_off_y, 3, 1)
        grid_layout.addWidget(QLabel("Кут нахилу:"), 4, 0); grid_layout.addWidget(self.spin_angle, 4, 1)
        grid_layout.addWidget(QLabel("Товщина ліній:"), 5, 0); grid_layout.addWidget(self.spin_thick, 5, 1)

        self.chk_horiz = QCheckBox("Малювати горизонтальні (січні) лінії")
        self.chk_horiz.setChecked(True)
        self.chk_vert = QCheckBox("Малювати вертикальні (основні) лінії")
        self.chk_vert.setChecked(True)

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Колір ліній:"))
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            self.setInteractive(False)
        elif event.matches(QKeySequence.StandardKey.Copy): self.copy_selection()
        elif event.matches(QKeySequence.StandardKey.Paste): self.paste_selection()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setInteractive(True)
        super().keyReleaseEvent(event)

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
        self.current_print_settings = None
        self.current_file = None
        self.project_title = "Нова силянка"
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
        help_label = QLabel("Пробіл + перетягування — рух · колесо — масштаб · Ctrl+C / Ctrl+V — фрагмент · 1…9 — колір")
        help_label.setObjectName("mutedLabel"); center.addWidget(help_label)
        root.addLayout(center, 1)
        root.addWidget(self._build_right_tabs())

        self.change_tool("pencil")
        self.refresh_layers_ui()
        self.setup_shortcuts()
        self.apply_theme()
        self.statusBar().showMessage("Готово")

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.autosave_project)
        self.autosave_timer.start(120_000)

    def _build_toolbar(self):
        toolbar = QToolBar("Головна панель", self)
        toolbar.setMovable(False); toolbar.setIconSize(QSize(20, 20)); toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        actions = [
            ("＋ Новий", self.new_project, "Ctrl+N"), ("Відкрити", self.load_project, "Ctrl+O"),
            ("Останній", self.open_last_project, "Ctrl+Alt+O"),
            ("Зберегти", self.save_project, "Ctrl+S"), ("Скасувати", self.canvas.do_undo, "Ctrl+Z"),
            ("Повторити", self.canvas.do_redo, "Ctrl+Y"), ("PDF", self.export_pdf, "Ctrl+Shift+S"),
        ]
        for text, slot, shortcut in actions:
            action = QAction(text, self); action.setShortcut(QKeySequence(shortcut)); action.triggered.connect(slot); toolbar.addAction(action)
        clear_button = QPushButton("Очистити полотно"); clear_button.setObjectName("dangerButton"); clear_button.setToolTip("Видалити всі намальовані клітинки з усіх шарів")
        clear_button.clicked.connect(self.confirm_clear_canvas); toolbar.addWidget(clear_button)
        toolbar.addSeparator(); toolbar.addWidget(QLabel("Масштаб"))
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal); self.zoom_slider.setRange(25, 300); self.zoom_slider.setValue(100); self.zoom_slider.setFixedWidth(130)
        self.zoom_slider.valueChanged.connect(self.set_zoom); toolbar.addWidget(self.zoom_slider)
        toolbar.addSeparator()
        self.theme_action = QAction("Темна тема", self); self.theme_action.setCheckable(True); self.theme_action.setChecked(self.dark_theme); self.theme_action.triggered.connect(self.toggle_theme); toolbar.addAction(self.theme_action)
        full_action = QAction("На весь екран", self); full_action.setShortcut(QKeySequence("F11")); full_action.triggered.connect(self.toggle_fullscreen); toolbar.addAction(full_action)

    def _build_tools_panel(self):
        panel = QFrame(); panel.setObjectName("sidePanel"); panel.setFixedWidth(210)
        layout = QVBoxLayout(panel); layout.setContentsMargins(12, 12, 12, 12)
        title = QLabel("Малювання"); title.setObjectName("panelTitle"); layout.addWidget(title)
        grid = QGridLayout(); grid.setSpacing(6)
        specs = [
            ("pencil", "✎ Пензель"), ("eraser", "⌫ Гумка"), ("fill", "▨ Заливка"),
            ("eyedropper", "◉ Піпетка"), ("line", "╱ Лінія"), ("shape", "□ Фігура"),
            ("text", "Текст у сітку"), ("select", "⛶ Виділення"), ("shift_row", "↔ Зсув"),
        ]
        self.tool_buttons = {}
        for i, (tool_id, label) in enumerate(specs):
            button = QPushButton(label); button.setCheckable(True); button.clicked.connect(lambda checked, t=tool_id: self.change_tool(t))
            self.tool_buttons[tool_id] = button; grid.addWidget(button, i // 2, i % 2)
        layout.addLayout(grid)
        self.btn_pencil = self.tool_buttons["pencil"]; self.btn_line = self.tool_buttons["line"]
        self.btn_eraser = self.tool_buttons["eraser"]; self.btn_shape = self.tool_buttons["shape"]
        self.btn_select = self.tool_buttons["select"]; self.btn_shift = self.tool_buttons["shift_row"]

        brush_row = QHBoxLayout(); brush_row.addWidget(QLabel("Товщина"))
        self.spin_brush = QSpinBox(); self.spin_brush.setRange(1, 8); self.spin_brush.setValue(1); brush_row.addWidget(self.spin_brush)
        layout.addLayout(brush_row)
        self.group_shapes = QGroupBox("Фігура"); shape_layout = QVBoxLayout(self.group_shapes)
        self.combo_shape = QComboBox()
        for label, value in (("Прямокутник", "rect"), ("Заокруглений прямокутник", "rounded"),
                             ("Коло / овал", "ellipse"), ("Трикутник", "triangle"), ("Ромб", "diamond"),
                             ("Шестикутник", "hexagon"), ("Зірка", "star"), ("Хрест", "cross")):
            self.combo_shape.addItem(label, value)
        self.chk_shape_filled = QCheckBox("Суцільна заливка"); shape_layout.addWidget(self.combo_shape); shape_layout.addWidget(self.chk_shape_filled); layout.addWidget(self.group_shapes)
        sym = QGroupBox("Симетрія"); sym_layout = QVBoxLayout(sym)
        self.chk_sym_h = QCheckBox("Горизонтальна"); self.chk_sym_h.stateChanged.connect(self.toggle_sym_h)
        self.chk_sym_v = QCheckBox("Вертикальна"); self.chk_sym_v.stateChanged.connect(self.toggle_sym_v)
        sym_layout.addWidget(self.chk_sym_h); sym_layout.addWidget(self.chk_sym_v); layout.addWidget(sym)
        select_group = QGroupBox("Виділений фрагмент"); select_layout = QGridLayout(select_group)
        for i, (label, mode) in enumerate((("Дзеркало ліво/право", "mirror_h"), ("Дзеркало верх/низ", "mirror_v"), ("Повернути 90°", "rotate"))):
            btn = QPushButton(label); btn.clicked.connect(lambda checked, m=mode: self.canvas.transform_selection(m)); select_layout.addWidget(btn, i, 0)
        layout.addWidget(select_group)
        self.btn_gen_grid = QPushButton("Генератор орнаменту"); self.btn_gen_grid.clicked.connect(self.open_grid_generator); layout.addWidget(self.btn_gen_grid)
        layout.addStretch()
        return panel

    def _build_right_tabs(self):
        tabs = QTabWidget(); tabs.setObjectName("propertyTabs"); tabs.setFixedWidth(390)
        tabs.tabBar().setUsesScrollButtons(False); tabs.tabBar().setExpanding(True)
        tabs.addTab(self._build_drawing_tab(), "Малювання")
        tabs.addTab(self._build_product_tab(), "Виріб")
        tabs.addTab(self._build_colors_tab(), "Кольори")
        tabs.addTab(self._build_layers_tab(), "Шари")
        tabs.addTab(self._build_export_tab(), "Експорт")
        return tabs

    def _scroll_tab(self):
        scroll = QScrollArea(); scroll.setWidgetResizable(True); body = QWidget(); layout = QVBoxLayout(body); layout.setAlignment(Qt.AlignmentFlag.AlignTop); scroll.setWidget(body)
        return scroll, layout

    def _build_drawing_tab(self):
        scroll, layout = self._scroll_tab()
        self.lbl_current_color = QLabel("Поточний колір"); self.lbl_current_color.setAlignment(Qt.AlignmentFlag.AlignCenter); layout.addWidget(self.lbl_current_color)
        color_button = QPushButton("Вибрати свій колір"); color_button.clicked.connect(self.choose_custom_color); layout.addWidget(color_button)
        layout.addWidget(QLabel("Швидка палітра")); palette_grid = QGridLayout()
        defaults = ["#111827", "#FFFFFF", "#DC2626", "#16A34A", "#2563EB", "#FACC15", "#EA580C", "#7C3AED", "#6B7280", "#EC4899"]
        self.palette_colors = self.settings.value("palette", defaults)
        if not isinstance(self.palette_colors, list) or len(self.palette_colors) < 10: self.palette_colors = defaults.copy()
        self.palette_buttons = []
        for i in range(10):
            btn = ColorPaletteButton(); btn.setFixedSize(42, 42); btn.setStyleSheet(f"background:{self.palette_colors[i]}; border:2px solid #d1d5db; border-radius:10px")
            btn.clicked.connect(lambda checked, idx=i: self.set_drawing_color(QColor(self.palette_colors[idx])))
            btn.rightClicked.connect(lambda idx=i: self.edit_palette_color(idx)); self.palette_buttons.append(btn); palette_grid.addWidget(btn, i // 5, i % 5)
        layout.addLayout(palette_grid)
        bg = QPushButton("Колір фону полотна"); bg.clicked.connect(self.choose_bg_color); layout.addWidget(bg)
        ref = QGroupBox("Ескіз"); ref_layout = QVBoxLayout(ref)
        load_ref = QPushButton("Завантажити зображення"); load_ref.clicked.connect(self.load_reference)
        fit_ref = QPushButton("Вписати зображення у сітку"); fit_ref.clicked.connect(self.fit_reference_to_grid)
        convert_ref = QPushButton("Перетворити зображення у схему"); convert_ref.setToolTip("Для кожної клітинки вибрати найближчий колір зі швидкої палітри"); convert_ref.clicked.connect(self.convert_reference_to_pattern)
        self.chk_ref_lock = QCheckBox("Зафіксувати"); self.chk_ref_lock.stateChanged.connect(self.toggle_ref_lock)
        self.lbl_ref_info = QLabel("Ескіз не завантажено"); self.lbl_ref_info.setObjectName("mutedLabel")
        self.slider_op = QSlider(Qt.Orientation.Horizontal); self.slider_op.setRange(10, 100); self.slider_op.setValue(100); self.slider_op.valueChanged.connect(self.update_ref_opacity)
        clear_ref = QPushButton("Видалити ескіз"); clear_ref.clicked.connect(self.clear_reference)
        for widget in (load_ref, fit_ref, convert_ref, self.chk_ref_lock, self.lbl_ref_info, QLabel("Прозорість"), self.slider_op, clear_ref): ref_layout.addWidget(widget)
        layout.addWidget(ref)
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
        form.addRow("Назва", self.title_edit); form.addRow("Автор", self.author_edit); form.addRow("Тип", self.product_combo)
        form.addRow("Сітка", self.grid_mode_combo); form.addRow("Форма", self.product_shape_combo); form.addRow("Рядків", self.spin_rows); form.addRow("Стовпців", self.spin_cols)
        layout.addLayout(form)
        resize = QPushButton("Застосувати розмір"); resize.clicked.connect(lambda: self.canvas.resize_grid(self.spin_rows.value(), self.spin_cols.value())); layout.addWidget(resize)
        self.chk_hide_grid = QCheckBox("Приховати лінії сітки"); self.chk_hide_grid.stateChanged.connect(lambda state: self.canvas.set_grid_hidden(bool(state))); layout.addWidget(self.chk_hide_grid)
        clear = QPushButton("Очистити полотно…"); clear.setObjectName("dangerButton"); clear.clicked.connect(self.confirm_clear_canvas); layout.addWidget(clear)
        return scroll

    def _build_colors_tab(self):
        scroll, layout = self._scroll_tab(); self.stats_container = QWidget(); self.stats_layout = QVBoxLayout(self.stats_container); self.stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.stats_container); self.update_calculator(); return scroll

    def _build_layers_tab(self):
        scroll, layout = self._scroll_tab(); self.layers_list = QListWidget(); self.layers_list.currentRowChanged.connect(self.select_layer); layout.addWidget(self.layers_list)
        buttons = QGridLayout()
        for i, (label, slot) in enumerate((("＋ Додати", self.add_layer), ("⧉ Дублювати", self.duplicate_layer), ("✎ Назва", self.rename_layer), ("Видалити", self.delete_layer), ("Видимість", self.toggle_layer_visibility), ("Блокування", self.toggle_layer_lock))):
            btn = QPushButton(label); btn.clicked.connect(slot); buttons.addWidget(btn, i // 2, i % 2)
        layout.addLayout(buttons); return scroll

    def _build_export_tab(self):
        scroll, layout = self._scroll_tab()
        info = QLabel("Експорт містить назву, автора, дату, нумерацію сторінок і легенду кольорів."); info.setWordWrap(True); info.setObjectName("mutedLabel"); layout.addWidget(info)
        for label, slot in (("PDF для друку", self.export_pdf), ("PNG / JPG", self.export_image), ("SVG", self.export_svg), ("Текстова схема", self.export_text_pattern), ("Попередній перегляд друку", self.print_project)):
            btn = QPushButton(label); btn.clicked.connect(slot); layout.addWidget(btn)
        return scroll

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
            QToolButton:hover, QPushButton:hover {{ border-color: #6366f1; background: #eef2ff; color: #312e81; }}
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
        self.dark_theme = checked; self.settings.setValue("dark_theme", checked); self.theme_action.setText("Світла тема" if checked else "Темна тема"); self.apply_theme()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def set_zoom(self, value):
        self.canvas.resetTransform(); factor = value / 100.0; self.canvas.scale(factor, factor)

    def set_author(self, text):
        self.project_author = text; self.settings.setValue("author", text)

    def change_product_type(self):
        self.product_type = self.product_combo.currentData()

    def confirm_clear_canvas(self):
        if not any(layer["colors"] for layer in self.canvas.layers):
            QMessageBox.information(self, "Очистити полотно", "Полотно вже порожнє."); return
        answer = QMessageBox.question(
            self, "Очистити все полотно?",
            "Буде видалено всі намальовані намистини з усіх шарів, включно із заблокованими.\n\n"
            "Фонове зображення та розміри сітки залишаться. Цю дію можна скасувати через Ctrl+Z.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes: return
        self.canvas._push_undo()
        for layer in self.canvas.layers: layer["colors"].clear()
        self.canvas.refresh_all_cells(); self.statusBar().showMessage("Полотно очищено", 4000)

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
        self.setWindowTitle(f"Редактор Силянок — {self.project_title}{suffix}")

    def refresh_layers_ui(self):
        if not hasattr(self, "layers_list"): return
        self.layers_list.blockSignals(True); self.layers_list.clear()
        for layer in reversed(self.canvas.layers):
            visibility = "Видимий" if layer["visible"] else "Прихований"
            lock = " · заблокований" if layer["locked"] else ""
            item = QListWidgetItem(f"{visibility} — {layer['name']}{lock}")
            item.setToolTip("Виберіть шар, а потім скористайтеся підписаними кнопками нижче")
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
        
        self.stats_layout.addWidget(QLabel("<b>Калькулятор бісеру:</b>"))
        if not stats: self.stats_layout.addWidget(QLabel("Поки пусто")); self.calc_colors = []; return

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
            lbl_info = QLabel(f"<b>{idx}. {code}</b><br>{count} шт. · із запасом {math.ceil(count * 1.1)}" + ("<br><span style='color:#dc2626'>Немає в запасі</span>" if shortage else ""))
            
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
        palette = [QColor(value) for value in dict.fromkeys(self.palette_colors) if QColor(value).isValid()]
        if not palette:
            QMessageBox.warning(self, "Зображення у схему", "Швидка палітра не містить придатних кольорів."); return
        answer = QMessageBox.question(
            self, "Перетворити зображення у схему?",
            f"Кожна клітинка в межах зображення отримає найближчий із {len(palette)} кольорів швидкої палітри.\n"
            f"Результат буде записано на шар «{layer['name']}». Поточні клітинки цього шару в зоні зображення буде замінено.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.Yes)
        if answer != QMessageBox.StandardButton.Yes: return
        self.canvas._push_undo(); image = item.pixmap().toImage()
        palette_rgb = [(color.red(), color.green(), color.blue(), color.name()) for color in palette]
        bounds = item.boundingRect(); converted = 0
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
                sr, sg, sb = source.red(), source.green(), source.blue()
                nearest = min(palette_rgb, key=lambda p: 0.30 * (sr - p[0]) ** 2 + 0.59 * (sg - p[1]) ** 2 + 0.11 * (sb - p[2]) ** 2)
                self.canvas.set_cell_color(row, col, QColor(nearest[3])); converted += 1
        finally:
            QApplication.restoreOverrideCursor()
        self.chk_ref_lock.setChecked(True); self.slider_op.setValue(25)
        self.canvas.refresh_all_cells(); self.statusBar().showMessage(f"Зображення перетворено: {converted} клітинок", 6000)

    def update_ref_opacity(self):
        if self.canvas.ref_image_item: self.canvas.ref_image_item.setOpacity(self.slider_op.value() / 100.0)
    def toggle_ref_lock(self, state):
        if self.canvas.ref_image_item:
            self.canvas.ref_image_item.set_locked(state)
            if state: self.change_tool("pencil")
            else: 
                for btn in self.tool_buttons.values(): btn.setChecked(False)
    def clear_reference(self):
        if self.canvas.ref_image_item: self.canvas.scene.removeItem(self.canvas.ref_image_item); self.canvas.ref_image_item = None; self.lbl_ref_info.setText("Видалено"); self.change_tool("pencil")

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
