import paho.mqtt.client as mqtt
import InverterMsg
import json
import time
import threading

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
        self.idle_time = int(config['inverter']['idle_time'])
        self.active = False
        self.last_message_time = None
        self.ha_configured = False
        self.check_loop = False

    def start(self):
        if not self.mqtt_enabled:
            return

        def on_mqtt_connect(client, userdata, flags, rc):
            # Subscribe to all topics in our namespace when we're connected. Send out
            # a message telling we're online
            self.log.info("[MqttClient] Connected with result code " + str(rc))
            if not self.ha_configured:
                self.configure_hass(True)
                self.configure_hass(False)
                self.ha_configured = True

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

        self.check_loop = True
        at = threading.Thread(target=self.activity_loop)
        at.start()

    def activity_loop(self):
        while self.check_loop:
            try:
                self.log.debug("Checking activity")
                if self.active and self.last_message_time is not None \
                        and (time.time() - self.last_message_time) >= self.idle_time:
                    self.device_deactivated()
                time.sleep(1)
            except Exception as ex:
                self.log.error(ex)

    def close(self):
        self.__mqttc.disconnect()
        self.__mqttc.loop_stop()
        self.check_loop = False

    def publish(self, msg):
        if not self.active:
            self.device_activated()
        self.last_message_time = time.time()
        self.__mqttc.publish(
                topic=self.mqtt_topic+"/"+self.inverter_sn+"/state",
                payload=msg,
                qos=self.mqtt_qos,
                retain=self.mqtt_retain)

    def device_activated(self):
        self.log.info("[MqttClient] Sending device connected message")
        self.active = True
        self.__mqttc.publish(
            topic=self.mqtt_topic+"/"+self.inverter_sn+"/availability",
            payload="online",
            qos=1,
            retain=False)

    def device_deactivated(self):
        self.log.info("[MqttClient] Sending device disconnected message")
        self.active = False
        self.__mqttc.publish(
            topic=self.mqtt_topic+"/"+self.inverter_sn+"/availability",
            payload="offline",
            qos=1,
            retain=False)

    def hass_sensors_config(self, sensor_name_prefix):

        d = {}
        d["temp"] = {"unit_of_measurement": u"\N{DEGREE SIGN}C"}
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
        d["power"] = {"unit_of_measurement": "W"}
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
            if sensor_name_prefix:
                d[k]["name"] = self.inverter_sn + "_" + k
            else:
                d[k]["name"] = k
            if not k.startswith("e_"):
                d[k]["availability_topic"] = self.mqtt_topic+"/"+self.inverter_sn+"/availability"

        return d

    def configure_hass(self, sensor_name_prefix):
        self.log.info("[MqttClient] Configuring Home Assistant" )
        sensors = self.hass_sensors_config(sensor_name_prefix)
        for sensor in sensors:
            msg = json.dumps(sensors[sensor], ensure_ascii=False)
            self.log.debug("[MqttClient] Sensor config message to HA: %s" % msg)
            self.__mqttc.publish(
                        topic="homeassistant/sensor/"+self.inverter_sn+"_"+sensor+"/config",
                        payload=msg,
                        qos=2,
                        retain=False)
            time.sleep(0.1)


if __name__ == '__main__':
    for k in InverterMsg.InverterMsg(None).dict().keys():
        print k
