import socket
import threading
import time

class UDPClient:
    def __init__(self, client_id: str, host: str, port: int, logger=None, listen_port: int = None, on_message=None):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.logger = logger or print
        self.listen_port = listen_port or 0  # 0 means OS assigns a port
        self.sock = None
        self.listening = False
        self.listen_thread = None
        self.on_message = on_message
    
    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.listen_port))
        self.listening = True
        self.listen_thread = threading.Thread(target=self.listen_for_responses, daemon=True)
        self.listen_thread.start()
        self.logger(f"[UDP:{self.client_id}] Started, listening on port {self.sock.getsockname()[1]}")
    
    def send_message(self, message: str, addr=None) -> bool:
        if not self.sock:
            self.logger(f"[UDP:{self.client_id}] Socket not started.")
            return False
        try:
            target = addr if addr else (self.host, self.port)
            self.sock.sendto(message.encode('utf-8'), target)
            self.logger(f"[UDP:{self.client_id}] Sent: {message}")
            return True
        except Exception as e:
            self.logger(f"[UDP:{self.client_id}] Failed to send message: {e}")
            return False
    
    def listen_for_responses(self):
        while self.listening:
            try:
                self.sock.settimeout(1.0)
                data, addr = self.sock.recvfrom(4096)
                msg = data.decode('utf-8')
                self.logger(f"[UDP:{self.client_id}] Received from {addr}: {msg}")
                if self.on_message:
                    self.on_message(self, msg, addr)
            except socket.timeout:
                continue
            except Exception as e:
                self.logger(f"[UDP:{self.client_id}] Listen error: {e}")
                break
    
    def stop(self):
        self.listening = False
        if self.sock:
            self.sock.close()
            self.sock = None
        self.logger(f"[UDP:{self.client_id}] Stopped.") 