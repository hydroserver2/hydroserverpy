# TODO: The user needs to be able to configure their own

WEEDER_PROTOCOLS = {
    "auto_zero": {
        "command": "Z",
        "wait": 2,
        "response_format": "echo",
    },
    "single_ended_voltages": {
        "command": "S",
        "wait": 3,
        "response_format": "array",
    },
}

SDI12_PROTOCOLS = {
    "continuous_measurements": {
        "command": "R0!",
        "wait": 5,
        "response_format": "signed_numbers",
        # Responds with "a+X.XX+NNNN<cr><lf>" where:
        # +X.XX = Current position (stage), in user programmable units
        # +NNNN = Current position (raw counts), in raw position counts
    },
    "send_data": {
        "command": "D0!",
        "wait": 5,
        "response_format": "signed_numbers",
    },
    "send_identification": {
        "command": "I!",
        "wait": 5,
        "response_format": "identification",
        "token_format": "allccccccccmmmmmmvvvxxxxxxxxxxxxx",
    },
    "start_concurrent_measurement": {
        "type": "voltage_address",
        "command": "C!",
        "wait": 2,
        "response_format": "token",
        "token_format": "atttnn",
    },
    "start_measurement": {
        "command": "M!",
        "wait": 5,
        "response_format": "token",
        "token_format": "atttn",
    },
}

CUSTOM_PROTOCOLS = {
    "IKF_custom": {
        "command": "RA",
        "wait": 5,
        "response_format": "number",
    },
}

TCP_PROTOCOLS = {**WEEDER_PROTOCOLS, **SDI12_PROTOCOLS, **CUSTOM_PROTOCOLS}
