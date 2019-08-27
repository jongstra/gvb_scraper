<!--####################################################################################
# This file creates the markdown documentation for the GVB scraper repository.         #
#                                                                                      #
# Created by Thomas Jongstra 2019 - for the Municipality of Amsterdam                  #
#####################################################################################-->

## Install Locally

#### Create a local virtual Python environment:
	virtualenv --python=$(which python3) venv

#### Activate the local environment (do this everytime you want to run the code) using the following statement:
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

#### Spin up the 'database' Docker container:
	docker-compose up database

#### Run the 'scraper' Docker container (downloads the data to cache, and fills the database with the raw data):
    docker-compose up scraper

#### Instead of running the 'scraper' docker container directly, we can also run the scraping script outside of the Docker container. The --debug flag ensures that we only download and process a small amount of files from our data source, and that we see all debug log messages. The --local flag ensures that we use the correct database configuration settings for local development.
    python scraper/scrape.py --debug --local


## Check

#### Check the log file to see what operations have been performed (instead of printing it with cat, you can also open the log file with an editor):
    cat gvbScraperLog.log

#### Check the data in the database using DBeaver:
Start DBeaver and connect to the database. Make sure the database docker is running. When developing locally, the settings in scraper/config.ini can be used to connect to the database.