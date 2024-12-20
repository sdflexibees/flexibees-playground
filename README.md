# Flexibees Candidate Backend

This repo is specifically for candidate specific operations 

### System Requirements
- Python 3+, (use python 3.8.18 or 3.8.20)   [python --version]
- pip 23
------------
### 1. Create of virtual environment
Open the terminal and enter the following command:`pyenv exec python -m venv venv` or  <br />`$ virtualenv venv`<br />
Once the environment has been created, activate the environment:<br />`$ source venv activate`

------------
### 2. Clone project to the local machine
In the terminal, navigate to the location where the project folder has to be created. Then enter the git command to clone the project:<br />`$ git clone https://github.com/appinessgit/flexibees-bed.git` <br />
Once cloned, change the directory to **flexibees_finance**<br /> `$ cd flexibees_finance`

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

Steps to Build and Run the Docker Image:
Build the Image:

```
docker build -t flexibees_app .
```
Run the Container:

```
docker run -p 8000:8000 flexibees_app
```
Test the Application:
Access your Django app in a web browser or via curl at:

arduino
Copy code
http://localhost:8000


1. Build the Docker Images
```
sudo docker-compose build
```
2. Start the Containers
Start the containers using:
```
sudo docker-compose up
```
- Add -d to run the containers in detached mode
```
docker-compose up -d
```
4. To ensure the containers are running
```
docker ps
```
5. View the logs for debugging if needed:
```
docker-compose logs app
```
or
```
docker-compose logs
```
6. When you’re done, stop the running containers:
```
docker-compose down
```
7. Run the following command to check the Docker service status:
```
sudo systemctl status docker
```
If it's not running, start the Docker daemon
```
sudo systemctl start docker
```
8. 6. Test Docker
Run a basic Docker command to see if it works:
```
sudo docker run hello-world

```
2. Check Docker Daemon Process
Verify if the dockerd process is running:
ps aux | grep dockerd
10.  Stop and Disable the Snap Docker Service
To prevent conflicts, stop the Docker service installed via sna
sudo snap stop docker
sudo snap remove docker
Restart the System Docker Service
Ensure only the system-installed Docker service is running:
sudo systemctl restart docker
sudo systemctl status docker
11. Check Docker Logs for Errors
If the issue persists, inspect the Docker logs:

```
sudo journalctl -u docker.service | tail -n 50
```
12. sudo sysctl vm.overcommit_memory=1

13. Steps to Rebuild and Run
Rebuild the Docker image:

```
docker build -t flexibees-finance .
```
Run the Docker container:
```docker-compose up --build```

14. export PYTHONPATH="/Documents/Flexibees/playground/flexibees-playground:$PYTHONPATH"

15. Analyze Conflicts
Use pipdeptree to visualize dependency conflicts:

```pip install pipdeptree
pipdeptree > dependencies.txt```

16. Use a Tool to Resolve Conflicts
Install and use pip-tools to resolve dependencies:
```pip install pip-tools
pip-compile requirements.txt --output-file resolved-requirements.txt
pip install -r resolved-requirements.txt


```
Re-run the pipdeptree command to verify no conflicts remain:
pipdeptree > dependencies.txt

16. Try Docker Build with Dependency Isolation
Modify your Dockerfile to install dependencies with conflict resolution:
```RUN pip install --no-cache-dir pip-tools \
    && pip-compile /app/requirements.txt --output-file /app/resolved-requirements.txt \
    && pip install --no-cache-dir -r /app/resolved-requirements.txt```

17. Rebuild and start the containers after updating the files:
```sudo docker-compose down
sudo docker-compose build
sudo docker-compose up```

18. Run the following command on the host to set vm.overcommit_memory=1:

sudo sysctl -w vm.overcommit_memory=1

Make the change persistent: To ensure the setting is preserved across reboots, add the setting to /etc/sysctl.conf:
echo "vm.overcommit_memory = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p  # Apply the changes


