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

def test_2link_freeflow():
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
    W.addNode("mid", 0.5, 0)
    W.addNode("dest", 1, 0)

    link1 = W.addLink("link1", "orig", "mid", 10000, 20, 0.2, 1)
    link2 = W.addLink("link2", "mid", "dest", 10000, 20, 0.2, 1)

    W.adddemand("orig", "dest", 0,   1000, 0.5)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    assert eq_tol(link1.inflow(0,1000), 0.5)
    assert eq_tol(link1.inflow(1000,2000), 0) 

    assert eq_tol(link1.outflow(0,500), 0) 
    assert eq_tol(link1.outflow(500,1500), 0.5)
    assert eq_tol(link1.outflow(1500,2500), 0) 

    assert eq_tol(link2.inflow(0,500), 0) 
    assert eq_tol(link2.inflow(500,1500), 0.5)
    assert eq_tol(link2.inflow(1500,2000), 0) 

    assert eq_tol(link2.outflow(0,1000), 0) 
    assert eq_tol(link2.outflow(1000,2000), 0.5)
    assert eq_tol(link2.outflow(2000,2900), 0) 

    assert eq_tol(W.VEHICLES[0].travel_time, 1000)
    assert eq_tol(W.VEHICLES[-1].travel_time, 1000)
    
def test_1link_freeflow_deltan1():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=1.0,
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

def test_2link_freeflow_deltan1():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=1.0,
        tau=1.0,
        duo_update_time=300.0,
        duo_update_weight=0.25,
        print_mode=1,
        random_seed=42
    )

    W.addNode("orig", 0, 0)
    W.addNode("mid", 0.5, 0)
    W.addNode("dest", 1, 0)

    link1 = W.addLink("link1", "orig", "mid", 10000, 20, 0.2, 1)
    link2 = W.addLink("link2", "mid", "dest", 10000, 20, 0.2, 1)

    W.adddemand("orig", "dest", 0,   1000, 0.5)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    assert eq_tol(link1.inflow(0,1000), 0.5)
    assert eq_tol(link1.inflow(1000,2000), 0) 

    assert eq_tol(link1.outflow(0,500), 0) 
    assert eq_tol(link1.outflow(500,1500), 0.5)
    assert eq_tol(link1.outflow(1500,2500), 0) 

    assert eq_tol(link2.inflow(0,500), 0) 
    assert eq_tol(link2.inflow(500,1500), 0.5)
    assert eq_tol(link2.inflow(1500,2000), 0) 

    assert eq_tol(link2.outflow(0,1000), 0) 
    assert eq_tol(link2.outflow(1000,2000), 0.5)
    assert eq_tol(link2.outflow(2000,2900), 0) 

    assert eq_tol(W.VEHICLES[0].travel_time, 1000)
    assert eq_tol(W.VEHICLES[-1].travel_time, 1000)


def test_bottleneck():
    W = newWorld(
        "test",
        tmax=10000.0,
        deltan=5.0,
        tau=1.0,
        duo_update_time=300.0,
        duo_update_weight=0.25,
        print_mode=1,
        random_seed=42
    )

    W.addNode("orig", 0, 0)
    W.addNode("mid", 0.5, 0)
    W.addNode("dest", 1, 0)

    link1 = W.addLink("link1", "orig", "mid", 10000, 20, 0.2, 1, capacity_out=0.4)
    link2 = W.addLink("link2", "mid", "dest", 10000, 20, 0.2, 1)

    W.adddemand("orig", "dest", 0,   1000, 0.2)
    W.adddemand("orig", "dest", 500,   1000, 0.6)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    # figure()
    # plot_cumcurves(link1, "b")
    # plot_cumcurves(link2, "r")
    # xlim([0,2000])

    assert eq_tol(link1.inflow(0, 500), 0.2)
    assert eq_tol(link1.inflow(500, 1000), 0.8)
    assert eq_tol(link1.outflow(500, 1000), 0.2)
    assert eq_tol(link1.outflow(1000, 2000), 0.4)
    assert eq_tol(link2.inflow(500, 1000), 0.2)
    assert eq_tol(link2.inflow(1000, 2000), 0.4)
    assert eq_tol(W.VEHICLES[0].travel_time, 1000)
    assert eq_tol(W.VEHICLES[-1].travel_time, 1500)

