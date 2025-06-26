from tcp.tcp_client_manager import TCPClientManager
from udp.udp_client_manager import UDPClientManager
from osc.osc_client_manager import OSCClientManager
from midi.midi_client_manager import MIDIClientManager
from midi.nanokontrol2_reader import KorgNanoKONTROL2Reader
import time

# Helper: Synchronous TCP send/receive (for relay)
def tcp_send_and_receive(tcp_manager, client_id, message, timeout=5):
    client = tcp_manager.clients.get(client_id)
    if not client or not client.connected:
        return None
    try:
        client.send_message(message)
        # Wait for a response (naive: sleep and hope for a response)
        # In production, use a queue or event for real sync
        time.sleep(0.5)
        # No direct way to get the last response in current TCPClient, so just return a dummy
        return f"[Simulated TCP response to '{message}']"
    except Exception as e:
        return f"[TCP error: {e}]"
    
def tcp_send(tcp_manager, client_id, message):
    client = tcp_manager.clients.get(client_id)
    if not client or not client.connected:
        return None
    try:
        client.send_message(message)
    except Exception as e:
        return f"[TCP error: {e}]"

def main():
    print("=== Multi-Client Orchestration Relay Demo ===")
    tcp_manager = TCPClientManager()
    udp_manager = UDPClientManager()
    osc_manager = OSCClientManager()
    midi_manager = MIDIClientManager()

    # Add a TCP client (relay target)
    tcp_manager.add_client("Filemona", host="127.0.0.1", port=1025)
    # tcp_manager.add_client("Mortadela", host="127.0.0.1", port=1026)

    # UDP relay callback
    def udp_on_message(client, message, addr):
        print(f"[Relay] UDP message from {addr}: {message}")
        tcp_response = tcp_send_and_receive(tcp_manager, "RelayTCP", message)
        if tcp_response:
            client.send_message(tcp_response, addr=addr)

    # OSC relay callback
    def osc_on_message(client, address, args):
        print(f"[Relay] OSC message {address} {args}")
        # Handle the incoming OSC message
        msg = ""
        if address == "/pose":
            # Extract x, y, z from args [0:3] and quaternion qw, qx, qy, qz from args[3:]
            x = args[0]
            y = args[1]
            z = args[2]
            qw = args[3]
            qx = args[4]
            qy = args[5]
            qz = args[6]
            print(f"[Relay] Received pose: x={x}, y={y}, z={z}, qw={qw}, qx={qx}, qy={qy}, qz={qz}")
            # Format this for RAPID
            msg = f"pose/[[{x},{y},{z}],[{qw},{qx},{qy},{qz}]];"
        elif address == "/joints":
            # Extract joint angles from args [0:7]
            joint_angles = args[0:7]
            print(f"[Relay] Received j[oint angles: {joint_angles}")
            # Format this for RAPID
            # msg = f"joints/[{','.join(map(str, joint_angles))},[0,0,0,0,0,0]];"
            msg = f"joints/[{joint_angles[0]},{joint_angles[1]},{joint_angles[2]},{joint_angles[3]},{joint_angles[4]},{joint_angles[5]},[0,0,0,0,0,0]];"
        elif address == "/home":
            msg = f"GoHome/;"
        elif address == "/PosA": # Received from TouchOSC
            msg = f"do_draw_circle/;" #Message RAPID is expecting
        elif address == "/filemona/rot": # Received from TouchOSC
            msg = f"PosA;/" #Message RAPID is expecting
        else:
            print(f"[Relay] Unknown OSC message: {address}, {args}")
        if msg != "":
            # Send and receive to all clients
            for client_id in tcp_manager.clients:
                tcp_response = tcp_send(tcp_manager, client_id, msg)
                if tcp_response:
                    client.send_message(address, tcp_response)
            

    # MIDI relay callback
    def midi_on_message(client, parsed, midi_data, timestamp, simple=None):
        msg = ""
        if simple is not None:
            input_name, midi_val = simple
            print(f"[Relay] MIDI message: {input_name},{midi_val}")
        else:
            # split the parsed message by commas into a key and value and remove the spaces
            key, value = parsed.split(",")
            key = key.strip()
            value = value.strip()
            print(f"[Relay] MIDI message: {key},{value}")
            if key == "0": # Slider 1
                # convert value to int if you'd like
                value = int(value)
                msg = f"slider1/{value};"                
            elif key == "1": # Slider 2
                value = int(value)
                msg = f"slider2/{value};"
            elif key == "2": # Slider 3
                value = int(value)
                msg = f"slider3/{value};"
            if msg != "":
                for client_id in tcp_manager.clients:
                    tcp_response = tcp_send(tcp_manager, client_id, msg)

    # Add UDP, OSC, and MIDI clients with relay callbacks
    udp_manager.add_client("RelayUDP", host="127.0.0.1", port=9000, listen_port=9001, on_message=udp_on_message)
    osc_manager.add_client("OSC_GH", send_host="127.0.0.1", send_port=8000, listen_port=8001, on_message=osc_on_message)
    # Auto-select MIDI device if only one is present
    midi_devices = KorgNanoKONTROL2Reader().list_devices()
    print(f"[MIDI] Found {len(midi_devices)} MIDI devices: {midi_devices}") 
    if len(midi_devices) == 1:
        midi_device_index = midi_devices[0][0]
        print(f"[MIDI] Only one device found, using index {midi_device_index}: {midi_devices[0][1]}")
    else:
        midi_device_index = 0
        if len(midi_devices) > 1:
            print(f"[MIDI] Multiple devices found, using default index 0: {midi_devices[0][1]}")
        else:
            print("[MIDI] No MIDI devices found. MIDI client may not work.")
    midi_manager.add_client("RelayMIDI", device_index=midi_device_index, on_message=midi_on_message)

    print("Commands: list | send_tcp <id> <msg> | send_udp <id> <msg> | send_osc <id> <address> <msg> | send_midi <id> <msg> | quit")
    while True:
        cmd = input("main> ").strip().split()
        if not cmd:
            continue
        if cmd[0] == "list":
            tcp_manager.list_clients()
            udp_manager.list_clients()
            osc_manager.list_clients()
            midi_manager.list_clients()
        elif cmd[0] == "send_tcp" and len(cmd) >= 3:
            client_id = cmd[1]
            msg = " ".join(cmd[2:])
            tcp_manager.send_message(client_id, msg)
        elif cmd[0] == "send_udp" and len(cmd) >= 3:
            client_id = cmd[1]
            msg = " ".join(cmd[2:])
            udp_manager.send_message(client_id, msg)
        elif cmd[0] == "send_osc" and len(cmd) >= 4:
            client_id = cmd[1]
            address = cmd[2]
            msg = " ".join(cmd[3:])
            osc_manager.send_message(client_id, address, msg)
        elif cmd[0] == "send_midi" and len(cmd) >= 3:
            client_id = cmd[1]
            msg = " ".join(cmd[2:])
            # For now, just log sending MIDI (sending MIDI out not implemented)
            print(f"[MIDI:{client_id}] (send not implemented): {msg}")
        elif cmd[0] == "quit":
            break
        else:
            print("Unknown command.")

    tcp_manager.stop_all()
    udp_manager.stop_all()
    osc_manager.stop_all()
    midi_manager.stop_all()
    print("Goodbye!")

if __name__ == "__main__":
    main() 