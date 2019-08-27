########################################################################################
# This file defines the Docker settings for the scraping process.                      #
#                                                                                      #
# This is an adaptation of a previous file by Stephan Preeker.                         #
# Curated by Thomas Jongstra 2019 - for the Municipality of Amsterdam                  #
########################################################################################

FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

EXPOSE 9000

# only do a pip install if requirements are changed
COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir -r /requirements.txt

COPY . /app/

WORKDIR /app
