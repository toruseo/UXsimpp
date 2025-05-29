// clang-format off

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h> // if you need to bind functionals or std::function

#include <memory>
#include <sstream>
#include <string>
#include <iostream>
#include <streambuf>

#include "traffi.cpp"

namespace py = pybind11;


// ----------------------------------------------------------------------
// カスタム streambuf: Python の sys.stdout に出力する
// ----------------------------------------------------------------------
#ifdef __GNUC__
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wattributes" //ignore warning: greater visibility than the type of its field 
#endif
class py_stdout_redirect_buf : public std::streambuf {
public:
    py_stdout_redirect_buf() {
        // Python の sys.stdout を取得（※これがグローバル領域で呼ばれると問題になるので、後述の get_pyout() 内で初期化する）
        py::object sys = py::module_::import("sys");
        py_stdout = sys.attr("stdout");
    }
protected:
    // 単一文字出力時：char を 1文字の std::string に変換して出力
    virtual int overflow(int c) override {
        if (c != EOF) {
            std::string s(1, static_cast<char>(c));
            py_stdout.attr("write")(s);
        }
        return c;
    }
    // 複数文字出力時
    virtual std::streamsize xsputn(const char* s, std::streamsize n) override {
        std::string str(s, n);
        py_stdout.attr("write")(str);
        return n;
    }
private:
    py::object py_stdout;
};
#ifdef __GNUC__
#pragma GCC diagnostic pop
#endif

// ----------------------------------------------------------------------
// Python インタープリタが初期化された後に呼ばれるようにするため、
// 出力用 std::ostream を返すヘルパー関数を作成する
// ----------------------------------------------------------------------
std::ostream* get_pyout() {
    // 関数内の static 変数は、初回呼び出し時（すなわちPython側でインポート後）に初期化されるので安全
    static py_stdout_redirect_buf custom_buf;
    static std::ostream pyout(&custom_buf);
    return &pyout;
}

// ----------------------------------------------------------------------
// create_world() の実装（World::writer を Python の sys.stdout 経由の ostream に切り替える）
// ----------------------------------------------------------------------
std::unique_ptr<World> create_world(
        const std::string &world_name,
        double t_max,
        double delta_n,
        double tau,
        double duo_update_time,
        double duo_update_weight,
        double route_choice_uncertainty,
        int print_mode,
        long long random_seed,
        bool vehicle_log_mode){
    auto world = std::make_unique<World>(
        world_name,
        t_max,
        delta_n,
        tau,
        duo_update_time,
        duo_update_weight,
        route_choice_uncertainty,
        print_mode,
        random_seed,
        vehicle_log_mode);
    // World 内の出力先を Python の sys.stdout 経由に変更
    world->writer = get_pyout();
    return world;
}

// ----------------------------------------------------------------------
// シナリオ定義関数
// ----------------------------------------------------------------------
void add_node(World &world, const std::string &node_name, double x, double y, 
        vector<double> signal_intervals = {0}, double signal_offset = 0) {
    new Node(&world, node_name, x, y, signal_intervals, signal_offset);
}

void add_link(
        World &world,
        const std::string &link_name,
        const std::string &start_node_name,
        const std::string &end_node_name,
        double vmax,
        double kappa,
        double length,
        double merge_priority,
        double capacity_out,
        vector<int> signal_group={0}){
    new Link(&world, link_name, start_node_name, end_node_name,
                        vmax, kappa, length, merge_priority, capacity_out, signal_group);
}

void add_demand(
    World *w,
    const std::string &orig_name,
    const std::string &dest_name,
    double start_t,
    double end_t,
    double flow,
    vector<string> links_preferred_str);

// ----------------------------------------------------------------------
// コンパイル日時を返す関数
// ----------------------------------------------------------------------
std::string get_compile_datetime() {
    return std::string("Compiled on ") + __DATE__ + " at " + __TIME__;
}

