# Delete Cisco AnyConnect Secure Mobility Client [Broken]
echo "Deleting Cisco AnyConnect Secure Mobility Client"
sudo rm -rf /opt/.cisco
sudo rm -rf /opt/cisco

bash ~/dev/letus-scraper/operation/install_vpn.sh