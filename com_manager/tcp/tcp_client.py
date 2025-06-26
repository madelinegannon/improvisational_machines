import socket
import threading
import time

class TCPClient:
    def __init__(self, client_id: str, host: str, port: int, logger=None):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.logger = logger or print
        self.connected = False
        self.client_socket = None
        self.should_reconnect = True
        self.listen_thread = None
        self.connect_thread = None
    
    def connect_to_server(self):
        while self.should_reconnect:
            try:
                if self.client_socket:
                    self.client_socket.close()
                
                # Create a new TCP socket
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # Connect to the server
                self.logger(f"[{self.client_id}] Connecting to {self.host}:{self.port}...")
                self.client_socket.connect((self.host, self.port))
                self.logger(f"[{self.client_id}] Connected successfully!")
                self.connected = True
                
                # Send initial greeting
                greeting = f"Hello from TCP client {self.client_id}!"
                self.client_socket.send(greeting.encode('utf-8'))
                self.logger(f"[{self.client_id}] Sent: {greeting}")
                
                return True
                
            except ConnectionRefusedError:
                self.logger(f"[{self.client_id}] Connection refused. Retrying in 5 seconds...")
                self.connected = False
                time.sleep(5)
            except Exception as e:
                self.logger(f"[{self.client_id}] Connection error: {e}. Retrying in 5 seconds...")
                self.connected = False
                time.sleep(5)
        
        return False
    
    def listen_for_messages(self):
        while self.should_reconnect:
            if not self.connected:
                time.sleep(0.1)
                continue
                
            try:
                response = self.client_socket.recv(1024)
                if not response:
                    self.logger(f"[{self.client_id}] Server closed the connection. Attempting to reconnect...")
                    self.connected = False
                    # Start reconnection in a separate thread
                    self.connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
                    self.connect_thread.start()
                    continue
                self.logger(f"[{self.client_id}] Received: {response.decode('utf-8')}")
            except socket.error:
                self.logger(f"[{self.client_id}] Connection lost. Attempting to reconnect...")
                self.connected = False
                # Start reconnection in a separate thread
                self.connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
                self.connect_thread.start()
    
    def start(self):
        # Initial connection
        self.connect_thread = threading.Thread(target=self.connect_to_server, daemon=True)
        self.connect_thread.start()
        
        # Wait a moment for initial connection attempt
        time.sleep(0.5)
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_for_messages, daemon=True)
        self.listen_thread.start()
    
    def send_message(self, message: str) -> bool:
        if self.connected and self.client_socket:
            try:
                self.client_socket.send(message.encode('utf-8'))
                self.logger(f"[{self.client_id}] Sent: {message}")
                return True
            except socket.error as e:
                self.logger(f"[{self.client_id}] Failed to send message: {e}")
                return False
        else:
            self.logger(f"[{self.client_id}] Not connected. Message will be sent after reconnection.")
            return False
    
    def stop(self):
        self.should_reconnect = False
        if self.client_socket:
            self.client_socket.close()
        self.logger(f"[{self.client_id}] Connection closed") 