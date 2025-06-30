// clang-format off

#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <deque>
#include <string>
#include <cmath>
#include <random>
#include <map>
#include <algorithm>
#include <chrono>
#include <queue>

#include "traffi.h"

using std::string, std::vector, std::deque, std::pair, std::map, std::unordered_map;
using std::round, std::floor, std::ceil;
using std::cout, std::endl;

// -----------------------------------------------------------------------
// MARK: Node 
// -----------------------------------------------------------------------

/**
 * @brief Create a node.
 * 
 * @param w The world to which the node belongs.
 * @param node_name The name of the node.
 * @param x The x-coordinate of the node.
 * @param y The y-coordinate of the node.
 * @param signal_intervals A list representing the signal at the node.
 * @param signal_offset The offset of the signal.
 */
Node::Node(World *w, const string &node_name, double x, double y, vector<double> signal_intervals, double signal_offset)
    : w(w),
      id(w->node_id),
      name(node_name),
      x(x),
      y(y),
      signal_intervals(signal_intervals),
      signal_offset(signal_offset){
    w->nodes.push_back(this);
    w->node_id++;
    w->nodes_map[node_name] = this;

    signal_t = signal_offset;
    signal_phase = 0;
}

/**
 * @brief Generate a single vehicle if possible.
 */
void Node::generate(){
    // If there's a waiting vehicle to be generated onto an outgoing link
    if (!generation_queue.empty()){
        Vehicle *veh = generation_queue.front();
        
        //Choose the link
        veh -> route_next_link_choice(out_links);

        if (!out_links.empty() && veh->route_next_link != nullptr){
            Link *outlink = veh->route_next_link;

            // check if outlink can accept a new vehicle
            if (outlink->vehicles.empty() || outlink->vehicles.back()->x > outlink->delta * w->delta_n){
                // pop front
                generation_queue.pop_front();

                veh->state = vsRUN;
                veh->link = outlink;
                veh->x = 0.0;
                veh->record_travel_time(nullptr, (double)w->timestep * w->delta_t);

                w->vehicles_running[veh->id] = veh;

                // Leader-Follower
                if (!outlink->vehicles.empty()){
                    veh->leader = outlink->vehicles.back();
                    outlink->vehicles.back()->follower = veh;
                }
                outlink->vehicles.push_back(veh);

                // arrival curve
                outlink->arrival_curve[w->timestep] += w->delta_n;
            }
        }
    }
}

/**
 * @brief Update the signal state of the node.
 */
void Node::signal_update(){
    if (signal_intervals.size() > 1){
        while (signal_t > signal_intervals[signal_phase]){
            signal_t -= signal_intervals[signal_phase];
            signal_phase ++;
            if (signal_phase >= signal_intervals.size()){
                signal_phase = 0;
            }
        }
        signal_t += w->delta_t;
    }
}

/**
 * @brief Transfer vehicles between links at the node.
 */
void Node::transfer(){
    // For each outlink, check if we can accept a vehicle
    for (auto outlink : out_links){
        if (outlink->vehicles.empty() ||
            outlink->vehicles.back()->x > outlink->delta * w->delta_n){

            // collect merging vehicles that want to go to `outlink`
            vector<Vehicle *> merging_vehs;
            vector<double> merge_priorities;
            for (auto veh : incoming_vehicles){
                if (veh->route_next_link == outlink &&
                        veh->link->capacity_out_remain >= w->delta_n &&
                        contains(veh->link->signal_group, signal_phase)){
                    merging_vehs.push_back(veh);
                    // weighting = veh->link_ptr->merge_priority
                    if (veh->link){
                        merge_priorities.push_back(veh->link->merge_priority);
                    }else{
                        merge_priorities.push_back(1.0);
                    }
                }
            }
            if (merging_vehs.empty()){
                continue;
            }

            // pick exactly one to merge
            Vehicle *chosen_veh = random_choice<Vehicle>(
                merging_vehs,
                merge_priorities,
                w->rng);
            if (!chosen_veh){
                continue;
            }

            chosen_veh->link->capacity_out_remain -= w->delta_n;

            // departure curve of the old link
            chosen_veh->link->departure_curve[w->timestep] += w->delta_n;
            // arrival curve of the new link
            outlink->arrival_curve[w->timestep] += w->delta_n;

            // record travel time
            chosen_veh->record_travel_time(chosen_veh->link, (double)w->timestep * w->delta_t);

            // remove from old link's vehicle
            chosen_veh->link->vehicles.pop_front();
            
            chosen_veh->link = outlink;
            chosen_veh->x = 0.0;
            chosen_veh->x_next = 0.0;

            if (chosen_veh->follower){
                chosen_veh->follower->leader = nullptr;
            }
            chosen_veh->leader = nullptr;
            chosen_veh->follower = nullptr;

            if (!outlink->vehicles.empty()){
                Vehicle *leader_veh = outlink->vehicles.back();
                chosen_veh->leader = leader_veh;
                leader_veh->follower = chosen_veh;
            }
            outlink->vehicles.push_back(chosen_veh);

            // remove chosen_veh from incoming_vehicles
            remove_from_vector(incoming_vehicles, chosen_veh);
        }
    }

    incoming_vehicles.clear();
    incoming_vehicles_requests.clear();
}

