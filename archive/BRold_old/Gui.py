import os
import sys
import json
import time
import threading
import subprocess
from tkinter import *
from tkinter import ttk, filedialog, messagebox

# =============== 组分数据库（下拉自动填充） ==================
CHEM_DB = [
    {"name_cn": "硝化纤维素", "formula": "(C6H9N3O11)n", "remark": "300聚合度", "default_pct": 54.5, "mw": 299.0, "code": "NC"},
    {"name_cn": "硝化甘油",   "formula": "C3H5N3O9",     "remark": "",         "default_pct": 30.0,  "mw": 227.0, "code": "NG"},
    {"name_cn": "中定剂",     "formula": "C15H16N2O1",   "remark": "",         "default_pct": 1.5,   "mw": 240.0, "code": "ZDJ"},
    {"name_cn": "邻苯二甲酸二乙酯", "formula": "C12H14O4", "remark": "",     "default_pct": 10.5,  "mw": 222.0, "code": "DEP"},
    {"name_cn": "吉纳",       "formula": "C4H8N4O8",      "remark": "",         "default_pct": 3.5,   "mw": 240.0, "code": "DINA"},
    {"name_cn": "镍粉",       "formula": "Ni",            "remark": "",         "default_pct": None,  "mw": 59.0,  "code": "Ni"},
    {"name_cn": "四氧化三钴", "formula": "Co3O4",        "remark": "",         "default_pct": None,  "mw": 241.0, "code": "Co3O4"},
    {"name_cn": "苯二甲酸铅", "formula": "C8H4O4Pb",      "remark": "",         "default_pct": None,  "mw": 371.0, "code": "C8H4O4Pb"},
    {"name_cn": "氧化镁",     "formula": "MgO",           "remark": "",         "default_pct": None,  "mw": 40.0,  "code": "MgO"},
    {"name_cn": "蒽醌镁",     "formula": "C28H18O10Mg(DAQ-Mg)", "remark": "",  "default_pct": None,  "mw": 538.74, "code": "DAQ-Mg"},
    {"name_cn": "基于蒽醌镁的改进催化剂-1", "formula": "DAQ-Mg-1", "remark": "包含有蒽醌镁、铜盐、铅盐以及炭黑", "default_pct": None, "mw": 538.74, "code": "DAQ-Mg-1"},
    {"name_cn": "基于蒽醌镁的改进催化剂-2", "formula": "DAQ-Mg-2", "remark": "包含有蒽醌镁、铜盐、铅盐以及炭黑", "default_pct": None, "mw": 538.74, "code": "DAQ-Mg-2"},
    {"name_cn": "基于蒽醌镁的改进催化剂-3", "formula": "DAQ-Mg-3", "remark": "包含有蒽醌镁、铜盐、铅盐以及炭黑", "default_pct": None, "mw": 538.74, "code": "DAQ-Mg-3"},
    {"name_cn": "基于蒽醌镁的改进催化剂-4", "formula": "DAQ-Mg-4", "remark": "包含有蒽醌镁、铜盐、铅盐以及炭黑", "default_pct": None, "mw": 538.74, "code": "DAQ-Mg-4"},
    {"name_cn": "炭黑",       "formula": "C",             "remark": "",         "default_pct": None,  "mw": 12.0,  "code": "C"},
    {"name_cn": "己二酸铜",   "formula": "C6H8O4Cu",      "remark": "",         "default_pct": None,  "mw": 207.67, "code": "C6H8O4Cu"},
    {"name_cn": "二四二羟基苯甲酸铅", "formula": "C14H10O8Pb", "remark": "", "default_pct": None,  "mw": 513.42, "code": "C14H10O8Pb"},
    {"name_cn": "二四二羟基苯甲酸铜", "formula": "C14H10O8Cu", "remark": "", "default_pct": None,  "mw": 369.77, "code": "C14H10O8Cu"},
    {"name_cn": "水杨酸铅", "formula": "C14H10O6Pb", "remark": "", "default_pct": None, "mw": 481.43, "code": "C14H10O6Pb"},
    {"name_cn": "水杨酸铜", "formula": "C14H10O6Cu", "remark": "", "default_pct": None, "mw": 337.77, "code": "C14H10O6Cu"},
    {"name_cn": "氧化铝",     "formula": "Al2O3",         "remark": "",         "default_pct": None,  "mw": 101.96, "code": "Al2O3"},
    {"name_cn": "铝粉",       "formula": "Al",            "remark": "",         "default_pct": None,  "mw": 26.98,  "code": "Al"},
    {"name_cn": "碳酸钙",     "formula": "CaCO3",         "remark": "",         "default_pct": None,  "mw": 100.09, "code": "CaCO3"},
    {"name_cn": "硝酸铅",     "formula": "Pb(NO3)2",      "remark": "",         "default_pct": None,  "mw": 331.21, "code": "Pb(NO3)2"},
    {"name_cn": "硝酸铜",     "formula": "Cu(NO3)2",      "remark": "",         "default_pct": None,  "mw": 187.56, "code": "Cu(NO3)2"},
    {"name_cn": "聚四氟乙烯", "formula": "C2F4",          "remark": "",         "default_pct": None,  "mw": 100.02, "code": "C2F4"},
]

