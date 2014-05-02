from csv_io import *
import psycopg2, os, urlparse, json
from math import trunc
from datetime import date, timedelta, datetime #(need datetime.strptime for the unicode date YYYYMMDD conversion)



cwd = os.getcwd() # working directory for static files
path = cwd+'/static/standards_data_complete.csv'

############ DB CONNECTION ############ 

production = False # set this to true if pushing changes to production server (heroku) else keep false on development box

if production == False:

	# development server (local box)
	host = 'localhost'
	dbname = 'inquisv2'
	user = 'postgres'
	password = 'password'
	conn_string = 'host=%s dbname=%s user=%s password=%s' %(host,dbname,user,password)
	conn = psycopg2.connect(conn_string)

else:

	#production server (heroku)
	urlparse.uses_netloc.append("postgres")
	url = urlparse.urlparse(os.environ["DATABASE_URL"])

	conn = psycopg2.connect(
	    database=url.path[1:],
	    user=url.username,
	    password=url.password,
	    host=url.hostname,
	    port=url.port
	)

# cursor object
cursor = conn.cursor()

###############################################################################################################################################
################################################################# VICKI V2 ####################################################################
###############################################################################################################################################

####### CHART 1 - Grade level data object 
def grade_level_data():
	sql = 'SELECT grade_level, ROUND(AVG(proficient),2) ppa, COUNT(*) students FROM vw_average_high_scores GROUP BY grade_level'
	cursor.execute(sql)
	rs = cursor.fetchall()
	obj = [{"grade":r[0],"ppa":str(r[1]),"count":str(r[2])} for r in rs]
	return sorted(obj,key=lambda k: k["grade"])

####### CHART 2 - Assessments by grade level (last 8 assessments)
def recent_assessment_data():
	sql = 'SELECT * FROM vw_assessment_averages WHERE rowcnt <= 8'
	cursor.execute(sql)
	rs = cursor.fetchall()
	grades = set(sorted([r[0] for r in rs]))
	obj = {}
	for g in grades:
		obj[g]=sorted([{"grade":r[0],"assessment":r[1],"domain":'',"standard":'',"date":r[2].strftime("%m/%d"),"strength":str(r[4])} for r in rs if r[0]==g],key=lambda k:k['date'])
	return obj


