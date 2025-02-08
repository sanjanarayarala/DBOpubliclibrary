from dataclasses import dataclass

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import db_config 
from flask import flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Hardcoded credentials for admin and user
CREDENTIALS = {
    'admin': 'adminpass',
    'user': 'userpass'
}

@dataclass
class UserFilter:
    has_membership: bool = False
    has_borrowed: bool = False
    has_overdue: bool = False

@app.route('/')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    username = request.form['username']
    password = request.form['password']

    # Check if the provided credentials are valid
    if username in CREDENTIALS and CREDENTIALS[username] == password:
        if username == 'admin':
            session['role'] = 'admin'
            return redirect(url_for('index2'))
        else:
            session['role'] = 'user'
            return redirect(url_for('index'))
    else:
        return render_template('login.html', error="Invalid credentials")


@app.route('/index')
def index():
    if 'role' in session and session['role'] == 'user':
        return render_template('index.html')  # Regular user page
    else:
        return redirect(url_for('login'))  # Redirect to login if not authorized


@app.route('/index2')
def index2():
    if 'role' in session and session['role'] == 'admin':
        b=[]
        try:
            with db_config.connect_db() as db:
                with db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Books")  # Correct table name
                    books = cursor.fetchall()  # Fetch all records
                    b=books
                    #print(f"Fetched books: {books}")  # Debug print to check fetched data
        except Exception as e:
            print(f"Error retrieving books: {e}")
            books = []  # Fallback to empty list if an error occurs
        print(f"Rendering index2.html with books: {b}")
        return render_template('index2.html', books=b)
    else:
        return redirect(url_for('login'))  # Redirect to login if not authorized


@app.route('/logout')
def logout():
    session.pop('role', None)  # Remove role from session on logout
    return redirect(url_for('login'))

@app.route('/Books')
def books():
    return render_template('Books.html')

@app.route('/Magazines')
def magazines():
    return render_template('Magazines.html')

@app.route('/Events')
def events():
    return render_template('Events.html')


@app.route('/add_book', methods=['POST'])
def add_book():
    ISBN = request.form['ISBN']
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    publisher = request.form['publisher']
    status = request.form['status']
    total_copies = request.form['total_copies']
    available_count = request.form['available_count']
    borrowed_count = request.form['borrowed_count']
    edition = request.form['edition']
    
    # Check for required fields
    if not all([ISBN, title, status, total_copies, available_count, borrowed_count]):
        flash('Please fill in all required fields (ISBN, Title, Status, TotalCopies, Available_count, Borrowed_count).', 'error')
        return redirect(url_for('index2'))

    print(f"Received data: ISBN={ISBN}, Title={title}, Author={author}, Genre={genre}, Publisher={publisher}")

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                query = """
                    INSERT INTO Books (ISBN, Title, Authors, Publisher, Category, Status, TotalCopies, Available_count, Borrowed_count, Edition) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (ISBN, title, author, publisher, genre, status, total_copies, available_count, borrowed_count, edition))
                db.commit()
                print("Book added successfully")
                flash("Book added successfully", 'success')

    except Exception as e:
        print(f"Error adding book: {e}")
        flash(f'Error adding book: {str(e)}', 'error')

    return redirect(url_for('index2'))



@app.route('/update_book/<string:item_id>', methods=['POST'])
def update_book(item_id):
    # Get form data
    ISBN = request.form.get('ISBN')
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    publisher = request.form.get('publisher')
    status = request.form.get('status')
    total_copies = request.form.get('total_copies')
    available_count = request.form.get('available_count')
    borrowed_count = request.form.get('borrowed_count')
    edition = request.form.get('edition')

    # Dictionary to hold non-empty fields
    fields_to_update = {}

    # Add non-empty fields to the dictionary
    if ISBN:
        fields_to_update['ISBN'] = ISBN
    if title:
        fields_to_update['Title'] = title
    if author:
        fields_to_update['Authors'] = author
    if publisher:
        fields_to_update['Publisher'] = publisher
    if genre:
        fields_to_update['Category'] = genre
    if status:
        fields_to_update['Status'] = status
    if total_copies:
        fields_to_update['TotalCopies'] = total_copies
    if available_count:
        fields_to_update['Available_count'] = available_count
    if borrowed_count:
        fields_to_update['Borrowed_count'] = borrowed_count
    if edition:
        fields_to_update['Edition'] = edition

    # If no fields to update, return an error or handle accordingly
    if not fields_to_update:
        flash('No valid parameters to update.', 'error')
        return redirect(url_for('index2'))

    # Dynamically build the SQL query
    set_clause = ", ".join([f"{key}=%s" for key in fields_to_update.keys()])
    query = f"UPDATE Books SET {set_clause} WHERE ItemID=%s"

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Execute the query with non-empty fields and item_id
                cursor.execute(query, list(fields_to_update.values()) + [item_id])
                db.commit()
                flash(f"Updated book ({item_id}) successfully", 'success')

    except Exception as e:
        print(f"Error updating book: {e}")
        flash(f'Error updating book: {str(e)}', 'error')

    return redirect(url_for('index2'))


@app.route('/delete_book/<string:item_id>', methods=['POST'])  # Change book_id to item_id
def delete_book(item_id):
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Books WHERE ItemID=%s", (item_id,))
                db.commit()
                flash(f"Deleted book({item_id}) successfully", 'success')

    except Exception as e:
        print(f"Error deleting book: {e}")
        flash(f'Error deleting book: {str(e)}', 'error')

    return redirect(url_for('index2'))

@app.route('/update_book_by_id', methods=['POST'])
def update_book_by_id():
    item_id = request.form.get('item_id')
    ISBN = request.form.get('ISBN')
    title = request.form.get('title')
    author = request.form.get('author')
    genre = request.form.get('genre')
    publisher = request.form.get('publisher')
    status = request.form.get('status')
    total_copies = request.form.get('total_copies')
    available_count = request.form.get('available_count')
    borrowed_count = request.form.get('borrowed_count')
    edition = request.form.get('edition')

    # Dictionary to hold non-empty fields
    fields_to_update = {}

    # Add non-empty fields to the dictionary
    if ISBN:
        fields_to_update['ISBN'] = ISBN
    if title:
        fields_to_update['Title'] = title
    if author:
        fields_to_update['Authors'] = author
    if publisher:
        fields_to_update['Publisher'] = publisher
    if genre:
        fields_to_update['Category'] = genre
    if status:
        fields_to_update['Status'] = status
    if total_copies:
        fields_to_update['TotalCopies'] = total_copies
    if available_count:
        fields_to_update['Available_count'] = available_count
    if borrowed_count:
        fields_to_update['Borrowed_count'] = borrowed_count
    if edition:
        fields_to_update['Edition'] = edition

    # If no fields to update, return an error or handle accordingly
    if not fields_to_update:
        flash('No valid parameters to update.', 'error')
        return redirect(url_for('index2'))

    # Dynamically build the SQL query
    set_clause = ", ".join([f"{key}=%s" for key in fields_to_update.keys()])
    query = f"UPDATE Books SET {set_clause} WHERE ItemID=%s"

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Execute the query with non-empty fields and item_id
                cursor.execute(query, list(fields_to_update.values()) + [item_id])
                db.commit()
                flash(f"Updated book ({item_id}) successfully", 'success')

    except Exception as e:
        print(f"Error updating book: {e}")
        flash(f'Error updating book: {str(e)}', 'error')

    return redirect(url_for('index2'))


@app.route('/delete_book_by_id', methods=['POST'])  
def delete_book_by_id():
    item_id = request.form.get('item_id')
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Books WHERE ItemID=%s", (item_id,))
                db.commit()
                flash(f"Deleted book({item_id}) successfully", 'success')

    except Exception as e:
        print(f"Error deleting book: {e}")
        flash(f'Error deleting book: {str(e)}', 'error')

    return redirect(url_for('index2'))

#--------------------------------------------------------

@app.route('/Aevents')
def aevents():
    if 'role' in session and session['role'] == 'admin':
        # Fetch events from the database and pass them to the template
        events = []
        try:
            with db_config.connect_db() as db:
                with db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Events")  # Adjust the query as per your Events table structure
                    events = cursor.fetchall()
        except Exception as e:
            print(f"Error retrieving events: {e}")
        return render_template('aevents.html', events=events)
    else:
        return redirect(url_for('login'))  # Redirect to login if not authorized

# Add Event

@app.route('/add_event', methods=['POST'])
def add_event():
    EID = request.form['eventID']
    date_str = request.form.get('date')  # This should now be YYYY-MM-DD
    location = request.form['location']
    audience = request.form['audience']
    event_type = request.form['type']
    language = request.form['language']

    # Check for required fields
    if not all([EID, date_str, location, audience, event_type]):
        flash('Please fill in all required fields (EventID, Date, Location, Audience, Type).', 'error')
        return redirect(url_for('aevents'))

    # Print the received date string for debugging
    print(f"Received date string: '{date_str}'")

    # No need to convert date_str since it's already in YYYY-MM-DD format
    try:
        # Convert the date string to a date object if needed, but can directly use it as a string
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError as ve:
        print(f"Date parsing error: {ve}")
        flash(f'Please provide a valid date. Received: {date_str}', 'error')
        return redirect(url_for('aevents'))

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                query = """
                    INSERT INTO Events (EventID, Date, Location, Audience, Type, Language)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (EID, date, location, audience, event_type, language))
                db.commit()
                print("Event added successfully")
                flash("Event added successfully", 'success')

    except Exception as e:
        print(f"Error adding event: {e}")
        flash(f'Error adding event: {str(e)}', 'error')

    return redirect(url_for('aevents'))



