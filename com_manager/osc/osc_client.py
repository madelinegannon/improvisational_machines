from pythonosc import udp_client, dispatcher, osc_server
import threading
import time

class OSCClient:
    def __init__(self, client_id: str, send_host: str, send_port: int, listen_port: int = None, logger=None, on_message=None):
        self.client_id = client_id
        self.send_host = send_host
        self.send_port = send_port
        self.listen_port = listen_port
        self.logger = logger or print
        self.osc_client = udp_client.SimpleUDPClient(self.send_host, self.send_port)
        self.server = None
        self.server_thread = None
        self.running = False
        self.on_message = on_message
    
    def start(self):
        if self.listen_port:
            disp = dispatcher.Dispatcher()
            disp.set_default_handler(self._osc_handler)
            self.server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", self.listen_port), disp)
            self.running = True
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.logger(f"[OSC:{self.client_id}] Listening for OSC on port {self.listen_port}")
        else:
            self.logger(f"[OSC:{self.client_id}] No listen port specified; will only send.")
    
    def _run_server(self):
        while self.running:
            try:
                self.server.handle_request()
            except Exception as e:
                self.logger(f"[OSC:{self.client_id}] Server error: {e}")
                break
    
    def _osc_handler(self, address, *args):
        self.logger(f"[OSC:{self.client_id}] Received: {address} {args}")
        if self.on_message:
            self.on_message(self, address, args)
    
    def send_message(self, address: str = '/test', value=None):
        try:
            if value is not None:
                self.osc_client.send_message(address, value)
                self.logger(f"[OSC:{self.client_id}] Sent: {address} {value}")
            else:
                self.osc_client.send_message(address, [])
                self.logger(f"[OSC:{self.client_id}] Sent: {address} []")
            return True
        except Exception as e:
            self.logger(f"[OSC:{self.client_id}] Failed to send message: {e}")
            return False
    
    def stop(self):
        self.running = False
        if self.server:
            self.server.server_close()
            self.server = None
        self.logger(f"[OSC:{self.client_id}] Stopped.")

# Note: Requires python-osc. Install with: pip install python-osc 