// -----------------------------------------------------------------------
// MARK: Link 
// -----------------------------------------------------------------------

/**
 * @brief Create a link.
 * 
 * @param w The world to which the link belongs.
 * @param link_name The name of the link.
 * @param start_node_name The name of the start node.
 * @param end_node_name The name of the end node.
 * @param vmax The free flow speed on the link.
 * @param kappa The jam density on the link.
 * @param length The length of the link.
 * @param merge_priority The priority of the link when merging.
 * @param capacity_out The capacity out of the link.
 * @param signal_group The signal group(s) to which the link belongs.
 */
Link::Link(
    World *w,
    const string &link_name,
    const string &start_node_name,
    const string &end_node_name,
    double vmax,
    double kappa,
    double length,
    double merge_priority,
    double capacity_out,
    vector<int> signal_group)
    : w(w),
      id(w->link_id),
      name(link_name),
      length(length),
      vmax(vmax),
      kappa(kappa),
      merge_priority(merge_priority),
      capacity_out(capacity_out),
      signal_group(signal_group){
        
    if (kappa <= 0.0){
        kappa = 0.2;
    }
    delta = 1.0/kappa;
    tau = w->tau;

    backward_wave_speed = 1/tau/kappa;
    capacity = vmax*backward_wave_speed*kappa/(vmax+backward_wave_speed);

    if (capacity_out < 0.0){
        capacity_out = 10e10;
    }
    capacity_out_remain = capacity_out*w->delta_t;

    start_node = w->nodes_map[start_node_name];
    end_node = w->nodes_map[end_node_name];

    arrival_curve.resize(w->total_timesteps, 0.0);
    departure_curve.resize(w->total_timesteps, 0.0);

    traveltime_real.resize(w->total_timesteps, 0.0);
    traveltime_instant.resize(w->total_timesteps, 0.0);

    // Insert self into global vectors
    start_node->out_links.push_back(this);
    end_node->in_links.push_back(this);

    w->links.push_back(this);
    w->link_id++;
    w->links_map[link_name] = this;
}

/**
 * @brief Update link state and capacity.
 */
void Link::update(){
    set_travel_time();

    if (w->timestep != 0){
        arrival_curve[w->timestep] = arrival_curve[w->timestep-1];
        departure_curve[w->timestep] = departure_curve[w->timestep-1];
    }

    if (capacity_out < 10e9 ){
        if (capacity_out_remain  < w->delta_n){
            capacity_out_remain += capacity_out*w->delta_t;
        }
    } else {
        capacity_out_remain = 10e9;
    }
}

/**
 * @brief Set travel time based on current traffic conditions.
 */
