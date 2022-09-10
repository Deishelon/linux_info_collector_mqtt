# Linux Info Collector / MQTT
> Collect info from a linux PC/PI and report it back to MQTT (i.e. temperatures // avg load)

# Use
- Clone the repo
- cd into the cloned dir
- `python3 -m venv venv`
- `. venv/bin/activate`
- `pip install -r requirements.txt`
- `deactivate`
- Create yaml config file (see sample for reference)
- Do a sample to make sure all works (i.e `./bootstrap.sh ../linux_info_collector_mqtt.yml`)

# Cron job
- Open the cron editor: `crontab -e`
- Add the following line (ajust the paths to match your install) to run collection every 1 min:
```
* * * * * /home/pi/linux_info_collector_mqtt/bootstrap.sh /home/pi/linux_info_collector_mqtt.yml
```
- Save crontab and wait 1 min to see the new reports are coming from the device
- If something wrong with the cron job, you can start by debugging it with ` grep CRON /var/log/syslog`