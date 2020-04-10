<!--####################################################################################
# This file creates the markdown documentation for the GVB scraper repository.         #
#                                                                                      #
# Created by Thomas Jongstra 2019 - for the Municipality of Amsterdam                  #
#####################################################################################-->

## Install Locally

#### Create a local virtual Python environment:
	virtualenv --python=$(which python3) venv

#### Activate the virtual environment using the following statement:
	source venv/bin/activate

#### Install some Linux packages in this virtual environment using apt (to be able to install and use psycopg2):
    apt install -y libpq-dev python3-dev

#### Install the required Python packages in the virtual environment:
	pip install requirements.txt

#### Create a cache folder (in the root of this repo), where the scraped files can be saved/cached. When deploying this scraper on a server, (files in) the cache folder should not be granted execute rights:
    mkdir cache

#### Build the Docker containers:
    docker-compose build





## Run

#### Activate the virtual environment, if it isn't active already:
    source venv/bin/activate

#### Create the following environment variables, and assign the correct values to them:
    GVB_FTP_URL
    GVB_FTP_USERNAME
    GVB_FTP_PASSWORD

For local development, it is possible to automatically add/remove these environment variables when activating/deactivating the virtual environment. This can be accomplished by modifying the **venv/bin/activate** file. To accomplish this, add **export** statements for these variable at the bottom of the file, and **unset** statements for these variables within the **deactivate** function in this script. When deploying the code on a server, it would probably be a good idea to use more secure options to expose these secrets.

#### Start the 'database' Docker container. The -d flag makes the database container run in the background:
	docker-compose up -d database

#### Run the 'scraper' Docker container (downloads the data to cache, and fills the database with all raw data):
    docker-compose up scraper

#### Instead of running the scraping script from the 'scraper' docker container, we can also run the scraping script locally. We can do this by directly calling the scrape.py script, using the --local flag. This flag ensures that a fitting database configuration is used. The --debug flag can also be used to only download & process a small amount of files from our data source, so we can quickly see whether everything is working correctly.
    python scraper/scrape.py --debug --local


## Check

#### Check the data in the database using DBeaver:
Start DBeaver and connect to the database. Make sure the database docker is running.
At the time of writing, the settings to connect with the local database are as follows:

    host=localhost
    port=9000
    database=gvb
    username=postgres
    password=insecure