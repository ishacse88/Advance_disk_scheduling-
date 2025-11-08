import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Configuration Constants ---
MAX_TRACK = 199 
MIN_TRACK = 0
SEEK_TIME_PER_TRACK = 1.0 

# =================================================================
# === PART 1: DISK SCHEDULING LOGIC (Backend Class) ================

# =================================================================

class DiskScheduler:
    """
    A class containing the core logic for disk scheduling algorithms.
    """
    def __init__(self, requests: List[int], initial_head: int = 50):
        self.initial_requests = requests[:]
        self.initial_head = initial_head
        self.head_position = initial_head
        self.total_seek_time = 0
        self.movement_sequence = [initial_head]

    def _calculate_metrics(self) -> Tuple[float, float, float]:
        """Calculates performance metrics."""
        total_time = self.total_seek_time * SEEK_TIME_PER_TRACK
        num_requests = len(self.initial_requests)
        
        avg_seek_time = self.total_seek_time / num_requests if num_requests else 0
        throughput = num_requests / total_time if total_time > 0 else 0
        
        return self.total_seek_time, avg_seek_time, throughput

    def simulate(self, algorithm: str, direction: str = 'UP'):
        """Runs the specified algorithm and returns results."""
        self.head_position = self.initial_head
        self.requests = self.initial_requests[:]
        self.total_seek_time = 0
        self.movement_sequence = [self.initial_head]
        
        if algorithm == 'FCFS':
            self._fcfs()
        elif algorithm == 'SSTF':
            self._sstf()
        elif algorithm in ('SCAN', 'C-SCAN'):
            self._scan_or_cscan(algorithm, direction)
        else:
            return None, None, None, None

        total_seek, avg_seek, throughput = self._calculate_metrics()
        
        return self.movement_sequence, total_seek, avg_seek, throughput

    def _fcfs(self):
        current_requests = self.requests[:]
        while current_requests:
            next_track = current_requests.pop(0)
            seek = abs(next_track - self.head_position)
            self.total_seek_time += seek
            self.head_position = next_track
            self.movement_sequence.append(next_track)

    def _sstf(self):
        current_requests = self.requests[:]
        while current_requests:
            next_track = min(current_requests, 
                             key=lambda track: abs(track - self.head_position))
            
            seek = abs(next_track - self.head_position)
            self.total_seek_time += seek
            self.head_position = next_track
            self.movement_sequence.append(next_track)
            current_requests.remove(next_track)
            
    def _scan_or_cscan(self, algorithm: str, direction: str):
        requests = sorted(self.requests)
        current_head = self.initial_head
        
        lower = [r for r in requests if r < current_head]
        upper = [r for r in requests if r >= current_head]
        
        sequence = []
        boundaries = []

        if direction == 'UP':
            current_list = sorted(upper)
            other_list = sorted(lower, reverse=True)
            if algorithm == 'SCAN':
                boundaries = [MAX_TRACK] 
            elif algorithm == 'C-SCAN':
                boundaries = [MAX_TRACK, MIN_TRACK] 

        elif direction == 'DOWN':
            current_list = sorted(lower, reverse=True)
            other_list = sorted(upper)
            if algorithm == 'SCAN':
                boundaries = [MIN_TRACK] 
            elif algorithm == 'C-SCAN':
                boundaries = [MIN_TRACK, MAX_TRACK] 

        # 1. Primary Direction
        sequence.extend(current_list)
        
        # 2. Boundary and Secondary Sweep
        if algorithm == 'SCAN':
            sequence.extend(boundaries) 
            sequence.extend(other_list)
        elif algorithm == 'C-SCAN':
            sequence.extend(boundaries)
            
            if direction == 'UP':
                sequence.extend(sorted(lower)) 
            elif direction == 'DOWN':
                sequence.extend(sorted(upper, reverse=True)) 

        # 3. Calculate seek time
        for next_track in sequence:
            seek = abs(next_track - self.head_position)
            
            # Handle C-SCAN wrap-around jump (0 seek time)
            if (algorithm == 'C-SCAN' and 
                ((self.head_position == MAX_TRACK and next_track == MIN_TRACK) or
                 (self.head_position == MIN_TRACK and next_track == MAX_TRACK))):
                seek = 0
            
            self.total_seek_time += seek
            self.head_position = next_track
            self.movement_sequence.append(next_track)

# =================================================================
# === PART 2: GUI IMPLEMENTATION ============
# =================================================================

class DiskSchedulerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Interactive Disk Scheduling Simulator 📈")
        master.geometry("1100x750") # Increased size for the plot

        # Variables
        self.requests_var = tk.StringVar(value="82, 170, 43, 140, 24, 16, 190")
        self.head_var = tk.StringVar(value="50")
        self.algorithm_var = tk.StringVar(value="SSTF")
        self.direction_var = tk.StringVar(value="UP")
        
        # Style
        style = ttk.Style()
        style.configure('TFrame', background='#e8f4f8')
        style.configure('TLabel', background='#e8f4f8', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10, 'bold'), padding=5)

        # --- Main Frame (Split into Control Panel and Plot) ---
        main_paned_window = ttk.PanedWindow(master, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill='both', expand=True, padx=10, pady=10)

        # --- Control Panel Frame (Left Side) ---
        control_frame = ttk.Frame(main_paned_window, width=400)
        main_paned_window.add(control_frame, weight=0)

        # --- Plot Frame (Right Side) ---
        self.plot_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(self.plot_frame, weight=1)

        # --- 1. Input Configuration ---
        input_frame = ttk.LabelFrame(control_frame, text="⚙️ Input Configuration", padding="10")
        input_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(input_frame, text="Requests (Comma Separated):").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.requests_entry = ttk.Entry(input_frame, textvariable=self.requests_var, width=35)
        self.requests_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        
        ttk.Label(input_frame, text="Initial Head Position (0-199):").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.head_entry = ttk.Entry(input_frame, textvariable=self.head_var, width=10)
        self.head_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # --- 2. Algorithm & Direction Selection ---
        select_frame = ttk.Frame(control_frame, padding="5")
        select_frame.pack(fill='x', padx=5, pady=5)

        # Algorithm Selection
        algo_frame = ttk.LabelFrame(select_frame, text="🧮 Algorithm", padding="10")
        algo_frame.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        
        algorithms = ['FCFS', 'SSTF', 'SCAN', 'C-SCAN']
        for i, algo in enumerate(algorithms):
            ttk.Radiobutton(algo_frame, text=algo, variable=self.algorithm_var, value=algo).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            
        # Direction Selection
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
            
        # Movement Sequence Display (Scrolled Text)
        ttk.Label(output_frame, text="Movement Sequence:", font=('Arial', 10, 'bold')).grid(row=len(metrics), column=0, sticky='nw', padx=5, pady=5)
        self.seq_text = scrolledtext.ScrolledText(output_frame, height=5, width=35, state='disabled', wrap='word', font=('Courier New', 9))
        self.seq_text.grid(row=len(metrics), column=1, padx=5, pady=5, sticky='ew')
        
        # --- Initialize Plot Area ---
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.initialize_plot()


    def initialize_plot(self):
        """Sets up the initial empty plot."""
        self.ax.clear()
        self.ax.set_title("Disk Head Movement Visualization")
        self.ax.set_xlabel("Time Step (Request Order)")
        self.ax.set_ylabel("Track Number")
        self.ax.set_xlim(-0.5, 1) # Placeholder x-limit
        self.ax.set_ylim(MIN_TRACK - 10, MAX_TRACK + 10)
        self.ax.grid(True, linestyle='--')
        self.canvas.draw()
        
    def plot_sequence(self, sequence: List[int], algorithm: str, requests: List[int], initial_head: int):
        """Generates the plot of the disk head movement."""
        self.ax.clear()
        
        x = list(range(len(sequence)))
        y = sequence
        
        # 1. Plot the movement line
        self.ax.plot(x, y, marker='o', linestyle='-', color='b', label=f'{algorithm} Path')
        
        # 2. Mark the requests (excluding initial_head)
        request_indices = [i for i, track in enumerate(y) if track in requests and i > 0]
        request_tracks = [y[i] for i in request_indices]
        request_x = [x[i] for i in request_indices]
        
        self.ax.scatter(request_x, request_tracks, color='r', marker='x', s=100, label='Request Served')
        
        # 3. Mark the initial position
        self.ax.scatter(0, initial_head, color='g', marker='D', s=150, zorder=5, label='Start Head')
        
        # 4. Annotate requests
        # Note: This is optional and can clutter the graph for large datasets
        # for i, txt in enumerate(y):
        #     self.ax.annotate(txt, (x[i], y[i]), textcoords="offset points", xytext=(0,10), ha='center')

        # Set title and labels
        self.ax.set_title(f"Disk Head Movement: {algorithm} (Total Seek: {self.labels['Total Seek Time:'].cget('text')})", fontsize=12)
        self.ax.set_xlabel("Time Step (Order of Service)")
        self.ax.set_ylabel(f"Track Number ({MIN_TRACK} to {MAX_TRACK})")
        self.ax.set_xlim(-0.5, len(sequence) - 0.5)
        self.ax.set_ylim(MIN_TRACK - 10, MAX_TRACK + 10)
        
        # Add a horizontal line for the initial head position
        self.ax.axhline(initial_head, color='g', linestyle=':', alpha=0.5, label='Initial Head Pos')
        
        self.ax.grid(True, linestyle='--')
        self.ax.legend(loc='best')
        self.canvas.draw()


    def validate_inputs(self) -> Tuple[List[int], int] | None:
        """Validates user input and returns requests and head position."""
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
        
        # Update Movement Sequence Text Box
        self.seq_text.config(state='normal')
        self.seq_text.delete('1.0', tk.END)
        if sequence:
            # Display sequence with a line break every 10 elements for readability
            seq_str = ' -> '.join(map(str, sequence))
            self.seq_text.insert(tk.END, seq_str)
        else:
            self.seq_text.insert(tk.END, "No movement sequence generated.")
        self.seq_text.config(state='disabled')

    def run_simulation(self):
        """Called when the Run Simulation button is pressed."""
        
        validated_inputs = self.validate_inputs()
        if not validated_inputs:
            return

        requests, initial_head = validated_inputs
        algorithm = self.algorithm_var.get()
        direction = self.direction_var.get()
        
        # Initialize and Run
        scheduler = DiskScheduler(requests, initial_head)
        
        sequence, total_seek, avg_seek, throughput = scheduler.simulate(algorithm, direction)
        
        if sequence is not None:
            self.update_results(algorithm, sequence, total_seek, avg_seek, throughput)
            self.plot_sequence(sequence, algorithm, requests, initial_head)
            # messagebox.showinfo("Simulation Complete", f"{algorithm} simulation finished!")
        else:
            messagebox.showerror("Simulation Error", "Could not run the selected algorithm.")

# =================================================================
# === PART 3: MAIN EXECUTION ======================================
# =================================================================

if __name__ == "__main__":
    # Check for Matplotlib installation
    try:
        import matplotlib.pyplot
    except ImportError:
        messagebox.showerror("Setup Error", "Matplotlib is required for the visual plot.\nPlease install it using: pip install matplotlib")
        sys.exit(1)

    root = tk.Tk()
    app = DiskSchedulerGUI(root)
    root.mainloop()