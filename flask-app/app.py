#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, flash, redirect, url_for, abort, jsonify
# from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from logging import Formatter, FileHandler
import logging
from werkzeug.utils import secure_filename
import os
from flask_moment import Moment
import flask, eventlet
import queueing
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_socketio import send, emit
import time
import threading

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
socketio = SocketIO(app, async_mode="eventlet")

app.config.from_object('config')
queue = None

ALLOWED_EXTENSIONS = {'txt', 'csv'}


db = SQLAlchemy(app)

# @app.teardown_request
# def shutdown_session(exception=None):
#     db.session.remove()

@app.template_filter('print_tags')
def print_list(s):
    out = ["#"+x.name for x in s]
    return ', '.join(out)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#
@app.route('/')
def home():
    from models import Experiment, Author, Tag, Queue

    # authors_lst = ['mando', 'test']
    # tags_lst = ['one', 'two']
    #
    # e = Experiment(name='test', data_file_path='testing', authors=authors_lst, tags=tags_lst)
    # q = Queue(e)
    #
    # db.session.add(e)
    # db.session.add(q)
    # db.session.commit()

    return render_template('pages/placeholder.home.html', names='dummy')


@app.before_first_request
def init():
    print("Init first request")
    global queue
    queue = queueing.QueueWorker(db)


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/testing_connectivity')
def testing():
    # print("Is there: ", queue.check_tasks('running'))
    # if not queue.check_tasks('running'):
    #     queue.create_new_task()
    #
    # solved = queue.check_tasks()

    solved = False

    return render_template('pages/placeholder.scores.html', result=solved)


@app.route('/show_network/<int:id>')
def show_network(id=1):
    from models import Experiment
    show = Experiment.query.get(id)

    if show is None:
        # if there is not an experiment with that name
        abort(404)

    print(show)
    print(show.model.raw_nodes)
    print(show.model.raw_CD)
    print(show.model.raw_FD)

    return render_template('pages/placeholder.show_network.html', network=show)

def message_wrapper(where, data):
    emit(where, data)
    eventlet.sleep()

@socketio.on('score_model')
def score_network(data):
    id = data['which_network']

    @flask.copy_current_request_context
    def background_thread(id):
        from models import Experiment
        from worker import train_and_score

        show = Experiment.query.get(id)

        if show is None:
            # emit("score_resp", {'status': "Error! No experiment with that ID!"})
            return redirect(url_for('queue'))

        model = show.model
        alias = show.alias
        filename = show.data_file_path

        steps = {
            "Preparing to train variables": 1,
            "Data loaded": 2,
            "Build K-Context for data": 3,
            "Finished training data": 4,
            "Finished testing": 5,
            "Preparing scoring": 6,
            "Finished scoring": 7,
            "Finished": 8
        }

        scores = train_and_score(model, alias, filename, message_wrapper)
        message_wrapper("score_resp", {'step': 8, "msg": "Finished!", "scores": scores})

        # redirect with data
        # https://stackoverflow.com/questions/17057191/redirect-while-passing-arguments
        return redirect(url_for('queue'))

    thread = socketio.start_background_task(background_thread, id)


@app.route('/queue')
def queue():
    from models import Queue
    all_queued = Queue.query.all()

    return render_template('pages/placeholder.queue.html', all_queued=all_queued, datetimes=None)


@app.route('/application')
def application():
    # flash('this is a flash message')
    # return redirect(url_for('home'))
    return render_template('pages/placeholder.application.html')

@app.route('/experiment/delete', methods=['POST'])
def delete_experiment():
    from models import Experiment, Queue, Tag, Author
    id = request.form['queue-id']

    queue = Queue.query.get(id)
    experiment = queue.experiment
    experiment_id = experiment.id

    if queue is None:
        # flash("An error occurred!", category="danger")
        return redirect(url_for('queue'))

    # if you delete using the query(X).filter(<cond>).delete()
    # will delete rows. whereas the code below will use the
    # cascading options
    q = db.session.query(Queue).filter(Queue.id == id).first()
    db.session.delete(q)
    u = db.session.query(Experiment).filter(Experiment.id == experiment_id).first()
    db.session.delete(u)
    db.session.commit()

    return redirect(url_for('queue'))


@app.route('/submit_to_queue', methods=['POST'])
def log_file_analyse():
    from models import Experiment, Queue
    print("Name:", request.form['name-input'])
    print("Tags:", request.form['tags-input'])
    print("Notes", request.form['name-input'])
    print("Author", request.form['author-input'])
    print("Dataset alias", request.form['alias-input'])
    print("Dataset:", request.files['datasetInputFile'])

    name = request.form['name-input']
    tags_s = request.form['tags-input']
    notes = request.form['name-input']
    authors_s = request.form['author-input']
    alias = request.form['alias-input']
    file = request.files['datasetInputFile']

    tags = tags_s.split(',')
    authors = authors_s.split(',')

    filename = None

    if file.filename == '':
        print("PROOOBLEM!!!!")
        return redirect(url_for("home"))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    print("here")
    e = Experiment(name=name, data_file_path=filename, authors=authors, tags=tags, notes=notes, alias=alias)
    q = Queue(e)

    db.session.add(e)
    db.session.add(q)

    db.session.commit()
    print("New task")
    queue.create_new_task(q)

    return redirect(url_for('queue'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#----------------------------------------------------------------------------#
# Error handlers.
#----------------------------------------------------------------------------#
@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(Exception)
def exception_happened(error):
    return render_template('errors/exception.html'), error


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')



#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
