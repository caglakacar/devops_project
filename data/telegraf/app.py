from flask import Flask, jsonify, request
import subprocess
import logging
import time

app = Flask(__name__)

RESET = "\033[0m"
PURPLE = "\033[95m"  
RED = "\033[91m"     
BLUE = "\033[94m"    
GREEN = "\033[92m"   

logging.basicConfig(
    level=logging.DEBUG, 
    format=f'{RESET}%(asctime)s - %(levelname)s - %(message)s'
)

def log_get_config():
    logging.info(f'{PURPLE}GET /config called.{RESET}')

def log_put_config():
    logging.info(f'{RED}PUT /config called.{RESET}')

def log_get_restart():
    logging.info(f'{BLUE}GET /restart called.{RESET}')

def log_telegraf_started():
    logging.info(f'{GREEN}Telegraf started.{RESET}')


def start_telegraf():
    try:
        result = subprocess.run(["pgrep", "telegraf"], stdout=subprocess.PIPE)
        if result.returncode != 0:  
            subprocess.Popen(["telegraf", "--config", "/etc/telegraf/telegraf.conf"])
            log_telegraf_started()
        else:
            logging.info("Telegraf is already running.")
    except Exception as e:
        logging.error(f"Failed to start Telegraf: {e}")


def restart_telegraf():
    try:
        logging.info("Attempting to restart Telegraf...")
        subprocess.run(["pkill", "telegraf"], check=True)
        time.sleep(2)
        subprocess.Popen(["telegraf", "--config", "/etc/telegraf/telegraf.conf"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.info("Telegraf restarted successfully.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to restart Telegraf: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while restarting Telegraf: {e}")
        return False


@app.route('/config', methods=['GET'])
def get_telegraf_config():
    log_get_config()
    try:
        with open('/etc/telegraf/telegraf.conf', 'r') as file:
            config_data = file.read()
        return config_data, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        logging.error(f"Failed to read Telegraf config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/config', methods=['PUT'])
def update_telegraf_config():
    log_put_config()
    try:
        new_config = request.data.decode('utf-8')
        with open('/etc/telegraf/telegraf.conf', 'w') as file:
            file.write(new_config)  
        
        if restart_telegraf():
            return "Config updated and Telegraf restarted successfully.", 200
        else:
            return "Config updated but failed to restart Telegraf.", 500
    except Exception as e:
        logging.error(f"Failed to update Telegraf config: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/restart', methods=['GET'])
def restart_telegraf_route():
    log_get_restart()
    if restart_telegraf():
        return "Telegraf restarted successfully.", 200
    else:
        return "Failed to restart Telegraf.", 500


@app.route('/version', methods=['GET'])
def get_telegraf_version():
    logging.info("Attempting to get Telegraf version...")
    try:
        result = subprocess.run(["telegraf", "version"], capture_output=True, text=True)
        clean_version = result.stdout.split('(')[0].strip()
        return jsonify({"Telegraf Version": clean_version})
    except Exception as e:
        logging.error(f"Failed to get Telegraf version: {e}")
        return jsonify({"error": f"Failed to get Telegraf version: {str(e)}"}), 500


if __name__ == '__main__':
    start_telegraf()
    app.run(host='0.0.0.0', port=5000)