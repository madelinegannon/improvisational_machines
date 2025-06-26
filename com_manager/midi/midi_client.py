import threading
import time
from .nanokontrol2_reader import KorgNanoKONTROL2Reader

class MIDIClient:
    def __init__(self, client_id, device_index=0, logger=None, on_message=None):
        self.client_id = client_id
        self.device_index = device_index
        self.logger = logger or print
        self.on_message = on_message
        self.running = False
        self.listen_thread = None
        self.reader = None

    def start(self):
        if KorgNanoKONTROL2Reader is None:
            self.logger(f"[MIDI:{self.client_id}] nanokontrol2_reader not found!")
            return
        self.reader = KorgNanoKONTROL2Reader()
        if not self.reader.connect(self.device_index):
            self.logger(f"[MIDI:{self.client_id}] Failed to connect to device {self.device_index}")
            return
        self.running = True
        self.listen_thread = threading.Thread(target=self.listen, daemon=True)
        self.listen_thread.start()
        self.logger(f"[MIDI:{self.client_id}] Started on device {self.device_index}")

    def listen(self):
        try:
            last_values = {}  # (status, data1) -> data2
            while self.running:
                if self.reader.messages:
                    while self.reader.messages:
                        midi_data, timestamp = self.reader.messages.pop(0)
                        # Extract bytes
                        byte1 = midi_data & 0xFF
                        byte2 = (midi_data >> 8) & 0xFF
                        byte3 = (midi_data >> 16) & 0xFF
                        status = byte1
                        data1 = byte2
                        data2 = byte3
                        key = (status, data1)
                        prev_val = last_values.get(key)
                        if prev_val == data2:
                            continue  # Skip if value did not change
                        last_values[key] = data2
                        parsed = self.reader.parse_midi_message(midi_data, timestamp)
                        simple = None  # No simple parser in generic version
                        if parsed:
                            # self.logger(f"[MIDI:{self.client_id}] {parsed}")
                            pass
                        if self.on_message:
                            self.on_message(self, parsed, midi_data, timestamp, simple)
                time.sleep(0.001)
        except Exception as e:
            self.logger(f"[MIDI:{self.client_id}] Listen error: {e}")

    def stop(self):
        self.running = False
        if self.reader:
            self.reader.disconnect()
        self.logger(f"[MIDI:{self.client_id}] Stopped.")

# Note: Requires nanokontrol2_reader.py in the same directory and python-osc for full integration. 