# 构建下拉显示文本；带默认含量的打★标记（Tk 的 Combobox 不支持逐项着色）
CHEM_OPTIONS = []  # [(display, key_name)]
for rec in CHEM_DB:
    star = "★" if rec.get("default_pct") not in (None, "") else ""
    display = f"{rec['name_cn']} ({rec['code']}){(' '+star) if star else ''}"
    CHEM_OPTIONS.append((display, rec['name_cn']))

# 快速索引
CHEM_BY_NAME = {rec['name_cn']: rec for rec in CHEM_DB}

# =============== Helper: center a window ==================
def center_window(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = int((sw - w) / 2)
    y = int((sh - h) / 3)
    win.geometry(f"{w}x{h}+{x}+{y}")

# =============== Splash / Loading Screen ==================
class Splash(Toplevel):
    def __init__(self, master, seconds=10):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg="#0b1220")
        center_window(self, 720, 360)

        title = Label(
            self,
            text="双基推进剂燃速预测平台",
            fg="#ffffff",
            bg="#0b1220",
            font=("Microsoft YaHei UI", 24, "bold")
        )
        title.pack(pady=30)

        authors = Label(
            self,
            text="作者：西安近代化学研究所 × 西北工业大学",
            fg="#b9c0d0",
            bg="#0b1220",
            font=("Microsoft YaHei UI", 14)
        )
        authors.pack(pady=5)

        self.pbar = ttk.Progressbar(self, mode="determinate", length=520, maximum=seconds*10)
        self.pbar.pack(pady=30)

        info = Label(
            self,
            text="正在加载模块与界面，请稍候…",
            fg="#dfe6f3",
            bg="#0b1220",
            font=("Microsoft YaHei UI", 12)
        )
        info.pack(pady=10)

        # 使用 after() 在主线程更新进度条
        self._steps = seconds * 10
        self._i = 0
        def _tick():
            if self._i < self._steps:
                self._i += 1
                self.pbar['value'] = self._i
                self.after(100, _tick)
            else:
                self.destroy()
        self.after(100, _tick)

