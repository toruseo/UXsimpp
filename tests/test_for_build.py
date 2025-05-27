import pytest
import sys, os
import random
import warnings
from collections import defaultdict

import numpy as np


sys.path.append("..")

from uxsimpp import create_world, eq_tol
from uxsimpp import *


warnings.filterwarnings("ignore", message=".*cannot collect 'test' because it is not a function.*")



####################################################
## MARK: Straight

def test_1link_freeflow():
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
    W.addNode("dest", 1, 0)

    link = W.addLink("link", "orig", "dest", 10000, 20, 0.2, 1)

    W.adddemand("orig", "dest", 0,   1000, 0.5)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    assert eq_tol(link.inflow(0,1000), 0.5)
    assert eq_tol(link.inflow(1000,2000), 0) 

    assert eq_tol(link.outflow(0,500), 0) 
    assert eq_tol(link.outflow(500,1500), 0.5)
    assert eq_tol(link.outflow(1500,2500), 0) 

    assert eq_tol(W.VEHICLES[0].travel_time, 500)
    assert eq_tol(W.VEHICLES[-1].travel_time, 500)


def test_merge_free():
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

    W.addNode("orig1", 0, 0)
    W.addNode("orig2", 0, 2)
    W.addNode("merge", 1, 1)
    W.addNode("dest", 2, 1)

    l1 = W.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 1)
    l2 = W.addLink("link2", "orig2", "merge", 10000, 20, 0.2,  1)
    l3 = W.addLink("link3", "merge", "dest",10000,  20, 0.2, 1)

    W.adddemand("orig1", "dest", 0,   1000, 0.3)
    W.adddemand("orig2", "dest", 0, 1000, 0.3)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    assert eq_tol(l1.inflow(0,1000), 0.3)
    assert eq_tol(l1.outflow(500,1500), 0.3)
    assert eq_tol(l1.outflow(1500,2000), 0)

    assert eq_tol(l2.inflow(0,1000), 0.3)
    assert eq_tol(l2.outflow(500,1500), 0.3)
    assert eq_tol(l2.outflow(1500,2000), 0)

    assert eq_tol(l3.inflow(0,500), 0.0)
    assert eq_tol(l3.inflow(500,1500), 0.6)
    assert eq_tol(l3.inflow(1500,2000), 0.0)

    assert eq_tol(l3.outflow(0,1000), 0.0)
    assert eq_tol(l3.outflow(1000,2000), 0.6)
    assert eq_tol(l3.outflow(2000,2900), 0.0)


def test_routechoice_faster_1route():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=5.0,
        tau=1.0,
        duo_update_time=300.0,
        duo_update_weight=0.25,
        print_mode=1,
        random_seed=random.randint(0,999999)
    )

    W.addNode("orig", 0, 0)
    W.addNode("mid1", 1, 1)
    W.addNode("mid2", 0, 0)
    W.addNode("dest", 2, 1)

    l1a = W.addLink("link1a", "orig", "mid1", 1000, 20, 0.2, 1)
    l1b = W.addLink("link1b", "mid1", "dest", 1000, 20, 0.2, 1,)
    l2a = W.addLink("link2a", "orig", "mid2", 1000, 10, 0.2, 1)
    l2b = W.addLink("link2b", "mid2", "dest", 1000, 10, 0.2, 1,)

    W.adddemand("orig", "dest", 0, 1000, 0.6)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    # figure()
    # plot_cumcurves(l1a, "b")
    # plot_cumcurves(l2a, "r")
    # grid()
    # show()

    assert eq_tol(l1a.inflow(0,1000), 0.6)
    assert eq_tol(l2a.inflow(0,1000), 0)


def test_route_specified():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=5.0,
        tau=1.0,
        duo_update_time=300.0,
        duo_update_weight=0.25,
        print_mode=1,
        random_seed=random.randint(0,999999)
    )

    W.addNode("orig0", 0, 0)
    W.addNode("orig", 0, 0)
    W.addNode("mid1", 1, 1)
    W.addNode("mid2", 0, 0)
    W.addNode("dest", 2, 1)

    l0 = W.addLink("link0", "orig0", "orig", 1000, 20, 0.2, 1)
    l1a = W.addLink("link1a", "orig", "mid1", 1000, 20, 0.2, 1)
    l1b = W.addLink("link1b", "mid1", "dest", 1000, 20, 0.2, 1,)
    l2a = W.addLink("link2a", "orig", "mid2", 1000, 10, 0.2, 1)
    l2b = W.addLink("link2b", "mid2", "dest", 1000, 10, 0.2, 1,)

    W.adddemand("orig0", "dest", 0, 1000, 0.6, links_preferred_list=["link2a", "link2b"])

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results() 

    # figure()
    # plot_cumcurves(l1a, "b")
    # plot_cumcurves(l2a, "r")
    # grid()
    # show()

    assert eq_tol(l1a.inflow(0,1000), 0)
    assert eq_tol(l2a.inflow(50,1050), 0.6)
    