@app.route('/update_event/<string:eventID>', methods=['POST'])
def update_event(eventID):
    # Get form data
    date_str = request.form.get('date')  # Retrieve date input
    location = request.form.get('location')
    audience = request.form.get('audience')
    event_type = request.form.get('type')
    language = request.form.get('language')

    # Dictionary to hold non-empty fields
    fields_to_update = {}

    # Add non-empty fields to the dictionary
    if date_str:  # Check if date is provided
        try:
            # Assuming the date is in YYYY-MM-DD format from a type="date" input
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            fields_to_update['Date'] = date
        except ValueError:
            flash('Please provide a valid date in YYYY-MM-DD format.', 'error')
            return redirect(url_for('aevents'))
    
    if location:
        fields_to_update['Location'] = location
    if audience:
        fields_to_update['Audience'] = audience
    if event_type:
        fields_to_update['Type'] = event_type
    if language:
        fields_to_update['Language'] = language

    # If no fields to update, return an error or handle accordingly
    if not fields_to_update:
        flash('No valid parameters to update.', 'error')
        return redirect(url_for('aevents'))

    # Dynamically build the SQL query
    set_clause = ", ".join([f"{key}=%s" for key in fields_to_update.keys()])
    query = f"UPDATE Events SET {set_clause} WHERE EventID=%s"

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Execute the query with non-empty fields and eventID
                cursor.execute(query, list(fields_to_update.values()) + [eventID])
                db.commit()
                flash(f"Updated event {eventID} successfully", 'success')

    except Exception as e:
        print(f"Error updating Event: {e}")
        flash(f'Error updating event: {str(e)}', 'error')

    return redirect(url_for('aevents'))



@app.route('/delete_event/<string:eventID>', methods=['POST'])  # Change book_id to item_id
def delete_event(eventID):
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Events WHERE EventID=%s", (eventID,))
                flash(f"Deleted event successfully", 'success')
                db.commit()
                flash(f"Deleted event {eventID} successfully", 'success')

    except Exception as e:
        print(f"Error deleting Event: {e}")
        flash(f'Error deleting event: {str(e)}', 'error')

    return redirect(url_for('aevents'))


# Update Magazine by id
@app.route('/update_event_by_id', methods=['POST'])
def update_event_by_id():
    EID = request.form.get('eventID')
    # Get form data
    date_str = request.form.get('date')  # Retrieve date input
    location = request.form.get('location')
    audience = request.form.get('audience')
    event_type = request.form.get('type')
    language = request.form.get('language')

    # Dictionary to hold non-empty fields
    fields_to_update = {}

    # Add non-empty fields to the dictionary
    if date_str:  # Check if date is provided
        try:
            # Assuming the date is in YYYY-MM-DD format from a type="date" input
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            fields_to_update['Date'] = date
        except ValueError:
            flash('Please provide a valid date in YYYY-MM-DD format.', 'error')
            return redirect(url_for('aevents'))
    
    if location:
        fields_to_update['Location'] = location
    if audience:
        fields_to_update['Audience'] = audience
    if event_type:
        fields_to_update['Type'] = event_type
    if language:
        fields_to_update['Language'] = language

    # If no fields to update, return an error or handle accordingly
    if not fields_to_update:
        flash('No valid parameters to update.', 'error')
        return redirect(url_for('aevents'))

    # Dynamically build the SQL query
    set_clause = ", ".join([f"{key}=%s" for key in fields_to_update.keys()])
    query = f"UPDATE Events SET {set_clause} WHERE EventID=%s"

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Execute the query with non-empty fields and eventID
                cursor.execute(query, list(fields_to_update.values()) + [EID])
                db.commit()
                flash(f"Updated event {EID} successfully", 'success')

    except Exception as e:
        print(f"Error updating Event: {e}")
        flash(f'Error updating event: {str(e)}', 'error')

    return redirect(url_for('aevents'))


