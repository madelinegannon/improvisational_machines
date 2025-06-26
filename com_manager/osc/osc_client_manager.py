from .osc_client import OSCClient
import threading
import time

class OSCClientManager:
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()
    
    def log(self, message):
        print(f"{time.strftime('%H:%M:%S')} {message}")
    
    def add_client(self, client_id, send_host='127.0.0.1', send_port=8000, listen_port=None, on_message=None):
        with self.lock:
            if client_id in self.clients:
                self.log(f"OSC client '{client_id}' already exists!")
                return False
            client = OSCClient(client_id, send_host, send_port, listen_port=listen_port, logger=self.log, on_message=on_message)
            self.clients[client_id] = client
            client.start()
            self.log(f"Added OSC client '{client_id}' for {send_host}:{send_port}")
            return True
    
    def set_on_message(self, client_id, callback):
        with self.lock:
            if client_id in self.clients:
                self.clients[client_id].on_message = callback
    
    def remove_client(self, client_id):
        with self.lock:
            if client_id not in self.clients:
                self.log(f"OSC client '{client_id}' not found!")
                return False
            client = self.clients[client_id]
            client.stop()
            del self.clients[client_id]
            self.log(f"Removed OSC client '{client_id}'")
            return True
    
    def send_message(self, client_id, address, value=None):
        with self.lock:
            if client_id not in self.clients:
                self.log(f"OSC client '{client_id}' not found!")
                return False
            return self.clients[client_id].send_message(address, value)
    
    def broadcast_message(self, address, value=None):
        with self.lock:
            for client in self.clients.values():
                client.send_message(address, value)
    
    def list_clients(self):
        with self.lock:
            if not self.clients:
                self.log("No OSC clients connected")
                return
            self.log("Connected OSC clients:")
            for client_id, client in self.clients.items():
                self.log(f"  {client_id}: {client.send_host}:{client.send_port} (listen: {client.listen_port})")
    
    def stop_all(self):
        with self.lock:
            for client in self.clients.values():
                client.stop()
            self.clients.clear()
            self.log("All OSC clients stopped") 