def test_signal_straight():
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
    W.addNode("mid", 0.5, 0, signal_intervals=[60,60])
    W.addNode("dest", 1, 0)

    link1 = W.addLink("link1", "orig", "mid", 10000, 20, 0.2, 1, signal_group=0)
    link2 = W.addLink("link2", "mid", "dest", 10000, 20, 0.2, 1)

    W.adddemand("orig", "dest", 0,   1000, 0.4)
    W.adddemand("orig", "dest", 1000,   2000, 0.8)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    #plot_cumcurves(link1, col="r")

    assert eq_tol(link1.outflow(500,2500), 0.4)
    assert eq_tol(link1.outflow(500,1500), 0.4)
    assert eq_tol(link1.outflow(1500,2500), 0.4)

def test_iterative_execution():
    random.seed(None)
    for i in range(10):
        seed = random.randint(0,300)
        # iter 1
        W = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=1,
            random_seed=seed
        )

        W.addNode("orig1", 0, 0)
        W.addNode("orig2", 0, 2)
        W.addNode("merge", 1, 1)
        W.addNode("dest", 2, 1)

        l1 = W.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 1)
        l2 = W.addLink("link2", "orig2", "merge", 10000, 20, 0.2, 1)
        l3 = W.addLink("link3", "merge", "dest", 10000, 20, 0.2, 1)

        W.adddemand("orig1", "dest", 0,   1000, 0.5)
        W.adddemand("orig2", "dest", 0, 1000, 0.5)

        W.print_scenario_stats()
        W.exec_simulation()
        W.print_simple_results()

        vehicle_log_x = W.VEHICLES[160].log_x
        vehicle_log_v = W.VEHICLES[160].log_v

        print("iter 1 finished")

        ###################################
        # iter 2
        W2 = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=1,
            random_seed=seed
        )

        W2.addNode("orig1", 0, 0)
        W2.addNode("orig2", 0, 2)
        W2.addNode("merge", 1, 1)
        W2.addNode("dest", 2, 1)

        l1 = W2.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 1)
        l2 = W2.addLink("link2", "orig2", "merge", 10000, 20, 0.2, 1)
        l3 = W2.addLink("link3", "merge", "dest", 10000, 20, 0.2, 1)

        W2.adddemand("orig1", "dest", 0,   1000, 0.5)
        W2.adddemand("orig2", "dest", 0, 1000, 0.5)


        W2.print_scenario_stats()
        while W2.check_simulation_ongoing():
            if W2.time < 50:
                t = random.randint(0,20)
            else:
                t = random.randint(0,300)
            print(t)
            W2.exec_simulation(duration_t=t)
        W2.print_simple_results()
        print("iter 2 finished")

        vehicle_log_x2 = W2.VEHICLES[160].log_x
        vehicle_log_v2 = W2.VEHICLES[160].log_v

        assert sum(vehicle_log_x) == sum(vehicle_log_x2)
        assert np.average(vehicle_log_v)==np.average(vehicle_log_v2)

        print("COMPLETED")

def test_iterative_execution_until_t():
    random.seed(None)
    for i in range(10):
        seed = random.randint(0,300)
        # iter 1
        W = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=1,
            random_seed=seed
        )

        W.addNode("orig1", 0, 0)
        W.addNode("orig2", 0, 2)
        W.addNode("merge", 1, 1)
        W.addNode("dest", 2, 1)

        l1 = W.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 1)
        l2 = W.addLink("link2", "orig2", "merge", 10000, 20, 0.2, 1)
        l3 = W.addLink("link3", "merge", "dest", 10000, 20, 0.2, 1)

        W.adddemand("orig1", "dest", 0,   1000, 0.5)
        W.adddemand("orig2", "dest", 0, 1000, 0.5)

        W.print_scenario_stats()
        W.exec_simulation()
        W.print_simple_results()

        vehicle_log_x = W.VEHICLES[160].log_x
        vehicle_log_v = W.VEHICLES[160].log_v

        print("iter 1 finished")

        ###################################
        # iter 2
        W2 = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=1,
            random_seed=seed
        )

        W2.addNode("orig1", 0, 0)
        W2.addNode("orig2", 0, 2)
        W2.addNode("merge", 1, 1)
        W2.addNode("dest", 2, 1)

        l1 = W2.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 1)
        l2 = W2.addLink("link2", "orig2", "merge", 10000, 20, 0.2, 1)
        l3 = W2.addLink("link3", "merge", "dest", 10000, 20, 0.2, 1)

        W2.adddemand("orig1", "dest", 0,   1000, 0.5)
        W2.adddemand("orig2", "dest", 0, 1000, 0.5)

        W2.print_scenario_stats()
        while W2.check_simulation_ongoing():
            if W2.time < 50:
                t = random.randint(0,20)
            else:
                t = random.randint(0,300)
            print(t)
            W2.exec_simulation(until_t=W2.time+t)
        W2.print_simple_results()
        print("iter 2 finished")

        vehicle_log_x2 = W2.VEHICLES[160].log_x
        vehicle_log_v2 = W2.VEHICLES[160].log_v

        assert sum(vehicle_log_x) == sum(vehicle_log_x2)
        assert np.average(vehicle_log_v)==np.average(vehicle_log_v2)

        print("COMPLETED")