####################################################
## MARK: Merge


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

def test_merge_saturation():
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

    W.addNode("orig1", 0, 0)
    W.addNode("orig2", 0, 2)
    W.addNode("merge", 1, 1)
    W.addNode("dest", 2, 1)

    l1 = W.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 1)
    l2 = W.addLink("link2", "orig2", "merge", 10000, 20, 0.2,  1)
    l3 = W.addLink("link3", "merge", "dest", 10000, 20, 0.2,  1)

    W.adddemand("orig1", "dest", 0,   1000, 0.4)
    W.adddemand("orig2", "dest", 0, 1000, 0.4)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    assert eq_tol(l1.inflow(0,1000), 0.4)
    assert eq_tol(l1.outflow(500,1500), 0.4)
    assert eq_tol(l1.outflow(1500,2000), 0)

    assert eq_tol(l2.inflow(0,1000), 0.4)
    assert eq_tol(l2.outflow(500,1500), 0.4)
    assert eq_tol(l2.outflow(1500,2000), 0)

    assert eq_tol(l3.inflow(0,500), 0.0)
    assert eq_tol(l3.inflow(500,1500), 0.8)
    assert eq_tol(l3.inflow(1500,2000), 0.0)

    assert eq_tol(l3.outflow(0,1000), 0.0)
    assert eq_tol(l3.outflow(1000,2000), 0.8)
    assert eq_tol(l3.outflow(2000,2900), 0.0)

@pytest.mark.flaky(reruns=5)
def test_merge_congested():
    res = defaultdict(list)
    for i in range(10):
        W = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=1,
            random_seed=random.randint(0,1000)
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

        res["l1 inflow flowing"].append(l1.inflow(0,1000))
        res["l1 inflow after"].append(l1.inflow(1000,2000))
        res["l1 outflow flowing"].append(l1.outflow(500,500+1250))
        res["l1 outflow after"].append(l1.outflow(500+1250,500+1250+500))

        res["l2 inflow flowing"].append(l2.inflow(0,1000))
        res["l2 inflow after"].append(l2.inflow(1000,2000))
        res["l2 outflow flowing"].append(l2.outflow(500,500+1250))
        res["l2 outflow after"].append(l2.outflow(500+1250,500+1250+500))
        
        res["l3 inflow before"].append(l3.inflow(0,500))
        res["l3 inflow flowing"].append(l3.inflow(500,500+1250))
        res["l3 inflow after"].append(l3.inflow(500+1250,500+1250+500))

    for key in res:
        res[key] = np.mean(res[key])

    assert eq_tol(res["l1 inflow flowing"], 0.5)
    assert eq_tol(res["l1 inflow after"], 0)
    assert eq_tol(res["l1 outflow flowing"], 0.4)
    assert eq_tol(res["l1 outflow after"], 0)

    assert eq_tol(res["l2 inflow flowing"], 0.5)
    assert eq_tol(res["l2 inflow after"], 0)
    assert eq_tol(res["l2 outflow flowing"], 0.4)
    assert eq_tol(res["l2 outflow after"], 0)

    assert eq_tol(res["l3 inflow after"], 0)
    assert eq_tol(res["l3 inflow flowing"], 0.8)
    assert eq_tol(res["l3 inflow after"], 0)

