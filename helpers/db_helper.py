########################################################################################
# This file defines several methods to enable several database operations, such as:    #
#                                                                                      #
# - creating a database engine                                                         #
# - creating a database connection                                                     #
# - creating a new databas                                                             #
# - creating database tables                                                           #
# - specific operations to log the status of jobs in the CacheStatus table             #
#                                                                                      #
# This code is an adaptation and major extension of previous code by Stephan Preeker.  #
# Curated by Thomas Jongstra 2019 - for the Municipality of Amsterdam                  #
########################################################################################

# Import public modules.
import os
import sys
import logging
import configparser
from sqlalchemy import create_engine, func, MetaData
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy_utils.functions import database_exists
from sqlalchemy_utils.functions import create_database
from sqlalchemy_utils.functions import drop_database

# Add the parent paths to sys.path, so our own modules can be imported.
parent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir)
sys.path.append(parent_path)

# Import own modules.
from models import models

# Get database configurations using a config parser.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_auth = configparser.ConfigParser()
config_auth.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini"))

# Turn on logging.
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# Instantiate a sqlalchemy sessionmaker to use in this script.
Session = sessionmaker()


#########################################
# Database Connection Related Functions #
#########################################

def make_conf(section, environment_overrides=[]):
    """Create database configuration."""

    # Load the database configuration from the config.ini file.
    db = {
        'host': config_auth.get(section, "host"),
        'port': config_auth.get(section, "port"),
        'database': config_auth.get(section, "database"),
        'username': config_auth.get(section, "username"),
        'password': config_auth.get(section, "password"),
    }

    # Override defaults with environment settings, whenever they exist.
    for var, env in environment_overrides:
        if os.getenv(env):
            db[var] = os.getenv(env)

    # Create the configuration.
    conf = URL(
        drivername="postgresql",
        host=db['host'],
        port=db['port'],
        database=db['database'],
        username=db['username'],
        password=db['password'],
    )

    host, port, name = db['host'], db['port'], db['database']
    log.info(f"Database config {host}:{port}:{name}")
    return conf


def make_engine(section="docker", environment=[]):
    """Create a database engine using the credentials in the corresponding section in config.ini."""
    conf = make_conf(section, environment_overrides=environment)
    engine = create_engine(conf)
    return engine


def set_session(engine):
    """Create a database session."""
    Session.configure(bind=engine)
    session = Session()
    return session


#################################################
# Table and Database Handling Related Functions #
#################################################

def create_tables(section="docker"):
    """Create tables in the database based on the models defined in this file."""

    # Create a database session.
    engine = make_engine(section)
    session = set_session(engine)

    # Create all tables. Use the Base from models/models.py, as this contains all table definitions.
    log.warning("Creating defined tables (this is only done when they do not exist yet).")
    models.Base.metadata.create_all(engine, checkfirst=True)


def table_exists(name, engine):
    """Checks whether a table exists in the database."""
    ret = engine.dialect.has_table(engine, name)
    print('Table "{}" exists: {}'.format(name, ret))
    return ret


###############################
# CacheStatus Table Functions #
###############################

def create_job_record(filename, session):
    """Create a row in the cache_status table, to indicate the start of cache file processing job."""

    # Create the record.
    new_record = models.CacheStatus(FileName = filename,
                                    StartTime = func.now(),
                                    JobFinished = False)

    # Add the record to the database.
    session.add(new_record)
    session.commit()

    # Return the id of the newly created job.
    return new_record.Id


def indicate_job_finished(filename, entries_added, table, job_id, session):
    """
    Update a row in the cache_status table, to indicate that
    a cache file processing job is completed.
    """

    # Get the record for the given job_id.
    record = session.query(models.CacheStatus).filter(models.CacheStatus.Id == job_id).first()

    # Update the record, so it indicates that the job has been finished.
    record.JobFinished = True
    record.FinishedTime = func.now()
    record.EntriesAdded = entries_added
    record.FilledTable = table
    session.commit()


def check_job_already_completed(filename, session):
    """
    Check in the cache_status table whether a specific cached/downloaded file
    has already been processed succesfully.
    """

    # Find all finished jobs for the given file.
    q = session.query(models.CacheStatus)
    q = (q.filter(models.CacheStatus.FileName==filename)
          .filter(models.CacheStatus.JobFinished==True))
    number_of_succesful_adds = q.count()

    # Log a warning when the file has accidentally added to the database multiple times.
    if number_of_succesful_adds > 1:
         log.warning(f'The data of file "{filename}" has been added to the database multiple times! ({number_of_succesful_adds} times to be specific)')

    # Return a boolean indicating whether the file has already been processed before.
    if number_of_succesful_adds > 0:
         return True
    else:
         return False


###########################################
# Functions for Testing Database Creation #
###########################################

def create_db(section="test", environment=[]):
    """Create test database."""
    conf = make_conf(section)
    log.info(f"Created database")
    if not database_exists(conf):
        create_database(conf)


def drop_db(section="test", environment=[]):
    """Remove test database."""
    log.info(f"Drop database")
    conf = make_conf(section)
    if database_exists(conf):
        drop_database(conf)
