from flask import Flask, render_template, request, redirect, url_for, session
import db_config 
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Hardcoded credentials for admin and user
CREDENTIALS = {
    'admin': 'adminpass',
    'user': 'userpass'
}

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
    except Exception as e:
        print(f"Error adding book: {e}")

    return redirect(url_for('index2'))




@app.route('/update_book/<string:item_id>', methods=['POST'])  # Change book_id to item_id
def update_book(item_id):
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
    
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute(
                "UPDATE Books SET ISBN=%s, Title=%s, Authors=%s, Publisher=%s, Category=%s, Status=%s, TotalCopies=%s, Available_count=%s, Borrowed_count=%s, Edition=%s WHERE ItemID=%s", 
                (ISBN, title, author, publisher, genre, status, total_copies, available_count, borrowed_count, edition, item_id)
            )
                db.commit()
    except Exception as e:
        print(f"Error updating book: {e}")

    return redirect(url_for('index2'))


@app.route('/delete_book/<string:item_id>', methods=['POST'])  # Change book_id to item_id
def delete_book(item_id):
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Books WHERE ItemID=%s", (item_id,))
                db.commit()
    except Exception as e:
        print(f"Error deleting book: {e}")

    return redirect(url_for('index2'))

@app.route('/update_book_by_id', methods=['POST'])
def update_book_by_id():
    item_id = request.form['item_id']
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
    
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute(
                    "UPDATE Books SET ISBN=%s, Title=%s, Authors=%s, Publisher=%s, Category=%s, Status=%s, TotalCopies=%s, Available_count=%s, Borrowed_count=%s, Edition=%s WHERE ItemID=%s", 
                    (ISBN, title, author, publisher, genre, status, total_copies, available_count, borrowed_count, edition, item_id)
                )
                db.commit()
    except Exception as e:
        print(f"Error updating book by ID: {e}")

    return redirect(url_for('index2'))


@app.route('/delete_book_by_id', methods=['POST'])
def delete_book_by_id():
    item_id = request.form['item_id']
    
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Books WHERE ItemID=%s", (item_id,))
                db.commit()
    except Exception as e:
        print(f"Error deleting book by ID: {e}")

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
    location = request.form['location']
    audience = request.form['audience']
    type = request.form['type']
    language = request.form['language']
    
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                query = """
                    INSERT INTO Events (EventID, Location, Audience, Type, Language)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (EID, location, audience, type, language))
                db.commit()
                print("Event added successfully")
    except Exception as e:
        print(f"Error adding event: {e}")

    return redirect(url_for('aevents'))

@app.route('/update_event/<string:eventID>', methods=['POST'])  
def update_event(eventID):
    location = request.form['location']
    audience = request.form['audience']
    type = request.form['type']
    language = request.form['language']
    
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute(
                "UPDATE Events SET Location=%s, Audience=%s, Type=%s, Language=%s WHERE EventID=%s", 
                (location, audience, type, language, eventID,)
            )
                db.commit()
    except Exception as e:
        print(f"Error updating Event: {e}")

    return redirect(url_for('aevents'))


@app.route('/delete_event/<string:eventID>', methods=['POST'])  # Change book_id to item_id
def delete_event(eventID):
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Events WHERE EventID=%s", (eventID,))
                db.commit()
    except Exception as e:
        print(f"Error deleting Event: {e}")

    return redirect(url_for('aevents'))


# Update Magazine by id
@app.route('/update_event_by_id', methods=['POST'])
def update_event_by_id():
    EID = request.form['eventID']
    location = request.form['location']
    audience = request.form['audience']
    type = request.form['type']
    language = request.form['language']

    try:
        with db_config.connect_db() as db:
           with db.cursor() as cursor:
                cursor.execute(
                "UPDATE Events SET Location=%s, Audience=%s, Type=%s, Language=%s WHERE EventID=%s", 
                (location, audience, type, language, EID)
            )
                db.commit()
                print(f"Event {EID} updated successfully")
    except Exception as e:
        print(f"Error updating event: {e}") 

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
    except Exception as e:
        print(f"Error deleting Event: {e}")

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
    except Exception as e:
        print(f"Error adding magazine: {e}")

    return redirect(url_for('amagazines'))

@app.route('/update_magazine/<string:item_id>', methods=['POST'])  
def update_magazine(item_id):
    MID = request.form['magazineID']
    title = request.form['title']
    authors = request.form['authors']
    publisher = request.form['publisher']
    category = request.form['category']
    status = request.form['status']
    
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute(
                "UPDATE Magazines SET MagazineID=%s, Title=%s, Authors=%s, Publisher=%s, Category=%s, Status=%s WHERE ItemID=%s", 
                (MID, title, authors, publisher, category, status, item_id)
            )
                db.commit()
    except Exception as e:
        print(f"Error updating book: {e}")

    return redirect(url_for('amagazines'))


@app.route('/delete_magazine/<string:item_id>', methods=['POST'])  # Change book_id to item_id
def delete_magazine(item_id):
    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                cursor.execute("DELETE FROM Magazines WHERE ItemID=%s", (item_id,))
                db.commit()
    except Exception as e:
        print(f"Error deleting book: {e}")

    return redirect(url_for('amagazines'))


# Update Magazine by id
@app.route('/update_magazine_by_id', methods=['POST'])
def update_magazine_by_id():
    itemID= request.form['itemID']
    MID = request.form['magazineID']
    title = request.form['title']
    authors = request.form['authors']
    publisher = request.form['publisher']
    category = request.form['category']
    status = request.form['status']

    try:
        with db_config.connect_db() as db:
           with db.cursor() as cursor:
                cursor.execute(
                "UPDATE Magazines SET MagazineID=%s, Title=%s, Authors=%s, Publisher=%s, Category=%s, Status=%s WHERE ItemID=%s", 
                (MID, title, authors, publisher, category, status, itemID,)
            )
                db.commit()
                print(f"Magazine {itemID} updated successfully")
    except Exception as e:
        print(f"Error updating magazine: {e}")

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
                print(f"Magazine {itemID} deleted successfully")
    except Exception as e:
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


@app.route('/add_user', methods=['POST'])
def add_user():
    UID = request.form['userID']
    AID = request.form['accountID']
    fname = request.form['fname']
    lname = request.form['lname']
    mtype = request.form['membershipType']
    items = request.form['itemsBorrowed']
    penalty = request.form['penalty']
    phone = request.form['phone']
    email = request.form['email']

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Insert into Users table
                query = """
                    INSERT INTO Users (UserID, AccountID, FirstName, LastName, EmailID, Phone) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (UID, AID, fname, lname, email, phone))
                user_id = cursor.lastrowid  # Get the inserted user ID
                
                # Insert into Account table with CURDATE() for JoiningDate
                query = """
                    INSERT INTO Account (UserID, AccountID, MembershipType, JoiningDate, Penalty, ItemsBorrowed) 
                    VALUES (%s, %s, %s, CURDATE(), %s, %s)
                """
                cursor.execute(query, (UID, AID, mtype, penalty, items))
                db.commit()
                print("User added successfully")
    except Exception as e:
        print(f"Error adding user: {e}")

    return redirect(url_for('ausers'))

