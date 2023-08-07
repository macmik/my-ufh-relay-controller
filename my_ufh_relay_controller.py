import sys
import logging
from os import environ

import RPi.GPIO as GPIO
from flask import Flask, jsonify, request


def setup_logging():
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    log_level = environ.get("LOG_LVL", "dump")
    if log_level == "dump":
        level = logging.DEBUG
    elif log_level == "info":
        level = logging.INFO
    elif log_level == "error":
        level = logging.ERROR
    elif log_level == "warning":
        level = logging.WARNING
    else:
        logging.error('"%s" is not correct log level', log_level)
        sys.exit(1)
    if getattr(setup_logging, "_already_set_up", False):
        logging.warning("Logging already set up")
    else:
        logging.basicConfig(format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", level=level)
        setup_logging._already_set_up = True


def create_app():
    app = Flask(__name__, static_folder='templates')
    GPIO.setmode(GPIO.BOARD)

    setup_logging()

    return app


app = create_app()


@app.route('/set', methods=['POST'])
def set_gpio_state():
    try:
        gpio = _get_int('gpio')
        value = _get_int('value')
        GPIO.setup(gpio, GPIO.OUT)
        GPIO.output(gpio, GPIO.HIGH if value else GPIO.LOW)
    except Exception as e:
        return str(e), 400

    return 'ok', 200


@app.route('/get', methods=['GET'])
def get_gpio_state():
    try:
        gpio = _get_int('gpio')
        GPIO.setup(gpio, GPIO.OUT)
        return jsonify({'state': GPIO.input(gpio)})
    except Exception as e:
        return str(e), 400


def _get_int(key):
    return int(request.args.to_dict()[key])


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8002)
