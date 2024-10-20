from PySide6.QtWidgets import QCheckBox, QErrorMessage ,QDialogButtonBox, QApplication, QPushButton, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLineEdit, QLabel, QDialog
from PySide6.QtGui import QDoubleValidator
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
# Требования python 3.9

class GraphLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.canvas = MatplotlibGraph(self)
        self.addWidget(self.canvas)
    def clear(self):
        self.canvas.clear()

    def set_ylabel(self, label):
        self.canvas.set_ylabel(label)

    def set_xlabel(self, label):
        self.canvas.set_xlabel(label)

    def set_title(self, title):
        self.canvas.set_title(title)

    def plot(self, X, Y):
        self.canvas.plot(X, Y)

    def draw(self):
        self.canvas.Draw()



class LatexRendererLayout(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.canvas = MatplolibLatexRenderer(self)
        self.addWidget(self.canvas)

        
    def render(self, tex):
        self.canvas.render(tex)

class MatplolibLatexRenderer(FigureCanvas):
    def __init__(self, parent=None):
        # Создание Figure и добавление осей
        self.fig = Figure()
        #self.canvas = FigureCanvas(self.fig)


        # Инициализация FigureCanvas с созданной фигурой
        super(MatplolibLatexRenderer, self).__init__(self.fig)
        self.render()

    def render(self, tex='$x$'):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        ax.axis('off')
        ax.text(0.5, 0.5, tex, fontsize=20, ha='center', va='center')
        self.draw()


class MatplotlibGraph(FigureCanvas):
    def __init__(self, parent=None):
        # Создание Figure и добавление осей
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)

        # Инициализация FigureCanvas с созданной фигурой
        super(MatplotlibGraph, self).__init__(self.fig)


    def clear(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

    def set_ylabel(self, label):
        self.ax.set_ylabel(label)

    def set_xlabel(self, label):
        self.ax.set_xlabel(label)

    def set_title(self, title):
        self.ax.set_title(title)

    def plot(self, X, Y):
        self.ax.plot(X, Y)

    def Draw(self):
        self.draw()


class ErrorDialog(QDialog):
    def __init__(self, errorMessage):
        super().__init__()

        self.setWindowTitle("Ошибка!")

        QBtn = QDialogButtonBox.Ok

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(errorMessage)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

class FloatNumberInput(QHBoxLayout):
    def __init__(self, label):
        super().__init__()
        self.label = label
        self.addWidget(QLabel(label))
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.ScientificNotation)  # Для ввода числа в экспоненциальной форме
        # Поле для ввода числа с плавающей точкой
        self.floatNumberLineEdit = QLineEdit()
        self.floatNumberLineEdit.setValidator(validator)
        #startXLineEdit.setText(str(startX))
        self.addWidget(self.floatNumberLineEdit)
    def getFloatNumber(self):
        FloatNumberString = self.floatNumberLineEdit.text()
        return float(FloatNumberString)
    def setReadOnly(self, state):
        self.floatNumberLineEdit.setReadOnly(state)
    



class ScalarStartConditions(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.addWidget(QLabel("Начальные условия"))
        initialConditionsLoyaut = QHBoxLayout()
        self.X0Input = FloatNumberInput('X0')
        initialConditionsLoyaut.addLayout(self.X0Input)
        self.UX0Input = FloatNumberInput('U(X0)')
        initialConditionsLoyaut.addLayout(self.UX0Input)
        self.addLayout(initialConditionsLoyaut)

    def getX0(self):
        return self.X0Input.getFloatNumber()
    
    def getUX0(self):
        return self.UX0Input.getFloatNumber()

class NumericalIntegrationParametersInput(QVBoxLayout):
    def __init__(self):
        super().__init__()
        mainLoyaut = QHBoxLayout()
        self.h0Input = FloatNumberInput('Начальный шаг')
        mainLoyaut.addLayout(self.h0Input)
        #mainLoyaut.addWidget(QLabel("Контроль локальной погрешности"))
        self.controlLocalErrorCheckBox = QCheckBox("Контроль локальной погрешности")
        self.controlLocalErrorCheckBox.stateChanged.connect(self.controlLocalErrorCheckBoxStateChanged)
        self.addWidget(self.controlLocalErrorCheckBox)

        self.epsilonInput = FloatNumberInput('Параметр локальной ошибки')
        mainLoyaut.addLayout(self.epsilonInput)
        self.addLayout(mainLoyaut)
    def controlLocalErrorCheckBoxStateChanged(self):
        self.epsilonInput.setReadOnly(not self.controlLocalErrorCheckBox.isChecked())


class XlimitsInput(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.addWidget(QLabel("Отрезок интегрирования"))
        self.addLayout(self.createXLimitsInput())

    def createXLimitsInput(self):
        layout2 = QHBoxLayout()
        self.startXInput = FloatNumberInput("X начальное")
        layout2.addLayout(self.startXInput)
        self.endXInput = FloatNumberInput("X конечное")
        layout2.addLayout(self.endXInput)
        self.epsilonBorderInput = FloatNumberInput("ε граничное")
        layout2.addLayout(self.epsilonBorderInput)
        return layout2
    
    def getStartX(self):
        return self.startXInput.getFloatNumber()
    
    def getEndX(self):
        endXText = self.endXLineEdit.text()
        return tryConvertToFloat(endXText, 'Неправильно указан конечный X')
    
    def getEndEpsilon(self):
        epsilonBorderText = self.epsilonBorderLineEdit.text()
        return tryConvertToFloat(epsilonBorderText, 'Неправильно указан ε граничное')

def tryConvertToFloat(startXText, errorMessage):
    try:
        startX = float(startXText)
    except(ValueError):
        showErrorMessage(errorMessage)


def showErrorMessage(errorMessage):
    dlg = ErrorDialog(errorMessage)
    dlg.exec()

