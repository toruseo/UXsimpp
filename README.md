# UXsim++: Fast and simple traffic simulator for Python

**UXsim++** (or **uxsimpp**) is a free, open-source mesoscopic network traffic flow simulator for Python. 
It simulates the movements of car travelers and traffic congestion in road networks. 
It is suitable for simulating large-scale (e.g., city-scale) traffic phenomena. 
UXsim++ would be especially useful for scientific and educational purposes because of its fast, simple, lightweight, and customizable features, but users are free to use UXsim++ for any purpose.

UXsim++ is a significantly faster variant of [**UXsim**](https://github.com/toruseo/UXsim), a pure Python-based traffic simulator.
Its functionalities and syntax are almost equivalent to UXsim.
Meanwhile, the internal simulation engine is thoroughly written in C++, making it 20 to 30 times faster than UXsim.
Thanks to pybind11, the C++ engine is fully accessible from Python codes without any dependencies.

**This is alpha stage.**
**The codes and docs are work in progress.**

## Main Features

- Simple, fast, lightweight, and easy-to-use Python package for modern standard models of dynamic network traffic flow
- Macroscopic traffic simulation: Simulating over 60000 vehicles in a city in 1 second
- Dynamic traffic assignment: Traffic flow simulation with a given network and time-dependent OD demand
- Theoretically valid models commonly used in academic/professional transportation research
  - Car-following model (Newell's simplified model)
  - Reactive route choice model (dynamic user optimum)
- Significantly faster variant of [**UXsim**](https://github.com/toruseo/UXsim), with almost equivalent functionalities and syntax
  
## Examples

To be added

## Install

To be added

## Getting Started

```python
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
```

## Further Reading

ArXiv preprint will be added

## Terms of Use & License

MIT License