import random
from collections.abc import Iterable
import numpy as np
import matplotlib.pyplot as plt
import sys

################################
# C++拡張モジュールからクラスと関数をインポート
from . import trafficppy

World = trafficppy.World
Link = trafficppy.Link
Node = trafficppy.Node
Vehicle = trafficppy.Vehicle
create_world = trafficppy.create_world
add_node = trafficppy.add_node
add_link = trafficppy.add_link
add_demand = trafficppy.add_demand

################################

from .analyzer import *
from .utils import *


#####################################################
## MARK: シナリオ定義関数

def newWorld(name="", 
             tmax=3600, deltan=5, tau=1,
             duo_update_time=600, duo_update_weight=0.5, 
             print_mode=True,
             random_seed=None,
             vehicle_detailed_log=1):
    """
    Create a new traffic simulation world.

    Parameters
    ----------
    name : str, optional
        Name of the world. Default is "".
    tmax : int, optional
        Maximum simulation time in seconds. Default is 3600.
    deltan : int, optional
        Time step for simulation in seconds. Default is 5.
    tau : int, optional
        Reaction time parameter. Default is 1.
    duo_update_time : int, optional
        Time interval for dynamic user optimization update. Default is 600.
    duo_update_weight : float, optional
        Weight for dynamic user optimization update. Default is 0.5.
    print_mode : bool, optional
        Whether to print simulation progress. Default is True.
    random_seed : int, optional
        Random seed for simulation. If None, a random seed is generated.
    vehicle_detailed_log : int, optional
        Level of vehicle logging detail. Default is 1.

    Returns
    -------
    World
        A new World instance for traffic simulation.
    """
    
    if random_seed is None:
        random_seed = random.randint(0, 2**8)

    W = create_world(
        name,              # world_name
        tmax,              # t_max
        deltan,           # delta_n
        tau,               # tau
        duo_update_time,   # duo_update_time
        duo_update_weight, # duo_update_weight
        0,                 # route_choice_uncertainty
        int(print_mode),        # print_mode
        random_seed,       # random_seed
        vehicle_detailed_log,  # vehicle_log_mode 
    )

    return W

def addNode(W, name, x, y, signal_intervals=[0], signal_offset=0):
    """
    Add a node to the traffic simulation world.

    Parameters
    ----------
    W : World
        The world instance to add the node to.
    name : str
        Name of the node.
    x : float
        X coordinate of the node.
    y : float
        Y coordinate of the node.
    signal_intervals : list of int, optional
        Signal timing intervals. Default is [0].
    signal_offset : int, optional
        Signal timing offset. Default is 0.

    Returns
    -------
    Node
        The created node instance.
    """
    add_node(W, name, x, y, signal_intervals, signal_offset)
    return W.get_node(name)
World.addNode = addNode

def addLink(W, name, start_node, end_node, length, free_flow_speed=20, jam_density=0.2, merge_priority=1, capacity_out=-1, signal_group=[0]):
    """
    Add a link to the traffic simulation world.

    Parameters
    ----------
    W : World
        The world instance to add the link to.
    name : str
        Name of the link.
    start_node : Node or str
        Starting node of the link.
    end_node : Node or str
        Ending node of the link.
    length : float
        Length of the link in meters.
    free_flow_speed : float, optional
        Free flow speed in m/s. Default is 20.
    jam_density : float, optional
        Jam density in vehicles per meter. Default is 0.2.
    merge_priority : int, optional
        Merge priority for the link. Default is 1.
    capacity_out : float, optional
        Output capacity. Default is -1 (unlimited).
    signal_group : list of int, optional
        Signal group assignment. Default is [0].

    Returns
    -------
    Link
        The created link instance.
    """
    if type(start_node) == Node:
        start_node = start_node.name
    if type(end_node) == Node:
        end_node = end_node.name

    if isinstance(signal_group, Iterable) and not isinstance(signal_group, (str, bytes)):
        signal_group = list(signal_group)
    else:
        signal_group = [signal_group]

    add_link(W, name, start_node, end_node, free_flow_speed, jam_density, length, merge_priority, capacity_out, signal_group)
    return W.get_link(name)
