/**
 * @file traffi.h
 * @brief Header file for UXsim++ C++ traffic simulation core
 * 
 * This file contains the core classes and structures for the mesoscopic traffic simulation.
 * It is a C++ port of the original UXsim Python implementation.
 */

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

/**
 * @brief Node in a traffic network
 * 
 * Represents an intersection or junction in the traffic network where vehicles
 * can transfer between links. Nodes can have traffic signals and flow capacity constraints.
 */
struct Node {
    World *w;                    ///< Pointer to the world this node belongs to
    int id;                      ///< Unique identifier for this node
    string name;                 ///< Name of the node

    vector<Link *> in_links;     ///< Incoming links to this node
    vector<Link *> out_links;    ///< Outgoing links from this node

    /// Vehicles that have just arrived at this node (not on any link)
    vector<Vehicle *> incoming_vehicles;
    /// Requested next-links by each incoming vehicle
    vector<Link *> incoming_vehicles_requests;

    /// Vehicles waiting to be generated onto the outgoing link (vertical queue)
    deque<Vehicle *> generation_queue;

    double x;                    ///< X-coordinate of the node (for visualization)
    double y;                    ///< Y-coordinate of the node (for visualization)

    // Signal control parameters
    vector<double> signal_intervals;  ///< Green time for each signal phase
    double signal_offset;             ///< Signal offset time
    double signal_t;                  ///< Elapsed time since current phase started
    int signal_phase;                 ///< Current signal phase

    /**
     * @brief Constructor for Node
     * @param w Pointer to the world this node belongs to
     * @param node_name Name of the node
     * @param x X-coordinate of the node (for visualization)
     * @param y Y-coordinate of the node (for visualization)
     * @param signal_intervals Green times for each signal phase. Default is {0} (no signal)
     * @param signal_offset Signal offset time. Default is 0
     */
    Node(
        World *w, 
        const string &node_name, 
        double x, 
        double y, 
        vector<double> signal_intervals = {0}, 
        double signal_offset = 0);

    /**
     * @brief Generate vehicles from the generation queue
     * 
     * Attempts to depart vehicles from the generation queue to outgoing links.
     * The choice of outgoing link is based on the vehicle's route preference.
     */
    void generate();

    /**
     * @brief Transfer vehicles between links at the node
     * 
     * Handles the transfer of vehicles from incoming links to outgoing links.
     * Considers signal phases, merge priorities, and link capacities.
     */
    void transfer();

    /**
     * @brief Update signal timing
     * 
     * Updates the signal phase and timing for traffic signal control.
     */
    void signal_update();
};

// -----------------------------------------------------------------------
// MARK: class Link
// -----------------------------------------------------------------------

/**
 * @brief Link in a traffic network
 * 
 * Represents a road segment connecting two nodes. Uses a mesoscopic traffic flow model
 * based on the Newell car-following model with fundamental diagram parameters.
 */
struct Link {
    World *w;                    ///< Pointer to the world this link belongs to

    int id;                      ///< Unique identifier for this link
    string name;                 ///< Name of the link
    double length;               ///< Length of the link in meters
    Node *start_node;            ///< Starting node of the link
    Node *end_node;              ///< Ending node of the link

    // Traffic flow model parameters
    double vmax;                 ///< Free flow speed (m/s)
    double delta;                ///< Minimum spacing per vehicle (m/veh)
    double tau;                  ///< Reaction time per vehicle (s/veh)
    double kappa;                ///< Jam density (veh/m)
    double capacity;             ///< Link capacity (veh/s)
    double backward_wave_speed;  ///< Backward wave speed (m/s)
    
    deque<Vehicle *> vehicles;   ///< Vehicles currently on this link (FIFO order)

    // Travel time tracking
    vector<double> traveltime_tt; ///< Travel time increments
    vector<double> traveltime_t;  ///< Time stamps for travel time records

