# Wrangle OpenStreetMap Data

## Summary
Data from google open streetmap (https://www.openstreetmap.org) about a specific place was acquired. The data was accessed for quality,validity, accuracy, completeness, consistency and uniformity. The data was then loaded into a SQL database and queried for analysis. 

## Objectives
* Accessing the quality of the data for validity, accuracy, completeness, consistency and uniformity.
* Cleaning the data where ever required.
* Understanding SQLite and its commands.

## Project Details
The place chosen was Calgary, Canada. The data acquired is in XML format. Required data was gathered from various XML nodes. Since the data set was huge, a small sample from the original data set was used for analysis. 

## Tools Used
* Jupyter Notebook
* SQLite
* Python

## File description :
* sample_canada.osm - Data set used
* Calgary_Cleaning.py - Python script used to Audit & Clean the OSM file
* Process.py - Python script used to Process the OSM file
* Sample_Generator+.py - Python Script to create a sample file of the original OSM
* Schema_SQL.txt - Schema used to create SQL database
* OpenStreetMap Data Case Study_Calgary.pdf - A PDF file containing the answers to thee rubic questions.
