// clang-format off
#pragma once

#include <iostream>
#include <iomanip>
#include <vector>
#include <random>
#include <algorithm>

using std::vector, std::cout, std::endl;

// -----------------------------------------------------------------------
// MARK: Utility
// -----------------------------------------------------------------------

// /**
//  * fill_slice: sets arr[idx] = new_value if in range.
//  */
// template <typename T>
// inline vector<T> &fill_slice(
//         vector<T> &arr,
//         int idx_from,
//         int idx_end,
//         double new_value) {
//     if (idx_end == -1){
//         idx_end = (int)arr.size();
//     }
//     for (int i = idx_from; i < idx_end; i++){
//         if (i >= 0 && i < static_cast<int>(arr.size())){
//             arr[i] = new_value;
//         }
//     }
//     return arr;
// }

/**
 * remove_from_vector: remove a particular pointer from a vector.
 */
template <typename T>
inline void remove_from_vector(vector<T *> &vec, T *item) {
    vec.erase(
        std::remove(vec.begin(), vec.end(), item),
        vec.end());
}

/**
 * random_range_float64: produce a random factor in [min_factor, max_factor].
 */
inline double random_range_float64(
    double min_factor,
    double max_factor,
    std::mt19937 &rng) {
    std::uniform_real_distribution<double> dist(min_factor, max_factor);
    return dist(rng);
}

/**
 * @brief Selects a random item from a list of items based on given weights.
 * 
 * This function takes a vector of pointers to items and a corresponding vector of weights,
 * and returns a randomly selected item based on the weights. If the weights sum to zero or
 * are invalid, it falls back to uniform random selection.
 * 
 * @tparam T The type of the items.
 * @param items A vector of pointers to items to choose from.
 * @param weights A vector of weights corresponding to each item.
 * @param rng A random number generator.
 * @return T* A pointer to the randomly selected item, or nullptr if the input vectors are invalid.
 */
template <typename T>
inline T *random_choice(const vector<T *> &items, const vector<double> &weights, std::mt19937 &rng) {
    if (items.empty() || items.size() != weights.size()){
        return nullptr;
    }
    double wsum = 0.0;
    for (auto w : weights){
        wsum += w;
    }
    if (wsum <= 0.0){
        // Fallback: pick uniformly
        std::uniform_int_distribution<int> uni(0, (int)items.size() - 1);
        return items[uni(rng)];
    }
    std::uniform_real_distribution<double> dist(0.0, wsum);
    double r = dist(rng);
    double accum = 0.0;
    for (size_t i = 0; i < items.size(); i++){
        accum += weights[i];
        if (r <= accum){
            return items[i];
        }
    }
    // fallback
    return items.back();
}

/**
 * @brief Prints a matrix with fixed width and precision for large numbers.
 * 
 * This function prints a 2D matrix with each element formatted to a fixed width.
 * If an element is greater than 1e10, it prints "~INF" instead of the actual value.
 * Otherwise, it prints the value with one decimal place precision.
 * 
 * @tparam T The type of the elements in the matrix.
 * @param mat The matrix to be printed, represented as a vector of vectors.
 */
template <typename T>
inline void print_matrix(const vector<vector<T>> &mat) {
    // Print matrix with fixed width and precision for large numbers
    for (const auto &row : mat) {
        for (const auto &val : row) {
            if (val > 1e10) {
                cout << std::setw(8) << "~INF";
            } else {
                cout << std::fixed << std::setprecision(1) << std::setw(8) << val;
            }
        }
        cout << endl;
    }
    cout << std::setw(16);  // Reset to default format
}

/**
 * @brief Calculates the sum of values in a map with object pointers as keys.
 * 
 * @tparam Obj The type of object being pointed to by the map keys.
 * @param m The map containing object pointers and double values.
 * @return double The sum of all double values in the map.
 */
template <typename Obj>
inline double sum_map_values(const std::map<Obj*, double>& m) {
    double total = 0.0;
    for (const auto& [_, value] : m) {
        total += value;
    }
    return total;
}

// デバッグプリント
template<typename... Args>
void DEBUG(const Args&... args) {
    std::cout << "(";
    bool first = true;
    auto print = [&first](const auto& arg) {
        if (!first) {
            std::cout << " ";
        }
        std::cout << arg;
        first = false;
    };
    (print(args), ...);
    std::cout << ") ";
    // 改行なし
}


// 一般的なイテレータ範囲で探索（例：vector, list, dequeなど）
template <typename Container, typename T>
bool contains(const Container& container, const T& value) {
    return std::find(std::begin(container), std::end(container), value) != end(container);
}
