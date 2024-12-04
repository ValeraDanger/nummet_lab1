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
    std::filesystem::path outputPath = executablePath.parent_path() / ".." / ".." / "output" / "output_ksr11.csv";
    return outputPath.string();
}

#define OUT_PATH getOutputPath().c_str()

// Определение функций правой части системы
extern "C" EXPORT
double f1(double x, double y1, double y2, double K, double L) {
    return y2;
}

extern "C" EXPORT
double f2(double x, double y1, double y2, double K, double L) {
    return K * (L - x) * pow(1 + y2 * y2, 1.5);
}


// Метод Рунге-Кутты 4-го порядка (один шаг)
extern "C" EXPORT
void rungeKuttaStep(double& x, double& y1, double& y2, double h, double K, double L) {
    double ky11 = f1(x, y1, y2, K, L);
    double ky21 = f2(x, y1, y2, K, L);

    double ky12 = f1(x + h / 2, y1 + h / 2 * ky11, y2 + h / 2 * ky21, K, L);
    double ky22 = f2(x + h / 2, y1 + h / 2 * ky11, y2 + h / 2 * ky21, K, L);

    double ky13 = f1(x + h / 2, y1 + h / 2 * ky12, y2 + h / 2 * ky22, K, L);
    double ky23 = f2(x + h / 2, y1 + h / 2 * ky12, y2 + h / 2 * ky22, K, L);

    double ky14 = f1(x + h, y1 + h * ky13, y2 + h * ky23, K, L);
    double ky24 = f2(x + h, y1 + h * ky13, y2 + h * ky23, K, L);

    y1 = y1 + h * (ky11 + 2 * ky12 + 2 * ky13 + ky14) / 6;
    y2 = y2 + h * (ky21 + 2 * ky22 + 2 * ky23 + ky24) / 6;

    if (std::isinf(y1) || std::isnan(y1) || std::fabs(y1) > DBL_MAX ||
        std::isinf(y2) || std::isnan(y2) || std::fabs(y2) > DBL_MAX) {
        throw std::overflow_error("Value is NaN. | Value is infinite. | Value exceeds the maximum representable double.");
    }

    x = x + h;
}



