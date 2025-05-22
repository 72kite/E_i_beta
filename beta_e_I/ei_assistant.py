from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import requests # For interacting with Home Assistant API
import json

app = Flask(__name__)

# --- Configuration (Replace with your actual Home Assistant details) ---
HOME_ASSISTANT_URL = "YOUR_HOME_ASSISTANT_URL"  # e.g., http://localhost:8123
HOME_ASSISTANT_TOKEN = "YOUR_HOME_ASSISTANT_TOKEN" # Your Long-Lived Access Token
# --- End Configuration ---

# --- Helper Function for Home Assistant API Calls ---
def call_home_assistant_api(endpoint, method="GET", data=None):
    """Helper function to call the Home Assistant API."""
    headers = {
        "Authorization": f"Bearer {HOME_ASSISTANT_TOKEN}",
        "content-type": "application/json",
    }
    url = f"{HOME_ASSISTANT_URL}/api/{endpoint}"
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Home Assistant API: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from Home Assistant API. Response text: {response.text}")
        return {"error": "Invalid JSON response from Home Assistant API"}


# --- Backend API Endpoints ---
@app.route('/')
def index():
    """Serves the main HTML interface."""
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Fetches and returns the status of configured devices from Home Assistant."""
    # Example: Get the state of a light
    light_status = call_home_assistant_api("states/light.your_light_entity_id") # Replace with your entity ID
    # Example: Get the state of a thermostat
    thermostat_status = call_home_assistant_api("states/climate.your_thermostat_entity_id") # Replace

    return jsonify({
        "light": light_status.get('state', 'unknown') if light_status else 'error',
        "thermostat_temp": thermostat_status.get('attributes', {}).get('current_temperature', 'unknown') if thermostat_status else 'error',
        "thermostat_hvac_action": thermostat_status.get('attributes', {}).get('hvac_action', 'unknown') if thermostat_status else 'error',
    })

@app.route('/api/listen', methods=['POST'])
def listen_for_command():
    """
    Placeholder for voice command processing.
    In a real app, this would use a microphone and SpeechRecognition.
    For now, it simulates recognizing a command.
    """
    # --- Actual Speech Recognition (Conceptual) ---
    # recognizer = sr.Recognizer()
    # with sr.Microphone() as source:
    #     print("E-i: Listening...")
    #     try:
    #         audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
    #         text = recognizer.recognize_google(audio)
    #         print(f"E-i: You said: {text}")
    #         response = process_command(text)
    #         return jsonify({"status": "success", "transcription": text, "response": response})
    #     except sr.WaitTimeoutError:
    #         return jsonify({"status": "error", "message": "No speech detected within timeout."})
    #     except sr.UnknownValueError:
    #         return jsonify({"status": "error", "message": "Could not understand audio."})
    #     except sr.RequestError as e:
    #         return jsonify({"status": "error", "message": f"Speech recognition service error; {e}"})
    # --- End Actual Speech Recognition ---

    # --- Simulated Speech Recognition ---
    data = request.get_json()
    command_text = data.get('command_text', '').lower()
    print(f"E-i: Received command text: {command_text}")
    response_message = process_command(command_text)
    return jsonify({"status": "simulated_success", "transcription": command_text, "response": response_message})
    # --- End Simulated ---


def process_command(command):
    """Processes the recognized voice command and interacts with Home Assistant."""
    command = command.lower()
    response_message = f"I heard: '{command}'. "

    if "turn on light" in command or "lights on" in command:
        # Replace 'light.your_light_entity_id' with your actual light entity ID
        result = call_home_assistant_api("services/light/turn_on", method="POST", data={"entity_id": "light.your_light_entity_id"})
        if result:
            response_message += "Turning the light on."
        else:
            response_message += "Failed to turn the light on."
    elif "turn off light" in command or "lights off" in command:
        # Replace 'light.your_light_entity_id' with your actual light entity ID
        result = call_home_assistant_api("services/light/turn_off", method="POST", data={"entity_id": "light.your_light_entity_id"})
        if result:
            response_message += "Turning the light off."
        else:
            response_message += "Failed to turn the light off."
    elif "set thermostat to" in command:
        try:
            # Example: "set thermostat to 72 degrees"
            temp_str = command.split("to")[-1].strip().split(" ")[0]
            temperature = int(temp_str)
            # Replace 'climate.your_thermostat_entity_id' with your actual thermostat entity ID
            result = call_home_assistant_api("services/climate/set_temperature", method="POST", data={"entity_id": "climate.your_thermostat_entity_id", "temperature": temperature})
            if result:
                response_message += f"Setting thermostat to {temperature} degrees."
            else:
                response_message += "Failed to set thermostat."
        except ValueError:
            response_message += "Could not parse the temperature from your command."
        except Exception as e:
            response_message += f"Error setting thermostat: {e}"
    elif "lock the door" in command:
        # Replace 'lock.your_lock_entity_id' with your actual lock entity ID
        result = call_home_assistant_api("services/lock/lock", method="POST", data={"entity_id": "lock.your_lock_entity_id"})
        if result:
            response_message += "Locking the door."
        else:
            response_message += "Failed to lock the door."
    elif "unlock the door" in command:
        # Replace 'lock.your_lock_entity_id' with your actual lock entity ID
        result = call_home_assistant_api("services/lock/unlock", method="POST", data={"entity_id": "lock.your_lock_entity_id"})
        if result:
            response_message += "Unlocking the door."
        else:
            response_message += "Failed to unlock the door."
    else:
        response_message += "Sorry, I didn't understand that command."

    return response_message

@app.route('/api/device_control', methods=['POST'])
def device_control():
    """Controls a device based on JSON payload."""
    data = request.get_json()
    entity_id = data.get('entity_id')
    service = data.get('service') # e.g., "turn_on", "turn_off", "set_temperature"
    service_domain = data.get('domain') # e.g., "light", "climate", "lock"
    service_data = data.get('service_data', {}) # e.g., {"temperature": 22}

    if not all([entity_id, service, service_domain]):
        return jsonify({"status": "error", "message": "Missing entity_id, service, or domain"}), 400

    ha_service_data = {"entity_id": entity_id, **service_data}
    result = call_home_assistant_api(f"services/{service_domain}/{service}", method="POST", data=ha_service_data)

    if result:
        # Check if the service call was successful (HA API usually returns the new state or an empty list on success)
        # This check might need to be adjusted based on specific service call responses
        if isinstance(result, list) or (isinstance(result, dict) and 'entity_id' in result.get('context', {})):
             return jsonify({"status": "success", "message": f"Called {service_domain}.{service} on {entity_id}", "details": result})
        elif isinstance(result, dict) and result.get('message'): # Home Assistant often returns a message on error
            return jsonify({"status": "error", "message": f"Home Assistant error: {result.get('message')}", "details": result})
        else: # Fallback for successful calls that might not fit the above
             return jsonify({"status": "success", "message": f"Service {service_domain}.{service} called on {entity_id}", "details": result})

    else:
        return jsonify({"status": "error", "message": f"Failed to call service {service_domain}.{service} on {entity_id}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)