// clang-format off

/*
trafficppの全体的なテストコード．
直接
```
g++ test_03_gridnetwork.cpp
./a.exe
```
で実行できる
*/

#include <iostream>
#include <string>
#include <vector>
#include <cassert>

#include "../uxsimpp/trafficpp/traffi.cpp"

using std::string, std::vector, std::cout, std::endl;

int main(){

    World* w = new World(
        "example",
        10000.0,   // t_max
        5.0,    // delta_n
        1.0,    // tau
        300.0,  // duo_update_time
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
    
    int imax = 8;
    
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

    w->main_loop();
    w->print_simple_results();

    assert(w->ave_v > 5.0 && w->ave_v < 6.0);
    assert(w->ave_vratio > 0.5 && w->ave_vratio < 0.6);
    assert(w->trips_completed > 37000 && w->trips_completed < 38000);
    assert(w->trips_total > 37000 && w->trips_total < 38000);
    
    delete w;
    return 0;
}