@pytest.mark.flaky(reruns=5)
def test_merge_verycongested():
    res = defaultdict(list)
    for i in range(10):
        W = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=0,
            random_seed=random.randint(0,999999)
        )

        W.addNode("orig1", 0, 0)
        W.addNode("orig2", 0, 2)
        W.addNode("merge", 1, 1)
        W.addNode("dest", 2, 1)

        l1 = W.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 1)
        l2 = W.addLink("link2", "orig2", "merge", 10000, 20, 0.2, 1)
        l3 = W.addLink("link3", "merge", "dest", 10000, 20, 0.2, 1)

        W.adddemand("orig1", "dest", 0,   1000, 0.8)
        W.adddemand("orig2", "dest", 0, 1000, 0.8)

        W.print_scenario_stats()
        W.exec_simulation()
        W.print_simple_results()

        res["l1 inflow flowing"].append(l1.inflow(0,1000))
        res["l1 inflow after"].append(l1.inflow(1000,2000))
        res["l1 outflow flowing"].append(l1.outflow(500,500+2000))
        res["l1 outflow after"].append(l1.outflow(500+2000,500+2000+400))

        res["l2 inflow flowing"].append(l2.inflow(0,1000))
        res["l2 inflow after"].append(l2.inflow(1000,2000))
        res["l2 outflow flowing"].append(l2.outflow(500,500+2000))
        res["l2 outflow after"].append(l2.outflow(500+2000,500+2000+400))
        
        res["l3 inflow before"].append(l3.inflow(0,500))
        res["l3 inflow flowing"].append(l3.inflow(500,500+2000))
        res["l3 inflow after"].append(l3.inflow(500+2000,500+2000+400))

    for key in res:
        res[key] = np.mean(res[key])

    assert eq_tol(res["l1 inflow flowing"], 0.8)
    assert eq_tol(res["l1 inflow after"], 0)
    assert eq_tol(res["l1 outflow flowing"], 0.4)
    assert eq_tol(res["l1 outflow after"], 0)

    assert eq_tol(res["l2 inflow flowing"], 0.8)
    assert eq_tol(res["l2 inflow after"], 0)
    assert eq_tol(res["l2 outflow flowing"], 0.4)
    assert eq_tol(res["l2 outflow after"], 0)

    assert eq_tol(res["l3 inflow after"], 0)
    assert eq_tol(res["l3 inflow flowing"], 0.8)
    assert eq_tol(res["l3 inflow after"], 0)

@pytest.mark.flaky(reruns=5)
def test_merge_verycongested_veryunfair():
    res = defaultdict(list)
    for i in range(10):
        W = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=0,
            random_seed=random.randint(0,999999)
        )

        W.addNode("orig1", 0, 0)
        W.addNode("orig2", 0, 2)
        W.addNode("merge", 1, 1)
        W.addNode("dest", 2, 1)

        l1 = W.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 100)
        l2 = W.addLink("link2", "orig2", "merge", 10000, 20, 0.2, 1)
        l3 = W.addLink("link3", "merge", "dest", 10000, 20, 0.2, 1)

        W.adddemand("orig1", "dest", 0,   1000, 0.8)
        W.adddemand("orig2", "dest", 0, 1000, 0.8)

        W.print_scenario_stats()
        W.exec_simulation()
        #W.print_simple_results()

        res["l1 inflow flowing"].append(l1.inflow(0,1000))
        res["l1 inflow after"].append(l1.inflow(1000,2000))
        res["l1 outflow flowing"].append(l1.outflow(500,500+1000))
        res["l1 outflow after"].append(l1.outflow(500+1000,500+1000+400))

        res["l2 inflow flowing"].append(l2.inflow(0,1000))
        res["l2 inflow after"].append(l2.inflow(1000,2000))
        res["l2 outflow flowing-stop"].append(l2.outflow(500,500+1000))
        res["l2 outflow flowing-flow"].append(l2.outflow(500+1000,500+1000+1000))
        res["l2 outflow after"].append(l2.outflow(500+1000+1000,500+1000+1000+400))
        
        res["l3 inflow before"].append(l3.inflow(0,500))
        res["l3 inflow flowing"].append(l3.inflow(500,500+2000))
        res["l3 inflow after"].append(l3.inflow(500+2000,500+2000+400))

        # figure()
        # for l in (l1, l2, l3):
        #     if l==l1:
        #         color = "r"
        #     if l==l2:
        #         color = "b"
        #     if l==l3:
        #         color = "y"
        #     title(str(i))
        #     plot(l.arrival_curve, color=color)
        #     plot(l.departure_curve, color=color)
        # grid()
        # show()


    for key in res:
        res[key] = np.mean(res[key])

    assert eq_tol(res["l1 inflow flowing"], 0.8)
    assert eq_tol(res["l1 inflow after"], 0)
    assert eq_tol(res["l1 outflow flowing"], 0.8)
    assert eq_tol(res["l1 outflow after"], 0)

    assert eq_tol(res["l2 inflow flowing"], 0.8)
    assert eq_tol(res["l2 inflow after"], 0)
    assert eq_tol(res["l2 outflow flowing-stop"], 0.0)
    assert eq_tol(res["l2 outflow flowing-flow"], 0.8)
    assert eq_tol(res["l2 outflow after"], 0)

    assert eq_tol(res["l3 inflow after"], 0)
    assert eq_tol(res["l3 inflow flowing"], 0.8)
    assert eq_tol(res["l3 inflow after"], 0)

