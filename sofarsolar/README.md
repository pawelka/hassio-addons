# Home Assistant Add-on: SofarSolar sensors

SofarSolar WiFi integration with Home Assistant

## About

SofarSolar WiFi stick is used to upload inverter data to solarmanpv cloud. WiFi kit in latest 
versions uses V5 protocol which is closed. Add-on sniff traffic and decode main package with 
inverter data. Add-on only require to configure inverter WiFi setting to redirect DNS traffic 
to add-on. After that FakeDNS return add-on IP and expose proxy to solarmanpv cloud. During proxing
sniff main data package and result send to MQTT.

On top of above add-on integrate with HA MQTT discovery feature and automatically adds device and
and sensors.

![Device][device]

## Features

- Discovery device and sensors in HA (MQTT discovery)
- Support online/offline data for current data
- Sniff iGen V5 protocol and decode main data
- Use latest DNS resolution as target server (TODO: ?consider to do round robin for all addresses)

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Find the "SofarSolar" add-on and click it.
3. Click on the "INSTALL" button.

## Configuration

### Add-on settings configuration:

Minimal:
```yaml
inverter:
  sn: SF4ES00XXXXXXX
fakedns:
  target_ip: 192.168.1.2
mqtt:
  mqtt_host: 192.168.1.3
  mqtt_port: 1883
```
Full:
```yaml
inverter:
  name: Inverter
  sn: SF4ES00XXXXXXX
  manufacturer: SofarSolar
  model: 8.8KTL-X
  idle_time: 660
log:
  log_level: INFO
fakedns:
  initial_domain: data1.solarmanpv.com
  target_ip: 192.168.1.2
mqtt:
  mqtt_host: 192.168.1.3
  mqtt_port: 1883
  mqtt_topic: inverter
  mqtt_username: 'userhere'
  mqtt_password: 'passwordhere'
  mqtt_qos: 0
  mqtt_retain: false
```

#### Option: `inverter.name` (optional)
Name of the device in HA.

*Default: Inverter*

#### Option: `inverter.sn` (required)
Serial number of your inverter. It's only used to properly setup sensors in HA and for MQTT topics. Fake SN will also work.

#### Option: `inverter.manufacturer` (optional)
Manufacturer of the device in HA.

*Default: SofarSolar*

#### Option: `inverter.model` (optional)
Model of the device in HA.

*Default: KTL-X*

#### Option: `inverter.idle_time` (optional)
Time in seconds after which HA should receive offline message to sensors.
Normally WiFi Logger send status every 5 min, but configured 11 min restarts support.

*Default: 660*

#### Option: `log.log_level` (optional)
Logging level: ERROR, WARNING, INFO, DEBUG

*Default: INFO*

#### Option: `fakedns.initial_domain` (optional)
Initial domain which should be used for connection to the cloud. In case of add-on
restart WiFi Logger doesn't resolve IP again, but trying to connect, so domain
has to be known just after restart.

*Default: data1.solarmanpv.com*

#### Option: `fakedns.target_ip` (required)
IP address of you HASS.io installation where add-on is installed. IP is return
during DNS resolution for inverter.

#### Option: `mqtt.mqtt_host` (required)
MQTT broker host.

#### Option: `mqtt.mqtt_port` (required)
MQTT broker port.

#### Option: `mqtt.mqtt_topic` (optional)
MQTT topic prefix. 

State topic pattern: <mqtt.mqtt_topic>/<inverter.sn>/state
Availability topic pattern: <mqtt.mqtt_topic>/<inverter.sn>/availability

*Default: inverter*

#### Option: `mqtt.mqtt_username` (optional)
Username to MQTT broker

*Default: ''*

#### Option: `mqtt.mqtt_password` (optional)
Password to MQTT broker

*Default: ''*

#### Option: `mqtt.mqtt_qos` (optional)
MQTT message qos.

*Default: 0*

#### Option: `mqtt.mqtt_retain` (optional)
MQTT message retain.

*Default: false*

### WiFi Logger target port
If you need to change proxy server port, you should change mapping in add-on. Default is 10000:10000.

### Inverter configuration
You need to conifgure DNS server pointing to IP. The easiest way is to:
1. Obtain IP
1. Save configuration and enter to configuration again
1. Disable IP obtaining
1. Change DNS to you add-on location (you cannot change DNS when obtained IP)

![Inverter][inverter]

## Example dashboard

![Dashboard][dashboard]

## Known issues and limitations

- Add-on expose port 53 for DNS. There can be a conflict with some deployment on HA. The one which expose DNS port 
(like Ubuntu). In that  case you need to disable system DNS if you can if not. You can install it on different machine 
in pure docker.

## Support

Got questions?

In case you've found a bug, please [open an issue on our GitHub][issue].

[issue]: https://github.com/pawelka/hassio-addons/issues
[device]: https://raw.githubusercontent.com/pawelka/hassio-addons/master/sofarsolar/images/device.png
[inverter]: https://raw.githubusercontent.com/pawelka/hassio-addons/master/sofarsolar/images/inverter.png
[dashboard]: https://raw.githubusercontent.com/pawelka/hassio-addons/master/sofarsolar/images/dashboard.png