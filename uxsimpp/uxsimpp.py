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
    Create a World (simulation environment).

    Parameters
    ----------
    name : str, optional
        The name of the world, default is empty string.
    tmax : float, optional
        The simulation duration, default is 3600 seconds.
    deltan : int, optional
        The platoon size, default is 5 vehicles.
    tau : float, optional
        The reaction time, default is 1 second.
    duo_update_time : float, optional
        The time interval for route choice update, default is 600 seconds.
    duo_update_weight : float, optional
        The update weight for route choice, default is 0.5.
    print_mode : bool, optional
        Whether print the simulation progress or not, default is True.
    random_seed : int or None, optional
        The random seed, default is None.
    vehicle_detailed_log : int, optional
        Whether save vehicle data or not, default is 1.

    Returns
    -------
    World
        World simulation object.
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
    Add a node to the world.

    Parameters
    ----------
    W : World
        The world to which the node belongs.
    name : str
        The name of the node.
    x : float
        The x-coordinate of the node.
    y : float
        The y-coordinate of the node.
    signal_intervals : list of float, optional
        A list representing the signal at the node, default is [0].
    signal_offset : float, optional
        The offset of the signal, default is 0.

    Returns
    -------
    Node
        The created node.
    """
    add_node(W, name, x, y, signal_intervals, signal_offset)
    return W.get_node(name)
World.addNode = addNode

def addLink(W, name, start_node, end_node, length, free_flow_speed=20, jam_density=0.2, merge_priority=1, capacity_out=-1, signal_group=[0]):
    """
    Add a link to the world.

    Parameters
    ----------
    W : World
        The world to which the link belongs.
    name : str
        The name of the link.
    start_node : str or Node
        The name of the start node of the link.
    end_node : str or Node
        The name of the end node of the link.
    length : float
        The length of the link.
    free_flow_speed : float, optional
        The free flow speed on the link, default is 20.
    jam_density : float, optional
        The jam density on the link, default is 0.2.
    merge_priority : float, optional
        The priority of the link when merging, default is 1.
    capacity_out : float, optional
        The capacity out of the link, default is -1 (unlimited).
    signal_group : int or list, optional
        The signal group(s) to which the link belongs, default is [0].

    Returns
    -------
    Link
        The created link.
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
    Add demand (vehicle generation) to the world.

    Parameters
    ----------
    W : World
        The world to which the demand belongs.
    origin : str or Node
        The origin node.
    destination : str or Node
        The destination node.
    start_time : float
        The start time of demand.
    end_time : float
        The end time of demand.
    flow : float
        The flow rate of vehicles.
    links_preferred_list : list of str or Link, optional
        The names of the links the vehicles prefer, default is empty list.
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
    return W.Link_resolve(link_like1, ret_type="name") == W.Link_resolve(link_like2, ret_type="name")
World.eq_Link = eq_Link #TODO: Link.__eq__とLink.__hash__をオーバーライドすべきか？

#####################################################
## MARK: シミュ実行関数

def exec_simulation(W, duration_t=-1, until_t=-1):
    """
    Execute the simulation.

    Parameters
    ----------
    W : World
        The world simulation object.
    duration_t : float, optional
        Duration to run simulation, default is -1 (until completion).
    until_t : float, optional
        Time to run simulation until, default is -1 (until completion).
    """
    W.initialize_adj_matrix()
    W.main_loop(duration_t, until_t)
World.exec_simulation = exec_simulation


#####################################################
## MARK: 簡易状態分析関数

def inflow(l, t1, t2):
    return (l.arrival_curve[int(t2/l.W.delta_t)]-l.arrival_curve[int(t1/l.W.delta_t)])/(t2-t1)
Link.inflow = inflow 

def outflow(l, t1, t2):
    return (l.departure_curve[int(t2/l.W.delta_t)]-l.departure_curve[int(t1/l.W.delta_t)])/(t2-t1)
Link.outflow = outflow 

def link_inflow(W, l, t1, t2):
    if type(l) is str:
        l = W.get_link(l)
    return l.inflow(t1, t2)
World.link_inflow = link_inflow

def link_outflow(W, l, t1, t2):
    if type(l) is str:
        l = W.get_link(l)
    return l.outflow(t1, t2)
World.link_outflow = link_outflow


#####################################################
## MARK: 簡易可視化

def plot_cumcurves(l, col):
    plt.plot([t*l.W.delta_t for t in range(len(l.arrival_curve))], l.arrival_curve, color=col)
    plt.plot([t*l.W.delta_t for t in range(len(l.arrival_curve))], l.departure_curve, color=col)


#####################################################
## MARK: util

def eq_tol(val, check, rel_tol=0.1, abs_tol=0.0, print_mode=True):
    """
    function for tests
    """
    if check == 0 and abs_tol == 0:
        abs_tol = 0.1
    if print_mode:
        print(val, check)
    return abs(val - check) <= abs(check*rel_tol) + abs_tol

def show_variables():
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
