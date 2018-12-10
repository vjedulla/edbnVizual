from edbn.Experiments import RuneDBN
from threading import Thread
from queue import Queue
from worker import solve_edbn
from models import Status, Experiment, Queue as QueueDB
import datetime

class QueueWorker:
    UPLOAD_FOLDER = 'flask-app/uploads/'

    def __init__(self, db, num=2):
        self.q = Queue()
        self.db = db

        self.queue_tasks = []
        self.results = []

        self.start_deamons(num)

    def add(self, task):
        self.queue_tasks.append(task)
        self.q.put(task)

    def create_new_task(self, obj, parameters=None):
        task = {
            'task_id': obj.id,
            'experiment_id': obj.experiment.id,
            'status': obj.status,
            'parameters': parameters
        }

        self.add(task)

    # def check_tasks(self, id=None):
    #     if id == 'running':
    #         return any(x['status'] == 'Waiting' for x in self.queue_tasks)
    #
    #     if id is None:
    #         return any(x['status'] == 'Done' for x in self.queue_tasks)
    #
    #     return any(x['id'] == id and x['status'] == 'Done' for x in self.queue_tasks)

    def queue_solver(self):
        print("Silently working on a process")

        while True:
            task = self.q.get()

            if task['status'] is not "In Progress":
                print("One task is on the run!!")

                task['status'] = 'In Progress'
                task_id = task['task_id']
                experiment_id = task['experiment_id']

                # models
                experiment = Experiment.query.get(experiment_id)
                queue = QueueDB.query.get(task_id)

                experiment.queued_at = datetime.datetime.utcnow()

                filepath = self.UPLOAD_FOLDER + experiment.data_file_path
                alias = experiment.alias + "/"

                scores, model = solve_edbn(task, filepath, alias)

                print("solved")

                task['status'] = 'Done'
                experiment.queued_end = datetime.datetime.utcnow()
                # experiment.data_processed = scores
                experiment.model = model
                queue.status = Status.done

                current_db_sessions = self.db.session.object_session(queue)
                current_db_sessions.add(queue)
                current_db_sessions.add(experiment)

                current_db_sessions.commit()

                result = {
                    'id': task['task_id'],
                    'data': [scores, model]
                }

                self.results.append(result)

                self.q.task_done()

    def start_deamons(self, num=2):
        for i in range(num):
            t = Thread(target=self.queue_solver)
            t.daemon = True
            t.start()

