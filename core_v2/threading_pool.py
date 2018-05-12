"""
runtime.threading_pool
~~~~~~~~~~~~~~~~~~~~~~
Used for make threading pool in runtime.

How to use:
    1.Create class named 'Task'.(In fact, name could be everything.)
    2.Rewrite its 'run' function, the worker will run the function 'run' to start the task.

    WARNING: Do not use 'while True' in run method.
"""
import time
import Queue
import threading

__ThreadingCount__ = 3

pipeline = Queue.Queue(maxsize=0)


class ThreadingPool(threading.Thread):
    """Threading pool."""

    def __init__(self):
        super(ThreadingPool, self).__init__()

    @staticmethod
    def threading_run(task):
        """A wrapper to run the task.Just for catch the exception."""
        task.run()

    def run(self):
        """worker run its task."""
        while True:
            try:
                self.threading_run(pipeline.get())
            except Exception as e:
                print(e)
            print('done')
            time.sleep(3)


"""Open __ThreadingCount__ thread to handle task."""
while threading.active_count() < __ThreadingCount__ + 1:
    ThreadingPool().start()
