from custom_loyauts import *


class TabMainTask2(QWidget):
    def __init__(self):
        super().__init__()
        mainLayout = QVBoxLayout()
        
        testTaskLayout = LatexRendererLayout()

        texTask1 = r"$\frac{d^2 u}{dx^2} + a^2 \sin(u) + b \sin(x) = 0$"
        testTaskLayout.render(texTask1)
        
        mainLayout.addLayout(testTaskLayout, 1)
        
        self.abinput = ABInput()
        mainLayout.addLayout(self.abinput)

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

class ABInput(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.addWidget(QLabel("Параметры"))
        self.addLayout(self.createABInput())

    def createABInput(self):
        layout2 = QHBoxLayout()
        self.AInput = FloatNumberInput("a")
        layout2.addLayout(self.AInput)
        self.BInput = FloatNumberInput("b")
        layout2.addLayout(self.BInput)
        return layout2
    
    def getA(self):
        return self.AInput.getFloatNumber()
    
    def getB(self):
        endXText = self.endXLineEdit.text()
        return self.BInput.getFloatNumber()
