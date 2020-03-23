# etrv2mqtt
MQTT bridge for Danfoss eTRV thermostats

## Installation
```sh
mkdir -p ~/venv/libetrv
virtualenv ~/venv/libetrv
git clone https://github.com/keton/etrv2mqtt.git
cd etrv2mqtt
~/venv/libetrv/bin/pip3 install -r requirements.txt
```

## Configuration

`config.json` example:
```json
{
    "$schema": "https://raw.githubusercontent.com/keton/etrv2mqtt/master/etrv2mqtt/schemas/config.schema.json",
    "mqtt": {
        "base_topic": "etrv",
        "server": "localhost",
        "port": 1883
    },
    "poll_interval": 20,
    "retry_limit": 5,
    "thermostats": [
        {
            "topic": "room",
            "address": "00:01:02:03:04:05",
            "secret_key": "01020304050607080910111213141516"
        },
        {
            "topic": "kitchen",
            "address": "02:03:04:03:04:05",
            "secret_key": "11121304050607080910111213141516"
        }
    ]
}
```

## Running
`~/venv/libetrv/bin/python3 etrv2mqtt.cli config.json`