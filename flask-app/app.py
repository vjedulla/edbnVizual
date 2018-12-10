#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, flash, redirect, url_for, abort
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template
from logging import Formatter, FileHandler
import logging
from werkzeug.utils import secure_filename
import os
import time
from flask import jsonify
import queueing

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
queue = None

ALLOWED_EXTENSIONS = set(['txt', 'csv'])

# app.config['TRAP_HTTP_EXCEPTIONS'] = True

db = SQLAlchemy(app)

# Automatically tear down SQLAlchemy.

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
    print(show.model.raw_edges)
    return render_template('pages/placeholder.show_network.html', network=show)


@app.route('/queue')
def queue():
    from models import Experiment, Queue

    all_queued = Queue.query.all()

    return render_template('pages/placeholder.queue.html', all_queued=all_queued)


@app.route('/application')
def application():
    # flash('this is a flash message')
    # return redirect(url_for('home'))
    return render_template('pages/placeholder.application.html')


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

    e = Experiment(name=name, data_file_path=filename, authors=authors, tags=tags, notes=notes, alias=alias)
    q = Queue(e)

    db.session.add(e)
    db.session.add(q)

    db.session.commit()

    queue.create_new_task(q)

    return redirect(url_for('queue'))
    # return jsonify({
    #     'status': 'ok'
    # })


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