// ----------------------------------------------------------------------
// Pybind11 モジュール定義
// ----------------------------------------------------------------------
PYBIND11_MODULE(trafficppy, m) {
    m.doc() = "trafficppy: pybind11 bindings for C++ mesoscopic traffic simulation";

    //
    // MARK: Scenario
    //
    m.def("create_world", &create_world,
          py::arg("world_name"),
          py::arg("t_max"),
          py::arg("delta_n"),
          py::arg("tau"),
          py::arg("duo_update_time"),
          py::arg("duo_update_weight"),
          py::arg("route_choice_uncertainty"),
          py::arg("print_mode"),
          py::arg("random_seed"),
          py::arg("vehicle_log_mode"),
          R"docstring(
          Create a new World simulation object.

          Parameters
          ----------
          world_name : str
              Name of the simulation scenario.
          t_max : float
              Maximum simulation time in seconds.
          delta_n : float
              Platoon size (vehicles per platoon).
          tau : float
              Reaction time per vehicle in seconds.
          duo_update_time : float
              Time interval for DUO route choice update in seconds.
          duo_update_weight : float
              Weight for DUO route choice update.
          route_choice_uncertainty : float
              Uncertainty in route choice.
          print_mode : int
              Whether to print simulation progress (1 for enabled, 0 for disabled).
          random_seed : int
              Random seed for reproducibility.
          vehicle_log_mode : bool
              Whether to enable detailed vehicle logging.

          Returns
          -------
          World
              The created World simulation object.
          )docstring");

    m.def("add_node", &add_node,
          py::arg("world"),
          py::arg("node_name"),
          py::arg("x"),
          py::arg("y"),
          py::arg("signal_intervals"),
          py::arg("signal_offset"),
          R"docstring(
          Add a new Node to the World.

          Parameters
          ----------
          world : World
              The World object to add the node to.
          node_name : str
              Name of the node.
          x : float
              X-coordinate of the node (for visualization).
          y : float
              Y-coordinate of the node (for visualization).
          signal_intervals : list of float
              Green times for each signal phase. Default is [0] (no signal).
          signal_offset : float
              Signal offset time. Default is 0.
          )docstring");

    m.def("add_link", &add_link,
          py::arg("world"),
          py::arg("link_name"),
          py::arg("start_node_name"),
          py::arg("end_node_name"),
          py::arg("vmax"),
          py::arg("kappa"),
          py::arg("length"),
          py::arg("merge_priority"),
          py::arg("capacity_out"),
          py::arg("signal_group"),
          R"docstring(
          Add a new Link to the World.

          Parameters
          ----------
          world : World
              The World object to add the link to.
          link_name : str
              Name of the link.
          start_node_name : str
              Name of the starting node.
          end_node_name : str
              Name of the ending node.
          vmax : float
              Free flow speed (m/s).
          kappa : float
              Jam density (veh/m).
          length : float
              Length of the link (m).
          merge_priority : float
              Priority when merging at downstream node.
          capacity_out : float
              Outflow capacity (veh/s). Use -1.0 for unlimited.
          signal_group : list of int
              Signal groups this link belongs to.
          )docstring");

    m.def("add_demand", &add_demand,
          py::arg("world"),
          py::arg("orig_name"),
          py::arg("dest_name"),
          py::arg("start_t"),
          py::arg("end_t"),
          py::arg("flow"),
          py::arg("links_preferred_str"),
          R"docstring(
          Add demand (vehicle generation) to the World.

          Parameters
          ----------
          world : World
              The World object to add demand to.
          orig_name : str
              Name of the origin node.
          dest_name : str
              Name of the destination node.
          start_t : float
              Start time for demand generation (seconds).
          end_t : float
              End time for demand generation (seconds).
          flow : float
              Flow rate (vehicles per second).
          links_preferred_str : list of str
              List of preferred link names for vehicles to use.
          )docstring");

    //
    // 2) MARK: World
    //
    py::class_<World>(m, "World")
        .def("initialize_adj_matrix", &World::initialize_adj_matrix,
             R"docstring(
             Initialize adjacency matrices for the network.
             
             Creates adjacency matrices for network connectivity and travel times.
             Must be called before simulation execution.
             )docstring")
        .def("print_scenario_stats", &World::print_scenario_stats,
             R"docstring(
             Print scenario statistics.
             
             Displays information about the simulation scenario including
             number of nodes, links, vehicles, and simulation parameters.
             )docstring")
        .def("main_loop", &World::main_loop,
             py::arg("duration_t") = -1, py::arg("end_t") = -1,
             R"docstring(
             Execute the main simulation loop.

             Parameters
             ----------
             duration_t : float, optional
                 Duration to simulate in seconds. Default -1 means until end.
             end_t : float, optional
                 End time for simulation in seconds. Default -1 means until end.
             )docstring")
        .def("check_simulation_ongoing", &World::check_simulation_ongoing,
             R"docstring(
             Check if simulation is still ongoing.

             Returns
             -------
             bool
                 True if simulation has not reached its end time.
             )docstring")
        .def("print_simple_results", &World::print_simple_results,
             R"docstring(
             Print simple simulation results.
             
             Displays basic simulation results including average speeds
             and trip completion statistics.
             )docstring")
        .def("update_adj_time_matrix", &World::update_adj_time_matrix,
             R"docstring(
             Update adjacency matrix with current travel times.
             
             Updates the travel time matrix based on current link conditions
             for route choice calculations.
             )docstring")
        .def("get_node", &World::get_node,
             py::return_value_policy::reference,
             py::arg("node_name"),
             R"docstring(
             Get a Node by name.

             Parameters
             ----------
             node_name : str
                 Name of the node to find.

             Returns
             -------
             Node
                 Reference to the node object.
             )docstring")
        .def("get_link", &World::get_link,
             py::return_value_policy::reference,
             py::arg("link_name"),
             R"docstring(
             Get a Link by name.

             Parameters
             ----------
             link_name : str
                 Name of the link to find.

             Returns
             -------
             Link
                 Reference to the link object.
             )docstring")
        .def("get_vehicle", &World::get_vehicle,
             py::return_value_policy::reference,
             py::arg("vehicle_name"),
             R"docstring(
             Get a Vehicle by name.

             Parameters
             ----------
             vehicle_name : str
                 Name of the vehicle to find.

             Returns
             -------
             Vehicle
                 Reference to the vehicle object.
             )docstring")
        .def_readonly("VEHICLES", &World::vehicles,
                      "Vector of pointers to all Vehicles in the world.")
        .def_readonly("LINKS", &World::links,
                      "Vector of pointers to all Links in the world.")
        .def_readonly("NODES", &World::nodes,
                      "Vector of pointers to all Nodes in the world.")
        .def_readonly("timestep", &World::timestep)
        .def_readonly("time", &World::time)
        .def_readonly("delta_t", &World::delta_t)
        .def_readonly("DELTAT", &World::delta_t)
        .def_readonly("t_max", &World::t_max)
        .def_readonly("TMAX", &World::t_max)
        .def_readonly("name", &World::name)
        .def_readonly("deltan", &World::delta_n)
        ;

    //
    // MARK: Node
    //
    py::class_<Node>(m, "Node")
        .def(py::init<World *, const std::string &, double, double>(),
             py::arg("world"),
             py::arg("node_name"),
             py::arg("x"),
             py::arg("y"),
             R"docstring(
             Create a new Node.

             Parameters
             ----------
             world : World
                 The World object this node belongs to.
             node_name : str
                 Name of the node.
             x : float
                 X-coordinate of the node (for visualization).
             y : float
                 Y-coordinate of the node (for visualization).
             )docstring")
        .def_readonly("W", &Node::w, "Pointer to the world this node belongs to.")
        .def_readonly("id", &Node::id, "Unique identifier for this node.")
        .def_readonly("name", &Node::name, "Name of the node.")
        .def_readwrite("x", &Node::x, "X-coordinate of the node (for visualization).")
        .def_readwrite("y", &Node::y, "Y-coordinate of the node (for visualization).")
        .def_readwrite("signal_intervals", &Node::signal_intervals, "Green times for each signal phase.")
        .def_readwrite("signal_offset", &Node::signal_offset, "Signal offset time.")
        .def_readwrite("signal_t", &Node::signal_t, "Elapsed time since current phase started.")
        .def_readwrite("signal_phase", &Node::signal_phase, "Current signal phase.")
        .def_readonly("in_links", &Node::in_links, "Incoming links to this node.")
        .def_readonly("out_links", &Node::out_links, "Outgoing links from this node.")
        .def_readonly("incoming_vehicles", &Node::incoming_vehicles, "Vehicles that have just arrived at this node.")
        .def_readonly("generation_queue", &Node::generation_queue, "Vehicles waiting to be generated onto outgoing links.")
        .def("generate", &Node::generate,
             R"docstring(
             Generate vehicles from the generation queue.
             
             Attempts to depart vehicles from the generation queue to outgoing links.
             The choice of outgoing link is based on the vehicle's route preference.
             )docstring")
        .def("transfer", &Node::transfer,
             R"docstring(
             Transfer vehicles between links at the node.
             
             Handles the transfer of vehicles from incoming links to outgoing links.
             Considers signal phases, merge priorities, and link capacities.
             )docstring")
        ;

    //
    // MARK: Link
    //
    py::class_<Link>(m, "Link")
        .def(py::init<World *, const std::string &, const std::string &, const std::string &,
                      double, double, double, double, double>(),
             py::arg("world"),
             py::arg("link_name"),
             py::arg("start_node_name"),
             py::arg("end_node_name"),
             py::arg("vmax"),
             py::arg("kappa"), 
             py::arg("length"),
             py::arg("merge_priority"),
             py::arg("capacity_out"),
             R"docstring(
             Create a new Link.

             Parameters
             ----------
             world : World
                 The World object this link belongs to.
             link_name : str
                 Name of the link.
             start_node_name : str
                 Name of the starting node.
             end_node_name : str
                 Name of the ending node.
             vmax : float
                 Free flow speed (m/s).
             kappa : float
                 Jam density (veh/m).
             length : float
                 Length of the link (m).
             merge_priority : float
                 Priority when merging at downstream node.
             capacity_out : float
                 Outflow capacity (veh/s).
             )docstring")
        .def_readonly("W", &Link::w, "Pointer to the world this link belongs to.")
        .def_readonly("id", &Link::id, "Unique identifier for this link.")
        .def_readonly("name", &Link::name, "Name of the link.")
        .def_readwrite("length", &Link::length, "Length of the link in meters.")
        .def_readwrite("u", &Link::vmax, "Free flow speed (m/s).")
        .def_readwrite("vmax", &Link::vmax, "Free flow speed (m/s).")
        .def_readwrite("kappa", &Link::kappa, "Jam density (veh/m).")
        .def_readwrite("delta", &Link::delta, "Minimum spacing per vehicle (m/veh).")
        .def_readwrite("tau", &Link::tau, "Reaction time per vehicle (s/veh).")
        .def_readwrite("capacity", &Link::capacity, "Link capacity (veh/s).")
        .def_readwrite("w", &Link::backward_wave_speed, "Backward wave speed (m/s).")
        .def_readwrite("merge_priority", &Link::merge_priority, "Priority when merging at downstream node.")
        .def_readwrite("capacity_out", &Link::capacity_out, "Outflow capacity (veh/s).")
        .def_readwrite("signal_group", &Link::signal_group, "Signal groups this link belongs to.")
        .def_readonly("start_node", &Link::start_node, "Starting node of the link.")
        .def_readonly("end_node", &Link::end_node, "Ending node of the link.")
        .def_readonly("vehicles", &Link::vehicles, "Vehicles currently on this link (FIFO order).")
        .def_readonly("arrival_curve", &Link::arrival_curve, "Cumulative arrival count over time.")
        .def_readonly("cum_arrival", &Link::arrival_curve, "Cumulative arrival count over time.")
        .def_readonly("departure_curve", &Link::departure_curve, "Cumulative departure count over time.")
        .def_readonly("cum_departure", &Link::departure_curve, "Cumulative departure count over time.")
        .def_readonly("traveltime_real", &Link::traveltime_real, "Actual travel time experienced by vehicles.")
        .def_readonly("traveltime_instant", &Link::traveltime_instant, "Instantaneous travel time based on current conditions.")
        .def("update", &Link::update,
             R"docstring(
             Update link state for current timestep.
             
             Updates travel time calculations and capacity constraints.
             )docstring")
        .def("set_travel_time", &Link::set_travel_time,
             R"docstring(
             Calculate and set travel time metrics.
             
             Computes both actual and instantaneous travel times based on current traffic conditions.
             )docstring")
        ;

    //
    // MARK: Vehicle
    //
    py::class_<Vehicle>(m, "Vehicle")
        .def(py::init<World *, const std::string &, double, const std::string &, const std::string &>(),
             py::arg("world"),
             py::arg("name"),
             py::arg("departure_time"),
             py::arg("orig_name"),
             py::arg("dest_name"),
             R"docstring(
             Create a new Vehicle.

             Parameters
             ----------
             world : World
                 The World object this vehicle belongs to.
             name : str
                 Name of the vehicle.
             departure_time : float
                 Scheduled departure time (seconds).
             orig_name : str
                 Name of the origin node.
             dest_name : str
                 Name of the destination node.
             )docstring")
        .def_readonly("W", &Vehicle::w, "Pointer to the world this vehicle belongs to.")
        .def_readonly("id", &Vehicle::id, "Unique identifier for this vehicle.")
        .def_readwrite("name", &Vehicle::name, "Name of the vehicle.")
        .def_readonly("departure_time", &Vehicle::departure_time, "Scheduled departure time (seconds).")
        .def_readwrite("orig", &Vehicle::orig, "Origin node.")
        .def_readwrite("dest", &Vehicle::dest, "Destination node.")
        .def_readonly("link", &Vehicle::link, "Current link the vehicle is on.")
        .def_readonly("x", &Vehicle::x, "Current position on the link (meters).")
        .def_readonly("x_next", &Vehicle::x_next, "Next position for car-following calculation.")
        .def_readonly("v", &Vehicle::v, "Current speed (m/s).")
        .def_readonly("leader", &Vehicle::leader, "Leading vehicle in the same lane.")
        .def_readonly("follower", &Vehicle::follower, "Following vehicle in the same lane.")
        .def_readonly("state", &Vehicle::state, "Vehicle state: home(0), wait(1), run(2), end(3).")
        .def_readonly("arrival_time_link", &Vehicle::arrival_time_link, "Time when vehicle entered current link.")
        .def_readwrite("route_next_link", &Vehicle::route_next_link, "Next link chosen by route choice.")
        .def_readwrite("route_choice_flag_on_link", &Vehicle::route_choice_flag_on_link, "Flag indicating if route choice has been made on current link.")
        .def_readwrite("route_adaptive", &Vehicle::route_adaptive, "Route adaptation parameter.")
        .def_readwrite("route_preference", &Vehicle::route_preference, "Preference weights for each link.")
        .def_readwrite("links_preferred", &Vehicle::links_preferred, "Preferred links for this vehicle.")
        .def_readonly("log_t", &Vehicle::log_t, "Time log.")
        .def_readonly("log_state", &Vehicle::log_state, "State log.")
        .def_readonly("log_link", &Vehicle::log_link, "Link ID log.")
        .def_readonly("log_x", &Vehicle::log_x, "Position log.")
        .def_readonly("log_v", &Vehicle::log_v, "Speed log.")
        .def_readonly("arrival_time", &Vehicle::arrival_time, "Actual arrival time at destination.")
        .def_readonly("travel_time", &Vehicle::travel_time, "Total travel time (arrival_time - departure_time).")
        // .def("update", &Vehicle::update)
        // .def("end_trip", &Vehicle::end_trip)
        // .def("car_follow_newell", &Vehicle::car_follow_newell)
        // .def("route_choice", &Vehicle::route_choice,
        //      py::arg("principle"),
        //      py::arg("duo_update_weight"),
        //      py::arg("uncertainty"))
        // .def("route_next_link_choice", &Vehicle::route_next_link_choice)
        // .def("route_next_link_choice_old", &Vehicle::route_next_link_choice_old)
        // .def("record_travel_time", &Vehicle::record_travel_time,
        //      py::arg("link"),
        //      py::arg("t"))
        // .def("log_data", &Vehicle::log_data)
        ;

          
    m.def("get_compile_datetime", &get_compile_datetime, "Return the compile date and time");
}
