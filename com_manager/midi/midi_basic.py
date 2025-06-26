import ctypes
import ctypes.wintypes
import time
from threading import Thread, Event
import sys

# Windows MIDI API constants
MMSYSERR_NOERROR = 0
CALLBACK_FUNCTION = 0x30000
MIM_OPEN = 0x3C1
MIM_CLOSE = 0x3C2
MIM_DATA = 0x3C3
MIM_LONGDATA = 0x3C4
MIM_ERROR = 0x3C5
MIM_LONGERROR = 0x3C6

# Load Windows multimedia library
winmm = ctypes.windll.winmm

# Define callback function type
MIDI_CALLBACK = ctypes.WINFUNCTYPE(None, ctypes.wintypes.HANDLE, ctypes.wintypes.UINT, 
                                  ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD)

class MIDIDeviceReader:
    def __init__(self):
        self.device_id = None
        self.handle = None
        self.is_listening = False
        self.callback_installed = False
        self.messages = []
        self.message_lock = Event()
        
    def list_devices(self):
        """List all available MIDI input devices"""
        num_devices = winmm.midiInGetNumDevs()
        print(f"Found {num_devices} MIDI input devices:")
        
        devices = []
        for i in range(num_devices):
            # Structure for device info
            class MIDIINCAPS(ctypes.Structure):
                _fields_ = [
                    ("wMid", ctypes.wintypes.WORD),
                    ("wPid", ctypes.wintypes.WORD),
                    ("vDriverVersion", ctypes.wintypes.DWORD),
                    ("szPname", ctypes.c_char * 32),
                    ("dwSupport", ctypes.wintypes.DWORD)
                ]
            
            caps = MIDIINCAPS()
            result = winmm.midiInGetDevCapsA(i, ctypes.byref(caps), ctypes.sizeof(caps))
            
            if result == MMSYSERR_NOERROR:
                device_name = caps.szPname.decode('ascii', errors='ignore').rstrip('\x00')
                print(f"  {i}: {device_name}")
                devices.append((i, device_name))
            else:
                print(f"  {i}: Error getting device info (code: {result})")
        
        return devices
    
    def midi_callback(self, handle, msg, instance, param1, param2):
        """Callback function for MIDI input"""
        if msg == MIM_DATA:
            # Store message data
            timestamp = time.time()
            self.messages.append((param1, timestamp))
    
    def connect(self, device_index=0):
        """Connect to a MIDI input device"""
        num_devices = winmm.midiInGetNumDevs()
        
        if num_devices == 0:
            print("No MIDI input devices found!")
            return False
        
        if device_index >= num_devices or device_index < 0:
            print(f"Invalid device index {device_index}. Available devices: 0-{num_devices-1}")
            return False
        
        # Create callback
        self.callback = MIDI_CALLBACK(self.midi_callback)
        
        # Open MIDI input
        handle = ctypes.wintypes.HANDLE()
        result = winmm.midiInOpen(
            ctypes.byref(handle),
            device_index,
            self.callback,
            0,  # callback instance data
            CALLBACK_FUNCTION
        )
        
        if result != MMSYSERR_NOERROR:
            print(f"Failed to open MIDI device {device_index} (error code: {result})")
            return False
        
        self.handle = handle
        self.device_id = device_index
        
        # Get device name
        class MIDIINCAPS(ctypes.Structure):
            _fields_ = [
                ("wMid", ctypes.wintypes.WORD),
                ("wPid", ctypes.wintypes.WORD),
                ("vDriverVersion", ctypes.wintypes.DWORD),
                ("szPname", ctypes.c_char * 32),
                ("dwSupport", ctypes.wintypes.DWORD)
            ]
        
        caps = MIDIINCAPS()
        winmm.midiInGetDevCapsA(device_index, ctypes.byref(caps), ctypes.sizeof(caps))
        device_name = caps.szPname.decode('ascii', errors='ignore').rstrip('\x00')
        
        print(f"Connected to: {device_name}")
        
        # Start MIDI input
        result = winmm.midiInStart(self.handle)
        if result != MMSYSERR_NOERROR:
            print(f"Failed to start MIDI input (error code: {result})")
            self.disconnect()
            return False
        
        self.callback_installed = True
        return True
    
    def parse_midi_message(self, midi_data, timestamp):
        """Parse and format MIDI message for readable output"""
        # Extract bytes from the DWORD
        byte1 = midi_data & 0xFF
        byte2 = (midi_data >> 8) & 0xFF
        byte3 = (midi_data >> 16) & 0xFF
        
        status = byte1
        data1 = byte2
        data2 = byte3
        
        channel = (status & 0x0F) + 1  # MIDI channels are 1-16
        
        # Note On (0x90-0x9F)
        if 0x90 <= status <= 0x9F:
            note_name = self.note_to_name(data1)
            if data2 > 0:  # velocity > 0
                return f"Note ON  - Ch:{channel:2d} Note:{data1:3d}({note_name:>3}) Vel:{data2:3d}"
            else:
                return f"Note OFF - Ch:{channel:2d} Note:{data1:3d}({note_name:>3}) Vel:{data2:3d}"
        
        # Note Off (0x80-0x8F)
        elif 0x80 <= status <= 0x8F:
            note_name = self.note_to_name(data1)
            return f"Note OFF - Ch:{channel:2d} Note:{data1:3d}({note_name:>3}) Vel:{data2:3d}"
        
        # Control Change (0xB0-0xBF)
        elif 0xB0 <= status <= 0xBF:
            return f"CC       - Ch:{channel:2d} Ctrl:{data1:3d} Val:{data2:3d}"
        
        # Program Change (0xC0-0xCF)
        elif 0xC0 <= status <= 0xCF:
            return f"Program  - Ch:{channel:2d} Prog:{data1:3d}"
        
        # Pitch Bend (0xE0-0xEF)
        elif 0xE0 <= status <= 0xEF:
            bend_value = (data2 << 7) | data1
            return f"PitchBnd - Ch:{channel:2d} Val:{bend_value:5d}"
        
        # Other messages
        else:
            return f"Other    - Status:{status:02X} Data1:{data1:02X} Data2:{data2:02X}"
    
    def note_to_name(self, note_number):
        """Convert MIDI note number to note name"""
        if note_number < 0 or note_number > 127:
            return "???"
        
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (note_number // 12) - 1
        note_name = notes[note_number % 12]
        return f"{note_name}{octave}"
    
    def start_listening(self, callback=None):
        """Start listening for MIDI messages"""
        if not self.handle:
            print("No MIDI device connected!")
            return False
        
        if self.is_listening:
            print("Already listening!")
            return False
        
        self.is_listening = True
        print("Listening for MIDI data... (Press Ctrl+C to stop)")
        print("-" * 60)
        
        try:
            while self.is_listening:
                # Process any accumulated messages
                if self.messages:
                    while self.messages:
                        midi_data, timestamp = self.messages.pop(0)
                        parsed = self.parse_midi_message(midi_data, timestamp)
                        if parsed:
                            print(f"[{timestamp:8.3f}] {parsed}")
                            
                            # Call custom callback if provided
                            if callback:
                                callback(midi_data, parsed, timestamp)
                
                time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\nStopping...")
            self.stop_listening()
    
    def stop_listening(self):
        """Stop listening for MIDI messages"""
        self.is_listening = False
        print("Stopped listening.")
    
    def disconnect(self):
        """Disconnect from MIDI device"""
        self.stop_listening()
        
        if self.handle:
            # Stop MIDI input
            winmm.midiInStop(self.handle)
            # Reset MIDI input
            winmm.midiInReset(self.handle)
            # Close MIDI input
            winmm.midiInClose(self.handle)
            self.handle = None
            print("Disconnected from MIDI device.")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.disconnect()

