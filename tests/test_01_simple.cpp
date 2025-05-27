// clang-format off

/**
 * trafficppのテスト用コード．
 * 直接
 * ```
 * g++ test_01_simple.cpp
 * ./a.exe
 * ```
 * で実行できる
 * 
 * 標準的な結果
 * ```
 * Running simple test
 * Scenario statistics:
 *     duration: 3000 s
 *     timesteps: 600
 *     nodes: 4
 *     links: 3
 *     vehicles: 2690 veh
 *     platoon size: 5 veh
 *     platoons: 538
 *     vehicles: 2690 veh
 * ....................
 * Stats:
 *     Average speed: 7.39903
 *     Average speed ratio: 0.369952
 *     Trips completion: 2115 / 2690
 * ```
 */

#include <iostream>
#include <string>
#include <vector>
#include <chrono>

#include "../uxsimpp/trafficpp/traffi.cpp"

using std::string, std::vector, std::cout, std::endl;

int main(){
    // Simple example
    cout << "Running simple test" << endl;

    World* w = new World(
        "example",
        1200.0,   // t_max
        5.0,      // delta_n
        1.0,      // tau
        300.0,    // duo_update_time
        0.25,     // duo_update_weight
        0.5,      // route_choice_uncertainty
        1,        // print_mode
        42,     // random_seed
        1       // vehicle_log_mode
    );

    // Build a small scenario
    new Node(w, "orig1", 0, 0);
    new Node(w, "orig2", 0, 2);
    new Node(w, "merge", 1, 1);
    new Node(w, "dest",  2, 1);

    Link* link1 = new Link(w, "link1", "orig1", "merge", 20, 0.2, 1000, 0.5);
    new Link(w, "link2", "orig2", "merge", 20, 0.2, 1000, 2);
    new Link(w, "link3", "merge", "dest",  20, 0.2, 1000, 1);

    add_demand(w, "orig1", "dest", 0,   1000, 0.45);
    add_demand(w, "orig2", "dest", 400, 1000, 0.6);

    w->initialize_adj_matrix();
    w->print_scenario_stats();

    w->main_loop();

    // while (w->check_simulation_ongoing()){
    //     double t = 100;
    //     // cout << w->time << "->" << w->time+t << endl;
    //     // w->main_loop(-1, w->time+t);
        
    //     cout << w->time << "->" << t << endl;
    //     w->main_loop(t, -1);
    // }

    w->print_simple_results();

    // Cleanup
    delete w;
    return 0;
}