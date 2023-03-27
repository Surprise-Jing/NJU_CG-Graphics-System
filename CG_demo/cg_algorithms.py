#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            if y0 > y1:
                y0, y1 = y1, y0
            for y in range(y0, y1 + 1):
                result.append((x0, y))
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append((x, int(y0 + k * (x - x0))))
    elif algorithm == 'DDA':
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))   # 判断斜率，取绝对值较大者作为单位间隔取样
        if steps == 0:
            result.append((int(x0 + 0.5), int(y0 + 0.5)))
        else:
            delta_x = float(dx/steps)
            delta_y = float(dy/steps)
            # 四舍五入，保证x和y的增量小于等于1，后面int()向下取整
            x = x0 + 0.5
            y = y0 + 0.5
            for i in range(0, int(steps+1)):
                result.append((int(x), int(y)))
                x += delta_x
                y += delta_y
    elif algorithm == 'Bresenham':
        dx = x1 - x0
        dy = y1 - y0
        s1 = 1 if(dx >= 0) else -1
        s2 = 1 if(dy >= 0) else -1
        dx, dy = abs(dx), abs(dy)
        result.append((x0, y0))
        x = x0
        y = y0
        if dx >= dy:
            e = 2 * dy - dx
            deta1 = 2 * dy
            deta2 = (dy-dx) * 2
            while x != x1:
                if e >= 0:   # y方向增量为1
                    x += s1
                    y += s2
                    e += deta2
                else:
                    x += s1
                    e += deta1
                result.append((x, y))
        else:
            e = 2 * dx - dy
            deta1 = 2 * dx
            deta2 = (dx-dy) * 2
            while y != y1:
                if e >= 0:   # x方向增量为1
                    x += s1
                    y += s2
                    e += deta2
                else:
                    y += s2
                    e += deta1
                result.append((x, y))
    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    quarter_result = []
    xc, yc = int((x0 + x1) / 2 + 0.5), int((y0 + y1) / 2 + 0.5)
    rx, ry = int(abs(x0 - x1) / 2), int(abs(y0 - y1) / 2)
    x, y = 0, ry
    p1k = float(ry*ry - rx*rx*ry + rx*rx/4)
    quarter_result.append((x, y))
    while ry*ry*x < rx*rx*y:
        if p1k < 0:
            p1k = p1k + 2*ry*ry*x + 3*ry*ry
        else:
            p1k = p1k + 2*ry*ry*x - 2*rx*rx*y + 2*rx*rx + 3*ry*ry
            y = y - 1
        x = x + 1
        quarter_result.append((x, y))
    p2k = ry*ry*(x+0.5)*(x+0.5) + rx*rx*(y-1)*(y-1) - rx*rx*ry*ry
    while y > 0:
        if p2k > 0:
            p2k = p2k - 2*rx*rx*y + 3*rx*rx
        else:
            p2k = p2k + 2*ry*ry*x - 2*rx*rx*y + 2*ry*ry + 3*rx*rx
            x = x + 1
        y = y - 1
        quarter_result.append((x, y))
    for tempx, tempy in quarter_result:
        result.append((tempx+xc, tempy+yc))
        result.append((-tempx+xc, tempy+yc))
        result.append((tempx+xc, -tempy+yc))
        result.append((-tempx+xc, -tempy+yc))
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    def bezier_getpoint(u, n, p_list):
        while n > 1:
            for i in range(0, n-1):
                x0, y0 = p_list[i]
                x1, y1 = p_list[i+1]
                x = (1-u)*x0 + u*x1
                y = (1-u)*y0 + u*y1
                p_list[i] = [x, y]
            n -= 1
        return p_list[0]

    def bezier(p_list):
        precision = len(p_list)*100
        result = []
        for i in range(precision + 1):
            u = i * 1.0 / precision
            x, y = bezier_getpoint(u, len(p_list), p_list.copy())
            result.append((int(x+0.5), int(y+0.5)))
        return result

    def debook_cox(u, i, k):
        if k == 1:
            if u >= i and u < i+1:
                return 1
            else:
                return 0
        else:
            return (u-i)/(k-1)*debook_cox(u, i, k-1)+(i+k-u)/(k-1)*debook_cox(u, i+1, k-1)

    def b_spline(p_list):
        result = []
        k = 4  # 三次四阶
        n = len(p_list)
        u = k-1
        precision = float(1/1000)
        while u < n:
            x, y = 0, 0
            for i in range(0, n):
                bik = debook_cox(u, i, k)
                x += bik * p_list[i][0]
                y += bik * p_list[i][1]
            result.append((int(x+0.5), int(y+0.5)))
            u += precision
        return result

    if algorithm == 'Bezier':
        return bezier(p_list)
    elif algorithm == 'B-spline':  # 三次（四阶）均匀B样条曲线
        return b_spline(p_list)


