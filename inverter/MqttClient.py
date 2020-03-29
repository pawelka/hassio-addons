import paho.mqtt.client as mqtt
import logging


class MqttClient(object):

    def __init__(self, log, config):
        self.log = log;
        self.mqtt_enabled = bool(config['mqtt']['mqtt_enabled'])
        self.mqtt_host = config['mqtt']['mqtt_host']
        self.mqtt_port = config['mqtt']['mqtt_port']
        self.mqtt_topic = config['mqtt']['mqtt_topic']
        self.mqtt_username = config['mqtt']['mqtt_username']
        self.mqtt_password = config['mqtt']['mqtt_password']
        self.mqtt_qos = int(config['mqtt']['mqtt_qos'])
        self.mqtt_retain = bool(config['mqtt']['mqtt_retain'])
        self.__mqttc = None

    def start(self):
        if not self.mqtt_enabled:
            return

        def on_mqtt_connect(client, userdata, flags, rc):
            # Subscribe to all topics in our namespace when we're connected. Send out
            # a message telling we're online
            self.log.info("[MqttClient] Connected with result code " + str(rc))

        def on_disconnect(client, userdata, rc):
            if rc != 0:
                self.log.warning("[MqttClient] Unexpected MQTT disconnection. Will auto-reconnect")

        mqttc = mqtt.Client("inverter", clean_session=False)
        if self.mqtt_username:
            mqttc.username_pw_set(self.mqtt_username, self.mqtt_password)
        mqttc.connect(self.mqtt_host, self.mqtt_port)
        mqttc.on_connect = on_mqtt_connect
        mqttc.on_disconnect = on_disconnect
        self.__mqttc = mqttc
        mqttc.loop_start()

    def close(self):
        self.__mqttc.disconnect()
        self.__mqttc.loop_stop()

    def publish(self, msg):
        self.__mqttc.publish(
                topic=self.mqtt_topic,
                payload=msg,
                qos=self.mqtt_qos,
                retain=self.mqtt_retain)
