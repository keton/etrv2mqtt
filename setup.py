import setuptools

setuptools.setup(
    name="etrv2mqtt",
    version="0.0.2",
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
    install_requires=('jsonschema', 'loguru', 'paho-mqtt', 'libetrv @ git+https://github.com/AdamStrojek/libetrv.git@902495fbfeac74ebae908dab373b962eec6a92bc#egg=libetrv',),
    setup_requires=('wheel'),
)
