#include <fstream>
#include <cmath>
#include <filesystem>
#include <string>
#include <limits>
#include <filesystem>

#include <cfloat> // Для DBL_MAX

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#include <dlfcn.h>
//#include <limits.h> // Для PATH_MAX (Linux/macOS)
#endif

#ifdef _WIN64  // Проверка на 64-битную версию Windows
#define EXPORT __declspec(dllexport)
#elif defined(_WIN32)  // Проверка на 32-битную версию Windows
#define EXPORT __declspec(dllexport)
#else
#define EXPORT __attribute__((visibility("default")))
#endif

// Получаем абсолютный путь к DLL/so/dylib, в которой находится эта функция
EXPORT std::filesystem::path getThisLibraryPath() {
#ifdef _WIN32
    HMODULE hModule;
    BOOL success = GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS |
        GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
        (LPCSTR)&getThisLibraryPath,
        &hModule);
    if (success) {
        char buffer[MAX_PATH];
        GetModuleFileNameA(hModule, buffer, MAX_PATH);
        return std::filesystem::path(buffer);
    }
#else
    Dl_info info;
    if (dladdr((void*)&getThisLibraryPath, &info) != 0) {
        return std::filesystem::path(info.dli_fname);
    }
#endif
    return ""; // Возвращаем пустой путь в случае ошибки
}



// Формируем абсолютный путь к output
EXPORT std::string getOutputPath() {
    std::filesystem::path executablePath = getThisLibraryPath();
    std::filesystem::path outputPath = executablePath.parent_path() / ".." / ".." / "output" / "output_2.csv";
    return outputPath.string();
}

#define OUT_PATH getOutputPath().c_str()


const double X0 = 0.0;
const double Y10 = 0.0;
const double Y20 = 1.0;
const double H0 = 0.1;
const double XMAX = 10.435634972918;
const double A = 1.0;
const double B = 1.0;
const int MAX_STEPS = 1000;
const double TOLERANCE = 1e-7;
const double EDGE = 1e-7;


// Определение функций правой части системы
// Args:
//    x - текущее значение x (double)
//    y1 - текущее значение y1 (double)
//    y2 - текущее значение y2 (double)
//    a - параметр системы уравнений (double)
//    b - параметр системы уравнений (double)
// Returns:
//    Значение функции f1 (double)
extern "C" EXPORT
double f1(double x, double y1, double y2, double a, double b) {
    return y2;
}



// Args:
//    x - текущее значение x (double)
//    y1 - текущее значение y1 (double)
//    y2 - текущее значение y2 (double)
//    a - параметр системы уравнений (double)
//    b - параметр системы уравнений (double)
// Returns:
//    Значение функции f2 (double)
extern "C" EXPORT
double f2(double x, double y1, double y2, double a, double b) {
    return -a*y2 + b*sin(y1);
}


// Метод Рунге-Кутты 4-го порядка (один шаг)
// Args:
//    x - текущее значение x (double, передается по ссылке)
//    y1 - текущее значение y1 (double, передается по ссылке)
//    y2 - текущее значение y2 (double, передается по ссылке)
//    h -  размер шага (double)
//    a - параметр системы уравнений (double)
//    b - параметр системы уравнений (double)
// Returns:
//     void (результат записывается в x, y1, y2)
extern "C" EXPORT
void rungeKuttaStep(double& x, double& y1, double& y2, double h, double a, double b) {
    double ky11 = f1(x, y1, y2, a, b);
    double ky21 = f2(x, y1, y2, a, b);

    double ky12 = f1(x + h / 2, y1 + h / 2 * ky11, y2 + h / 2 * ky21, a, b);
    double ky22 = f2(x + h / 2, y1 + h / 2 * ky11, y2 + h / 2 * ky21, a, b);

    double ky13 = f1(x + h / 2, y1 + h / 2 * ky12, y2 + h / 2 * ky22, a, b);
    double ky23 = f2(x + h / 2, y1 + h / 2 * ky12, y2 + h / 2 * ky22, a, b);

    double ky14 = f1(x + h, y1 + h * ky13, y2 + h * ky23, a, b);
    double ky24 = f2(x + h, y1 + h * ky13, y2 + h * ky23, a, b);

    y1 = y1 + h * (ky11 + 2 * ky12 + 2 * ky13 + ky14) / 6;
    y2 = y2 + h * (ky21 + 2 * ky22 + 2 * ky23 + ky24) / 6;

    if (std::isinf(y1) || std::isnan(y1) || std::fabs(y1) > DBL_MAX ||
        std::isinf(y2) || std::isnan(y2) || std::fabs(y2) > DBL_MAX) {
        throw std::overflow_error("Value is NaN. | Value is infinite. | Value exceeds the maximum representable double.");
    }

    x = x + h;
}


// Метод Рунге-Кутты 4-го порядка без контроля локальной погрешности
// Args:
//     x0 - начальное значение x (double)
//     y10 - начальное значение y1 (double)
//     y20 - начальное значение y2 (double)
//     h - размер шага (double)
//     xmax - конечное значение x (double)
//     a - параметр системы уравнений (double)
//     b - параметр системы уравнений (double)
//     maxSteps - максимальное число шагов (int)
// Returns:
//     0 - если вычисления прошли успешно.
extern "C" EXPORT
int rungeKutta(double x0, double y10, double y20, double h, double xmax, double a, double b, int maxSteps) {
    double x = x0;
    double y1 = y10;
    double y2 = y20;

    std::ofstream output(OUT_PATH);
    output << "xi;vi1;vi2" << std::endl;  // Заголовок CSV

    int step = 0;
    while (x+h <= xmax && step < maxSteps) {
        rungeKuttaStep(x, y1, y2, h, a, b);

        output << x << ";" << y1 << ";" << y2 << std::endl; // Вывод с разделителем ;
        step++;
    }

    output.close();
    return 0;
}


