#include <fstream>
#include <iostream>
#include <cmath>

#define OUT_PATH "output/output_test.csv"
#ifdef _WIN64  // Проверка на 64-битную версию Windows
    #define EXPORT __declspec(dllexport)
#elif defined(_WIN32)  // Проверка на 32-битную версию Windows
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT __attribute__((visibility("default")))
#endif

extern "C" {
    double f(const double &x, const double &y) {
        return y;                                           //Ввод функции
    }
}

extern "C" {
    double u(const double &x, const double &C)
    {
        return C * (std::exp(x));
    }
}

// Метод Рунге-Кутта четвертого порядка
extern "C" {
double RK_4_Step(const double &x, const double &y,const double &h)
{
    double k1 = h * f(x, y);
    double k2 = h * f(x + h / 2., y + k1 / 2.);
    double k3 = h * f(x + h / 2., y + k2 / 2.);
    double k4 = h * f(x + h, y + k3);

    double y_next = y + (k1 + 2. * k2 + 2. * k3 + k4) / 6.;

    if (std::isinf(y_next) || std::isnan(y_next) || std::fabs(y_next) > std::numeric_limits<double>::max()) { 
        throw std::overflow_error("Value is NaN. | Value is infinite. | Value exceeds the maximum representable double.");
    }

    return y_next;
}
}

extern "C" EXPORT
int RK_4(double x0, double y0, double h, double xmax, int Nmax)
{
    int step = 0;
    double x = x0;
    double y = y0;

    std::ofstream output(OUT_PATH);
    output << "x;v;u" << std::endl;     // Заголовок CSV с разделителем ;
    while (x + h <= xmax && step < Nmax) {
        y = RK_4_Step(x, y, h);
        x = x + h;

        output << x << ";" << y << ";" << u(x, y0) << std::endl;
        ++step;
    }

    return 0;
}


extern "C"  EXPORT
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
 
    // Заголовок CSV с разделителем ;
    output << "x;v;v2i;v-v2i;E;h;c1;c2;u;|ui-vi|" << std::endl;

    while (x + h < xmax && std::abs(x + h - xmax) > eps_out && step < Nmax) {

        // Делаем шаг методом Рунге-Кутта с h и два шага с h/2
        y1 = RK_4_Step(x, y, h);
        y2 = RK_4_Step(x, y, h / 2);
        y2 = RK_4_Step(x + h / 2, y2, h / 2);

        // Вычисляем оценку локальной погрешности
        error = (std::abs(y1 - y2)) / (pow(2, p) - 1);     //2^p-1 - знаменатель в формуле вычисления О.Л.П

        // Проверяем, соответствует ли оценка погрешности заданной точности
        if (error > eps) {
            h=h/2;
            ++step;
            c1++;
        }
        else if( error < eps / pow(2, p + 1) ) {  //2^(p+1)
            y = y1;
            x += h;  //Увеличиваем шаг перед выводом, т.к. метод Р.К. считает значение в следующей точке
            c2++;

            //2^p
            output << x << ";" << y << ";" << y2 << ";" << y-y2 << ";" << error * pow(2, p) << ";" << h << ";" << c1 << ";" << c2 << ";" << u(x, y0) << ";" << std::fabs(u(x, y0) - y) << std::endl;
            
            h *= 2;
            ++step;
  
        }
        else {
            y = y1;
            x += h;  //Увеличиваем шаг перед выводом, т.к. метод Р.К. считает значение в следующей точке
            //2^p
            output << x << ";" << y << ";" << y2 << ";" << y-y2 << ";" << error * pow(2, p) << ";" << h << ";" << c1 << ";" << c2 << ";" << u(x, y0) << ";" << std::fabs(u(x, y0) - y) << std::endl;
            
            
            ++step;
        }
    }




    output.close();

return 0;
}

int main()
{
    setlocale(LC_ALL, "Russian");
    double x0 = 0.0;     
    double y0 = 1.0;         
    double h0 = 0.1;          
    double xmax = 20.0;   
    double tolerance = 1e-6; 
    double edge = 0.1;
    int maxSteps = 1000;

    //RK_4_adaptive(x0, y0, h0, xmax, tolerance, edge, maxSteps);
    // RK_4(x0, y0, h0, xmax, maxSteps);

    return 0;
}