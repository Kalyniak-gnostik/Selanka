import sys
import json
import base64
import math
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QGraphicsView, QGraphicsScene,
                             QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsPixmapItem,
                             QGraphicsItem, QColorDialog, QLabel, QCheckBox, QFileDialog, 
                             QMessageBox, QScrollArea, QGridLayout, QSpinBox, QGroupBox, 
                             QComboBox, QSlider, QDialog, QRadioButton, QDialogButtonBox, 
                             QMenu, QDoubleSpinBox, QGraphicsLineItem) # <--- ДОДАНО QGraphicsLineItem в кінці
from PyQt6.QtGui import (QColor, QPen, QBrush, QPainter, QImage, QKeySequence, QShortcut, QAction,
                         QPixmap, QPainterPath, QPainterPathStroker, QTransform, QCursor, QPageLayout, QIcon)
from PyQt6.QtCore import Qt, QRectF, QBuffer, QIODevice, QPointF, pyqtSignal, QSettings
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

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
            if (tr, tc) in self.cells and self.cells[(tr, tc)].current_color != color_to_apply:
                self.cells[(tr, tc)].setColor(color_to_apply)

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
        if self.current_tool == "shift_row":
            self._push_undo()
            self.row_shifts[item.row] = not self.row_shifts.get(item.row, False)
            self.update_row_positions(item.row)
            return
        if self.current_tool in ["select", "line"]: return 

        c_apply = self.current_draw_color if self.current_tool in ["pencil", "shape"] else item.default_color
        self.color_cell_with_symmetry(item.row, item.col, c_apply)
        self.main_window.update_calculator()

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
                self.preview_shape = QGraphicsRectItem() if self.main_window.combo_shape.currentData() == "rect" else QGraphicsEllipseItem()
                self.preview_shape.setPen(QPen(self.current_draw_color, 2, Qt.PenStyle.DashLine))
                if self.main_window.chk_shape_filled.isChecked():
                    c = QColor(self.current_draw_color); c.setAlpha(100)
                    self.preview_shape.setBrush(QBrush(c))
                self.scene.addItem(self.preview_shape)
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
                self.preview_shape.setRect(QRectF(self.selection_start, pos).normalized())
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
            else: self.apply_tool(item)
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

    def apply_shape(self, rect):
        path = QPainterPath()
        path.addRect(rect) if self.main_window.combo_shape.currentData() == "rect" else path.addEllipse(rect)
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
            if (sr + dr, sc_col + dc) in self.cells: self.cells[(sr + dr, sc_col + dc)].setColor(QColor(col))
        self.main_window.update_calculator()

    def get_current_state(self):
        return {"colors": {p: c.current_color.name() for p, c in self.cells.items() if c.current_color != c.default_color}, "shifts": self.row_shifts.copy()}
        
    def apply_state(self, state):
        for cell in self.cells.values(): cell.setColor(cell.default_color)
        for pos, color in state.get("colors", {}).items():
            if pos in self.cells: self.cells[pos].setColor(QColor(color))
            
        saved_shifts = state.get("shifts", {})
        for row in range(self.rows):
            self.row_shifts[row] = saved_shifts.get(row, False)
            self.update_row_positions(row)

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
        for cell in self.cells.values(): cell.setColor(cell.default_color)
        self.row_shifts = {row: False for row in range(self.rows)}
        for row in range(self.rows): self.update_row_positions(row)
        self.main_window.update_calculator()

