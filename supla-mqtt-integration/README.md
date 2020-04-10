# Home Assistant Add-on: Supla MQTT Integration

Addons integrate with Supla as a Client and forwards event to MQTT, which 
can be later processed by Home Assistance

Plugin base on experimental development from supla:
https://github.com/SUPLA/supla-core/tree/mqtt-experimental/supla-mqtt-client

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Find the "Supla MQTT Integration" add-on and click it.
3. Click on the "INSTALL" button.

## Configuration

### Add-on settings configuration:

Minimal:
```yaml
supla:
  host: 192.168.1.2
  email: yourmail@here.pl
mqtt:
  host: 192.168.1.3
```
Full:
```yaml
supla:
  port: 2016
  host: 192.168.1.2
  protocol_version: 10
  email: yourmail@here.pl
mqtt:
  host: 192.168.1.3
  port: 1883
  commands_file_path: config-supla/command.yaml
  states_file_path: config-supla/state.yaml
  client_name: supla_mqtt_client
  protocal_version: 3
  publish_supla_events: true
  username: 
  password:   
```
Minimal version shows required parameters.
Maximum version shows optional and also default values.

Description for the parameters can be found here:
https://github.com/SUPLA/supla-core/blob/mqtt-experimental/supla-mqtt-client/README.md

## Support

Got questions?

In case you've found a bug, please [open an issue on our GitHub][issue].

[issue]: https://github.com/pawelka/hassio-addons/issues