# Update User
@app.route('/update_user/<int:user_id>', methods=['POST'])
def update_user(user_id):
    fname = request.form['fname']
    lname = request.form['lname']
    mtype = request.form['membershipType']
    items = request.form['itemsBorrowed']
    penalty = request.form['penalty']
    phone = request.form['phone']
    email = request.form['email']

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Update Users table
                cursor.execute(
                    "UPDATE Users SET FirstName=%s, LastName=%s, EmailID=%s, Phone=%s WHERE UserID=%s",
                    (fname, lname, email, phone, user_id)
                )
                # Update Account table
                cursor.execute(
                    "UPDATE Account SET MembershipType=%s, Penalty=%s, ItemsBorrowed=%s WHERE UserID=%s",
                    (mtype, penalty, items, user_id)
                )
                db.commit()
                print("User updated successfully")
    except Exception as e:
        print(f"Error updating user: {e}")

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
    except Exception as e:
        print(f"Error deleting user: {e}")

    return redirect(url_for('ausers'))

@app.route('/update_user_by_id', methods=['POST'])
def update_user_by_id():
    UID= request.form['userID']
    fname = request.form['fname']
    lname = request.form['lname']
    mtype = request.form['membershipType']
    items = request.form['itemsBorrowed']
    penalty = request.form['penalty']
    phone = request.form['phone']
    email = request.form['email']

    try:
        with db_config.connect_db() as db:
            with db.cursor() as cursor:
                # Update Users table
                cursor.execute(
                    "UPDATE Users SET FirstName=%s, LastName=%s, EmailID=%s, Phone=%s WHERE UserID=%s",
                    (fname, lname, email, phone, UID)
                )
                # Update Account table
                cursor.execute(
                    "UPDATE Account SET MembershipType=%s, Penalty=%s, ItemsBorrowed=%s WHERE UserID=%s",
                    (mtype, penalty, items, UID)
                )
                db.commit()
                print("User updated successfully")
    except Exception as e:
        print(f"Error updating user: {e}")

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
    except Exception as e:
        print(f"Error deleting user: {e}")

    return redirect(url_for('ausers'))  


if __name__ == '__main__':
    app.run(debug=True)