void Link::set_travel_time(){
    // last vehicle's real travel time
    if (!traveltime_tt.empty() && !vehicles.empty()){
        traveltime_real[w->timestep] = (double)traveltime_tt.back();
    }else{
        traveltime_real[w->timestep] = (double)length / (double)vmax;
    }

    // instantaneous travel time = length / average speed
    if (!vehicles.empty()){
        double vsum = 0.0;
        for (auto veh : vehicles){
            vsum += veh->v;
        }
        double avg_v = vsum / (double)vehicles.size();
        if (avg_v > vmax / 10.0){
            traveltime_instant[w->timestep] = (double)length / avg_v;
        }else{
            traveltime_instant[w->timestep] = (double)length / (vmax / 10.0);
        }
    }else{
        traveltime_instant[w->timestep] = (double)length / (double)vmax;
    }
}

// -----------------------------------------------------------------------
// MARK: Vehicle 
// -----------------------------------------------------------------------


/**
 * @brief Create a vehicle.
 * 
 * @param w The world to which the vehicle belongs.
 * @param vehicle_name The name of the vehicle.
 * @param departure_time The departure time of the vehicle.
 * @param orig_name The origin node.
 * @param dest_name The destination node.
 */
Vehicle::Vehicle(
    World *w,
    const string &vehicle_name,
    double departure_time,
    const string &orig_name,
    const string &dest_name)
    : w(w),
      id(w->vehicle_id),
      name(vehicle_name),
      departure_time(departure_time),
      orig(nullptr),
      dest(nullptr),
      link(nullptr),
      x(0.0),
      x_next(0.0),
      v(0.0),
      leader(nullptr),
      follower(nullptr),
      state(vsHOME),
      arrival_time(0.0),
      travel_time(0.0),
      arrival_time_link(0.0),
      route_next_link(nullptr),
      route_choice_flag_on_link(0),
      route_choice_principle(rcpDUO),
      route_adaptive(0.0),
      route_choice_uncertainty(0.0){
    orig = w->nodes_map[orig_name];
    dest = w->nodes_map[dest_name];

    // Initialize link preference
    for (auto ln : w->links){
        route_preference[ln] = 0.0;
    }
    route_choice_uncertainty = w->route_choice_uncertainty;

    log_t.reserve(w->vehicle_log_reserve_size);
    log_state.reserve(w->vehicle_log_reserve_size);
    log_link.reserve(w->vehicle_log_reserve_size);
    log_x.reserve(w->vehicle_log_reserve_size);
    log_v.reserve(w->vehicle_log_reserve_size);

    w->vehicles.push_back(this);
    w->vehicles_living[id] = this;
    w->vehicle_id++;
    w->vehicles_map[vehicle_name] = this;
}

/**
 * @brief Update vehicle state and movement.
 */
void Vehicle::update(){

    if (state == vsHOME){
        if ((double)w->timestep * w->delta_t >= departure_time){
            log_data();
            state = vsWAIT;
            // push self onto the generation_queue of the origin
            orig->generation_queue.push_back(this);
        }
    }else if (state == vsWAIT){
        log_data();
    }else if (state == vsRUN){
        log_data();
        // route choice check
        if (x == 0.0){
            route_choice_flag_on_link = 0;
        }

        // update speed
        v = (x_next - x) / (w->delta_t);
        x = x_next;

        // check if we are at end of the link
        if (std::fabs(x - link->length) < 1e-9){
            // we reached the end of this link
            if (link->end_node == dest){
                end_trip();
                log_data();
            }else{
                route_next_link_choice(link->end_node->out_links);
                link->end_node->incoming_vehicles.push_back(this);
                link->end_node->incoming_vehicles_requests.push_back(route_next_link);
            }
        }
    }else if (state == vsEND){
        // do nothing
    }
}

/**
 * @brief End the vehicle's trip.
 */
void Vehicle::end_trip(){
    state = vsEND;
    link->departure_curve[w->timestep] += w->delta_n;
    record_travel_time(link, (double)w->timestep * w->delta_t);

    arrival_time = (double)w->timestep * w->delta_t;
    travel_time = arrival_time - departure_time;

    w->vehicles_living.erase(id);
    w->vehicles_running.erase(id);

    link->vehicles.pop_front();

    if (follower){
        follower->leader = nullptr;
    }
    link = nullptr;
    x = 0.0;
}

/**
 * @brief Apply Newell's car-following model.
 */
