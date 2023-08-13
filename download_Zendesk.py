# invoke: python3 -v download_Zendesk.py 2> log.txt 
# as of writing this code, it needs 8 iterations to download all tickets.

import requests
import json
import sys
import time
import psycopg2   # needed for interaction with postgres
import dataset

# modify these to your liking
maxindex = 200
_trace = True
pguser = 'zendesk'
pgpw = 'zendesk'
zdpw = 'zendesk'
zduser = 'zendesk'
pghost = 'localhost'
pgport = '5434'
pgdb = 'zendesk'



def construct_pg_url(postgres_user=pguser, postgres_password=pgpw, postgres_host=pghost, postgres_port=pgport, postgres_database=pgdb):
    PG_URL = "postgresql://" + postgres_user + ":" + postgres_password + '@' + postgres_host + ':' + postgres_port + '/' + postgres_database
    return PG_URL

pgconn = dataset.Database(
             url=construct_pg_url(),
             schema='zendesk'
)

conn = psycopg2.connect(
    host=pghost,
	port=pgport,
    database=pgdb,
    user=pguser,
    password=pgpw)


# 	#     strSQL = "INSERT INTO zendesk." + _table + "(id, jdoc) VALUES (" + str(_id) + "," + str(_jdoc) + "::jsonb )"
    # strSQL = "INSERT INTO zendesk." + _table + " SELECT json_populate_recordset(NULL::'" + str(_jdoc) + "', %s);"
    # strSQL = "INSERT INTO zendesk." + _table + "(id, jdoc) VALUES (%i, %s)"

def addRecord(_table, _id, _jdoc):
    cursor = conn.cursor()
    # strSQL = "INSERT INTO zendesk." + _table + " (id, jdoc) VALUES (" + str(_id) + ", '" + json.dumps(_jdoc) + "');"
    strSQL = "INSERT INTO zendesk." + _table + " (id, jdoc) VALUES (%(id)s, %(jd)s);" # + str(_id) + ", '" + json.dumps(_jdoc) + "');"
    # print(strSQL, _id, json.dumps(_jdoc))
    cursor.execute(strSQL, {'id':_id, 'jd': json.dumps(_jdoc)})
    cursor.close()
    conn.commit()

def trace (_text):
	if _trace:
		print('================================================================================', file=sys.stderr)
		print(_text, file=sys.stderr)


headers = {
	"Content-Type": "application/json",
}

# ================================================================================
# get groups data 
# ================================================================================
trace('Obtaining groups data')
url = "https://nolsupport.zendesk.com/api/v2/groups"

response = requests.request(
	"GET",
	url,
	auth=(zduser, zdpw),
	headers=headers
)

data = json.loads(response.text)
groups = data['groups']
table = pgconn['groups']
# rows = [dict(foo='bar', baz='foo')] * 10000
table.insert_many(groups)

trace('Writing groups data to file')

# write the groups data to a file groups.json
output_json = json.dumps(groups)
with open('groups.json', 'w') as outfile:
	json.dump(output_json, outfile)


# ================================================================================
# get users
# ================================================================================
trace('Obtaining users data')

url = "https://nolsupport.zendesk.com/api/v2/users?role[]=agent&role[]=end-user&role[]=admin"

response = requests.request(
	"GET",
	url,
	auth=(zduser, zdpw),
	headers=headers
)

data = json.loads(response.text)
users = data['users']   # users are paginated as well
i = 2
while data['next_page'] is not None and i < maxindex:
	url = data['next_page']
	trace ('iteration: ' + str(i))
	response = requests.request(
		"GET",
		url,
		auth=(zduser, zdpw),
		headers=headers
	)
	if response.status_code == 429:
		print('Rate limited, wait a bit')
		time.sleep(int(response.headers['retry-after']))
		continue
	data = json.loads(response.text)
	users.extend(data['users'])
	i=i+1

# now loop through the rest of the users
# table = pgconn['users']
# table.insert_many(users)  # this fails with an internal error
# next is slower, but works
i = 1
for user in users:
	addRecord('users', user['id'], user)
	i = i + 1
	if i % 50 == 0:
		trace('written ' + str(i) + ' users to the database')

trace('Writing users data to file')

output_json = json.dumps(users)
with open('users.json', 'w') as outfile:
	json.dump(output_json, outfile)

# ================================================================================
# get the tickets
# ================================================================================
url = "https://nolsupport.zendesk.com/api/v2/incremental/tickets/cursor.json?start_time=1332034771"

trace('Obtaining tickets data')
response = requests.request(
	"GET",
	url,
	auth=(zduser, zdpw),
	headers=headers	
)

