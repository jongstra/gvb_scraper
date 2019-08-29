########################################################################################
# This file defines functions to download the GVB documents from their FTP server,     #
# as well as functions to process these files and add their raw data                   #
# to their corresponding database tables.                                              #
#                                                                                      #
# This code is an adaptation and major extension of previous code by Stephan Preeker.  #
# Curated by Thomas Jongstra 2019 - for the Municipality of Amsterdam                  #
########################################################################################

# Import public modules.
import argparse
import logging
import sys
import os
import pandas as pd
import pysftp

# Add the parent paths to sys.path, so our own modules can be imported.
parent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir)
sys.path.append(parent_path)

# Import own modules.
from models import models
from helpers import db_helper


############################################
# Initiate logger and set global variables #
############################################

# Set SEBUB and RUN_LOCAL flags (can be overridden using a command line argument/flag).
DEBUG = False
RUN_LOCAL = False

# Set the logging level for the console output.
console_logging_level = logging.ERROR
if DEBUG == True:
    console_logging_level = logging.DEBUG

# Create the logger object.
log = logging.getLogger('gvb_scraper')
log.setLevel(console_logging_level)
# Create file handler, which always logs debug messages.
file_handler = logging.FileHandler('gvbScraperLog.log')
file_handler.setLevel(logging.DEBUG)
# Create console handler with a different log level.
stream_handler = logging.StreamHandler()
stream_handler.setLevel(console_logging_level)
# Create formatter and add it to the handlers.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)
# Add the handlers to the logger.
log.addHandler(file_handler)
log.addHandler(stream_handler)

# Get the API url, username and password from the environment variables. Put them in a dictionary.
AUTH = {
    "url": os.getenv("GVB_FTP_URL"),
    "username": os.getenv("GVB_FTP_USERNAME"),
    "password": os.getenv("GVB_FTP_PASSWORD"),
}
# Ensure the API username and password are set.
assert AUTH['url'], "The required environment variable 'GVB_FTP_URL' has not been set."
assert AUTH['username'], "The required environment variable 'GVB_FTP_USERNAME' has not been set."
assert AUTH['password'], "The required environment variable 'GVB_FTP_PASSWORD' has not been set."

# Set the cache directory.
CACHE_DIRECTORY = os.path.abspath('./cache')


#############################################################
# Check download/cache directory existence & writing access #
#############################################################

def check_cache_directory():
    """Check whether there is a writable cache directory to save all downloaded data."""
    if not os.path.isdir(CACHE_DIRECTORY):
        log.error(f'The necessary cache directory at location "{CACHE_DIRECTORY}" does not exists. Please create it. This code should have writing permissions to this directory, but no executing permissions!')
    else:
        log.info('The necessary cache directory exists.')

    # Test whether we are allowed to write/save data to the cache directory.
    try:
        test_file = os.path.join(CACHE_DIRECTORY, 'test.txt')
        with open(test_file, 'w') as outfile:
            outfile.write('File writing test. This file should automatically be removed after the writing test is completed. Feel free to remove the file when it is still here.')
        os.remove(test_file)  # remove test file.
        log.info('Cache directory writing test succeeded.')
    except IOError:
        log.error(f'No writing access for the directory "{CACHE_DIRECTORY}". Please change the folder permissions to allow writing to it.')


#####################
# Download GVB data #
#####################

def create_ftp_file_listing():
    """Create a listing of all file paths present on the server."""

    # Connect with the GVB server.
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  # TODO: change so we do use a hostkey.
    with pysftp.Connection(host=AUTH['url'], username=AUTH['username'], password=AUTH['password'], cnopts=cnopts) as conn:
        log.info("Connection with GVB FTP server is succesfully established... ")

        # Create lists to save results from the recursive directory walktree.
        file_paths = []
        dir_paths = []
        other_files_paths = []

        # Recursively walk through the entire GVB ftp, and save all directory and file paths.
        conn.walktree(remotepath='.',
                      fcallback=lambda x: file_paths.append(x),
                      dcallback=lambda x: dir_paths.append(x),
                      ucallback=lambda x: other_files_paths.append(x),
                      recurse=True)

        log.info("File listing of server has been created. Now closing server connection.")

    # Return the file path listing.
    return file_paths


def download_gvb_data():
    """Download all new GVB files from the server. Files in our cache are not downloaded again."""

    # Create a listing of all files on the FTP server.
    file_paths = create_ftp_file_listing()

    # Connect with the GVB server.
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None  # TODO: change so we do use a hostkey.
    with pysftp.Connection(host=AUTH['url'], username=AUTH['username'], password=AUTH['password'], cnopts=cnopts) as conn:
        log.info("Connection with GVB FTP server is succesfully established... ")

        # When debugging, only download a small set of the file paths.
        if DEBUG == True:
            sample_size = min(len(file_paths), 10)
            file_paths = file_paths[:sample_size]

        # Create a list of all document names in the download cache.
        cached_files = os.listdir(CACHE_DIRECTORY)

        # Iterate over all the found regular files, and save them in a local folder
        for path in file_paths:

            # Get the filename.
            filename = os.path.basename(path)

            # Only download the file when it is not in our cache yet.
            if filename in cached_files:
                log.info(f'File "{path}" is already present in our download cache. Skipping download.')
            else:
                # Define the target path for the file. Ensure this path lies within our cache folder (to protect from possible hacks).
                target_file_path = os.path.join(CACHE_DIRECTORY, filename)
                target_file_path = os.path.abspath(target_file_path)
                target_file_path_dir = os.path.dirname(target_file_path)
                if target_file_path_dir == CACHE_DIRECTORY:
                    # Download the file, and save it in the download cache folder.
                    file = conn.get(path, target_file_path)
                    log.info(f'File "{path}" has been downloaded.')
                else:
                    # Log an error when the filename would indicate of an attempted writing action outside of our intended cache directory.
                    log.critical(f'Write action would write file to other directory then our cache directory. Write action has not been performed. This could indicate a possible hacking attempt!')

        log.info('Finished downloading files! Now closing server connection.')