void Vehicle::car_follow_newell(){
    // free-flow
    x_next = x + link->vmax * w->delta_t;

    // congested
    if (leader != nullptr){
        double gap = leader->x - link->delta * w->delta_n;
        if (x_next >= gap){
            x_next = gap;
        }
    }

    // non-decreasing
    if (x_next < x){
        x_next = x;
    }

    // clamp to link length
    if (x_next >= link->length){
        x_next = link->length;
    }
}

/**
 * @brief Choose the next link based on route choice principle.
 * 
 * @param linkset Available links to choose from.
 */
void Vehicle::route_next_link_choice(vector<Link*> linkset){
    if (linkset.empty()){
        // no outgoing link
        route_next_link = nullptr;
        route_choice_flag_on_link = 1;
        return;
    }

    vector<double> outlink_pref;
    bool prefer_flag = 0;

    if (!links_preferred.empty()) {
        for (auto ln_out : linkset){
            outlink_pref.push_back(0);
            for (auto ln_prefer : links_preferred){
                if (ln_out == ln_prefer){
                    outlink_pref.back() = 1;
                    prefer_flag = 1;
                }
            }
        }
    }
    if (prefer_flag == 0){ //指定されたリンクがなければ通常通り
        outlink_pref = {};
        for (auto ln : linkset){
            outlink_pref.push_back(w->route_preference[dest->id][ln]);
        }
    }

    route_next_link = random_choice<Link>(
        linkset,
        outlink_pref,
        w->rng);
    route_choice_flag_on_link = 1;
}

/**
 * @brief Record travel time for the link.
 * 
 * @param link The link to record travel time for.
 * @param t The current time.
 */
void Vehicle::record_travel_time(Link *link, double t){
    if (link != nullptr){
        link->traveltime_t.push_back(t);
        link->traveltime_tt.push_back(t - arrival_time_link);
    }
    arrival_time_link = t + 1.0;
}

/**
 * @brief Log vehicle data for analysis.
 */
void Vehicle::log_data(){
    // 各タイムステップのログを push_back で追加する
    if (w->vehicle_log_mode == 1){
        log_t.push_back((double)w->timestep * w->delta_t);
        log_state.push_back(state);
        if (link) {
            log_link.push_back(link->id);
        } else {
            log_link.push_back(-1);
        }
        log_x.push_back(x);
        if (link != nullptr && std::fabs(x - (link->length - 1.0)) > 1e-9){
            log_v.push_back(v);
        } else {
            log_v.push_back(0.0);
        }
}
}


// -----------------------------------------------------------------------
// MARK: World 
// -----------------------------------------------------------------------

/**
 * @brief Create a World (simulation environment).
 * 
 * @param world_name The name of the world.
 * @param t_max The simulation duration.
 * @param delta_n The platoon size.
 * @param tau The reaction time.
 * @param duo_update_time The time interval for route choice update.
 * @param duo_update_weight The update weight for route choice.
 * @param route_choice_uncertainty The noise in route choice.
 * @param print_mode Whether print the simulation progress or not.
 * @param random_seed The random seed.
 * @param vehicle_log_mode Whether save vehicle data or not.
 */
World::World(
    const string &world_name,
    double t_max,
    double delta_n,
    double tau,
    double duo_update_time,
    double duo_update_weight,
    double route_choice_uncertainty,
    int print_mode,
    long long random_seed,
    bool vehicle_log_mode)
    : timestamp(std::chrono::high_resolution_clock::now().time_since_epoch().count()),
      name(world_name),
      t_max(t_max),
      delta_n(delta_n),
      tau(tau),
      duo_update_time(duo_update_time),
      duo_update_weight(duo_update_weight),
      print_mode(print_mode),
      delta_t(tau * delta_n),
      total_timesteps((int)(t_max / (tau * delta_n))),
      timestep_for_route_update((int)(duo_update_time / (tau * delta_n))),
      time(0),
      node_id(0),
      link_id(0),
      vehicle_id(0),
      timestep(0),
      route_choice_uncertainty(route_choice_uncertainty),
      random_seed(random_seed),
      vehicle_log_reserve_size(0),
      vehicle_log_mode(vehicle_log_mode),
      ave_v(0.0),
      ave_vratio(0.0),
      trips_total(0.0),
      trips_completed(0.0),
      rng((std::mt19937::result_type)random_seed),
      flag_initialized(false),
      writer(&std::cout){
}