# ==============================================================================
# --- ГОЛОВНЕ ВІКНО ---
# ==============================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Редактор Силянок - PRO 7.0")
        self.setGeometry(50, 50, 1450, 850)
        
        # Завантаження іконки у вікно
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.settings = QSettings("SashaDev", "SelankaEditor")
        self.current_print_settings = None 
        self.calc_colors = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # --- 1. ЛІВА ПАНЕЛЬ ---
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFixedWidth(290)
        left_widget = QWidget()
        left_panel = QVBoxLayout(left_widget)
        
        left_panel.addWidget(QLabel("<b>🛠 Інструменти</b>"))
        self.btn_pencil = QPushButton("✏️ Олівець")
        self.btn_line = QPushButton("📏 Лінія")
        self.btn_eraser = QPushButton("🧹 Гумка")
        self.btn_shape = QPushButton("🔺 Фігури")
        self.btn_select = QPushButton("👆 Виділення")
        self.btn_shift = QPushButton("↔️ Зсув рядка")
        self.btn_gen_grid = QPushButton("🕸️ Додати сітку")

        self.tool_buttons = {"pencil": self.btn_pencil, "line": self.btn_line, "eraser": self.btn_eraser, 
                             "shape": self.btn_shape, "select": self.btn_select, "shift_row": self.btn_shift}

        for t_id, btn in self.tool_buttons.items(): btn.clicked.connect(lambda ch, t=t_id: self.change_tool(t))
        self.btn_gen_grid.clicked.connect(self.open_grid_generator)

        for btn in [self.btn_pencil, self.btn_line, self.btn_eraser, self.btn_shape]: left_panel.addWidget(btn)
        
        self.group_shapes = QGroupBox("Налаштування фігури")
        shape_layout = QVBoxLayout()
        self.combo_shape = QComboBox(); self.combo_shape.addItems(["Квадрат / Прямокутник", "Круг / Овал"])
        self.combo_shape.setItemData(0, "rect"); self.combo_shape.setItemData(1, "ellipse")
        self.chk_shape_filled = QCheckBox("Заливка кольором")
        shape_layout.addWidget(self.combo_shape); shape_layout.addWidget(self.chk_shape_filled)
        self.group_shapes.setLayout(shape_layout)
        left_panel.addWidget(self.group_shapes)
        
        for btn in [self.btn_select, self.btn_shift, self.btn_gen_grid]: left_panel.addWidget(btn)

        sym_group = QGroupBox("Симетрія")
        sym_layout = QVBoxLayout()
        self.chk_sym_h = QCheckBox("По горизонталі ↔️")
        self.chk_sym_h.stateChanged.connect(self.toggle_sym_h)
        self.chk_sym_v = QCheckBox("По вертикалі ↕️")
        self.chk_sym_v.stateChanged.connect(self.toggle_sym_v)
        sym_layout.addWidget(self.chk_sym_h); sym_layout.addWidget(self.chk_sym_v)
        sym_group.setLayout(sym_layout); left_panel.addWidget(sym_group)

        size_group = QGroupBox("Розмір та вигляд")
        size_layout = QGridLayout()
        self.spin_rows = QSpinBox(); self.spin_rows.setRange(10, 500); self.spin_rows.setValue(50)
        self.spin_cols = QSpinBox(); self.spin_cols.setRange(10, 500); self.spin_cols.setValue(70)
        btn_resize = QPushButton("Змінити")
        btn_resize.clicked.connect(lambda: self.canvas.resize_grid(self.spin_rows.value(), self.spin_cols.value()))
        self.chk_hide_grid = QCheckBox("Приховати сітку")
        self.chk_hide_grid.stateChanged.connect(lambda s: self.canvas.set_grid_hidden(bool(s)))
        
        size_layout.addWidget(QLabel("Рядки:"), 0, 0); size_layout.addWidget(self.spin_rows, 0, 1)
        size_layout.addWidget(QLabel("Стовпці:"), 1, 0); size_layout.addWidget(self.spin_cols, 1, 1)
        size_layout.addWidget(btn_resize, 2, 0, 1, 2); size_layout.addWidget(self.chk_hide_grid, 3, 0, 1, 2)
        size_group.setLayout(size_layout); left_panel.addWidget(size_group)

        ref_group = QGroupBox("Ескіз (Фонове зображення)")
        ref_layout = QVBoxLayout()
        btn_load_ref = QPushButton("📂 Завантажити ескіз"); btn_load_ref.clicked.connect(self.load_reference)
        self.chk_ref_lock = QCheckBox("🔒 Зафіксувати"); self.chk_ref_lock.stateChanged.connect(self.toggle_ref_lock)
        self.lbl_ref_info = QLabel("Інфо")
        self.slider_op = QSlider(Qt.Orientation.Horizontal); self.slider_op.setRange(10, 100); self.slider_op.setValue(100); self.slider_op.valueChanged.connect(self.update_ref_opacity)
        btn_clear_ref = QPushButton("❌ Видалити ескіз"); btn_clear_ref.clicked.connect(self.clear_reference)
        for w in [btn_load_ref, self.chk_ref_lock, self.lbl_ref_info, QLabel("Прозорість:"), self.slider_op, btn_clear_ref]: ref_layout.addWidget(w)
        ref_group.setLayout(ref_layout); left_panel.addWidget(ref_group)

        left_panel.addWidget(QLabel("<b>Дії</b>"))
        action_layout_1 = QHBoxLayout()
        btn_copy = QPushButton("📝 Копіювати"); btn_copy.clicked.connect(lambda: self.canvas.copy_selection())
        btn_paste = QPushButton("📋 Вставити"); btn_paste.clicked.connect(lambda: self.canvas.paste_selection())
        action_layout_1.addWidget(btn_copy); action_layout_1.addWidget(btn_paste)
        left_panel.addLayout(action_layout_1)
        left_panel.addStretch(); left_scroll.setWidget(left_widget)

        # --- 2. ЦЕНТР ---
        canvas_layout = QVBoxLayout()
        
        top_action_layout = QHBoxLayout()
        btn_undo = QPushButton("↩️ Undo (Ctrl+Z)"); btn_undo.clicked.connect(lambda: self.canvas.do_undo())
        btn_redo = QPushButton("↪️ Redo"); btn_redo.clicked.connect(lambda: self.canvas.do_redo())
        
        # Кнопка очищення перенесена сюди і відцентрована вправо
        btn_clear = QPushButton("🗑️ Очистити сітку")
        btn_clear.setStyleSheet("background-color: #ff9800; color: white; font-weight: bold;")
        btn_clear.clicked.connect(lambda: self.canvas.clear_grid())
        
        top_action_layout.addWidget(btn_undo); top_action_layout.addWidget(btn_redo)
        top_action_layout.addStretch() # Відсуває кнопку очищення вправо
        top_action_layout.addWidget(btn_clear)
        canvas_layout.addLayout(top_action_layout)
        
        self.canvas = GridCanvas(rows=50, cols=70, cell_size=15, main_window=self)
        canvas_layout.addWidget(self.canvas)

        file_layout = QHBoxLayout()
        btn_save = QPushButton("💾 Зберегти (Ctrl+S)"); btn_save.clicked.connect(self.save_project)
        btn_load = QPushButton("📂 Відкрити проєкт"); btn_load.clicked.connect(self.load_project)
        
        self.btn_recent = QPushButton("🕒 Останні...")
        self.menu_recent = QMenu()
        self.btn_recent.setMenu(self.menu_recent)
        self.update_recent_menu()
        
        btn_print = QPushButton("🖨️ Друк (Ctrl+P)"); btn_print.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;"); btn_print.clicked.connect(self.print_project)
        btn_pdf = QPushButton("📄 PDF (Ctrl+Shift+S)"); btn_pdf.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;"); btn_pdf.clicked.connect(self.export_pdf)
        
        for w in [btn_save, btn_load, self.btn_recent, btn_print, btn_pdf]: file_layout.addWidget(w)
        canvas_layout.addLayout(file_layout)

        help_label = QLabel("<i>Пробіл+ЛКМ=Рухати | Коліщатко=Зум | 1..9=Вибір кольору з калькулятора | ПКМ по палітрі=Змінити</i>")
        help_label.setStyleSheet("color: gray;"); canvas_layout.addWidget(help_label)

        # --- 3. ПРАВА ПАНЕЛЬ ---
        right_panel = QVBoxLayout()
        btn_bg_color = QPushButton("🏞️ Колір фону полотна"); btn_bg_color.clicked.connect(self.choose_bg_color)
        right_panel.addWidget(btn_bg_color); right_panel.addWidget(QLabel(" ")) 
        
        self.lbl_current_color = QLabel("Поточний колір")
        self.lbl_current_color.setStyleSheet("background-color: black; color: white; padding: 15px; border-radius: 5px; font-weight: bold;"); self.lbl_current_color.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.lbl_current_color)

        btn_color_picker = QPushButton("🎨 Свій колір..."); btn_color_picker.clicked.connect(self.choose_custom_color)
        right_panel.addWidget(btn_color_picker)

        right_panel.addWidget(QLabel("<b>Швидка палітра:</b>"))
        palette_grid = QGridLayout()
        default_colors = ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FFA500", "#800080", "#808080", "#FFC0CB"]
        self.palette_colors = self.settings.value("palette", default_colors)
        if not isinstance(self.palette_colors, list) or len(self.palette_colors) < 10: self.palette_colors = default_colors.copy()
        
        self.palette_buttons = []
        for i in range(10):
            btn = ColorPaletteButton()
            btn.setStyleSheet(f"background-color: {self.palette_colors[i]}; border: 1px solid gray; width: 30px; height: 30px;")
            btn.clicked.connect(lambda ch, idx=i: self.set_drawing_color(QColor(self.palette_colors[idx])))
            btn.rightClicked.connect(lambda idx=i: self.edit_palette_color(idx))
            self.palette_buttons.append(btn)
            palette_grid.addWidget(btn, i // 2, i % 2)
        right_panel.addLayout(palette_grid)

        self.stats_container = QWidget()
        self.stats_layout = QVBoxLayout(self.stats_container); self.stats_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.update_calculator() 

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setWidget(self.stats_container)
        right_panel.addWidget(scroll)

        main_layout.addWidget(left_scroll, 1); main_layout.addLayout(canvas_layout, 5); main_layout.addLayout(right_panel, 1)

        self.change_tool("pencil")
        self.setup_shortcuts()

    def toggle_sym_h(self, state):
        self.canvas.sym_h = bool(state)
        self.canvas.sym_axis_v.setVisible(bool(state))

    def toggle_sym_v(self, state):
        self.canvas.sym_v = bool(state)
        self.canvas.sym_axis_h.setVisible(bool(state))

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self.canvas.do_undo)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_project)
        QShortcut(QKeySequence("Ctrl+P"), self).activated.connect(self.print_project)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self).activated.connect(self.export_pdf)
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
            self.palette_buttons[idx].setStyleSheet(f"background-color: {c.name()}; border: 1px solid gray;")
            self.set_drawing_color(c)

    def update_recent_menu(self):
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

    def change_tool(self, tool_id):
        if not self.canvas.is_drawing_allowed(): return
        if self.canvas.current_tool == "select" and tool_id != "select": self.canvas.clear_selection()
        self.canvas.current_tool = tool_id
        for t_id, btn in self.tool_buttons.items():
            btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; border: 2px solid #0D47A1; padding: 5px;" if t_id == tool_id else "padding: 5px;")
        self.canvas.setFocus()

    def set_drawing_color(self, color):
        self.canvas.current_draw_color = color
        self.lbl_current_color.setStyleSheet(f"background-color: {color.name()}; color: {'white' if color.lightness() < 128 else 'black'}; padding: 15px; border-radius: 5px; font-weight: bold;")
        if self.canvas.is_drawing_allowed() and self.canvas.current_tool not in ["shape", "pencil", "line"]: self.change_tool("pencil")
        self.canvas.setFocus()

    def choose_custom_color(self):
        c = QColorDialog.getColor(); self.set_drawing_color(c) if c.isValid() else None; self.canvas.setFocus()
    def choose_bg_color(self):
        c = QColorDialog.getColor(QColor(self.canvas.bg_color)); self.canvas.set_bg_color(c.name()) if c.isValid() else None; self.canvas.setFocus()

    def update_calculator(self):
        stats = {}
        for cell in self.canvas.cells.values():
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
            
            lbl_info = QLabel(f"<b>{idx}.</b> {color_hex}: <b>{count}</b> шт." if idx <= 9 else f"{color_hex}: <b>{count}</b> шт.")
            
            btn_rep = QPushButton("🔄"); btn_rep.setFixedSize(25, 25); btn_rep.clicked.connect(lambda ch, c=color_hex: self.replace_color_on_canvas(c))
            row.addWidget(btn_pick); row.addWidget(lbl_info); row.addStretch(); row.addWidget(btn_rep)
            self.stats_layout.addLayout(row)

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
            for cell in self.canvas.cells.values():
                # ГОЛОВНЕ ВИПРАВЛЕННЯ: перевіряємо, щоб колір збігався І клітинка не була прозорою
                if cell.current_color.name() == old_c and cell.current_color.alpha() != 0:
                    cell.setColor(new_c)
                    replaced_count += 1
            
            self.update_calculator()
            self.canvas.scene.update()
            
            if replaced_count == 0:
                QMessageBox.information(self, "Інфо", "Жодної зафарбованої клітинки не знайдено.")

    def load_reference(self):
        f, _ = QFileDialog.getOpenFileName(self, "Вибрати зображення", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if f:
            if self.canvas.ref_image_item: self.canvas.scene.removeItem(self.canvas.ref_image_item)
            self.canvas.ref_image_item = TransformablePixmapItem(QPixmap(f), self)
            self.canvas.scene.addItem(self.canvas.ref_image_item)
            self.chk_ref_lock.setChecked(False); self.canvas.ref_image_item.set_locked(False); self.slider_op.setValue(100)
            for btn in self.tool_buttons.values(): btn.setStyleSheet("padding: 5px;")

    def update_ref_opacity(self):
        if self.canvas.ref_image_item: self.canvas.ref_image_item.setOpacity(self.slider_op.value() / 100.0)
    def toggle_ref_lock(self, state):
        if self.canvas.ref_image_item:
            self.canvas.ref_image_item.set_locked(state)
            if state: self.change_tool("pencil")
            else: 
                for btn in self.tool_buttons.values(): btn.setStyleSheet("padding: 5px;")
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
                
                painter.setFont(ft); painter.drawText(mx, int(pr.top() + dy * 0.4), "Редактор Силянок PRO")
                painter.setFont(fs); painter.drawText(mx, int(pr.top() + dy * 0.7), f"Рядки: {sr+1}-{er} | Стовпці: {sc+1}-{ec}")
                pt = f"Сторінка {cp} з {tp_x * tp_y}"; painter.drawText(int(pr.right() - mx - painter.fontMetrics().horizontalAdvance(pt)), int(pr.top() + dy * 0.7), pt)
                
                self.canvas.scene.render(painter, t_rect, s_rect)
                if settings["show_calc"]: self.draw_calc_printer(painter, t_rect.bottom() + int(dy * 0.3), mx, dx, dy, pr)
                cp += 1
        painter.end()

    def draw_calc_printer(self, painter, sy, mx, dx, dy, pr):
        stats = {}
        for c in self.canvas.cells.values():
            if c.current_color != c.default_color: stats[c.current_color.name()] = stats.get(c.current_color.name(), 0) + 1
        if not stats: return
        f = painter.font(); f.setPointSize(11); f.setBold(True); painter.setFont(f); painter.drawText(int(mx), int(sy), "Калькулятор бісеру:")
        f.setBold(False); painter.setFont(f)
        yo, xo, cw, rs = sy + int(dy * 0.2), int(mx), int(dx * 1.8), int(dy * 0.15)
        for hex_c, count in stats.items():
            painter.setBrush(QColor(hex_c)); painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawRect(xo, int(yo - rs * 0.8), rs, rs); painter.drawText(int(xo + rs + dx * 0.1), int(yo), f"{hex_c}: {count} шт.")
            xo += cw
            if xo > pr.right() - mx - cw: xo = int(mx); yo += int(dy * 0.25)

    def save_project(self):
        f, _ = QFileDialog.getSaveFileName(self, "Зберегти проєкт", "", "Selanka Files (*.syl)")
        if f:
            if not f.endswith('.syl'): f += '.syl'
            d = {"rows": self.canvas.rows, "cols": self.canvas.cols, "bg_color": self.canvas.bg_color, "shifts": self.canvas.row_shifts,
                 "cells": [{"r": r, "c": c, "color": cell.current_color.name()} for (r, c), cell in self.canvas.cells.items() if cell.current_color != cell.default_color]}
            if self.canvas.ref_image_item:
                buf = QBuffer(); buf.open(QIODevice.OpenModeFlag.WriteOnly); self.canvas.ref_image_item.pixmap().save(buf, "PNG")
                d["ref"] = {"b64": buf.data().toBase64().data().decode('utf-8'), "x": self.canvas.ref_image_item.x(), "y": self.canvas.ref_image_item.y(),
                            "op": self.slider_op.value(), "rot": self.canvas.ref_image_item.rotation(), "sc": self.canvas.ref_image_item.scale(), "lock": self.chk_ref_lock.isChecked()}
            with open(f, 'w') as file: json.dump(d, file)
            self.add_recent_file(f)
            QMessageBox.information(self, "Успіх", "Збережено!")

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
            
            # 2. Отримуємо нові розміри та оновлюємо інтерфейс
            new_rows = d.get("rows", 40)
            new_cols = d.get("cols", 60)
            self.spin_rows.setValue(new_rows)
            self.spin_cols.setValue(new_cols)
            
            self.canvas.rows = new_rows
            self.canvas.cols = new_cols
            
            # 3. Встановлюємо зсуви ДО створення сітки, щоб клітинки одразу стали правильно
            self.canvas.row_shifts = {int(k): v for k, v in d.get("shifts", {}).items()}
            
            # 4. ПОВНІСТЮ перестворюємо сітку (це знищить старий малюнок і попередить накладання)
            self.canvas.init_grid()
            
            # 5. Відновлюємо фон та кольори
            self.canvas.set_bg_color(d.get("bg_color", "#FFFFFF"))
            for c_data in d.get("cells", []):
                r, c = c_data["r"], c_data["c"]
                if (r, c) in self.canvas.cells:
                    self.canvas.cells[(r, c)].setColor(QColor(c_data["color"]))
            
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
                
            self.update_calculator()
            self.canvas.undo_stack.clear()
            self.canvas.redo_stack.clear()
            self.canvas._push_undo()
            self.add_recent_file(f)
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося відкрити файл:\n{str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())