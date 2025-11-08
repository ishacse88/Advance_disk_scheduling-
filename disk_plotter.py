# disk_plotter.py - Data Visualization and Comparison
import matplotlib.pyplot as plt
from typing import List, Tuple

# Constants used for plot boundaries (must match disk_logic.py)
MIN_TRACK = 0
MAX_TRACK = 199

class DiskPlotter:
    """
    Handles all Matplotlib plotting functionality for the simulator.
    """
    def __init__(self, fig, ax, canvas):
        self.fig = fig
        self.ax = ax
        self.canvas = canvas
        self.initialize_plot()

    def initialize_plot(self):
        """Sets up the initial empty plot area."""
        self.ax.clear()
        self.ax.set_title("Disk Head Movement Visualization")
        self.ax.set_xlabel("Time Step (Request Order)")
        self.ax.set_ylabel(f"Track Number ({MIN_TRACK}-{MAX_TRACK})")
        self.ax.set_xlim(-0.5, 1)
        self.ax.set_ylim(MIN_TRACK - 10, MAX_TRACK + 10)
        self.ax.grid(True, linestyle='--')
        self.canvas.draw()
        
    def plot_sequence(self, sequence: List[int], algorithm: str, requests: List[int], initial_head: int, total_seek_str: str):
        """Generates and displays the plot for a single algorithm run."""
        self.initialize_plot()
        
        x = list(range(len(sequence)))
        y = sequence
        
        self.ax.plot(x, y, marker='o', linestyle='-', color='b', label=f'{algorithm} Path', linewidth=2)
        
        # Mark requests served (excluding initial position)
        served_requests = set(requests)
        for i, track in enumerate(y):
            if track in served_requests and i > 0:
                 self.ax.scatter(x[i], y[i], color='r', marker='x', s=100, zorder=3)
        
        # Mark the initial position
        self.ax.scatter(0, initial_head, color='g', marker='D', s=150, zorder=5, label='Start Head')
        
        self.ax.set_title(f"Disk Head Movement: {algorithm} (Total Seek: {total_seek_str})", fontsize=12)
        self.ax.set_xlim(-0.5, len(sequence) - 0.5)
        self.ax.axhline(initial_head, color='g', linestyle=':', alpha=0.5, label='Initial Head Pos')
        
        self.ax.grid(True, linestyle='--')
        self.ax.legend(loc='best')
        self.canvas.draw()