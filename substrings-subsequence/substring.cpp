#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <regex>
#include <algorithm>
#include <chrono>
using namespace std;

string lcSub(string s, string t) {
    transform(s.begin(), s.end(), s.begin(), ::tolower);
    transform(t.begin(), t.end(), t.begin(), ::tolower);

    int m = s.size(), n = t.size();
    vector<vector<int>> dp(2, vector<int>(n + 1, 0));
    int max_length = 0, end_index = 0;

    for (int i = 1; i <= m; i++) {
        for (int j = 1; j <= n; j++) {
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

    if (max_length == 0) return "no common substring";
    return s.substr(end_index - max_length, max_length);
}

void search_in_file(const string& file1, const string& file2) {
    ifstream f1(file1), f2(file2);
    if (!f1.is_open() || !f2.is_open()) {
        cerr << "Error opening files.\n";
        return;
    }

    string text1((istreambuf_iterator<char>(f1)), istreambuf_iterator<char>());
    string text2((istreambuf_iterator<char>(f2)), istreambuf_iterator<char>());

    auto start = chrono::high_resolution_clock::now();
    string longest_common = lcSub(text1, text2);
    auto end = chrono::high_resolution_clock::now();

    chrono::duration<double> duration = end - start;
    cout << "Longest common substring: '" << longest_common << "' (length of) " << longest_common.size() <<"\n";
    cout << "Tiempo: " << duration.count() << " segundos\n";
}

int main() {
    search_in_file("frankenstein.txt", "ethics.txt");
    return 0;
}