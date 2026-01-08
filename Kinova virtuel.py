import paho.mqtt.client as paho
import time

# --- MQTT Configuration ---
MQTT_BROKER_IP = "127.0.0.1"
MQTT_PORT = 1883
MQTT_COMMAND_ROBOTINO_TOPIC = "robotino/command"

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Connecté au broker MQTT!")
    else:
        print(f"Échec de la connexion, code de retour: {rc}\n")

def on_publish(client, userdata, mid, rc, properties):
    print(f"Message {mid} publié.")

client = paho.Client(paho.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_publish = on_publish

try:
    print(f"Tentative de connexion au broker MQTT à {MQTT_BROKER_IP}:{MQTT_PORT}...")
    client.connect(MQTT_BROKER_IP, MQTT_PORT, 60)
    client.loop_start() # Démarrer la boucle en arrière-plan

    # Attendre un court instant pour que la connexion s'établisse
    time.sleep(1)

    # Publier le message 'continue'
    message = "continue"
    client.publish(MQTT_COMMAND_ROBOTINO_TOPIC, message)
    print(f"Message '{message}' publié sur le topic '{MQTT_COMMAND_ROBOTINO_TOPIC}'.")

    # Attendre un court instant avant de déconnecter
    time.sleep(0.5)

    client.loop_stop() # Arrêter la boucle
    client.disconnect()
    print("Déconnecté du broker MQTT.")

except Exception as e:
    print(f"Erreur de connexion ou de publication MQTT: {e}")