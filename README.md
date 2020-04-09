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

#### Start the 'database' Docker container. The -d flag makes the database container run in the background:
	docker-compose up -d database

#### Run the 'scraper' Docker container (downloads the data to cache, and fills the database with all raw data):
    docker-compose up scraper

#### Instead of running the 'scraper' docker container directly, we can also run the scraping script outside of the Docker container. We can do this by directly calling the scrape.py script while using the --local flag, to ensure that fitting database configuration settings are used. The --debug flag can also be used to download & process a small amount of files from our data source.
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