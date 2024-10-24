from PySide6.QtWidgets import QCheckBox, QApplication, QPushButton, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLineEdit, QLabel, QDialog, QTableWidget, QTableWidgetItem, QFileDialog
from PySide6.QtGui import QDoubleValidator, QIntValidator
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import sys
import json
import os
import typing
import ctypes
import platform
import subprocess
import pandas as pd
from RK import l1_test
from custom_loyauts import LatexRendererLayout, GraphLayout, IntNumberInput, FloatNumberInput, NumericalIntegrationParametersInput, ScalarStartConditions, XlimitsInput, NewWindow, ErrorDialog

# ... (остальные классы: CPPDynamicLibrary, CSVReaderPandas, l1_test,
# GraphLayout, LatexRendererLayout, MatplotlibGraph, MatplolibLatexRenderer,
# ErrorDialog, FloatNumberInput, IntNumberInput, ScalarStartConditions,
# NumericalIntegrationParametersInput, XlimitsInput)

from abc import ABC, abstractmethod

class Calculator(ABC):
    @abstractmethod
    def calculate(self, *args, **kwargs):
        pass

class RK4Calculator(Calculator):
    def __init__(self, rk_solver):
        self.rk_solver = rk_solver

    def calculate(self, x0, u_x0, h0, x_end, amountOfSteps):
        try:
            self.rk_solver.rk_4(x0, u_x0, h0, x_end, amountOfSteps)
        except Exception as e:
            print(f"Ошибка во время вычислений RK4: {e}", file=sys.stderr)
            ErrorDialog(f"Ошибка во время вычислений RK4: {e}").exec()

class RK4AdaptiveCalculator(Calculator):
    def __init__(self, rk_solver):
        self.rk_solver = rk_solver

    def calculate(self, x0, u_x0, h0, x_end, local_error, epsilon_border, amountOfSteps):
        try:
            self.rk_solver.rk4_adaptive(x0, u_x0, h0, x_end, local_error, epsilon_border, amountOfSteps)
        except Exception as e:
            print(f"Ошибка во время вычислений RK4 Adaptive: {e}", file=sys.stderr)
            ErrorDialog(f"Ошибка во время вычислений RK4 Adaptive: {e}").exec()

# Класс для отображения графика
class TestTaskPlotter:
    def __init__(self, graph_layout, show_numeric_solve_checkbox, show_real_solve_checkbox):
        self.graph_layout = graph_layout
        self.show_numeric_solve_checkbox = show_numeric_solve_checkbox
        self.show_real_solve_checkbox = show_real_solve_checkbox

    def plot(self, x, v, u):
        self.graph_layout.clear()

        if self.show_numeric_solve_checkbox.isChecked():
            self.graph_layout.plot(x, v, label="Численное решение")

        if self.show_real_solve_checkbox.isChecked():
            #print(f"x {x} \ny {u}")
            self.graph_layout.plot(x, u, label="Аналитическое решение")

        # Заголовок выводится только один раз при инициализации
        if self.graph_layout.canvas.ax.get_title() == '':
            self.graph_layout.set_title("График решения")

        self.graph_layout.set_xlabel("x")
        self.graph_layout.set_ylabel("u(x)")
        if (self.show_real_solve_checkbox.isChecked() or self.show_numeric_solve_checkbox.isChecked()):
            self.graph_layout.legend()
        self.graph_layout.draw()

