Zendesk sub project
Obtain all tickets from teh zendesk system and store in a postgres database or in a file
Be aware, this is a first, brute force approach where every record gets inserted separately into postgres

The postgres tables are very simple: an ID and a json object

Python prerequisite:
pip install psycopg2 / pip3 install psycopg2
pip install dataset / pip3 install dataset



Database prerequisite
create database zendesk

-- DROP ROLE zendesk;

-- DROP ROLE zendesk;

CREATE ROLE zendesk WITH 
	SUPERUSER
	CREATEDB
	CREATEROLE
	INHERIT
	LOGIN
	REPLICATION
	NOBYPASSRLS
	CONNECTION LIMIT -1;

ALTER ROLE zendesk IN DATABASE customdatabase SET search_path="$user", public, resp_val, zendesk;


-- DROP SCHEMA zendesk;

CREATE SCHEMA zendesk AUTHORIZATION zendesk;

Create the tables as in SQL/tables.sql

make sure to modify the connection settings at the top of the script
for a test-run I suggest to set teh maxindex variable at the top of the python script to a value of 3 or so.
for the real stuff set it to a large value like 2000 or higher.