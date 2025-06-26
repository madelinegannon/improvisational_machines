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

class KorgNanoKONTROL2Reader:
    def __init__(self):
        self.device_id = None
        self.handle = None
        self.is_listening = False
        self.callback_installed = False
        self.messages = []
        self.message_lock = Event()
        
        # Korg nanoKONTROL2 Control Mapping (Default Factory Settings)
        self.control_map = {
            # Sliders (Channel 1, CC 0-7)
            0: "Slider 1", 1: "Slider 2", 2: "Slider 3", 3: "Slider 4",
            4: "Slider 5", 5: "Slider 6", 7: "Slider 7", 6: "Slider 8",
            
            # Knobs (Channel 1, CC 16-23)
            16: "Knob 1", 17: "Knob 2", 18: "Knob 3", 19: "Knob 4",
            20: "Knob 5", 21: "Knob 6", 22: "Knob 7", 23: "Knob 8",
            
            # Solo Buttons (Channel 1, CC 32-39) - Momentary
            32: "Solo 1", 33: "Solo 2", 34: "Solo 3", 35: "Solo 4",
            36: "Solo 5", 37: "Solo 6", 38: "Solo 7", 39: "Solo 8",
            
            # Mute Buttons (Channel 1, CC 48-55) - Toggle
            48: "Mute 1", 49: "Mute 2", 50: "Mute 3", 51: "Mute 4",  
            52: "Mute 5", 53: "Mute 6", 54: "Mute 7", 55: "Mute 8",
            
            # Record Buttons (Channel 1, CC 64-71) - Toggle
            64: "Rec 1", 65: "Rec 2", 66: "Rec 3", 67: "Rec 4",
            68: "Rec 5", 69: "Rec 6", 70: "Rec 7", 71: "Rec 8",
            
            # Transport Buttons
            41: "◄◄ (Prev Track)", 42: "►► (Next Track)", 43: "⚫ (Set)", 44: "■ (Marker)",
            45: "◄ (Rewind)", 46: "⏵ (Fast Forward)", 47: "⏹ (Stop)", 40: "▶ (Play)", 
            
            # Scene Button
            60: "🎬 (Scene)"
        }
        
        # Button states for toggle buttons
        self.button_states = {}
        
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
                
                # Highlight if it looks like a nanoKONTROL2
                if "nanokontrol" in device_name.lower() or "nano kontrol" in device_name.lower():
                    print(f"      ⭐ This looks like your nanoKONTROL2!")
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
        
        print(f"🎛️  Connected to: {device_name}")
        print("=" * 60)
        
        # Start MIDI input
        result = winmm.midiInStart(self.handle)
        if result != MMSYSERR_NOERROR:
            print(f"Failed to start MIDI input (error code: {result})")
            self.disconnect()
            return False
        
        self.callback_installed = True
        return True
    
    def parse_nanokontrol_message(self, midi_data, timestamp):
        """Parse MIDI message specifically for nanoKONTROL2"""
        # Extract bytes from the DWORD
        byte1 = midi_data & 0xFF
        byte2 = (midi_data >> 8) & 0xFF
        byte3 = (midi_data >> 16) & 0xFF
        
        status = byte1
        controller = byte2
        value = byte3
        
        channel = (status & 0x0F) + 1  # MIDI channels are 1-16
        
        # Control Change messages (0xB0-0xBF) - what nanoKONTROL2 sends
        if 0xB0 <= status <= 0xBF:
            control_name = self.control_map.get(controller, f"CC {controller}")
            
            # Special handling for different control types
            if controller in range(0, 8) or controller in range(16, 24):
                # Sliders and Knobs (0-127 range)
                percentage = round((value / 127.0) * 100, 1)
                bar = self.create_value_bar(value, 127)
                return f"{control_name:<12} │ {bar} │ {value:3d}/127 ({percentage:5.1f}%)"
                
            elif controller in [32, 33, 34, 35, 36, 37, 38, 39]:
                # Solo buttons (momentary - press/release)
                if value == 127:
                    return f"{control_name:<12} │ 🔴 PRESSED"
                else:
                    return f"{control_name:<12} │ ⚪ RELEASED"
                    
            elif controller in range(48, 72):
                # Toggle buttons (Mute, Rec) - track state
                if value == 127:  # Button pressed
                    # Toggle the state
                    current_state = self.button_states.get(controller, False)
                    new_state = not current_state
                    self.button_states[controller] = new_state
                    
                    if controller in range(48, 56):  # Mute buttons
                        state_icon = "🔇 MUTED" if new_state else "🔊 UNMUTED"
                    else:  # Record buttons
                        state_icon = "🔴 RECORDING" if new_state else "⚫ STOPPED"
                    
                    return f"{control_name:<12} │ {state_icon}"
                else:
                    return None  # Don't show button release for toggle buttons
                    
            elif controller in [40, 41, 42, 43, 44, 45, 46, 47]:
                # Transport buttons
                if value == 127:
                    transport_actions = {
                        40: "▶️  PLAY STARTED",
                        41: "⏮️  PREVIOUS TRACK", 
                        42: "⏭️  NEXT TRACK",
                        43: "📍 MARKER SET",
                        44: "🏷️  MARKER",
                        45: "⏪ REWINDING",
                        46: "⏩ FAST FORWARD",
                        47: "⏹️  STOPPED"
                    }
                    action = transport_actions.get(controller, "TRANSPORT")
                    return f"{control_name:<12} │ {action}"
                else:
                    return None  # Don't show transport button releases
                    
            elif controller == 60:
                # Scene button
                if value == 127:
                    return f"{control_name:<12} │ 🎬 SCENE TRIGGERED"
                else:
                    return None
            else:
                # Unknown control
                return f"Unknown CC{controller:<3} │ Value: {value}"
        
        # Other message types (shouldn't happen with nanoKONTROL2)
        else:
            return f"Non-CC Message   │ Status:{status:02X} Data1:{controller:02X} Data2:{value:02X}"
    
    def create_value_bar(self, value, max_value, length=20):
        """Create a visual bar representation of a value"""
        filled = int((value / max_value) * length)
        bar = "█" * filled + "░" * (length - filled)
        return bar
    
    def start_listening(self, callback=None):
        """Start listening for MIDI messages"""
        if not self.handle:
            print("No MIDI device connected!")
            return False
        
        if self.is_listening:
            print("Already listening!")
            return False
        
        self.is_listening = True
        print("🎵 Listening for nanoKONTROL2 input... (Press Ctrl+C to stop)")
        print("=" * 80)
        print("Try moving sliders, turning knobs, and pressing buttons!")
        print("-" * 80)
        
        try:
            while self.is_listening:
                # Process any accumulated messages
                if self.messages:
                    while self.messages:
                        midi_data, timestamp = self.messages.pop(0)
                        parsed = self.parse_nanokontrol_message(midi_data, timestamp)
                        if parsed:  # Only show if parsing returned something
                            time_str = time.strftime("%H:%M:%S", time.localtime(timestamp))
                            print(f"[{time_str}] {parsed}")
                            
                            # Call custom callback if provided
                            if callback:
                                callback(midi_data, parsed, timestamp)
                
                time.sleep(0.001)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\n" + "=" * 80)
            print("🛑 Stopping...")
            self.stop_listening()
    
    def stop_listening(self):
        """Stop listening for MIDI messages"""
        self.is_listening = False
        print("✅ Stopped listening.")
    
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
            print("🔌 Disconnected from MIDI device.")
    
    def print_controller_layout(self):
        """Print a visual representation of the nanoKONTROL2 layout"""
        print("\n" + "=" * 80)
        print("🎛️  KORG nanoKONTROL2 Layout")
        print("=" * 80)
        print("   Knobs:    [  1  ] [  2  ] [  3  ] [  4  ] [  5  ] [  6  ] [  7  ] [  8  ]")
        print("   Sliders:  [  1  ] [  2  ] [  3  ] [  4  ] [  5  ] [  6  ] [  7  ] [  8  ]")
        print("   Solo:     [ S1  ] [ S2  ] [ S3  ] [ S4  ] [ S5  ] [ S6  ] [ S7  ] [ S8  ]")
        print("   Mute:     [ M1  ] [ M2  ] [ M3  ] [ M4  ] [ M5  ] [ M6  ] [ M7  ] [ M8  ]") 
        print("   Record:   [ R1  ] [ R2  ] [ R3  ] [ R4  ] [ R5  ] [ R6  ] [ R7  ] [ R8  ]")
        print()
        print("   Transport: [◄◄] [►►] [⚫] [■] | [◄] [⏵] [⏹] [▶] | [🎬]")
        print("             Prev Next Set Mark  Rew FFwd Stop Play Scene")
        print("=" * 80)
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.disconnect()


