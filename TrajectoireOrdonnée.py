import time
import requests
import sys
import paho.mqtt.client as paho
import json


# ----- CONFIG MQTT ------
MQTT_BROKER_IP = "127.0.0.1"
MQTT_PORT = 1883
client = paho.Client(paho.CallbackAPIVersion.VERSION2)

# Subscribe
MQTT_COMMAND_ROBOTINO_TOPIC = "robotino/command"
MQTT_FINISH_PISTON1_TOPIC = "piston1/finish"
MQTT_FINISH_PISTON2_TOPIC = "piston2/finish"

# Publish
MQTT_COMMAND_PISTON1_TOPIC = "piston1/command"
MQTT_COMMAND_PISTON2_TOPIC = "piston2/command"

# Connexion aux topics
def on_connect(client, userdata, flags, rc, properties):
    global _mqtt_continue_received
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(MQTT_COMMAND_ROBOTINO_TOPIC) # Souscrire au topic de commande robotino
        client.subscribe(MQTT_FINISH_PISTON1_TOPIC)   # Souscrire au topic de fin piston 1
        client.subscribe(MQTT_FINISH_PISTON2_TOPIC)   # Souscrire au topic de fin piston 2
        client.subscribe(MQTT_COMMAND_PISTON1_TOPIC)  # Souscrire au topic de commande piston 1
        client.subscribe(MQTT_COMMAND_PISTON2_TOPIC)  # Souscrire au topic de commande piston 2
    else:
        print("Failed to connect, return code %d\n", rc)

def on_publish(client, userdata, mid, rc, properties):
    print(f"Message {mid} published with result {rc}")

def on_message(client, userdata, msg):
    global _mqtt_continue_received
    print(f"Received MQTT message on topic '{msg.topic}': {msg.payload.decode()}")
    if (msg.topic == MQTT_COMMAND_ROBOTINO_TOPIC or msg.topic == MQTT_FINISH_PISTON1_TOPIC or msg.topic == MQTT_FINISH_PISTON2_TOPIC) and msg.payload.decode() == "continue":
        _mqtt_continue_received = True
        print("💡 Received 'continue' command. Robot will resume movement.")

client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message

try:
    client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
    client.loop_start() # Start non-blocking loop
except Exception as e:
    print(f"Error connecting to MQTT broker: {e}")

def publish_mqtt_piston1_command():
    try:
        message = {"robot_id": "robotino_1", "location": "vertex 1", "timestamp": time.time()}
        client.publish(MQTT_COMMAND_PISTON1_TOPIC, json.dumps(message))
        print(f"Published MQTT message: {json.dumps(message)}")
    except Exception as e:
        print(f"Error publishing MQTT message: {e}")

def publish_mqtt_piston2_command():
    try:
        message = {"robot_id": "robotino_1", "location": "vertex 2", "timestamp": time.time()}
        client.publish(MQTT_COMMAND_PISTON2_TOPIC, json.dumps(message))
        print(f"Published MQTT message: {json.dumps(message)}")
    except Exception as e:
        print(f"Error publishing MQTT message: {e}")


# ----- CONFIG Robotino -----
_mqtt_continue_received = False
ROBOT_IP = "192.168.0.101"
OMNIDRIVE_URL = f"http://{ROBOT_IP}/data/omnidrive"
BUMPER_URL = f"http://{ROBOT_IP}/data/bumper"

def send_velocity(vx, vy, omega):
    """Send velocity command to Robotino."""
    try:
        requests.post(OMNIDRIVE_URL, json=[vx, vy, omega], timeout=0.2)
    except Exception as e:
        print("Warning: failed to send velocity:", e)

def stop():
    """Stop Robotino."""
    send_velocity(0.0, 0.0, 0.0)

def bumper_pressed():
    """Return True if bumper is pressed."""
    try:
        resp = requests.get(BUMPER_URL, timeout=0.2).json()
        return resp.get("value", False)
    except:
        return False  # if we can't read bumper, assume not pressed

def move_forward(distance_m, speed_mps=0.4):
    duration = distance_m / speed_mps
    print(f"Moving forward {distance_m:.2f} m...")

    start = time.time()
    while time.time() - start < duration:
        if bumper_pressed():
            print("❗ Bumper touched! Stopping robot.")
            stop()
            return  # immediately stop this movement
        send_velocity(speed_mps, 0.0, 0.0)
        time.sleep(0.05)

    stop()
    time.sleep(0.3)

