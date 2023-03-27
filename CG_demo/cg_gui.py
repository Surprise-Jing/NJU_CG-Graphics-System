#!/usr/bin/env python
# -*- coding:utf-8 -*-
import math
import sys
import cg_algorithms as alg
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QStyleOptionGraphicsItem,
    QColorDialog,
    QFileDialog,
    QMessageBox,
    QGraphicsRectItem,
    QInputDialog)
from PyQt5.QtGui import QPainter, QMouseEvent, QColor
from PyQt5.QtCore import QRectF, Qt


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.color = QColor(0, 0, 0)
        self.temp_pos = None
        self.temp_center = None
        self.temp_p_list = []
        self.temp_flag = False
        self.temp_bound = None

    def check(self):
        if self.status == 'polygon' or self.status == 'curve':
            if self.temp_item is not None:
                self.item_dict[self.temp_id] = self.temp_item
                self.list_widget.addItem(self.temp_id)
                self.finish_draw()

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = item_id

    def finish_draw(self):
        self.temp_id = self.main_window.get_id()
        self.temp_item = None
        self.status = ''

    def start_select(self):
        self.check()
        self.list_widget.clearSelection()
        self.clear_selection()
        self.updateScene([self.sceneRect()])
        self.status = 'select'
        self.temp_item = None

    def start_translate(self):
        self.check()
        if self.selected_id != '':
            self.status = 'translate'
            self.temp_algorithm = ''
            self.temp_item = self.item_dict[self.selected_id]
        else:
            self.status = ''

    def start_rotate(self):
        self.check()
        if self.selected_id != '' and self.item_dict[self.selected_id].item_type != 'ellipse':
            self.status = 'rotate'
            self.temp_algorithm = ''
            self.temp_item = self.item_dict[self.selected_id]
            self.temp_flag = False
        else:
            self.status = ''

    def start_scale(self):
        self.check()
        if self.selected_id != '':
            self.status = 'scale'
            self.temp_algorithm = ''
            self.temp_item = self.item_dict[self.selected_id]
            self.temp_flag = False
        else:
            self.status = ''

    def start_clip(self, algorithm):
        self.check()
        if self.selected_id != '' and self.item_dict[self.selected_id].item_type == 'line':
            self.status = 'clip'
            self.temp_algorithm = algorithm
            self.temp_item = self.item_dict[self.selected_id]
        else:
            self.status = ''

    def start_delete(self):
        self.check()
        if self.selected_id != '':
            selected = self.selected_id
            self.list_widget.clearSelection()
            self.clear_selection()
            self.scene().removeItem(self.item_dict[selected])
            del self.item_dict[selected]
            self.temp_item = None
            for index in range(self.list_widget.count()):
                if self.list_widget.item(index).text() == selected:
                    item = self.list_widget.item(index)
                    self.list_widget.takeItem(index)
                    del item
                    break
            self.updateScene([self.sceneRect()])
        self.status = ''

    @staticmethod
    def calculate_angle(x1, y1, x2, y2) -> int:
        a1 = math.atan2(y1, x1)
        a1 = int(a1 * 180/ math.pi)
        a2 = math.atan2(y2, x2)
        a2 = int(a2 * 180 / math.pi)
        return a2 - a1

    @staticmethod
    def calculate_times(x1, y1, x2, y2) -> float:
        l1 = math.sqrt(x1*x1 + y1*y1)
        l2 = math.sqrt(x2*x2 + y2*y2)
        if l1 == 0:
            return 0
        return float(l2 / l1)

    def selection(self, x, y) -> str:
        for index, item in self.item_dict.items():
            if item.boundingRect().contains(x, y):
                return index
        return ''

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''

    def selection_changed(self, selected):
        self.check()
        if selected == 'clear':
            self.list_widget.clearSelection()
            self.clear_selection()
            self.main_window.statusBar().showMessage('清除选择')
            self.updateScene([self.sceneRect()])
            return
        if selected not in self.item_dict.keys():
            return
        self.main_window.statusBar().showMessage('图元选择： %s' % selected)
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.item_dict[self.selected_id].update()
        self.selected_id = selected
        self.item_dict[selected].selected = True
        self.item_dict[selected].update()
        self.status = ''
        self.updateScene([self.sceneRect()])

    def mousePressEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm, self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'polygon' or self.status == 'curve':
            if event.button() == Qt.LeftButton:
                if self.temp_item is None:
                    self.temp_item = MyItem(self.temp_id, self.status, [[x, y]], self.temp_algorithm, self.color)
                    self.scene().addItem(self.temp_item)
                else:
                    self.temp_item.p_list.append([x, y])
            else:
                if self.temp_item is not None:
                    self.item_dict[self.temp_id] = self.temp_item
                    self.list_widget.addItem(self.temp_id)
                    self.finish_draw()
        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], '', self.color)
            self.scene().addItem(self.temp_item)
        elif self.status == 'translate':
            self.temp_pos = pos
        elif self.status == 'rotate' or self.status == 'scale':
            if not self.temp_flag:
                self.temp_center = pos
                self.temp_p_list = self.temp_item.p_list
            else:
                self.temp_pos = pos
        elif self.status == 'clip':
            self.temp_center = pos
            self.temp_bound = QGraphicsRectItem(x-1, y-1, 2, 2)
            self.temp_bound.setPen(QColor(0, 255, 0))
            self.scene().addItem(self.temp_bound)
        elif self.status == 'select':
            index = self.selection(x, y)
            if index != '':
                self.selection_changed(index)
                self.list_widget.setCurrentItem(self.list_widget.findItems(index, Qt.MatchContains)[0])
            else:
                self.clear_selection()
        elif self.status == '':
            self.main_window.statusBar().showMessage('')
        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line' or self.status == 'ellipse':
            self.temp_item.p_list[1] = [x, y]
        elif self.status == 'polygon' or self.status == 'curve':
            self.temp_item.p_list[len(self.temp_item.p_list)-1] = [x, y]
        elif self.status == 'translate':
            x0, y0 = int(self.temp_pos.x()), int(self.temp_pos.y())
            self.temp_item.p_list = alg.translate(self.temp_item.p_list, x - x0, y - y0)
            self.temp_pos = pos
        elif self.status == 'rotate':
            if not self.temp_flag:
                self.temp_pos = pos
            else:
                xc, yc = int(self.temp_center.x()), int(self.temp_center.y())
                x0, y0 = int(self.temp_pos.x()), int(self.temp_pos.y())
                r = self.calculate_angle(x0-xc, y0-yc, x-xc, y-yc)
                self.temp_item.p_list = alg.rotate(self.temp_p_list, xc, yc, r)
        elif self.status == 'scale':
            if not self.temp_flag:
                self.temp_pos = pos
            else:
                xc, yc = int(self.temp_center.x()), int(self.temp_center.y())
                x0, y0 = int(self.temp_pos.x()), int(self.temp_pos.y())
                s = self.calculate_times(x0-xc, y0-yc, x-xc, y-yc)
                self.temp_item.p_list = alg.scale(self.temp_p_list, xc, yc, s)
        elif self.status == 'clip':
            x0, y0 = int(self.temp_center.x()), int(self.temp_center.y())
            x_min, y_min = min(x0, x), min(y0, y)
            x_max, y_max = max(x0, x), max(y0, y)
            self.temp_bound.setRect(x_min-1, y_min-1, x_max-x_min+2, y_max-y_min+2)
            self.temp_pos = pos
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        if self.status == 'line' or self.status == 'ellipse':
            self.item_dict[self.temp_id] = self.temp_item
            self.list_widget.addItem(self.temp_id)
            self.finish_draw()
        elif self.status == 'polygon' or self.status == 'curve':
            pass
        elif self.status == 'rotate' or self.status == 'scale':
            if not self.temp_flag:
                self.temp_flag = True
                self.temp_pos = pos
            else:
                self.temp_flag = False
        elif self.status == 'clip':
            self.temp_pos = pos
            x0, y0 = int(self.temp_center.x()), int(self.temp_center.y())
            x1, y1 = int(self.temp_pos.x()), int(self.temp_pos.y())
            self.temp_p_list = alg.clip(self.temp_item.p_list, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1), self.temp_algorithm)
            if self.temp_p_list:
                self.temp_item.p_list = self.temp_p_list
            else:
                selected = self.selected_id
                self.list_widget.clearSelection()
                self.clear_selection()
                self.scene().removeItem(self.item_dict[selected])
                del self.item_dict[selected]
                self.temp_item = None
                for index in range(self.list_widget.count()):
                    if self.list_widget.item(index).text() == selected:
                        item = self.list_widget.item(index)
                        self.list_widget.takeItem(index)
                        del item
                        break
                self.status = ''
            self.scene().removeItem(self.temp_bound)
            self.temp_bound = None
            self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """
    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color: QColor = QColor(0, 0, 0),
                 parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id           # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list        # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)
            painter.setPen(self.color)
            for p in item_pixels:
                painter.drawPoint(*p)
            if self.selected:
                painter.setPen(QColor(255, 0, 0))
                painter.drawRect(self.boundingRect())

    def boundingRect(self) -> QRectF:
        if self.item_type == 'line' or self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'curve':
            x_min, y_min = self.p_list[0]
            x_max, y_max = self.p_list[0]
            for p in self.p_list:
                x_min = min(x_min, p[0])
                y_min = min(y_min, p[1])
                x_max = max(x_max, p[0])
                y_max = max(y_max, p[1])
            w = x_max - x_min
            h = y_max - y_min
            return QRectF(x_min - 1, y_min - 1, w + 2, h + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """
    def __init__(self):
        super().__init__()
        self.item_cnt = 0
        self.filename = ''

        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)

        # 使用QGraphicsView作为画布
        self.length = 600
        self.width = 600
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.length, self.width)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.length, self.width)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget
        self.list_widget.addItem('clear')

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_act = file_menu.addAction('设置画笔')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        select_act = edit_menu.addAction('选择')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        clip_menu = edit_menu.addMenu('裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        delete_act = edit_menu.addAction('删除')

        # 连接信号和槽函数
        set_pen_act.triggered.connect(self.set_pen_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        reset_canvas_act.setShortcut('Ctrl+R')
        save_canvas_act.triggered.connect(self.save_canvas_action)
        save_canvas_act.setShortcut('Ctrl+S')
        exit_act.triggered.connect(self.exit_action)

        line_naive_act.triggered.connect(self.line_naive_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)

        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)

        ellipse_act.triggered.connect(self.ellipse_action)

        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)

        select_act.triggered.connect(self.select_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        delete_act.triggered.connect(self.delete_action)
        delete_act.setShortcut('Del')

        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(self.length, self.width)
        self.setWindowTitle('CG Demo')

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def set_pen_action(self):
        self.canvas_widget.check()
        self.statusBar().showMessage('设置画笔颜色')
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas_widget.color = color

    def reset_canvas_action(self):
        self.canvas_widget.check()
        self.statusBar().showMessage('重置画布')
        self.scene.clear()
        self.list_widget.clearSelection()
        self.list_widget.clear()
        self.canvas_widget.clear_selection()
        self.canvas_widget.item_dict.clear()
        self.canvas_widget.status = ''
        self.item_cnt = 0
        self.filename = ''
        l, ok = QInputDialog.getInt(self, 'Input', 'length', 600, 500, 1500)
        if ok:
            self.length = l
        w, ok = QInputDialog.getInt(self, 'Input', 'width', 600, 400, 1200)
        if ok:
            self.width = w
        self.scene.setSceneRect(0, 0, self.length, self.width)
        self.canvas_widget.setFixedSize(self.length, self.width)
        self.list_widget.addItem('clear')

    def save_canvas_action(self):
        self.canvas_widget.check()
        self.statusBar().showMessage('保存画布')
        if self.filename == '':
            self.filename = QFileDialog.getSaveFileName(self, '保存画布', './', 'Image (*.png *.jpg *.bmp)')
        if self.filename[0]:
            pixels = self.canvas_widget.grab(self.canvas_widget.sceneRect().toRect())
            pixels.save(self.filename[0])
            self.setWindowTitle(self.filename[0])
        else:
            self.filename = ''

    def exit_action(self):
        self.canvas_widget.check()
        save = QMessageBox.question(self, 'save', "是否保存当前画布？",
                                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Yes)
        if save == QMessageBox.Yes:
            self.save_canvas_action()
            qApp.quit()
        elif save == QMessageBox.No:
            qApp.quit()

    def line_naive_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('绘制Bezier曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.check()
        if self.item_cnt > 1:
            self.item_cnt -= 1
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('绘制B-spline曲线')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def select_action(self):
        self.canvas_widget.start_select()
        self.statusBar().showMessage('选择图元')

    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移图元')

    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转图元')

    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放图元')

    def clip_cohen_sutherland_action(self):
        self.canvas_widget.start_clip('Cohen-Sutherland')
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪线段')

    def clip_liang_barsky_action(self):
        self.canvas_widget.start_clip('Liang-Barsky')
        self.statusBar().showMessage('Liang-Barsky算法裁剪线段')

    def delete_action(self):
        self.canvas_widget.start_delete()
        self.statusBar().showMessage('删除图元')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
