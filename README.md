# SS-CMS
## (Simple Serverless CMS)

https://github.com/pratermade/pratermade-cms/issues

This is a simple CMS that uses Django, Zappa and other open source projects to build a basic serverless Content Management System.
It uses AWS Lambda, AWS RDS, and AWS S3 to do all the hosting. It is hoped that a release build will allow for the use of S3 for the database, removing the cost of RDS.

**This is a very early release, almost functional even. Under rapid development.**
## Installation

1. Requires python3.6
2. Create a virtualenv with python3.6
3. pip install -r requirements.txt
4. Create S3 Bucket for 'static' that is publicly readable
5. Create 'or use' an RDS instance for the database. Tested with MariaDB
6. cp pratermade/settings.py.example pratermade/settings.py
7. Setup your ALLOWED_HOSTS = ['your.domain.com']
8. Update the AWS_STORAGE_BUCKET_NAME = [the bucket you created]
9. Update the database information
10. ./manage.py migrate
11. ./manage.py createsuperuser
12. zappa init 
13. zappa deploy
14. ./manage.py collectstatic --noinput
 
## Features

- User/Group permissions per page.
- Dynamic Bread Crumbs (Coming Soon)
- Dynamic menu based on permissions and content 

 
## GIT help
1. git add .
2. git commit -m "comment goes here"
3. git push wosc wosc (local branch to gogs.wosc.edu server)
4. git pull origin master
5. *fix merge conflicts*
6. git add .
7. git commit
8. IF model changes:
* manage.py makemigrations
* manage.py migrate
