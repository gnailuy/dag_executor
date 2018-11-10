import argparse


def default_args(description=None, epilog=None):
    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument('--conf', '-f', metavar='conf.ini',
                        type=str, required=False, nargs='?',
                        help='the configure file')
    parser.add_argument('--logfile', metavar='./logs/app.log',
                        type=str, required=False, nargs='?',
                        help='the configure file')
    parser.add_argument('--debug', '-d', required=False, action='store_true',
                        help='debug trigger')
    parser.add_argument('--module_definition', '-m', metavar='modules.yaml',
                        type=str, required=False, nargs='?',
                        help='the modules definition file')
    parser.add_argument('--module_location', '-l', metavar='./modules/',
                        type=str, required=False, nargs='?',
                        help='the modules location')
    parser.add_argument('--module_run_all', '-a', required=False, action='store_true',
                        help='run all module if it is set true')
    parser.add_argument('--queue_host', '-q', metavar='localhost',
                        type=str, required=False, nargs='?',
                        help='the queue server address')
    parser.add_argument('--queue_port', '-p', metavar=6379,
                        type=int, required=False, nargs='?',
                        help='the queue server port')
    parser.add_argument('--cache_host', metavar='localhost',
                        type=str, required=False, nargs='?',
                        help='the cache server address')
    parser.add_argument('--cache_port', metavar=6379,
                        type=int, required=False, nargs='?',
                        help='the cache server port')
    parser.add_argument('--cache_timeout', metavar=86400,
                        type=int, required=False, nargs='?',
                        help='the cache expire time in seconds')
    return parser

