# Communications Manager
### Improvisational Machines Workshop: Live Coding with Industrial Robots
#### Barcelona, June 2025 | _[Madeline Gannon](https://atonaton.com)_

This project connects TCP, UDP, OSC, and MIDI clients to ABB robots using the RAPID Server in `/rapid`.

## Requirements
- Python 3.8+
- [python-osc](https://pypi.org/project/python-osc/) (`pip install python-osc`)
- Windows (for MIDI support via `ctypes`)

## Usage
1. **Install dependencies:**
   ```sh
   pip install python-osc
   ```
2. **Run the orchestration CLI:**
   ```sh
   cd communication/com_manager
   python main.py
   ```
3. **Interact via CLI:**
   - List clients: `list`
   - Send messages: `send_tcp <id> <msg>`, `send_udp <id> <msg>`, `send_osc <id> <address> <msg>`
   - Relay logic: UDP/OSC/MIDI messages are automatically relayed to all TCP clients, and responses are sent back.
   - Quit: `quit`

## Example: OSC to TCP Relay
- Send an OSC message (e.g., `/pose` or `/joints`) to the listening OSC port (default: 8001).
- The message is formatted for RAPID and relayed to all TCP clients (e.g., ABB robot controllers).
- The TCP response is sent back to the OSC sender.

## MIDI Integration
- The MIDI client supports Korg nanoKONTROL2 controllers on Windows.
- MIDI messages can be relayed to TCP clients for robot control or logging.

## Extending
- Add new protocols by creating a new subdirectory and following the client/manager pattern.
- Update `main.py` to register new clients and relay logic as needed.

## License
MIT License 