@pytest.mark.flaky(reruns=5)
def test_merge_verycongested_unfair():
    res = defaultdict(list)
    for i in range(10):
        W = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=300.0,
            duo_update_weight=0.25,
            print_mode=0,
            random_seed=random.randint(0,999999)
        )

        W.addNode("orig1", 0, 0)
        W.addNode("orig2", 0, 2)
        W.addNode("merge", 1, 1)
        W.addNode("dest", 2, 1)

        l1 = W.addLink("link1", "orig1", "merge", 10000, 20, 0.2, 2)
        l2 = W.addLink("link2", "orig2", "merge", 10000, 20, 0.2, 1)
        l3 = W.addLink("link3", "merge", "dest", 10000, 20, 0.2, 1)

        W.adddemand("orig1", "dest", 0,   1000, 0.8)
        W.adddemand("orig2", "dest", 0, 1000, 0.8)

        W.print_scenario_stats()
        W.exec_simulation()
        #W.print_simple_results()

        res["l1 inflow flowing"].append(l1.inflow(0,1000))
        res["l1 inflow after"].append(l1.inflow(1000,2000))
        res["l1 outflow flowing"].append(l1.outflow(500,500+1500))
        res["l1 outflow after"].append(l1.outflow(500+1500,500+1500+400))

        res["l2 inflow flowing"].append(l2.inflow(0,1000))
        res["l2 inflow after"].append(l2.inflow(1000,2000))
        res["l2 outflow flowing-low"].append(l2.outflow(500,500+1500))
        res["l2 outflow flowing-high"].append(l2.outflow(500+1500,500+1500+500))
        res["l2 outflow after"].append(l2.outflow(500+1500+500,500+1500+500+400))
        
        res["l3 inflow before"].append(l3.inflow(0,500))
        res["l3 inflow flowing"].append(l3.inflow(500,500+2000))
        res["l3 inflow after"].append(l3.inflow(500+2000,500+2000+400))

        # figure()
        # for l in (l1, l2, l3):
        #     if l==l1:
        #         color = "r"
        #     if l==l2:
        #         color = "b"
        #     if l==l3:
        #         color = "y"
        #     title(str(i))
        #     plot(l.arrival_curve, color=color)
        #     plot(l.departure_curve, color=color)
        # grid()
        # show()


    for key in res:
        res[key] = np.mean(res[key])

    assert eq_tol(res["l1 inflow flowing"], 0.8)
    assert eq_tol(res["l1 inflow after"], 0)
    assert eq_tol(res["l1 outflow flowing"], 0.5333)
    assert eq_tol(res["l1 outflow after"], 0)

    assert eq_tol(res["l2 inflow flowing"], 0.8)
    assert eq_tol(res["l2 inflow after"], 0)
    assert eq_tol(res["l2 outflow flowing-low"], 0.2666)
    assert eq_tol(res["l2 outflow flowing-high"], 0.8)
    assert eq_tol(res["l2 outflow after"], 0)

    assert eq_tol(res["l3 inflow after"], 0)
    assert eq_tol(res["l3 inflow flowing"], 0.8)
    assert eq_tol(res["l3 inflow after"], 0)