# obtain last cursor
data = json.loads(response.text)   # transform the json object to an array
url = data["after_url"]
eos = data['end_of_stream']
tickets = data['tickets']

index = 1
# print(index, eos, url, file=sys.stderr)
while eos == False and index < maxindex:
	response = requests.request(
		"GET",
		url,
		auth=(zduser, zdpw),
		headers=headers
	)
	data = json.loads(response.text)
	url = data["after_url"]
	eos = data['end_of_stream']
	tickets.extend(data['tickets']) # add the new batch to the existing array
	index = index + 1  # a safety mechanism against endless loops
	trace(str(index) + ' - ' + str(eos) + ' - ' + url)  # used for tracing

# convert the array of tickets back to json
trace('Writing tickets to file')
output_json = json.dumps(tickets)
# print(output_json)   # dump the actual tickets to the stdout
with open('tickets.json', 'w') as outfile:
    json.dump(json.dumps(tickets), outfile)


# ================================================================================
# obtain the comments
# and while looping through the tickets anyway, write each record to the database
# ticket id's: 3581; 3605   -- 'https://nolsupport.zendesk.com/api/v2/tickets/11/comments'
# 'https://nolsupport.zendesk.com/api/v2/tickets/22/comments'
# ================================================================================
allcomments = []
trace ('Start writing tickets to database and obtain the comments related to each ticket')
i = 1
for ticket in tickets:
	addRecord('tickets', ticket['id'], ticket) # write to the database
	# -- get the comments for this ticket
	url = 'https://nolsupport.zendesk.com/api/v2/tickets/' + str(ticket['id']) + '/comments'
	# print(url, file=sys.stderr)   # a bit of tracing info
	response = requests.request(
		"GET",
		url,
		auth=(zduser, zdpw),
		headers=headers
	)
	if response.status_code == 429:
		print('Rate limited, wait a bit')
		time.sleep(int(response.headers['retry-after']))
		continue
	# response now holds the comments
	# print(str(ticket['id']), file=sys.stderr)
	# print(response.text)
	data = json.loads(response.text)
	comments = data['comments']
	allcomments.extend(comments)
	for comment in comments:
		addRecord('comments', comment['id'], comment)
	i = i + 1
	if i > 52:
		break
	if i % 50 == 0:
		trace('written ' + str(i) + ' tickets with comments to the database')

# output_json = json.dump(comments)
# with open('comments.json', 'w') as outfile:
# 	json.dump(json.dumps(comments), outfile)

# some additional data that needs downloading
# url = 'https://nolsupport.zendesk.com/api/v2/users'

    # "requester_id": 376794459471,
    # "submitter_id": 376794459471,
	#	 GET /api/v2/users
	# 	GET /api/v2/users/{user_id}/organizations.json
    # "assignee_id": 361231612032, # assignees
    # "group_id": 360000322151,    # groups
	#	GET /api/v2/groups
	#	GET /api/v2/users/{user_id}/groups
	#	 GET /api/v2/groups/{group_id}/users
	# "organisation"   # NOT filled
	# 	GET /api/v2/organizations
	#	 GET /api/v2/organizations/{organization_id}/users
    # "brand_id": 360000198171,    # brands
# GET /api/v2/tickets/{ticket_id}/comments    # get the comments -- needs to loop through the tickets to check if there is a thread of comments

#url = "https://nolsupport.zendesk.com/api/v2/users?external_id=abc&permission_set=123&role=agent&role[]=agent"

# old stuff
# import psycopg2   # needed for interaction with postgres
# import database

# open the database connection - close it when done
# conn = psycopg2.connect("dbname=zendesk user=respval password=XHmpkbrhUCmpjf86whIw")

# conn = psycopg2.connect(
#     host="localhost",
# 	port="5434",
#     database="zendesk",
#     user="zendesk",
#     password="zendesk")


# # 	#     strSQL = "INSERT INTO zendesk." + _table + "(id, jdoc) VALUES (" + str(_id) + "," + str(_jdoc) + "::jsonb )"
# def addRecord(_table, _id, _jdoc):
#     cursor = conn.cursor()
#     # strSQL = "INSERT INTO zendesk." + _table + " SELECT json_populate_recordset(NULL::'" + str(_jdoc) + "', %s);"
#     strSQL = "INSERT INTO zendesk." + _table + "(id, jdoc) VALUES (%i, %s)"
#     cursor.execute(strSQL, _id, json.dumps(_jdoc))
#     cursor.close()
#     conn.commit()

# query_sql = """
# insert into json_table select * from
# json_populate_recordset(NULL::json_table, %s);
# """
