import swiftclient
import os
import hashlib
import MySQLdb
import swiftclient
from flask import Flask, render_template,request, redirect,flash,url_for,send_from_directory
from cryptography.fernet import Fernet
from werkzeug import secure_filename
from stat import * # ST_SIZE

key = Fernet.generate_key()
cipher_suite = Fernet(key)

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']
	

user = ''
password = ''
projectid = ''
regionname = ''
userid=""
project=""


connection = swiftclient.Connection(
        user=user,
        key=password,
        authurl='https://identity.open.softlayer.com/v3',
		auth_version='3',
		os_options={"project_id": projectid,
                    "user_id": userid,
                    "region_name": regionname
							 }
						
	
)


# connect
db = MySQLdb.connect(host="us-cdbr-iron-east-04.cleardb.net", 
					user="b2147326e0439e",
					passwd="00da2a67",
					db="ad_d75ac0c204babdf")

cursor = db.cursor()

# execute SQL select statement
cursor.execute("SELECT * FROM user")

# commit your changes
db.commit()

# get the number of rows in the resultset
numrows = int(cursor.rowcount)

# get and display one row at a time.
for x in range(0,numrows):
    row = cursor.fetchone()
    print row[0], "-->", row[1]
	
db.close()

container_name = 'MyCloudData'
connection.put_container(container_name);
print "\nContainer %s created successfully." % container_name


# List your containers
print ("\nContainer List:")
for container in connection.get_account()[1]:
    print container['name']
	

		
print "------------------------"
	
# List objects in a container, and prints out each object name, the file size, and last modified date
print ("\nObject List:")
for container in connection.get_account()[1]:
    for data in connection.get_container(container['name'])[1]:
		print 'File: {0}\t Size: {1}\t Date: {2}'.format(data['name'], data['bytes'], data['last_modified'])
		

	
@app.route('/')
@app.route('/index')
def main():
	
	return	"""
	<!DOCTYPE html>
	<html lang='en'>
	  <head>
		<title>Cloud App</title>
	 
		
		<link href='http://getbootstrap.com/dist/css/bootstrap.min.css' rel='stylesheet'>
	 
		<link href='http://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css' rel='stylesheet'>
	
		
	  </head>
	 
	  <body>
	 
		<div class='container'>
		  <div class='header'>
			<nav>
			  <ul class='nav nav-pills pull-right'>
				<li role='presentation' ><a href='main'>Home</a></li>
				<li role='presentation'><a href='#'>Sign In</a></li>
				<li role='presentation' class='active'><a href='#'>Sign Up</a></li>
			  </ul>
			</nav>
			<h3 class='text-muted'>Cloud App</h3>
		  </div>
	 
		  <div class='jumbotron'>
			<h1>Bucket List App</h1>
			<form method='POST' action='/homepage' class='form-signin' enctype=multipart/form-data>
			<label for='inputName' class='sr-only'>Username</label>
			<input type='name' name='uname' id='inputName' class='form-control' placeholder='Username' required autofocus>
			<label for='inputPassword' class='sr-only'>Password</label>
			<input type='password' name='password' id='inputPassword' class='form-control' placeholder='Password' required>
			 <p><input class="btn btn-lg btn-primary" type=submit value=Submit></p>
			
		  </form>
		  </div>
	 
		   
	 
		  <footer class='footer'>
			<p>&copy; Company 2015</p>
		  </footer>
	 
		</div>
	  </body>
	</html>
	"""	

userid = 0
def set_userid(id):
    global userid    # Needed to modify global copy of globvar
    userid = id
def get_userid():
    return userid

spacelimit = 0
def set_spacelimit(id):
    global spacelimit    # Needed to modify global copy of globvar
    spacelimit = id

def get_spacelimit():
    return spacelimit
	
spaceused = 0
def set_spaceused(id):
    global spaceused    # Needed to modify global copy of globvar
    spaceused = id

def get_spaceused():
    return spaceused	


