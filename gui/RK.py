import typing 

class RungeKutte:

    def setStep(self, steps: list) -> None:
        '''
        Устанавливает шаг интегрирования step в книге h
        '''
        self.steps = steps

    def setFunction(self, function: typing.Callable) -> None:
        '''
        Устанавливаем функцию dy/dx = F(x, v, h)
        '''
        self.function = function

    def setStepFunction(self, stepFunction):
        self.stepFunction = stepFunction
    
    def setStages(self, numberOfStages: int, As: list, Bs: list, p: list, ) -> None:
        '''
        Устанавливаем количество шагов и коэффициэнты As alfa в левой части
        Bs beta в правой части \n
        As - одномерный список длиной numberOfStages - 1 \n
        s - numberofStages \n
        [a2, ..., ai, ... as] \n
        Bs - двумерный список следущего вида\n
        [
            [b21],
            [b31, b32],
            ...
            [bi1, bi2, ... bi i-1],
            ...
            [bs1, bs2, ... bs s-1]
        ]
        '''
        if not self.isCorrectLen(numberOfStages, As, Bs):
            raise TypeError("len of As or Bs is not suite numberofStages")
        
        if not self.isBsShapeCorrect(Bs):
            raise TypeError("Shape of Bs is not correct")
        if len(p) != numberOfStages:
            raise TypeError("len p is uncorrect")

        self.As = As
        self.Bs = Bs
        self.numberOfStages = numberOfStages
        self.p = p

    def isBsShapeCorrect(self, Bs: list):
        for i, el in enumerate(Bs, 1):
            if not len(el) == i:
                return False
        return True

    def isCorrectLen(self, numberOfStages, As, Bs):
        return (len(As) == numberOfStages - 1) and (len(Bs) == numberOfStages - 1)
    
    def __init__(self, initialConditions):
        self.currentCoordinates = initialConditions

    def _calculateKs(self, step):
        ks = []
        currentCoordinates = self.currentCoordinates
        ks.append(self.function(currentCoordinates))
        x, y = self.currentCoordinates
        for a, bs in zip(self.As, self.Bs):
            # f (left, right)
            left = x + a * step
            right = 0
            for b, k in zip(bs, ks):
                right += b * k
            right *= step
            right += y
            ks.append(self.function((left, right)))
        return ks



    def next(self) -> tuple:
        step = self.stepFunction(self.currentCoordinates)
        F = self.calculateF(step)
        x, v = self.currentCoordinates
        self.currentCoordinates = (x + step, v + step * F)

    def getCoordinates(self):
        return self.currentCoordinates

    def calculateF(self, step):
        ks = self._calculateKs(step)
        resultado = 0
        for p, k in zip(self.p, ks):
            resultado += p * k
        return resultado


    #def f(u, x):
     #   return u**2-2*x**2


def createFromInitialConditions(initialConditions: tuple) -> RungeKutte:
    '''
    создание Рунге-Кутта по initialConditions - начальные условия (x0, u0)
    '''
    return RungeKutte(initialConditions)

#рунге Кутта явный 2-го порядка



def Oleg():
    def Fu(coordinates):
        x, y = coordinates
        return 2*y

    def stepF(coordinates):
        return 0.01
    
    RK3 = createFromInitialConditions((1, 1))
    RK3.setFunction(Fu)
    RK3.setStages(2, [1, ], [[1,],], [0.5, 0.5])
    RK3.setStepFunction(stepF)

    for i in range(2):
        RK3.next()
        print(RK3.getCoordinates())


class RK2(RungeKutte):
    def __init__(self):
        super(self).__init__()
        


def Ruslan():
    def Fu(coordinates):
        x, y = coordinates
        return y**2-2*x**2

    def stepF(coordinates):
        return 0.01
    
    RK4 = createFromInitialConditions((1, 1))
    RK4.setFunction(Fu)
    RK4.setStages(2, [0.5, ], [[0.5,],], [0, 1])
    RK4.setStepFunction(stepF)

    for i in range(2):
        RK4.next()
        print(RK4.getCoordinates())

def Diana():
    def Fu(coordinates):
        x, y = coordinates
        return 2*y

    def stepF(coordinates):
        return 0.01
    
    RK4 = createFromInitialConditions((1, 1))
    RK4.setFunction(Fu)
    RK4.setStages(2, [0.5, ], [[0.5,],], [0, 1])
    RK4.setStepFunction(stepF)

    for i in range(2):
        RK4.next()
        print(RK4.getCoordinates())

def Ivan():
    def Fu(coordinates):
        x, y = coordinates
        return y**2-2*x**2

    def stepF(coordinates):
        return 0.01
    
    RK3 = createFromInitialConditions((1, 1))
    RK3.setFunction(Fu)
    RK3.setStages(2, [1, ], [[1,],], [0.5, 0.5])
    RK3.setStepFunction(stepF)

    for i in range(2):
        RK3.next()
        print(RK3.getCoordinates())
#Oleg()
#Ruslan()
#Ivan()

#Diana()
'''
v1 = 0.98969975
x1 = 1.01
h = 0.01
#print(v1+h*(v1+h/2*(v1**2-2*x1**2)**2)-2*(x1+h/2)**2)

z4 = (v1**2-2*x1**2)
print(z4)

z1 = v1 + h/2*(v1**2-2*x1**2)
print(z1)

z2 = z1**2-2*(x1+h/2)**2
print(z2)

v2 = v1 + h*z2
print(v2)
'''