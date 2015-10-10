import os
import threading
import imp
import time
import datetime
from django.conf import settings


_ts_start = time.mktime(datetime.datetime.now().timetuple())


def mts_now():
    global _ts_start
    dt = datetime.datetime.now()
    return (time.mktime(dt.timetuple()) - _ts_start) * 1000 + dt.microsecond / 1000


mts_start = mts_now()


class CyclicTaskBase(object):
    run_wait = 1000      # wait before first execution, ms
    run_interval = None  # execution interval, ms

    def __init__(self):
        self.last_run = mts_start + self.run_wait
        self.is_running = False
        self.thread = None

    def task(self):
        raise NotImplementedError('subclasses of CyclicTaskBase must provide a task() method')

    def run(self):
        self.is_running = True
        self.thread = threading.Thread(target=self.run_task)
        self.last_run = mts_now()
        self.thread.start()

    def run_task(self):
        self.task()
        self.is_running = False

    @classmethod
    def register(cls):
        CyclicTaskManager.register(cls)


class CyclicTaskManager(object):
    CYCLE_INTERVAL = 0.01
    _registered_tasks = []

    @classmethod
    def register(cls, task):
        assert issubclass(task, CyclicTaskBase)
        task = task()
        assert isinstance(task.run_interval, (int, long))
        assert task not in cls._registered_tasks
        cls._registered_tasks.append(task)

    @classmethod
    def start(cls):
        while True:
            now = mts_now()
            for t in cls._registered_tasks:
                if not t.is_running and (t.last_run + t.run_interval) < now:
                    t.run()
            time.sleep(cls.CYCLE_INTERVAL)

    @classmethod
    def count_tasks(cls):
        return len(cls._registered_tasks)


_manager_thread = None


def init(pid_fn=None):
    global _manager_thread
    if _manager_thread is not None:
        return
    for app in settings.INSTALLED_APPS:
        try:
            imp.find_module('cyclictask', __import__(app, fromlist=[app.split('.')[-1]]).__path__)
        except (AttributeError, ImportError):
            continue
        __import__('%s.cyclictask' % app)
    _manager_thread = False
    if CyclicTaskManager.count_tasks():
        _manager_thread = threading.Thread(target=CyclicTaskManager.start, name='cyclictask')
        _manager_thread.setDaemon(True)
        _manager_thread.start()
        created_pid = False
        try:
            if pid_fn:
                if os.path.exists(pid_fn):
                    try:
                        pid = int(open(pid_fn).read())
                    except (OSError, TypeError):
                        pass
                    else:
                        try:
                            if os.name == 'nt':
                                os.popen('TASKKILL /PID {pid} /F'.format(pid=pid))
                            else:
                                os.kill(pid, 0)
                        except OSError:
                            pass
                with open(pid_fn, 'w') as f:
                    f.write(str(os.getpid()))
                    created_pid = True
            try:
                while _manager_thread.is_alive():
                    _manager_thread.join(1)
            except (KeyboardInterrupt, SystemExit):
                pass
        finally:
            if created_pid and os.path.exists(pid_fn):
                try:
                    os.remove(pid_fn)
                except OSError:
                    pass