# =================== Main Wizard App ======================
class WizardApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Energetic Material Combustion Simulator – DB Propellant")
        center_window(self, 1160, 800)
        self.minsize(980, 680)

        # Shared state across steps
        self.state = {
            "files": {"mech": "", "thermo": "", "yaml": ""},
            "formula_rows": [],  # list of dicts
            "density": 1.60,
            "storage_year": 0,
            "temperatures": [],  # legacy support
            "pressures": [],     # legacy support
            "cases": [],         # list of {T, P}
            "outputs": [],       # stdout per case
            "summary": []        # parsed results per case
        }

        # Splash: 阻塞直到加载页关闭
        self.withdraw()
        splash = Splash(self, seconds=10)
        self.wait_window(splash)
        self.deiconify()

        # Multi-frame wizard
        container = Frame(self)
        container.pack(fill=BOTH, expand=True)

        self.frames = {}
        for F in (Step1Files, Step2Formula , Step3Storage, Step4PT, Step5Output):# 显示中隐藏相对分子质量、机理名列，但保留数据接口
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.show_frame("Step1Files")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    # 统一运行一批工况：对每个 (T, P) 组合依次运行 run.py
    def run_batch(self):
        self.state["outputs"].clear()
        self.state["summary"].clear()
        app = self

        def work():
            step5 = app.frames["Step5Output"]
            step5.clear_output()

            files = app.state["files"]
            rows = [r for r in app.state["formula_rows"] if r.get("name")]
            # 归一化含量
            total = sum([float(r.get("content", 0) or 0) for r in rows])
            liquid_name_map = {
                "NC": "NC(L)",
                "NG": "NG(L)",
                "ZDJ": "ZDJ(L)",
                "DEP": "DEP(L)",
                "DINA": "DINA(L)",
            }
            species = []
            if total > 0:
                for r in rows:
                    code = (r.get("code") or r.get("name") or "").strip()
                    frac = float(r.get("content") or 0) / total
                    species.append({
                        "name": liquid_name_map.get(code, code),  # ★ 用液相名
                        "molecular_weight": float(r.get("mw", 0) or 0),
                        "amount": frac
                    })
            # 工况来源：优先使用 Step4 建好的 cases；若为空，退回到笛卡尔积(兼容旧状态)
            cases = list(self.state.get("cases", []))
            if not cases:
                Ts = list(self.state.get("temperatures", []))
                Ps = list(self.state.get("pressures", []))
                cases = [{"T": t, "P": p} for t in Ts for p in Ps]

            if not cases:
                step5.append("[WARN] 未选择任何工况，无法开始计算。\n")
                return

            # 逐工况运行
            for i, case in enumerate(cases, 1):
                t_c = float(case["T"])  # °C
                p = float(case["P"])   # MPa
                Tinit = t_c + 273.15  # convert to K
                config = {
                    "density": float(self.state["density"]),
                    "pressure": p,
                    "Tinit": float(Tinit),
                    "storage_time": float(self.state["storage_year"]),
                    "liquid_phase_mech_file": files.get("mech", ""),
                    "thermo_data_file": files.get("thermo", ""),
                    "gas_phase_yaml_file": files.get("yaml", ""),
                    "species": species
                }
                with open("config_input.json", "w", encoding="utf-8") as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                step5.append(f"\n==== 工况{i}：温度{t_c:.0f}℃，压力{p} MPa ====\n")
                step5.append("写入配置 config_input.json 完成。\n")

                exe = sys.executable
                cmd = [exe, "run.py", "--config", "config_input.json"]
                try:
                    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                    stdout_lines = []
                    for line in proc.stdout:
                        stdout_lines.append(line)
                        step5.append(line)
                    proc.wait()
                    out = "".join(stdout_lines)
                except FileNotFoundError:
                    out = "[INFO] 未找到 run.py，使用示例数据。\nBurn rate: {:.3f} mm/s\n".format(max(0.5, (t_c+40)/300) * (1 + p/30))
                    step5.append(out)
                except Exception as e:
                    out = f"[ERROR] 运行失败：{e}\n"
                    step5.append(out)

                rate = parse_burn_rate(out)
                self.state["summary"].append({"T": t_c, "P": p, "burn_rate": rate})

            # 更新图表
            step5.draw_chart(self.state["summary"]) 

        threading.Thread(target=work, daemon=True).start()

# =============== Utilities ===============
def parse_burn_rate(text):
    """
    从标准输出里解析一行形如 'Burn rate: <value>' 的数值；否则返回 None。
    """
    if not text:
        return None
    for line in text.splitlines():
        s = line.strip().lower()
        if s.startswith("burn rate:"):
            try:
                num = s.split(":", 1)[1].strip().split()[0]
                return float(num)
            except Exception:
                pass
    return None

