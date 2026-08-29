<div align="center">

# 推进剂燃速仿真 | Combustion-Rate-Simulation

### A propellant combustion-rate simulation with Cantera.

Mechanism selection, formulation design, storage & operating-condition config and real-time output in a modern GUI.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Cantera](https://img.shields.io/badge/Cantera-2.6-7B1FA2)](https://cantera.org/)
[![PyQt](https://img.shields.io/badge/PyQt-GUI-41CD52)](https://www.riverbankcomputing.com/software/pyqt/)

</div>

---

**Combustion-Rate-Simulation** is a professional **propellant combustion-rate** computation system built on **Cantera**. It combines mechanism selection, formulation design, storage & operating-condition configuration and real-time result output in a modern side-bar GUI, with a layered architecture that decouples the compute engine from the UI.

> [!NOTE]
> 中文项目：推进剂燃烧速度仿真软件——Cantera 计算核心 + 侧边栏 GUI，机理/配方/贮存/工况配置，多线程并行。

---

## Features

- **Cantera engine** — combustion-rate computation with multiple mechanisms.
- **Full workflow** — mechanism selection, formulation, storage params, operating conditions, result output.
- **Layered design** — compute core decoupled from GUI; multi-threaded parallel computing.
- **Fast** — single case < 2s, 100+ batch cases, UI response < 100ms.
- **Modern GUI** — particle animations, side-bar navigation.

---

## Quickstart

```bash
git clone https://github.com/Windyhhh/Combustion-Rate-Simulation.git
cd Combustion-Rate-Simulation

pip install -r requirements.txt

python src/main.py          # launch the simulation GUI
```

---

## Project Structure

```
Combustion-Rate-Simulation/
├── src/
│   ├── engine/             # Cantera computation core
│   ├── gui/                # PyQt interface
│   └── config/             # mechanism & formulation config
├── data/                   # mechanisms, properties
└── docs/                   # optimization, blog
```

---

## License

MIT — free to use, modify and distribute.
