#!/usr/bin/env python3
import random
import subprocess
import sys

import yaml
from paho.mqtt import client as mqtt_client


def connect_mqtt(client_id, username, password, host):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker {host}")
        else:
            print(f"Failed to connect {host}, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    return client


def publish(client: mqtt_client, payload, topic: str, is_retained):
    result = client.publish(topic, payload, retain=is_retained)  # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Send `{payload}` to topic `{topic}`")
    else:
        print(f"Failed to send message to topic {topic}")


def read_file_or_none(path: str):
    # noinspection PyBroadException
    try:
        with open(path, mode="r") as f:
            lines = f.read()
            return lines
    except:
        return None


def run_command_or_none(commands):
    # noinspection PyBroadException
    try:
        result = subprocess.run(commands, stdout=subprocess.PIPE)
        if result.returncode != 0:
            return None
        return result.stdout
    except:
        return None


def run_collector(config):
    mqtt_host = config['mqtt']['host']
    mqtt_port = config['mqtt']['port']
    mqtt_user = config['mqtt'].get("user")
    mqtt_password = config['mqtt'].get("password")
    mqtt_topic_raw = config['mqtt']['topic']
    mqtt_client_id = f'python-info-collector-mqtt-{random.randint(0, 1000)}'

    host_id = config['host']['id']

    mqtt_topic_device_id = mqtt_topic_raw.format(host_id)

    mqtt_connection = connect_mqtt(mqtt_client_id, mqtt_user, mqtt_password, mqtt_host)
    try:
        mqtt_connection.connect(mqtt_host, mqtt_port)
    except Exception as e:
        print(f"Error making connection to {mqtt_host}:{mqtt_port}, {e}")
        exit(1)

    # Proc reader
    print("Proc reader")
    proc_entries = config.get("proc-reader") or {}
    for key in proc_entries:
        proc_entry_path = proc_entries[key]['path']
        proc_entry_should_separate = proc_entries[key].get("should_separate") or False
        proc_entry_separator = proc_entries[key].get("separator")
        file_content = read_file_or_none(proc_entry_path)
        if file_content is None:
            print("Skipping {} as file can't be read".format(proc_entry_path))
            continue
        if proc_entry_should_separate:
            split_result = file_content.split(proc_entry_separator)
            separator_mapping = proc_entries[key]["separator_mapping"]
            for separator_key in separator_mapping:
                position = proc_entries[key]["separator_mapping"][separator_key]['position']
                type_to_cast = proc_entries[key]["separator_mapping"][separator_key].get('type') or 'str'
                type_to_cast = eval(type_to_cast)
                proc_info_topic = "{}/{}/{}".format(mqtt_topic_device_id, key, separator_key)
                value = type_to_cast(split_result[position]) if position < len(split_result) else None
                publish(mqtt_connection, value, proc_info_topic, True)
                print()

        print(file_content)
    # Proc reader END
    mqtt_connection.disconnect()


def main(config_file_location: str):
    with open(config_file_location, "r") as stream:
        try:
            config = yaml.safe_load(stream)
            print(config)
            run_collector(config)
        except yaml.YAMLError as exc:
            print(exc)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Pass config file path as the only parameter to the application")
        print(f"Usage: '{sys.argv[0]} bridge_config.yml'")
        pass
    else:
        print(f"Starting bridge with `{sys.argv[1]}` config file")
        main(sys.argv[1])