#############################################
# Functions Related to Data Model Detection #
#############################################

def get_columns_from_data_model(data_model):
    """Get the list of columns for a given data model."""
    columns = data_model.__table__.columns.keys()
    for x in ['Id', 'JobId']:  # Removes columns, since they identify the tables.
        if x in columns: columns.remove(x)
    return set(columns)


def create_data_models_dict(models):
    """
    Create a data models dict with the following type of entries:
    data_model_name -> (data_model, data_model_columns).
    """

    # Only the models/classes defined by ourselves (subclasses of the Base model).
    own_models = models.Base.__subclasses__()

    # Create the dictionary.
    data_models_dict = {cls.__name__: (cls, get_columns_from_data_model(cls)) for cls in own_models}
    return data_models_dict


def get_data_model_from_df(df, models):
    """Return the correct data model for a given dataframe."""

    # Create a set of the column names of the dataframe.
    df_cols = set(df.columns)

    # Compare the dataframe data model with all data models.
    data_models_dict = create_data_models_dict(models)  # Could be taken outside of loop, but kept for clarity.
    for k, v in data_models_dict.items():
        model_cols = v[1]

        # When we have a match, return the found data model.
        if df_cols == model_cols:
            data_model = v[0]
            return data_model


###################################
# Fill Database with Raw GVB Data #
###################################

def store_data_in_database():
    """Save the data from the downloaded/cached files to the database."""

    log.info('Now storing all unprocessed files in the database...')

    # Get the database session to be able to commit data to the database.
    section = "docker"  # Use the docker configuration (in config.ini) by default.
    if RUN_LOCAL:
        section = "local_development"  # Use the configuration for local development when the script is called with the --local flag.
    engine = db_helper.make_engine(section=section)
    session = db_helper.set_session(engine)

    # Create a lookup dict for our models/classes. We use this to select the right data model for each file.
    data_models_dict = create_data_models_dict(models)

    # Create a list of all document names in the download cache.
    cached_files = os.listdir(CACHE_DIRECTORY)

    # When debugging, only process a small set of the files.
    if DEBUG == True:
        sample_size = min(len(cached_files), 10)
        cached_files = cached_files[:sample_size]

    # Load the data of each file into a dataframe, and add it to the database.
    for filename in cached_files:

        # Check whether the file was succesfully processed before. If not, process it now.
        if not db_helper.check_job_already_completed(filename, session):

            # Log which file is being processed now.
            log.info(f'Processing file "{filename}" now.')

            # Create a record in the cache_status table, to indicate that the job has been started.
            job_id = db_helper.create_job_record(filename, session)

            # Load the data of the csv file into a dataframe.
            df = pd.read_csv(os.path.join(CACHE_DIRECTORY, filename), sep=';')

            # Rename columns in the raw data if they contain spaces.  # CHECK: do we want this?
            df_columns = df.columns
            if 'UurgroepOmschrijving (van aankomst)' in df_columns:
                df = df.rename(columns={'UurgroepOmschrijving (van aankomst)': 'UurgroepOmschrijvingVanAankomst'})
            if 'UurgroepOmschrijving (van vertrek)' in df_columns:
                df = df.rename(columns={'UurgroepOmschrijving (van vertrek)': 'UurgroepOmschrijvingVanVertrek'})

            # Get the right data model for the current file.
            data_model = get_data_model_from_df(df, models)

            # Add the job id of the current job to all records created with this job.
            df['JobId'] = job_id

            # Convert the dataframe to a format to be consumed by the database.
            objects = df.to_dict('records')

            # Commit the data to the database.
            session.bulk_insert_mappings(data_model, objects)
            session.commit()

            # Update a record in the cache_status table to indicate that the job has been finished.
            db_helper.indicate_job_finished(filename, len(df), data_model.__name__, job_id, session)
            log.info(f'Finished processing file {filename}". Stored {len(df)} records in the database.')

    log.info('Finished processing all unprocessed files, and storing their data in the database!')


################
# Main Routine #
################

def main():
    """This main routine performs all GVB raw data scraping steps in sequence."""

    # Check whether the cache directory exists and is writable.
    check_cache_directory()

    # Download the GVB data.
    download_gvb_data()

    # Ensure all database tables (defined in model.py) exist. Create them when they do not exists.
    section = "docker"  # Use the docker configuration (in config.ini) by default.
    if RUN_LOCAL:
        section = "local_development"  # Use the configuration for local development when the script is called with the --local flag.
    db_helper.create_tables(section=section)

    # Fill the GVB raw data tables, using all downloaded/cached files.
    store_data_in_database()


# When calling this script directly, run the main routine.
if __name__ == "__main__":

    # Parse the commandline arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Print debug messages to stderr.')
    parser.add_argument('--local', action='store_true', help='Use the local database configuration.')
    args = parser.parse_args()
    # When using the "debug" flag, we only download and process up to 10 files. We also show debug messages in console.
    if args.debug == True:
        DEBUG = True
    # When using the "local" flag, make sure the local configuration settings to the database are used.
    if args.local == True:
        RUN_LOCAL = True

    # Run the main routine.
    main()
