#include <fstream>
#include <cmath>
#include <string>
#include <limits> // Для std::numeric_limits

#define OUT_PATH "output/output_2.csv"

#ifdef _WIN64  // Проверка на 64-битную версию Windows
    #define EXPORT __declspec(dllexport)
#elif defined(_WIN32)  // Проверка на 32-битную версию Windows
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif

// Определение функций правой части системы
extern "C" {
double f1(double x, double y1, double y2, double a, double b) {
    return y2;
}

double f2(double x, double y1, double y2, double a, double b) {
    return -a*y2 + b*sin(y1);
}
}

// Метод Рунге-Кутты 4-го порядка (один шаг)
extern "C" {
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

    if (std::isinf(y1) || std::isnan(y1) || std::fabs(y1) > std::numeric_limits<double>::max() ||
        std::isinf(y2) || std::isnan(y2) || std::fabs(y2) > std::numeric_limits<double>::max()) {
        throw std::overflow_error("Value is NaN. | Value is infinite. | Value exceeds the maximum representable double.");
    }

    x = x + h;
}
}

// Метод Рунге-Кутты 4-го порядка без контроля локальной погрешности
extern "C" EXPORT
int rungeKutta(double x0, double y10, double y20, double h, double xmax, double a, double b, int maxSteps) {
    double x = x0;
    double y1 = y10;
    double y2 = y20;

    std::ofstream output(OUT_PATH);
    output << "xi;vi1;vi2" << std::endl;  // Заголовок CSV

    int step = 0;
    while (x < xmax && step < maxSteps) {
        rungeKuttaStep(x, y1, y2, h, a, b);

        output << x << ";" << y1 << ";" << y2 << std::endl; // Вывод с разделителем ;
        step++;
    }

    output.close();
    return 0;
}



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


    while (x + h < xmax && std::abs(x + h - xmax) > edge && step < maxSteps) {

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

    output.close();
    return 0;
}


int main() {
    setlocale(LC_ALL, "Russian");

    //определяем параметры для функции rungeKuttaAdaptive
    double x0 = 0.0;
    double y10 = 0.0;
    double y20 = 1.0;
    double h0 = 0.001;
    double xmax = 1000.0;
    double a = 1.0;
    double b = 1.0;
    int maxSteps = 1000;
    double tolerance = 1e-7;
    double edge = 1e-7;


    //Вызов rungeKuttaAdaptive с данными переменными
    //rungeKuttaAdaptive(x0, y10, y20, h0, xmax, a, b, maxSteps, tolerance, edge);
    //rungeKutta(x0, y10, y20, h0, xmax, a, b, maxSteps);

    return 0;
}