# SQLite Connection & Functions

import sqlite3 as lite
import md5
import time

conn = lite.connect('static/funct/twmp.db', check_same_thread=False)


def version():
    with conn:
        cur = conn.cursor()
        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()
        return "SQLite version: %s" % data


def table(table='peeps'):
    if table == 'peeps':
        with conn:
            cur = conn.cursor()
            cur.executescript("""DROP TABLE IF EXISTS Peeps;
                              CREATE TABLE Peeps(Email TEXT PRIMARY KEY,
                                                 Password TEXT,
                                                 Created INTEGER,
                                                 Plan TEXT,
                                                 Paid INTEGER,
                                                 Sent INTEGER)""")
    elif table == 'terms':
        with conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE Terms(Email TEXT, Term TEXT)")
    return True


def usercreate(data):
    ''' Create with json of email & password '''
    email = data['email']
    saltpw = 'twiTTer%smInInG' % data['password']
    password = md5.new(saltpw).hexdigest()
    with conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO Peeps VALUES(?,?,?,?,?,?)",
                (email, password, int(time.time()), '', 0, 0))
            return True
        except StandardError as e:
            print 'ERROR: ', e
            return False


def userget(email=None):
    if email is None:
        sql = "SELECT * FROM Peeps"
    else:
        sql = "SELECT * FROM Peeps WHERE Email='%s'" % email
    with conn:
        conn.row_factory = lite.Row
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        alldata = []
        for row in rows:
            data = {}
            data['email'] = row['Email']
            data['password'] = row['Password']
            data['created'] = row['Created']
            data['plan'] = row['Plan']
            data['paid'] = row['Paid']
            data['sent'] = row['Sent']
            alldata.append(data)
        if len(alldata) == 1:
            alldata = alldata[0]
        return alldata


def update_pw(data):
    ''' Update account with json of email & password '''
    email = data['email']
    saltpw = 'twiTTer%smInInG' % data['password']
    password = md5.new(saltpw).hexdigest()
    with conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE Peeps SET Password=? WHERE Email=?",
            (password, email))
        return True


def update_plan(data):
    ''' Update account plan '''
    email = data['email']
    plan = data['plan']
    with conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE Peeps SET Plan=? WHERE Email=?",
            (plan, email))
    if plan == 'bronze':
        update_pd(data)
        return True


def update_pd(data):
    ''' Update account with json of email'''
    email = data['email']
    date = int(time.time())
    with conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE Peeps SET Paid=? WHERE Email=?",
            (date, email))
        return True


def userlogin(data):
    ''' Validate json of email & password '''
    email = data['email']
    saltpw = 'twiTTer%smInInG' % data['password']
    password = md5.new(saltpw).hexdigest()
    with conn:
        conn.row_factory = lite.Row
        cur = conn.cursor()
        cur.execute("SELECT Password FROM Peeps where Email=?", (email,))
        row = cur.fetchall()
        try:
            if password == row[0]['password']:
                return True
        except:
            return False
    return False


def add_term(data):
    ''' Add term from json of email + term '''
    email = data['email']
    terms = data['terms']
    plan = data['plan']
    limit = 5
    if plan == 'bronze':
        limit = 1
    elif plan == 'gold':
        limit = 10
    temp = terms[:limit]
    termset = '~'.join([x.replace('~', '') for x in temp])
    with conn:
        # Remove old terms
        cur = conn.cursor()
        cur.execute("DELETE FROM Terms WHERE Email=?", (email,))
        cur.fetchall()
        # Set new
        cur = conn.cursor()
        cur.execute("INSERT INTO Terms VALUES(?,?)", (email, termset))
        cur.fetchall()


def get_terms(email):
    ''' Get terms from email '''
    terms = ['', '', '', '', '', '', '', '', '', '']
    with conn:
        cur = conn.cursor()
        cur.execute("SELECT Term FROM Terms WHERE Email=?", (email,))
        row = cur.fetchall()
        if len(row) > 0:
            terms = row[0][0].split('~')
    return terms


def get_mech():
    '''Display data for mech page'''
    data = [['Name | Plan | Paid | Sent | Terms']]
    with conn:
        conn.row_factory = lite.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Peeps NATURAL JOIN Terms;")
    rows = cur.fetchall()
    if len(rows) > 0:
        for row in rows:
            line = [row['Email'], row['Plan'], row['Paid'],
                    row['Sent'], row['Term']]
            data.append(line)
    return data
