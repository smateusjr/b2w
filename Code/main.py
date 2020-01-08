import argparse
import os
import importlib
import signal
import redis
import sys
import configobj

# Tornado
import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.escape
import tornado.process

# deamon
import services.daemon as daemon
from multiprocessing import Lock

# Swagger
from docs.compile_json import yaml_to_json

# Log Class
import services.logs as logs

config_mutex = Lock()
PIDFILE = 'planet.pid'
ROOTPATH = os.path.dirname(os.path.abspath(__file__))
CONFIGPATH = '%s/configs' % (ROOTPATH)
APPFOLDER = '%s/application/' % ROOTPATH


def get_configs():

    if os.path.isfile('%s/config.ini' % CONFIGPATH):
        config = configobj.ConfigObj('%s/config.ini' % CONFIGPATH)
    else:
        config = None
        print('File config.ini not found.')

    if os.path.isfile('%s/server.ini' % CONFIGPATH):
        server_config = configobj.ConfigObj('%s/server.ini' % CONFIGPATH)
    else:
        server_config = None
        print('File server.ini not found.')

    return config, server_config


def sig_handler_reload(sig, frame):
    instance = tornado.ioloop.IOLoop.instance()

    with config_mutex:

        config, server_config = get_configs()
        if config:
            instance.config = config

        if server_config:
            instance.server_config = server_config


def sig_handler(sig, frame):
    tornado.ioloop.IOLoop.instance().add_callback(shutdown)


def shutdown():
    server.stop()
    tornado.ioloop.IOLoop().instance().add_callback(
        tornado.ioloop.IOLoop().instance().stop
    )
    tornado.ioloop.IOLoop().instance().add_callback_from_signal(
        tornado.ioloop.IOLoop().instance().stop
    )
    try:
        os.remove('%s/%s' % (ROOTPATH, PIDFILE))
    except OSError:
        pass


def send_signal(signal):
    try:
        with open('%s/%s' % (ROOTPATH, PIDFILE)) as f:
            pid = int(f.read().strip())

        pgid = os.getpgid(pid)
        os.killpg(pgid, signal)
    except Exception as e:
        sys.exit(1)


def save_pid():
    with open('%s/%s' % (ROOTPATH, PIDFILE), 'w') as f:
        f.write(str(os.getpid()))


