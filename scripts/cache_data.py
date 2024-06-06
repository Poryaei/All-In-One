import os
import json

class SimpleCache:
    
    def __init__(self, key):
        
        self.key  = key

        if not os.path.exists('cache'):
            os.mkdir('cache')
        
        self.load()
    
    def load(self):
        file_path = f'cache/{self.key}.json'
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    self.data = json.load(f)
            except json.JSONDecodeError:
                self.data = {}
        else:
            self.data = {}

    def save(self):
        file_path = f'cache/{self.key}.json'
        with open(file_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get(self, key):
        return self.data.get(key)
    
    def exists(self, key):
        return key in self.data
        
    def clear(self):
        self.data = {}
        self.save()
