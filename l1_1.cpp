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
    std::filesystem::path outputPath = executablePath.parent_path() / ".." / ".." / "output" / "output_1.csv";
    return outputPath.string();
}



// Константы, используемые в программе
// X0 - начальное значение x
// Y0 - начальное значение y
// H0 - начальный шаг
// XMAX - конечное значение x
// EPS - точность вычислений
// EPS_OUT - точность выхода
// NMAX - максимальное число шагов

const double X0 = 0.0;
const double Y0 = 1.0;
const double H0 = 0.01;
const double XMAX = 0.4;
const double EPS = 1e-15;
const double EPS_OUT = 1e-3;
const int NMAX = 10000;


// Args:
//     x - значение независимой переменной (double)
//     y - значение зависимой переменной (double)
// Returns:
//     Значение функции f(x, y) (double)
extern "C" EXPORT
    double f(const double &x, const double &y)
    {
        return pow(y, 2)*x / ( 1+pow(x, 2) ) + y - pow(y, 3)*std::sin(10 * x);
    }



// Метод Рунге-Кутта четвертого порядка
// Args:
//     x - значение независимой переменной (double)
//     y - значение зависимой переменной (double)
//     h - размер шага (double)
// Returns:
//     Значение y на следующем шаге (double)
extern "C" EXPORT
    double RK_4_Step(const double &x, const double &y,const double &h)
    {
        double k1 = h * f(x, y);
        double k2 = h * f(x + h / 2, y + k1 / 2);
        double k3 = h * f(x + h / 2, y + k2 / 2);
        double k4 = h * f(x + h, y + k3);

        double y_next = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6;

        if (std::isinf(y_next) || std::isnan(y_next) || std::fabs(y_next) > DBL_MAX) { 
            throw std::overflow_error("Value is NaN. | Value is infinite. | Value exceeds the maximum representable double.");
        }

        return y_next;
    }



// Args:
//     x0 - начальное значение x (double)
//     y0 - начальное значение y (double)
//     h - размер шага (double)
//     xmax - конечное значение x (double)
//     maxSteps - максимальное число шагов (int)
// Returns:
//     0 - если вычисления прошли успешно.
extern "C" EXPORT
    int RK_4(double x0, double y0, double h, double xmax, int maxSteps)
    {
        int steps = 0;
        double x = x0;
        double y = y0;
        std::ofstream output(getOutputPath().c_str());

        output << "xi;vi" << std::endl;   // Заголовок CSV
        while (x+h <= xmax && steps < maxSteps) {

            y = RK_4_Step(x, y, h);
            x = x + h;  //Увеличиваем шаг перед выводом, т.к. метод Р.К. считает значение в следующей точке

            output << x << ";" << y << std::endl;

            ++steps;
        }
        return 0;
    }

// Args:
//     x0 - начальное значение x (double)
//     y0 - начальное значение y (double)
//     h0 - начальный размер шага (double)
//     xmax - конечное значение x (double)
//     eps - заданная точность (double)
//     eps_out -  точность выхода (double)
//     Nmax - максимальное число шагов (int)
// Returns:
//     0 - если вычисления прошли успешно
extern "C" EXPORT
    int RK_4_adaptive(double x0, double y0, double h0, double xmax, double eps, double eps_out, int Nmax)
    {
        double x = x0;
        double y = y0;
        double h = h0;
        double y1;
        double y2;
        int c1 = 0;
        int c2 = 0;
        int step = 0;
        double error = 0.;
        int p = 4;

        std::ofstream output(getOutputPath().c_str());

        output << "xi;vi;v2i;vi-v2i;E;hi;c1;c2" << std::endl; // Заголовок CSV
        
        while ((x + h) <= xmax && std::abs(x - xmax)>eps_out && step < Nmax)
        {
            
            // Делаем шаг методом Рунге-Кутта с h и два шага с h/2
            y1 = RK_4_Step(x, y, h);
            y2 = RK_4_Step(x, y, h / 2.);
            y2 = RK_4_Step(x + h / 2., y2, h / 2.);

            // Вычисляем оценку локальной погрешности
            error = (std::abs(y1 - y2))/(pow(2., p) - 1.);     //2^p-1 - знаменатель в формуле вычисления О.Л.П
            // Проверяем, соответствует ли оценка погрешности заданной точности
            if (error > eps)
            {
                h=h/2.;
                ++step;
                c1 += 1;        
            }
            else if(error < eps / pow(2, p + 1))     //2^(p+1)
            {
                y = y1;
                x += h;     //Увеличиваем шаг перед выводом, т.к. метод Р.К. считает значение в следующей точке
                c2++;

                //2^p
                output << x << ";" << y << ";" << y2 << ";" << y-y2 << ";" << error * pow(2, p) << ";" << h << ";" << c1 << ";" << c2 << std::endl;
                h*=2;
                ++step;
            }
            else
            {
                y = y1;
                x += h;

                //2^p
                output << x << ";" << y << ";" << y2 << ";" << y-y2 << ";" << error * pow(2, p) << ";" << h << ";" << c1 << ";" << c2 << std::endl;
                ++step;
            }
        }

        if (x + h > xmax)
        {
            h = xmax - x;
            //++c1;
            // Делаем шаг методом Рунге-Кутта с h и два шага с h/2
            y1 = RK_4_Step(x, y, h);
            y2 = RK_4_Step(x, y, h / 2);
            y2 = RK_4_Step(x + h / 2, y2, h / 2);

            output << x+h << ";" << y1 << ";" << y2 << ";" << y1-y2 << ";" << error * pow(2, p) << ";" << h << ";" << c1 << ";" << c2 << std::endl;

        }


        output.close();
    return 0;
    }


int main()
{
    setlocale(LC_ALL, "Russian");

    //RK_4_adaptive(X0, Y0, H0, XMAX, EPS, EPS_OUT, NMAX);
    //RK_4(X0, Y0, H0, XMAX, EPS, EPS_OUT, NMAX);


    return 0;
}