#!/bin/bash

echo "run with sudo ./install.sh"

installfolder=" $(pwd)"
echo "$installfolder"

cat <<EOF > /etc/systemd/system/remoteconnect.service
[Unit]
Description=remoteconnect
After=multi-user.target

[Service]
Type=simple
ExecStart=$installfolder/remoteconnect.sh
User=pi
Restart=always
RestartSec=3
StandardInput=tty-force
TTYPath=/dev/tty3

[Install]
WantedBy=multi-user.target
EOF
cat <<EOF > /etc/systemd/system/doorlock.service
[Unit]
Description=doorlock
After=multi-user.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 $installfolder/doorlock.py
User=pi
Restart=always
RestartSec=3
StandardInput=tty-force
TTYPath=/dev/tty1

[Install]
WantedBy=multi-user.target
EOF
systemctl enable doorlock
systemctl enable remoteconnect
systemctl daemon-reload

