from __future__ import division

from flask import Flask
from flask_restful import Resource, Api

import random
import time

app = Flask(__name__)
api = Api(app)


class Success(Resource):

    def get(self):
        time.sleep(random.random() / 10)  # sleep for up to 100 ms
        return "Success", 200

api.add_resource(Success, '/success')


class Random(Resource):

    def get(self):
        time.sleep(random.random() / 10)  # sleep for up to 100 ms
        status_codes = [200, 204, 400, 401, 403, 500, 501]
        return "A random response", random.choice(status_codes)

api.add_resource(Random, '/random')

if __name__ == '__main__':
    app.run(debug=True)