# =================== Step 1: 选择机理文件 ==================
class Step1Files(Frame):
    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app

        Label(self, text="步骤一：选择三个机理文件", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w", pady=(10, 6))
        Label(self, text="请依次选择：液相机理、分子参数数据、气相机理 (YAML)").pack(anchor="w")

        body = Frame(self)
        body.pack(fill=X, pady=20)

        self.entries = {}
        self._row(body, "液相机理文件：", "mech")
        self._row(body, "分子参数数据文件：", "thermo")
        self._row(body, "气相机理 (YAML)：", "yaml")

        nav = Frame(self)
        nav.pack(fill=X, pady=10)
        Button(nav, text="完成", command=self.finish).pack(side=RIGHT)

    def _row(self, parent, label, key):
        fr = Frame(parent)
        fr.pack(fill=X, pady=6)
        Label(fr, text=label, width=16, anchor="e").pack(side=LEFT, padx=6)
        e = Entry(fr)
        e.pack(side=LEFT, fill=X, expand=True, padx=6)
        Button(fr, text="浏览…", command=lambda: self.pick(e)).pack(side=LEFT)
        self.entries[key] = e

    def pick(self, entry):
        path = filedialog.askopenfilename()
        if path:
            entry.delete(0, END)
            entry.insert(0, path)

    def finish(self):
        vals = {k: v.get().strip() for k, v in self.entries.items()}
        missing = [k for k, v in vals.items() if not v]
        if missing:
            if not messagebox.askyesno("确认", "仍有文件未选择，是否继续？"):
                return
        self.app.state["files"].update(vals)
        self.app.show_frame("Step2Formula")

# =================== Step 2: 配方与密度（下拉自动填充） ===================
class Step2Formula(Frame):
    COLS = ("序号", "化学名称", "化学组成", "备注", "含量(%)", "相对分子质量", "机理名")
    # 在界面上仅显示这些列，其他列隐藏但仍保留在数据中
    DISPLAY_COLS = ("序号", "化学名称", "化学组成", "备注", "含量(%)")

    # 不允许编辑的列（始终只读）：序号/化学组成/MW/机理名
    LOCKED_COLS = {"序号", "化学组成", "相对分子质量", "机理名"}
    # 允许手动编辑的列：备注/含量(%)；化学名称用专用下拉对话框
    EDITABLE_COLS = {"备注", "含量(%)"}

    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app

        Label(self, text="步骤二：输入配方与密度", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w", pady=(10, 6))
        Label(self, text="选择‘化学名称’会自动填充其他列；‘含量(%)’与‘备注’可手动修改。带★为有默认含量。双击单元格进行操作。").pack(anchor="w")

        # 表格
        table_fr = Frame(self)
        table_fr.pack(fill=BOTH, expand=True, pady=8)

        self.tree = ttk.Treeview(table_fr, columns=self.COLS, show="headings", height=12)
        # 设置列：显示列可拉伸填满；隐藏列宽度为 0
        widths_visible = {"序号":80, "化学名称":180, "化学组成":220, "备注":400, "含量(%)":100}
        for c in self.COLS:
            self.tree.heading(c, text=c)
            if c in self.DISPLAY_COLS:
                self.tree.column(
                    c,
                    width=widths_visible.get(c, 140),
                    minwidth=60,
                    anchor=CENTER if c in ("序号", "含量(%)") else W,
                    stretch=True,
                )
            else:
                # 隐藏列仍保留在数据中
                self.tree.column(c, width=0, minwidth=0, stretch=False)
        # 只显示 DISPLAY_COLS，隐藏 MW/机理名
        self.tree["displaycolumns"] = self.DISPLAY_COLS
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        vsb = ttk.Scrollbar(table_fr, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        vsb.pack(side=LEFT, fill=Y)

        # 初始化 22 行
        for i in range(22):
            self.tree.insert("", "end", values=("", "", "", "", "", "", ""))

        self.tree.bind("<Double-1>", self._edit_cell)

        # 密度输入
        den_fr = Frame(self)
        den_fr.pack(fill=X, pady=8)
        Label(den_fr, text="密度 (g/cm³)：").pack(side=LEFT)
        self.density_var = StringVar(value=str(self.app.state.get("density", 1.60)))
        Entry(den_fr, textvariable=self.density_var, width=10).pack(side=LEFT, padx=6)

        # 导航
        nav = Frame(self)
        nav.pack(fill=X, pady=10)
        Button(nav, text="上一步", command=lambda: self.app.show_frame("Step1Files")).pack(side=LEFT)
        Button(nav, text="完成", command=self.finish).pack(side=RIGHT)

    def on_show(self):
        pass

    # 单元格编辑弹窗
    def _edit_cell(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return
        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col_index = int(col_id.replace('#', '')) - 1
        if not row_id:
            return

        old_vals = list(self.tree.item(row_id, 'values'))
        col_name = self.COLS[col_index]

        # 锁定列：禁止编辑（序号/化学组成/MW/机理名）
        if col_name in self.LOCKED_COLS:
            # 静默返回，避免误操作；如需提示可改为 messagebox.showinfo
            return

        # 化学名称列：弹出下拉选择，自动填充
        if col_name == "化学名称":
            top = Toplevel(self)
            top.title("选择化学名称")
            center_window(top, 420, 160)
            Label(top, text="选择化学名称（★表示有默认含量）").pack(pady=(12,6))
            var = StringVar()
            combo = ttk.Combobox(top, state="readonly", width=48, textvariable=var,
                                  values=[disp for (disp, key) in CHEM_OPTIONS])
            combo.pack(padx=16)
            if old_vals[1]:
                # 回填选择项
                for disp, key in CHEM_OPTIONS:
                    if key == old_vals[1]:
                        var.set(disp)
                        break

            def ok():
                disp = var.get()
                if not disp:
                    top.destroy(); return
                # 解析选中的中文名称（"中文名 (code)" 或带★）
                name_cn = disp.split('(')[0].strip()
                rec = CHEM_BY_NAME.get(name_cn)
                if not rec:
                    top.destroy(); return
                # 互斥校验：MgO 与 DAQ-Mg 系列互斥；DAQ-Mg-1/2/3/4 只能出现一个
                daq_mg_all = {"DAQ-Mg", "DAQ-Mg-1", "DAQ-Mg-2", "DAQ-Mg-3", "DAQ-Mg-4"}
                new_code = rec.get('code', '')
                # 收集当前已有的机理名（不含本行）
                existing_codes = []
                for iid2 in self.tree.get_children():
                    if iid2 == row_id:
                        continue
                    vals2 = list(self.tree.item(iid2, 'values'))
                    code2 = (vals2[6] if len(vals2) > 6 else '') or ''
                    code2 = str(code2).strip()
                    if code2:
                        existing_codes.append(code2)
                has_mgo = "MgO" in existing_codes
                has_any_daq = any(c in daq_mg_all for c in existing_codes)
                # 新选 MgO 的限制
                if new_code == "MgO":
                    if has_mgo:
                        messagebox.showwarning("非法添加", "当前已包含 MgO，不能再添加 MgO。")
                        top.destroy(); return
                    if has_any_daq:
                        messagebox.showwarning("非法添加", "当前已包含 DAQ-Mg 系列物种（含 DAQ-Mg 及其 -1/2/3/4），不能再添加 MgO。")
                        top.destroy(); return
                # 新选 DAQ-Mg / DAQ-Mg-1/2/3/4 的限制
                if new_code in daq_mg_all:
                    if has_any_daq:
                        messagebox.showwarning("非法添加", "DAQ-Mg 及 DAQ-Mg-1/2/3/4 只能存在一个，不能重复。")
                        top.destroy(); return
                    if has_mgo:
                        messagebox.showwarning("非法添加", "当前已包含 MgO，不能再添加 DAQ-Mg 系列物种。")
                        top.destroy(); return
                # 自动填充：化学名称、化学组成、备注、相对分子质量、机理名、含量(%)（若有默认值）
                old_vals[1] = rec['name_cn']
                old_vals[2] = rec['formula']
                # 备注若原本有值则尊重原值；否则用默认备注
                old_vals[3] = old_vals[3] or rec.get('remark', '')
                # 含量默认（保留可手改）
                default_pct = rec.get('default_pct')
                if default_pct not in (None, ""):
                    old_vals[4] = str(default_pct)
                # MW、机理名
                old_vals[5] = rec.get('mw', '')
                old_vals[6] = rec.get('code', '')
                # 自动编号：当“化学名称”非空时，写入序号（顺序编号）
                if old_vals[1]:
                    all_ids = self.tree.get_children()
                    # 以已有已填名称的数量+1 作为新序号
                    idx = 1
                    for iid in all_ids:
                        name_val = (self.tree.item(iid, 'values')[1] or "").strip()
                        if name_val:
                            idx += 1
                    old_vals[0] = idx
                self.tree.item(row_id, values=tuple(old_vals))
                top.destroy()
            Button(top, text="确定", command=ok).pack(pady=10)
            return

        # 仅允许编辑：备注 / 含量(%)
        if col_name not in self.EDITABLE_COLS:
            return

        # 其他允许编辑列：普通输入框
        top = Toplevel(self)
        top.title(f"编辑：{col_name}")
        center_window(top, 360, 160)
        Label(top, text=f"{col_name}:").pack(pady=10)
        var = StringVar(value=str(old_vals[col_index] or ""))
        e = Entry(top, textvariable=var)
        e.pack(fill=X, padx=20)
        e.focus_set()
        def ok2():
            old_vals[col_index] = var.get()
            self.tree.item(row_id, values=tuple(old_vals))
            top.destroy()
        Button(top, text="确定", command=ok2).pack(pady=10)

    def finish(self):
        # 读取表格
        rows = []
        for iid in self.tree.get_children():
            v = list(self.tree.item(iid, 'values'))
            row = {
                "index": v[0],            # 序号
                "name": v[1],            # 中文名
                "composition": v[2],      # 化学组成
                "remark": v[3],           # 备注
                "content": v[4],          # 含量(%) —— 可手动调整
                "mw": v[5],               # 相对分子质量
                "code": v[6],             # 机理名（用于计算）
            }
            if any([str(row[k]).strip() for k in ("name", "composition", "remark", "content", "mw", "code")]):
                rows.append(row)

        # 校验含量与 MW
        for r in rows:
            if str(r.get("content", "")).strip():
                try:
                    float(r["content"])  # 允许空/数字
                except Exception:
                    messagebox.showerror("格式错误", f"含量必须为数字: {r}")
                    return
            if str(r.get("mw", "")).strip():
                try:
                    float(r["mw"])  # 允许空/数字
                except Exception:
                    messagebox.showerror("格式错误", f"相对分子质量必须为数字: {r}")
                    return

        # 密度
        try:
            density = float(self.density_var.get())
        except Exception:
            messagebox.showerror("格式错误", "密度必须为数字。")
            return

        self.app.state["formula_rows"] = rows
        self.app.state["density"] = density
        self.app.show_frame("Step3Storage")

# =================== Step 3: 贮存时间（年） =================
class Step3Storage(Frame):
    YEARS = [0, 4, 8, 12, 16, 20, 24]
    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app

        Label(self, text="步骤三：选择贮存时间（年）", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w", pady=(10, 6))

        row = Frame(self)
        row.pack(pady=18)
        Label(row, text="贮存时间：").pack(side=LEFT)
        self.year_var = IntVar(value=self.YEARS[0])
        self.cb = ttk.Combobox(row, state="readonly", values=self.YEARS, textvariable=self.year_var, width=12)
        self.cb.pack(side=LEFT, padx=6)

        nav = Frame(self)
        nav.pack(fill=X, pady=10)
        Button(nav, text="上一步", command=lambda: self.app.show_frame("Step2Formula")).pack(side=LEFT)
        Button(nav, text="完成", command=self.finish).pack(side=RIGHT)

    def finish(self):
        self.app.state["storage_year"] = int(self.year_var.get())
        self.app.show_frame("Step4PT")

# =================== Step 4: 压力与温度（下拉逐条添加） =============
class Step4PT(Frame):
    TEMPS = list(range(-40, 101, 10))  # °C
    PRESSURES = [0.1] + list(range(1, 31))  # 0.1, 1, 2, ..., 30 (MPa)

    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app
        self.cases = []  # local staging list of dicts {T,P}

        Label(self, text="步骤四：选择压力与温度（下拉，逐条添加工况）", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w", pady=(10, 6))

        body = Frame(self)
        body.pack(fill=X, pady=10)

        # 温度下拉
        Label(body, text="温度 (°C)：").grid(row=0, column=0, sticky="e", padx=6, pady=6)
        self.temp_var = IntVar(value=25)
        self.temp_cb = ttk.Combobox(body, state="readonly", values=self.TEMPS, textvariable=self.temp_var, width=12)
        self.temp_cb.grid(row=0, column=1, sticky="w", padx=6, pady=6)

        # 压力下拉
        Label(body, text="压力 (MPa)：").grid(row=0, column=2, sticky="e", padx=6, pady=6)
        self.pres_var = StringVar(value=str(self.PRESSURES[1]))
        self.pres_cb = ttk.Combobox(body, state="readonly", values=self.PRESSURES, textvariable=self.pres_var, width=12)
        self.pres_cb.grid(row=0, column=3, sticky="w", padx=6, pady=6)

        # 按钮区
        btns = Frame(self)
        btns.pack(fill=X, pady=6)
        Button(btns, text="添加工况", command=self.add_case).pack(side=LEFT, padx=6)
        Button(btns, text="删除所选", command=self.delete_selected).pack(side=LEFT, padx=6)
        Button(btns, text="清空工况", command=self.clear_cases).pack(side=LEFT, padx=6)

        # 工况展示
        list_fr = Frame(self)
        list_fr.pack(fill=BOTH, expand=True, pady=6)
        self.case_view = ttk.Treeview(list_fr, columns=("序号", "温度(°C)", "压力(MPa)"), show="headings", height=10)
        for c, w in [("序号", 80), ("温度(°C)", 120), ("压力(MPa)", 120)]:
            self.case_view.heading(c, text=c)
            self.case_view.column(c, width=w, anchor=CENTER)
        self.case_view.pack(side=LEFT, fill=BOTH, expand=True)
        vsb = ttk.Scrollbar(list_fr, orient=VERTICAL, command=self.case_view.yview)
        self.case_view.configure(yscroll=vsb.set)
        vsb.pack(side=LEFT, fill=Y)

        # 导航
        nav = Frame(self)
        nav.pack(fill=X, pady=10)
        Button(nav, text="上一步", command=lambda: self.app.show_frame("Step3Storage")).pack(side=LEFT)
        Button(nav, text="完成", command=self.finish).pack(side=RIGHT)

    def on_show(self):
        # 载入已有工况（若从输出返回）
        self.cases = list(self.app.state.get("cases", []))
        self.refresh_view()

    def add_case(self):
        try:
            t = int(self.temp_var.get())
            p = float(self.pres_var.get())
        except Exception:
            messagebox.showerror("格式错误", "温度或压力数值不合法。")
            return
        self.cases.append({"T": t, "P": p})
        self.refresh_view()

    def delete_selected(self):
        sel = self.case_view.selection()
        if not sel:
            return
        idxs = sorted([self.case_view.index(iid) for iid in sel], reverse=True)
        for i in idxs:
            if 0 <= i < len(self.cases):
                self.cases.pop(i)
        self.refresh_view()

    def clear_cases(self):
        self.cases.clear()
        self.refresh_view()

    def refresh_view(self):
        for iid in self.case_view.get_children():
            self.case_view.delete(iid)
        for i, c in enumerate(self.cases, 1):
            self.case_view.insert("", "end", values=(i, c["T"], c["P"]))

    def finish(self):
        if not self.cases:
            if not messagebox.askyesno("确认", "尚未添加任何工况，是否继续？"):
                return
        self.app.state["cases"] = list(self.cases)
        # 清理 legacy，避免混淆
        self.app.state["temperatures"] = []
        self.app.state["pressures"] = []
        self.app.show_frame("Step5Output")

# =================== Step 5: 输出与图表 =====================
class Step5Output(Frame):
    def __init__(self, parent, app: WizardApp):
        super().__init__(parent)
        self.app = app

        Label(self, text="输出与统计", font=("Microsoft YaHei UI", 16, "bold")).pack(anchor="w", pady=(10, 6))

        # 文本输出
        top = Frame(self)
        top.pack(fill=BOTH, expand=True)
        self.text = Text(top, wrap="word")
        self.text.pack(side=LEFT, fill=BOTH, expand=True)
        sb = ttk.Scrollbar(top, command=self.text.yview)
        self.text.configure(yscroll=sb.set)
        sb.pack(side=LEFT, fill=Y)

        # 图表区（matplotlib 可选）
        self.figure_canvas = None
        try:
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            import matplotlib.pyplot as plt
            self._plt = plt
            self.FigureCanvasTkAgg = FigureCanvasTkAgg
            chart_fr = LabelFrame(self, text="多工况统计图（燃速 vs. 压力/温度）")
            chart_fr.pack(fill=BOTH, expand=False, pady=8)
            self.chart_frame = chart_fr
        except Exception:
            self._plt = None
            self.chart_frame = None

        # 操作区
        ops = Frame(self)
        ops.pack(fill=X, pady=8)
        Button(ops, text="开始运行全部工况", command=self.app.run_batch).pack(side=LEFT)
        Button(ops, text="保存日志为TXT", command=self.save_log).pack(side=LEFT, padx=8)
        Button(ops, text="返回修改工况", command=lambda: self.app.show_frame("Step4PT")).pack(side=LEFT)

    def on_show(self):
        # 展示前面步骤选择的概览
        s = self.app.state
        self.append("=== 概览 ===\n")
        self.append(f"文件: mech={s['files'].get('mech','')}, thermo={s['files'].get('thermo','')}, yaml={s['files'].get('yaml','')}\n")
        self.append(f"密度: {s['density']} g/cm³\n")
        self.append(f"贮存时间: {s['storage_year']} 年\n")
        if s.get('cases'):
            for i, c in enumerate(s['cases'], 1):
                self.append(f"工况{i}：温度{c['T']}℃，压力{c['P']} MPa\n")
        else:
            self.append(f"温度(°C): {s['temperatures']}\n")
            self.append(f"压力: {s['pressures']}\n")
        self.append("================\n\n")

    def clear_output(self):
        self.text.delete("1.0", END)

    def append(self, msg: str):
        self.text.insert(END, msg)
        self.text.see(END)
        self.update_idletasks()

    def save_log(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if not path:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.text.get("1.0", END))
        messagebox.showinfo("已保存", f"日志已保存到：\n{path}")

    def draw_chart(self, summary):
        if not self._plt or not self.chart_frame:
            self.append("[INFO] 未安装 matplotlib，跳过绘图。若需图表，请安装 matplotlib。\n")
            return
        # 按温度分组，绘制多条曲线：x=Pressure, y=Burn rate
        temps = sorted({d['T'] for d in summary if d.get('burn_rate') is not None})
        if not temps:
            self.append("[WARN] 未解析到燃速结果，无法绘图。\n")
            return

        # 清理旧画布
        if self.figure_canvas:
            self.figure_canvas.get_tk_widget().destroy()
            self.figure_canvas = None

        fig = self._plt.figure(figsize=(8, 4.5), dpi=120)
        ax = fig.add_subplot(111)
        for t in temps:
            pts = [(d['P'], d['burn_rate']) for d in summary if d['T'] == t and d.get('burn_rate') is not None]
            pts.sort(key=lambda x: x[0])
            if not pts:
                continue
            xs = [p for p, _ in pts]
            ys = [r for _, r in pts]
            ax.plot(xs, ys, marker='o', label=f"T={t}°C")
        ax.set_xlabel("压力")
        ax.set_ylabel("燃速 (mm/s)")
        ax.set_title("多工况燃速统计")
        ax.grid(True, linestyle='--', linewidth=0.6, alpha=0.6)
        ax.legend()

        self.figure_canvas = self.FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.figure_canvas.draw()
        self.figure_canvas.get_tk_widget().pack(fill=BOTH, expand=True)


if __name__ == '__main__':
    # Windows 打包时的兼容
    import multiprocessing
    multiprocessing.freeze_support()

    app = WizardApp()
    app.mainloop()