# Delete Magazine by id
@app.route('/delete_event_by_id', methods=['POST'])
def delete_event_by_id():
    EID= request.form['eventID']
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Events WHERE EventID=%s", (EID,))
                db.commit()
                print(f"Event {EID} deleted successfully")
                flash(f"Event {EID} deleted successfully", 'success')

    except Exception as e:
        print(f"Error deleting Event: {e}")
        flash(f'Error deleting event: {str(e)}', 'error')


    return redirect(url_for('aevents'))


#----------------------------------------------------
# View All Magazines
@app.route('/amagazines')
def amagazines():
    if 'role' in session and session['role'] == 'admin':
        magazines = []
        try:
            with db_config.connect_db() as db:
                with db.cursor() as cursor:
                    cursor.execute("SELECT * FROM Magazines")  # Query all magazines
                    magazines = cursor.fetchall()  # Fetch all records
        except Exception as e:
            print(f"Error retrieving magazines: {e}")
            magazines = []
        return render_template('amagazines.html', magazines=magazines)
    else:
        return redirect(url_for('login'))  # Redirect to login if not authorized




# Add Magazine
@app.route('/add_magazine', methods=['POST'])
def add_magazine():
    MID = request.form['magazineID']
    title = request.form['title']
    authors = request.form['authors']
    publisher = request.form['publisher']
    category = request.form['category']
    status = request.form['status']

    # Check for required fields
    if not all([MID, title, status]):
        flash('Please fill in all required fields (MagazineID, Title, Status).', 'error')
        return redirect(url_for('amagazines'))

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                query = """
                    INSERT INTO Magazines (MagazineID, Title, Authors, Publisher, Category, Status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (MID, title, authors, publisher, category, status))
                db.commit()
                print("Magazine added successfully")
                flash("Magazine added successfully", 'success')

    except Exception as e:
        print(f"Error adding magazine: {e}")
        flash(f'Error adding magazine: {str(e)}', 'error')

    return redirect(url_for('amagazines'))



@app.route('/update_magazine/<string:item_id>', methods=['POST'])
def update_magazine(item_id):
    MID = request.form.get('magazineID')
    title = request.form.get('title')
    authors = request.form.get('authors')
    publisher = request.form.get('publisher')
    category = request.form.get('category')
    status = request.form.get('status')

    # Dictionary to hold non-empty parameters
    params_to_update = {}

    if MID:
        params_to_update['MagazineID'] = MID
    if title:
        params_to_update['Title'] = title
    if authors:
        params_to_update['Authors'] = authors
    if publisher:
        params_to_update['Publisher'] = publisher
    if category:
        params_to_update['Category'] = category
    if status:
        params_to_update['Status'] = status

    # If no parameters are provided, return or handle accordingly
    if not params_to_update:
        return redirect(url_for('amagazines'))

    # Dynamically build the update query
    set_clause = ", ".join([f"{key}=%s" for key in params_to_update.keys()])
    query = f"UPDATE Magazines SET {set_clause} WHERE ItemID=%s"

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Execute the query with non-empty values and item_id
                cursor.execute(query, list(params_to_update.values()) + [item_id])
                db.commit()
                flash(f"Magazine {item_id} updated successfully", 'success')

    except Exception as e:
        print(f"Error updating magazine: {e}")
        flash(f'Error updating magazine: {str(e)}', 'error')

        return "An error occurred", 500

    return redirect(url_for('amagazines'))


@app.route('/delete_magazine/<string:item_id>', methods=['POST'])
def delete_magazine(item_id):
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Magazines WHERE ItemID=%s", (item_id,))
                db.commit()
                flash('Magazine deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting magazine: {e}")
        flash(f'Error deleting magazine: {str(e)}', 'error')

    return redirect(url_for('amagazines'))
# Update Magazine by id
@app.route('/update_magazine_by_id', methods=['POST'])
def update_magazine_by_id():
    itemID= request.form['itemID']
    MID = request.form.get('magazineID')
    title = request.form.get('title')
    authors = request.form.get('authors')
    publisher = request.form.get('publisher')
    category = request.form.get('category')
    status = request.form.get('status')

    # Dictionary to hold non-empty parameters
    params_to_update = {}

    if MID:
        params_to_update['MagazineID'] = MID
    if title:
        params_to_update['Title'] = title
    if authors:
        params_to_update['Authors'] = authors
    if publisher:
        params_to_update['Publisher'] = publisher
    if category:
        params_to_update['Category'] = category
    if status:
        params_to_update['Status'] = status

    # If no parameters are provided, return or handle accordingly
    if not params_to_update:
        return redirect(url_for('amagazines'))

    # Dynamically build the update query
    set_clause = ", ".join([f"{key}=%s" for key in params_to_update.keys()])
    query = f"UPDATE Magazines SET {set_clause} WHERE ItemID=%s"

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Execute the query with non-empty values and item_id
                cursor.execute(query, list(params_to_update.values()) + [itemID])
                db.commit()
                flash(f"Magazine {itemID} updated successfully", 'success')

    except Exception as e:
        print(f"Error updating magazine: {e}")
        flash(f'Error updating magazine: {str(e)}', 'error')

        return "An error occurred", 500

    return redirect(url_for('amagazines'))


# Delete Magazine by id
@app.route('/delete_magazine_by_id', methods=['POST'])
def delete_magazine_by_id():
    itemID= request.form['itemID']
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Magazines WHERE ItemID=%s", (itemID,))
                db.commit()
                flash('Magazine deleted successfully!', 'success')
                print(f"Magazine {itemID} deleted successfully")
    except Exception as e:
        flash(f'Error deleting magazine: {str(e)}', 'error')
        print(f"Error deleting magazine: {e}")

    return redirect(url_for('amagazines'))



#------------------------------------------------

@app.route('/Ausers')
def ausers():
    if 'role' in session and session['role'] == 'admin':
        users = []
        borrows=[]
        try:
            with db_config.connect_db() as db:
                with db.cursor() as cursor:
                    query = """
                        SELECT 
                                Users.UserID, 
                                Users.EmailID, 
                                Users.FirstName, 
                                Users.MiddleName, 
                                Users.LastName, 
                                Users.DateOfBirth, 
                                Users.Address, 
                                Users.Phone, 
                                Users.AccountID, 
                                Account.MembershipType, 
                                Account.JoiningDate, 
                                Account.Penalty, 
                                Account.ItemsBorrowed,
                                GROUP_CONCAT(DISTINCT Books.Title ORDER BY Books.Title SEPARATOR ', ') AS BorrowedBooks, 
                                GROUP_CONCAT(DISTINCT Books.ISBN ORDER BY Books.ISBN SEPARATOR ', ') AS BookISBNs, 
                                GROUP_CONCAT(DISTINCT Borrows.BorrowedDate ORDER BY Borrows.BorrowedDate SEPARATOR ', ') AS BorrowedDates
                        FROM Users
                        LEFT JOIN Account ON Users.UserID = Account.UserID
                        LEFT JOIN Borrows ON Users.UserID = Borrows.UserID
                        LEFT JOIN Books ON Borrows.ItemID = Books.ItemID
                            GROUP BY 
                                Users.UserID, 
                                Users.EmailID, 
                                Users.FirstName, 
                                Users.MiddleName, 
                                Users.LastName, 
                                Users.DateOfBirth, 
                                Users.Address, 
                                Users.Phone, 
                                Users.AccountID, 
                                Account.MembershipType, 
                                Account.JoiningDate, 
                                Account.Penalty, 
                                Account.ItemsBorrowed;

                    """
                    cursor.execute(query)

                    users = cursor.fetchall()

                    query2= """SELECT Users.UserID, 
                            Users.AccountID, 
                            Users.FirstName, 
                            Users.LastName, 
                            Account.MembershipType, 
                            Books.ItemID, 
                            Books.ISBN, 
                            Books.Title, 
                            Borrows.BorrowedDate, 
                            Users.Phone
                        FROM Users
                        INNER JOIN Account ON Users.UserID = Account.UserID
                        INNER JOIN Borrows ON Users.UserID = Borrows.UserID
                        INNER JOIN Books ON Borrows.ItemID = Books.ItemID
                        ORDER BY Users.UserID, Borrows.BorrowedDate;"""
                    
                    cursor.execute(query2)

                    borrows = cursor.fetchall()

        except Exception as e:
            print(f"Error retrieving users: {e}")
        return render_template('ausers.html', users=users, borrows= borrows)
    else:
        return redirect(url_for('login'))


# Add user
@app.route('/add_user', methods=['POST'])
def add_user():
    UID = request.form['userID']
    AID = request.form.get('accountID')  # Use get to allow None if not provided
    fname = request.form['fname']
    lname = request.form['lname']
    mtype = request.form.get('membershipType')  # Get membership type, can be None
    items = request.form.get('itemsBorrowed')  # Get items borrowed, can be None
    penalty = request.form.get('penalty')  # Get penalty, can be None
    phone = request.form['phone']
    email = request.form['email']

    # Check for required fields
    if not all([UID, fname, lname, phone, email]):
        flash('Please fill in all required fields (UserID, FirstName, LastName, Phone, Email).', 'error')
        return redirect(url_for('ausers'))

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Insert into Users table
                user_query = """
                    INSERT INTO Users (UserID, FirstName, LastName, EmailID, Phone) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(user_query, (UID, fname, lname, email, phone))

                # Check if AccountID is provided before inserting into Account table
                if AID:
                    # Insert into Account table with CURDATE() for JoiningDate
                    account_query = """
                        INSERT INTO Account (UserID, AccountID, MembershipType, JoiningDate, Penalty, ItemsBorrowed) 
                        VALUES (%s, %s, %s, CURDATE(), %s, %s)
                    """
                    cursor.execute(account_query, (UID, AID, mtype, penalty, items))

                db.commit()
                print("User added successfully")
                flash(f"User added successfully", 'success')

    except Exception as e:
        print(f"Error adding user: {e}")
        flash(f'Error adding user: {str(e)}', 'error')

    return redirect(url_for('ausers'))