def translate(p_list, dx, dy):
    """平移变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for x, y in p_list:
        result.append((x+dx, y+dy))
    return result


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    rad = r * math.pi / 180
    for x0, y0 in p_list:
        result.append((int((x0-x)*math.cos(rad) - (y0-y)*math.sin(rad) + x),
                       int((x0-x)*math.sin(rad) + (y0-y)*math.cos(rad) + y)))
    return result


def scale(p_list, x, y, s):
    """缩放变换

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    result = []
    for x0, y0 in p_list:
        result.append((int(x0*s + x*(1-s)), int(y0*s + y*(1-s))))
    return result


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Cohen-Sutherland':
        while 1:
            code0, code1 = 0, 0   # 1_left, 2_right, 4_down, 8_up
            # 计算code0
            if x0 < x_min:
                code0 += 1
            elif x0 > x_max:
                code0 += 2
            if y0 < y_min:
                code0 += 4
            elif y0 > y_max:
                code0 += 8
            # 计算code1
            if x1 < x_min:
                code1 += 1
            elif x1 > x_max:
                code1 += 2
            if y1 < y_min:
                code1 += 4
            elif y1 > y_max:
                code1 += 8
            if (code0 | code1) == 0:  # inside
                result = [[x0, y0], [x1, y1]]
                break
            elif (code0 & code1) != 0:   # outside
                break
            else:
                if code0 == 0:
                    x0, x1 = x1, x0
                    y0, y1 = y1, y0
                    code0, code1 = code1, code0
                if code0 & 1:
                    y0 = int(y0 + ((x_min-x0)*(y0-y1)/(x0-x1)) + 0.5)
                    x0 = x_min
                if code0 & 2:
                    y0 = int(y0 + ((x_max-x0)*(y0-y1)/(x0-x1)) + 0.5)
                    x0 = x_max
                if code0 & 4:
                    x0 = int(x0 + ((y_min-y0)*(x0-x1)/(y0-y1)) + 0.5)
                    y0 = y_min
                if code0 & 8:
                    x0 = int(x0 + ((y_max-y0)*(x0-x1)/(y0-y1)) + 0.5)
                    y0 = y_max
    elif algorithm == 'Liang-Barsky':
        u0, u1 = 0.0, 1.0
        p = [x0-x1, x1-x0, y0-y1, y1-y0]
        q = [x0-x_min, x_max-x0, y0-y_min, y_max-y0]
        for i in range(4):
            if p[i] == 0 and q[i] < 0:
                return None
            elif p[i] < 0:
                u0 = max(u0, q[i]/p[i])
            elif p[i] > 0:
                u1 = min(u1, q[i]/p[i])
            if u0 > u1:
                return None
        result.append((int(x0 + u0*(x1-x0) + 0.5), int(y0 + u0*(y1-y0) + 0.5)))
        result.append((int(x0 + u1*(x1-x0) + 0.5), int(y0 + u1*(y1-y0) + 0.5)))
    return result