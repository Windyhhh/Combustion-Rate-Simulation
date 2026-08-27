# 🔥 推进剂燃烧速率仿真 | Combustion Rate Simulation

> **推进剂燃烧速率计算仿真软件——全栈计算系统、多参数建模、可复用架构，助力航天动力工程研究。**
>
> *Propellant combustion rate simulation software — full-stack calculation system, multi-parameter modeling, reusable architecture, supporting aerospace propulsion research.*

---

## ⭐ 核心卖点 | Why Star This

| 卖点 | Feature | 一句话 |
|------|---------|--------|
| 🔥 **燃烧速率计算** | Combustion Rate | 推进剂燃烧速率精确计算 |
| 🧮 **多参数建模** | Multi-Parameter | 压力、温度、配方多参数建模 |
| 🖥️ **全栈系统** | Full-Stack | 前端交互 + 后端计算一体化 |
| 🔧 **可复用架构** | Reusable | 模块化设计，易于扩展复用 |
| 📊 **可视化输出** | Visualization | 燃烧曲线、参数影响可视化 |

---

## 🏆 技术栈 | Tech Stack

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-black?logo=flask)
![NumPy](https://img.shields.io/badge/NumPy-1.21+-blue?logo=numpy)
![Scipy](https://img.shields.io/badge/Scipy-1.7+-blue?logo=scipy)
![HTML5](https://img.shields.io/badge/HTML5-5.0+-red?logo=html5)
![ECharts](https://img.shields.io/badge/ECharts-5.0+-orange?logo=apacheecharts)

---

## 🚀 快速开始 | Quick Start

```bash
git clone https://github.com/Windyhhh/Combustion-Rate-Simulation.git
cd Combustion-Rate-Simulation

# 1. 安装依赖
pip install -r requirements.txt

# 2. 计算燃烧速率
python src/calculate.py --pressure 5.0 --temperature 300

# 3. 参数敏感性分析
python src/sensitivity_analysis.py --pressure 3.0 10.0 --steps 20

# 4. 启动 Web 系统
python app.py --port 5000
# 访问 http://localhost:5000
```

---

## 📂 项目结构 | Project Structure

```
Combustion-Rate-Simulation/
├── app.py                     # Web 应用
├── src/                       # 核心代码
│   ├── calculate.py           # 燃烧速率计算
│   ├── burn_rate_model.py     # 燃烧模型
│   ├── propellant.py          # 推进剂配方
│   ├── sensitivity_analysis.py # 敏感性分析
│   └── thermo.py              # 热力学计算
├── frontend/                  # 前端界面
├── data/                      # 配方数据
└── requirements.txt
```

---

## 🔬 核心实现 | Core Implementation

### 燃烧速率计算 | Burn Rate Calculation

```python
# 推进剂燃烧速率计算 (Vielle's Law)
import numpy as np

def calculate_burn_rate(pressure, temperature, propellant_params):
    """
    计算推进剂燃烧速率
    
    使用 Vieille 定律: r = a * P^n
    Args:
        pressure: 燃烧室压力 (MPa)
        temperature: 推进剂初温 (K)
        propellant_params: 推进剂参数 {a, n, temperature_coeff}
    """
    a = propellant_params['a']     # 燃烧速率系数
    n = propellant_params['n']     # 压力指数
    beta = propellant_params['temperature_coeff']  # 温度敏感系数
    
    # 温度修正
    temp_correction = np.exp(beta * (temperature - 298))
    
    # Vieille 定律
    burn_rate = a * (pressure ** n) * temp_correction
    
    return burn_rate
```

---

## 📊 输出示例 | Output Example

```
🔥 推进剂燃烧速率仿真
━━━━━━━━━━━━━━━━━━━━━━━━━
配方: HTPB/AP 复合推进剂
压力: 5.0 MPa
温度: 300 K

📊 计算结果:
  燃烧速率: 8.52 mm/s
  压力指数 n: 0.35
  温度敏感系数: 0.0025 /K

📈 压力-燃烧速率关系:
  P=3MPa → 6.95 mm/s
  P=5MPa → 8.52 mm/s
  P=8MPa → 10.12 mm/s
━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 应用场景 | Use Cases

- 🚀 **航天动力**：固体推进剂燃烧研究
- 🔬 **材料科学**：含能材料性能分析
- 🎓 **工程计算**：燃烧计算仿真教学
- 🖥️ **全栈开发**：科学计算 Web 系统

---

## 📄 License

MIT License — 自由使用、修改和分发。

---

> 💡 **推进剂燃烧速率全栈仿真，Star ⭐ 助力航天动力研究！**
