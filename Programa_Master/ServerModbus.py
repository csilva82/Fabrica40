import argparse
import logging
from pyModbusTCP.server import ModbusServer
import signal
import sys
import threading
from queue import Queue
import time

# Configurer les logs
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Parse args
parser = argparse.ArgumentParser()
parser.add_argument('-H', '--host', type=str, default='127.0.0.1', help='Host (default: localhost)')
parser.add_argument('-p', '--port', type=int, default=5050, help='TCP port (default: 5050)')
#parser.add_argument('-d', '--debug', action='store_true', help='Set debug mode')
args = parser.parse_args()

# Logging setup
#if args.debug:
    #logging.getLogger('pyModbusTCP.server').setLevel(logging.DEBUG)

# Variable to store coil values written by the client
coil_values = [False, False, True, True]


# Queue to communicate between threads
coil_values_queue = Queue()

# Function to read coils
def read_coils(address, count):
    return coil_values[address: address + count]

# Function to write coils
def write_coils(address, values):
    global coil_values
    coil_values[address: address + len(values)] = values
    # Put the modified values in the queue
    coil_values_queue.put(coil_values)

# Function to handle signal interruption (e.g., Ctrl+C)
def signal_handler(sig, frame):
    print("\nStopping Modbus server...")
    server.stop()
    sys.exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Initialize Modbus server
server = ModbusServer(host=args.host, port=args.port, no_block=True)

def start_modbus_server():
    print("Before starting Modbus server")
    try:
        server.start()
        print("Modbus server started")
        
       
            
    except Exception as start_error:
        print(f"Error starting Modbus server: %s", str(start_error))
        print("Error starting Modbus server")
        sys.exit(1)

# Start Modbus server in a separate thread
modbus_thread = threading.Thread(target=start_modbus_server, daemon=True)
modbus_thread.start()

try:
    # Main loop for the main thread
    while True:
        # Check if there are modified values in the queue
        if not coil_values_queue.empty():
            coils_values = coil_values_queue.get()
            print("Read coils: " + str (coils_values))
            # Do something with the coil values if needed
except Exception as e:
    print("An error occurred:" + str (e))
finally:
    print("Exiting the main loop.")
    # Ensure the server is stopped when the script exits
    server.stop()
    print("Modbus server stopped.")