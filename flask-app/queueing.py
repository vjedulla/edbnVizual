from edbn.Experiments import RuneDBN
from threading import Thread
from queue import Queue
from worker import solve_edbn
import datetime
import threading
import time
from models import engine

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

class QueueWorker:
    UPLOAD_FOLDER = 'flask-app/uploads/'

    def __init__(self, db=None, num=2):
        self.q = Queue()
        self.db = db

        self.start_deamons(num)

    def add(self, task):
        self.q.put(task)

    def create_new_task(self, obj, parameters=None):
        task = {
            'task_id': obj.id,
            'experiment_id': obj.experiment.id,
            'status': obj.status,
            'parameters': parameters
        }

        self.add(task)

    def queue_solver(self, name):
        print("Silently working on a process to thread={}".format(name))

        while True:
            task = self.q.get()

            if task['status'] is not "In Progress":
                from models import Status, Experiment, Queue as QueueDB
                from sqlalchemy.orm import scoped_session
                from sqlalchemy.orm import sessionmaker

                print(threading.currentThread().getName(), 'Starting')
                session_factory = sessionmaker(bind=engine)
                Session = scoped_session(session_factory)

                session_scope = Session()

                task['status'] = 'In Progress'
                task_id = task['task_id']
                experiment_id = task['experiment_id']

                # models
                experiment = session_scope.query(Experiment).get(experiment_id)
                queue = session_scope.query(QueueDB).get(task_id)

                experiment.queued_at = datetime.datetime.utcnow()

                filepath = self.UPLOAD_FOLDER + experiment.data_file_path
                alias = experiment.alias + "/"

                model = solve_edbn(task, filepath, alias)

                print("solved")

                task['status'] = 'Done'
                experiment.queued_end = datetime.datetime.utcnow()
                # experiment.data_processed = scores
                experiment.model = model
                queue.status = Status.done

                session_scope.add(queue)
                session_scope.add(queue)

                session_scope.commit()
                session_scope.commit()

                self.q.task_done()

                print(threading.currentThread().getName(), 'Exiting')
                # you can now use some_session to run multiple queries, etc.
                # remember to close it when you're finished!
                Session.remove()

    def start_deamons(self, num=2):
        for i in range(num):
            name = "Thread-{}".format(i)
            t = Thread(target=self.queue_solver, name=name, args=[name])
            t.daemon = True
            t.start()


