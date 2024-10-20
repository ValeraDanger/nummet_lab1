import typing 
import os
import ctypes
import platform
import subprocess
import pandas as pd
import numpy as np

class CPPDynamicLibrary:
    def __init__(self):
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        parent_directory = os.path.dirname(current_directory)
        libs_directory = os.path.join(parent_directory, 'libs')

        folders = {"Windows": 'windows', "Darwin": 'macos', "Linux": 'linux'}
        self.extensions = {"Windows": '.dll', "Darwin": '.dylib', "Linux": '.so'}
        system = platform.system()
        self.libs_directory = os.path.join(libs_directory, folders[system])
        self.extension = self.extensions[system]
        os.environ['PATH'] = self.libs_directory + os.pathsep + os.environ['PATH']
    def getPathTo(self, name: str):
        return os.path.join(self.libs_directory, name + self.extension)

class CSVReaderPandas:
    """
    Класс для чтения CSV файлов с использованием Pandas.
    """

    def __init__(self, filename, delimiter=",", quotechar='"'):
        """
        Инициализирует объект CSVReaderPandas.

        :param filename: Путь к CSV файлу.
        :param delimiter: Разделитель столбцов (по умолчанию ",").
        :param quotechar: Символ для экранирования значений (по умолчанию '"').
        """
        directory = self.getOutputDirectory()
        self.filename = os.path.join(directory, filename)
        self.delimiter = delimiter
        self.quotechar = quotechar

    def readAsNumpy(self, header=0):
        """
        Читает CSV файл и возвращает заголовки и значения в виде массивов NumPy.

        :param header: Номер строки или список номеров строк, которые будут использоваться как заголовки 
                       (по умолчанию 0 - первая строка).
        :return: Кортеж из двух массивов NumPy: (заголовки, значения).
        """
        df = pd.read_csv(self.filename, delimiter=self.delimiter, quotechar=self.quotechar, header=header)
        headers = df.columns.to_numpy()  # Использование to_numpy() для заголовков
        values = df.to_numpy()           # Использование to_numpy() для значений
        return headers, values
    def getOutputDirectory():
        current_file_path = os.path.abspath(__file__)
        current_directory = os.path.dirname(current_file_path)
        parent_directory = os.path.dirname(current_directory)
        return os.path.join(parent_directory, 'output')

class l1_test:
    def __init__(self):
        dynamicLibrary = CPPDynamicLibrary()
        lib_path = dynamicLibrary.getPathTo("l1_test")
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"Не найден файл DLL по пути: {lib_path}")
        self.lib = ctypes.WinDLL(lib_path)
        self.lib.RK_4.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int]
        self.lib.RK_4.restype = ctypes.c_int

        self.lib.RK_4_adaptive.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.c_int]
        self.lib.RK_4_adaptive.restype = ctypes.c_int
    def rk_4(self, x0: float, y0: float, h:float, xmax:float, maxSteps: int):
        #int RK_4(double x0, double y0, double h, double xmax, int maxSteps)
        code = self.lib.RK_4(x0, y0, h, xmax, maxSteps)
        if code != 0:
            raise Exception("Something went wrong")
        return self.getResult()
    def rk4_adaptive(self, x0: float, y0: float, h0: float, xmax: float, eps: float, eps_out:float, n_max:int):
        code = self.lib.RK_4_adaptive(x0, y0, h0, xmax, eps, eps_out, n_max)
        if code != 0:
            raise Exception("Something went wrong")
        return self.getResult()
    def getResult(self):
        CSVReader = CSVReaderPandas('output_test.csv')
        headers, values = CSVReader.readAsNumpy()
        return headers, values





        