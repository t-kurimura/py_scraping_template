# This Repository

The py_scraping_template repository contains a Python script for scraping data from a certain website and inserting the retrieved data into a Firestore database.

## Setup

The following tools and packages are required to run the scripts in this repository.

- Docker
- Docker Compose
- Python 3.7 or higher

### Step 1: Clone the Repository

Clone this repository to your local machine:

### Step 2: Create Directories on the Remote Instance

Run the following command to create directories on the remote instance:

```
make remote-create-dir
```

This command creates the following directories:

- `/usr/local/hoge_board_scraping/logs`
- `/usr/local/hoge_board_scraping/chrome`
- `/usr/local/hoge_board_scraping/cred`
- `/usr/local/hoge_board_scraping/script/images`

### Step 3: Install Docker and Docker Compose on the Remote Instance

Run the following commands to install Docker and Docker Compose on the remote instance:

```
make remote-install-docker
make remote-install-docker-compose
```

### Step 4: Change files in ./cred directories

#### hoge-board-ipass
```
ID={Your Id}
PASSWORD={Your  password}
```

#### firebase-adminsdk.json
To obtain the Firebase Admin SDK JSON file, follow these steps:

1. Go to the Firebase console and select your project.
2. Click on the gear icon at the top left corner and select "Project settings."
3. Navigate to the "Service accounts" tab and click on "Generate new private key."
4. A JSON file containing your private key will be downloaded to your computer.
5. Make sure to keep the private key in a secure location and not to share it with anyone who should not have access to your Firebase project.

### Step 5: Copy Files to the Remote Instance

Run the following command to copy the necessary files to the remote instance:

```
make scp-all
```

This command copies the following files:

- `docker-compose.yml`
- `python-selenium/`
- `script/`
- `cred/`

### Step 6: Rebuild and Restart the Python Container

Run the following command to rebuild and restart the Python container:

```
make rebuild-restart-python
```

### Step 7: Start Scraping

To start scraping, run the following command:

```
make ssh
```

This command logs you into the remote instance. Then, run the following command to start scraping:

```
cd /usr/local/hoge_board_scraping/
docker-compose up -d
```

### Note

The `docker-compose.yml` file is used to start the Selenium Grid and Python containers. 
This file specifies the following services:

- selenium-hub: Selenium Grid hub
- chrome: Selenium Chrome node
- python: Python container that runs the scraping script

The `python` container is built using the `python-selenium` directory, which contains the necessary packages and dependencies to run the scraping script.

The `script` directory contains the Python script for scraping the