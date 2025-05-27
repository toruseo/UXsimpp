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
    add_node(W, name, x, y, signal_intervals, signal_offset)
    return W.get_node(name)
World.addNode = addNode

def addLink(W, name, start_node, end_node, length, free_flow_speed=20, jam_density=0.2, merge_priority=1, capacity_out=-1, signal_group=[0]):
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
