# XDrive 💿📈

## Team Members 🧑‍💼🧑‍💼
| Name            | Email                     | GitHub User    |
|-----------------|---------------------------|----------------|
| Roger Huauya Mamani | roger.huauya@utec.edu.pe | [Rogerhuauya](https://github.com/Rogerhuauya) |
| Jonathan Quilca Valenzuela | jonathan.quilca@utec.edu.pe | [jonyyy1](https://github.com/jonyyy1) |
| Alvaro Garcia Hurtado | alvaro.garcia.h@utec.edu.pe | [AlvaUtec](https://github.com/AlvaUtec) |
| Juan Diego Castro | juan.castro.p@utec.edu.pe | [ByJuanDiego](https://github.com/ByJuanDiego) |
## Description

This project aims to create a file storage system that allow users to upload, download files, providing a unique URL for each file uploaded. The project is built using Django and Django Rest Framework.

## Table of Contents

- [XDrive 💿📈](#xdrive-)
  - [Team Members 🧑‍💼🧑‍💼](#team-members-)
  - [Description](#description)
  - [Table of Contents](#table-of-contents)
  - [Public Repository 📁🔗](#public-repository-)
  - [Task Overview 📝📈](#task-overview-)
  - [Installation 💻🔧](#installation-)
    - [Requirements 🔍✔️](#requirements-️)
    - [Setting up Docker environment 🐳🔧🛠️](#setting-up-docker-environment-️)
      - [Prerequisites](#prerequisites)
      - [For Windows and macOS:](#for-windows-and-macos)
      - [For Linux:](#for-linux)
    - [Docker Compose Workflow Guide 🚀🐳](#docker-compose-workflow-guide-)
      - [Starting Docker Compose](#starting-docker-compose)
      - [Checking Container Status](#checking-container-status)
      - [Entering the Shell of a Container](#entering-the-shell-of-a-container)
      - [Entering ZSH Terminal (Optional)](#entering-zsh-terminal-optional)
      - [Exiting the Container's Shell](#exiting-the-containers-shell)
    - [Setting up Django environment 🐍🛠️](#setting-up-django-environment-️)
      - [Prerequisites](#prerequisites-1)
      - [Django Workflow Guide](#django-workflow-guide)
    - [Running Tests 🏃‍♂️🔬](#running-tests-️)
  - [Usage 🔄💻](#usage-)
    - [API Endpoints](#api-endpoints)
      - [File Upload](#file-upload)
      - [File Download](#file-download)
  - [License 📜⚖️](#license-️)


## Public Repository 📁🔗
- **Github URL**: https://github.com/RogerHuauya/XDrive

## Task Overview 📝📈

This project has been created using Github Projects. You can access the project board by visiting the following URL:

- **Github Project Board**: [XDrive Project Board](https://github.com/users/RogerHuauya/projects/7)

## Installation 💻🔧

### Requirements 🔍✔️

- Python 3.9
- Django 5.02
- Django Rest Framework 3.14
- Docker
- Docker Compose
  Make sure you have the above requirements installed before proceeding. Try running the following command to install them:

```bash
pip install -r requirements.txt
```

After, you can proceed to check if they are installed correctly by running the following command:

```bash
python --version
docker --version
docker-compose --version
djangorestframework --version
```

### Setting up Docker environment 🐳🔧🛠️
_________________________________

This section provides step-by-step instructions on
how to set up and work with the literal project using Docker and Docker Compose

#### Prerequisites

Before you begin, you need to install Docker.
Follow these steps based on your operating system:

#### For Windows and macOS:

1. *Download Docker Desktop*: Go to the [Docker Desktop website](https://www.docker.com/products/docker-desktop) and download the appropriate installer for your operating system.

2. *Install Docker Desktop*: Run the installer and follow the on-screen instructions.

#### For Linux:

1. *Download Docker Engine*: Go to the [Docker Engine website](https://docs.docker.com/engine/install/) and follow the instructions for your Linux distribution.
2. *Download Docker Compose*: Go to the [Docker Compose website](https://docs.docker.com/compose/install/) and follow the instructions for your Linux distribution.
3. *Add your user to the docker group*: Run the following command in your terminal:
   bash
   sudo usermod -aG docker $USER

   You will need to log out and log back in for this to take effect.
4. *Verify that Docker is installed correctly*: Run the following command in your terminal:
   bash
   docker run hello-world

   This command downloads a test image and runs it in a container. When the container runs, it prints an informational message and exits.
5. *Verify that Docker Compose is installed correctly*: Run the following command in your terminal:
   bash
   docker-compose --version

   This command prints the version number of Docker Compose.

### Docker Compose Workflow Guide 🚀🐳

#### Starting Docker Compose

- *Navigate to the literal project root folder*:

Replace DB variables in .env in order to use docker db

DB_HOST='db'
DB_NAME='postgres'
DB_USER='postgres'
DB_PASSWORD='postgres'
DB_PORT=5432

- *Start Docker Compose*:
  bash
  docker-compose up

  Add -d to run containers in the background.

#### Checking Container Status

- *List Active Containers*:
  bash
  docker ps

  This will show container IDs, names, and status.

#### Entering the Shell of a Container

- *Find the Container ID or Name* (use docker ps to list running containers):
  bash
  docker ps


- *Access the Container's Shell*:
  Replace container_id_or_name with your container's ID or name.
  bash
  docker exec -it <container_id_or_name> /bin/bash


#### Entering ZSH Terminal (Optional)

- *Once in the Container's Shell*:
  bash
  exec zsh


#### Exiting the Container's Shell

- To exit the shell without stopping the container:
  bash
  exit


### Setting up Django environment 🐍🛠️

#### Prerequisites

Before you begin, you need to install Python and Django.
Follow these steps based on your operating system:

1. *Install Python*: Go to the [Python website](https://www.python.org/downloads/) and download the latest version of Python.
2. *Install Django*: Run the following command in your terminal:
   bash
   pip install django

   You can also install a specific version of Django by running:
   bash
   pip install django==3.2

#### Django Workflow Guide

- *Navigate to the literal project root folder*:
- *Run Migrations*:
  ```bash
  python manage.py migrate
  ```

- *Run the Server*:
  ```bash
    python manage.py runserver
    ```

#### Accessing the API

After running the server, you can access the API by visiting the following URL in your browser:

```bash
http://127:0.0.1:8000
```

### Running Tests 🏃‍♂️🔬

- *Navigate to the literal project root folder*:
- *Run Tests*:
  ```bash
  python manage.py test
  ```


## Usage 🔄💻

APIs have been implemented using Django Rest Framework. The project has been containerized using Docker and Docker Compose. The project has been tested using Django's built-in testing framework.

All endpoints can be found by running the project and visiting the following URL:

```bash
http://127:0.0.1:8000/docs
```

### API Endpoints

- /
- api/chunked_upload_complete/
- api/chunked_upload/,
- api/my_chunked_uploads/


#### File Upload

- *URL*: /api/chunked_upload/
- *Method*: POST
- *Description*: Uploads a file in chunks.
- *Request Body*:
    - *file*: The file to be uploaded.
    - *filename*: The name of the file.
    - *offset*: The offset of the file.
    - *upload*: The upload ID.
- *Response*:
- *Status Code*: 200
- *Response Body*:
    - *message*: The message indicating the file was uploaded successfully.


#### File Download
- *URL* /api/my_chunked_uploads/
- *Method*: GET
- *Description*: Lists all the files uploaded in the system and their URLs for download.


- *URL*: /chunked_uploads/<upload_id>/
- *Method*: GET
- *Description*: Downloads a file by its upload ID.


## License 📜⚖️

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Happy coding! ✨👩‍💻👨‍💻