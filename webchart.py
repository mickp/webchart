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
from flask import Flask, send_from_directory, jsonify, session

app = Flask(__name__)
app.secret_key = '/W3b/Ch4rt/S3cr3t!'

@app.after_request
def add_headers(r):
    """Add headers to prevent caching."""
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    return r

@app.route('/')
def index():
    return send_from_directory('./', 'webchart.html')

@app.route('/raw_data')
def raw_data():
    data = []
    with open(app.data_source, 'r') as source:
        return jsonify(source.readlines())


@app.route('/all_data')
def all_data():
    data = []
    with open(app.data_source, 'r') as source:
        for line in source:
            x, y = re.split('\s+', line.rstrip())
            data.append({'x': x, 'y':y})
        session['last_seek'] = source.tell()
    return jsonify(data)


@app.route('/poll')
def poll():
    if 'last_mtime' not in session:
        session['last_mtime'] = 0
    while (os.path.getmtime(app.data_source) == session['last_mtime']):
        time.sleep(1)
    session['last_mtime'] = os.path.getmtime(app.data_source)
    with open(app.data_source, 'r') as source:
        source.seek(session['last_seek'])
        data = []
        for line in source.readlines():
            if len(line) == 1: continue
            x, y = re.split('\s+', line.rstrip())
            data.append({'x': x, 'y':y})
        session['last_seek'] = source.tell()
    return jsonify(data)


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