import os
import json
import logging
import sqlite3
from datetime import datetime
import hashlib
import requests

class KnowledgeBase:
    def __init__(self):
        self.logger = logging.getLogger('KnowledgeBase')
        self.db_path = "knowledge_base.db"
        self.resources_dir = "resources/knowledge"
        self.remote_index = "https://raw.githubusercontent.com/devos-toolkit/knowledge/main/index.json"
        
    def load(self):
        """Load knowledge base into database"""
        try:
            os.makedirs(self.resources_dir, exist_ok=True)
            
            # Initialize database
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            
            # Create tables
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS resources (
                    id TEXT PRIMARY KEY,
                    category TEXT,
                    title TEXT,
                    url TEXT,
                    content TEXT,
                    tags TEXT,
                    last_updated REAL
                )
            ''')
            
            # Load local resources
            self._load_local_resources()
            
            self.logger.info("Knowledge base loaded")
            return True
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {str(e)}")
            return False
            
    def _load_local_resources(self):
        """Load local knowledge resources into database"""
        categories = os.listdir(self.resources_dir)
        for category in categories:
            cat_path = os.path.join(self.resources_dir, category)
            if os.path.isdir(cat_path):
                for file in os.listdir(cat_path):
                    if file.endswith('.json'):
                        file_path = os.path.join(cat_path, file)
                        with open(file_path, 'r') as f:
                            try:
                                resource = json.load(f)
                                self._add_resource(resource, category)
                            except json.JSONDecodeError:
                                self.logger.warning(f"Invalid JSON in {file_path}")
    
    def _add_resource(self, resource, category):
        """Add resource to database"""
        resource_id = hashlib.md5(
            f"{category}-{resource['title']}".encode()
        ).hexdigest()
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO resources 
            (id, category, title, url, content, tags, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            resource_id,
            category,
            resource.get('title', ''),
            resource.get('url', ''),
            resource.get('content', ''),
            json.dumps(resource.get('tags', [])),
            datetime.now().timestamp()
        ))
        self.conn.commit()
    
    def search(self, query, limit=20):
        """Search knowledge base"""
        try:
            # Simple SQLite full-text search
            self.cursor.execute('''
                SELECT * FROM resources 
                WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'id': row[0],
                    'category': row[1],
                    'title': row[2],
                    'url': row[3],
                    'content': row[4],
                    'tags': json.loads(row[5]),
                    'last_updated': row[6]
                })
            return results
        except Exception as e:
            self.logger.error(f"Search failed: {str(e)}")
            return []
    
    def get_resource(self, category, key):
        """Get specific resource by category and key"""
        try:
            self.cursor.execute('''
                SELECT * FROM resources 
                WHERE category = ? AND (title = ? OR id = ?)
            ''', (category, key, key))
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'category': row[1],
                    'title': row[2],
                    'url': row[3],
                    'content': row[4],
                    'tags': json.loads(row[5]),
                    'last_updated': row[6]
                }
            return None
        except Exception as e:
            self.logger.error(f"Resource retrieval failed: {str(e)}")
            return None
    
    def periodic_update(self, interval=86400):  # 24 hours
        """Periodically update knowledge base from remote"""
        while True:
            try:
                self._update_from_remote()
                time.sleep(interval)
            except Exception as e:
                self.logger.error(f"Knowledge base update failed: {str(e)}")
                time.sleep(3600)  # Retry in 1 hour
    
    def _update_from_remote(self):
        """Update knowledge base from remote index"""
        response = requests.get(self.remote_index)
        if response.status_code == 200:
            index = response.json()
            for resource in index['resources']:
                self._download_resource(resource)
    
    def _download_resource(self, resource):
        """Download and store a remote resource"""
        try:
            response = requests.get(resource['url'])
            if response.status_code == 200:
                # Save to local file
                os.makedirs(os.path.join(self.resources_dir, resource['category']), exist_ok=True)
                file_path = os.path.join(
                    self.resources_dir, 
                    resource['category'],
                    f"{resource['id']}.json"
                )
                
                with open(file_path, 'w') as f:
                    json.dump({
                        'title': resource['title'],
                        'url': resource['url'],
                        'content': response.text,
                        'tags': resource.get('tags', [])
                    }, f)
                
                # Add to database
                self._add_resource({
                    'title': resource['title'],
                    'url': resource['url'],
                    'content': response.text,
                    'tags': resource.get('tags', [])
                }, resource['category'])
                
                self.logger.info(f"Updated resource: {resource['title']}")
        except Exception as e:
            self.logger.error(f"Failed to download resource: {str(e)}")