# unzip tar.gz file to ~/setting/cisco
echo "Unzipping tar.gz file to ~/setting/cisco"
tar zxf /mnt/c/users/rtkfi/dev/bin/anyconnect-linux64-4.10.06090-predeploy-k9.tar.gz -C ~/setting/cisco/

# Install VPN
echo "Installing VPN"
cd ~/setting/cisco/anyconnect-linux64-4.10.06090/vpn/
yes | sudo ~/setting/cisco/anyconnect-linux64-4.10.06090/vpn/vpn_install.sh
