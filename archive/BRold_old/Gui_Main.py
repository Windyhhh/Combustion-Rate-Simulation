import os
import sys
import subprocess
#from run import run_simulation_core
import threading
from tkinter import *
from tkinter import filedialog, ttk, messagebox

def get_embedded_python_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, filename)

class CombustionSimulatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Energetic Material Combustion Simulator")
        master.geometry("1080x950")

        self.species_names = [
            "NC(L)", "NG(L)", "ZDJ(L)", "DINA(L)", "DEP(L)",
            "Ni", "Co3O4", "C8H4O4Pb", "MgO", "C",
            "C6H8O4Cu", "C14H10O8Pb", "C14H10O8Cu", "C14H10O6Pb",
            "C14H10O6Cu", "Al2O3", "Al", "CaCO3", "Pb(NO3)2",
            "Cu(NO3)2", "C2F4", "DAQ-Mg-1", "DAQ-Mg-2", "DAQ-Mg-3",
            "DAQ-Mg-4"
        ]
        self.SPECIES_MW = {
            "NC(L)": 299.0,
            "NG(L)": 227.0,
            "ZDJ(L)": 240.0,
            "DINA(L)": 240.0,
            "DEP(L)": 222.0,

            # 以下请按你的数据补齐；未知可先设为 None，运行时报错提示
            "Ni": 1,
            "Co3O4": 1,
            "C8H4O4Pb": 1,
            "MgO": 1,
            "C": 1,
            "C6H8O4Cu": 1,
            "C14H10O8Pb": 1,
            "C14H10O8Cu": 1,
            "C14H10O6Pb": 1,
            "C14H10O6Cu": 1,
            "Al2O3": 1,
            "Al": 1,
            "CaCO3": 1,
            "Pb(NO3)2": 1,
            "Cu(NO3)2": 1,
            "C2F4": 1,
            "DAQ-Mg-1": 1,
            "DAQ-Mg-2": 1,
            "DAQ-Mg-3": 1,
            "DAQ-Mg-4": 1,
            "C28H18O10Mg": 1,
        }

        self.proc = None
        self.sim_thread = None

        # 控件管理
        self.input_widgets = []
        self.runtime_buttons = []
        self.editable_table = None

        self.file_paths = {}

        self.init_widgets()

    def init_widgets(self):
        # === Parameter Inputs ===
        param_frame = Frame(self.master)
        param_frame.pack(pady=10)

        Label(param_frame, text="Density (g/cm3):").grid(row=0, column=0, padx=5)
        self.entry_density = Entry(param_frame)
        self.entry_density.insert(0, "1.6")
        self.entry_density.grid(row=0, column=1, padx=5)
        self.input_widgets.append(self.entry_density)

        Label(param_frame, text="Initial Pressure (atm):").grid(row=0, column=2, padx=5)
        self.entry_press = Entry(param_frame)
        self.entry_press.insert(0, "80.0")
        self.entry_press.grid(row=0, column=3, padx=5)
        self.input_widgets.append(self.entry_press)

        Label(param_frame, text="Initial Temperature (K):").grid(row=0, column=4, padx=5)
        self.entry_temp = Entry(param_frame)
        self.entry_temp.insert(0, "298.0")
        self.entry_temp.grid(row=0, column=5, padx=5)
        self.input_widgets.append(self.entry_temp)
        
        # === 第二行：环境参数 ===
        Label(param_frame, text="Environment Temp (K):").grid(row=1, column=0, padx=5)
        self.entry_env_temp = Entry(param_frame)
        self.entry_env_temp.insert(0, "298.0")
        self.entry_env_temp.grid(row=1, column=1, padx=5)
        self.input_widgets.append(self.entry_env_temp)

        Label(param_frame, text="Humidity (%):").grid(row=1, column=2, padx=5)
        self.entry_humidity = Entry(param_frame)
        self.entry_humidity.insert(0, "50.0")
        self.entry_humidity.grid(row=1, column=3, padx=5)
        self.input_widgets.append(self.entry_humidity)

        Label(param_frame, text="Storage Time (days):").grid(row=1, column=4, padx=5)
        self.entry_storage = Entry(param_frame)
        self.entry_storage.insert(0, "30")
        self.entry_storage.grid(row=1, column=5, padx=5)
        self.input_widgets.append(self.entry_storage)


        # === File Selectors ===
        file_frame = Frame(self.master)
        file_frame.pack(pady=10)

        def create_file_selector(label_text, key, row):
            Label(file_frame, text=label_text).grid(row=row, column=0, sticky=W, padx=5)
            entry = Entry(file_frame, width=80)
            entry.grid(row=row, column=1, padx=5)
            Button(file_frame, text="Browse", command=lambda: self.select_file(entry, key)).grid(row=row, column=2, padx=5)
            self.file_paths[key] = entry
            self.input_widgets.append(entry)

        create_file_selector("Liquid-phase mechanism file:", "mech", 0)
        create_file_selector("Molecular parameters data file:", "thermo", 1)
        create_file_selector("Gas-phase mechanism file:", "yaml", 2)

        # === Species Table ===
        species_frame = Frame(self.master)
        species_frame.pack(pady=10)
        Label(species_frame, text="Species Table").pack()

        columns = ("Name", "Content")
        self.tree = ttk.Treeview(species_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180 if col == "Name" else 120)
        self.tree.pack(side=LEFT)
        self.editable_table = self.tree
        self.tree.bind("<Double-1>", self.on_treeview_double_click)

        scrollbar_y = Scrollbar(species_frame, orient=VERTICAL, command=self.tree.yview)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree.configure(yscroll=scrollbar_y.set)

        # 默认物种（不再显示 MW，只显示 Name、Content）
        default_species = [
            ("NC(L)", 54.5),
            ("NG(L)", 30.0),
            ("ZDJ(L)", 1.5),
            ("DINA(L)", 3.5),
            ("DEP(L)", 10.5),
        ]

        for name, content in default_species:
            self.tree.insert("", "end", values=(name, content))
        for _ in range(22 - len(default_species)):
            self.tree.insert("", "end", values=("", ""))

        # === Output Text Area ===
        output_frame = Frame(self.master)
        output_frame.pack(pady=10, fill='both', expand=True)

        Label(output_frame, text="Simulation Output:").pack()
        self.text_output = Text(output_frame, wrap="word", height=15)
        self.text_output.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(output_frame, command=self.text_output.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_output.config(yscrollcommand=scrollbar.set)

        # === Control Buttons ===
        button_frame = Frame(self.master)
        button_frame.pack(pady=10)

        start_btn = Button(button_frame, text="Start Simulation", command=self.run_simulation)
        start_btn.grid(row=0, column=0, padx=10)
        self.runtime_buttons.append(start_btn)

        save_btn = Button(button_frame, text="Save Log to TXT", command=self.save_log)
        save_btn.grid(row=0, column=1, padx=10)
        self.runtime_buttons.append(save_btn)

        Button(button_frame, text="Exit", command=self.exit_program).grid(row=0, column=2, padx=10)

        self.stop_button = Button(button_frame, text="Stop Simulation", command=self.stop_simulation, state='disabled')
        self.stop_button.grid(row=0, column=3, padx=10)

    def disable_inputs(self):
        for widget in self.input_widgets:
            widget.config(state='disabled')
        for btn in self.runtime_buttons:
            btn.config(state='disabled')
        self.tree.unbind("<Double-1>")
        self.stop_button.config(state='normal')

    def enable_inputs(self):
        for widget in self.input_widgets:
            widget.config(state='normal')
        for btn in self.runtime_buttons:
            btn.config(state='normal')
        self.tree.bind("<Double-1>", self.on_treeview_double_click)
        self.stop_button.config(state='disabled')

    def on_treeview_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.edit_species_row(item_id)

    def edit_species_row(self, iid):
        top = Toplevel(self.master)
        top.title("Edit Species Entry")
        values = self.tree.item(iid, "values")
    
        # 兼容：values 可能为空或长度异常
        cur_name = values[0] if len(values) >= 1 else ""
        cur_content = values[1] if len(values) >= 2 else ""
    
        # 第1行：Name（下拉）
        Label(top, text="Species Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_var = StringVar(value=cur_name)
        name_cb = ttk.Combobox(top, textvariable=name_var, values=self.species_names, state="readonly", width=28)
        name_cb.grid(row=0, column=1, padx=5, pady=5)
    
        # 第2行：Content（数值）
        Label(top, text="Initial Content:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        content_var = StringVar(value=str(cur_content))
        Entry(top, textvariable=content_var, width=30).grid(row=1, column=1, padx=5, pady=5)
    
        def save():
            new_name = name_var.get().strip()
            try:
                content_val = float(content_var.get())
            except Exception:
                messagebox.showwarning("输入错误", "Content 必须是数字。")
                return
    
            # 互斥校验（保持原逻辑）
            existing_names = [
                self.tree.item(child)["values"][0]
                for child in self.tree.get_children()
                if child != iid and self.tree.item(child)["values"] and self.tree.item(child)["values"][0]
            ]

            # 定义互斥组
            daq_mg_set = {"DAQ-Mg-1", "DAQ-Mg-2", "DAQ-Mg-3", "DAQ-Mg-4"}
            has_mgo = "MgO" in existing_names
            has_daq = any(name in daq_mg_set for name in existing_names)

            # 如果新选的是 MgO
            if new_name == "MgO":
                if has_mgo:
                    messagebox.showwarning("非法添加", "当前已包含 MgO，不能再添加 MgO。")
                    return
                if has_daq:
                    messagebox.showwarning("非法添加", "当前已包含 DAQ-Mg 系列物种，不能再添加 MgO。")
                    return

            # 如果新选的是 DAQ-Mg 系列
            if new_name in daq_mg_set:
                if has_daq:
                    messagebox.showwarning("非法添加", "DAQ-Mg-1/2/3/4 只能存在一个，不能重复。")
                    return
                if has_mgo:
                    messagebox.showwarning("非法添加", "当前已包含 MgO，不能再添加 DAQ-Mg 系列物种。")
                    return
    
            # 写回 Treeview：只两列
            self.tree.item(iid, values=(new_name, content_val))
            top.destroy()
    
        Button(top, text="Save", command=save).grid(row=2, column=0, columnspan=2, pady=10)

    def select_file(self, entry_widget, key):
        path = filedialog.askopenfilename()
        if path:
            entry_widget.delete(0, END)
            entry_widget.insert(0, path)

    def get_simulation_input(self):
        try:
            density = float(self.entry_density.get())
            press = float(self.entry_press.get())
            temp = float(self.entry_temp.get())
            env_temp = float(self.entry_env_temp.get())
            humidity = float(self.entry_humidity.get())
            storage_time = float(self.entry_storage.get())
            mech = self.file_paths['mech'].get()
            thermo = self.file_paths['thermo'].get()
            yaml = self.file_paths['yaml'].get()
            

            if not (mech and thermo and yaml):
                raise ValueError("All input files must be selected.")

            self.text_output.insert(END, f"Selected files:\n  Mechanism: {mech}\n  Thermo: {thermo}\n  YAML: {yaml}\n\n")

            species_data = []
            total_content = 0.0
            for item in self.tree.get_children():
                values = self.tree.item(item)["values"]
                # 现在表格是两列：(Name, Content)
                if len(values) >= 2 and str(values[0]).strip() and str(values[1]).strip():
                    name = str(values[0]).strip()
                    try:
                        content = float(values[1])
                    except Exception:
                        raise ValueError(f"Content 必须为数字：{name}")
                    mw = self.SPECIES_MW.get(name, None)
                    if mw is None:
                        raise ValueError(f"缺少分子量（MW）定义：{name}，请在 self.SPECIES_MW 中补充。")
                    species_data.append([name, float(mw), content])
                    total_content += content

            if total_content == 0:
                raise ValueError("Total species content cannot be zero.")

            # 归一化
            for spec in species_data:
                spec[2] /= total_content

            # ✅ 把环境参数也返回
            return density, press, temp, env_temp, humidity, storage_time, mech, thermo, yaml, species_data
        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return None

    def run_simulation(self):
        result = self.get_simulation_input()
        if result is None:
            return

        self.disable_inputs()

        density, press, temp, env_temp, humidity, storage_time, mech, thermo, yaml, species = result

        formula_str = ", ".join([f"{s[0]}: {s[2]:.2f}" for s in species])
        self.text_output.insert(END, f"\nRunning simulation with:\n"
                                     f"  Density = {density} g/cm³\n"
                                     f"  Pressure = {press} atm\n"
                                     f"  Temperature = {temp} K\n"
                                     f"  Environment Temp = {env_temp} K\n"
                                     f"  Humidity = {humidity} %\n"
                                     f"  Storage Time = {storage_time} days\n"
                                     f"  Formula = {formula_str}\n\n")
        self.text_output.see(END)

        import json
        config_data = {
            "density": density,
            "pressure": press,
            "Tinit": temp,
            "environment_temp": env_temp,   # ✅ 新增
            "humidity": humidity,           # ✅ 新增
            "storage_time": storage_time,   # ✅ 新增
            "liquid_phase_mech_file": mech,
            "thermo_data_file": thermo,
            "gas_phase_yaml_file": yaml,
            "species": [
                {"name": s[0], "molecular_weight": s[1], "amount": s[2]} for s in species
            ]
        }
        with open("config_input.json", "w") as f:
            json.dump(config_data, f, indent=4)

        def task():
            try:
                env = os.environ.copy()
                run_exe_path = sys.executable
                self.proc = subprocess.Popen(
                    [run_exe_path, "run.py", "--config", "config_input.json"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env
                )
        
                for line in self.proc.stdout:
                    self.text_output.insert(END, line)
                    self.text_output.see(END)
                    self.master.update_idletasks()
        
                self.proc.wait()
            except Exception as e:
                self.text_output.insert(END, f"Error: {str(e)}\n")
            finally:
                self.proc = None
                self.enable_inputs()


        self.sim_thread = threading.Thread(target=task)
        self.sim_thread.start()

    def stop_simulation(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            self.text_output.insert(END, "\nSimulation forcefully terminated by user.\n")
            self.text_output.see(END)
        self.enable_inputs()

    def exit_program(self):
        if self.proc and self.proc.poll() is None:
            try:
                self.proc.terminate()
            except Exception as e:
                print("Terminate failed:", e)

        self.master.quit()
        self.master.destroy()

    def save_log(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.text_output.get("1.0", END))


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    root = Tk()
    app = CombustionSimulatorGUI(root)
    root.mainloop()
