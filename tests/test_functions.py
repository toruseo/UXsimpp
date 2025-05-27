import pytest
import sys, os
import random
import warnings
from collections import defaultdict

import numpy as np


sys.path.append("..")

from uxsimpp import eq_tol
from uxsimpp import *

warnings.filterwarnings("ignore", message=".*cannot collect 'test' because it is not a function.*")

####################################################
## MARK: Analyzer

def test_analyzer():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=5.0,
        tau=1.0,
        duo_update_time=300.0,
        duo_update_weight=0.25,
        print_mode=1,
        random_seed=42
    )

    W.addNode("orig", 0, 0)
    W.addNode("mid", 1, 0, signal_intervals=[60,60])
    W.addNode("dest", 1, 1)

    link1 = W.addLink("link1", "orig", "mid", 10000, 20, 0.2, 1, signal_group=0)
    link2 = W.addLink("link2", "mid", "dest", 10000, 20, 0.2, 1)

    W.adddemand("orig", "dest", 0,   1000, 0.4)
    W.adddemand("orig", "dest", 1000,   2000, 0.6)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()


    ana = Analyzer(W)

    ana.plot_time_space_trajectories(["link1", "link2"])

    ana.network(t=1500, image_return=True)

    ana.network_anim(state_variables="flow_delay")

    ana.network_fancy()

    print(ana.df_vehicle_details(0))
    print(ana.df_vehicles())
    print(ana.df_link_details(0))
    print(ana.df_links())
    
    assert True

def test_garbage_collection_and_pointer():
    """
    Strange behavior possibly due to raw pointer in C++ code and garbage collection of Python

    If `Ws.append(W)` is active, the last print sentences work as intended.
    If it is commented out, they work strangely.
    At least it does not cause an error?
    """

    def create_world(demand):
        W = newWorld(
            name=f"basic{demand}",
            deltan=5,
            tmax=1200,
            random_seed=42
        )

        W.addNode("orig1", 0, 0)
        W.addNode("orig2", 0, 2)
        W.addNode("merge", 1, 1)
        W.addNode("dest", 2, 1)

        W.addLink("link1", "orig1", "merge", 1000, 20, 0.2, 1)
        link = W.addLink("link2", "orig2", "merge", 1000, 20, 0.2, 1)
        W.addLink("link3", "merge", "dest", 1000, 20, 0.2, 1)

        W.adddemand("orig1", "dest", 0, 1000, 0.45)
        W.adddemand("orig2", "dest", 400, 1000, demand)

        return W, link

    links = []
    Ws = []
    for demand in [0, 0.3, 0.6, 0.8]:
        W, link = create_world(demand)
        W.print_scenario_stats()

        W.exec_simulation()
        W.print_simple_results()

        ana = Analyzer(W, show_mode=True, save_mode=True)

        #Ws.append(W)
        links.append(link)

    print(links)
    print([type(l.W) for l in links])
    print([l.W.name for l in links])

    assert True