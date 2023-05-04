from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'customer'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('AddCus.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addcus", methods=['POST'])
def AddCus():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    cus_image_file = request.files['cus_image_file']

    insert_sql = "INSERT INTO customer VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if cus_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (first_name, last_name, email, password))
        db_conn.commit()
        cus_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        cus_image_file_name_in_s3 = "last_name-" + str(last_name) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=cus_image_file_name_in_s3, Body=cus_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                cus_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddCusOutput.html', name=cus_name)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