World.addLink = addLink

def adddemand(W, origin, destination, start_time, end_time, flow, links_preferred_list=[]):
    """
    Add traffic demand to the simulation world.

    Parameters
    ----------
    W : World
        The world instance to add the demand to.
    origin : Node or str
        Origin node for the demand.
    destination : Node or str
        Destination node for the demand.
    start_time : float
        Start time of the demand in seconds.
    end_time : float
        End time of the demand in seconds.
    flow : float
        Traffic flow rate in vehicles per second.
    links_preferred_list : list of Link or str, optional
        List of preferred links for routing. Default is [].

    Returns
    -------
    None
    """
    if type(origin) == Node:
        origin = origin.name
    if type(destination) == Node:
        destination = destination.name
    for i in range(len(links_preferred_list)):
        if type(links_preferred_list[i]) == Link:
            links_preferred_list[i] = links_preferred_list[i].name
    add_demand(W, origin, destination, start_time, end_time, flow, links_preferred_list)
World.adddemand = adddemand

def link__repr__(s):
    return f"<Link `{s.name}`>"
Link.__repr__ = link__repr__

def node__repr__(s):
    return f"<Node `{s.name}`>"
Node.__repr__ = node__repr__

def veh__repr__(s):
    return f"<Vehicle `{s.name}`>"
Vehicle.__repr__ = veh__repr__

#####################################################
## MARK: インスタンス-name-idの変換関数など

def Link_resolve(W, link_like, ret_type="instance"):
    """
    Resolve a link-like object to a Link instance, name, or ID.

    Parameters
    ----------
    W : World
        The world instance containing the link.
    link_like : Link, str, or int
        Link instance, name, or ID to resolve.
    ret_type : str, optional
        Return type: "instance", "name", or "id". Default is "instance".

    Returns
    -------
    Link, str, or int
        The resolved link in the requested format.

    Raises
    ------
    ValueError
        If the link_like or ret_type is unknown.
    """
    instance = None
    if isinstance(link_like, Link):
        instance = link_like
    elif isinstance(link_like, str):
        instance = W.get_link(link_like)
    elif isinstance(link_like, int):
        instance = W.LINKS[link_like]
    else:
        raise ValueError(f"Unknown Link {link_like}")
    
    if ret_type == "instance":
        return instance
    elif ret_type == "name":
        return instance.name
    elif ret_type == "id":
        return instance.id
    else:
        raise ValueError(f"Unknown ret_type {ret_type}")
World.Link_resolve = Link_resolve

def eq_Link(W, link_like1, link_like2):
    """
    Check if two link-like objects refer to the same link.

    Parameters
    ----------
    W : World
        The world instance containing the links.
    link_like1 : Link, str, or int
        First link to compare.
    link_like2 : Link, str, or int
        Second link to compare.

    Returns
    -------
    bool
        True if both link-like objects refer to the same link.
    """
    return W.Link_resolve(link_like1, ret_type="name") == W.Link_resolve(link_like2, ret_type="name")
World.eq_Link = eq_Link #TODO: Link.__eq__とLink.__hash__をオーバーライドすべきか？

#####################################################
## MARK: シミュ実行関数

def exec_simulation(W, duration_t=-1, until_t=-1):
    """
    Execute the traffic simulation.

    Parameters
    ----------
    W : World
        The world instance to simulate.
    duration_t : float, optional
        Duration of simulation in seconds. Default is -1 (use world's tmax).
    until_t : float, optional
        Simulate until this time in seconds. Default is -1 (use world's tmax).

    Returns
    -------
    None
    """
    W.initialize_adj_matrix()
    W.main_loop(duration_t, until_t)
World.exec_simulation = exec_simulation


#####################################################
## MARK: 簡易状態分析関数

