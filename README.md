# Flexibees Candidate Backend

This repo is specifically for candidate specific operations 

### System Requirements
- Python 3+, (use python 3.8.18 or 3.8.20)

------------
### 1. Create of virtual environment
Open the terminal and enter the following command:`pyenv exec python -m venv venv` or  <br />`$ virtualenv venv`<br />
Once the environment has been created, activate the environment:<br />`$ source venv activate`

------------
### 2. Clone project to the local machine
In the terminal, navigate to the location where the project folder has to be created. Then enter the git command to clone the project:<br />`$ git clone https://github.com/appinessgit/flexibees-bed.git` <br />
Once cloned, change the directory to **flexibees_candidate**<br /> `$ cd flexibees_candidate`

------------
### 3. Install the project requirements
Install the python packages listed in the **requirements.txt** file.

pip install --upgrade setuptools wheel
pip install --upgrade backports.zoneinfo
Enter the following command in the terminal:<br />`$ pip install -r requirements.txt`   [Use cmd , not VSCode]

------------
nv
### 4. Run the development server
To start the development server, run the following command:<br />`$ python manage.py runserver` <br />
By default the server runs on port`8000`<br />
Check whether the server is running by going to [localhost:8000/admin](localhost:8000/admin "localhost:8000/admin") <br />
Swagger URL: [localhost:8000](localhost:8000 "localhost:8000")

------------
#### References
Django : https://docs.djangoproject.com/en/3.1/
