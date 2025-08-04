# core/metrics_monitor.py
# This component is a simulated system metrics monitor.

import threading
import time
import logging
import datetime
from typing import Dict, Any

# --- DevOS Component: MetricsMonitor ---
class MetricsMonitor:
    """
    Simulated class to monitor system metrics (e.g., CPU, memory).
    This would typically use a library like `psutil`.
    """
    def __init__(self):
        self.metrics = {
            "cpu_usage": [],
            "memory": [],
            "timestamps": []
        }
        self.is_monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, interval=1000):
        """Starts a background thread to record metrics at a given interval."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logging.info("Metrics monitor started.")

    def stop_monitoring(self):
        """Stops the monitoring thread."""
        self.is_monitoring = False
        logging.info("Metrics monitor stopped.")

    def _monitor_loop(self):
        """Loop to record metrics."""
        while self.is_monitoring:
            self.record_metrics()
            time.sleep(1)

    def record_metrics(self):
        """Records a snapshot of the system metrics."""
        try:
            now = datetime.datetime.now()
            # Placeholder for actual data collection using psutil
            cpu_usage = 50.0  # psutil.cpu_percent()
            memory_usage = 60.0 # psutil.virtual_memory().percent

            self.metrics["timestamps"].append(now)
            self.metrics["cpu_usage"].append(cpu_usage)
            self.metrics["memory"].append(memory_usage)
        except Exception as e:
            logging.error(f"Failed to record metrics: {e}")

    def plot_metrics(self, output_path: str):
        """
        Generates a plot of the collected metrics using Matplotlib.
        """
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            logging.error("Matplotlib not found. Cannot plot metrics.")
            # We can't use show_message here because it's not part of the main app.
            # Instead, we'll log the error and expect the main app to handle UI messaging.
            return

        if not self.metrics["timestamps"]:
            logging.info("No metrics have been recorded yet.")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(self.metrics["timestamps"], self.metrics["cpu_usage"], 'r-')
        ax1.set_title('CPU Usage')
        ax1.set_ylabel('Percentage')

        ax2.plot(self.metrics["timestamps"], self.metrics["memory"], 'b-')
        ax2.set_title('Memory Usage')
        ax2.set_ylabel('Percentage')

        plt.tight_layout()
        try:
            plt.savefig(output_path)
            logging.info(f"Metrics plot saved to {output_path}")
        except Exception as e:
            logging.error(f"Failed to save metrics plot: {e}")
