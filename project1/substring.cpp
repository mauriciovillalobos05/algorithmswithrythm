#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <chrono>
#include <unordered_set>
#include <iomanip>
#include <cctype>

using namespace std;

const unordered_set<string> stopwords = {
    "the","be","to","of","and","a","in","that","have","i",
    "it","for","not","on","with","he","as","you","do","at",
    "this","but","his","by","from","they","we","say","her","she",
    "or","an","will","my","one","all","would","there","their",
    "what","so","up","out","if","about","who","get","which","go",
    "me","when","make","can","like","time","no","just","him","know",
    "take","into","year","your","some","could","them","see","other",
    "than","then","now","look","only","come","its","over","think",
    "also","back","after","use","two","how","our","work","first",
    "well","way","even","new","want","because","any","these","give",
    "day","most","us","is","was","are","been","has","had","were",
    "said","did","having","may","should","am","being"
};

string normalizeText(const string& text) {
    string normalized;

    for (char c : text) {
        if (isalpha(static_cast<unsigned char>(c))) {
            normalized += static_cast<char>(tolower(static_cast<unsigned char>(c)));
        } else if (isspace(static_cast<unsigned char>(c))) {
            normalized += ' ';
        }
    }

    string result;
    string current_word;

    for (char c : normalized) {
        if (c == ' ') {
            if (!current_word.empty()) {
                if (stopwords.find(current_word) == stopwords.end()) {
                    result += current_word + " ";
                }
                current_word.clear();
            }
        } else {
            current_word += c;
        }
    }

    if (!current_word.empty()) {
        if (stopwords.find(current_word) == stopwords.end()) {
            result += current_word + " ";
        }
    }

    if (!result.empty() && result.back() == ' ') {
        result.pop_back();
    }

    return result;
}

string lcSub(const string& s, const string& t) {
    int m = s.size(), n = t.size();
    if (m == 0 || n == 0) return "";

    vector<vector<int>> dp(2, vector<int>(n + 1, 0));
    int max_length = 0, end_index = 0;

    for (int i = 1; i <= m; ++i) {
        for (int j = 1; j <= n; ++j) {
            if (s[i - 1] == t[j - 1]) {
                dp[1][j] = dp[0][j - 1] + 1;
                if (dp[1][j] > max_length) {
                    max_length = dp[1][j];
                    end_index = i;
                }
            } else {
                dp[1][j] = 0;
            }
        }
        dp[0] = dp[1];
        fill(dp[1].begin(), dp[1].end(), 0);
    }

    if (max_length == 0) return "";
    return s.substr(end_index - max_length, max_length);
}

double calculateSimilarity(int lcs_length, int text1_size, int text2_size) {
    int min_size = min(text1_size, text2_size);
    if (min_size == 0) return 0.0;
    return (double)lcs_length / min_size * 100.0;
}

void printFragment(const string& fragment, int max_chars = 200) {
    if (fragment.empty()) {
        cout << "(no se encontró substring común)\n";
        return;
    }

    if (static_cast<int>(fragment.size()) <= max_chars) {
        cout << "'" << fragment << "'\n";
    } else {
        cout << "'" << fragment.substr(0, max_chars) << "...'\n";
        cout << "(fragmento truncado - mostrando primeros " << max_chars << " caracteres)\n";
    }
}

