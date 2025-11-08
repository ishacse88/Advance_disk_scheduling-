# main_gui.py - Graphical User Interface and Controller
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys
from typing import List, Tuple

# Import the code from the other two files
from disk_logic import DiskScheduler, MAX_TRACK, MIN_TRACK
from disk_plotter import DiskPlotter

class DiskSchedulerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Interactive Disk Scheduling Simulator 📈")
        master.geometry("1100x750")

        # Variables
        self.requests_var = tk.StringVar(value="82, 170, 43, 140, 24, 16, 190")
        self.head_var = tk.StringVar(value="50")
        self.algorithm_var = tk.StringVar(value="SSTF")
        self.direction_var = tk.StringVar(value="UP")
        
        # ... (GUI setup code remains largely the same) ...
        style = ttk.Style()
        style.configure('TFrame', background='#e8f4f8')
        style.configure('TLabel', background='#e8f4f8', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)

        # --- Layout setup (PanedWindow, Frames) ---
        main_paned_window = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill='both', expand=True, padx=10, pady=10)
        control_frame = ttk.Frame(main_paned_window, width=400)
        main_paned_window.add(control_frame, weight=0)
        self.plot_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(self.plot_frame, weight=1)

        # --- 1. Input Configuration ---
        input_frame = ttk.LabelFrame(control_frame, text="⚙️ Input Configuration", padding="10")
        input_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(input_frame, text="Requests (Comma Separated):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.requests_entry = ttk.Entry(input_frame, textvariable=self.requests_var, width=35)
        self.requests_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(input_frame, text=f"Initial Head Position ({MIN_TRACK}-{MAX_TRACK}):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.head_entry = ttk.Entry(input_frame, textvariable=self.head_var, width=10)
        self.head_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # --- 2. Algorithm & Direction Selection ---
        select_frame = ttk.Frame(control_frame, padding="5")
        select_frame.pack(fill='x', padx=5, pady=5)
        algo_frame = ttk.LabelFrame(select_frame, text="🧮 Algorithm", padding="10")
        algo_frame.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        algorithms = ['FCFS', 'SSTF', 'SCAN', 'C-SCAN']
        for i, algo in enumerate(algorithms):
            ttk.Radiobutton(algo_frame, text=algo, variable=self.algorithm_var, value=algo).grid(row=i, column=0, sticky='w', padx=5, pady=2)
        dir_frame = ttk.LabelFrame(select_frame, text="⬆️ Direction (SCAN/C-SCAN)", padding="10")
        dir_frame.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        ttk.Radiobutton(dir_frame, text="UP (to 199)", variable=self.direction_var, value="UP").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Radiobutton(dir_frame, text="DOWN (to 0)", variable=self.direction_var, value="DOWN").grid(row=1, column=0, sticky='w', padx=5, pady=2)

        # --- 3. Control Button ---
        ttk.Button(control_frame, text="🚀 Run Simulation & Visualize", command=self.run_simulation, style='TButton', compound=tk.LEFT).pack(fill='x', pady=15, padx=5)

        # --- 4. Output Metrics ---
        output_frame = ttk.LabelFrame(control_frame, text="📊 Performance Metrics", padding="10")
        output_frame.pack(fill='x', padx=5, pady=5)
        self.labels = {}
        metrics = ["Algorithm:", "Total Seek Time:", "Average Seek Time:", "System Throughput:"]
        for i, metric in enumerate(metrics):
            ttk.Label(output_frame, text=metric, font=('Arial', 10, 'bold')).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            value_label = ttk.Label(output_frame, text="N/A", font=('Arial', 10))
            value_label.grid(row=i, column=1, sticky='w', padx=5, pady=2)
            self.labels[metric] = value_label
        ttk.Label(output_frame, text="Movement Sequence:", font=('Arial', 10, 'bold')).grid(row=len(metrics), column=0, sticky='nw', padx=5, pady=5)
        self.seq_text = scrolledtext.ScrolledText(output_frame, height=5, width=35, state='disabled', wrap='word', font=('Courier New', 9))
        self.seq_text.grid(row=len(metrics), column=1, padx=5, pady=5, sticky='ew')
        
        # --- Initialize Plot Area ---
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Initialize the Plotter object
        self.plotter = DiskPlotter(self.fig, self.ax, self.canvas)
        self.plotter.initialize_plot()


    def validate_inputs(self) -> Tuple[List[int], int] | None:
        """Validates user input."""
        try:
            head = int(self.head_var.get().strip())
            if not (MIN_TRACK <= head <= MAX_TRACK):
                messagebox.showerror("Input Error", f"Head position must be between {MIN_TRACK} and {MAX_TRACK}.")
                return None
            
            requests_str = self.requests_var.get()
            requests = [int(r.strip()) for r in requests_str.split(',') if r.strip()]
            
            if not requests:
                messagebox.showerror("Input Error", "Request list cannot be empty.")
                return None
            
            for r in requests:
                if not (MIN_TRACK <= r <= MAX_TRACK):
                    messagebox.showerror("Input Error", f"Track {r} is outside the valid range [{MIN_TRACK}-{MAX_TRACK}].")
                    return None
                    
            return requests, head
        except ValueError:
            messagebox.showerror("Input Error", "Please ensure Head Position and all Requests are valid integers.")
            return None

    def update_results(self, algorithm, sequence, total_seek, avg_seek, throughput):
        """Updates the GUI labels and text area with simulation results."""
        self.labels["Algorithm:"].config(text=f"{algorithm}")
        self.labels["Total Seek Time:"].config(text=f"{total_seek:.2f} tracks")
        self.labels["Average Seek Time:"].config(text=f"{avg_seek:.2f} tracks/request")
        self.labels["System Throughput:"].config(text=f"{throughput:.4f} requests/time_unit")
        
        self.seq_text.config(state='normal')
        self.seq_text.delete('1.0', tk.END)
        self.seq_text.insert(tk.END, ' -> '.join(map(str, sequence)))
        self.seq_text.config(state='disabled')

    def run_simulation(self):
        """Called when the Run Simulation button is pressed."""
        
        validated_inputs = self.validate_inputs()
        if not validated_inputs:
            return

        requests, initial_head = validated_inputs
        algorithm = self.algorithm_var.get()
        direction = self.direction_var.get()
        
        # Call the Logic (from disk_logic.py)
        scheduler = DiskScheduler(requests, initial_head)
        sequence, total_seek, avg_seek, throughput = scheduler.simulate(algorithm, direction)
        
        if sequence is not None:
            # Update Metrics (in this file)
            self.update_results(algorithm, sequence, total_seek, avg_seek, throughput)
            
            # Call Plotter (from disk_plotter.py)
            self.plotter.plot_sequence(sequence, algorithm, requests, initial_head, f"{total_seek:.2f}")
        else:
            messagebox.showerror("Simulation Error", "Could not run the selected algorithm.")

# =================================================================
# === PART 4: MAIN EXECUTION ======================================
# =================================================================

if __name__ == "__main__":
    
    try:
        import matplotlib.pyplot
    except ImportError:

        messagebox.showerror("Setup Error", "Matplotlib is required for the visual plot.\nPlease install it using: pip install matplotlib")
        sys.exit(1)

    root = tk.Tk()
    app = DiskSchedulerGUI(root)
    root.mainloop()