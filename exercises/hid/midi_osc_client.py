import socket
import sys
import argparse
import threading
import time
import json
from datetime import datetime
import traceback

# OSC imports
try:
    from pythonosc import dispatcher
    from pythonosc import server
    from pythonosc.server import BlockingOSCUDPServer
    OSC_AVAILABLE = True
except ImportError:
    print("⚠️  python-osc not installed. OSC functionality will be disabled.")
    print("   Install with: pip install python-osc")
    OSC_AVAILABLE = False

# Import your MIDI reader (assuming it's in the same directory)
try:
    from nanokontrol2_reader import KorgNanoKONTROL2Reader
    MIDI_AVAILABLE = True
except ImportError:
    print("⚠️  nanokontrol2_reader.py not found. MIDI functionality will be disabled.")
    MIDI_AVAILABLE = False

class MIDIOSCBridge:
    def __init__(self, server_host='127.0.0.1', server_port=1025, osc_port=5005):
        self.server_host = server_host
        self.server_port = server_port
        self.osc_port = osc_port
        
        # Network connection
        self.client_socket = None
        self.connected = False
        self.connection_lock = threading.Lock()
        
        # MIDI setup
        self.midi_reader = None
        self.midi_enabled = MIDI_AVAILABLE
        
        # OSC setup
        self.osc_server = None
        self.osc_enabled = OSC_AVAILABLE
        self.osc_thread = None
        
        # Message queue and threading
        self.message_queue = []
        self.queue_lock = threading.Lock()
        self.running = True
        
        print("🌉 MIDI/OSC to Server Bridge")
        print("=" * 50)
        
    def connect_to_server(self):
        """Connect to the TCP server"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"🔌 Connecting to server {self.server_host}:{self.server_port}...")
            self.client_socket.connect((self.server_host, self.server_port))
            
            with self.connection_lock:
                self.connected = True
            
            print("✅ Connected to server successfully!")
            
            # Start listening for server responses
            server_listener = threading.Thread(target=self.listen_to_server, daemon=True)
            server_listener.start()
            
            return True
            
        except ConnectionRefusedError:
            print(f"❌ Connection refused. Make sure server is running on {self.server_host}:{self.server_port}")
            return False
        except Exception as e:
            print(f"❌ Failed to connect to server: {e}")
            return False
    
    def listen_to_server(self):
        """Listen for messages from the server"""
        try:
            while self.running and self.connected:
                try:
                    response = self.client_socket.recv(1024)
                    if not response:
                        print("🔌 Server closed the connection")
                        with self.connection_lock:
                            self.connected = False
                        break
                    
                    message = response.decode('utf-8')
                    print(f"📨 Server: {message}")
                    
                except socket.timeout:
                    continue
                except socket.error:
                    break
        except Exception as e:
            print(f"❌ Error listening to server: {e}")
    
    def send_to_server(self, message_type, data):
        """Send a message to the server"""
        if not self.connected:
            return False
        
        try:
            # Create a structured message
            message = {
                "timestamp": datetime.now().isoformat(),
                "type": message_type,
                "data": data
            }
            
            message_str = json.dumps(message)
            
            with self.connection_lock:
                if self.connected and self.client_socket:
                    self.client_socket.send(message_str.encode('utf-8'))
                    print(f"📤 Sent {message_type}: {data}")
                    return True
                    
        except socket.error as e:
            print(f"❌ Failed to send message: {e}")
            with self.connection_lock:
                self.connected = False
            return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def setup_midi(self, device_index=None):
        """Setup MIDI input"""
        if not self.midi_enabled:
            print("⚠️  MIDI functionality not available")
            return False
        
        try:
            self.midi_reader = KorgNanoKONTROL2Reader()
            
            # List available devices
            print("\n🎛️  Scanning for MIDI devices...")
            devices = self.midi_reader.list_devices()
            
            if not devices:
                print("❌ No MIDI devices found")
                return False
            
            # Auto-detect or use specified device
            if device_index is None:
                # Try to auto-detect nanoKONTROL2
                for i, (dev_id, dev_name) in enumerate(devices):
                    if "nanokontrol" in dev_name.lower() or "nano kontrol" in dev_name.lower():
                        device_index = dev_id
                        print(f"🎯 Auto-detected nanoKONTROL2 at device {device_index}")
                        break
                
                if device_index is None:
                    device_index = 0
                    print(f"⚠️  No nanoKONTROL2 detected, using device {device_index}")
            
            # Connect to MIDI device
            if self.midi_reader.connect(device_index):
                print("✅ MIDI device connected successfully!")
                
                # Start MIDI listening in a separate thread
                midi_thread = threading.Thread(target=self.start_midi_listening, daemon=True)
                midi_thread.start()
                
                return True
            else:
                print("❌ Failed to connect to MIDI device")
                return False
                
        except Exception as e:
            print(f"❌ Error setting up MIDI: {e}")
            return False
    
    def midi_callback(self, midi_data, parsed_message, timestamp):
        """Callback for MIDI messages"""
        if parsed_message and self.connected:
            # Send MIDI data to server
            midi_info = {
                "control": parsed_message,
                "raw_data": midi_data,
                "midi_timestamp": timestamp
            }
            self.send_to_server("MIDI", midi_info)
    
    def start_midi_listening(self):
        """Start listening for MIDI messages"""
        try:
            if self.midi_reader:
                print("🎵 MIDI listening started...")
                self.midi_reader.start_listening(callback=self.midi_callback)
        except Exception as e:
            print(f"❌ Error in MIDI listening: {e}")
    
    def setup_osc(self):
        """Setup OSC input"""
        if not self.osc_enabled:
            print("⚠️  OSC functionality not available")
            return False
        
        try:
            # Create OSC dispatcher
            disp = dispatcher.Dispatcher()
            disp.set_default_handler(self.osc_handler)
            
            # Create OSC server
            self.osc_server = BlockingOSCUDPServer(("127.0.0.1", self.osc_port), disp)
            
            print(f"🎵 OSC server listening on port {self.osc_port}")
            
            # Start OSC server in a separate thread
            self.osc_thread = threading.Thread(target=self.start_osc_server, daemon=True)
            self.osc_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Error setting up OSC: {e}")
            return False
    
    def osc_handler(self, address, *args):
        """Handle incoming OSC messages"""
        try:
            osc_data = {
                "address": address,
                "args": list(args) if args else []
            }
            
            print(f"🎵 OSC: {address} {args}")
            
            if self.connected:
                self.send_to_server("OSC", osc_data)
                
        except Exception as e:
            print(f"❌ Error handling OSC message: {e}")
    
    def start_osc_server(self):
        """Start the OSC server"""
        try:
            if self.osc_server:
                print("🎵 OSC listening started...")
                self.osc_server.serve_forever()
        except Exception as e:
            print(f"❌ Error in OSC server: {e}")
    
    def run(self, midi_device=None):
        """Main run loop"""
        try:
            # Connect to server
            if not self.connect_to_server():
                return
            
            # Setup MIDI if available
            if self.midi_enabled:
                self.setup_midi(midi_device)
            
            # Setup OSC if available
            if self.osc_enabled:
                self.setup_osc()
            
            if not self.midi_enabled and not self.osc_enabled:
                print("❌ Neither MIDI nor OSC functionality is available!")
                return
            
            print("\n" + "=" * 60)
            print("🚀 Bridge is running!")
            if self.midi_enabled:
                print("   • MIDI: Move controls on your nanoKONTROL2")
            if self.osc_enabled:
                print(f"   • OSC: Send messages to 127.0.0.1:{self.osc_port}")
            print("   • Press Ctrl+C to stop")
            print("=" * 60)
            
            # Keep the main thread alive
            try:
                while self.running and self.connected:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping bridge...")
                self.stop()
                
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            traceback.print_exc()
    
    def stop(self):
        """Stop the bridge"""
        self.running = False
        
        # Stop MIDI
        if self.midi_reader:
            self.midi_reader.stop_listening()
            self.midi_reader.disconnect()
        
        # Stop OSC
        if self.osc_server:
            self.osc_server.shutdown()
        
        # Close socket
        with self.connection_lock:
            if self.client_socket:
                self.client_socket.close()
            self.connected = False
        
        print("✅ Bridge stopped")

def main():
    parser = argparse.ArgumentParser(description="MIDI/OSC to Server Bridge")
    parser.add_argument('--server-host', default='127.0.0.1', 
                       help='Server host (default: 127.0.0.1)')
    parser.add_argument('--server-port', type=int, default=1025, 
                       help='Server port (default: 1025)')
    parser.add_argument('--osc-port', type=int, default=5005, 
                       help='OSC listening port (default: 5005)')
    parser.add_argument('--midi-device', type=int, default=None,
                       help='MIDI device index (auto-detect if not specified)')
    
    args = parser.parse_args()
    
    # Check platform for MIDI
    if MIDI_AVAILABLE and sys.platform != "win32":
        print("⚠️  MIDI functionality currently only works on Windows!")
    
    bridge = MIDIOSCBridge(
        server_host=args.server_host,
        server_port=args.server_port,
        osc_port=args.osc_port
    )
    
    try:
        bridge.run(midi_device=args.midi_device)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    finally:
        bridge.stop()

if __name__ == "__main__":
    main()