void World::initialize_adj_matrix(){
    if (flag_initialized==false){
        adj_mat.resize(node_id, vector<int>(node_id, 0));
        adj_mat_time.resize(node_id, vector<double>(node_id, 0.0));
        for (auto ln : links){
            int i = ln->start_node->id;
            int j = ln->end_node->id;
            adj_mat[i][j] = 1;
            adj_mat_time[i][j] = ln->length / ln->vmax;
        }

        route_preference.resize(nodes.size());
        for (auto nd : nodes){
            for (auto ln : links){
                route_preference[nd->id][ln] = 0.0;
            }
        }
        flag_initialized = true;
    }
}

void World::update_adj_time_matrix(){
    for (auto ln : links){
        int i = ln->start_node->id;
        int j = ln->end_node->id;
        if (ln->traveltime_real[timestep] != 0.0){
            adj_mat_time[i][j] = ln->traveltime_real[timestep];
        }else{
            adj_mat_time[i][j] = ln->length / ln->vmax;
        }
    }
}

pair<vector<vector<double>>, vector<vector<int>>> 
  World::route_search_all(const vector<vector<double>> &adj, double infty) {
    int nsize = (int)adj.size();
    if (std::fabs(infty) < 1e-9) {
        infty = 1e15;
    }

    // 隣接リストの構築: pair<隣接ノード, 重み>
    vector<vector<pair<int, double>>> adj_list(nsize);
    for (int i = 0; i < nsize; i++) {
        for (int j = 0; j < nsize; j++) {
            if (adj[i][j] > 0.0) {
                adj_list[i].push_back({j, adj[i][j]});
            }
        }
    }

    vector<vector<double>> dist(nsize, vector<double>(nsize, infty));
    vector<vector<int>> next_hop(nsize, vector<int>(nsize, -1));
    
    // 優先度付きキューを使用: pair<距離, 頂点番号>
    using pdi = pair<double, int>;
    std::priority_queue<pdi, vector<pdi>, std::greater<pdi>> pq;
    
    // 各始点からダイクストラ法を実行
    for (int start = 0; start < nsize; start++) {
        vector<bool> visited(nsize, false);
        dist[start][start] = 0.0;
        next_hop[start][start] = start;
        pq.push({0.0, start});
        
        while (!pq.empty()) {
            auto [d, current] = pq.top();
            pq.pop();
            
            if (visited[current]) continue;
            visited[current] = true;
            
            // 隣接リストを使用した隣接頂点の探索
            for (const auto& [next, weight] : adj_list[current]) {
                double new_dist = dist[start][current] + weight;
                if (new_dist < dist[start][next]) {
                    dist[start][next] = new_dist;
                    // 次のホップを更新
                    next_hop[start][next] = (current == start) ? 
                                          next : next_hop[start][current];
                    pq.push({new_dist, next});
                }
            }
        }
    }
    
    return {dist, next_hop};
}

/**
 * @brief Update route choice using dynamic user optimum.
 */
void World::route_choice_duo(){
    for (auto dest : nodes){
        int k = dest->id;

        auto duo_update_weight_tmp = duo_update_weight;
        if (sum_map_values(route_preference[k]) == 0){
             duo_update_weight_tmp = 1; //initialize with deterministic shortest path
        }

        // For each link in the world, update preference
        for (auto ln : links){
            int i = ln->start_node->id;
            int j = ln->end_node->id;
            if (route_next[i][k] == j){
                route_preference[k][ln] = (1.0 - duo_update_weight) * route_preference[k][ln] + duo_update_weight;
            }else{
                route_preference[k][ln] = (1.0 - duo_update_weight) * route_preference[k][ln];
            }
        }
    }
}

