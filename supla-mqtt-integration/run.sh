#!/bin/bash

CONFIG_FILE=/data/options.json

cd /supla-mqtt-client

cat <<EOF > generated-config.yaml
mqtt:
  host: '$(jq --raw-output '.mqtt.host' $CONFIG_FILE)'
  port: $(jq --raw-output '.mqtt.port // "1883"' $CONFIG_FILE)
  commands_file_path: '$(jq --raw-output '.mqtt.commands_file_path // "config-supla/command.yaml"' $CONFIG_FILE)'
  states_file_path: '$(jq --raw-output '.mqtt.states_file_path // "config-supla/state.yaml"' $CONFIG_FILE)'
  client_name: '$(jq --raw-output '.mqtt.client_name // "supla_mqtt_client"' $CONFIG_FILE)'
  protocol_version: $(jq --raw-output '.mqtt.protocol_version // "3"' $CONFIG_FILE)
  publish_supla_events: $(jq --raw-output '.mqtt.publish_supla_events // "true"' $CONFIG_FILE)
  username: $(jq --raw-output '.mqtt.username // ""' $CONFIG_FILE)
  password: $(jq --raw-output '.mqtt.password // ""' $CONFIG_FILE)
supla:
  port: $(jq --raw-output '.supla.port // "2016"' $CONFIG_FILE)
  host: '$(jq --raw-output '.supla.host' $CONFIG_FILE)'
  protocol_version: $(jq --raw-output '.supla.protocol_version // "10"' $CONFIG_FILE)
  email: '$(jq --raw-output '.supla.email' $CONFIG_FILE)'
EOF

if [ ! -d "/data/supla-mqtt-client-data" ]; then  
  mkdir /data/supla-mqtt-client-data
fi

ln -s /data/supla-mqtt-client-data /root/.supla-mqtt-client

./supla-mqtt-client -config generated-config.yaml
