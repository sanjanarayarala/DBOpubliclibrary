# Chicago Public Library - A class project in CS-425

## Project Description
This project is a web-based application to interact with chicago public library database through UI. This application has 
features as below, 
View and Manage Books: View books, Add books, edit books, delete books
View and Manage Magazines: View magazine, Add magazine, edit magazine, delete magazine
View and Manage Events: View events, Add events, edit events, delete events
View and Manage Users: View users, Add users, edit users, delete users, view users who borrowed books, view users with penalties.

## Installation instructions
Ensure Python3 is installed in your local
1. Clone the repository
2. Set up virtual environment
3. Install the dependencies: `pip install -r requirements.txt`
4. Set up database configuration in `db_config.py`: Update host, user, password, database and port to point to your database. 
5. Start the flask server. (Run `app.py` to launch manually)

Launch the application: http://127.0.0.1:5000/ 

Note that login page is on the first screen. 
Default login credentials are: 
    - username: admin
    - password: adminpass
