# [ SERVER HOOKS ]
def on_starting(server):
    pass


def on_reload(server):
    pass


def when_ready(server):
    pass


def on_exit(server):
    pass


# [ DEVELOPMENT ]
reload = False
reload_extra_files = []
# Capture output from stdout/err and redirect to errorlog
capture_output = False

# [ WORKER ]
# handle with care
import multiprocessing
workers = 2 * multiprocessing.cpu_count()
worker_class = "sync"
threads = 1

# [ LOGGING ]
loglevel = "info"
# "-" is stdout
accesslog = "-"
errorlog = "-"

# [ DEPLOYMENT ]
# X-Forwarded-For trusted sources, comma seperated
forwarded_allow_ips = '127.0.0.1'
