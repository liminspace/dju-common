from dju_common.cyclictask_core import CyclicTaskBase


class RunHandlerSiteTasks(CyclicTaskBase):
    run_interval = 1000

    def task(self):
        print 'Hello world'


RunHandlerSiteTasks.register()
