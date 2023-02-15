from mqtt.WatchMileMQTT import WatchMileMQTT
from mqtt.Login_MQTT import login_mqtt
from mqtt.Service_MQTT import service_mqtt, mqtt_data_client

logins = login_mqtt()
service_mqtt_client = mqtt_data_client(logins)
client_id = logins.clientID
topic_class = 'log'
service_topic = "wlogs/device/service/" + client_id + "/" + topic_class
# wlogs/device/service/{client_id}/v1/api/skv1/log
service_mqtt_client.subscribe(service_topic)
