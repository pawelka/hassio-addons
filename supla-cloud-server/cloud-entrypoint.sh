#!/bin/sh
set -e

CONFIG_FILE=/data/options.json

echo "Setuping Supla Cloud"

mkdir -p /var/run/supla

rm -rf /etc/apache2/ssl
mkdir -p /data/ssl-cloud
ln -s /data/ssl-cloud /etc/apache2/ssl

if [ ! -f /etc/apache2/ssl/server.crt ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/apache2/ssl/server.key -out /etc/apache2/ssl/server.crt -subj "/C=PL/ST=SUPLA/L=SUPLA/O=SUPLA/CN=SUPLA"
fi

sed -i "s+database_host: supla-db+database_host: $(jq --raw-output '.mysql.host' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+database_port: ~+database_port: $(jq --raw-output '.mysql.port' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+database_name: supla+database_name: $(jq --raw-output '.mysql.database' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+database_user: supla+database_user: $(jq --raw-output '.mysql.username' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+database_password: ~+database_password: $(jq --raw-output '.mysql.password' $CONFIG_FILE)+g" app/config/parameters.yml

sed -i "s+secret: ThisTokenIsNotSoSecretChangeIt+secret: $(jq --raw-output '.supla.secret' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+supla_server: ~+supla_server: $(jq --raw-output '.supla.server' $CONFIG_FILE)+g" app/config/parameters.yml
#sed -E -i "s@supla_url: '(.+)'@supla_url: '$(jq --raw-output '.supla.url' $CONFIG_FILE)'@g" app/config/config.yml
sed -i "s+supla_protocol: https+supla_protocol: $(jq --raw-output '.supla.protocol' $CONFIG_FILE)+g" app/config/config.yml
sed -i "s+supla_server_socket: /supla-server/supla-server-ctrl.sock+supla_server_socket: /var/run/supla/supla-server-ctrl.sock+g" app/config/config.yml


sed -i "s+recaptcha_enabled: true+recaptcha_enabled: false+g" app/config/parameters.yml
sed -i "s+ewz_recaptcha_public_key: ~+ewz_recaptcha_public_key: ~+g" app/config/parameters.yml
sed -i "s+ewz_recaptcha_private_key: ~+ewz_recaptcha_private_key: ~+g" app/config/parameters.yml

sed -i "s+mailer_host: 127.0.0.1+mailer_host: $(jq --raw-output '.mailer.host' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+mailer_user: ~+mailer_user: $(jq --raw-output '.mailer.username' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+mailer_password: ~+mailer_password: $(jq --raw-output '.mailer.username' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+mailer_port: 465+mailer_port: $(jq --raw-output '.mailer.port' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+mailer_encryption: ssl+mailer_encryption: $(jq --raw-output '.mailer.encryption' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+mailer_from: ~+mailer_from: $(jq --raw-output '.mailer.from' $CONFIG_FILE)+g" app/config/parameters.yml
sed -i "s+admin_email: ~+admin_email: $(jq --raw-output '.mailer.admin_email' $CONFIG_FILE)+g" app/config/parameters.yml

sed -i "s+cors_allow_origin_regex: \[\]+cors_allow_origin_regex: \[local\]+g" app/config/parameters.yml
#sed -i "s+use_webpack_dev_server: false+use_webpack_dev_server: true+g" app/config/config.yml

rm -fr var/cache/*
php bin/console supla:initialize
php bin/console cache:warmup
chown -hR www-data:www-data var
php bin/console supla:create-confirmed-user $FIRST_USER_EMAIL $FIRST_USER_PASSWORD --no-interaction --if-not-exists

# first arg is `-f` or `--some-option`
if [ "${1#-}" != "$1" ]; then
	set -- apache2-foreground "$@"
fi

#########################################################################################

echo "Setuping Supla Server"

sed -i "s+MYSQL_HOST+$(jq --raw-output '.mysql.host' $CONFIG_FILE)+g" /etc/supla-server/supla.cfg
sed -i "s+MYSQL_PORT+$(jq --raw-output '.mysql.port' $CONFIG_FILE)+g" /etc/supla-server/supla.cfg
sed -i "s+MYSQL_DATABASE+$(jq --raw-output '.mysql.database' $CONFIG_FILE)+g" /etc/supla-server/supla.cfg
sed -i "s+MYSQL_USERNAME+$(jq --raw-output '.mysql.username' $CONFIG_FILE)+g" /etc/supla-server/supla.cfg
sed -i "s+MYSQL_PASSWORD+$(jq --raw-output '.mysql.password' $CONFIG_FILE)+g" /etc/supla-server/supla.cfg

mkdir -p /data/ssl-server
ln -s /data/ssl-server /etc/supla-server/ssl

if [ ! -f /etc/supla-server/ssl/cert.crt ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/supla-server/ssl/private.key -out /etc/supla-server/ssl/cert.crt -subj "/C=PL/ST=SUPLA/L=SUPLA/O=SUPLA/CN=SUPLA"
fi

chown -R www-data:www-data /var/run/supla
chown -R www-data:www-data /data/ssl-server
chown -R www-data:www-data /data/ssl-cloud

exec "$@"