// clang-format off

/*
trafficppのベンチマーク用コード．
直接
```
g++ test_03_gridnetwork_bench.cpp
./a.exe
```
で実行できる
*/

#include <iostream>
#include <string>
#include <vector>
#include <chrono>

#include "../uxsimpp/trafficpp/traffi.cpp"

using std::string, std::vector, std::cout, std::endl;

int main(){
    cout << "Running heavy benchmark" << endl;

    auto start = std::chrono::high_resolution_clock::now();

    World* w = new World(
        "example",
        10000.0,   // t_max
        5.0,    // delta_n
        1.0,    // tau
        200.0,  // duo_update_time
        0.5,    // duo_update_weight
        0.5,    // route_choice_uncertainty
        1,      // print_mode
        42,     // random_seed
        1       // vehicle_log_mode
    );

    
    auto coord = [](int i, int j) -> string {
        return std::to_string(i) + "-"+ std::to_string(j);
    };
    auto coord2 = [](int i, int j, int k, int l) -> string {
        return std::to_string(i) + "-"+ std::to_string(j) +"-" + std::to_string(k) + "-"+ std::to_string(l);
    };
    
    int imax = 10;
    
    for (int i=0; i<imax; i++){
        for (int j=0; j<imax; j++){
            new Node(w, "node" + coord(i,j) , i, j);
        }
    }
    for (int i=0; i<imax; i++){
        for (int j=0; j<imax; j++){
            if (i > 0){
                new Link(w, "link" + coord2(i,j, i-1,j) + "a", "node" + coord(i,j), "node" +coord(i-1,j), 10, 0.2, 1000, 1);
            }
            if (i < imax-1){
                new Link(w, "link" + coord2(i,j, i+1,j) + "b", "node" + coord(i,j), "node" +coord(i+1,j), 10, 0.2, 1000, 1);
            }
            if (j > 0){
                new Link(w, "link" + coord2(i,j, i,j-1) + "c", "node" + coord(i,j), "node" +coord(i,j-1), 10, 0.2, 1000, 1);
            }
            if (j < imax-1){
                new Link(w, "link" + coord2(i,j, i,j+1) + "d", "node" + coord(i,j), "node" +coord(i,j+1), 10, 0.2, 1000, 1);
            }   
        }
    }
    
    for (int i=0; i<imax; i++){
        for (int j=0; j<imax; j++){
            add_demand(w, "node" + coord(0,i), "node" + coord(imax-1,j), 0,   3000, 0.05); 
            add_demand(w, "node" + coord(i,0), "node" + coord(j,imax-1), 0,   3000, 0.05);
            add_demand(w, "node" + coord(imax-1,i), "node" + coord(0,j), 0,   3000, 0.05); 
            add_demand(w, "node" + coord(i,imax-1), "node" + coord(j,0), 0,   3000, 0.05);
        }
    }

    w->initialize_adj_matrix();
    w->print_scenario_stats();

    auto end_scenario_definition = std::chrono::high_resolution_clock::now();
    

    w->main_loop();
    w->print_simple_results();

    
    auto end_simulation = std::chrono::high_resolution_clock::now();
    
    std::chrono::duration<double, std::milli> duration_ms_scenario = end_scenario_definition - start;
    std::cout << "TIME FOR SCENARIO:   " << duration_ms_scenario.count() << " ms" << std::endl;

    std::chrono::duration<double, std::milli> duration_ms_sim = end_simulation - end_scenario_definition;
    std::cout << "TIME FOR SIMULATION: " << duration_ms_sim.count() << " ms" << std::endl;
    
    std::cout << duration_ms_sim.count()+duration_ms_scenario.count() << std::endl;  //ベンチマーク用のprint
    // Cleanup
    delete w;
    return 0;
}