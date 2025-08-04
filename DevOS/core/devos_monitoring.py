import time
import psutil
import matplotlib.pyplot as plt
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "cpu": [],
            "memory": [],
            "timestamps": []
        }
    
    def start_monitoring(self, interval=1, duration=60):
        end_time = time.time() + duration
        while time.time() < end_time:
            self.metrics["cpu"].append(psutil.cpu_percent())
            self.metrics["memory"].append(psutil.virtual_memory().percent)
            self.metrics["timestamps"].append(datetime.now().strftime("%H:%M:%S"))
            time.sleep(interval)
    
    def generate_report(self, output_path):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        ax1.plot(self.metrics["timestamps"], self.metrics["cpu"], 'r-')
        ax1.set_title('CPU Usage')
        ax1.set_ylabel('Percentage')
        
        ax2.plot(self.metrics["timestamps"], self.metrics["memory"], 'b-')
        ax2.set_title('Memory Usage')
        ax2.set_ylabel('Percentage')
        
        plt.tight_layout()
        plt.savefig(output_path)
        return f"Report saved to {output_path}"
    
    def optimize_react(self, app_path):
        # Run React optimization tools
        cmds = [
            f"cd {app_path}",
            "npm install -g source-map-explorer",
            "npm run build",
            "source-map-explorer build/static/js/*.js"
        ]
        result = subprocess.run(" && ".join(cmds), shell=True, capture_output=True)
        return result.stdout.decode()