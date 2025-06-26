import socket
import sys
import argparse
import threading
import time
from typing import Dict, Optional
from .tcp_client import TCPClient

class TCPClientManager:
    def __init__(self):
        self.clients: Dict[str, TCPClient] = {}
        self.lock = threading.Lock()
    
    def log(self, message: str):
        print(f"{time.strftime('%H:%M:%S')} {message}")
    
    def add_client(self, client_id: str, host: str = '127.0.0.1', port: int = 1025) -> bool:
        with self.lock:
            if client_id in self.clients:
                self.log(f"Client '{client_id}' already exists!")
                return False
            
            client = TCPClient(client_id, host, port, logger=self.log)
            self.clients[client_id] = client
            client.start()
            self.log(f"Added client '{client_id}' for {host}:{port}")
            return True
    
    def remove_client(self, client_id: str) -> bool:
        with self.lock:
            if client_id not in self.clients:
                self.log(f"Client '{client_id}' not found!")
                return False
            
            client = self.clients[client_id]
            client.stop()
            del self.clients[client_id]
            self.log(f"Removed client '{client_id}'")
            return True
    
    def send_message(self, client_id: str, message: str) -> bool:
        with self.lock:
            if client_id not in self.clients:
                self.log(f"Client '{client_id}' not found!")
                return False
            
            return self.clients[client_id].send_message(message)
    
    def broadcast_message(self, message: str):
        with self.lock:
            for client_id, client in self.clients.items():
                client.send_message(message)
    
    def list_clients(self):
        with self.lock:
            if not self.clients:
                self.log("No clients connected")
                return
            
            self.log("Connected clients:")
            for client_id, client in self.clients.items():
                status = "Connected" if client.connected else "Disconnected"
                self.log(f"  {client_id}: {client.host}:{client.port} - {status}")
    
    def stop_all(self):
        with self.lock:
            for client in self.clients.values():
                client.stop()
            self.clients.clear()
            self.log("All clients stopped")


def main():
    parser = argparse.ArgumentParser(description="TCP Client Manager")
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Start in interactive mode')
    
    args = parser.parse_args()
    
    manager = TCPClientManager()
    
    if args.interactive:
        print("TCP Client Manager - Interactive Mode")
        print("Commands:")
        print("  add <client_id> [host] [port] - Add a new client")
        print("  remove <client_id>            - Remove a client")
        print("  send <client_id> <message>    - Send message to specific client")
        print("  broadcast <message>           - Send message to all clients")
        print("  list                          - List all clients")
        print("  quit                          - Exit")
        print()
        
        try:
            while True:
                try:
                    cmd = input("manager> ").strip().split()
                    if not cmd:
                        continue
                    
                    if cmd[0] == "add":
                        if len(cmd) < 2:
                            print("Usage: add <client_id> [host] [port]")
                            continue
                        client_id = cmd[1]
                        host = cmd[2] if len(cmd) > 2 else '127.0.0.1'
                        port = int(cmd[3]) if len(cmd) > 3 else 1025
                        manager.add_client(client_id, host, port)
                    
                    elif cmd[0] == "remove":
                        if len(cmd) < 2:
                            print("Usage: remove <client_id>")
                            continue
                        manager.remove_client(cmd[1])
                    
                    elif cmd[0] == "send":
                        if len(cmd) < 3:
                            print("Usage: send <client_id> <message>")
                            continue
                        client_id = cmd[1]
                        message = " ".join(cmd[2:])
                        manager.send_message(client_id, message)
                    
                    elif cmd[0] == "broadcast":
                        if len(cmd) < 2:
                            print("Usage: broadcast <message>")
                            continue
                        message = " ".join(cmd[1:])
                        manager.broadcast_message(message)
                    
                    elif cmd[0] == "list":
                        manager.list_clients()
                    
                    elif cmd[0] == "quit":
                        break
                    
                    else:
                        print("Unknown command. Type 'quit' to exit.")
                
                except ValueError:
                    print("Invalid port number")
                except Exception as e:
                    print(f"Error: {e}")
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        manager.stop_all()
    
    else:
        # Example usage without interactive mode - with keyboard input
        print("Starting TCP Client Manager with example clients...")
        
        # Add some example clients
        manager.add_client("Filemona", "127.0.0.1", 1025)
        manager.add_client("Mortadela", "127.0.0.1", 1026)
        
        time.sleep(2)  # Let connections establish
        
        # List clients
        manager.list_clients()
        
        print("\nType messages to broadcast to all clients (type 'quit' to exit):")
        print("Available commands:")
        print("  send <client_id> <message> - Send to specific client")
        print("  list                       - Show client status")
        print("  quit                       - Exit")
        print("  <message>                  - Broadcast to all clients")
        print()
        
        try:
            while True:
                user_input = input("broadcast> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'quit':
                    break
                
                # Check for commands
                parts = user_input.split()
                if parts[0] == "send" and len(parts) >= 3:
                    client_id = parts[1]
                    message = " ".join(parts[2:])
                    manager.send_message(client_id, message)
                elif parts[0] == "list":
                    manager.list_clients()
                else:
                    # Broadcast the message
                    if manager.clients:
                        manager.broadcast_message(user_input)
                    else:
                        print("No clients connected!")
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        manager.stop_all()


if __name__ == "__main__":
    main()