from flask import Flask, render_template, jsonify
import subprocess
import os
import threading
import sys
import time

app = Flask(__name__)

# Store running processes
processes = {}
process_lock = threading.Lock()  # Thread-safe access to processes

def run_script(script_name, key):
    """Runs a Python script in a separate subprocess."""
    with process_lock:
        if key in processes:
            # Check if the process is still running
            if processes[key].poll() is None:
                return jsonify({"status": f"{key} already running"})
            else:
                # Process has terminated, clean it up
                del processes[key]

        # Start the script in a subprocess
        try:
            process = subprocess.Popen([sys.executable, script_name])
            processes[key] = process
            return jsonify({"status": f"{key} started"})
        except Exception as e:
            return jsonify({"status": f"Failed to start {key}: {str(e)}"})

def stop_process(key):
    """Stops a specific process by key."""
    with process_lock:
        if key in processes:
            process = processes[key]
            if process.poll() is None:  # Check if the process is still running
                process.terminate()  # Gracefully terminate the process
                process.wait()  # Wait for the process to terminate
            del processes[key]
            return jsonify({"status": f"{key} stopped"})
        return jsonify({"status": f"{key} not running"})

def cleanup_processes():
    """Periodically clean up terminated processes."""
    while True:
        with process_lock:
            for key, process in list(processes.items()):
                if process.poll() is not None:  # Process has terminated
                    del processes[key]
        time.sleep(5)  # Check every 5 seconds

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_mouse')
def start_mouse():
    return run_script("virtual_mouse.py", "Mouse")

@app.route('/start_keyboard')
def start_keyboard():
    return run_script("virtual_keyboard.py", "keyboard")

@app.route('/start_rps')
def start_rps():
    return run_script("RPS-CV.py", "RPS")

@app.route('/stop_mouse')
def stop_mouse():
    return stop_process("mouse")

@app.route('/stop_keyboard')
def stop_keyboard():
    return stop_process("keyboard")

@app.route('/stop_rps')
def stop_rps():
    return stop_process("rps")

@app.route('/stop_all')
def stop_all():
    with process_lock:
        for key, process in list(processes.items()):
            if process.poll() is None:  # Check if the process is still running
                process.terminate()  # Gracefully terminate the process
                process.wait()  # Wait for the process to terminate
            del processes[key]
        return jsonify({"status": "All processes stopped"})

if __name__ == '__main__':
    # Start a background thread to clean up terminated processes
    cleanup_thread = threading.Thread(target=cleanup_processes, daemon=True)
    cleanup_thread.start()

    app.run(debug=True)