// Args:
//     x0 - начальное значение x (double)
//     y10 - начальное значение y1 (double)
//     y20 - начальное значение y2 (double)
//     h0 - начальный размер шага (double)
//     xmax - конечное значение x (double)
//     a - параметр системы уравнений (double)
//     b - параметр системы уравнений (double)
//     maxSteps - максимальное число шагов (int)
//     tolerance -  параметр контроля локальной погрешности (double)
//     edge - эпсилон граничное (double)
// Returns:
//     0 - если вычисления прошли успешно
extern "C" EXPORT
int rungeKuttaAdaptive(double x0, double y10, double y20, double h0, double xmax, double a, double b, int maxSteps, double tolerance, double edge) {

    double x = x0;
    double y1 = y10;
    double y2 = y20;
    double h = h0;

    double xtmp, y1tmp, y2tmp;  // Для временного хранения значений
    double x_half, y1_half, y2_half;


    int c1 = 0;
    int c2 = 0;
    int step = 0;
    double error = 0.0;
    double s1, s2;
    int p = 4;


    std::ofstream output(OUT_PATH);
    output << "xi;vi;vi2;v'i;v'i2;vi-vi2;v'i-v'i2;hi;E;E_v;E_v';c1;c2" << std::endl;


    while (x + h <= xmax && std::abs(x - xmax) > edge && step < maxSteps) {

        xtmp = x;
        y1tmp = y1;
        y2tmp = y2;

        rungeKuttaStep(x, y1, y2, h, a, b);

        x_half = xtmp;
        y1_half = y1tmp;
        y2_half = y2tmp;
        double h_half = h/2;


        rungeKuttaStep(x_half, y1_half, y2_half, h_half, a, b);
        rungeKuttaStep(x_half, y1_half, y2_half, h_half, a, b);


        s1 = std::abs(y1 - y1_half) / (pow(2, p) - 1);
        s2 = std::abs(y2 - y2_half) / (pow(2, p) - 1);

        error = sqrt(s1 * s1 + s2 * s2);


        if (error < tolerance / pow(2, p + 1)) {
            c2++;
            output << x << ";" << y1 << ";" << y1_half << ";" << y2 << ";" << y2_half << ";" << y1 - y1_half << ";" << y2-y2_half << ";" << h << ";" << error * pow(2, p) << ";" << s1 * pow(2, p) << ";" << s2 * pow(2, p) << ";" << c1 << ";" << c2 << std::endl;
            h *= 2;
        } else  {
            while (error > tolerance) {

                c1++;

                x = xtmp;
                y1 = y1tmp;
                y2 = y2tmp;
                h /= 2;

                x_half = xtmp;
                y1_half = y1tmp;
                y2_half = y2tmp;
                h_half = h/2;

                rungeKuttaStep(x, y1, y2, h, a, b);
                rungeKuttaStep(x_half, y1_half, y2_half, h_half, a, b);
                rungeKuttaStep(x_half, y1_half, y2_half, h_half, a, b);
            
                s1 = std::abs(y1 - y1_half) / (pow(2, p) - 1);
                s2 = std::abs(y2 - y2_half) / (pow(2, p) - 1);

                error = sqrt(s1 * s1 + s2 * s2);

            }

            output << x << ";" << y1 << ";" << y1_half << ";" << y2 << ";" << y2_half << ";" << y1 - y1_half << ";" << y2-y2_half << ";" << h << ";" << error * pow(2, p) << ";" << s1 * pow(2, p) << ";" << s2 * pow(2, p) << ";" << c1 << ";" << c2 << std::endl;
        }
        

		

        step++;

    }

    if (x + h > xmax)
    {
        h = xmax - x;
        //++c1;
        // Делаем шаг методом Рунге-Кутта с h и два шага с h/2
        xtmp = x;
        y1tmp = y1;
        y2tmp = y2;

        rungeKuttaStep(x, y1, y2, h, a, b);

        x_half = xtmp;
        y1_half = y1tmp;
        y2_half = y2tmp;
        double h_half = h/2;


        rungeKuttaStep(x_half, y1_half, y2_half, h_half, a, b);
        rungeKuttaStep(x_half, y1_half, y2_half, h_half, a, b);

        output << x << ";" << y1 << ";" << y1_half << ";" << y2 << ";" << y2_half << ";" << y1 - y1_half << ";" << y2-y2_half << ";" << h << ";" << error * pow(2, p) << ";" << s1 * pow(2, p) << ";" << s2 * pow(2, p) << ";" << c1 << ";" << c2 << std::endl;

    } 

    output.close();
    return 0;
}


int main() {
    setlocale(LC_ALL, "Russian");

    //rungeKuttaAdaptive(X0, Y10, Y20, H0, XMAX, A, B, MAX_STEPS, TOLERANCE, EDGE);
    //rungeKutta(X0, Y10, Y20, H0, XMAX, A, B, MAX_STEPS, TOLERANCE, EDGE);

    return 0;
}