####################################################
## MARK: Diverge

def test_diverge_oneway():
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
    W.addNode("diverge", 1, 1)
    W.addNode("dest1", 0, 0)
    W.addNode("dest2", 2, 1)

    l1 = W.addLink("link0", "orig", "diverge", 1000, 10, 0.2, 1)
    l2 = W.addLink("link1", "diverge", "dest1", 1000, 10, 0.2, 1)
    l3 = W.addLink("link2", "diverge", "dest2", 1000, 10, 0.2, 1)

    W.adddemand("orig", "dest1", 0, 1000, 0.4)
    #W.adddemand("orig", "dest2", 0, 1000, 0.4)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    assert eq_tol(l1.outflow(100,1100), 0.4)
    assert eq_tol(l2.inflow(100,1100), 0.4)
    assert eq_tol(l3.inflow(100,1100), 0)

def test_diverge_twoway():
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
    W.addNode("diverge", 1, 1)
    W.addNode("dest1", 0, 0)
    W.addNode("dest2", 2, 1)

    l1 = W.addLink("link0", "orig", "diverge", 1000, 10, 0.2, 1)
    l2 = W.addLink("link1", "diverge", "dest1", 1000, 10, 0.2, 1)
    l3 = W.addLink("link2", "diverge", "dest2", 1000, 10, 0.2, 1)

    W.adddemand("orig", "dest1", 0, 1000, 0.4)
    W.adddemand("orig", "dest2", 0, 1000, 0.2)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    assert eq_tol(l1.outflow(100,1100), 0.6)
    assert eq_tol(l2.inflow(100,1100), 0.4)
    assert eq_tol(l3.inflow(100,1100), 0.2)

def test_diverge_congested():
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
    W.addNode("diverge", 1, 1)
    W.addNode("dest1", 0, 0)
    W.addNode("dest1-true", 0, 0)
    W.addNode("dest2", 2, 1)

    l1 = W.addLink("link0", "orig", "diverge",  1000, 10, 0.2,1)
    l2 = W.addLink("link1", "diverge", "dest1",  1000, 10, 0.2, 1, capacity_out=0.1)
    l2_dummy = W.addLink("link1-dummy", "dest1", "dest1-true", 1000, 10, 0.2, 1)
    l3 = W.addLink("link2", "diverge", "dest2",  1000, 10, 0.2, 1)

    W.adddemand("orig", "dest1-true", 0, 1000, 0.4)
    W.adddemand("orig", "dest2", 0, 1000, 0.2)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    """
    shockwave speed at l2: (0.4-0.3)/(0.18-0.04) = 2.14
    arrival time of shockwave to node "diverge": 100+100+467=667
    node flow after the node congestion: 0.1*1.666 = 0.1666
    l3 flow after the node congestion: 0.666
    the node congestion lasts untill: 667+260/0.1666 = 2227
    """
    # figure()
    # plot_cumcurves(l1, "b")
    # plot_cumcurves(l2, "r")
    # plot_cumcurves(l3, "y")
    # plot([667,667], [0,600], "k--")
    # plot([2221,2221], [0,600], "k--")
    # grid()
    # show()

    assert eq_tol(l1.outflow(100,667), 0.6)
    assert eq_tol(l1.outflow(667,2227), 0.1666)
    assert eq_tol(l2.inflow(667,2227), 0.1, abs_tol=0.01)
    assert eq_tol(l3.inflow(667,2227), 0.0666, abs_tol=0.01)
    assert eq_tol(l1.outflow(2227,2990), 0.0)

    
####################################################
## MARK: Route choice

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

    

