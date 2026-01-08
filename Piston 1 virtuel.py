import paho.mqtt.client as paho
import time
import json

# --- Configuration MQTT ---
MQTT_BROKER_IP = "127.0.0.1"
MQTT_PORT = 1883

MQTT_COMMAND_PISTON1_TOPIC = "piston1/command"
MQTT_FINISH_PISTON1_TOPIC = "piston1/finish"

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Piston 1: Connecté au broker MQTT!")
        client.subscribe(MQTT_COMMAND_PISTON1_TOPIC)
    else:
        print(f"Piston 1: Échec de la connexion, code de retour: {rc}\n")

def on_message(client, userdata, msg):
    print(f"Piston 1: Message reçu sur topic '{msg.topic}': {msg.payload.decode()}")
    if msg.topic == MQTT_COMMAND_PISTON1_TOPIC:
        print("Piston 1: Démarrage du moteur du Piston 1...")
        # Simule l'action du piston
        time.sleep(3) # Attendre 3 secondes pour simuler le mouvement
        print("Piston 1: Moteur du Piston 1 terminé. Publication du message 'finish'.")
        client.publish(MQTT_FINISH_PISTON1_TOPIC, "continue")

client_piston1 = paho.Client(paho.CallbackAPIVersion.VERSION2)
client_piston1.on_connect = on_connect
client_piston1.on_message = on_message

try:
    print(f"Piston 1: Tentative de connexion au broker MQTT à {MQTT_BROKER_IP}:{MQTT_PORT}...")
    client_piston1.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
    client_piston1.loop_forever() # Boucle infinie pour rester connecté et recevoir les messages
except Exception as e:
    print(f"Piston 1: Erreur de connexion au broker MQTT: {e}")