# Example usage
if __name__ == "__main__":
    if sys.platform != "win32":
        print("❌ This version only works on Windows!")
        sys.exit(1)
    
    print("🎛️" + "=" * 50)
    print("   KORG nanoKONTROL2 MIDI Monitor")
    print("=" * 51)
    
    nano_reader = KorgNanoKONTROL2Reader()
    
    try:
        # Show controller layout
        nano_reader.print_controller_layout()
        
        # List available devices
        print("\n📱 Scanning for MIDI devices...")
        devices = nano_reader.list_devices()
        
        if devices:
            print(f"\n🔌 Which device would you like to connect to?")
            print("   (Usually the nanoKONTROL2 will be device 0 or 1)")
            
            # Try to auto-detect nanoKONTROL2
            nanokontrol_device = None
            for i, (device_id, device_name) in enumerate(devices):
                if "nanokontrol" in device_name.lower() or "nano kontrol" in device_name.lower():
                    nanokontrol_device = device_id
                    break
            
            if nanokontrol_device is not None:
                print(f"🎯 Auto-detected nanoKONTROL2 at device {nanokontrol_device}")
                device_index = nanokontrol_device
            else:
                print("❓ No nanoKONTROL2 auto-detected. Trying device 0...")
                device_index = 0
            
            if nano_reader.connect(device_index):
                
                # Define a custom callback for special processing (optional)
                def my_callback(midi_data, parsed_message, timestamp):
                    # You can add custom processing here
                    # For example, log to file, send to other applications, etc.
                    pass
                
                # Start listening (this will block until Ctrl+C)
                nano_reader.start_listening(callback=my_callback)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        nano_reader.disconnect()