void World::print_scenario_stats(){
    if (print_mode == 1){
        (*writer) << "Scenario statistics:\n";
        (*writer) << "    duration: " << t_max << " s\n";
        (*writer) << "    timesteps: " << total_timesteps << "\n";
        (*writer) << "    nodes: " << nodes.size() << "\n";
        (*writer) << "    links: " << links.size() << "\n";
        (*writer) << "    vehicles: " << (int)vehicles.size() * (int)delta_n << " veh\n";
        (*writer) << "    platoon size: " << delta_n << " veh\n";
        (*writer) << "    platoons: " << vehicles.size() << "\n";
        (*writer) << "    vehicles: " << (double)vehicles.size() * delta_n << " veh\n";
    }
}

void World::print_simple_results(){
    double n = 0.0;

    for (auto veh : vehicles){
        trips_total += delta_n;
        for (int j = 0; j < veh->log_state.size(); j++){
            if (veh->log_state[j] == vsRUN){
                double v_cur = veh->log_v[j];
                ave_v += (v_cur - ave_v) / (n + 1.0);

                Link *ln_ptr = nullptr;
                if (veh->log_link[j] != -1){
                    ln_ptr = get_link_by_id(veh->log_link[j]);
                }
                double denom_vmax = (ln_ptr) ? ln_ptr->vmax : 1.0;
                double vratio = v_cur / denom_vmax;

                ave_vratio += (vratio - ave_vratio) / (n + 1.0);
                n += 1.0;
            }else if (veh->log_state[j] == vsEND){
                trips_completed += delta_n;
                break;
            }
        }
    }

    (*writer) << "Stats:\n";
    (*writer) << "    Average speed: " << ave_v << "\n";
    (*writer) << "    Average speed ratio: " << ave_vratio << "\n";
    (*writer) << "    Trips completion: "
              << trips_completed << " / " << trips_total << "\n";
}

// -----------------------------------------------------------------------
//MARK: mainloop
// -----------------------------------------------------------------------

/**
 * @brief Main simulation loop.
 * 
 * @param duration_t Duration to run simulation.
 * @param until_t Time to run simulation until.
 */
void World::main_loop(double duration_t=-1, double until_t=-1){
    int start_ts, end_ts;
    start_ts = timestep;

    if (duration_t < 0 && until_t < 0){
        end_ts = total_timesteps;
    } else if (duration_t >= 0 && until_t < 0){
        end_ts = static_cast<size_t>(floor((duration_t+time)/delta_t)) + 1;
    } else if (duration_t < 0 && until_t >= 0){
        end_ts = static_cast<size_t>(floor(until_t/delta_t)) + 1;
    } else {
        throw std::runtime_error("Cannot specify both `duration_t` and `until_t` parameters for `World.main_loop`");
    }

    if (end_ts > total_timesteps){
        end_ts = total_timesteps;
    }
    if (end_ts <= start_ts){
        return;
    }

    for (timestep = start_ts; timestep < end_ts; timestep++){
        time = timestep*delta_t;

        // Link updates
        for (auto ln : links){
            ln->update();
        }

        // Node generate & update
        for (auto nd : nodes){
            nd->generate();
            nd->signal_update();
        }

        // Node transfer
        for (auto nd : nodes){
            nd->transfer();
        }

        // car-following
        int veh_count = 0;
        double ave_speed = 0;
        for (const auto& veh : vehicles_running){
            veh.second->car_follow_newell();
            
            veh_count++;
            ave_speed = ave_speed*(veh_count-1)/veh_count + veh.second->v/(veh_count);
        }

        // vehicle update: 安全な走査のため、一度キーをコピーする
        for (auto it = vehicles_living.begin(); it != vehicles_living.end(); ) {
            Vehicle* veh = it->second;
            ++it;  // update 前に次のイテレータへ進める
            veh->update();

        }        

        // route choice update
        if (timestep_for_route_update > 0 && timestep % timestep_for_route_update == 0){
            update_adj_time_matrix();            
            auto res = route_search_all(adj_mat_time, 0.0);
            route_dist = res.first;
            route_next = res.second;
            route_choice_duo();
        }

        // Print progress in steps
        if (print_mode == 1 && total_timesteps > 0 && timestep % (total_timesteps / 10 == 0 ? 1 : total_timesteps / 10) == 0){
            if (timestep == 0){
                (*writer) <<  "Simulating..." << endl;
                (*writer) <<  std::setw(10) << "time" 
                    << "|"<< std::setw(14) <<  "# of vehicles"
                    << "|"<< std::setw(11) << " ave speed" << endl;
            }
            (*writer) << std::setw(8) << std::fixed << std::setprecision(0) << time << " s"
                  << "|" << std::setw(10) << veh_count*delta_n << " veh"
                  << "|" << std::setw(7) << std::fixed << std::setprecision(2) << ave_speed << " m/s"
                  << endl;
        }        
    }
}


