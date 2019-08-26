########################################################################################
# This file defines the GVB data models, so they can be created in a database.         #
#                                                                                      #
# Created by Thomas Jongstra 2019 - for the Municipality of Amsterdam                  #
########################################################################################

# Import public modules.
import logging
import argparse
import sys
import os
from sqlalchemy import Column, Integer, Float, String, TIMESTAMP, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

# Add the parent path to sys.path, so our own modules can be imported.
sys.path.append(os.path.abspath('..'))

# Turn on the logger.
log = logging.getLogger(__name__)

# Set the declarative base, which is used when defining data models.
Base = declarative_base()


###########################
# Cache Status Data Model #
###########################

class CacheStatus(Base):
    """This table is used for indicating whether our chached documents have been processed yet."""
    __tablename__ = "CacheStatus"
    Id = Column(Integer, primary_key=True)
    FileName = Column(String, index=True)
    StartTime = Column(TIMESTAMP, index=True)
    JobFinished = Column(Boolean, index=True)
    EntriesAdded = Column(Integer, index=True)
    FilledTable = Column(String, index=True)
    FinishedTime = Column(TIMESTAMP, index=True)


############################
# Raw Data Models - Reizen #
############################

class GvbReisBestemmingDatumRaw(Base):
    """One of the data model definitions of the raw GVB API data (ftp.gvb.nl)."""
    __tablename__ = "GvbReisBestemmingDatumRaw"
    Id = Column(Integer, primary_key=True)
    Datum = Column(Date, index=True)
    AankomstHalteCode = Column(String, index=True)
    AankomstHalteNaam = Column(String, index=True)
    AankomstLat = Column(Float)
    AankomstLon = Column(Float)
    AantalReizen = Column(Integer)
    JobId = Column(Integer)


class GvbReisHerkomstDatumRaw(Base):
    """One of the data model definitions of the raw GVB API data (ftp.gvb.nl)."""
    __tablename__ = "GvbReisHerkomstDatumRaw"
    Id = Column(Integer, primary_key=True)
    Datum = Column(Date, index=True)
    VertrekHalteCode = Column(String, index=True)
    VertrekHalteNaam = Column(String, index=True)
    VertrekLat = Column(Float)
    VertrekLon = Column(Float)
    AantalReizen = Column(Integer)
    JobId = Column(Integer)


class GvbReisBestemmingUurRaw(Base):
    """One of the data model definitions of the raw GVB API data (ftp.gvb.nl)."""
    __tablename__ = "GvbReisBestemmingUurRaw"
    Id = Column(Integer, primary_key=True)
    Datum = Column(Date, index=True)
    UurgroepOmschrijvingVanAankomst = Column(String, index=True)
    AankomstHalteCode = Column(String, index=True)
    AankomstHalteNaam = Column(String, index=True)
    AankomstLat = Column(Float)
    AankomstLon = Column(Float)
    AantalReizen = Column(Integer)
    JobId = Column(Integer)


class GvbReisHerkomstUurRaw(Base):
    """One of the data model definitions of the raw GVB API data (ftp.gvb.nl)."""
    __tablename__ = "GvbReisHerkomstUurRaw"
    Id = Column(Integer, primary_key=True)
    Datum = Column(Date, index=True)
    UurgroepOmschrijvingVanVertrek = Column(String, index=True)
    VertrekHalteCode = Column(String, index=True)
    VertrekHalteNaam = Column(String, index=True)
    VertrekLat = Column(Float)
    VertrekLon = Column(Float)
    AantalReizen = Column(Integer)
    JobId = Column(Integer)


############################
# Raw Data Models - Ritten #
############################

class GvbRitHerkomstBestemmingUurRaw(Base):
    """One of the data model definitions of the raw GVB API data (ftp.gvb.nl)."""
    __tablename__ = "GvbRitHerkomstBestemmingUurRaw"
    Id = Column(Integer, primary_key=True)
    Datum = Column(Date, index=True)
    UurgroepOmschrijvingVanVertrek = Column(String, index=True)
    VertrekHalteCode = Column(String, index=True)
    VertrekHalteNaam = Column(String, index=True)
    VertrekLat = Column(Float)
    VertrekLon = Column(Float)
    AankomstHalteCode = Column(String, index=True)
    AankomstHalteNaam = Column(String, index=True)
    AankomstLat = Column(Float)
    AankomstLon = Column(Float)
    AantalRitten = Column(Integer)
    JobId = Column(Integer)


class GvbRitBestemmingUurRaw(Base):
    """One of the data model definitions of the raw GVB API data (ftp.gvb.nl)."""
    __tablename__ = "GvbRitBestemmingUurRaw"
    Id = Column(Integer, primary_key=True)
    Datum = Column(Date, index=True)
    UurgroepOmschrijvingVanAankomst = Column(String, index=True)
    AankomstHalteCode = Column(String, index=True)
    AankomstHalteNaam = Column(String, index=True)
    AankomstLat = Column(Float)
    AankomstLon = Column(Float)
    AantalRitten = Column(Integer)
    JobId = Column(Integer)


class GvbRitHerkomstUurRaw(Base):
    """One of the data model definitions of the raw GVB API data (ftp.gvb.nl)."""
    __tablename__ = "GvbRitHerkomstUurRaw"
    Id = Column(Integer, primary_key=True)
    Datum = Column(Date, index=True)
    UurgroepOmschrijvingVanVertrek = Column(String, index=True)
    VertrekHalteCode = Column(String, index=True)
    VertrekHalteNaam = Column(String, index=True)
    VertrekLat = Column(Float)
    VertrekLon = Column(Float)
    AantalRitten = Column(Integer)
    JobId = Column(Integer)
