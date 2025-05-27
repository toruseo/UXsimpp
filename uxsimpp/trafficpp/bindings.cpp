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
          "Create a new World simulation object.");

    m.def("add_node", &add_node,
          py::arg("world"),
          py::arg("node_name"),
          py::arg("x"),
          py::arg("y"),
          py::arg("signal_intervals"),
          py::arg("signal_offset"),
          "Add a new Node to the World");

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
          "Add a new Link to the World");

    m.def("add_demand", &add_demand,
          py::arg("world"),
          py::arg("orig_name"),
          py::arg("dest_name"),
          py::arg("start_t"),
          py::arg("end_t"),
          py::arg("flow"),
          py::arg("links_preferred_str"),
          "Add demand (vehicle generation) in the World");

    //
    // 2) MARK: World
    //
    py::class_<World>(m, "World")
        .def("initialize_adj_matrix", &World::initialize_adj_matrix)
        .def("print_scenario_stats", &World::print_scenario_stats)
        .def("main_loop", &World::main_loop)
        .def("check_simulation_ongoing", &World::check_simulation_ongoing)
        .def("print_simple_results", &World::print_simple_results)
        .def("update_adj_time_matrix", &World::update_adj_time_matrix)
        .def("get_node", &World::get_node,
             py::return_value_policy::reference,
             "Get a Node by name (reference)")
        .def("get_link", &World::get_link,
             py::return_value_policy::reference,
             "Get a Link by name (reference)")
        .def("get_vehicle", &World::get_vehicle,
             py::return_value_policy::reference,
             "Get a Vehicle by name (reference)")
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
             py::arg("y"))
        .def_readonly("W", &Node::w)
        .def_readonly("id", &Node::id)
        .def_readonly("name", &Node::name)
        .def_readwrite("x", &Node::x)
        .def_readwrite("y", &Node::y)
        .def_readwrite("signal_intervals", &Node::signal_intervals)
        .def_readwrite("signal_offset", &Node::signal_offset)
        .def_readwrite("signal_t", &Node::signal_t)
        .def_readwrite("signal_phase", &Node::signal_phase)
        .def_readonly("in_links", &Node::in_links)
        .def_readonly("out_links", &Node::out_links)
        .def_readonly("incoming_vehicles", &Node::incoming_vehicles)
        .def_readonly("generation_queue", &Node::generation_queue)
        .def("generate", &Node::generate)
        .def("transfer", &Node::transfer)
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
             py::arg("capacity_out"))
        .def_readonly("W", &Link::w)
        .def_readonly("id", &Link::id)
        .def_readonly("name", &Link::name)
        .def_readwrite("length", &Link::length)
        .def_readwrite("u", &Link::vmax)
        .def_readwrite("vmax", &Link::vmax)
        .def_readwrite("kappa", &Link::kappa)
        .def_readwrite("delta", &Link::delta)
        .def_readwrite("tau", &Link::tau)
        .def_readwrite("capacity", &Link::capacity)
        .def_readwrite("w", &Link::backward_wave_speed)
        .def_readwrite("merge_priority", &Link::merge_priority)
        .def_readwrite("capacity_out", &Link::capacity_out)
        .def_readwrite("signal_group", &Link::signal_group)
        .def_readonly("start_node", &Link::start_node)
        .def_readonly("end_node", &Link::end_node)
        .def_readonly("vehicles", &Link::vehicles)
        .def_readonly("arrival_curve", &Link::arrival_curve)
        .def_readonly("cum_arrival", &Link::arrival_curve)
        .def_readonly("departure_curve", &Link::departure_curve)
        .def_readonly("cum_departure", &Link::departure_curve)
        .def_readonly("traveltime_real", &Link::traveltime_real)
        .def_readonly("traveltime_instant", &Link::traveltime_instant)
        .def("update", &Link::update)
        .def("set_travel_time", &Link::set_travel_time)
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
             py::arg("dest_name"))
        .def_readonly("W", &Vehicle::w)
        .def_readonly("id", &Vehicle::id)
        .def_readwrite("name", &Vehicle::name)
        .def_readonly("departure_time", &Vehicle::departure_time)
        .def_readwrite("orig", &Vehicle::orig)
        .def_readwrite("dest", &Vehicle::dest)
        .def_readonly("link", &Vehicle::link)
        .def_readonly("x", &Vehicle::x)
        .def_readonly("x_next", &Vehicle::x_next)
        .def_readonly("v", &Vehicle::v)
        .def_readonly("leader", &Vehicle::leader)
        .def_readonly("follower", &Vehicle::follower)
        .def_readonly("state", &Vehicle::state)
        .def_readonly("arrival_time_link", &Vehicle::arrival_time_link)
        .def_readwrite("route_next_link", &Vehicle::route_next_link)
        .def_readwrite("route_choice_flag_on_link", &Vehicle::route_choice_flag_on_link)
        .def_readwrite("route_adaptive", &Vehicle::route_adaptive)
        .def_readwrite("route_preference", &Vehicle::route_preference)
        .def_readwrite("links_preferred", &Vehicle::links_preferred)
        .def_readonly("log_t", &Vehicle::log_t)
        .def_readonly("log_state", &Vehicle::log_state)
        .def_readonly("log_link", &Vehicle::log_link)
        .def_readonly("log_x", &Vehicle::log_x)
        .def_readonly("log_v", &Vehicle::log_v)
        .def_readonly("arrival_time", &Vehicle::arrival_time)
        .def_readonly("travel_time", &Vehicle::travel_time)
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
