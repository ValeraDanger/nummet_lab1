#include <fstream>
#include <cmath>
#include <filesystem>
#include <string>

#include <filesystem>

#ifdef _WIN32
#include <Windows.h>
#else
#include <unistd.h>
#include <dlfcn.h>
#include <limits.h> // Для PATH_MAX (Linux/macOS)
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
  HMODULE hModule = GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS | 
                                      GET_MODULE_HANDLE_EX_FLAG_UNCHANGED_REFCOUNT,
                                      (LPCSTR)&getThisLibraryPath, 
                                      &hModule);
  if (hModule != NULL) {
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
    std::filesystem::path outputPath = executablePath.parent_path() / ".."/ ".." / "output" / "output_1.csv";
    return outputPath.string();
}

// Определяем OUT_PATH с использованием функции getOutputPath()
#define OUT_PATH getOutputPath().c_str() 

extern "C" EXPORT
    double f(const double &x, const double &y)
    {
        return pow(y, 2)*x / ( 1+pow(x, 2) ) + y - pow(y, 3)*std::sin(10 * x);
    }


// Метод Рунге-Кутта четвертого порядка
extern "C" EXPORT
    double RK_4_Step(const double &x, const double &y,const double &h)
    {
        double k1 = h * f(x, y);
        double k2 = h * f(x + h / 2, y + k1 / 2);
        double k3 = h * f(x + h / 2, y + k2 / 2);
        double k4 = h * f(x + h, y + k3);

        double y_next = y + (k1 + 2 * k2 + 2 * k3 + k4) / 6;

        if (std::isinf(y_next) || std::isnan(y_next) || std::fabs(y_next) > std::numeric_limits<double>::max()) { 
            throw std::overflow_error("Value is NaN. | Value is infinite. | Value exceeds the maximum representable double.");
        }

        return y_next;
    }


extern "C" EXPORT
    int RK_4(double x0, double y0, double h, double xmax, int maxSteps)
    {
        int steps = 0;
        double x = x0;
        double y = y0;
        std::ofstream output(OUT_PATH);

        output << "xi;vi" << std::endl;   // Заголовок CSV
        while (x < xmax && steps < maxSteps) {

            y = RK_4_Step(x, y, h);
            x = x + h;  //Увеличиваем шаг перед выводом, т.к. метод Р.К. считает значение в следующей точке

            output << x << ";" << y << std::endl;

            ++steps;
        }
        return 0;
    }


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

        std::ofstream output(OUT_PATH);

        output << "xi;vi;v2i;vi-v2i;E;hi;c1;c2" << std::endl; // Заголовок CSV
        
        while ((x + h) < xmax && std::abs(x + h - xmax)>eps_out && step < Nmax)
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


        output.close();
    return 0;
    }


int main()
{
    setlocale(LC_ALL, "Russian");
    double x0 = 0.;            // Начальная точка x
    double y0 = 1.0;            // Начальное значение y
    double h0 = 0.00001;            // Начальный размер шага
    double xmax = 20.0;          // Граница x
    double tolerance = 1e-6;   // Заданная точность
    double edge = 0.001;
    int maxSteps = 1000;         // Максимальное количество шагов

    //RK_4_adaptive(x0, y0, h0, xmax, tolerance, edge,maxSteps);
    //RK_4(x0, y0, h0, xmax, maxSteps);

    return 0;
}