# Класс для управления настройками
class TestTaskSettingsManager:
    def __init__(self, settings_file, ui_elements):
        self.settings_file = settings_file
        self.ui_elements = ui_elements

    def save_settings(self, df, filename):
        # Сохранение DataFrame в CSV файл
        csv_filename = filename + ".csv"
        df.to_csv(csv_filename, sep=";", index=False, header=False)

        # Сохранение настроек в JSON файл
        settings = {
            "initialConditions": {
                "X0": self.ui_elements["initialConditions"].X0Input.floatNumberLineEdit.text(),
                "UX0": self.ui_elements["initialConditions"].UX0Input.floatNumberLineEdit.text()
            },
            "xlimits": {
                "endX": self.ui_elements["xlimitsInput"].endXInput.floatNumberLineEdit.text(),
                "epsilonBorder": self.ui_elements["xlimitsInput"].epsilonBorderInput.floatNumberLineEdit.text()
            },
            "numericalIntegrationParameters": {
                "h0": self.ui_elements["numericalIntegrationParametersInput"].h0Input.floatNumberLineEdit.text(),
                "controlLocalError": self.ui_elements["numericalIntegrationParametersInput"].controlLocalErrorCheckBox.isChecked(),
                "epsilon": self.ui_elements["numericalIntegrationParametersInput"].epsilonInput.floatNumberLineEdit.text(),
                "to_be_control_local_error": self.ui_elements["numericalIntegrationParametersInput"].isControlLocalError()
            },
            "showNumericSolve": self.ui_elements["showNumericSolveCheckBox"].isChecked(),
            "showRealSolve": self.ui_elements["showRealSolveCheckBox"].isChecked(),
            "amountOfSteps": self.ui_elements["amountOfStepsInput"].intNumberLineEdit.text(),
            "csv_filename": os.path.relpath(csv_filename, os.path.dirname(filename)),  # Относительный путь
            "task_number": 0
        }

        json_filename = filename + ".json"
        try:
            with open(json_filename, "w") as f:
                json.dump(settings, f, indent=4)
            print(f"Настройки сохранены в файлы {json_filename} и {csv_filename}")
        except Exception as e:
            print(f"Ошибка при сохранении настроек: {e}", file=sys.stderr)
            ErrorDialog(f"Ошибка при сохранении настроек: {e}").exec()

    def load_settings(self):
        filename, _ = QFileDialog.getOpenFileName(
            None, "Загрузить настройки", "", "JSON files (*.json)"
        )
        if filename:
            try:
                with open(filename, "r") as f:
                    settings = json.load(f)

                if "task_number" not in settings or settings["task_number"] != 0:
                    print("Ошибка: Загруженный файл настроек не соответствует тестовой задаче.")
                    ErrorDialog("Ошибка: Загруженный файл настроек не соответствует тестовой задаче.").exec()
                    return

                self.ui_elements["initialConditions"].X0Input.floatNumberLineEdit.setText(settings["initialConditions"]["X0"])
                self.ui_elements["initialConditions"].UX0Input.floatNumberLineEdit.setText(settings["initialConditions"]["UX0"])
                self.ui_elements["xlimitsInput"].endXInput.floatNumberLineEdit.setText(settings["xlimits"]["endX"])
                self.ui_elements["xlimitsInput"].epsilonBorderInput.floatNumberLineEdit.setText(settings["xlimits"]["epsilonBorder"])
                self.ui_elements["numericalIntegrationParametersInput"].h0Input.floatNumberLineEdit.setText(settings["numericalIntegrationParameters"]["h0"])
                self.ui_elements["numericalIntegrationParametersInput"].controlLocalErrorCheckBox.setChecked(settings["numericalIntegrationParameters"]["controlLocalError"])
                self.ui_elements["numericalIntegrationParametersInput"].epsilonInput.floatNumberLineEdit.setText(settings["numericalIntegrationParameters"]["epsilon"])
                self.ui_elements["showNumericSolveCheckBox"].setChecked(settings["showNumericSolve"])
                self.ui_elements["showRealSolveCheckBox"].setChecked(settings["showRealSolve"])
                self.ui_elements["amountOfStepsInput"].intNumberLineEdit.setText(settings["amountOfSteps"])
                self.ui_elements["numericalIntegrationParametersInput"].setChecked(settings["numericalIntegrationParameters"]["to_be_control_local_error"])

                csv_filename = os.path.join(os.path.dirname(filename), settings["csv_filename"])
                self.ui_elements["parent"].load_dataframe(csv_filename, self.ui_elements["numericalIntegrationParametersInput"].isControlLocalError())
                self.ui_elements["parent"].refreshPlot()  # Обновление графика после загрузки

                print(f"Настройки загружены из файла {filename}")
            except Exception as e:
                print(f"Ошибка при загрузке настроек: {e}", file=sys.stderr)
                ErrorDialog(f"Ошибка при загрузке настроек: {e}").exec()

