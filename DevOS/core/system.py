import psutil
import time
import threading
from collections import deque
from typing import Dict, List, Any, Deque

class SystemMonitor:
    """
    Monitors system-wide resource usage (CPU, Memory) in a background thread.

    Collects real-time metrics and maintains a historical buffer.
    """

    def __init__(self, history_length: int = 60):
        """
        Initializes the SystemMonitor.

        Args:
            history_length (int): The number of recent data points to keep in history.
                                  Defaults to 60 (e.g., last 60 seconds if interval is 1s).
        """
        self._cpu_history: Deque[float] = deque(maxlen=history_length)
        self._memory_history: Deque[float] = deque(maxlen=history_length)
        self._timestamps: Deque[str] = deque(maxlen=history_length)

        self._is_monitoring: bool = False
        self._monitor_thread: threading.Thread = None
        self._lock = threading.Lock() # To ensure thread-safe access to histories

    def start_monitoring(self, interval: int = 1):
        """
        Starts the background thread for continuous system monitoring.

        Args:
            interval (int): The interval (in seconds) between data collection points.
        """
        if self._is_monitoring:
            print("System monitoring is already running.")
            return

        self._is_monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,), daemon=True)
        self._monitor_thread.start()
        print(f"System monitoring started with {interval}-second interval.")

    def stop_monitoring(self):
        """
        Stops the background monitoring thread.
        """
        if not self._is_monitoring:
            print("System monitoring is not running.")
            return

        self._is_monitoring = False
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5) # Wait for the thread to finish
            if self._monitor_thread.is_alive():
                print("Warning: Monitoring thread did not terminate gracefully.")
        print("System monitoring stopped.")

    def _monitor_loop(self, interval: int):
        """
        The main loop for collecting system metrics. Runs in a separate thread.
        """
        while self._is_monitoring:
            try:
                cpu_percent = psutil.cpu_percent(interval=None) # Non-blocking call for instantaneous CPU
                memory_percent = psutil.virtual_memory().percent
                timestamp = time.strftime('%H:%M:%S')

                with self._lock:
                    self._cpu_history.append(cpu_percent)
                    self._memory_history.append(memory_percent)
                    self._timestamps.append(timestamp)

                time.sleep(interval)
            except Exception as e:
                print(f"Error during system monitoring: {e}")
                self._is_monitoring = False # Stop monitoring on error
                break

    def get_latest_metrics(self) -> Dict[str, Any]:
        """
        Retrieves the most recent CPU and Memory usage percentages.

        Returns:
            Dict[str, Any]: A dictionary containing 'cpu_percent', 'memory_percent', and 'timestamp'.
                            Returns default values (0, 0, 'N/A') if no data is available.
        """
        with self._lock:
            return {
                'cpu_percent': self._cpu_history[-1] if self._cpu_history else 0.0,
                'memory_percent': self._memory_history[-1] if self._memory_history else 0.0,
                'timestamp': self._timestamps[-1] if self._timestamps else 'N/A'
            }

    def get_historical_metrics(self) -> Dict[str, List[Any]]:
        """
        Retrieves the historical CPU, Memory, and Timestamp data.

        Returns:
            Dict[str, List[Any]]: A dictionary with 'cpu_history', 'memory_history', and 'timestamps' lists.
        """
        with self._lock:
            return {
                'cpu_history': list(self._cpu_history),
                'memory_history': list(self._memory_history),
                'timestamps': list(self._timestamps)
            }

# Example usage of SystemMonitor
if __name__ == '__main__':
    monitor = SystemMonitor(history_length=10)
    print("Starting system monitor for 5 seconds...")
    monitor.start_monitoring(interval=1)

    # Let it collect some data
    time.sleep(5)

    print("\nLatest metrics:")
    latest = monitor.get_latest_metrics()
    print(f"CPU: {latest['cpu_percent']:.2f}% | Memory: {latest['memory_percent']:.2f}% at {latest['timestamp']}")

    print("\nHistorical metrics:")
    history = monitor.get_historical_metrics()
    for i in range(len(history['timestamps'])):
        print(f"Time: {history['timestamps'][i]} | CPU: {history['cpu_history'][i]:.2f}% | Memory: {history['memory_history'][i]:.2f}%")

    print("\nStopping monitor...")
    monitor.stop_monitoring()
    print("Monitor stopped.")

    # Try starting again after stopping
    print("\nStarting monitor again for 2 seconds...")
    monitor.start_monitoring(interval=1)
    time.sleep(2)
    latest = monitor.get_latest_metrics()
    print(f"CPU: {latest['cpu_percent']:.2f}% | Memory: {latest['memory_percent']:.2f}% at {latest['timestamp']}")
    monitor.stop_monitoring()
