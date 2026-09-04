from flask import Flask, render_template, jsonify,request
import serial
import json
import threading
import time
import pandas as pd

app = Flask(__name__,template_folder="",static_folder="")

SERIAL_PORT = 'COM6'
BAUD_RATE = 9600

scanned_uids = [] 
is_scanning = False  



def read_from_arduino():
    global scanned_uids, is_scanning
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        
        while True:
            if is_scanning and ser.in_waiting > 0:
                raw_data = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if raw_data and (raw_data not in scanned_uids):
                    scanned_uids.append(raw_data)
            
            time.sleep(0.05)
            
    except Exception as e:
        print(f"Error Serial: {e}")

threading.Thread(target=read_from_arduino, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.jinja')

@app.route('/start-scan', methods=['POST'])
def start_scan():
    global scanned_uids, is_scanning
    scanned_uids = []  
    is_scanning = True 
    return jsonify({'status': 'scanning_started'})

@app.route('/stop-scan', methods=['POST'])
def stop_scan():
    global is_scanning
    is_scanning = False 
    return jsonify({'status': 'scanning_stopped'})

@app.route('/get-uid')
def get_uid():
    return jsonify({'uids': scanned_uids})

@app.route('/uidContent', methods=["GET"])
def uidContent():
  d = request.args.getlist('uids') 
  dfExcel=pd.read_excel("sample_data.xlsx")
  dfFilt=dfExcel[dfExcel["UID"].isin(d)]
  dfTJ = dfFilt.to_json(orient='records')
  dfJl=json.loads(dfTJ)
  return json.dumps([dfJl],check_circular=False)

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False)