def test_routechoice_shorter_1route():
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

    l1a = W.addLink("link1a", "orig", "mid1", 2000, 10, 0.2, 1)
    l1b = W.addLink("link1b", "mid1", "dest", 2000, 10, 0.2, 1,)
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

    assert eq_tol(l1a.inflow(0,1000), 0)
    assert eq_tol(l2a.inflow(0,1000), 0.6)

@pytest.mark.flaky(reruns=10)
def test_routechoice_switch_routes():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=5.0,
        tau=1.0,
        duo_update_time=50.0,
        duo_update_weight=1.0,
        print_mode=0,
        random_seed=random.randint(0,999999)
    )

    W.addNode("orig", 0, 0)
    W.addNode("mid1", 1, 1)
    W.addNode("mid2", 0, 0)
    W.addNode("dest", 2, 1)

    l1a = W.addLink("link1a", "orig", "mid1", 2000, 20, 0.2, 1, capacity_out=0.1)
    l1b = W.addLink("link1b", "mid1", "dest", 1000, 20, 0.2, 1,)
    l2a = W.addLink("link2a", "orig", "mid2", 2000, 10, 0.2, 1)
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

    assert eq_tol(l1a.inflow(0,300), 0.6)
    assert eq_tol(l1a.inflow(400,500), 0)
    assert eq_tol(l2a.inflow(0,300), 0)
    assert eq_tol(l2a.inflow(400,500), 0.6)

@pytest.mark.flaky(reruns=10)
def test_routechoice_switch_routes_insensitive():
    res = defaultdict(list)
    for i in range(20):
        W = newWorld(
            "test",
            tmax=3000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=50.0,
            duo_update_weight=0.0001,
            print_mode=0,
            random_seed=random.randint(0,999999)
        )

        W.addNode("orig", 0, 0)
        W.addNode("mid1", 1, 1)
        W.addNode("mid2", 0, 0)
        W.addNode("dest", 2, 1)

        l1a = W.addLink("link1a", "orig", "mid1", 2000, 20, 0.2, 1, capacity_out=0.1)
        l1b = W.addLink("link1b", "mid1", "dest", 1000, 20, 0.2, 1,)
        l2a = W.addLink("link2a", "orig", "mid2", 2000, 10, 0.2, 1)
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
        res["l1 inflow 1"].append(l1a.inflow(0,300))
        res["l1 inflow 2"].append(l1a.inflow(400,500))
        res["l2 inflow 1"].append(l2a.inflow(0,300))
        res["l2 inflow 2"].append(l2a.inflow(400,500))

    for key in res:
        res[key] = np.mean(res[key])

    assert eq_tol(res["l1 inflow 1"], 0.58, rel_tol=0.2)
    assert eq_tol(res["l1 inflow 2"], 0.45, rel_tol=0.2)
    assert eq_tol(res["l2 inflow 1"], 0)
    assert eq_tol(res["l2 inflow 2"], 0.15, rel_tol=0.2)

@pytest.mark.flaky(reruns=10)
def test_routechoice_congested_equal_routes():
    res = defaultdict(list)
    for i in range(10):
        W = newWorld(
            "test",
            tmax=5000.0,
            deltan=5.0,
            tau=1.0,
            duo_update_time=50.0,
            duo_update_weight=0.1,
            print_mode=0,
            random_seed=random.randint(0,999999)
        )

        W.addNode("orig", 0, 0)
        W.addNode("mid1", 1, 1)
        W.addNode("mid2", 0, 0)
        W.addNode("dest", 2, 1)

        l1a = W.addLink("link1a", "orig", "mid1", 1000, 10, 0.2, 1, capacity_out=0.3)
        l1b = W.addLink("link1b", "mid1", "dest", 1000, 10, 0.2, 1,)
        l2a = W.addLink("link2a", "orig", "mid2", 1000, 10, 0.2, 1, capacity_out=0.3)
        l2b = W.addLink("link2b", "mid2", "dest", 1000, 10, 0.2, 1,)

        W.adddemand("orig", "dest", 0, 3000, 0.6)

        W.print_scenario_stats()
        W.exec_simulation()
        W.print_simple_results()

        # figure()
        # plot_cumcurves(l1a, "b")
        # plot_cumcurves(l2a, "r")
        # grid()
        # show()

        res["l1 users"].append(l1a.arrival_curve[-1])
        res["l2 users"].append(l2a.arrival_curve[-1])
        res["l1 ave tt"].append(np.average(l1a.traveltime_real))
        res["l2 ave tt"].append(np.average(l2a.traveltime_real))

    for key in res:
        res[key] = np.mean(res[key])

    assert eq_tol(res["l1 users"], res["l2 users"], rel_tol=0.15)
    assert eq_tol(res["l1 ave tt"], res["l2 ave tt"], rel_tol=0.15)

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
    
