import os
import logging
from datetime import datetime

class MEDC17EmissionHandler:
    """
    MEDC17.9 JLR ECU Emission Handler
    Securely disables DPF, EGR, SCR, and Start/Stop systems in the binary file.
    Includes advanced pattern matching and switches for feature control.
    """

    def __init__(self, input_file="ecu.bin", output_file=None, options=None):
        self.input_file = input_file
        self.output_file = output_file or f"{os.path.splitext(self.input_file)[0]}_modified_{datetime.now().strftime('%Y%m%d%H%M%S')}.bin"
        self.options = options or {'dpf': True, 'egr': True, 'scr': True, 'start_stop': True}  # Default: All features enabled
        self.patterns = {
            'DPF': {
                'signature': bytes([0x44, 0x50, 0x46, 0x5F]),  # 'DPF_'
                'stock': bytes([0x01, 0x01, 0x01, 0x00, 0x00]),
                'off': bytes([0x00, 0x00, 0x00, 0xFF, 0xFF])
            },
            'EGR': {
                'signature': bytes([0x45, 0x47, 0x52, 0x56]),  # 'EGRV'
                'stock': bytes([0x01, 0x01, 0x01, 0x00]),
                'off': bytes([0x00, 0x00, 0x00, 0xFF])
            },
            'SCR': {
                'signature': bytes([0x53, 0x43, 0x52, 0x5F]),  # 'SCR_'
                'stock': bytes([0x01, 0x01, 0x01, 0x00, 0x00]),
                'off': bytes([0x00, 0x00, 0x00, 0xFF, 0xFF])
            },
            'StartStop': {
                'signature': bytes([0x53, 0x54, 0x41, 0x52, 0x54]),  # 'START'
                'stock': bytes([0x01, 0x01, 0x00]),
                'off': bytes([0x00, 0x00, 0xFF])
            }
        }
        self.setup_logging()

    def setup_logging(self):
        """
        Sets up secure logging to track changes and errors during the process.
        """
        logging.basicConfig(
            filename="emission_handler.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        logging.info("Initialized MEDC17EmissionHandler with options: %s", self.options)

    def validate_file(self):
        """
        Validates if the input file exists and is accessible.
        """
        if not os.path.exists(self.input_file):
            logging.error(f"Input file {self.input_file} does not exist.")
            raise FileNotFoundError(f"File {self.input_file} not found.")
        if not os.access(self.input_file, os.R_OK):
            logging.error(f"Input file {self.input_file} is not readable.")
            raise PermissionError(f"File {self.input_file} is not readable.")
        logging.info(f"Validated input file {self.input_file}.")

    def read_binary(self):
        """
        Reads the binary file and returns its content as a bytearray.
        """
        try:
            with open(self.input_file, 'rb') as f:
                logging.info(f"Reading binary file {self.input_file}.")
                return bytearray(f.read())
        except Exception as e:
            logging.error(f"Error reading file {self.input_file}: {e}")
            raise

    def write_binary(self, data):
        """
        Writes the modified binary data to a new file.
        """
        try:
            with open(self.output_file, 'wb') as f:
                f.write(data)
                logging.info(f"Modified file saved as {self.output_file}.")
        except Exception as e:
            logging.error(f"Error writing file {self.output_file}: {e}")
            raise

    def apply_modifications(self, data):
        """
        Applies all enabled pattern modifications to the binary data.
        """
        changes = []
        for pattern_name, pattern in self.patterns.items():
            if not self.options.get(pattern_name.lower(), False):  # Check if the feature is enabled
                logging.info(f"Skipping {pattern_name} modification (disabled by user).")
                continue

            for i in range(len(data) - len(pattern['signature'])):
                # Match the signature
                if data[i:i + len(pattern['signature'])] == pattern['signature']:
                    # Check if the stock bytes match
                    stock_start = i + len(pattern['signature'])
                    stock_end = stock_start + len(pattern['stock'])
                    if data[stock_start:stock_end] == pattern['stock']:
                        # Replace stock bytes with off bytes
                        data[stock_start:stock_end] = pattern['off']
                        changes.append((pattern_name, hex(i)))
                        logging.info(f"{pattern_name} modified at offset {hex(i)}.")
                        break  # Once applied, move to the next pattern
        return changes

    def process(self):
        """
        Main process to validate, read, apply modifications, and save the output.
        """
        try:
            self.validate_file()
            data = self.read_binary()
            changes = self.apply_modifications(data)
            if changes:
                print("\nModification Report:")
                print("-" * 40)
                for name, offset in changes:
                    print(f"{name} modified at offset {offset}")
                self.write_binary(data)
                print(f"\nModified file saved as {self.output_file}")
            else:
                logging.warning("No modifications applied. Patterns may not match the input file.")
                print("No modifications applied. Patterns may not match the input file.")
        except Exception as e:
            logging.error(f"Processing failed: {e}")
            print(f"Error during processing: {e}")

if __name__ == "__main__":
    print("\nMEDC17.9 JLR ECU Emission Handler")
    print("Advanced version with feature switches and logging")
    print("-" * 40)

    input_file = input("Enter the ECU binary file name (default: ecu.bin): ") or "ecu.bin"
    
    # User-defined feature switches
    print("\nEnable or disable features (y/n):")
    dpf_switch = input("Disable DPF (y/n): ").strip().lower() == 'y'
    egr_switch = input("Disable EGR (y/n): ").strip().lower() == 'y'
    scr_switch = input("Disable SCR (y/n): ").strip().lower() == 'y'
    start_stop_switch = input("Disable Start/Stop (y/n): ").strip().lower() == 'y'

    options = {
        'dpf': dpf_switch,
        'egr': egr_switch,
        'scr': scr_switch,
        'start_stop': start_stop_switch
    }

    handler = MEDC17EmissionHandler(input_file=input_file, options=options)
    handler.process()