def rotate_angle(angle_deg, omega_rad_s=0.3):
    angle_rad = angle_deg * 3.14159265 / 180.0
    duration = abs(angle_rad) / omega_rad_s
    direction = 1.0 if angle_rad > 0 else -1.0

    print(f"Rotating {angle_deg:.1f}°...")

    start = time.time()

    while time.time() - start < duration:
        if bumper_pressed():
            print("❗ Bumper touched during rotation! Stopping robot.")
            stop()
            return
        send_velocity(0.0, 0.0, direction * omega_rad_s)
        time.sleep(0.05)

    stop()
    time.sleep(0.3)


# ----- Trajectoire -----
def drive_triangle(edge_length_m=2):
    global _mqtt_continue_received
    print("Starting triangle...")


    # Wait for MQTT robotino/command to continue
    _mqtt_continue_received = False
    print(f"Waiting at vertex start for 'continue' MQTT command on topic '{MQTT_COMMAND_ROBOTINO_TOPIC}'...")
    while not _mqtt_continue_received:
        time.sleep(0.1) # Check flag periodically
    print(f"Resuming movement from vertex 0.")
    # End Wait
    print(f"\nEdge 1")
    move_forward(edge_length_m)
    if bumper_pressed(): # Check for bumper after movement
        print("Triangle aborted because bumper was pressed.")
        stop()
        return

    # Stop and publish at vertex
    print(f"Reached vertex 1. Stopping and publishing presence...")
    stop() # Ensure robot is stopped at the vertex
    time.sleep(1.0) # Pause for 1 second at the vertex
    publish_mqtt_piston1_command()
    time.sleep(0.5) # Small delay after publishing

    # Send to MQTT piston1/command
    message = "start"
    client.publish(MQTT_COMMAND_PISTON1_TOPIC, message)
    print(f"Message '{message}' publié sur le topic '{MQTT_COMMAND_PISTON1_TOPIC}'.")

    # Wait for MQTT piston1/finish to continue
    _mqtt_continue_received = False
    print(f"Waiting at vertex 1 for 'continue' MQTT command on topic '{MQTT_FINISH_PISTON1_TOPIC}'...")
    while not _mqtt_continue_received:
        time.sleep(0.1) # Check flag periodically
    print(f"Resuming movement from vertex 1.")
    # End Wait

    rotate_angle(120.0) # Rotate for next edge
    if bumper_pressed(): # If a bumper stopped movement during rotation
        print("Triangle aborted because bumper was pressed during rotation.")
        stop()
        return


    print(f"\nEdge 2")
    move_forward(edge_length_m)
    if bumper_pressed(): # Check for bumper after movement
        print("Triangle aborted because bumper was pressed.")
        stop()
        return

    # Stop and publish at vertex
    print(f"Reached vertex 2. Stopping and publishing presence...")
    stop() # Ensure robot is stopped at the vertex
    time.sleep(1.0) # Pause for 1 second at the vertex
    publish_mqtt_piston2_command()
    time.sleep(0.5) # Small delay after publishing

    # Send to MQTT piston2/command
    message = "start"
    client.publish(MQTT_COMMAND_PISTON2_TOPIC, message)
    print(f"Message '{message}' publié sur le topic '{MQTT_COMMAND_PISTON2_TOPIC}'.")

    # Wait for MQTT piston2/finish to continue
    _mqtt_continue_received = False
    print(f"Waiting at vertex 2 for 'continue' MQTT command on topic '{MQTT_FINISH_PISTON2_TOPIC}'...")
    while not _mqtt_continue_received:
        time.sleep(0.1) # Check flag periodically
    print(f"Resuming movement from vertex 2.")
    # End Wait

    rotate_angle(120.0) # Rotate for next edge
    if bumper_pressed(): # If a bumper stopped movement during rotation
        print("Triangle aborted because bumper was pressed during rotation.")
        stop()
        return


    print(f"\nEdge 3")
    move_forward(edge_length_m)
    if bumper_pressed(): # Check for bumper after movement
        print("Triangle aborted because bumper was pressed.")
        stop()
        return

    rotate_angle(120.0) # Rotate for next edge
    if bumper_pressed(): # If a bumper stopped movement during rotation
        print("Triangle aborted because bumper was pressed during rotation.")
        stop()
        return

    print("Triangle complete.")
    stop()

if __name__ == "__main__":
    while True:
        try:
            stop()
            time.sleep(1.0)
            drive_triangle(edge_length_m=2)
        except KeyboardInterrupt:
            print("Program interrupted. Stopping Robotino.")
            stop()
            # Ensure MQTT client loop is stopped gracefully
            try:
                client.loop_stop()
                client.disconnect()
                print("MQTT client disconnected.")
                sys.exit()
            except Exception as e:
                print(f"Error during MQTT client cleanup: {e}")
                sys.exit()