    // Cumulative curves for traffic analysis
    vector<double> arrival_curve;    ///< Cumulative arrival count over time
    vector<double> departure_curve;  ///< Cumulative departure count over time
    vector<double> traveltime_real;  ///< Actual travel time experienced by vehicles
    vector<double> traveltime_instant; ///< Instantaneous travel time based on current conditions

    double merge_priority;       ///< Priority when merging at downstream node

    // Capacity constraints
    double capacity_out;         ///< Outflow capacity (veh/s)
    double capacity_out_remain;  ///< Remaining outflow capacity for current timestep

    // Signal control
    vector<int> signal_group;    ///< Signal groups this link belongs to

    /**
     * @brief Constructor for Link
     * @param w Pointer to the world this link belongs to
     * @param link_name Name of the link
     * @param start_node_name Name of the starting node
     * @param end_node_name Name of the ending node
     * @param vmax Free flow speed (m/s)
     * @param kappa Jam density (veh/m)
     * @param length Length of the link (m)
     * @param merge_priority Priority when merging at downstream node
     * @param capacity_out Outflow capacity (veh/s). Default is -1.0 (unlimited)
     * @param signal_group Signal groups this link belongs to. Default is {0}
     */
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

    /**
     * @brief Update link state for current timestep
     * 
     * Updates travel time calculations and capacity constraints.
     */
    void update();

    /**
     * @brief Calculate and set travel time metrics
     * 
     * Computes both actual and instantaneous travel times based on current traffic conditions.
     */
    void set_travel_time();

};

// -----------------------------------------------------------------------
// MARK: class Vehicle
// -----------------------------------------------------------------------

/**
 * @brief Vehicle (or platoon) in the traffic network
 * 
 * Represents a vehicle or platoon of vehicles traveling through the network.
 * Vehicles follow the Newell car-following model and make route choices based on
 * dynamic user optimization (DUO) principles.
 */
struct Vehicle {
    World *w;                    ///< Pointer to the world this vehicle belongs to
    int id;                      ///< Unique identifier for this vehicle
    string name;                 ///< Name of the vehicle

    double departure_time;       ///< Scheduled departure time (seconds)
    Node *orig;                  ///< Origin node
    Node *dest;                  ///< Destination node
    Link *link;                  ///< Current link the vehicle is on

    double arrival_time;         ///< Actual arrival time at destination
    double travel_time;          ///< Total travel time (arrival_time - departure_time)

    // Position and motion
    double x;                    ///< Current position on the link (meters)
    double x_next;               ///< Next position for car-following calculation
    double v;                    ///< Current speed (m/s)

    // Car-following relationships
    Vehicle *leader;             ///< Leading vehicle in the same lane
    Vehicle *follower;           ///< Following vehicle in the same lane

    int state;                   ///< Vehicle state: home(0), wait(1), run(2), end(3)

    double arrival_time_link;    ///< Time when vehicle entered current link

    // Route choice logic
    Link *route_next_link;       ///< Next link chosen by route choice
    int route_choice_flag_on_link; ///< Flag indicating if route choice has been made on current link
    double route_adaptive;       ///< Route adaptation parameter
    double route_choice_uncertainty; ///< Uncertainty in route choice
    map<Link *, double> route_preference; ///< Preference weights for each link
    int route_choice_principle;  ///< Route choice principle (DUO or fixed)
    vector<Link *> links_preferred; ///< Preferred links for this vehicle

    // Logging data
    vector<double> log_t;        ///< Time log
    vector<int> log_state;       ///< State log
    vector<int> log_link;        ///< Link ID log
    vector<double> log_x;        ///< Position log
    vector<double> log_v;        ///< Speed log

    /**
     * @brief Constructor for Vehicle
     * @param w Pointer to the world this vehicle belongs to
     * @param vehicle_name Name of the vehicle
     * @param departure_time Scheduled departure time (seconds)
     * @param orig_name Name of the origin node
     * @param dest_name Name of the destination node
     */
    Vehicle(
        World *w,
        const string &vehicle_name,
        double departure_time,
        const string &orig_name,
        const string &dest_name);

