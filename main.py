import tkinter as tk
from tkinter import ttk, messagebox
import math
import random

# Геометрические вспомогательные функции

def dist_point_to_line(px, py, x1, y1, x2, y2):
    # Расстояние от точки (px, py) до прямой, проходящей через (x1,y1) и (x2,y2).
    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length == 0:
        return math.hypot(px - x1, py - y1)
    return abs(dx * (y1 - py) - (x1 - px) * dy) / length


def line_intersects_circle(x1, y1, x2, y2, cx, cy, r):
    # Проверяет, пересекает ли прямая (через две точки) окружность с центром (cx,cy) и радиусом r.
    d = dist_point_to_line(cx, cy, x1, y1, x2, y2)
    return d <= r


def count_intersections(p1, p2, circles):
    # Считает количество окружностей, пересекаемых прямой через p1 и p2.
    x1, y1 = p1
    x2, y2 = p2
    count = 0
    for (cx, cy, r) in circles:
        if line_intersects_circle(x1, y1, x2, y2, cx, cy, r):
            count += 1
    return count


def find_best_pair(points, circles):
    # Полный перебор: ищет пару точек из множества A,
    # прямая через которые пересекает максимальное число окружностей из B.
    # Возвращает (i, j, max_count).
    n = len(points)
    best_i, best_j, best_count = 0, 1, 0
    for i in range(n):
        for j in range(i + 1, n):
            cnt = count_intersections(points[i], points[j], circles)
            if cnt > best_count:
                best_count = cnt
                best_i, best_j = i, j
    return best_i, best_j, best_count


# Логика холста