@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    # Get form data
    AID = request.form.get('accountID')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    mtype = request.form.get('membershipType')
    items = request.form.get('itemsBorrowed')
    penalty = request.form.get('penalty')
    phone = request.form.get('phone')
    email = request.form.get('email')

    # Dictionaries to hold non-empty fields for each table
    user_fields_to_update = {}
    account_fields_to_update = {}

    # Add non-empty fields to respective dictionaries
    if AID:
        user_fields_to_update['AccountID'] = AID
    if fname:
        user_fields_to_update['FirstName'] = fname
    if lname:
        user_fields_to_update['LastName'] = lname
    if email:
        user_fields_to_update['EmailID'] = email
    if phone:
        user_fields_to_update['Phone'] = phone

    if mtype:
        account_fields_to_update['MembershipType'] = mtype
    if penalty:
        account_fields_to_update['Penalty'] = penalty
    if items:
        account_fields_to_update['ItemsBorrowed'] = items

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # If there are fields to update in the Users table
                if user_fields_to_update:
                    user_set_clause = ", ".join([f"{key}=%s" for key in user_fields_to_update.keys()])
                    user_query = f"UPDATE Users SET {user_set_clause} WHERE UserID=%s"
                    cursor.execute(user_query, list(user_fields_to_update.values()) + [user_id])

                # If there are fields to update in the Account table
                if account_fields_to_update:
                    account_set_clause = ", ".join([f"{key}=%s" for key in account_fields_to_update.keys()])
                    account_query = f"UPDATE Account SET {account_set_clause} WHERE UserID=%s"
                    cursor.execute(account_query, list(account_fields_to_update.values()) + [user_id])

                db.commit()
                print("User updated successfully")
                flash(f"User {user_id} updated successfully", 'success')

    except Exception as e:
        print(f"Error updating user: {e}")
        flash(f'Error updating user: {str(e)}', 'error')

    return redirect(url_for('ausers'))


# Delete User
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Users WHERE UserID=%s", (user_id,))
                db.commit()
                print("User deleted successfully")
                flash(f"User {user_id} deleted successfully", 'success')

    except Exception as e:
        print(f"Error deleting user: {e}")
        flash(f'Error deleting user: {str(e)}', 'error')

    return redirect(url_for('ausers'))

