#!/bin/bash

# backup dns settings
bash ~/dev/letus-scraper/operation/backup_dns_setting.sh

# reinstall vpn
bash ~/dev/letus-scraper/operation/reinstall_vpn.sh

# load env
source ~/dev/letus-scraper/.env

# connect vpn
/opt/cisco/anyconnect/bin/vpn -s connect $TUS_DOMAIN <<EOF
$TUS_USER
$TUS_PASSWORD
EOF