    /**
     * @brief Update vehicle state and position
     * 
     * Updates the vehicle's state based on its current situation:
     * - HOME: Check if departure time has arrived
     * - WAIT: Wait at origin node
     * - RUN: Move along current link and handle route choice
     * - END: Trip completed
     */
    void update();

    /**
     * @brief End the vehicle's trip
     * 
     * Handles trip completion, updates statistics, and removes vehicle from simulation.
     */
    void end_trip();

    /**
     * @brief Newell car-following model
     * 
     * Calculates the next position based on free-flow speed and leader constraints.
     */
    void car_follow_newell();

    /**
     * @brief Choose next link for route
     * @param linkset Available outgoing links to choose from
     * 
     * Selects the next link based on route preferences and DUO principles.
     */
    void route_next_link_choice(vector<Link*> linkset);

    /**
     * @brief Record travel time for a link
     * @param link Link for which to record travel time
     * @param t Current time
     */
    void record_travel_time(Link *link, double t);

    /**
     * @brief Log vehicle data for current timestep
     * 
     * Records position, speed, state, and other vehicle data for analysis.
     */
    void log_data();

};

// -----------------------------------------------------------------------
// MARK: class World
// -----------------------------------------------------------------------

/**
 * @brief World (simulation environment)
 * 
 * The main simulation environment that contains all nodes, links, and vehicles.
 * Manages the simulation loop, route choice updates, and global parameters.
 * This is the C++ equivalent of the Python World class.
 */
struct World {
    // Simulation configuration
    long long timestamp;         ///< Timestamp when world was created
    string name;                 ///< Name of the simulation scenario

    double t_max;                ///< Maximum simulation time (seconds)
    double delta_n;              ///< Platoon size (vehicles per platoon)
    double tau;                  ///< Reaction time per vehicle (seconds)
    double duo_update_time;      ///< Time interval for DUO route choice update (seconds)
    double duo_update_weight;    ///< Weight for DUO route choice update
    int print_mode;              ///< Whether to print simulation progress

    double delta_t;              ///< Simulation timestep width (seconds)
    size_t total_timesteps;      ///< Total number of simulation timesteps
    size_t timestep_for_route_update; ///< Timestep interval for route choice update

    // ID counters for object creation
    int node_id;                 ///< Next available node ID
    int link_id;                 ///< Next available link ID
    int vehicle_id;              ///< Next available vehicle ID

    // Collections of simulation objects
    vector<Vehicle *> vehicles;  ///< All vehicles (all states)
    vector<Link *> links;        ///< All links in the network
    vector<Node *> nodes;        ///< All nodes in the network
    unordered_map<int, Vehicle *> vehicles_living;  ///< Living vehicles (home, wait, run)
    unordered_map<int, Vehicle *> vehicles_running; ///< Running vehicles only
    unordered_map<string, Node *> nodes_map;        ///< Name to node mapping
    unordered_map<string, Link *> links_map;        ///< Name to link mapping
    unordered_map<string, Vehicle *> vehicles_map;  ///< Name to vehicle mapping

    // Simulation state
    size_t timestep;             ///< Current simulation timestep
    double time;                 ///< Current simulation time (seconds)

    // Route choice parameters
    double route_adaptive;       ///< Route adaptation parameter
    double route_choice_uncertainty; ///< Uncertainty in route choice
    vector<map<Link *, double>> route_preference; ///< Route preferences by destination

    // Network graph representation
    vector<vector<int>> adj_mat;        ///< Adjacency matrix (connectivity)
    vector<vector<double>> adj_mat_time; ///< Adjacency matrix with travel times
    vector<vector<int>> route_next;     ///< Next node matrix for shortest paths
    vector<vector<double>> route_dist;  ///< Distance matrix for shortest paths

