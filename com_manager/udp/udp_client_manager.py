from .udp_client import UDPClient
import threading
import time

class UDPClientManager:
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()
    
    def log(self, message):
        print(f"{time.strftime('%H:%M:%S')} {message}")
    
    def add_client(self, client_id, host='127.0.0.1', port=9000, listen_port=None, on_message=None):
        with self.lock:
            if client_id in self.clients:
                self.log(f"UDP client '{client_id}' already exists!")
                return False
            client = UDPClient(client_id, host, port, logger=self.log, listen_port=listen_port, on_message=on_message)
            self.clients[client_id] = client
            client.start()
            self.log(f"Added UDP client '{client_id}' for {host}:{port}")
            return True
    
    def set_on_message(self, client_id, callback):
        with self.lock:
            if client_id in self.clients:
                self.clients[client_id].on_message = callback
    
    def remove_client(self, client_id):
        with self.lock:
            if client_id not in self.clients:
                self.log(f"UDP client '{client_id}' not found!")
                return False
            client = self.clients[client_id]
            client.stop()
            del self.clients[client_id]
            self.log(f"Removed UDP client '{client_id}'")
            return True
    
    def send_message(self, client_id, message, addr=None):
        with self.lock:
            if client_id not in self.clients:
                self.log(f"UDP client '{client_id}' not found!")
                return False
            return self.clients[client_id].send_message(message, addr=addr)
    
    def broadcast_message(self, message):
        with self.lock:
            for client in self.clients.values():
                client.send_message(message)
    
    def list_clients(self):
        with self.lock:
            if not self.clients:
                self.log("No UDP clients connected")
                return
            self.log("Connected UDP clients:")
            for client_id, client in self.clients.items():
                self.log(f"  {client_id}: {client.host}:{client.port}")
    
    def stop_all(self):
        with self.lock:
            for client in self.clients.values():
                client.stop()
            self.clients.clear()
            self.log("All UDP clients stopped") 