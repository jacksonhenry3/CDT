import multiprocessing
import time


class Process(multiprocessing.Process):
    """docstring for Process."""

    def __init__(self, id):
        super(Process, self).__init__()
        self.id = id

    def run(self):
        time.sleep(1)
        print("I'm the process with id : {}".format(self.id))


if __name__ == "__main__":
    p = Process(0)
    p.start()
    p.join()
    p = Process(1)
    p.start()
    p.join()
import numpy as np


def square(x):
    return np.random.random()


inputs = np.linspace(0, 1, 10 ** 7)

pool = multiprocessing.Pool(multiprocessing.cpu_count())


import time

start = time.process_time()
outputs = pool.map_async(square, inputs)
outputs = np.mean(outputs)
end = time.process_time()
elapsed = end - start
print("multi-threaded")
print(elapsed)
print(outputs)
print("================")
print("single-threaded")
start = time.process_time()
outputs = np.mean([square(In) for In in inputs])
end = time.process_time()
elapsed = end - start
print(elapsed)
print(outputs)
