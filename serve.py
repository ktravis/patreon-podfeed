#!/usr/bin/env python
import os
import glob
import datetime
from mutagen import id3

from flask import Flask, request, url_for, send_from_directory, Response
from werkzeug.contrib.atom import AtomFeed
from functools import wraps

app = Flask(__name__)

FILE_DIR = os.path.join(app.root_path, 'podcasts')
app.config['UPLOAD_FOLDER'] = FILE_DIR

ADMIN_USER = ''
ADMIN_PASS = ''

def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/files/<filename>')
@requires_auth
def dl(filename):
    filename = filename.replace('/', '')
    return send_from_directory(directory=FILE_DIR, filename=filename)

@app.route('/entries/<filename>')
@requires_auth
def entry(filename):
    return filename

@app.route('/feed.atom')
@requires_auth
def atom_feed():
    processed = []
    album = None
    for f in glob.glob('{0}/*.mp3'.format(FILE_DIR)):
        y = id3.ID3(f)
        fbase = os.path.basename(f)
        if album is None:
            album = y.get('TALB')
        title = y.get('TIT2')
        dt = datetime.datetime.fromtimestamp(os.stat(f).st_mtime)
        props = {
            'publisher': y.get('TPUB'),
            'updated': dt,
            'published': dt,
            'genre': y.get('TCON'),
            'author': [y.get('TCOP')],
            'copyright': y.get('TPE1'),
            'home_url': y.get('WXXX'),
            'summary': y.get('COMM::eng'),
            'pic': y.get('APIC:'),
            'content_type': 'mp3',
            'id': fbase,
            'links': [
                {
                    'href': url_for('entry', filename=fbase)
                },
                {
                    'rel': 'enclosure',
                    'type': 'audio/mpeg',
                    'title': 'MP3',
                    'host': request.url_root,
                    'href': request.url_root+url_for('dl', filename=fbase),
                    'length': os.stat(f).st_size
                }
            ]
        }
        processed.append((title, props))
    feed = AtomFeed('{0} (Patreon Episodes)'.format(album), author='me',
            feed_url=request.url_root, url=request.url_root+'feed.atom')
    for title, props in processed:
        feed.add(title, title, **props) 
    return feed.get_response()

app.run(port=5000)
