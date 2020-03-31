[Unit]
Description=The CIS Ops Challenge Web Server (http)
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/processor/mlai
ExecStart=/usr/bin/python3 /processor/mlai/application.py

[Install]
WantedBy=multi-user.target