# disk_logic.py - Core Scheduling Logic (Backend)
from typing import List, Tuple

# --- Configuration Constants ---
MAX_TRACK = 199 
MIN_TRACK = 0
SEEK_TIME_PER_TRACK = 1.0 

class DiskScheduler:
    """
    Core logic for disk scheduling algorithms: FCFS, SSTF, SCAN, C-SCAN.
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

    def simulate(self, algorithm: str, direction: str = 'UP') -> Tuple[List[int], float, float, float] | Tuple[None, None, None, None]:
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
        """First-Come, First-Served simulation."""
        current_requests = self.requests[:]
        while current_requests:
            next_track = current_requests.pop(0)
            seek = abs(next_track - self.head_position)
            self.total_seek_time += seek
            self.head_position = next_track
            self.movement_sequence.append(next_track)

    def _sstf(self):
        """Shortest Seek Time First simulation."""
        current_requests = self.requests[:]
        while current_requests:
            # Find the request with the minimum distance
            next_track = min(current_requests, 
                             key=lambda track: abs(track - self.head_position))
            
            seek = abs(next_track - self.head_position)
            self.total_seek_time += seek
            self.head_position = next_track
            self.movement_sequence.append(next_track)
            current_requests.remove(next_track)
            
    def _scan_or_cscan(self, algorithm: str, direction: str):
        """Common logic for SCAN (Elevator) and C-SCAN."""
        requests = sorted(self.requests)
        current_head = self.initial_head
        
        lower = [r for r in requests if r < current_head]
        upper = [r for r in requests if r >= current_head]
        
        sequence = []
        boundaries = []

        if direction == 'UP':
            current_list = sorted(upper)
            other_list = sorted(lower)
            if algorithm == 'SCAN':
                boundaries = [MAX_TRACK] 
                other_list.reverse()
            elif algorithm == 'C-SCAN':
                boundaries = [MAX_TRACK, MIN_TRACK] 

        elif direction == 'DOWN':
            current_list = sorted(lower, reverse=True)
            other_list = sorted(upper, reverse=True)
            if algorithm == 'SCAN':
                boundaries = [MIN_TRACK] 
                other_list.reverse()
            elif algorithm == 'C-SCAN':
                boundaries = [MIN_TRACK, MAX_TRACK] 

        sequence.extend(current_list)
        
        if algorithm == 'SCAN':
            sequence.extend(boundaries) 
            sequence.extend(other_list)
        elif algorithm == 'C-SCAN':
            sequence.extend(boundaries)
            
            if direction == 'UP':
                sequence.extend(sorted(lower)) 
            elif direction == 'DOWN':
                sequence.extend(sorted(upper, reverse=True)) 

        # Calculate seek time
        for next_track in sequence:
            seek = abs(next_track - self.head_position)
            
            # C-SCAN jump (0 seek time)
            if (algorithm == 'C-SCAN' and 
                ((self.head_position == MAX_TRACK and next_track == MIN_TRACK) or
                 (self.head_position == MIN_TRACK and next_track == MAX_TRACK))):
                seek = 0
            
            self.total_seek_time += seek
            self.head_position = next_track
            self.movement_sequence.append(next_track)