<div align="center">

# 🔥 Combustion-Rate-Simulation

### Propellant combustion rate simulation software.

A full-stack, reusable system for computing propellant combustion rates with a GUI.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-Tkinter-2EA44F)](https://docs.python.org/3/library/tkinter.html)

</div>

---

**Combustion-Rate-Simulation** is a propellant combustion-rate simulation software. It models species, reactions, phases and boundary layers to compute combustion rates, wrapped in a desktop GUI — built as a modular, reusable system.

> [!NOTE]
> 中文项目：推进剂燃烧速率仿真软件——全栈计算系统，可复用架构。

---

## Quickstart

```bash
git clone https://github.com/Windyhhh/Combustion-Rate-Simulation.git
cd Combustion-Rate-Simulation

# Run the GUI simulation
python archive/BRold_old/Gui_Main.py
```

The core modules (`Phase`, `Reactions`, `Species`, `melt_layer`, `delta_layer`) live in `archive/BRold_old/` with chemical mechanisms under `resources/`.

---

## Features

- **Combustion-rate modeling** — species, reactions, phase and boundary-layer modules.
- **GUI** — desktop simulation interface.
- **Reusable architecture** — modular Python modules + YAML chemical mechanisms.

---

## Project Structure

```
Combustion-Rate-Simulation/
├── archive/BRold_old/     # Gui.py, Gui_Main.py, Phase.py, Reactions.py, Species.py, run.py
│   └── resources/         # chemical mechanisms (chem.yaml, ...)
├── assets/                # images / logos
└── build/                 # old packaged builds
```

---

## License

MIT — free to use, modify and distribute.
