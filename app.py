from flask import Flask, render_template, request
import pymysql
import datetime



connection = pymysql.connect(host='127.0.0.1',
                             user='root',
                             password='1q2w3e4rPoi',
                             db='new_schema')
print("Database connected...")
connection.query('SET GLOBAL connect_timeout=6000')

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/addmember', methods=['POST', 'GET'])
def new_member():
    return render_template('addmember.html')

@app.route('/new_member',methods=['POST', 'GET'])
def add_new_member():
    #lib_ssn = request.form['Lib_SSN']
    userid = request.form['ReaderID']
    name = str(request.form['Name'])
    email = str(request.form['Email'])
    phonenum = request.form['PhoneNum']

    cur = connection.cursor()
    try:
        command = "insert into reader(ReaderID, Name, Email, PhoneNum) values (" + userid + ", " + name + ", '" + email + "','" + phonenum + "');"
        print(command)
        cur.execute(command)
        connection.commit()
        return render_template('index.html')
    except:
        return render_template('addmember.html', result="Podano nieprawidlowe dane")

@app.route('/addbook', methods=['POST', 'GET'])
def new_book():
    return render_template('addbook.html')

@app.route('/add_new_book',methods=['POST', 'GET'])
def add_new_book():
    booksID = request.form['BooksID']
    title = request.form['Title']
    author = request.form['Author']
    edition = request.form['Edition']
    available = request.form['Available']
    genre = request.form['Genre']

    try:
        cur = connection.cursor()
        cmd1 = "insert into books(BooksID, Title, Author, Edition, Available, Genre) values (" + booksID + ",'" + title + "', '" + author + "', '" + edition + "', '" + available + "','" + genre + "');"
        cur.execute(cmd1)
        connection.commit()
       # cur2 = connection.cursor()
        #cmd2 = "insert into available values(" + book_isbn + ", '" + lang + "', '" + bind + "', '" + description + "', 1);"
        #print(cmd2)
        #cur2.execute(cmd2)
        #connection.commit()
        return render_template('index.html')
    except:
        return render_template('addbook.html', result="Podano bledne dane")

@app.route('/BorrowBook', methods=['POST', 'GET'])
def borrow_book():
    books_cursor = connection.cursor()
    books_cmd = "select b.BooksID, b.Title, b.Author, b.Edition, b.Available, b.Genre from books as b where Available > 0;"
    print(books_cmd)
    books_cursor.execute(books_cmd)
    total = books_cursor.fetchall()
    print(total)
    return render_template('borrowBook.html', total=total)

@app.route('/borrow_this_book',methods=['POST', 'GET'])
def get_this_book():
    #lib_ssn = request.form['Lib_SSN']
    booksid = request.form['BooksID']
    readerid = request.form['ReaderID']
    mem_cur = connection.cursor()

    cmd1 = "select * from reader where ReaderID =" + readerid + ";"
    #print(cmd1)
    mem_cur.execute(cmd1)
    is_mem = mem_cur.fetchall()
    #print(is_mem)
    if (len(is_mem) == 0):
        return "Nie jestes uzytkownikiem"
    else:
            try:
                
                days = 21
                grace = 7

                borrow_cur = connection.cursor()
                cmd3 = "INSERT INTO rental_list (RentalID, Date, ReturnDate, BookID, ReaderID) VALUES (" + 0 + ", CURDATE() , CURDATE(), DATE_ADD(CURDATE(), INTERVAL " + str(days) + " DAY), " + str(grace) + ", '" + booksid + "', '" + readerid + "');"
                print(cmd3)
                borrow_cur.execute(cmd3)

                update_cur = connection.cursor()
                cmd4 = "UPDATE books SET Available = 0 where BooksID = " + booksid + " ;"
                update_cur.execute(cmd4)

            except:
                return render_template("borrowBook.html", result="Wrong Details provided")

    connection.commit()

    return render_template('index.html')

@app.route('/ReturnBook', methods=['POST', 'GET'])
def return_book():
    return render_template('ReturnBook.html')

@app.route('/return_this_book',methods=['POST', 'GET'])
def return_this_book():
    booksid = request.form['BooksID']
    readerid = request.form['ReaderID']

    #try:
    check_cur = connection.cursor()
    cmd1 = "SELECT ren.RentalID ,ren.Date, ren.ReturnDate, CURDATE(), b.Title, b.Author FROM rental_list as ren, books as b where ren.BookID= " + booksid + " and b.BooksID = ren.BookID;"
    print(cmd1)
    check_cur.execute(cmd1)
    result = check_cur.fetchall()
    print(result[0][3] - result[0][2])
    if (len(result) == 0):
        return render_template("borrowBook.html", result="Ksiazka nie byla wypozyczona")

    days = str(result[0][3] - result[0][2])
    title = str(result[0][4])
    author = str(result[0][5])
    borroweddate = result[0][1]
    cur_date = result[0][3]
    print(days, title, author)
    available_cur = connection.cursor()
    cmd2 = "update books set Available = 1 where BooksID=" + booksid + ";"
    available_cur.execute(cmd2)

    delete_cur = connection.cursor()
    cmd3 = "delete from rental_list where BookID=" + booksid + ";"
    delete_cur.execute(cmd3)

    connection.commit()


    #except:
    #    return render_template("ReturnBook.html", result="Wrong details provided")

    return render_template("ReturnBook.html", booksid = booksid, title = title, author = author, borroweddate = borroweddate, days=days, result="Receipt", cur_date = cur_date)


if __name__ == '__main__':
    app.run()