void search_in_file(const string& file1, const string& file2) {
    ifstream f1(file1), f2(file2);

    if (!f1.is_open() || !f2.is_open()) {
        cerr << "Error al abrir los archivos.\n";
        return;
    }

    string text1((istreambuf_iterator<char>(f1)), istreambuf_iterator<char>());
    string text2((istreambuf_iterator<char>(f2)), istreambuf_iterator<char>());

    cout << "          ANÁLISIS DE LONGEST COMMON SUBSTRING (LCS)           \n\n";

    cout << " ESTADÍSTICAS DE TEXTOS ORIGINALES \n";
    cout << "Archivo 1: " << file1 << "\n";
    cout << "  Tamaño: " << text1.size() << " caracteres\n";
    cout << "Archivo 2: " << file2 << "\n";
    cout << "  Tamaño: " << text2.size() << " caracteres\n\n";

    cout << "ANÁLISIS CON NORMALIZACIÓN (sin stopwords)\n\n";

    auto norm_start = chrono::high_resolution_clock::now();
    string normalized1 = normalizeText(text1);
    string normalized2 = normalizeText(text2);
    auto norm_end = chrono::high_resolution_clock::now();
    chrono::duration<double> norm_duration = norm_end - norm_start;

    cout << "Preprocesamiento completado:\n";
    cout << "  Texto 1: " << normalized1.size() << " caracteres (reducción: "
         << fixed << setprecision(2)
         << ((1.0 - static_cast<double>(normalized1.size()) / max(1.0, static_cast<double>(text1.size()))) * 100.0) << "%)\n";
    cout << "  Texto 2: " << normalized2.size() << " caracteres (reducción: "
         << ((1.0 - static_cast<double>(normalized2.size()) / max(1.0, static_cast<double>(text2.size()))) * 100.0) << "%)\n";
    cout << "  Tiempo de normalización: " << norm_duration.count() << " segundos\n\n";

    auto start1 = chrono::high_resolution_clock::now();
    string lcs_normalized = lcSub(normalized1, normalized2);
    auto end1 = chrono::high_resolution_clock::now();
    chrono::duration<double> duration1 = end1 - start1;

    int lcs_norm_length = static_cast<int>(lcs_normalized.size());
    double similarity_norm = calculateSimilarity(lcs_norm_length, static_cast<int>(normalized1.size()), static_cast<int>(normalized2.size()));

    cout << "RESULTADOS:\n";
    cout << "  Longitud del LCS: " << lcs_norm_length << " caracteres\n";
    cout << "  Porcentaje de similitud: " << fixed << setprecision(2)
         << similarity_norm << "%\n";
    cout << "  Tiempo de ejecución LCS: " << duration1.count() << " segundos\n";
    cout << "  Tiempo total (normalización + LCS): "
         << (norm_duration.count() + duration1.count()) << " segundos\n\n";

    cout << "  Fragmento encontrado:\n  ";
    printFragment(lcs_normalized);
    cout << "\n";

    cout << "                      CONCLUSIONES                           \n\n";

    if (lcs_norm_length < 50) {
        cout << " Los textos comparten principalmente PEQUEÑAS COINCIDENCIAS (post-normalización).\n";
        cout << "  El substring común más largo tiene solo " << lcs_norm_length
             << " caracteres, lo que\n  indica que no hay frases largas idénticas entre los documentos.\n\n";
    } else if (lcs_norm_length < 200) {
        cout << " Los textos comparten COINCIDENCIAS MODERADAS (post-normalización).\n";
        cout << "  Se encontraron fragmentos comunes de " << lcs_norm_length
             << " caracteres.\n\n";
    } else {
        cout << " Los textos comparten FRASES LARGAS IDÉNTICAS (post-normalización).\n";
        cout << "  El substring común más largo tiene " << lcs_norm_length
             << " caracteres, lo que\n  indica coincidencias significativas.\n\n";
    }

    cout << "Porcentaje de similitud:\n";
    cout << "  Con " << fixed << setprecision(2) << similarity_norm
         << "\% de similitud (calculado sobre el texto normalizado),\n";
    if (similarity_norm < 1.0) {
        cout << "  los textos son prácticamente INDEPENDIENTES.\n";
    } else if (similarity_norm < 5.0) {
        cout << "  los textos tienen BAJA similitud.\n";
    } else {
        cout << "  los textos tienen similitud notable.\n";
    }

}

int main() {
    search_in_file("littleWoman.txt", "prideAndPrejudice.txt");
    return 0;
}