from sqlalchemy import create_engine, Table, Column
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Enum
from sqlalchemy.pool import SingletonThreadPool
from app import db
import datetime

engine = create_engine('sqlite:///flask-app/database/database.db', connect_args={'check_same_thread': False}, poolclass=SingletonThreadPool)

db_session = scoped_session(sessionmaker(
                                    # autocommit=False,
                                    # autoflush=False,
                                    bind=engine
))

Base = declarative_base()
Base.query = db_session.query_property()


# Classes
experiment_author_table = db.Table('author_experiment', Base.metadata,
    db.Column('exp_id', db.Integer, db.ForeignKey('experiments.id', ondelete="CASCADE")),
    db.Column('auth_id', db.Integer, db.ForeignKey('authors.id', ondelete="CASCADE"))
)

experiment_tags_table = db.Table('experiments_tag', Base.metadata,
    db.Column('exp_id', db.Integer, db.ForeignKey('experiments.id', ondelete="CASCADE")),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id', ondelete="CASCADE"))
)

class Tag(Base):
    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    experiments = db.relationship(
        "Experiment",
        secondary=experiment_tags_table,
        back_populates="tags"
    )

    def __init__(self, tag_name=None):
        self.name = tag_name

    def __repr__(self):
        return '<Tag %r(id:%d)>' % (self.name, self.id)

class Author(Base):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(128), nullable=False)
    experiments = db.relationship(
        "Experiment",
        secondary=experiment_author_table,
        back_populates="authors"
    )

    def __init__(self, author=None):
        self.author = author


    def __repr__(self):
        return '<Author %r(id:%d)>' % (self.author, self.id)


class Experiment(Base):
    __tablename__ = 'experiments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    alias = db.Column(db.String(128), nullable=True)
    notes = db.Column(db.Text(), nullable=True)

    # authors = db.Column(db.String(128))
    # tags = db.Column(db.String(128))
    authors = db.relationship(
        "Author",
        secondary=experiment_author_table,
        back_populates="experiments",
        cascade="all,delete"
    )

    tags = db.relationship(
        "Tag",
        secondary=experiment_tags_table,
        back_populates="experiments",
        cascade="all,delete"
    )

    model = db.Column(db.PickleType(), nullable=True)
    parameters = db.Column(db.PickleType(), nullable=True)

    data_processed = db.Column(db.PickleType(), nullable=True)

    dataset_alias = db.Column(db.String(256), nullable=True)
    data_file_path = db.Column(db.String(256), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    queued_at = db.Column(db.DateTime(), nullable=True)
    queued_end = db.Column(db.DateTime(), nullable=True)

    queue = db.relationship("Queue", uselist=False, back_populates="experiment")

    # def __init__(self, name=None, alias=None, notes=None, authors=None,
    #                 tags=None, model=[], parameters=[], dataset_alias=None,
    #                 data_file_path=None, queued_at=None):
    #     self.name = name
    #     self.alias = alias
    #     self.notes = notes
    #
    #     self.authors.append(authors)
    #     self.tags.append(tags)
    #
    #     self.model = model
    #     self.parameters = parameters
    #     self.dataset_alias = dataset_alias
    #     self.data_file_path = data_file_path
    #     self.queued_at = queued_at  # datetime

    def __init__(self, name=None, data_file_path=None, authors=None, tags=None, notes='default', alias='no-alias',
                queued_at=None, queued_end=None, model=None):
        self.name = name
        self.data_file_path = data_file_path

        self.notes = notes
        self.alias = alias

        self.queued_at = queued_at
        self.queued_end = queued_end
        self.model = model

        if authors is not None and isinstance(authors[0], Author):
            self.add_all_authors(authors)
        elif authors is not None and isinstance(authors[0], str):
            tmp_auth = [Author(x) for x in authors]
            self.add_all_authors(tmp_auth)

        if tags is not None and isinstance(tags[0], Tag):
            self.add_all_tags(tags)
        elif tags is not None and isinstance(tags[0], str):
            tmp_tags = [Tag(x) for x in tags]
            self.add_all_tags(tmp_tags)

    def add_all_authors(self, author_list):
        for a in author_list:
            self.authors.append(a)

    def add_all_tags(self, tags_list):
        for t in tags_list:
            self.tags.append(t)

    def __repr__(self):
        return '<Experiment %r(id:%d)>' % (self.name, self.id)


class Status(Enum):
    done = 1
    waiting = 2
    progress = 3


class Queue(Base):
    __tablename__ = 'queue'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer)

    status = db.Column(db.SmallInteger)

    created_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)

    experiment_id = db.Column(db.Integer,  db.ForeignKey('experiments.id'))
    # parent_id = Column(db.Integer, db.ForeignKey('experiments.id')))
    experiment = db.relationship("Experiment", back_populates="queue")

    def __init__(self, exp):
        self.experiment = exp
        self.status = Status.waiting

    def __repr__(self):
        return '<Queue %r(id:%d)>' % (self.id, self.task_id)



'''
class User(Base):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(30))

    def __init__(self, name=None, password=None):
        self.name = name
        self.password = password
'''

# Create tables.
Base.metadata.create_all(bind=engine)
