import json
import os
from datetime import datetime

class DevelopmentTracker:
    TRACKING_FILE = "devos_progress.json"
    
    def __init__(self):
        self.data = self.load_data()
        
    def load_data(self):
        if os.path.exists(self.TRACKING_FILE):
            try:
                with open(self.TRACKING_FILE) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self.create_default_tracking()
        return self.create_default_tracking()
        
    def create_default_tracking(self):
        return {
            "languages": {},
            "frameworks": {
                "react": {"progress": 0, "last_updated": None},
                "react_native": {"progress": 0, "last_updated": None},
                "jetpack_compose": {"progress": 0, "last_updated": None},
                "flutter": {"progress": 0, "last_updated": None},
                "kotlin": {"progress": 0, "last_updated": None}
            },
            "projects": {}
        }
    
    def track_framework_progress(self, framework, progress):
        if framework in self.data["frameworks"]:
            self.data["frameworks"][framework]["progress"] = progress
            self.data["frameworks"][framework]["last_updated"] = datetime.now().isoformat()
            self.save()
            return True
        return False
    
    def get_framework_progress(self, framework):
        return self.data["frameworks"].get(framework, {}).get("progress", 0)
    
    def save(self):
        with open(self.TRACKING_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)