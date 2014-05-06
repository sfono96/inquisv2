from csv_io import *
import psycopg2, os, urlparse, json
from math import trunc
from datetime import date, timedelta, datetime #(need datetime.strptime for the unicode date YYYYMMDD conversion)



cwd = os.getcwd() # working directory for static files
path = cwd+'/static/standards_data_complete.csv'

############ DB CONNECTION ############ 

production = True # set this to true if pushing changes to production server (heroku) else keep false on development box

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
	sql = 'SELECT grade_level, ROUND(AVG(proficient),2) ppa, COUNT(*) students FROM vw_average_high_scores WHERE grade_level IS NOT NULL GROUP BY grade_level'
	cursor.execute(sql)
	rs = cursor.fetchall()
	obj = [{"grade":r[0],"ppa":str(r[1]),"count":str(r[2])} for r in rs]
	return sorted(obj,key=lambda k: k["grade"])

####### CHART 2 - Assessments by grade level (last 8 assessments)
def recent_assessment_data():
	#sql = 'SELECT * FROM vw_assessment_averages WHERE rowcnt <= 8 AND grade_level IS NOT NULL'
	sql = 'SELECT * FROM vw_assessment_averages WHERE grade_level IS NOT NULL'
	cursor.execute(sql)
	rs = cursor.fetchall()
	grades = set(sorted([r[0] for r in rs]))
	obj = {}
	for g in grades:
		obj[g]=sorted([{"grade":r[0],"assessment":r[1],"domain":'NBT',"standard":'',"date":r[2].strftime("%m/%d"),"strength":str(r[4])} for r in rs if r[0]==g],key=lambda k:k['date'])
	return obj

####### CHARTS 3 - Teacher Comps - Scores
def teacher_comps_score(grade):
	sql = 'SELECT *,LEFT(teacher,POSITION(\',\' IN teacher)-1) FROM vw_teacher_attempts WHERE grade_level = %s' % grade
	cursor.execute(sql)
	rs = cursor.fetchall()
	obj = {}
	assessments = set([r[2] for r in rs])
	for a in assessments:
		obj[a] = [{"teacher":r[8],"0":int(r[3]),"1":int(r[4]),"2":int(r[5]),"3":int(r[6]),"4":int(r[7])} for r in rs if r[2] == a]
	return obj

####### CHART 4 - Single Teacher Attempts
def single_teacher_attempts(grade):
	sql = 'SELECT *,LEFT(teacher,POSITION(\',\' IN teacher)-1) FROM vw_single_teacher_attempts WHERE grade_level = %s AND attempt IS NOT NULL' % grade
	cursor.execute(sql)
	rs = cursor.fetchall()
	obj = {}
	assessments = set([r[1] for r in rs])
	teachers = set([r[9] for r in rs])
	for a in assessments:
		obj[a] = {}
		for t in teachers:
			obj[a][t] = sorted([{"attempt":int(r[3]),"0":int(r[4]),"1":int(r[5]),"2":int(r[6]),"3":int(r[7]),"4":int(r[8])} for r in rs if r[9] == t and r[1] == a],key=lambda k: k["attempt"])
	return obj

####### TABLE 4 - Table data (still need positions and prior year scores)
def student_table_data(grade):
	sql = 'SELECT *,LEFT(teacher,POSITION(\',\' IN teacher)-1) FROM vw_student_attempts WHERE grade_level = %s' % grade
	cursor.execute(sql)
	rs = cursor.fetchall()
	obj = {}
	assessments = set([r[1] for r in rs])
	for a in assessments:
		obj[a] = [[r[8],r[3],170,str(r[4]),str(r[5]),str(r[6]),str(r[7])] for r in rs if r[1] == a]
	return obj

####### CHART 5 - Teacher Comps - Growth Line Chart
def teacher_comps_growth(grade):
	sql = 'SELECT * FROM vw_student_attempts_cumulative_flat WHERE assessment_group_name IS NOT NULL AND grade_level = %s ORDER BY 1,2,3,4' % grade
	cursor.execute(sql)
	rs = cursor.fetchall()
	obj = {}
	assessments = set([r[1] for r in rs])
	for a in assessments:
		obj[a] = []
		relevant_teachers = set([r[2] for r in rs if r[1] == a])
		for t in relevant_teachers:
			arr = []
			for r in rs:
				for i in range(3,6):
					if r[i] is not None and r[2] == t and r[1] == a:
						arr.append({"attempt":str(i-2),"score":str(r[i]),"teacher":t})
			obj[a].append(arr)
	return obj

# for r in teacher_comps_growth("4")['PLC -Mult.3/4digit by 1 test']:
# 	print r