# Класс для создания отчета
class ReportGenerator:
    def __init__(self, df, xlimits_input):
        self.df = df
        self.xlimits_input = xlimits_input

    def generate_report(self):
        report = ""
        amountOfIterations = len(self.df['x']) - 1
        report += f"Количество итераций: {amountOfIterations} \n"
        x = self.getColumnValues('x')
        l = len(x)
        difference_between_the_right_border_and_the_last_calculated_point = abs(
            x[l - 1] - self.xlimits_input.getEndX())
        report += f'разница между правой границей и последней вычисленной точки: {difference_between_the_right_border_and_the_last_calculated_point}\n'
        if 'e' in self.df.columns:  # Проверка наличия столбца 'e'
            E = self.getColumnValues('e')
            maxError = max(E)
            max_error_index = E.index(maxError)
            report += f'Максимальное значение ОЛП {maxError} при x = {x[max_error_index]}\n'
            doubling = self.getColumnValues('c2')
            countOfDoubling = sum(doubling)
            report += f'Количество удвоений {countOfDoubling}\n'
            doubling = self.getColumnValues('c1')
            countOfDoubling = sum(doubling)
            report += f'Количество делений {countOfDoubling}\n'
            h = self.getColumnValues('h')
            maxStep = max(h)
            minStep = min(h)
            xMinStep = h.index(minStep)
            xMinStep = x[xMinStep]
            xMaxStep = h.index(maxStep)
            xMaxStep = x[xMaxStep]
            report += f'максимальный шаг {maxStep} при x={xMaxStep}\n'
            report += f'Минимальный шаг {minStep} при x={xMinStep}\n'
            u = np.array(self.getColumnValues('u'), dtype=np.float64)
            v = np.array(self.getColumnValues('v'), dtype=np.float64)
            difference = np.abs(u - v)
            maxDifference = np.max(difference)
            report += f'Максимальная разница численного и реального решения {maxDifference}'
        return report

    def getColumnValues(self, column):
        return pd.to_numeric(self.df[column][1:], errors='coerce').dropna().tolist()

# Класс для создания UI элементов
class TestTaskUI:
    def __init__(self, main_layout):
        self.main_layout = main_layout
        self.initial_conditions = None
        self.xlimits_input = None
        self.numerical_integration_parameters_input = None
        self.show_numeric_solve_checkbox = None
        self.show_real_solve_checkbox = None
        self.amount_of_steps_input = None
        self.graph_layout = None

    def setup_ui(self):
        self._add_task_description()
        self._add_initial_conditions()
        self._add_xlimits_input()
        self._add_numerical_integration_parameters_input()
        self._add_calculate_button()
        self._add_checkboxes()
        self._add_amount_of_steps_input()
        self._add_graph_layout()
        self._add_buttons()

    def _add_task_description(self):
        test_task_layout = LatexRendererLayout()
        tex_task1 = "$\\frac{du}{dx} = -\\frac{7}{2}u$"
        test_task_layout.render(tex_task1)
        self.main_layout.addLayout(test_task_layout, 1)

    def _add_initial_conditions(self):
        self.initial_conditions = ScalarStartConditions()
        self.main_layout.addLayout(self.initial_conditions)

    def _add_xlimits_input(self):
        self.xlimits_input = XlimitsInput()
        self.main_layout.addLayout(self.xlimits_input)

    def _add_numerical_integration_parameters_input(self):
        self.numerical_integration_parameters_input = NumericalIntegrationParametersInput()
        self.main_layout.addLayout(self.numerical_integration_parameters_input)

    def _add_calculate_button(self):
        calculate_button = QPushButton()
        calculate_button.setText("Начать вычисления")
        self.main_layout.addWidget(calculate_button)
        calculate_button.clicked.connect(self.parent().calculateClick)  # Вызов метода calculateClick родительского класса

    def _add_checkboxes(self):
        self.show_numeric_solve_checkbox = QCheckBox("Показать численное решение")
        self.show_real_solve_checkbox = QCheckBox("Показать аналитическое решение")
        self.show_numeric_solve_checkbox.checkStateChanged.connect(self.parent().refreshPlot)
        self.show_real_solve_checkbox.checkStateChanged.connect(self.parent().refreshPlot)
        self.main_layout.addWidget(self.show_numeric_solve_checkbox)
        self.main_layout.addWidget(self.show_real_solve_checkbox)

    def _add_amount_of_steps_input(self):
        self.amount_of_steps_input = IntNumberInput("Количество шагов")
        self.main_layout.addLayout(self.amount_of_steps_input)

    def _add_graph_layout(self):
        self.graph_layout = GraphLayout()
        self.main_layout.addLayout(self.graph_layout, 3)

    def _add_buttons(self):
        about_layout = QHBoxLayout()
        reference_button = QPushButton()
        reference_button.setText("Справка")
        reference_button.clicked.connect(self.parent().referenceButtonClick)  # Вызов метода referenceButtonClick родительского класса
        about_layout.addWidget(reference_button)
        show_table_button = QPushButton()
        show_table_button.setText("Вывести таблицу")
        show_table_button.clicked.connect(self.parent().ShowTableButtonClick)  # Вызов метода ShowTableButtonClick родительского класса
        about_layout.addWidget(show_table_button)

        save_settings_button = QPushButton()
        save_settings_button.setText("Сохранить настройки")
        save_settings_button.clicked.connect(self.parent().saveSettings)  # Вызов метода saveSettings родительского класса
        about_layout.addWidget(save_settings_button)
        load_settings_button = QPushButton()
        load_settings_button.setText("Загрузить настройки")
        load_settings_button.clicked.connect(self.parent().loadSettings)  # Вызов метода loadSettings родительского класса
        about_layout.addWidget(load_settings_button)

        self.main_layout.addLayout(about_layout)

    def parent(self):
        return self.main_layout.parent()

