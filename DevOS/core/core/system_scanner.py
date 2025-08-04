import platform
import subprocess
import psutil
import shutil
import logging
from core.error_handler import ErrorHandler

class SystemScanner:
    def __init__(self):
        self.logger = logging.getLogger('SystemScanner')
        self.error_handler = ErrorHandler()
        self.requirements = {
            'min_ram': 8 * 1024**3,  # 8GB
            'min_disk': 50 * 1024**3,  # 50GB
            'min_cores': 4,
            'required_commands': ['git', 'python3', 'docker'],
            'platform_specific': {
                'Windows': ['wsl'],
                'Linux': ['gcc', 'make'],
                'Darwin': ['xcode-select']
            }
        }
        
    def full_scan(self):
        """Perform comprehensive system scan"""
        scan_results = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'cpu': self._get_cpu_info(),
            'memory': self._get_memory_info(),
            'disk': self._get_disk_info(),
            'issues': [],
            'repairable_issues': [],
            'meets_requirements': True,
            'issues_report': ""
        }
        
        # Check system resources
        self._check_resources(scan_results)
        
        # Check required commands
        self._check_commands(scan_results)
        
        # Check platform-specific requirements
        self._check_platform_specific(scan_results)
        
        # Generate issues report
        scan_results['issues_report'] = self._generate_report(scan_results)
        
        return scan_results
        
    def _get_cpu_info(self):
        """Get CPU information"""
        return {
            'cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'usage': psutil.cpu_percent(interval=1),
            'freq': psutil.cpu_freq().current if hasattr(psutil, 'cpu_freq') else 0
        }
        
    def _get_memory_info(self):
        """Get memory information"""
        mem = psutil.virtual_memory()
        return {
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'percent': mem.percent
        }
        
    def _get_disk_info(self):
        """Get disk information"""
        disk = psutil.disk_usage('/')
        return {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'percent': disk.percent
        }
        
    def _check_resources(self, results):
        """Check system resources against requirements"""
        # RAM check
        if results['memory']['total'] < self.requirements['min_ram']:
            issue = {
                'id': 'low_ram',
                'description': f"System has less than {self.requirements['min_ram'] // 1024**3}GB RAM",
                'severity': 'high',
                'repairable': False
            }
            results['issues'].append(issue)
            results['meets_requirements'] = False
            
        # Disk space check
        if results['disk']['free'] < self.requirements['min_disk']:
            issue = {
                'id': 'low_disk',
                'description': f"Low disk space (less than {self.requirements['min_disk'] // 1024**3}GB free)",
                'severity': 'medium',
                'repairable': True,
                'repair_command': 'disk_cleanup'
            }
            results['issues'].append(issue)
            results['repairable_issues'].append(issue)
            results['meets_requirements'] = False
            
        # CPU cores check
        if results['cpu']['cores'] < self.requirements['min_cores']:
            issue = {
                'id': 'insufficient_cores',
                'description': f"System has less than {self.requirements['min_cores']} CPU cores",
                'severity': 'medium',
                'repairable': False
            }
            results['issues'].append(issue)
            results['meets_requirements'] = False
            
    def _check_commands(self, results):
        """Check required commands are available"""
        for cmd in self.requirements['required_commands']:
            if not self._command_exists(cmd):
                issue = {
                    'id': f'missing_{cmd}',
                    'description': f"Required command not found: {cmd}",
                    'severity': 'high',
                    'repairable': True,
                    'repair_command': f'install_{cmd}'
                }
                results['issues'].append(issue)
                results['repairable_issues'].append(issue)
                results['meets_requirements'] = False
                
    def _check_platform_specific(self, results):
        """Check platform-specific requirements"""
        platform_name = results['platform']
        if platform_name in self.requirements['platform_specific']:
            for cmd in self.requirements['platform_specific'][platform_name]:
                if not self._command_exists(cmd):
                    issue = {
                        'id': f'missing_{cmd}',
                        'description': f"Platform-specific command not found: {cmd}",
                        'severity': 'high',
                        'repairable': True,
                        'repair_command': f'install_{cmd}'
                    }
                    results['issues'].append(issue)
                    results['repairable_issues'].append(issue)
                    results['meets_requirements'] = False
                    
    def repair_issue(self, issue_id):
        """Attempt to repair a system issue"""
        repair_commands = {
            'install_git': self._install_git,
            'install_docker': self._install_docker,
            'install_wsl': self._install_wsl,
            'install_gcc': self._install_gcc,
            'install_xcode-select': self._install_xcode_tools,
            'disk_cleanup': self._cleanup_disk
        }
        
        if issue_id in repair_commands:
            return repair_commands[issue_id]()
            
        return {
            'success': False,
            'message': f"No repair available for issue: {issue_id}"
        }
        
    def _install_git(self):
        try:
            if platform.system() == "Windows":
                subprocess.run("winget install -e --id Git.Git", shell=True, check=True)
            elif platform.system() == "Linux":
                subprocess.run("sudo apt install -y git", shell=True, check=True)
            elif platform.system() == "Darwin":
                subprocess.run("brew install git", shell=True, check=True)
            return {'success': True, 'message': "Git installed successfully"}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'message': f"Failed to install Git: {e}"}
    
    # Similar methods for other installations...
    
    def _cleanup_disk(self):
        try:
            # Windows
            if platform.system() == "Windows":
                subprocess.run("cleanmgr /sagerun:1", shell=True, check=True)
            # Linux
            elif platform.system() == "Linux":
                subprocess.run("sudo apt autoremove -y", shell=True, check=True)
                subprocess.run("sudo apt clean", shell=True, check=True)
            # macOS
            elif platform.system() == "Darwin":
                subprocess.run("sudo rm -rf ~/Library/Caches", shell=True, check=True)
                subprocess.run("sudo periodic daily weekly monthly", shell=True, check=True)
                
            return {'success': True, 'message': "Disk cleanup completed"}
        except subprocess.CalledProcessError as e:
            return {'success': False, 'message': f"Disk cleanup failed: {e}"}
            
    def _command_exists(self, command):
        try:
            subprocess.check_output(f"command -v {command}", shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def _generate_report(self, results):
        """Generate human-readable issues report"""
        if not results['issues']:
            return "System meets all requirements"
            
        report = "System Issues Report:\n"
        report += "=" * 40 + "\n"
        
        for issue in results['issues']:
            status = "Repairable" if issue.get('repairable', False) else "Not Repairable"
            report += f"- [{issue['severity'].upper()}] {issue['description']} ({status})\n"
            
        report += "\nRecommended actions:\n"
        for issue in results['repairable_issues']:
            report += f"- Repair: {issue['description']} (use repair command: {issue['id']})\n"
            
        return report