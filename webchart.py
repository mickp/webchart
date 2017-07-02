#!/usr/bin/python
# -*- coding: utf-8
#
# Copyright 2017 Mick Phillips (mick.phillips@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import time
from flask import Flask, send_from_directory, jsonify

last_time = 0

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('./', 'webchart.html')

@app.route('/all_data')
def all_data():
    data = []
    with open(app.data_source, 'r') as source:
        for line in source:
            x, y = re.split('\s+', line.rstrip())
            data.append({'x': x, 'y':y})
    return jsonify(data)


@app.route('/poll')
def poll():
    global last_time
    while (os.path.getmtime(app.data_source) == last_time):
        time.sleep(0.01)
    last_time = os.path.getmtime(app.data_source)
    with open(app.data_source, 'r') as source:
        source.seek(0,2)
        end = source.tell()
        if end < 1024:
            source.seek(0)
        else:
            source.seek(end - 512)
        line = source.readlines()[-1]
    x, y = re.split('\s+', line.rstrip())
    return jsonify({'x': x, 'y': y})


@app.route('/<path:path>')
def send_js(path):
    return send_from_directory('./', path)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Watch a file and plot data as it is written.')
    parser.add_argument('data_source', metavar='file', type=str, nargs='?',
                            help='file to watch')
    parser.add_argument('--public', action='store_const', dest='host',
                            default='127.0.0.1', const='0.0.0.0',
                            help='listen on public interfaces')
    args = parser.parse_args()
    print(args)
    app.data_source = args.data_source
    app.run(threaded=True, host=args.host)