import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QDoubleSpinBox, QPushButton
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


def set_korean_font():
    for f in fm.fontManager.ttflist:
        if f.name in ["Malgun Gothic", "맑은 고딕"]:
            plt.rcParams["font.family"] = f.name
            break
    plt.rcParams["axes.unicode_minus"] = False


set_korean_font()


class PlateBoundaryApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("판 경계 지도와 연령 그래프")
        self.setGeometry(100, 100, 1250, 760)

        layout = QVBoxLayout()
        self.setLayout(layout)

        top_layout = QHBoxLayout()

        self.boundary_dir = QComboBox()
        self.boundary_dir.addItems(["세로 경계", "가로 경계"])

        top_layout.addWidget(QLabel("경계 방향"))
        top_layout.addWidget(self.boundary_dir)
        top_layout.addStretch()

        layout.addLayout(top_layout)

        input_layout = QHBoxLayout()

        self.left_dir = QComboBox()
        self.left_dir.addItems(["왼쪽", "오른쪽", "위", "아래"])

        self.right_dir = QComboBox()
        self.right_dir.addItems(["왼쪽", "오른쪽", "위", "아래"])

        self.left_speed = QDoubleSpinBox()
        self.left_speed.setRange(0.1, 30)
        self.left_speed.setValue(3)
        self.left_speed.setSingleStep(0.5)
        self.left_speed.setSuffix(" cm/년")

        self.right_speed = QDoubleSpinBox()
        self.right_speed.setRange(0.1, 30)
        self.right_speed.setValue(8)
        self.right_speed.setSingleStep(0.5)
        self.right_speed.setSuffix(" cm/년")

        input_layout.addWidget(QLabel("판 1 방향"))
        input_layout.addWidget(self.left_dir)
        input_layout.addWidget(QLabel("속도"))
        input_layout.addWidget(self.left_speed)

        input_layout.addWidget(QLabel("판 2 방향"))
        input_layout.addWidget(self.right_dir)
        input_layout.addWidget(QLabel("속도"))
        input_layout.addWidget(self.right_speed)

        layout.addLayout(input_layout)

        self.result_label = QLabel("")
        layout.addWidget(self.result_label)

        button = QPushButton("그리기")
        button.clicked.connect(self.draw_all)
        layout.addWidget(button)

        self.figure = Figure(figsize=(12, 5.8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.draw_all()

    def velocity_vector(self, direction, speed):
        if direction == "왼쪽":
            return np.array([-speed, 0.0])
        if direction == "오른쪽":
            return np.array([speed, 0.0])
        if direction == "위":
            return np.array([0.0, speed])
        if direction == "아래":
            return np.array([0.0, -speed])

    def get_boundary_vectors(self):
        if self.boundary_dir.currentText() == "세로 경계":
            tangent = np.array([0.0, 1.0])
            normal = np.array([1.0, 0.0])
        else:
            tangent = np.array([1.0, 0.0])
            normal = np.array([0.0, 1.0])

        return tangent, normal

    def classify_boundary(self, v1, v2):
        tangent, normal = self.get_boundary_vectors()

        n1 = np.dot(v1, normal)
        n2 = np.dot(v2, normal)
        t1 = np.dot(v1, tangent)
        t2 = np.dot(v2, tangent)

        normal_relative = n2 - n1
        tangent_relative = t2 - t1

        if normal_relative > 0:
            boundary_type = "발산형 경계"
        elif normal_relative < 0:
            boundary_type = "수렴형 경계"
        elif abs(tangent_relative) > 0:
            boundary_type = "보존형 경계"
        else:
            boundary_type = "경계 아님"

        return boundary_type, normal_relative, tangent_relative, n1, n2

    def draw_arrow(self, ax, x, y, v, scale=0.25):
        vx, vy = v
        dx = vx * scale
        dy = vy * scale

        length = np.sqrt(dx ** 2 + dy ** 2)

        if length == 0:
            return

        if length > 1.4:
            dx = dx / length * 1.4
            dy = dy / length * 1.4

        ax.arrow(
            x, y, dx, dy,
            head_width=0.25,
            head_length=0.35,
            length_includes_head=True,
            color="black"
        )

    def draw_map(self, ax, boundary_type, v1, v2):
        ax.set_title("위에서 본 판 경계", fontsize=13)

        ax.set_xlim(-6, 6)
        ax.set_ylim(-5, 5)
        ax.set_aspect("equal")

        ax.set_xticks([])
        ax.set_yticks([])

        # 배경 판 영역
        if self.boundary_dir.currentText() == "세로 경계":
            ax.fill_between([-6, 0], -5, 5, alpha=0.08)
            ax.fill_between([0, 6], -5, 5, alpha=0.16)

            # 경계선
            if boundary_type == "보존형 경계":
                ax.plot([0, 0], [-5, 5], color="black", linewidth=2)
            elif boundary_type == "발산형 경계":
                ax.plot([0, 0], [-5, 5], color="black", linewidth=2)
                ax.plot([-0.15, -0.15], [-5, 5], color="black", linewidth=1)
                ax.plot([0.15, 0.15], [-5, 5], color="black", linewidth=1)
            elif boundary_type == "수렴형 경계":
                ax.plot([0, 0], [-5, 5], color="black", linewidth=2)
                ax.plot([0.25, 0.6, 0.25], [-4, -3.5, -3], color="black")
                ax.plot([0.25, 0.6, 0.25], [-2, -1.5, -1], color="black")
                ax.plot([0.25, 0.6, 0.25], [0, 0.5, 1], color="black")
                ax.plot([0.25, 0.6, 0.25], [2, 2.5, 3], color="black")

            self.draw_arrow(ax, -3, 0, v1)
            self.draw_arrow(ax, 3, 0, v2)

            ax.text(-3, 1.0, "판 1", ha="center", fontsize=11)
            ax.text(3, 1.0, "판 2", ha="center", fontsize=11)

        else:
            ax.fill_between([-6, 6], -5, 0, alpha=0.08)
            ax.fill_between([-6, 6], 0, 5, alpha=0.16)

            if boundary_type == "보존형 경계":
                ax.plot([-6, 6], [0, 0], color="black", linewidth=2)
            elif boundary_type == "발산형 경계":
                ax.plot([-6, 6], [0, 0], color="black", linewidth=2)
                ax.plot([-6, 6], [-0.15, -0.15], color="black", linewidth=1)
                ax.plot([-6, 6], [0.15, 0.15], color="black", linewidth=1)
            elif boundary_type == "수렴형 경계":
                ax.plot([-6, 6], [0, 0], color="black", linewidth=2)
                ax.plot([-4, -3.5, -3], [0.25, 0.6, 0.25], color="black")
                ax.plot([-2, -1.5, -1], [0.25, 0.6, 0.25], color="black")
                ax.plot([0, 0.5, 1], [0.25, 0.6, 0.25], color="black")
                ax.plot([2, 2.5, 3], [0.25, 0.6, 0.25], color="black")

            self.draw_arrow(ax, -2, -2.5, v1)
            self.draw_arrow(ax, 2, 2.5, v2)

            ax.text(-2, -1.4, "판 1", ha="center", fontsize=11)
            ax.text(2, 3.4, "판 2", ha="center", fontsize=11)

        ax.text(0, 4.4, boundary_type, ha="center", fontsize=11)

        for spine in ax.spines.values():
            spine.set_visible(False)

    def draw_age_graph(self, ax, boundary_type, n1, n2):
        ax.set_title("거리와 연령", fontsize=13)

        x_left = np.linspace(-10, 0, 300)
        x_right = np.linspace(0, 10, 300)

        s1 = max(abs(n1), 0.1)
        s2 = max(abs(n2), 0.1)

        if boundary_type == "발산형 경계":
            y_left = np.abs(x_left) / s1
            y_right = np.abs(x_right) / s2

        elif boundary_type == "수렴형 경계":
            y_left = (x_left - x_left.min()) / s1
            y_right = (x_right.max() - x_right) / s2

        elif boundary_type == "보존형 경계":
            y_left = np.full_like(x_left, 2.5)
            y_right = np.full_like(x_right, 6.5)

        else:
            y_left = np.full_like(x_left, 4)
            y_right = np.full_like(x_right, 4)

        ax.plot(x_left, y_left, color="black", linewidth=2.8)
        ax.plot(x_right, y_right, color="black", linewidth=2.8)

        ax.axhline(0, color="black", linewidth=1)
        ax.axvline(0, color="black", linewidth=1)

        ax.set_xlim(-10, 10)
        ax.set_ylim(-0.5, 9)

        ax.set_xlabel("경계로부터의 거리")
        ax.set_ylabel("연령")

        ax.set_xticks([])
        ax.set_yticks([])

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    def draw_all(self):
        self.figure.clear()

        ax_map = self.figure.add_subplot(121)
        ax_graph = self.figure.add_subplot(122)

        v1 = self.velocity_vector(
            self.left_dir.currentText(),
            self.left_speed.value()
        )

        v2 = self.velocity_vector(
            self.right_dir.currentText(),
            self.right_speed.value()
        )

        boundary_type, normal_relative, tangent_relative, n1, n2 = self.classify_boundary(v1, v2)

        self.result_label.setText(
            f"경계 유형: {boundary_type} / "
            f"수직 상대속도: {abs(normal_relative):.1f} cm/년 / "
            f"평행 상대속도: {abs(tangent_relative):.1f} cm/년"
        )

        self.draw_map(ax_map, boundary_type, v1, v2)
        self.draw_age_graph(ax_graph, boundary_type, n1, n2)

        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlateBoundaryApp()
    window.show()
    sys.exit(app.exec())