@app.route('/update_user_by_id', methods=['POST'])
def update_user_by_id():
    UID = request.form.get('userID')
    AID = request.form.get('accountID')
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    mtype = request.form.get('membershipType')
    items = request.form.get('itemsBorrowed')
    penalty = request.form.get('penalty')
    phone = request.form.get('phone')
    email = request.form.get('email')

    # Dictionaries to hold non-empty fields for each table
    user_fields_to_update = {}
    account_fields_to_update = {}

    # Add non-empty fields to respective dictionaries
    if AID:
        user_fields_to_update['AccountID'] = AID
    if fname:
        user_fields_to_update['FirstName'] = fname
    if lname:
        user_fields_to_update['LastName'] = lname
    if email:
        user_fields_to_update['EmailID'] = email
    if phone:
        user_fields_to_update['Phone'] = phone

    if mtype:
        account_fields_to_update['MembershipType'] = mtype
    if penalty:
        account_fields_to_update['Penalty'] = penalty
    if items:
        account_fields_to_update['ItemsBorrowed'] = items

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # If there are fields to update in the Users table
                if user_fields_to_update:
                    user_set_clause = ", ".join([f"{key}=%s" for key in user_fields_to_update.keys()])
                    user_query = f"UPDATE Users SET {user_set_clause} WHERE UserID=%s"
                    cursor.execute(user_query, list(user_fields_to_update.values()) + [UID])

                # If there are fields to update in the Account table
                if account_fields_to_update:
                    account_set_clause = ", ".join([f"{key}=%s" for key in account_fields_to_update.keys()])
                    account_query = f"UPDATE Account SET {account_set_clause} WHERE UserID=%s"
                    cursor.execute(account_query, list(account_fields_to_update.values()) + [UID])

                db.commit()
                print("User updated successfully")
                flash(f"User {UID} updated successfully", 'success')

    except Exception as e:
        print(f"Error updating user: {e}")
        flash(f'Error updating user: {str(e)}', 'error')

    return redirect(url_for('ausers'))




# Route to delete user by UserID
@app.route('/delete_user_by_id', methods=['POST'])
def delete_user_by_id():
    UID = request.form['userID']

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Users WHERE UserID=%s", (UID,))
                db.commit()
                print("User deleted successfully")
                flash(f"User {UID} deleted successfully", 'success')

    except Exception as e:
        print(f"Error deleting user: {e}")
        flash(f'Error deleting user: {str(e)}', 'error')

    return redirect(url_for('ausers'))  


@app.route('/Astats', methods=['GET', 'POST'])
def astats():
    if 'role' in session and session['role'] == 'admin':
        # Initialize variables for each query result
        branch_books = []
        category_rankings = []
        top_books = []
        most_popular_books = []
        borrowed_range_books = []
        
        
        try:
            with db_config.connect_db() as db:
                with db.cursor() as cursor:
                    

                    # Query 2
                    cursor.execute("""
                        SELECT Title, Category, TotalCopies,
                        RANK() OVER (PARTITION BY Category ORDER BY TotalCopies DESC) AS RankInCategory
                        FROM Books
                    """)
                    category_rankings = cursor.fetchall()
                    
                    # Query 3
                    cursor.execute("""
                        SELECT Title, TotalCopies,
                        DENSE_RANK() OVER (ORDER BY TotalCopies DESC) AS RankByCopies
                        FROM Books
                        WHERE TotalCopies > 0
                        ORDER BY RankByCopies
                        LIMIT 3
                    """)
                    top_books = cursor.fetchall()
                    
                    # Query 4
                    cursor.execute("""
                        SELECT ItemID, ISBN, MostPopular, Category
                        FROM (
                            SELECT * ,
                            FIRST_VALUE(Title) OVER w AS MostPopular,
                            row_number() OVER w AS rn
                            FROM Books
                            WINDOW w AS (PARTITION BY Category ORDER BY borrowed_count DESC)
                        ) b
                        WHERE b.rn = 1
                    """)
                    most_popular_books = cursor.fetchall()
                    
                    # Query 5
                    cursor.execute("""
                        SELECT Category, Title,
                        CASE
                            WHEN x.buckets = 1 THEN 'Most borrowed'
                            WHEN x.buckets = 2 THEN 'Mid-range borrowed'
                            WHEN x.buckets = 3 THEN 'Least borrowed'
                        END AS BorrowRange
                        FROM (
                            SELECT * ,
                            NTILE(3) OVER (PARTITION BY category ORDER BY Borrowed_count DESC) AS buckets
                            FROM Books
                        ) x
                    """)
                    borrowed_range_books = cursor.fetchall()
                    
        except Exception as e:
            print(f"Error retrieving data: {e}")

        # Pass the results to the template
        return render_template(
            'astats.html',
            category_rankings=category_rankings,
            top_books=top_books,
            most_popular_books=most_popular_books,
            borrowed_range_books=borrowed_range_books
        )
    else:
        return redirect(url_for('login'))


@app.route('/Astats2', methods=['GET', 'POST'])
def astats2():
    if 'role' in session and session['role'] == 'admin':
        # Pass the results to the template
        return render_template(
            'astats2.html'
        )
    else:
        return redirect(url_for('login'))

@app.route('/fetch_top_n_books', methods=['GET'])
def fetch_top_n_books():
    limit = int(request.args.get('limit', 3))
    query = f"""
                        SELECT Title, TotalCopies,
                        DENSE_RANK() OVER (ORDER BY TotalCopies DESC) AS RankByCopies
                        FROM Books
                        WHERE TotalCopies > 0
                        ORDER BY RankByCopies
                        LIMIT {limit}
                    """
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                print(f"/fetch_top_n_books: SQL Query :{query}")
                cursor.execute(query)
                results = cursor.fetchall()

        # Convert to JSON response
        top_books = [
            {
                "title": row[0],
                "total_copies": row[1],
                "rank_by_copies": row[2]
            }
            for row in results
        ]
        return jsonify(top_books)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(None)



