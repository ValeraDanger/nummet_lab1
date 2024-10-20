from custom_loyauts import GraphLayout, ScalarStartConditions, NumericalIntegrationParametersInput, XlimitsInput, LatexRendererLayout
from PySide6.QtWidgets import QCheckBox, QErrorMessage ,QDialogButtonBox, QApplication, QPushButton, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QDoubleSpinBox, QVBoxLayout, QLineEdit, QLabel, QDialog
import numpy as np
from RK import l1_test



class TabTestTask(QWidget):
    def __init__(self):
        super().__init__()
        mainLayout = QVBoxLayout()
        self.RK = l1_test()
        
        testTaskLayout = LatexRendererLayout()

        texTask1 = "$\\frac{du}{dx} = -\\frac{7}{2}u$"
        testTaskLayout.render(texTask1)
        
        mainLayout.addLayout(testTaskLayout, 1)

        self.initialConditions = ScalarStartConditions()
        mainLayout.addLayout(self.initialConditions)

        self.xlimitsInput = XlimitsInput()
        mainLayout.addLayout(self.xlimitsInput)

        self.numericalIntegrationParametersInput = NumericalIntegrationParametersInput()
        mainLayout.addLayout(self.numericalIntegrationParametersInput)

        calculatePushButton = QPushButton()
        calculatePushButton.setText("Начать вычисления")
        mainLayout.addWidget(calculatePushButton)
        calculatePushButton.clicked.connect(self.calculateClick)

        self.ShowNumericSolveCheckBox = QCheckBox("Показать численное решение")
        self.ShowRealSolveCheckBox = QCheckBox("Показать аналитическое решение")
        mainLayout.addWidget(self.ShowNumericSolveCheckBox)
        mainLayout.addWidget(self.ShowRealSolveCheckBox)

        self.graph = GraphLayout()
        mainLayout.addLayout(self.graph, 3)

        aboutLoyaut = QHBoxLayout()
        referenceButton = QPushButton()
        referenceButton.setText("Справка")
        referenceButton.clicked.connect(self.referenceButtonClick)
        aboutLoyaut.addWidget(referenceButton)
        ShowTableButton = QPushButton()
        ShowTableButton.setText("Вывести таблицу")
        ShowTableButton.clicked.connect(self.ShowTableButtonClick)
        aboutLoyaut.addWidget(ShowTableButton)

        mainLayout.addLayout(aboutLoyaut)
        self.setLayout(mainLayout)

    def ShowTableButtonClick(self):
        pass
    def referenceButtonClick(self):
        pass

    def calculateClick(self):
        x = self.xlimitsInput.getStartX()
        # Создание данных и построение графика
        self.graph.clear()
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        self.graph.plot(x, y)
        self.graph.set_title("График синуса")
        self.graph.set_xlabel("x")
        self.graph.set_ylabel("sin(x)")
        self.graph.plot(x, y)
        self.graph.draw()