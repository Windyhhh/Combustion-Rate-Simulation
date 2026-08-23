# 🔥 Combustion Rate Simulation | 推进剂燃烧速度仿真软件

> **Full-stack propellant combustion rate calculation and simulation software. Physics-based combustion models, parameter estimation, real-time simulation, visualization, and reusable architecture. Python + GUI.**
>
> 全栈推进剂燃烧速度计算与仿真软件。基于物理的燃烧模型、参数估计、实时仿真、可视化和可复用架构。Python + GUI。

---

## 🌟 Features | 核心特性

- **Combustion Models** — Vieille, Saint-Robert, pressure-coupled
- **Parameter Estimation** — Fit model parameters from experimental data
- **Real-time Simulation** — Dynamic combustion rate calculation
- **Pressure Coupling** — Pressure-dependent burning rate
- **Visualization** — Burn rate vs pressure, time series
- **GUI Interface** — User-friendly desktop application
- **Reusable Architecture** — Modular, extensible design

---

## 🚀 Quick Start | 快速开始

```bash
pip install numpy scipy matplotlib pyqt5 pandas

# Launch GUI
python main.py

# Command-line simulation
python simulate.py --pressure 70 --propellant HTPB --time 10

# Parameter fitting
python fit_parameters.py --data experimental_data.csv --model vieille
```

---

## 🔬 Models | 燃烧模型

| Model | Equation | Use Case |
|-------|----------|----------|
| **Vieille** | r = a·P^n | Standard propellants |
| **Saint-Robert** | r = a·P^n (extended) | Wide pressure range |
| **Pressure-Coupled** | r = f(P, T, composition) | Complex propellants |
| **Zeldovich** | r = f(P, activation energy) | High-temperature |

---

## 📄 License | 许可证

MIT License.

[GitHub](https://github.com/Windyhhh/Combustion-Rate-Simulation)
