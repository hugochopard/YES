import paho.mqtt.client as paho
import time
import json

# --- Configuration MQTT ---
MQTT_BROKER_IP = "127.0.0.1"
MQTT_PORT = 1883

MQTT_COMMAND_PISTON2_TOPIC = "piston2/command"
MQTT_FINISH_PISTON2_TOPIC = "piston2/finish"

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Piston 2: Connecté au broker MQTT!")
        client.subscribe(MQTT_COMMAND_PISTON2_TOPIC)
    else:
        print(f"Piston 2: Échec de la connexion, code de retour: {rc}\n")

def on_message(client, userdata, msg):
    print(f"Piston 2: Message reçu sur topic '{msg.topic}': {msg.payload.decode()}")
    if msg.topic == MQTT_COMMAND_PISTON2_TOPIC:
        print("Piston 2: Démarrage du moteur du Piston 2...")
        # Simule l'action du piston
        time.sleep(3) # Attendre 3 secondes pour simuler le mouvement
        print("Piston 2: Moteur du Piston 2 terminé. Publication du message 'finish'.")
        client.publish(MQTT_FINISH_PISTON2_TOPIC, "continue")

client_piston2 = paho.Client(paho.CallbackAPIVersion.VERSION2)
client_piston2.on_connect = on_connect
client_piston2.on_message = on_message

try:
    print(f"Piston 2: Tentative de connexion au broker MQTT à {MQTT_BROKER_IP}:{MQTT_PORT}...")
    client_piston2.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
    client_piston2.loop_forever() # Boucle infinie pour rester connecté et recevoir les messages
except Exception as e:
    print(f"Piston 2: Erreur de connexion au broker MQTT: {e}")