class TabTestTask(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.RK = l1_test()
        self.settings_file = "test_task"  # Базовое имя файла без расширения
        self.df = None  # Переменная для хранения DataFrame
        self.to_be_control_local_error = False

        self.rk4_calculator = RK4Calculator(self.RK)
        self.rk4_adaptive_calculator = RK4AdaptiveCalculator(self.RK)

        self.ui = TestTaskUI(self.main_layout)
        self.ui.setup_ui()
        self.plotter = TestTaskPlotter(self.ui.graph_layout, self.ui.show_numeric_solve_checkbox, self.ui.show_real_solve_checkbox)
        self.settings_manager = TestTaskSettingsManager(self.settings_file, {
            "initialConditions": self.ui.initial_conditions,
            "xlimitsInput": self.ui.xlimits_input,
            "numericalIntegrationParametersInput": self.ui.numerical_integration_parameters_input,
            "showNumericSolveCheckBox": self.ui.show_numeric_solve_checkbox,
            "showRealSolveCheckBox": self.ui.show_real_solve_checkbox,
            "amountOfStepsInput": self.ui.amount_of_steps_input,
            "parent": self  # Добавлено для доступа к методам TabTestTask
        })
        #self.loadSettings()  # Загрузка настроек после создания UI

    def calculateClick(self):
        # ... (код для получения параметров из UI)
        if self._validate_input():
            self._perform_calculation()
            self.tryLoadResult(self.to_be_control_local_error)
            self.refreshPlot()

    def _validate_input(self):
        # ... (код для валидации входных данных)
        x_end = self.ui.xlimits_input.getEndX()
        x0 = self.ui.initial_conditions.getX0()
        amount_of_steps = self.ui.amount_of_steps_input.getIntNumber()
        h0 = self.ui.numerical_integration_parameters_input.getStartStep()
        local_error = self.ui.numerical_integration_parameters_input.getEpsilonLocalError()

        if x_end <= x0:
            self.show_error("Ошибка: Конечное значение X должно быть больше начального.")
            return False

        if amount_of_steps <= 0:
            self.show_error("Ошибка: Количество шагов должно быть положительным числом.")
            return False

        if h0 <= 0:
            self.show_error("Ошибка: Начальный шаг должен быть положительным числом.")
            return False

        if local_error <= 0:
            self.show_error("Ошибка: Допустимая локальная погрешность должна быть положительным числом.")
            return False

        return True  # Возвращаем True, если все данные валидны

    def _perform_calculation(self):
        # ... (код для выполнения вычислений)
        x_end = self.ui.xlimits_input.getEndX()
        x0 = self.ui.initial_conditions.getX0()
        u_x0 = self.ui.initial_conditions.getUX0()
        epsilon_border = self.ui.xlimits_input.getEndEpsilon()
        amountOfSteps = self.ui.amount_of_steps_input.getIntNumber()
        h0 = self.ui.numerical_integration_parameters_input.getStartStep()
        local_error = self.ui.numerical_integration_parameters_input.getEpsilonLocalError()
        self.to_be_control_local_error = self.ui.numerical_integration_parameters_input.isControlLocalError()

        try:
            if self.to_be_control_local_error:
                self.rk4_adaptive_calculator.calculate(x0, u_x0, h0, x_end, local_error, epsilon_border, amountOfSteps)
            else:
                self.rk4_calculator.calculate(x0, u_x0, h0, x_end, amountOfSteps)
        except Exception as e:
            self.show_error(f"Ошибка во время вычислений: {e}")

    def refreshPlot(self):
        if self.df is not None:
            self.plotter.plot(self.getColumnValues(self.df, 'x'), self.getColumnValues(self.df, 'v'), self.getColumnValues(self.df, 'u'))

    def closeEvent(self, event):
        self.saveSettings()
        event.accept()

    def ShowTableButtonClick(self):
        if self.df is None:
            self.show_error("Ошибка: Сначала необходимо выполнить вычисления.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Таблица результатов")
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        layout.addWidget(table)

        if self.ui.numerical_integration_parameters_input.isControlLocalError():
            self.columns = ['x', 'v', 'v2i', 'v-v2i', 'e', 'h', 'c1', 'c2', 'u', '|ui-vi|']
        else:
            self.columns = ['x', 'v', 'u']

        table.setColumnCount(len(self.columns))
        table.setRowCount(len(self.df))
        table.setHorizontalHeaderLabels(self.columns)
        self.data = self.df.values.tolist()[1:]
        for row, data_row in enumerate(self.data):
            for col, value in enumerate(data_row):
                if col < len(self.columns):  # Проверка на выход за пределы списка columns
                    item = QTableWidgetItem(str(value))
                    table.setItem(row, col, item)

        dialog.exec()

    def referenceButtonClick(self):
        if self.df is None:
            self.show_error("Ошибка: Сначала необходимо выполнить вычисления.")
            return

        try:
            report_generator = ReportGenerator(self.df, self.ui.xlimits_input)
            report = report_generator.generate_report()

            window = NewWindow('Справка', report)
            window.show()
            window.exec()
        except Exception as e:
            self.show_error(f"Ошибка во время анализа: {e}")

    def tryLoadResult(self, to_be_control_local_error):
        try:
            current_file_path = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file_path)
            current_dir = os.path.join(current_dir, "..") 
            current_dir = os.path.join(current_dir, "output")
            file_path = os.path.join(current_dir, "output_test.csv")
            if to_be_control_local_error:
                self.df = pd.read_csv(file_path, delimiter=";", header=None,
                                 names=['x', 'v', 'v2i', 'v-v2i', 'e', 'h', 'c1', 'c2', 'u', '|ui-vi|'])
            else:
                self.df = pd.read_csv(file_path, delimiter=";", header=None, names=['x', 'v', 'u'])
        except Exception as e:
            self.show_error(f"Ошибка во время загрузки: {e}")

    def getColumnValues(self, df, column):
        return pd.to_numeric(df[column][1:], errors='coerce').dropna().tolist()

    def saveSettings(self):
        if self.df is not None:
            filename, _ = QFileDialog.getSaveFileName(None, "Сохранить настройки", self.settings_file, "JSON files (*.json)")
            if filename:
                self.settings_manager.save_settings(self.df, filename[:-5])  # Сохранение DataFrame и настроек

    def loadSettings(self):
        self.settings_manager.load_settings()
        self.to_be_control_local_error = self.ui.numerical_integration_parameters_input.isControlLocalError()

    def load_dataframe(self, csv_filename, control_local_error):
        """Загружает DataFrame из CSV файла в зависимости от control_local_error."""
        current_file_path = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file_path)
        current_dir = os.path.join(current_dir, "..") 
        current_dir = os.path.join(current_dir, "output")
        file_path = os.path.join(current_dir, csv_filename)
        try:
            if control_local_error:
                self.df = pd.read_csv(file_path, delimiter=";", header=None, low_memory=False,
                                       names=['x', 'v', 'v2i', 'v-v2i', 'e', 'h', 'c1', 'c2', 'u', '|ui-vi|'])
            else:
                self.df = pd.read_csv(file_path, delimiter=";", low_memory=False, header=None, names=['x', 'v', 'u'])
        except Exception as e:
            self.show_error(f"Ошибка при загрузке DataFrame: {e}")

    def show_error(self, message):
        """Отображает сообщение об ошибке."""
        print(message, file=sys.stderr)
        ErrorDialog(message).exec()