extern "C" EXPORT
int rungeKuttaAdaptive(double x0, double y10, double y20, double h0, double maxLength, double K, double L, int maxSteps, double tolerance, double edge) {

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
    
    double currentLength = 0.0; // Текущая длина стержня, для которой уже проведены рассчеты
    bool is_currentLength_more_maxLength = false;

    std::ofstream output(OUT_PATH);
    output << "xi;vi;vi2;v'i;v'i2;vi-vi2;v'i-v'i2;hi;E;E_v;E_v';c1;c2;currentLength_i" << std::endl;


    while (currentLength + h <= maxLength && std::abs(currentLength + h - maxLength) > edge && step < maxSteps) {

        xtmp = x;
        y1tmp = y1;
        y2tmp = y2;

        rungeKuttaStep(x, y1, y2, h, K, L);

        x_half = xtmp;
        y1_half = y1tmp;
        y2_half = y2tmp;
        double h_half = h/2;


        rungeKuttaStep(x_half, y1_half, y2_half, h_half, K, L);
        rungeKuttaStep(x_half, y1_half, y2_half, h_half, K, L);


        s1 = std::abs(y1 - y1_half) / (pow(2, p) - 1);
        s2 = std::abs(y2 - y2_half) / (pow(2, p) - 1);

        error = sqrt(s1 * s1 + s2 * s2);


        if (error < tolerance / pow(2, p + 1)) {
            // Вычисляем длину пройденного участка
            double dx = x - xtmp;
            double dy = y1 - y1tmp;
            double segmentLength = std::sqrt(dx * dx + dy * dy);
            currentLength += segmentLength; // Обновляем текущую длину

            if (currentLength > maxLength) {
                x = xtmp;
                y1 = y1tmp;
                y2 = y2tmp;
                is_currentLength_more_maxLength = true;
                currentLength -= segmentLength;
                break; // Выходим из цикла, если достигли максимальной длины
            }   

            c2++;
            output << x << ";" << y1 << ";" << y1_half << ";" << y2 << ";" << y2_half << ";" << y1 - y1_half << ";" << y2-y2_half << ";" << h << ";" << error * pow(2, p) << ";" << s1 * pow(2, p) << ";" << s2 * pow(2, p) << ";" << c1 << ";" << c2 << ";" << currentLength << std::endl;
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

                rungeKuttaStep(x, y1, y2, h, K, L);
                rungeKuttaStep(x_half, y1_half, y2_half, h_half, K, L);
                rungeKuttaStep(x_half, y1_half, y2_half, h_half, K, L);
            
                s1 = std::abs(y1 - y1_half) / (pow(2, p) - 1);
                s2 = std::abs(y2 - y2_half) / (pow(2, p) - 1);

                error = sqrt(s1 * s1 + s2 * s2);

            }

            // Вычисляем длину пройденного участка
            double dx = x - xtmp;
            double dy = y1 - y1tmp;
            double segmentLength = std::sqrt(dx * dx + dy * dy);
            currentLength += segmentLength; // Обновляем текущую длину

            if (currentLength > maxLength) {
                x = xtmp;
                y1 = y1tmp;
                y2 = y2tmp;
                currentLength -= segmentLength;
                is_currentLength_more_maxLength = true;
                break; // Выходим из цикла, если достигли максимальной длины
            } 
            output << x << ";" << y1 << ";" << y1_half << ";" << y2 << ";" << y2_half << ";" << y1 - y1_half << ";" << y2-y2_half << ";" << h << ";" << error * pow(2, p) << ";" << s1 * pow(2, p) << ";" << s2 * pow(2, p) << ";" << c1 << ";" << c2 << ";" << currentLength << std::endl;
        }
        

		

        step++;

    }

    if (currentLength + h > maxLength || is_currentLength_more_maxLength) {
        bool should_decrease_step = true;
        while (step < maxSteps) {
            step++;
            if(should_decrease_step) {
                h = h/2;
            }
            c1++;
            // Делаем шаг методом Рунге-Кутта с h и два шага с h/2
            xtmp = x;
            y1tmp = y1;
            y2tmp = y2;

            rungeKuttaStep(x, y1, y2, h, K, L);

            x_half = xtmp;
            y1_half = y1tmp;
            y2_half = y2tmp;
            double h_half = h/2;


            rungeKuttaStep(x_half, y1_half, y2_half, h_half, K, L);
            rungeKuttaStep(x_half, y1_half, y2_half, h_half, K, L);

            // Вычисляем длину пройденного участка
            double dx = x - xtmp;
            double dy = y1 - y1tmp;
            double segmentLength = std::sqrt(dx * dx + dy * dy);
            currentLength += segmentLength; // Обновляем текущую длину

            if (currentLength > maxLength) {
                x = xtmp;
                y1 = y1tmp;
                y2 = y2tmp;
                currentLength -= segmentLength;     //Возвращаемся к исходной точке и пересчитываем с уменьшенным шагом
                should_decrease_step = true;
                continue;
            } 
            else if (maxLength - currentLength > edge){         //Сохраняем точку и приближаемся к границе без уменьшения шага
                should_decrease_step = false;
                output << x << ";" << y1 << ";" << y1_half << ";" << y2 << ";" << y2_half << ";" << y1 - y1_half << ";" << y2-y2_half << ";" << h << ";" << error * pow(2, p) << ";" << s1 * pow(2, p) << ";" << s2 * pow(2, p) << ";" << c1 << ";" << c2 << ";" << currentLength << std::endl;
                continue;         
            }
            else {
                output << x << ";" << y1 << ";" << y1_half << ";" << y2 << ";" << y2_half << ";" << y1 - y1_half << ";" << y2-y2_half << ";" << h << ";" << error * pow(2, p) << ";" << s1 * pow(2, p) << ";" << s2 * pow(2, p) << ";" << c1 << ";" << c2 << ";" << currentLength << std::endl;
                break;
            }
        }

    } 

    output.close();
    return 0;
}


int main() {
    setlocale(LC_ALL, "Russian");

    //определяем параметры для функции rungeKuttaAdaptive
    double x0 = 0.0;
    double y10 = 0.0;
    double y20 = 0.0;
    double h0 = 0.001;
    double maxLength = 1.0;
    double K = 2.0;
    double L = 1.0;
    int maxSteps = 10000;
    double tolerance = 1e-7;
    double edge = 1e-6;


    //Вызов rungeKuttaAdaptive с данными переменными
    rungeKuttaAdaptive(x0, y10, y20, h0, maxLength, K, L, maxSteps, tolerance, edge);

    return 0;
}