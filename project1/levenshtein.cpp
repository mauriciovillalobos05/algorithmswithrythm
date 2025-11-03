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
    normalized.reserve(text.size());

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

    if (!current_word.empty() && stopwords.find(current_word) == stopwords.end()) {
        result += current_word + " ";
    }

    if (!result.empty() && result.back() == ' ')
        result.pop_back();

    return result;
}

double levenshteinDistance(const string& s, const string& t) {
    const int m = s.size();
    const int n = t.size();

    if (m == 0) return n;
    if (n == 0) return m;

    const string* a = &s;
    const string* b = &t;
    if (n < m) swap(a, b);

    int len1 = a->size();
    int len2 = b->size();

    vector<int> prev(len1 + 1), curr(len1 + 1);

    for (int i = 0; i <= len1; ++i)
        prev[i] = i;

    for (int j = 1; j <= len2; ++j) {
        curr[0] = j;
        for (int i = 1; i <= len1; ++i) {
            int cost = ((*a)[i - 1] == (*b)[j - 1]) ? 0 : 1;
            curr[i] = min({ prev[i] + 1, curr[i - 1] + 1, prev[i - 1] + cost });
        }
        swap(prev, curr);
    }

    return prev[len1];
}

pair<double, double> calculateLevenshteinSimilarity(const string& s, const string& t) {
    int maxLen = max(s.size(), t.size());
    if (maxLen == 0) return {100.0, 0.0};

    double dist = levenshteinDistance(s, t);
    double sim = (1.0 - static_cast<double>(dist) / maxLen) * 100.0;
    if (sim < 0) sim = 0.0;
    return {sim, dist};
}

void search_in_file(const string& file1, const string& file2) {
    ifstream f1(file1), f2(file2);
    if (!f1.is_open() || !f2.is_open()) {
        cerr << "Error al abrir los archivos.\n";
        return;
    }

    string text1((istreambuf_iterator<char>(f1)), istreambuf_iterator<char>());
    string text2((istreambuf_iterator<char>(f2)), istreambuf_iterator<char>());

    cout << "          ANÁLISIS DE SIMILITUD - DISTANCIA DE EDICIÓN (LEVENSHTEIN OPTIMIZADA)           \n\n";

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

    auto start = chrono::high_resolution_clock::now();
    auto [similarity, dist] = calculateLevenshteinSimilarity(normalized1, normalized2);
    auto end = chrono::high_resolution_clock::now();
    chrono::duration<double> duration = end - start;

    cout << "RESULTADOS:\n";
    cout << "  Porcentaje de similitud (Levenshtein): " << fixed << setprecision(2)
         << similarity << "%\n";
    cout << "  Distancia de edición: " << dist << "\n";
    cout << "  Tiempo de ejecución: " << duration.count() << " segundos\n";
    cout << "  Tiempo total (normalización + comparación): "
         << (norm_duration.count() + duration.count()) << " segundos\n";
    cout << "  Nota: Este método no busca el substring común más largo, "
            "sino que mide cuántas ediciones son necesarias para convertir un texto en otro.\n\n";

    cout << "                      CONCLUSIONES                           \n\n";

    if (similarity < 5.0) {
        cout << " Los textos son PRÁCTICAMENTE DIFERENTES.\n";
    } else if (similarity < 25.0) {
        cout << " Los textos tienen POCA similitud.\n";
    } else if (similarity < 60.0) {
        cout << " Los textos muestran SIMILITUD MODERADA.\n";
    } else {
        cout << " Los textos son ALTAMENTE SIMILARES o derivados uno del otro.\n";
    }
}

int main() {
    search_in_file("littleWoman.txt", "prideAndPrejudice.txt");
    return 0;
}