class App:
    CANVAS_W = 700
    CANVAS_H = 550
    POINT_R = 5
    MARGIN = 40

    def __init__(self, root):
        self.root = root
        self.root.title("Задание 18 - Прямая через множество точек и окружности")
        self.root.resizable(False, False)

        self.points_A = []   # список (x, y) в координатах холста
        self.circles_B = []  # список (x, y, r) в координатах холста
        self.mode = tk.StringVar(value="point")  # "point" или "circle"
        self.result_line = None  # индексы лучшей пары

        self._build_ui()

    # ── Построение интерфейса ──────────────────────────────────────────────────

    def _build_ui(self):
        # Верхняя панель управления
        ctrl = tk.Frame(self.root, bg="#f0f0f0", pady=6)
        ctrl.pack(fill=tk.X)

        tk.Label(ctrl, text="Режим добавления:", bg="#f0f0f0").pack(side=tk.LEFT, padx=8)
        tk.Radiobutton(ctrl, text="Точка (A)", variable=self.mode,
                       value="point", bg="#f0f0f0").pack(side=tk.LEFT)
        tk.Radiobutton(ctrl, text="Окружность (B)", variable=self.mode,
                       value="circle", bg="#f0f0f0").pack(side=tk.LEFT, padx=4)

        tk.Button(ctrl, text="Случайная генерация", command=self.generate_random,
                  bg="#4a90d9", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=10)
        tk.Button(ctrl, text="Найти решение", command=self.solve,
                  bg="#27ae60", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT)
        tk.Button(ctrl, text="Очистить", command=self.clear,
                  bg="#e74c3c", fg="white", relief=tk.FLAT, padx=8).pack(side=tk.LEFT, padx=10)

        # Холст
        self.canvas = tk.Canvas(self.root, width=self.CANVAS_W, height=self.CANVAS_H,
                                bg="white", cursor="crosshair")
        self.canvas.pack(padx=10, pady=4)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Нижняя строка состояния
        self.status_var = tk.StringVar(value="Кликните на холсте для добавления точек и окружностей.")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                              anchor=tk.W, bg="#dde", relief=tk.SUNKEN, padx=6)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Легенда
        legend = tk.Frame(self.root, bg="#f0f0f0", pady=3)
        legend.pack(fill=tk.X, padx=10)
        tk.Label(legend, text="● Синие - точки A    ○ Чёрные - окружности B    - Красная - оптимальная прямая",
                 bg="#f0f0f0", fg="#333").pack(side=tk.LEFT)

        self._draw_grid()

    # ── Сетка ─────────────────────────────────────────────────────────────────

    def _draw_grid(self):
        self.canvas.delete("grid")
        step = 50
        for x in range(0, self.CANVAS_W, step):
            self.canvas.create_line(x, 0, x, self.CANVAS_H,
                                    fill="#e8e8e8", tags="grid")
        for y in range(0, self.CANVAS_H, step):
            self.canvas.create_line(0, y, self.CANVAS_W, y,
                                    fill="#e8e8e8", tags="grid")

    # ── Обработка кликов ──────────────────────────────────────────────────────

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        if self.mode.get() == "point":
            self.points_A.append((x, y))
            self._draw_point(x, y, len(self.points_A) - 1)
            self.status_var.set(f"Добавлена точка A{len(self.points_A) - 1} ({x}, {y}). "
                                f"Всего точек: {len(self.points_A)}")
        else:
            r = random.randint(20, 55)
            self.circles_B.append((x, y, r))
            self._draw_circle(x, y, r, len(self.circles_B) - 1)
            self.status_var.set(f"Добавлена окружность B{len(self.circles_B) - 1} "
                                f"центр ({x}, {y}), r={r}. "
                                f"Всего окружностей: {len(self.circles_B)}")
        self.result_line = None

    # ── Отрисовка элементов ───────────────────────────────────────────────────

    def _draw_point(self, x, y, idx, highlight=False):
        r = self.POINT_R
        color = "#e74c3c" if highlight else "red"
        outline = "#c0392b" if highlight else "red"
        self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                fill=color, outline=outline,
                                width=2, tags=f"pt_{idx}")
        self.canvas.create_text(x + 8, y - 8,
                                text=f"A", font=("Arial", 8),
                                fill="#1a5276", tags=f"pt_{idx}_lbl")

    def _draw_circle(self, cx, cy, r, idx, highlight=False):
        color = "#e67e22" if highlight else "#2c3e50"
        width = 3 if highlight else 1.5
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                outline=color, width=width,
                                tags=f"circ_{idx}")
        self.canvas.create_text(cx, cy,
                                text=f"B{idx}", font=("Arial", 8),
                                fill="#7f8c8d", tags=f"circ_{idx}_lbl")

    def _draw_best_line(self, i, j):
        # Рисует прямую через точки i и j, продлённую до краёв холста.
        self.canvas.delete("best_line")
        x1, y1 = self.points_A[i]
        x2, y2 = self.points_A[j]
        pts = self._extend_line(x1, y1, x2, y2)
        if pts:
            self.canvas.create_line(*pts, fill="#e74c3c", width=2.5,
                                    dash=(8, 4), tags="best_line")

    def _extend_line(self, x1, y1, x2, y2):
        # Продлевает отрезок до пересечения с границами холста.
        W, H = self.CANVAS_W, self.CANVAS_H
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return None
        intersections = []
        for t in [
            (-x1 / dx) if dx != 0 else None,
            ((W - x1) / dx) if dx != 0 else None,
            (-y1 / dy) if dy != 0 else None,
            ((H - y1) / dy) if dy != 0 else None,
        ]:
            if t is None:
                continue
            xi, yi = x1 + t * dx, y1 + t * dy
            if -1 <= xi <= W + 1 and -1 <= yi <= H + 1:
                intersections.append((xi, yi))
        if len(intersections) >= 2:
            return (*intersections[0], *intersections[1])
        return None

    # ── Алгоритм решения ──────────────────────────────────────────────────────

    def solve(self):
        if len(self.points_A) < 2:
            messagebox.showwarning("Недостаточно данных",
                                   "Добавьте минимум 2 точки в множество A.")
            return
        if len(self.circles_B) == 0:
            messagebox.showwarning("Недостаточно данных",
                                   "Добавьте хотя бы одну окружность в множество B.")
            return

        best_i, best_j, best_count = find_best_pair(self.points_A, self.circles_B)

        # Перерисовываем с подсветкой
        self._redraw_all(best_i, best_j)
        self._draw_best_line(best_i, best_j)
        self.result_line = (best_i, best_j)

        self.status_var.set(
            f"Результат: прямая через A{best_i} и A{best_j} "
            f"пересекает {best_count} из {len(self.circles_B)} окружностей."
        )

    def _redraw_all(self, hi=None, hj=None):
        self.canvas.delete("all")
        self._draw_grid()
        for idx, (cx, cy, r) in enumerate(self.circles_B):
            # Определяем, пересекается ли эта окружность оптимальной прямой
            highlight = False
            if hi is not None and hj is not None:
                x1, y1 = self.points_A[hi]
                x2, y2 = self.points_A[hj]
                highlight = line_intersects_circle(x1, y1, x2, y2, cx, cy, r)
            self._draw_circle(cx, cy, r, idx, highlight=highlight)
        for idx, (x, y) in enumerate(self.points_A):
            highlight = idx in (hi, hj) if hi is not None else False
            self._draw_point(x, y, idx, highlight=highlight)

    # ── Генерация случайных данных ────────────────────────────────────────────

    def generate_random(self):
        self.clear()
        n_points = random.randint(5, 10)
        n_circles = random.randint(5, 10)
        pad = 60
        for _ in range(n_points):
            x = random.randint(pad, self.CANVAS_W - pad)
            y = random.randint(pad, self.CANVAS_H - pad)
            self.points_A.append((x, y))
        for _ in range(n_circles):
            cx = random.randint(pad, self.CANVAS_W - pad)
            cy = random.randint(pad, self.CANVAS_H - pad)
            r = random.randint(20, 60)
            self.circles_B.append((cx, cy, r))
        self._redraw_all()
        self.status_var.set(
            f"Сгенерировано: {n_points} точек A и {n_circles} окружностей B. "
            "Нажмите «Найти решение»."
        )

    # ── Очистка ───────────────────────────────────────────────────────────────

    def clear(self):
        self.points_A.clear()
        self.circles_B.clear()
        self.result_line = None
        self.canvas.delete("all")
        self._draw_grid()
        self.status_var.set("Холст очищен. Кликните для добавления точек и окружностей.")


# Точка входа

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