@app.route('/most_borrowed_books', methods=['GET'])
def most_borrowed_books():
    limit = int(request.args.get('limit', 20))
    branch_id = request.args.get('branch_id', None)  # Pass NULL for all branches
    category = request.args.get('category', None)  # Pass NULL for all categories
    view = request.args.get('view', 'books')  # Default to books view

    if branch_id != 'null':
        branch_id = f"\'{branch_id}\'"
    else:
        branch_id = "Null"

    if category != 'null':
        category = f"\'{category}\'"
    else:
        category = "Null"

    if view == 'books':
        query = f"""
            WITH BookStats AS (
                SELECT 
                    b.ItemID,
                    b.Title,
                    b.Category,
                    b.TotalCopies,
                    b.Borrowed_count as currently_borrowed,
                    b.Available_count as currently_available,
                    COUNT(bw.ItemID) as total_times_borrowed
                FROM Books b
                LEFT JOIN Borrows bw ON b.ItemID = bw.ItemID
                JOIN StoresBooks sb ON b.ItemID = sb.ItemID
                WHERE 
                    (sb.BranchID = {branch_id} OR {branch_id} IS NULL)
                    AND (b.Category = {category} OR {category} IS NULL)
                GROUP BY 
                    b.ItemID, 
                    b.Title, 
                    b.Category,
                    b.TotalCopies,
                    b.Borrowed_count,
                    b.Available_count
            ),
            BookRanking AS (
                SELECT 
                    *,
                    DENSE_RANK() OVER (ORDER BY total_times_borrowed DESC) as popularity_rank
                FROM BookStats
            )
            SELECT 
                popularity_rank,
                Title,
                Category,
                TotalCopies,
                currently_borrowed,
                currently_available,
                total_times_borrowed
            FROM BookRanking
            ORDER BY 
                popularity_rank
            LIMIT {limit}
        """
    else:
        # Group by category
        query = f"""
                    WITH CategoryStats AS (
                        SELECT 
                            b.Category,
                            SUM(b.TotalCopies) as total_copies,
                            SUM(b.Borrowed_count) as currently_borrowed,
                            SUM(b.Available_count) as currently_available,
                            COUNT(bw.ItemID) as total_times_borrowed
                        FROM Books b
                        LEFT JOIN Borrows bw ON b.ItemID = bw.ItemID
                        JOIN StoresBooks sb ON b.ItemID = sb.ItemID
                        WHERE 
                            (sb.BranchID = {branch_id} OR {branch_id} IS NULL)
                            AND (b.Category = {category} OR {category} IS NULL)
                        GROUP BY 
                            b.Category
                    ),
                    CategoryRanking AS (
                        SELECT 
                            *,
                            DENSE_RANK() OVER (ORDER BY total_times_borrowed DESC) as popularity_rank
                        FROM CategoryStats
                    )
                    SELECT 
                        popularity_rank,
                        Category,
                        Category,
                        total_copies,
                        currently_borrowed,
                        currently_available,
                        total_times_borrowed
                    FROM CategoryRanking
                    ORDER BY 
                        popularity_rank
                    LIMIT {limit}
                """
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                print(f"/most_borrowed_books: SQL Query :{query}")
                cursor.execute(query)
                results = cursor.fetchall()

        # Convert to JSON response
        books = [
            {
                "rank": row[0],
                "title": row[1],
                "category": row[2],
                "total_copies": row[3],
                "currently_borrowed": row[4],
                "currently_available": row[5],
                "total_times_borrowed": row[6]
            }
            for row in results
        ]
        return jsonify(books)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify(None)

@app.route('/fetch_branches', methods=['GET'])
def fetch_branches():
    query = """
        SELECT DISTINCT
            b.BranchID,
            CONCAT(b.Street, ', ', b.City, ' ', b.ZipCode) AS branch_location
        FROM Branch b
        ORDER BY b.BranchID;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_branches: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    branches = results #[row[0] for row in results]
    return jsonify(branches)


@app.route('/api/books/all', methods=['GET'])
def get_all_books():
    query = """SELECT DISTINCT ItemID, Title, Category
                FROM Books
                ORDER BY Title
                """
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                print(f"/api/books/all: SQL Query :{query}")
                cursor.execute(query)
                results = cursor.fetchall()
                # Convert to JSON response
                books = [
                    {
                        "ItemID": row[0],
                        "Title": row[1],
                        "Category": row[2]
                    }
                    for row in results
                ]
                return jsonify(books)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/fetch_categories', methods=['GET'])
def fetch_categories():
    query = """
        SELECT DISTINCT
            Category
        FROM Books
        WHERE Category IS NOT NULL
        ORDER BY Category;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_categories: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    categories = [row[0] for row in results]
    return jsonify(categories)