def test_route_specified_even():
        
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

    W.adddemand("orig", "dest", 0, 1000, 0.3, links_preferred_list=[l1a, l1b])
    W.adddemand("orig", "dest", 0, 1000, 0.3, links_preferred_list=["link2a", "link2b"])

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results() 

    # figure()
    # plot_cumcurves(l1a, "b")
    # plot_cumcurves(l2a, "r")
    # grid()
    # show()

    assert eq_tol(l1a.inflow(0,1000), 0.3)
    assert eq_tol(l2a.inflow(0,1000), 0.3)
    
@pytest.mark.flaky(reruns=10)
def test_route_specified_even_random():
        
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

    W.adddemand("orig", "dest", 0, 1000, 0.6, links_preferred_list=[l1a, l1b, "link2a", "link2b"])

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results() 

    # figure()
    # plot_cumcurves(l1a, "b")
    # plot_cumcurves(l2a, "r")
    # grid()
    # show()

    assert eq_tol(l1a.inflow(0,1000), 0.3)
    assert eq_tol(l2a.inflow(0,1000), 0.3)

####################################################
## MARK: Signal

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


def test_signal_straight_deltan1():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=1,
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


def test_signal_4legged_undersaturated():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=5,
        duo_update_time=300.0,
        duo_update_weight=0.25,
        print_mode=1,
        random_seed=42
    )

    nn = W.addNode("N", 0, 0)
    ee = W.addNode("E", 0, 0)
    ss = W.addNode("S", 1, 0)
    ww = W.addNode("W", 1, 0)
    mm = W.addNode("m", 0.5, 0, signal_intervals=[500,500])

    Nm = W.addLink("Nm", nn, mm, 10000, 20, 0.2, 1, signal_group=0)
    Em = W.addLink("Em", ee, mm, 10000, 20, 0.2, 1, signal_group=1)
    Sm = W.addLink("Sm", ss, mm, 10000, 20, 0.2, 1, signal_group=0)
    Wm = W.addLink("Wm", ww, mm, 10000, 20, 0.2, 1, signal_group=1)

    mN = W.addLink("mN", mm, nn, 1000, 20, 0.2, 1)
    mE = W.addLink("mE", mm, ee, 1000, 20, 0.2, 1)
    mS = W.addLink("mS", mm, ss, 1000, 20, 0.2, 1)
    mW = W.addLink("mW", mm, ww, 1000, 20, 0.2, 1)

    for n1,n2 in [[nn, ss], [ss, nn], [ee, ww], [ww, ee]]:
        W.adddemand(n1, n2, 0,   2000, 0.2)
    for n1,n2 in [[nn,ww], [nn,ee], [ss,ww], [ss,ee], [ee,nn], [ee,ss], [ww,nn], [ww,ss]]:
        W.adddemand(n1, n2, 0,   2000, 0.05)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    # figure()
    # plot_cumcurves(Nm, col="r")
    # plot_cumcurves(Em, col="b")

    # figure()
    # plot_cumcurves(mS, col="r")
    # plot_cumcurves(mW, col="b")

    assert eq_tol(Nm.inflow(0, 2000), 0.3)

    assert eq_tol(Nm.outflow(500, 1000), 0.0)
    assert eq_tol(Nm.outflow(1000, 1300), 0.8)
    assert eq_tol(Nm.outflow(1300, 1500), 0.3)
    assert eq_tol(Nm.outflow(1500, 2000), 0.0)
    assert eq_tol(Nm.outflow(2000, 2300), 0.8)

    assert eq_tol(mS.inflow(0, 500), 0)
    assert eq_tol(mS.inflow(500, 1000), 0.1, rel_tol=0.2)
    assert eq_tol(mS.inflow(1000, 1300), 0.8*0.2/0.3)
    assert eq_tol(mS.inflow(1300, 1500), 0.2)
    assert eq_tol(mS.inflow(1500, 1800), 0.8*0.1/0.3)
    assert eq_tol(mS.inflow(1800, 2000), 0.1)
    assert eq_tol(mS.inflow(2000, 2300), 0.8*0.2/0.3)

