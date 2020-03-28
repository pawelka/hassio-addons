import TcpProxy
import pprint
import InverterMsg
import FakeDNS
import ConfigParser
import os
import sys
import MqttClient
import logging


def create_callback(log, mqtt_client):
    def callback(data, src_address, src_port, dst_address, dst_port, direction):
        TcpProxy.TcpProxy.debug_callback(data, src_address, src_port, dst_address, dst_port, direction)
        if not direction and len(data) > 140:
            msg = InverterMsg.InverterMsg(data)
            pp = pprint.PrettyPrinter()
            log.debug("[Inverter] %s" % pp.pformat(msg.dict()))
            mqtt_client.publish(msg.dict())


def main():
    mydir = os.path.dirname(os.path.abspath(__file__))
    config = ConfigParser.RawConfigParser()
    # Load the setting file
    config.read([mydir + '/config-org.cfg', mydir + '/config.cfg'])

    logger = logging.getLogger("Inverter")
    file_handler = logging.FileHandler(config.get('log', 'log_filename'))
    console_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.getLevelName(config.get('log', 'log_level')))

    fake_dns = FakeDNS.FakeDNS(logger)
    mqtt_client = MqttClient.MqttClient(logger, config)
    tcp_proxy = TcpProxy.TcpProxy(config, logger, fake_dns, create_callback(logger, mqtt_client))
    try:
        mqtt_client.start()
        fake_dns.start()
        tcp_proxy.start()
    except KeyboardInterrupt:
        tcp_proxy.close()
        fake_dns.close()
        mqtt_client.close()


if __name__ == "__main__":
    main()
