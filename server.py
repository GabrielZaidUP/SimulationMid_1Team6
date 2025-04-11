from flask import Flask, jsonify, render_template, send_from_directory
import subprocess
import os
import sys

app = Flask(__name__)

# Path to your main simulation script
SIMULATION_SCRIPT = 'main.py'  # Adjust this path as needed

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('index.html')

@app.route('/dashboard_data/<path:filename>')
def serve_data_files(filename):
    """Serve files from the dashboard_data directory"""
    return send_from_directory('dashboard_data', filename)

@app.route('/run_simulation')
def run_simulation():
    """Run the Python simulation script"""
    try:
        # Get the path to the Python executable
        python_executable = sys.executable
        
        # Run the simulation script
        result = subprocess.run(
            [python_executable, SIMULATION_SCRIPT],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Return success response
        return jsonify({
            'success': True,
            'message': 'Simulation completed successfully',
            'output': result.stdout
        })
    
    except subprocess.CalledProcessError as e:
        # Return error response
        return jsonify({
            'success': False,
            'message': f'Simulation failed with code {e.returncode}',
            'output': e.stdout + '\n' + e.stderr
        })
    
    except Exception as e:
        # Return error response for other exceptions
        return jsonify({
            'success': False,
            'message': f'Error running simulation: {str(e)}',
            'output': ''
        })

if __name__ == '__main__':
    # Run the Flask server
    app.run(debug=True, port=8000)