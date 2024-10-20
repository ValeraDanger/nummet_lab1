from custom_loyauts import *


class TabMainTask1(QWidget):
    def __init__(self):
        super().__init__()
        mainLayout = QVBoxLayout()
        
        testTaskLayout = LatexRendererLayout()

        texTask1 = r"$\frac{d^2 u}{dx} = \frac{x}{1 + x^2} \cdot u^2 + u - u^3 \cdot \sin{10x}$"
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

        # self.ShowNumericSolveCheckBox = QCheckBox("Показать численное решение")
        # self.ShowRealSolveCheckBox = QCheckBox("Показать аналитическое решение")
        # mainLayout.addWidget(self.ShowNumericSolveCheckBox)
        # mainLayout.addWidget(self.ShowRealSolveCheckBox)

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