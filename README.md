# Rags To Riches
A web game simulation of Game of Life with financial literacy as its theme

## How to use

1. Clone this repository into your local computer by typing this into your terminal `git clone https://github.com/kuanjiahong/flask-projects.git`
2. Create a virtual environment folder in the root folder by typing this into your terminal. For Windows: `py -m venv env`. For Unix/macOS: `python3 -m venv env`
3. Activate the virtual environment. For Windows: `.\env\Scripts\activate`. For Unix/macOS: `source env/bin/activate`
4. pip install the require package by running this command in your terminal. Any OS is the same so just use this command line `pip install -r requirements.txt`
6. Create a folder with name `instance`. (Note: this is important)
7. Put the files from `samples` folder into the `instance` folder. 
8. In `prod_setting.cfg` in the `instance` folder, key in secret key of your choice. For simplicity sake, you can just put secret key as `abc123` for now but remember to change it to something more complex before deployment.
9. For `MONGODB_URI`, you need to get the connection string from your MongoDB Atlas account.
10. THE `samples` FOLDER SHOULD NEVER HAVE ANY CREDENTIALS. ALL CREDENTIALS MUST BE PUT INSIDE THE `instance` FOLDER.
11. After all of this is done, go to the terimninal and key in these commands. For CMD: `set FLASK_APP=ragstoriches`. For Bash: `export FLASK_APP=ragstoriches`.
12. Then, key in these command to launch development mode. For CMD: `set FLASK_ENV=development`. For Bash: `export FLASK_ENV=development` 
13. Finally, type `flask run` and if everything is set, you would be able to view the website in your local computer.

## Testing

Testing will use the `pytest` library which would have been installed for you if you follow the above steps in `requirements.txt`. If not, make sure you install `pytest` by running `pip install pytest`

1. Before you test, make sure you key in this command `pip install -e .`
2. After the installation, you can just key in `pytest` in your terminal and test will run.

# Documentation
Python 3.8.10

Flask version 2.0.2

Bootstrap 5.1.3

## Database

MongoDB Atlas Free tier

## Helpful links
1. [How to create and activate Python virtual enviroment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
2. [Flask 2.0.2](https://flask.palletsprojects.com/en/2.0.x/)
3. [MongoDB Atlas](https://www.mongodb.com/)
