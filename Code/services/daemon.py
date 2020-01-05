import os
import sys


def daemonize(stdout_path='logs/stdout.log', stderr_path='logs/stderr.log'):
    if os.fork():
        sys.exit(0)

    sys.stdin.close()
    sys.stdout.close()
    sys.stderr.close()

    os.setsid()
    os.umask(0)

    sys.stdout = open(stdout_path, 'a+')
    sys.stderr = open(stderr_path, 'a+')