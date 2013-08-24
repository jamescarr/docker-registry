
import logging
import datetime
from flask import Flask

import config
from toolkit import response, gen_random_string


VERSION = '0.5.8'
app = Flask('docker-registry')
cfg = config.load()
loglevel = getattr(logging, cfg.get('loglevel', 'INFO').upper())
logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    level=loglevel)


@app.route('/_ping')
@app.route('/v1/_ping')
def ping():
    return response()


@app.route('/')
def root():
    return response('docker-registry server ({0})'.format(cfg.flavor))


@app.after_request
def after_request(response):
    response.headers['X-Docker-Registry-Version'] = VERSION
    response.headers['X-Docker-Registry-Config'] = cfg.flavor
    return response


def init():
    # Configure the secret key
    if cfg.secret_key:
        Flask.secret_key = cfg.secret_key
    else:
        Flask.secret_key = gen_random_string(64)
    # Set the session duration time to 1 hour
    Flask.permanent_session_lifetime = datetime.timedelta(seconds=3600)
    # Configure the email exceptions
    info = cfg.email_exceptions
    if info:
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler(mailhost=info['smtp_host'],
                                   fromaddr=info['from_addr'],
                                   toaddrs=[info['to_addr']],
                                   subject='Docker registry exception',
                                   credentials=(info['smtp_login'],
                                                info['smtp_password']))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


init()