    bool flag_initialized;       ///< Whether the world has been initialized

    // Statistics
    double ave_v;                ///< Average vehicle speed
    double ave_vratio;           ///< Average speed ratio
    double trips_total;          ///< Total number of trips
    double trips_completed;      ///< Number of completed trips

    // Random number generation
    long long random_seed;       ///< Random seed for reproducibility
    std::mt19937 rng;            ///< Random number generator

    std::ostream *writer;        ///< Output stream for printing

    /**
     * @brief Constructor for World
     * @param world_name Name of the simulation scenario
     * @param t_max Maximum simulation time (seconds)
     * @param delta_n Platoon size (vehicles per platoon)
     * @param tau Reaction time per vehicle (seconds)
     * @param duo_update_time Time interval for DUO route choice update (seconds)
     * @param duo_update_weight Weight for DUO route choice update
     * @param route_choice_uncertainty Uncertainty in route choice
     * @param print_mode Whether to print simulation progress
     * @param random_seed Random seed for reproducibility
     * @param vehicle_log_mode Whether to enable detailed vehicle logging
     */
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

    /**
     * @brief Initialize adjacency matrices for the network
     * 
     * Creates adjacency matrices for network connectivity and travel times.
     * Must be called before simulation execution.
     */
    void initialize_adj_matrix();

    /**
     * @brief Update adjacency matrix with current travel times
     * 
     * Updates the travel time matrix based on current link conditions
     * for route choice calculations.
     */
    void update_adj_time_matrix();

    /**
     * @brief Update route preferences using DUO principle
     * 
     * Updates vehicle route preferences based on dynamic user optimization,
     * considering current shortest paths and update weights.
     */
    void route_choice_duo();

    /**
     * @brief Compute shortest paths for all node pairs
     * @param adj Adjacency matrix with travel times
     * @param infty Value representing infinity
     * @return Pair of distance matrix and next-hop matrix
     * 
     * Uses Dijkstra's algorithm to compute shortest paths between all node pairs.
     */
    pair<vector<vector<double>>, vector<vector<int>>> 
        route_search_all(const vector<vector<double>> &adj, double infty);

    /**
     * @brief Print scenario statistics
     * 
     * Displays information about the simulation scenario including
     * number of nodes, links, vehicles, and simulation parameters.
     */
    void print_scenario_stats();

    /**
     * @brief Print simple simulation results
     * 
     * Displays basic simulation results including average speeds
     * and trip completion statistics.
     */
    void print_simple_results();

    /**
     * @brief Execute the main simulation loop
     * @param duration_t Duration to simulate (seconds). Default -1 means until end
     * @param end_t End time for simulation (seconds). Default -1 means until end
     * 
     * Runs the main simulation loop, updating all objects at each timestep.
     */
    void main_loop(double duration_t, double end_t);

    /**
     * @brief Check if simulation is still ongoing
     * @return True if simulation has not reached its end time
     */
    bool check_simulation_ongoing();

    /**
     * @brief Get node by name
     * @param node_name Name of the node to find
     * @return Pointer to the node
     */
    Node *get_node(const string &node_name);

    /**
     * @brief Get link by name
     * @param link_name Name of the link to find
     * @return Pointer to the link
     */
    Link *get_link(const string &link_name);

    /**
     * @brief Get link by ID
     * @param link_id ID of the link to find
     * @return Pointer to the link
     */
    Link *get_link_by_id(const int link_id);

    /**
     * @brief Get vehicle by name
     * @param vehicle_name Name of the vehicle to find
     * @return Pointer to the vehicle
     */
    Vehicle *get_vehicle(const string &vehicle_name);

    size_t vehicle_log_reserve_size; ///< Reserved size for vehicle logging vectors
    bool vehicle_log_mode;           ///< Whether detailed vehicle logging is enabled

};
