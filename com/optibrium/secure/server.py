from com.optibrium.secure.message import Message
from com.optibrium.secure.backend import ObjectBackend
from com.optibrium.secure.backend import RedisBackend
from flask import Flask, request, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
from os import environ
import traceback

application = Flask(__name__)
limiter = Limiter(application, key_func=get_remote_address)

if 'DEBUG' not in environ:
    application.logger.disabled = True
    log = logging.getLogger('werkzeug')
    log.disabled = True

if 'REDIS' in environ:
    application.backend = RedisBackend(environ.get('REDIS'))
else:
    application.backend = ObjectBackend()


@application.route('/', methods=['GET'])
@limiter.limit('10/minute')
def index():
    if not len(list(request.args)):
        return render_template('index.tpl')
    else:
        message_id = list(request.args)[0]
        message = application.backend.get(message_id)
        return render_template('message.tpl', message=message)


@application.route('/', methods=['POST'])
@limiter.limit('10/minute')
def post():
    return application.backend.save(Message(request.json)), 201


@application.errorhandler(Exception)
def handle_error(error):

    if 'DEBUG' in environ:
        traceback.print_exc()

    return render_template('notfound.tpl'), 404
