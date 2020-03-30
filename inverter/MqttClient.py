import paho.mqtt.client as mqtt
import InverterMsg
import json

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
        self.inverter_sn = config['inverter']['sn']
        self.inverter_name = config['inverter']['name']
        self.inverter_manufacturer = config['inverter']['manufacturer']
        self.inverter_model = config['inverter']['model']

    def start(self):
        if not self.mqtt_enabled:
            return

        def on_mqtt_connect(client, userdata, flags, rc):
            # Subscribe to all topics in our namespace when we're connected. Send out
            # a message telling we're online
            self.log.info("[MqttClient] Connected with result code " + str(rc))
            self.configure_hass()

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
                topic=self.mqtt_topic+"/"+self.inverter_sn+"/state",
                payload=msg,
                qos=self.mqtt_qos,
                retain=self.mqtt_retain)

    def device_connected(self):
        self.log.info("[MqttClient] Sending device connected message")
        self.__mqttc.publish(
            topic=self.mqtt_topic+"/"+self.inverter_sn+"/state",
            payload="online",
            qos=self.mqtt_qos,
            retain=self.mqtt_retain)

    def device_disconnected(self):
        self.log.info("[MqttClient] Sending device disconnected message")
        self.__mqttc.publish(
            topic=self.mqtt_topic+"/"+self.inverter_sn+"/state",
            payload="offline",
            qos=self.mqtt_qos,
            retain=self.mqtt_retain)

    def hass_sensors_config(self):

        d = {}
        d["temp"] = {"device_class": "temperature", "unit_of_measurement": u"\N{DEGREE SIGN}C"}
        d["v_pv1"] = {"unit_of_measurement": "V"}
        d["v_pv2"] = {"unit_of_measurement": "V"}
        d["i_pv1"] = {"unit_of_measurement": "A"}
        d["i_pv2"] = {"unit_of_measurement": "A"}
        d["v_ac1"] = {"unit_of_measurement": "V"}
        d["v_ac2"] = {"unit_of_measurement": "V"}
        d["v_ac3"] = {"unit_of_measurement": "V"}
        d["i_ac1"] = {"unit_of_measurement": "A"}
        d["i_ac2"] = {"unit_of_measurement": "A"}
        d["i_ac3"] = {"unit_of_measurement": "A"}
        d["f_ac"] = {"unit_of_measurement": "Hz"}
        d["power"] = {"device_class": "power", "unit_of_measurement": "W"}
        d["e_today"] = {"unit_of_measurement": "kWh"}
        d["e_total"] = {"unit_of_measurement": "kWh"}

        for k in d:
            d[k]["device"] = {"identifiers": self.inverter_sn,
                              "name": self.inverter_name,
                              "manufacturer": self.inverter_manufacturer,
                              "model": self.inverter_model}
            d[k]["state_topic"] = self.mqtt_topic+"/"+self.inverter_sn+"/state"
            d[k]["unique_id"] = self.inverter_sn + "_" + k
            d[k]["value_template"] = "{{ value_json."+k+" }}"
            d[k]["name"] = k

        return d

    def configure_hass(self):
        self.log.info("[MqttClient] Configuring Home Assistant" )
        sensors = self.hass_sensors_config()
        for sensor in sensors:
            msg = json.dumps(sensors[sensor], ensure_ascii=False)
            self.log.debug("[MqttClient] Sensor config message to HA: %s" % msg)
            self.__mqttc.publish(
                        topic="homeassistant/sensor/"+self.inverter_name+"_"+sensor+"/config",
                        payload=msg,
                        qos=1,
                        retain=False)


if __name__ == '__main__':
    for k in InverterMsg.InverterMsg(None).dict().keys():
        print k