@app.route('/fetch_magazine_titles', methods=['GET'])
def fetch_magazine_titles():
    query = """
        SELECT DISTINCT
            Title
        FROM Magazines
        ORDER BY Title;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_magazine_titles: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    titles = [row[0] for row in results]
    return jsonify(titles)


# Main API endpoint to fetch filtered magazines
@app.route('/fetch_magazines', methods=['GET'])
def fetch_magazines():
    category = request.args.get('category')
    title = request.args.get('title')
    availability = request.args.get('availability')
    branch_id = request.args.get('branch_id')

    query = """
        SELECT 
            M.Title AS MagazineTitle,
            M.Category AS Category,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM StoresMags SM
                    WHERE SM.ItemID = M.ItemID
                ) THEN 'In Store'
                ELSE 'Online Only'
            END AS Availability,
            COALESCE(
                (
                    SELECT GROUP_CONCAT(
                        DISTINCT CONCAT(
                            'Branch ID: ', BR.BranchID,
                            ' (', BR.Street, ', ', BR.ZipCode,
                            ', Phone: ', BR.Phone, ')'
                        )
                        ORDER BY BR.BranchID
                        SEPARATOR '\n'
                    )
                    FROM StoresMags SM
                    JOIN Branch BR ON SM.BranchID = BR.BranchID
                    WHERE SM.ItemID = M.ItemID
                ), 'Online Only'
            ) AS BranchDetails
        FROM Magazines M
        WHERE 1=1
    """

    params = []
    if category:
        query += " AND M.Category = %s"
        params.append(category)
    if title:
        query += " AND M.Title LIKE %s"
        params.append(f"%{title}%")
    if availability:
        if availability == 'online':
            query += """ AND NOT EXISTS (
                SELECT 1 FROM StoresMags SM 
                WHERE SM.ItemID = M.ItemID
            )"""
        elif availability == 'instore':
            query += """ AND EXISTS (
                SELECT 1 FROM StoresMags SM 
                WHERE SM.ItemID = M.ItemID
            )"""
    if branch_id:
        query += """ AND EXISTS (
            SELECT 1 FROM StoresMags SM 
            WHERE SM.ItemID = M.ItemID 
            AND SM.BranchID = %s
        )"""
        params.append(branch_id)

    query += " ORDER BY M.Title"

    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_magazines: SQL Query :{query}")
            cursor.execute(query, params)
            results = cursor.fetchall()

    magazines = []
    for row in results:
        locations = row[3].split('\n') if row[3] != 'Online Only' else []
        magazines.append({
            'title': row[0],
            'category': row[1],
            'availability': row[2],
            'locations': locations
        })

    return jsonify(magazines)

@app.route('/least_borrowed_books', methods=['GET'])
def least_borrowed_books():
    # Get limit from request, default to 3
    limit = int(request.args.get('limit', 3))
    branch_id = request.args.get('branch_id', None)  # Pass NULL for all branches
    category = request.args.get('category', None)  # Pass NULL for all categories

    if branch_id != 'null':
        branch_id = f"\'{branch_id}\'"
    else:
        branch_id = "Null"

    if category != 'null':
        category = f"\'{category}\'"
    else:
        category = "Null"

    query = f"""
        WITH BookStats AS (
            SELECT 
                b.ItemID,
                b.Title,
                b.Category,
                b.TotalCopies,
                b.Borrowed_count as currently_borrowed,
                b.Available_count as currently_available,
                COUNT(bw.ItemID) as total_times_borrowed
            FROM Books b
            LEFT JOIN Borrows bw ON b.ItemID = bw.ItemID
            JOIN StoresBooks sb ON b.ItemID = sb.ItemID
            WHERE 
                (sb.BranchID = {branch_id} OR {branch_id} IS NULL)
                AND (b.Category = {category} OR {category} IS NULL)
            GROUP BY 
                b.ItemID, 
                b.Title, 
                b.Category,
                b.TotalCopies,
                b.Borrowed_count,
                b.Available_count
        ),
        BookRanking AS (
            SELECT 
                *,
                DENSE_RANK() OVER (ORDER BY total_times_borrowed ASC) as unpopularity_rank
            FROM BookStats
        )
        SELECT 
            unpopularity_rank,
            Title,
            Category,
            TotalCopies,
            currently_borrowed,
            currently_available,
            total_times_borrowed
        FROM BookRanking
        ORDER BY 
            unpopularity_rank
        LIMIT {limit}
    """

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                print(f"/least_borrowed_books: SQL Query :{query}")
                cursor.execute(query)
                results = cursor.fetchall()

        # Convert to JSON response
        books = [
            {
                "rank": row[0],
                "title": row[1],
                "category": row[2],
                "total_copies": row[3],
                "currently_borrowed": row[4],
                "currently_available": row[5],
                "total_times_borrowed": row[6]
            }
            for row in results
        ]
        return jsonify(books)
    except Exception as e:
        print(f"Error deleting magazine: {e}")
        return jsonify(None)


@app.route('/api/users/filter1', methods=['GET'])
def filter_users1():
    # Get filter parameters from query string
    filters = UserFilter(
        has_membership=request.args.get('membership') == 'true',
        has_borrowed=request.args.get('borrowed') == 'true',
        has_overdue=request.args.get('overdue') == 'true'
    )

    # Build the base query
    query = """
    SELECT DISTINCT 
        u.UserID,
        u.FirstName,
        u.LastName,
        u.EmailID,
        a.MembershipType,
        GROUP_CONCAT(DISTINCT b.ItemID) as BorrowedItems,
        GROUP_CONCAT(DISTINCT 
            CASE 
                WHEN b.DaysLeft < 0 THEN b.ItemID 
                ELSE NULL 
            END
        ) as OverdueItems
    FROM Users u
    LEFT JOIN Account a ON u.AccountID = a.AccountID
    LEFT JOIN Borrows b ON u.UserID = b.UserID
    """

    where_clauses = []
    if filters.has_membership:
        where_clauses.append("a.AccountID IS NOT NULL")
    if filters.has_borrowed:
        where_clauses.append("b.ItemID IS NOT NULL")
    if filters.has_overdue:
        where_clauses.append("b.DaysLeft < 0")

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += " GROUP BY u.UserID, u.FirstName, u.LastName, u.EmailID, a.MembershipType"

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                print(f"/api/users/filter1: SQL Query :{query}")
                cursor.execute(query)
                results = cursor.fetchall()
        query = """
                    SELECT 
                        CASE 
                            WHEN b.ItemID IS NOT NULL THEN 'Book'
                            ELSE 'Magazine'
                        END as ItemType,
                        COALESCE(b.Title, m.Title) as Title,
                        COALESCE(b.ItemID, m.ItemID) as ItemID
                    FROM (
                        SELECT DISTINCT unnest(%s) as item_id
                    ) t
                    LEFT JOIN Books b ON b.ItemID = t.item_id
                    LEFT JOIN Magazines m ON m.ItemID = t.item_id
                """
        # Enhance results with book/magazine details
        for result in results:
            if result['BorrowedItems']:
                borrowed_ids = result['BorrowedItems'].split(',')
                # Get book/magazine details for borrowed items
                print(f"Get book/magazine details for borrowed items: SQL Query :{query}")
                cursor.execute(query, (borrowed_ids,))
                result['BorrowedItemDetails'] = cursor.fetchall()

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/branches', methods=['GET'])
def get_branches():
    query = """
                    SELECT BranchID, Street,ZipCode
                    FROM Branch
                    ORDER BY City, Street
                """
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                print(f"/api/branches: SQL Query :{query}")
                cursor.execute(query)
                branches = cursor.fetchall()
                return jsonify(branches)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/filter', methods=['GET'])
def filter_users():
    # Get filter parameters
    membership_type = request.args.get('membership')
    has_borrowed = request.args.get('has_borrowed')
    has_penalty = request.args.get('has_penalty')
    book_id = request.args.get('book')
    category = request.args.get('category')
    branch_id = request.args.get('branch')

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                query = """
                    SELECT DISTINCT
                        Users.UserID, 
                        Users.EmailID, 
                        Users.FirstName, 
                        Users.MiddleName, 
                        Users.LastName, 
                        Users.DateOfBirth, 
                        Users.Address, 
                        Users.Phone, 
                        Account.MembershipType, 
                        Account.JoiningDate, 
                        Account.Penalty, 
                        Account.ItemsBorrowed
                    FROM Users
                    LEFT JOIN Account ON Users.AccountID = Account.AccountID
                    LEFT JOIN Borrows ON Users.UserID = Borrows.UserID
                    LEFT JOIN Books ON Borrows.ItemID = Books.ItemID
                    LEFT JOIN StoresBooks ON Books.ItemID = StoresBooks.ItemID
                    WHERE 1=1
                """
                params = []

                if membership_type:
                    query += " AND Account.MembershipType = %s"
                    params.append(membership_type)

                if has_borrowed == 'true':
                    query += " AND Account.ItemsBorrowed > 0"
                elif has_borrowed == 'false':
                    query += " AND (Account.ItemsBorrowed = 0 OR Account.ItemsBorrowed IS NULL)"

                if has_penalty == 'true':
                    query += " AND Account.Penalty > 0"

                if book_id:
                    query += " AND Books.ItemID = %s"
                    params.append(book_id)

                if category:
                    query += " AND Books.Category = %s"
                    params.append(category)

                if branch_id:
                    query += " AND StoresBooks.BranchID = %s"
                    params.append(branch_id)

                print(f"/api/users/filter: SQL Query :{query}")
                cursor.execute(query, params)
                results = cursor.fetchall()
                users = [
                    {
                        "UserID": row[0],
                        "EmailID": row[1],
                        "FirstName": row[2],
                        "MiddleName": row[3],
                        "LastName": row[4],
                        "DateOfBirth": row[5],
                        "Address": row[6],
                        "Phone": row[7],
                        "MembershipType": row[8],
                        "JoiningDate": row[9],
                        "Penalty": row[10],
                        "ItemsBorrowed": row[11]
                    }
                    for row in results
                ]
                return jsonify(users)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# API endpoint to fetch book titles
@app.route('/fetch_book_titles', methods=['GET'])
def fetch_book_titles():
    query = """
        SELECT DISTINCT Title 
        FROM Books 
        ORDER BY Title;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_book_titles: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    titles = [row[0] for row in results]
    return jsonify(titles)


