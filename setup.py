import setuptools

setuptools.setup(
    name="etrv2mqtt",
    version="1.0.0",
    author="Michał Lower",
    author_email="keton22@gmail.com",
    description="MQTT bridge for Danfoss Eco BLE thermostats and Home Assistant",
    url="https://github.com/keton/etrv2mqtt",
    packages=['etrv2mqtt', 'etrv2mqtt.schemas'],
    package_data={
        "etrv2mqtt.schemas": ["*.schema.json"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    entry_points={
        "console_scripts": [
            "etrv2mqtt = etrv2mqtt.cli:entrypoint",
        ]
    },
    install_requires=('jsonschema', 'loguru', 'paho-mqtt', 'schedule',
                      'libetrv',),
    setup_requires=('wheel'),
)