def inflow(l, t1, t2):
    """
    Calculate the inflow rate of a link between two time points.

    Parameters
    ----------
    l : Link
        The link to analyze.
    t1 : float
        Start time in seconds.
    t2 : float
        End time in seconds.

    Returns
    -------
    float
        Inflow rate in vehicles per second.
    """
    return (l.arrival_curve[int(t2/l.W.delta_t)]-l.arrival_curve[int(t1/l.W.delta_t)])/(t2-t1)
Link.inflow = inflow 

def outflow(l, t1, t2):
    """
    Calculate the outflow rate of a link between two time points.

    Parameters
    ----------
    l : Link
        The link to analyze.
    t1 : float
        Start time in seconds.
    t2 : float
        End time in seconds.

    Returns
    -------
    float
        Outflow rate in vehicles per second.
    """
    return (l.departure_curve[int(t2/l.W.delta_t)]-l.departure_curve[int(t1/l.W.delta_t)])/(t2-t1)
Link.outflow = outflow 

def link_inflow(W, l, t1, t2):
    """
    Calculate the inflow rate of a link between two time points.

    Parameters
    ----------
    W : World
        The world instance containing the link.
    l : Link or str
        The link to analyze or its name.
    t1 : float
        Start time in seconds.
    t2 : float
        End time in seconds.

    Returns
    -------
    float
        Inflow rate in vehicles per second.
    """
    if type(l) is str:
        l = W.get_link(l)
    return l.inflow(t1, t2)
World.link_inflow = link_inflow

def link_outflow(W, l, t1, t2):
    """
    Calculate the outflow rate of a link between two time points.

    Parameters
    ----------
    W : World
        The world instance containing the link.
    l : Link or str
        The link to analyze or its name.
    t1 : float
        Start time in seconds.
    t2 : float
        End time in seconds.

    Returns
    -------
    float
        Outflow rate in vehicles per second.
    """
    if type(l) is str:
        l = W.get_link(l)
    return l.outflow(t1, t2)
World.link_outflow = link_outflow


#####################################################
## MARK: 簡易可視化

def plot_cumcurves(l, col):
    """
    Plot cumulative arrival and departure curves for a link.

    Parameters
    ----------
    l : Link
        The link to plot curves for.
    col : str
        Color for the plot lines.

    Returns
    -------
    None
    """
    plt.plot([t*l.W.delta_t for t in range(len(l.arrival_curve))], l.arrival_curve, color=col)
    plt.plot([t*l.W.delta_t for t in range(len(l.arrival_curve))], l.departure_curve, color=col)


#####################################################
## MARK: util

def eq_tol(val, check, rel_tol=0.1, abs_tol=0.0, print_mode=True):
    """
    Check if two values are equal within tolerance for testing purposes.

    Parameters
    ----------
    val : float
        The value to check.
    check : float
        The expected value.
    rel_tol : float, optional
        Relative tolerance. Default is 0.1.
    abs_tol : float, optional
        Absolute tolerance. Default is 0.0.
    print_mode : bool, optional
        Whether to print the values. Default is True.

    Returns
    -------
    bool
        True if values are equal within tolerance.
    """
    if check == 0 and abs_tol == 0:
        abs_tol = 0.1
    if print_mode:
        print(val, check)
    return abs(val - check) <= abs(check*rel_tol) + abs_tol

def show_variables():
    """
    Display available variables and methods for UXsim++ classes.

    Returns
    -------
    None
    """
    dir_list = [e for e in dir() if not e.startswith("_")]
    dir_list_World = [e for e in dir(World) if not e.startswith("_")]
    dir_list_Link = [e for e in dir(Link) if not e.startswith("_")]
    dir_list_Node = [e for e in dir(Node) if not e.startswith("_")]
    dir_list_Vehicle = [e for e in dir(Vehicle) if not e.startswith("_")]

    print("module:")
    for e in dir_list:
        print("\t", e)
    print("World:")
    for e in dir_list_World:
        print("\t", e)
    print("Node:")
    for e in dir_list_Node:
        print("\t", e)
    print("Link:")
    for e in dir_list_Link:
        print("\t", e)
    print("Vehicle:")
    for e in dir_list_Vehicle:
        print("\t", e)
