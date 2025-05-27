from uxsimpp import newWorld, Analyzer

W = newWorld(
    name="basic",
    deltan=5,
    tmax=1200,
    random_seed=42
)

W.addNode("orig1", 0, 0)
W.addNode("orig2", 0, 2)
W.addNode("merge", 1, 1)
W.addNode("dest", 2, 1)

W.addLink("link1", "orig1", "merge", 1000, 20, 0.2, 1)
W.addLink("link2", "orig2", "merge", 1000, 20, 0.2, 1)
W.addLink("link3", "merge", "dest", 1000, 20, 0.2, 1)

W.adddemand("orig1", "dest", 0, 1000, 0.45)
W.adddemand("orig2", "dest", 400, 1000, 0.6)

W.print_scenario_stats()

W.exec_simulation()
W.print_simple_results()

ana = Analyzer(W)
ana.plot_time_space_trajectories(["link1", "link3"])
ana.network_fancy()