@app.route('/homepage',methods=['POST'])
def homepage():
	uname =  request.form["uname"]
	pwd =  request.form["password"]
	db = MySQLdb.connect(host="us-cdbr-iron-east-04.cleardb.net", 
					user="b2147326e0439e",
					passwd="00da2a67",
					db="ad_d75ac0c204babdf")
	cursor = db.cursor()
	cursor.execute("SELECT * FROM user WHERE uname='"+uname+"' AND password='"+pwd+"'")
	db.commit()
	numrows = int(cursor.rowcount)
	
	if numrows>0:
		# get and display one row at a time.
		for x in range(0,numrows):
			row = cursor.fetchone()
			set_userid(int(row[0]))
			set_spacelimit(int(row[3]))
			
		cursor1 = db.cursor()
		cursor1.execute("SELECT * FROM user_storage WHERE uid = '"+str(get_userid())+"'")
		db.commit()
		total = 0
		numinrows = int(cursor1.rowcount)
		if numinrows>0:
			for x in range(0,numinrows):
				row = cursor1.fetchone()
				total = total + int(row[3])
				set_spaceused(total)
				
			listfileshtml=""
			listfileshtml=listfileshtml+"<div>Total Space Used:"
			listfileshtml=listfileshtml+str(get_spaceused())+"/"+str(get_spacelimit())
			listfileshtml=listfileshtml+"</div>"
			
			listfileshtml=listfileshtml+"<tr>"
			listfileshtml=listfileshtml+"<td>#</td>"
			listfileshtml=listfileshtml+"<td>FileName\t</td>"
			listfileshtml=listfileshtml+"<td>Size\t</td>"
			listfileshtml=listfileshtml+"<td>Version\t</td>"
			listfileshtml=listfileshtml+"</tr>"	
			
			cursor2 = db.cursor()
			cursor2.execute("SELECT * FROM user_storage WHERE uid = '"+str(get_userid())+"'")
			db.commit()
			results = cursor2.fetchall()
			for row in results:
				print str(row[6])
				listfileshtml=listfileshtml+"<tr>"
				listfileshtml=listfileshtml+"<td><input name='checks' type='checkbox' id='checks' value="+str(row[0])+"\t</td>"
				listfileshtml=listfileshtml+"<td>"+str(row[2])+"\t</td>"
				listfileshtml=listfileshtml+"<td>"+str(row[3])+"\t</td>"
				listfileshtml=listfileshtml+"<td>"+str(row[6])+"\t</td>"
				listfileshtml=listfileshtml+"</tr>"
				

		
		listfileshtml = "<table class='table table-striped'>"+listfileshtml+"</table>"

		db.close
		return """
		   <!DOCTYPE html>
			<html lang="en">
				<head>
				<title>Cloud Assign 1</title>
			 
				
				<link href="http://getbootstrap.com/dist/css/bootstrap.min.css" rel="stylesheet">
			 
				<link href="http://getbootstrap.com/examples/jumbotron-narrow/jumbotron-narrow.css" rel="stylesheet">
				<link href="mystyle.css" rel="stylesheet">
				
			  </head>
			 
			  <body>
			 

				<div class="container">
				  <div class="header">
					<nav>
					  <ul class="nav nav-pills pull-right">
						<li role="presentation" ><a href="main">Home</a></li>
						<li role="presentation"><a href="#">Sign In</a></li>
						<li role="presentation" class="active"><a href="#">Sign Up</a></li>
					  </ul>
					</nav>
					<h3 class="text-muted">Cloud App</h3>
				  </div>
				
				<div class="list-files-box">
					
					<h3>List of Files</h3>
					<form action='process' method='POST' enctype=multipart/form-data>
					<div id='listfiles' class="table-title">
					%s
					</div>
					</form>
				</div>
			  
				<div id='innerdiv'class="jumbotron">
					
					<form action="upload" method=post enctype=multipart/form-data>
					  <p><input type=file name=file><input class="btn btn-lg btn-primary" type=submit value=Upload></p>
					</form>	
				  
				  
				</div>
			 
				   
			 
				  <footer class="footer">
					<p>&copy; Cloud UTA 2016</p>
				  </footer>
			 
				</div>
			  </body>
			</html>
				
			  

			
			""" % listfileshtml
	else:
		return """
            <!doctype html>
            <title>Wrong Paswword</title>
            <h1>Wrong Username or Password.Please try again</h1>
			</html>
            """ 
	
# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    # Get the name of the uploaded file
	file = request.files['file']
	filename = secure_filename(file.filename)
	blob = request.files['file'].read()
	size = len(blob)
	print (file.read())
	
	if int(size)+int(get_spaceused()) < int(get_spacelimit()):
		# Check if the file is one of the allowed types/extensions
		if file and allowed_file(file.filename):
			# Make the filename safe, remove unsupported chars
			filecontent = file.read()
			hashedFileContent= hashlib.md5(str(filecontent)).hexdigest()
		
		db = MySQLdb.connect(host="us-cdbr-iron-east-04.cleardb.net", 
						user="b2147326e0439e",
						passwd="00da2a67",
						db="ad_d75ac0c204babdf")
		cursor = db.cursor()
		cursor.execute("SELECT fid,md5,version FROM user_storage o1 WHERE filename = '"+filename+"' AND version = (SELECT MAX(version) FROM user_storage o2 WHERE o1.fid = o2.fid) GROUP BY version DESC LIMIT 1;")
		db.commit()
		numrows = int(cursor.rowcount)
		version =0
		query = ''
		v=0
		if numrows>0:
			for x in range(0,numrows):
				row = cursor.fetchone()
				oldmd5 = row[1]
				version = row[2]
			print oldmd5
			print hashedFileContent
			if oldmd5 == hashedFileContent:
				message = 'Same File already present'
				return """
						<!doctype html>
						<title>Uploaded</title>
						<h1>%s</h1>
						</html>
						"""%message
			else:
				try:
					v = version + 1
				except TypeError:
					v=1
				query = "INSERT INTO user_storage VALUES (null,'"+str(get_userid())+"','"+filename+"','"+str(size)+"',%s,'"+str(hashedFileContent)+"','"+str(v)+"')"
				message = 'File Uploaded Sucessfully'
		else:
			query = "INSERT INTO user_storage VALUES (null,'"+str(get_userid())+"','"+filename+"','"+str(size)+"',%s,'"+str(hashedFileContent)+"','1')"
			message = 'File Uploaded Sucessfully'
		
		cursor1 = db.cursor()
		cursor1.execute(query, (blob, ))
		db.commit()
		db.close
		
		return """
			<!doctype html>
			<title>Uploaded</title>
			<h1>%s</h1>
			</html>
			"""%message
	else:
		return """
			<!doctype html>
			<title>Space Limit</title>
			<h1>Space Limit reached</h1>
			</html>
			"""
	# Redirect the user to the uploaded_file route, which
	# will basicaly show on the browser the uploaded file
	return redirect(url_for('uploaded_file',
							filename=filename))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],
							   filename)

@app.route('/process', methods=['POST'])
def download():
	list =  request.form.getlist('checks')
	any_selected = bool(list)
	myvar =  request.form["button"]
	if any_selected:
		if myvar == 'Download':
			for name in list:
				obj = connection.get_object(container_name, name)
				encrypt_string = obj[1]
				plain_text = cipher_suite.decrypt(encrypt_string)
				with open('downloaded-'+name, 'wb+') as my_example:
					 my_example.write(plain_text)
				text = 'File has been downloaded'
		else:
			for name in list:
				connection.delete_object(container_name, name)
			text = 'File has been deleted'
	else:
		text = 'No files selected'
	return """
            <!doctype html>
            <title>List</title>
            <h1>hi%s</h1>
			</html>
            """ % text  


	
port = os.getenv('VCAP_APP_PORT','6060')
if __name__ == '__main__':
	app.secret_key = 'helloworld'
	app.run(host='127.0.0.1',port=int(port))