def test_signal_4legged_oversaturated():
    W = newWorld(
        "test",
        tmax=3000.0,
        deltan=5,
        duo_update_time=300.0,
        duo_update_weight=0.25,
        print_mode=1,
        random_seed=42
    )

    nn = W.addNode("N", 0, 0)
    ee = W.addNode("E", 0, 0)
    ss = W.addNode("S", 1, 0)
    ww = W.addNode("W", 1, 0)
    mm = W.addNode("m", 0.5, 0, signal_intervals=[500,500])

    Nm = W.addLink("Nm", nn, mm, 1000, 20, 0.2, 1, signal_group=0)
    Em = W.addLink("Em", ee, mm, 1000, 20, 0.2, 1, signal_group=1)
    Sm = W.addLink("Sm", ss, mm, 1000, 20, 0.2, 1, signal_group=0)
    Wm = W.addLink("Wm", ww, mm, 1000, 20, 0.2, 1, signal_group=1)

    mN = W.addLink("mN", mm, nn, 1000, 20, 0.2, 1)
    mE = W.addLink("mE", mm, ee, 1000, 20, 0.2, 1)
    mS = W.addLink("mS", mm, ss, 1000, 20, 0.2, 1)
    mW = W.addLink("mW", mm, ww, 1000, 20, 0.2, 1)

    for n1,n2 in [[nn, ss], [ss, nn], [ee, ww], [ww, ee]]:
        W.adddemand(n1, n2, 0,   2000, 0.4)
    for n1,n2 in [[nn,ww], [nn,ee], [ss,ww], [ss,ee], [ee,nn], [ee,ss], [ww,nn], [ww,ss]]:
        W.adddemand(n1, n2, 0,   2000, 0.1)

    W.print_scenario_stats()
    W.exec_simulation()
    W.print_simple_results()

    # figure()
    # plot_cumcurves(Nm, col="r")
    # plot_cumcurves(Em, col="b")

    # figure()
    # plot_cumcurves(mS, col="r")
    # plot_cumcurves(mW, col="b")

    assert eq_tol(Em.inflow(0,1000*0.2/0.6), 0.6)
    assert eq_tol(Em.inflow(1000*0.2/0.6,500), 0.0)
    assert eq_tol(Em.inflow(500,700), 0.0)
    assert eq_tol(Em.inflow(700,1200), 0.8)
    assert eq_tol(Em.inflow(1200,1500), 0.0)

    assert eq_tol(Em.outflow(0,500), 0.0)
    assert eq_tol(Em.outflow(500,1000), 0.8)
    assert eq_tol(Em.outflow(1000,1500), 0.0)

    assert eq_tol(mW.inflow(0,200), 0.0)
    assert eq_tol(mW.inflow(200,500), 0.2)
    assert eq_tol(mW.inflow(500,1000), 0.8 *0.4/0.6)
    assert eq_tol(mW.inflow(1000,1500), 0.8 *0.2/0.6)

####################################################
## MARK: Others

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