def main(args):

    global server

    # signal
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGHUP, sig_handler_reload)

    # Get configs
    config, server_config = get_configs()
    if not config or not server_config:
        sys.exit(1)

    # Utils
    utils = importlib.import_module('utils.%s.utils' % (config['versions']['utils']))

    # token redis
    try:
        redis.StrictRedis(
            host=server_config['redis_token']['host'],
            port=server_config['redis_token']['port'],
            db=server_config['redis_token']['db']
        ).ping()
    except Exception as e:
        print(e)
        print('Failed to connect to Redis server...')
        sys.exit(1)

    redis_db_token = redis.StrictRedis(**dict(server_config['redis_token']))
    redis_db_swapi = redis.StrictRedis(**dict(server_config['redis_swapi']))

    # Lista com as urls
    URLS = [
        (r'/favicon.ico',
         tornado.web.StaticFileHandler,
         {'path': '/templates/static/'}),
    ]

    # configs para o tornado
    settings = dict(
        config=config,
        server_config=server_config,
        redis_db_token=redis_db_token,
        redis_db_swapi=redis_db_swapi,
        utils=utils,
        template_path=os.path.join(ROOTPATH, 'templates'),
        static_path=os.path.join(ROOTPATH, 'templates/static'),
        root_path=ROOTPATH,
        test_mode=args.test,
        logs=logs.LogClass(
            server_config['tornado']['log_path'] if 'log_path' in\
            server_config['tornado'].keys() and\
            server_config['tornado']['log_path'] else '%s/logs' % (
                ROOTPATH
            ),
            utils.str_to_boolean(
                server_config['tornado']['propagate']) if 'propagate'\
                in server_config['tornado'].keys() and\
                server_config['tornado']['propagate'] else False
        )
    )

    # Urls do docs - docs
    if args.docs:

        # Cria os json para o docs
        os.system('rm -rf docs/json-generated')

        docs_dir = {
            'yaml_dir': os.path.join(ROOTPATH, 'docs', 'yaml'),
            'json_dir': os.path.join(ROOTPATH, 'docs', 'json-generated'),
            'browser_dir': os.path.join(ROOTPATH, 'docs', 'browser')
        }

        yaml_to_json(
            docs_dir['yaml_dir'],
            docs_dir['json_dir'],
            '',
            '%s' % (server_config['docs']['url']), config['http_codes']
        )

        for list_dir in os.listdir(docs_dir['json_dir']):
            if os.path.isdir(os.path.join(docs_dir['json_dir'], list_dir)):
                URLS += [(
                    r'/apiDoc/%s(.*)' % (list_dir),
                    tornado.web.StaticFileHandler,
                    dict(
                        path='%s/%s/docs.json' % (docs_dir['json_dir'],
                        list_dir)
                    )
                )]
        # atualiza a rota para o docs
        URLS += [
            (r'/apiDoc/(.*)',
             tornado.web.StaticFileHandler,
             dict(path='%s/docs.json' % (docs_dir['json_dir']))
             ),
            (r'/',
             tornado.web.RedirectHandler, dict(url='/docs/browser/index.html')
             )
        ]

        # settings para o docs
        settings.update({
            'static_path': docs_dir['browser_dir'],
            'static_url_prefix': '/docs/browser/'
        })

    for version in os.listdir(APPFOLDER):
        if os.path.isdir(os.path.join(APPFOLDER, version)):
            URLS += [
                (r'/%s/planet/?' % version, getattr(importlib.import_module(
                    'application.%s.planetHandler.planetHandler' % version),
                    'PlanetHandler')),
                (r'/%s/planet/authorization/?' % version, getattr(
                    importlib.import_module(
                        'application.%s.authorizationHandler.authorizationHandler' % version),
                    'AuthorizationHandler')),
                (r'/%s/planet/token/?' % version, getattr(
                    importlib.import_module(
                        'application.%s.tokenHandler.tokenHandler' % version),
                    'TokenHandler')),
            ]

    app = tornado.web.Application(URLS, **settings)
    server = tornado.httpserver.HTTPServer(app, xheaders=True)
    try:
        server.bind(
            int(
                server_config['tornado']['port']
            ) if not args.port else args.port
        )
        if args.test:
            return server

        server.start(
            int(
                server_config['tornado']['instances']
            ) if not args.instances else args.instances)
        save_pid()

        tornado.ioloop.IOLoop().instance().start()

    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Action Options
    actionArgs = parser.add_argument_group('Action options')
    actionArgs.add_argument(
        '-action',
        choices=['kill', 'reload', 'daemon'],
        help='Select the action.'
    )
    parser.add_argument(
        '-doc',
        '--docs',
        action='store_true',
        dest='docs',
        default=False,
        help='Load Documentation'
    )
    parser.add_argument(
        '-i',
        '--instances',
        dest='instances',
        action='store',
        default=False,
        type=int,
        help='Number of instances'
    )
    parser.add_argument(
        '-p',
        '--port',
        dest='port',
        action='store',
        default=False,
        type=int,
        help='Port Number'
    )
    parser.add_argument(
        '-t',
        '--test',
        dest='test',
        action='store',
        default=False,
        help='Run in test Mode'
    )

    args = parser.parse_args()

    if args.action == 'kill':
        send_signal(signal.SIGINT)
        sys.exit(0)

    if args.action == 'reload':
        send_signal(signal.SIGHUP)
        sys.exit(0)

    try:
        if args.action == 'daemon':
            config, server_config = get_configs()
            if 'log_path' in server_config['tornado'].keys() and \
                    server_config['tornado']['log_path']:
                log_path = server_config['tornado']['log_path']
            else:
                log_path = '%s/logs' % (ROOTPATH)
            daemon.daemonize(
                stdout_path='%s/stdout.log' % log_path,
                stderr_path='%s/stderr.log' % log_path)

        main(args)
    except Exception as e:
        print(e)