# Main API endpoint to fetch filtered books
@app.route('/fetch_books', methods=['GET'])
def fetch_books():
    category = request.args.get('category')
    title = request.args.get('title')
    availability = request.args.get('availability')
    branch_id = request.args.get('branch_id')

    query = """
        SELECT 
            B.Title AS BookTitle,
            B.Category AS Category,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM StoresBooks SB
                    WHERE SB.ItemID = B.ItemID
                ) THEN 'In Store'
                ELSE 'Online Only'
            END AS Availability,
            COALESCE(
                (
                    SELECT GROUP_CONCAT(
                        DISTINCT CONCAT(
                            'Branch ID: ', BR.BranchID,
                            ' (', BR.Street, ', ', BR.ZipCode,
                            ', Phone: ', BR.Phone, ')'
                        )
                        ORDER BY BR.BranchID
                        SEPARATOR '\n'
                    )
                    FROM StoresBooks SB
                    JOIN Branch BR ON SB.BranchID = BR.BranchID
                    WHERE SB.ItemID = B.ItemID
                ), 'Online Only'
            ) AS BranchDetails
        FROM Books B
        WHERE 1=1
    """

    params = []
    if category:
        query += " AND B.Category = %s"
        params.append(category)
    if title:
        query += " AND B.Title LIKE %s"
        params.append(f"%{title}%")
    if availability:
        if availability == 'online':
            query += """ AND NOT EXISTS (
                SELECT 1 FROM StoresBooks SB 
                WHERE SB.ItemID = B.ItemID
            )"""
        elif availability == 'instore':
            query += """ AND EXISTS (
                SELECT 1 FROM StoresBooks SB 
                WHERE SB.ItemID = B.ItemID
            )"""
    if branch_id:
        query += """ AND EXISTS (
            SELECT 1 FROM StoresBooks SB 
            WHERE SB.ItemID = B.ItemID 
            AND SB.BranchID = %s
        )"""
        params.append(branch_id)

    query += " ORDER BY B.Title"

    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_books: SQL Query :{query}")
            cursor.execute(query, params)
            results = cursor.fetchall()

    books = []
    for row in results:
        locations = row[3].split('\n') if row[3] != 'Online Only' else []
        books.append({
            'title': row[0],
            'category': row[1],
            'availability': row[2],
            'locations': locations
        })

    return jsonify(books)


# API endpoint to fetch unique event types
@app.route('/fetch_event_types', methods=['GET'])
def fetch_event_types():
    query = """
        SELECT DISTINCT Type 
        FROM Events 
        ORDER BY Type;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_event_types: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    types = [row[0] for row in results]
    return jsonify(types)


# API endpoint to fetch unique locations
@app.route('/fetch_locations', methods=['GET'])
def fetch_locations():
    query = """
        SELECT DISTINCT Location 
        FROM Events 
        ORDER BY Location;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_locations: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    locations = [row[0] for row in results]
    return jsonify(locations)


# API endpoint to fetch unique audiences
@app.route('/fetch_audiences', methods=['GET'])
def fetch_audiences():
    query = """
        SELECT DISTINCT Audience 
        FROM Events 
        ORDER BY Audience;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_audiences: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    audiences = [row[0] for row in results]
    return jsonify(audiences)


# API endpoint to fetch unique languages
@app.route('/fetch_languages', methods=['GET'])
def fetch_languages():
    query = """
        SELECT DISTINCT Language 
        FROM Events 
        ORDER BY Language;
    """
    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_languages: SQL Query :{query}")
            cursor.execute(query)
            results = cursor.fetchall()

    languages = [row[0] for row in results]
    return jsonify(languages)


# Main API endpoint to fetch filtered events
@app.route('/fetch_events', methods=['GET'])
def fetch_events():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    location = request.args.get('location')
    audience = request.args.get('audience')
    event_type = request.args.get('type')
    language = request.args.get('language')

    query = """
        SELECT 
            EventID,
            Date,
            Location,
            Audience,
            Type,
            Language
        FROM Events
        WHERE 1=1
    """

    params = []

    if start_date:
        query += " AND Date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND Date <= %s"
        params.append(end_date)
    if location:
        query += " AND Location = %s"
        params.append(location)
    if audience:
        query += " AND Audience = %s"
        params.append(audience)
    if event_type:
        query += " AND Type = %s"
        params.append(event_type)
    if language:
        query += " AND Language = %s"
        params.append(language)

    query += " ORDER BY Date"

    with db_config.connect_db() as db:
        with db.cursor() as cursor:
            print(f"/fetch_events: SQL Query :{query}")
            cursor.execute(query, params)
            results = cursor.fetchall()

    events = []
    for row in results:
        events.append({
            'id': row[0],
            'date': row[1].strftime('%Y-%m-%d'),
            'location': row[2],
            'audience': row[3],
            'type': row[4],
            'language': row[5]
        })

    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
