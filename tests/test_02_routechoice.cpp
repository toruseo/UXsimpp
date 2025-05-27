// clang-format off

/**
 * trafficppのテスト用コード．
 * 直接
 * ```
 * g++ test_02_routechoice.cpp
 * ./a.exe
 * ```
 * で実行できる
 * 
 */

#include <iostream>
#include <string>
#include <vector>
#include <chrono>

#include "../uxsimpp/trafficpp/traffi.cpp"

using std::string, std::vector, std::cout, std::endl;

int main(){  
        cout << "Running route choice test" << endl;

        World* w = new World(
            "example",
            4000.0,   // t_max
            5.0,      // delta_n
            1.0,      // tau
            300.0,    // duo_update_time
            0.25,     // duo_update_weight
            0.5,      // route_choice_uncertainty
            1,        // print_mode
            42,     // random_seed
            0       // vehicle_log_mode
        );

        // Build a small scenario
        new Node(w, "orig", 0, 0); //0
        new Node(w, "mid1", 0, 2); //1
        new Node(w, "mid2", 1, 1); //2
        new Node(w, "dest",  2, 1);//3

        new Link(w, "link1a", "orig", "mid1", 10, 0.2, 2000, 1); //0-1:   200
        new Link(w, "link1b", "mid1", "dest", 10, 0.2, 3000, 1); //0-1-3: 500 ... 0-2-3の250に上書きされる
        new Link(w, "link2a", "orig", "mid2", 10, 0.2, 1000, 1); //0-2:   100
        new Link(w, "link2b", "mid2", "dest", 10, 0.2, 1500, 1); //0-2-3: 250
        
        add_demand(w, "orig", "dest", 0,   3000, 0.6);

        w->initialize_adj_matrix();
        w->print_scenario_stats();

        w->main_loop();
        w->print_simple_results();

        cout << "link1a: " 
             << w->get_link("link1a")->arrival_curve.back() << endl;
        cout << "link2a: " 
             << w->get_link("link2a")->arrival_curve.back() << endl;

        cout << "link1b: " 
             << w->get_link("link1b")->arrival_curve.back() << endl;
        cout << "link2b: " 
             << w->get_link("link2b")->arrival_curve.back() << endl;

        // Cleanup
        delete w;
        return 0;
}