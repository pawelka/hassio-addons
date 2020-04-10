#!/bin/bash

CONFIG_FILE=/data/options.json

cd /supla-mqtt-client

cat <<EOF > generated-config.yaml
mqtt:
  host: '$(jq --raw-output ".mqtt.host" $CONFIG_FILE)'
  port: $(jq --raw-output ".mqtt.port" $CONFIG_FILE || echo "1883")
  commands_file_path: '$(jq --raw-output ".mqtt.commands_file_path" $CONFIG_FILE || echo "config-supla/command.yaml")'
  states_file_path: '$(jq --raw-output ".mqtt.states_file_path" $CONFIG_FILE || echo "config-supla/state.yaml")'
  client_name: '$(jq --raw-output ".mqtt.client_name" $CONFIG_FILE || echo "supla_mqtt_client")'
  protocol_version: $(jq --raw-output ".mqtt.protocol_version" $CONFIG_FILE || echo "3")
  publish_supla_events: $(jq --raw-output ".mqtt.publish_supla_events" $CONFIG_FILE || echo "true")
  username: $(jq --raw-output ".mqtt.username" $CONFIG_FILE || echo "")
  password: $(jq --raw-output ".mqtt.password" $CONFIG_FILE || echo "")
supla:
  port: $(jq --raw-output ".supla.port" $CONFIG_FILE || echo "2016")
  host: '$(jq --raw-output ".supla.host" $CONFIG_FILE || echo "192.168.1.3")'
  protocol_version: $(jq --raw-output ".supla.protocol_version" $CONFIG_FILE || echo "10")
  email: '$(jq --raw-output ".supla.email" $CONFIG_FILE || echo "yourmail@here.com")'
EOF

./supla-mqtt-client -config generated-config.yaml