bool World::check_simulation_ongoing(){
    if (timestep < total_timesteps){
        return true;
    } else {
        return false;
    }
}

// -----------------------------------------------------------------------
// MARK: World utils
// -----------------------------------------------------------------------

Node *World::get_node(const string &node_name){
    for (auto nd : nodes){
        if (nd->name == node_name){
            return nd;
        }
    }
    (*writer) << "Error at function get_node(): `"
              << node_name << "` not found\n";
    throw std::runtime_error("get_node() error");
}

Link *World::get_link(const string &link_name){
    for (auto ln : links){
        if (ln->name == link_name){
            return ln;
        }
    }
    (*writer) << "Error at function get_link(): `"
              << link_name << "` not found\n";
    throw std::runtime_error("get_link() error");
}


Vehicle *World::get_vehicle(const string &vehicle_name){
    for (auto vh : vehicles){
        if (vh->name == vehicle_name){
            return vh;
        }
    }
    (*writer) << "Error at function get_vehicle(): `"
              << vehicle_name << "` not found\n";
    throw std::runtime_error("get_vehicle() error");
}

Link *World::get_link_by_id(const int link_id){
    for (auto ln : links){
        if (ln->id == link_id){
            return ln;
        }
    }
    (*writer) << "Error at function get_link_id(): `"
              << link_id << "` not found\n";
    throw std::runtime_error("get_link_id() error");
}

// for some reason, this was defined outside of World
inline void add_demand(
        World *w,
        const string &orig_name,
        const string &dest_name,
        double start_t,
        double end_t,
        double flow,
        vector<string> links_preferred_str = {}){
    double demand = 0.0;
    for (double t = start_t; t < end_t; t += w->delta_t){
        demand += flow * w->delta_t;
        if (demand > (double)w->delta_n){
            // create new vehicle
            Vehicle *v = new Vehicle(
                w,
                orig_name + "-" + dest_name + "-" + std::to_string(t),
                t,
                orig_name,
                dest_name);
            
            for (auto ln_str : links_preferred_str){
                v->links_preferred.push_back(w->links_map[ln_str]);
            }
            //(void)v; // or store if needed //what is this???

            demand -= (double)w->delta_n;
        }
    }
}

// -----------------------------------------------------------------------
// main(): if you want to execute this file
// -----------------------------------------------------------------------

// int main() {
//     // Simple example
//     cout << "Running simple test" << endl;

//     World* w = new World(
//         "example",
//         3000.0,   // t_max
//         5.0,      // delta_n
//         1.0,      // tau
//         300.0,    // duo_update_time
//         0.25,     // duo_update_weight
//         0.5,      // route_choice_uncertainty
//         1,        // print_mode
//         42        // random_seed
//     );

//     // Build a small scenario
//     new Node(w, "orig1", 0, 0);
//     new Node(w, "orig2", 0, 2);
//     new Node(w, "merge", 1, 1);
//     new Node(w, "dest",  2, 1);

//     new Link(w, "link1", "orig1", "merge", 20, 0.2, 1000, 0.5);
//     new Link(w, "link2", "orig2", "merge", 20, 0.2, 1000, 2);
//     new Link(w, "link3", "merge", "dest",  20, 0.2, 1000, 1);

//     add_demand(w, "orig1", "dest", 0,   3000, 0.4);
//     add_demand(w, "orig2", "dest", 500, 3000, 0.6);

//     w->initialize_adj_matrix();
//     w->print_scenario_stats();

//     w->main_loop();
//     w->print_simple_results();

//     // Cleanup
//     delete w;
//     return 0;

// }