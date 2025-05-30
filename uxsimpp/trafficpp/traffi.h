// clang-format off
#pragma once

#include <iostream>
#include <iomanip>
#include <fstream>
#include <vector>
#include <deque>
#include <string>
#include <cmath>
#include <random>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <chrono>
#include <queue>
#include <execution>
#include <thread>

#include "utils.h"

using std::string, std::vector, std::deque, std::pair, std::map, std::unordered_map, std::priority_queue, std::greater, std::cout, std::endl;

// Forward declarations
struct World;
struct Node;
struct Link;
struct Vehicle;


enum VehicleState : int {
    vsHOME = 0,
    vsWAIT = 1,
    vsRUN  = 2,
    vsEND  = 3
};

enum RouteChoicePrinciple : int {
    rcpDUO = 0,
    rcpFIXED = 1
};

// -----------------------------------------------------------------------
// MARK: class Node
// -----------------------------------------------------------------------

struct Node {
    World *w;
    int id;
    string name;

    vector<Link *> in_links;
    vector<Link *> out_links;

    // Vehicles just arrived at this node (not on any link)
    vector<Vehicle *> incoming_vehicles;
    // Requested next-links by each incoming vehicle
    vector<Link *> incoming_vehicles_requests;

    // Vehicles waiting to be generated onto the outgoing link
    deque<Vehicle *> generation_queue;

    double x;
    double y;

    // signal
    vector<double> signal_intervals;
    double signal_offset;
    double signal_t;
    int signal_phase;

    Node(
        World *w, 
        const string &node_name, 
        double x, 
        double y, 
        vector<double> signal_intervals = {0}, 
        double signal_offset = 0);

    // Generate a single vehicle if possible
    void generate();

    // Transfer vehicles from incoming_vehicles to the next link
    void transfer();

    void signal_update();
};

// -----------------------------------------------------------------------
// MARK: class Link
// -----------------------------------------------------------------------

struct Link {
    World *w;

    int id;
    string name;
    double length;
    Node *start_node;
    Node *end_node;

    double vmax;
    double delta;
    double tau;
    double kappa;
    double capacity;
    double backward_wave_speed;
    deque<Vehicle *> vehicles;

    vector<double> traveltime_tt; // increments of time
    vector<double> traveltime_t;

    vector<double> arrival_curve;
    vector<double> departure_curve;
    vector<double> traveltime_real;
    vector<double> traveltime_instant;

    double merge_priority;

    double capacity_out;
    double capacity_out_remain;

    //signal
    vector<int> signal_group;

    Link(
        World *w,
        const string &link_name,
        const string &start_node_name,
        const string &end_node_name,
        double vmax,
        double kappa,
        double length,
        double merge_priority,
        double capacity_out=-1.0,
        vector<int> signal_group={0});

    void update();
    void set_travel_time();

};

// -----------------------------------------------------------------------
// MARK: class Vehicle
// -----------------------------------------------------------------------

struct Vehicle {
    World *w;
    int id;
    string name;

    double departure_time;
    Node *orig;
    Node *dest;
    Link *link;

    double arrival_time;
    double travel_time;

    double x;
    double x_next;
    double v;

    Vehicle *leader;
    Vehicle *follower;

    int state; // "home: 0", "wait: 1", "run: 2", "end: 3"

    double arrival_time_link;

    // Route logic
    Link *route_next_link;
    int route_choice_flag_on_link;
    double route_adaptive;
    double route_choice_uncertainty;
    map<Link *, double> route_preference;
    int route_choice_principle;
    vector<Link *> links_preferred;

    // Logging
    vector<double> log_t;
    vector<int> log_state;
    vector<int> log_link;
    vector<double> log_x;
    vector<double> log_v;

    Vehicle(
        World *w,
        const string &vehicle_name,
        double departure_time,
        const string &orig_name,
        const string &dest_name);

    void update();
    void end_trip();
    void car_follow_newell();
    void route_next_link_choice(vector<Link*> linkset);
    void record_travel_time(Link *link, double t);
    void log_data();

};

// -----------------------------------------------------------------------
// MARK: class World
// -----------------------------------------------------------------------

struct World {
    // Simulation config 
    long long timestamp;
    string name;

    double t_max;
    double delta_n;
    double tau;
    double duo_update_time;
    double duo_update_weight;
    int print_mode;

    double delta_t;
    size_t total_timesteps;
    size_t timestep_for_route_update;

    int node_id;
    int link_id;
    int vehicle_id;

    // Collections of objects
    vector<Vehicle *> vehicles;         //all state
    vector<Link *> links;
    vector<Node *> nodes;
    unordered_map<int, Vehicle *> vehicles_living;  //home, wait, run // vehicles_living[id] = vehicle
    unordered_map<int, Vehicle *> vehicles_running; //run
    unordered_map<string, Node *> nodes_map;
    unordered_map<string, Link *> links_map;
    unordered_map<string, Vehicle *> vehicles_map;

    size_t timestep;    //simulation timestep
    double time;    //simulation time in second

    double route_adaptive;
    double route_choice_uncertainty;
    vector<map<Link *, double>> route_preference;   //route_preference[dest][ln]: 目的ノードdestへのリンクlnの選好

    // Graph adjacency
    vector<vector<int>> adj_mat;
    vector<vector<double>> adj_mat_time;
    vector<vector<int>> route_next;
    vector<vector<double>> route_dist;

    bool flag_initialized;

    // stats
    double ave_v;
    double ave_vratio;
    double trips_total;
    double trips_completed;

    // Randomness
    long long random_seed;
    std::mt19937 rng;

    std::ostream *writer;

    World(
        const string &world_name,
        double t_max,
        double delta_n,
        double tau,
        double duo_update_time,
        double duo_update_weight,
        double route_choice_uncertainty,
        int print_mode,
        long long random_seed,
        bool vehicle_log_mode);

    void initialize_adj_matrix();
    void update_adj_time_matrix();

    void route_choice_duo();

    // Route search (Floyd-Warshall style)
    pair<vector<vector<double>>, vector<vector<int>>> 
        route_search_all(const vector<vector<double>> &adj, double infty);

    void print_scenario_stats();
    void print_simple_results();
    void main_loop(double duration_t, double end_t);

    bool check_simulation_ongoing();

    Node *get_node(const string &node_name);
    Link *get_link(const string &link_name);
    Link *get_link_by_id(const int link_id);
    Vehicle *get_vehicle(const string &vehicle_name);

    size_t vehicle_log_reserve_size;
    bool vehicle_log_mode;

};
