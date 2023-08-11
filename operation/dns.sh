#!/bin/bash
sudo unlink /etc/resolv.conf
wslIp=$(ipconfig.exe | awk '/Ethernet adapter vEthernet \(WSL\)/ {f=1} f==1 && /IPv4 Address/ {print $NF; exit}')
echo "nameserver $wslIp" | sudo tee /mnt/wsl/resolv.conf >/dev/null
sudo ln -sf /mnt/wsl/resolv.conf /etc/resolv.conf
