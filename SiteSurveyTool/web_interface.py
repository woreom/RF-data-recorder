from flask import Flask, render_template, request, jsonify
import json
import os
import sys
import datetime
import csv
from pathlib import Path
import threading

# Import the existing logic
# Ensure the current directory is in sys.path
sys.path.append(os.getcwd())
import recordHandle 

app = Flask(__name__)

PRESETS_FILE = 'presets.json'
RECORD_ROOT = os.environ.get('RECORD_FILE_PATH', 'data/') # Default to ./data/ if env var not set

# Ensure data directory exists
if not os.path.exists(RECORD_ROOT):
    os.makedirs(RECORD_ROOT)

def load_presets_data():
    if os.path.exists(PRESETS_FILE):
        with open(PRESETS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_presets_data(data):
    with open(PRESETS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/presets', methods=['GET'])
def get_presets():
    return jsonify(load_presets_data())

@app.route('/presets', methods=['POST'])
def save_preset():
    req = request.json
    name = req.get('name')
    data = req.get('data')
    
    presets = load_presets_data()
    presets[name] = data
    save_presets_data(presets)
    return jsonify({"status": "success"})

@app.route('/presets/<name>', methods=['GET'])
def get_preset(name):
    presets = load_presets_data()
    return jsonify(presets.get(name, {}))

@app.route('/start_recording', methods=['POST'])
def start_recording():
    options = request.form.to_dict()
    
    # Process inputs same as recordHandle.py
    # Conversions
    try:
        options['sampling_rate'] = int(options['sampling_rate'])
        options['drone_c_freq'] = options['center_freq'] 
        
        # Directory logic
        dir_name = options.pop('save_dir') # Remove from options to match logic or keep?
        # recordHandle uses dir_name to build path but options['record_dir'] is the final path
        
        ct = datetime.datetime.now()
        ct = str(ct).split(' ')
        ymd = ct[0]
        timestamp = ct[1]
        
        sub_dir = options['env'] + '_' + str(options['sdr_gain']) + '_' + str(options['sampling_rate']) + '_' + options['duration_recording'] + '_' + options['splitter'] + '_' + timestamp
        
        # Construct full path
        # Note: RECORD_ROOT should end with slash if logic expects it, or use os.path.join
        whole_dir = os.path.join(RECORD_ROOT, dir_name, ymd, sub_dir) + '/'
        
        print(f"Creating directory: {whole_dir}")
        options['record_dir'] = whole_dir
        nested_path = Path(whole_dir)
        nested_path.mkdir(parents=True, exist_ok=True)
        
        # Save readme
        des = options.pop('description', '')
        des_f = whole_dir + "readme.txt"
        with open(des_f, 'w') as file:
            file.write(des)
            file.write('\n')
            
        # Save CSV
        csv_f = whole_dir + "parameter_summary.csv"
        with open(csv_f, 'w', newline='') as c_f:
            fieldnames = options.keys()
            writer = csv.DictWriter(c_f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([options])
            
        # Setup GLOBAL_FILE_PATH for recordHandle
        # recordHandle uses this to call auto_record.py
        # In Docker, this script is in /app/SiteSurveyTool, so we can use os.getcwd()
        recordHandle.GLOBAL_FILE_PATH = os.getcwd()
        
        # Run in a separate thread so web server doesn't block (though Flask dev server is single threaded often)
        # Using a simple thread for now
        t = threading.Thread(target=run_recording_process, args=(options,))
        t.start()
        
        return f"Recording started! Saving to {whole_dir}. Check container logs for progress."

    except Exception as e:
        return f"Error: {str(e)}", 500

def run_recording_process(options):
    print("Starting recording process...")
    recordHandle.switchFreq2(options)
    print("Recording process finished.")

if __name__ == '__main__':
    # Listen on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
