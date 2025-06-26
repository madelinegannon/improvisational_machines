from .midi_client import MIDIClient
import threading
import time

class MIDIClientManager:
    def __init__(self):
        self.clients = {}
        self.lock = threading.Lock()

    def log(self, message):
        print(f"{time.strftime('%H:%M:%S')} {message}")

    def add_client(self, client_id, device_index=0, on_message=None):
        with self.lock:
            if client_id in self.clients:
                self.log(f"MIDI client '{client_id}' already exists!")
                return False
            client = MIDIClient(client_id, device_index=device_index, logger=self.log, on_message=on_message)
            self.clients[client_id] = client
            client.start()
            self.log(f"Added MIDI client '{client_id}' on device {device_index}")
            return True

    def set_on_message(self, client_id, callback):
        with self.lock:
            if client_id in self.clients:
                self.clients[client_id].on_message = callback

    def remove_client(self, client_id):
        with self.lock:
            if client_id not in self.clients:
                self.log(f"MIDI client '{client_id}' not found!")
                return False
            client = self.clients[client_id]
            client.stop()
            del self.clients[client_id]
            self.log(f"Removed MIDI client '{client_id}'")
            return True

    def list_clients(self):
        with self.lock:
            if not self.clients:
                self.log("No MIDI clients connected")
                return
            self.log("Connected MIDI clients:")
            for client_id, client in self.clients.items():
                self.log(f"  {client_id}: device {client.device_index}")

    def stop_all(self):
        with self.lock:
            for client in self.clients.values():
                client.stop()
            self.clients.clear()
            self.log("All MIDI clients stopped") 