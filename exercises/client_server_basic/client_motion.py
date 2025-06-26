import socket
import sys
import argparse
import threading
import time

def tcp_client(host='127.0.0.1', port=1025):
    connected = False
    client_socket = None
    should_reconnect = True
    
    def connect_to_server():
        nonlocal connected, client_socket
        while should_reconnect:
            try:
                if client_socket:
                    client_socket.close()
                
                # Create a new TCP socket
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # Connect to the server
                print(f"Connecting to {host}:{port}...")
                client_socket.connect((host, port))
                print("Connected successfully!")
                connected = True
                
                # Send initial greeting
                greeting = "Hello from TCP client!"
                client_socket.send(greeting.encode('utf-8'))
                print(f"Sent: {greeting}")
                
                return True
                
            except ConnectionRefusedError:
                print(f"Connection refused. Retrying in 5 seconds...")
                connected = False
                time.sleep(5)
            except Exception as e:
                print(f"Connection error: {e}. Retrying in 5 seconds...")
                connected = False
                time.sleep(5)
        
        return False
    
    def listen_for_messages():
        nonlocal connected
        while should_reconnect:
            if not connected:
                time.sleep(0.1)
                continue
                
            try:
                response = client_socket.recv(1024)
                if not response:
                    print("Server closed the connection. Attempting to reconnect...")
                    connected = False
                    # Start reconnection in a separate thread
                    threading.Thread(target=connect_to_server, daemon=True).start()
                    continue
                print(f"Received: {response.decode('utf-8')}")
            except socket.error:
                print("Connection lost. Attempting to reconnect...")
                connected = False
                # Start reconnection in a separate thread
                threading.Thread(target=connect_to_server, daemon=True).start()
    
    # Initial connection
    if not connect_to_server():
        print("Failed to establish initial connection")
        return
    
    # Start listening thread
    listen_thread = threading.Thread(target=listen_for_messages, daemon=True)
    listen_thread.start()
        
    # Keep listening for user input and send messages
    print("Type messages to send (type 'quit' to exit):")
    try:
        while should_reconnect:
            user_input = input("> ")
            if user_input.lower() == 'quit':
                should_reconnect = False
                break
            
            if connected:
                try:
                    client_socket.send(user_input.encode('utf-8'))
                    print(f"Sent: {user_input}")
                except socket.error as e:
                    print(f"Failed to send message: {e}")
                    print("Connection lost. Message will be sent after reconnection.")
            else:
                print("Not connected. Message will be sent after reconnection.")
    except KeyboardInterrupt:
        should_reconnect = False
        print("\nExiting...")
    
    # Cleanup
    if client_socket:
        client_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TCP Client")
    parser.add_argument('--host', default='127.0.0.1', help='Server host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=1025, help='Server port (default: 1025)')
    
    args = parser.parse_args()
    tcp_client(args.host, args.port)