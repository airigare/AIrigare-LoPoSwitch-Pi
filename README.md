# AIrigare-LoPoSwitch-Pi

MQTT Client installed on Raspberrypi to controll AIrigare Low Power Switch over BLE

## Install the Service

```bash
sudo cp airigareMQTT.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/airigareMQTT.service
chmod +x /home/pi/AIrigare-LoPoSwitch-Pi/airigareMQTTclient.py
sudo systemctl daemon-reload
sudo systemctl enable airigareMQTT.service
sudo systemctl start airigareMQTT.service
```

## Some Commands to run the Service

```bash
# Check status
sudo systemctl status airigareMQTT.service
 
# Start service
sudo systemctl start airigareMQTT.service
 
# Stop service
sudo systemctl stop airigareMQTT.service

# Restart service
sudo systemctl restart airigareMQTT.service

# Check service's log
sudo journalctl -f -u airigareMQTT.service
```
