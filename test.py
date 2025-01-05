# SuperFastPython.com
# example of join and task done for a joinable queue with processes
from time import sleep
from random import random
from multiprocessing import JoinableQueue
from multiprocessing import Process


# task for the producer process
def producer(queue):
	print('Producer starting', flush=True)
	# add tasks to the queue
	for i in range(10):
		# generate a task
		task = (i, random())
		print(f'.producer added {task}', flush=True)
		# add it to the queue
		queue.put(task)
	# send a signal that no further tasks are coming
	queue.put(None)
	print('Producer finished', flush=True)


# task for the consumer process
def consumer(queue):
	print('Consumer starting', flush=True)
	# process items from the queue
	while True:
		# get a task from the queue
		task = queue.get()
		# check for signal that we are done
		if task is None:
			break
		# process the item
		sleep(task[1])
		print(f'.consumer got {task}', flush=True)
		# mark the unit of work as processed
		queue.task_done()
	# mark the signal as processed
	queue.task_done()
	print('Consumer finished', flush=True)


# entry point
if __name__ == '__main__':
	# create the shared queue
	a_queue = JoinableQueue()
	# create and start the producer process
	producer_process = Process(target=producer, args=(a_queue,))
	producer_process.start()
	# create and start the consumer process
	consumer_process = Process(target=consumer, args=(a_queue,))
	consumer_process.start()
	# wait for the producer to finish
	producer_process.join()
	print('Main found that the producer has finished', flush=True)
	# wait for the queue to empty
	a_queue.join()
	print('Main found that all tasks are processed', flush=True)