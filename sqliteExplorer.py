from logging import exception, getLogger
from tkinter.messagebox import showerror, showinfo
from flask import Flask, render_template, request, redirect
import sqlite3
from os import path as os_path, environ
from json import dumps as json_dumps
from werkzeug.utils import secure_filename
from webbrowser import open as webbrowser_open
from pickle import load as pickle_load, dumps as pickle_dumps 
from tkinter import *
import tkinter.filedialog as filedialog

template_folder = os_path.abspath("pages")
static_folder = os_path.abspath("media")
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

getLogger('werkzeug').disabled = True
environ['WERKZEUG_RUN_MAIN'] = 'true'


file_for_storing = "media/data/data.sqliteExplorer"
def get_data():
    with open(file_for_storing, "rb") as e:
        return pickle_load(e)

def write_data(data):
    with open(file_for_storing, "wb") as e:
        e.write(pickle_dumps(data))

root = Tk()
def newDatabase(event):
    global database
    database = filedialog.asksaveasfilename(initialfile="*.db", filetypes=(('database files', 'db'),))
    if database == "":
        showerror("Error", "Please choose a filename and save it")
        exit()
    else:
        write_data({"file_location": database})
        root.destroy()


def openDatabase(event):
    global database
    database = filedialog.askopenfilename()
    if database == "":
        showerror("Error", "Please choose a database first")
        exit()
    else:
        write_data({"file_location": database})
        root.destroy()

def openLastDatabase(event):
    global database
    database = get_data()["file_location"]
    if database == "":
        showerror("Error", "Failed to open the database")
        exit()
    else:
        pass
        root.destroy()

def resetApp(event):
    write_data({"file_location": ""})
    showinfo("Info", "The application has been reset successfully")
    root.destroy()
    exit()


root.title("SQLite Database Explorer")
root.geometry("400x220")
# root.wm_iconbitmap("media/images/sqliteExplorer.ico")
root.minsize(400, 200)
root.maxsize(455, 300)
root.config(background="#ffffff")
button1 = Button(root, text="New Database", cursor="hand2")
button1.bind("<Button-1>", newDatabase)
button2 = Button(root, text="Open Database", cursor="hand2")
button2.bind("<Button-1>", openDatabase)
button3 = Button(root, text="Open Last Database", cursor="hand2")
button3.bind("<Button-1>", openLastDatabase)
button4 = Button(root, text="Reset App", cursor="hand2")
button4.bind("<Button-1>", resetApp)

frame1 = Frame(root)
frame1.pack(pady=20)
button1.pack(padx=140, pady=3, ipadx=13)
button2.pack(padx=140, pady=3, ipadx=10)
if get_data()["file_location"] != "":
    button3.pack(padx=140, pady=3)
    button4.pack(padx=140, pady=3, ipadx=26)

root.mainloop()



# database = "data.ytconvert"
# print(database)
# conn = sqlite3.connect(database, check_same_thread=False)
conn = sqlite3.connect(database, check_same_thread=False)

def sqliteFetch(query):
    data = conn.execute(f''' {query} ''')
    return data.fetchall()

def get_table_info(table):
    data = conn.execute(f'''
    PRAGMA table_info('{table}')
    ''')
    return data.fetchall()

def sendJson(dict, statusCode):
    response = app.response_class(
        response=json_dumps(dict),
        status=statusCode,
        mimetype="application/json"
    )
    return response

basicdata = {
    "database_name": os_path.basename(database),
    "table_array": sqliteFetch(''' select `tbl_name` from sqlite_master WHERE `tbl_name` IS NOT 'sqlite_sequence' '''),
    "database_location": database
}

@app.route("/")
def index():
    return render_template("index.sqliteExplorer", basicdata=basicdata)

@app.route("/browse")
def browse():
    if "table" in request.args:
        table = request.args.get("table")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        if "search_query" in request.args:
            search_query = request.args.get("search_query").replace("'", "&apos;")
            q = f''' SELECT * FROM {table} WHERE '''
            keys = get_table_info(table)
            i = 0
            for key in keys:
                i += 1
                if (len(keys) <= i):
                    q += f'''{key[1]} LIKE '%{ search_query }%' '''
                else:
                    q += f'''{key[1]} LIKE '%{ search_query }%' OR '''
            query = sqliteFetch(q)
            buttonDisabled = True
        else:
            query = sqliteFetch(f'''SELECT * FROM {table} LIMIT 50''')
            buttonDisabled = False
        column_data = get_table_info(table)
        primary_key = None
        primary_key_index = None
        for data in column_data:
            if data[5] == 1:
                primary_key = data[1]
                primary_key_index = data[0]
                break
        data = {
            "column_names": column_data,
            "rows": query,
            "primary_key": primary_key,
            "primary_key_index": primary_key_index
        }

        return render_template("browse.sqliteExplorer", basicdata=basicdata, selected_table=table, data=data, buttonDisabled=buttonDisabled)
    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.route("/~fetchrows", methods=['POST'])
def fetchrows():
    if "rows" in request.form and "table" in request.form:
        rows = request.form.get("rows")
        table = request.form.get("table")
        data = sqliteFetch(f''' SELECT * FROM {table} LIMIT {rows}, 50 ''')
        if data == []:
            return sendJson({"status": "finished", "message": "Finished"}, 200)
        return sendJson(data, 200)
    else:
        return sendJson({"status": "failure", "message": "Parameters are needed"}, 405)


@app.route("/structure")
def structure():
    if "table" in request.args:
        table = request.args.get("table")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        data = get_table_info(table)
        return render_template("structure.sqliteExplorer", basicdata=basicdata, selected_table=table, data=data)
    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.route("/create")
def create_table():
    return render_template("table.sqliteExplorer", basicdata=basicdata)

@app.post("/~create-table")
def create_table_function():
    if "sql" in request.form:
        sql = request.form.get("sql")
        try:
            conn.execute(sql)
            conn.commit()
            returnData = {
                "status": "success"
            }
        except exception as e:
            returnData = {
                "status": "failure",
                "message": e
            }
        return sendJson(returnData, 200)
    return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.route("/insert")
def insert():
    if "table" in request.args:
        table = request.args.get("table")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        data = get_table_info(table)
        return render_template("insert.sqliteExplorer", basicdata=basicdata, selected_table=table, data=data)
    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.post("/~insert-data")
def insert_data():
    if "sql" in request.form:
        sql = request.form.get("sql")

        try:
            conn.execute(sql)
            conn.commit()
            returnData = {
                "status": "success"
            }
        except exception as e:
            returnData = {
                "status": "failure",
                "message": e
            }
        return sendJson(returnData, 200)
    return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.route("/operations")
def operations():
    if "table" in request.args:
        table = request.args.get("table")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        data = get_table_info(table)
        return render_template("operations.sqliteExplorer", basicdata=basicdata, selected_table=table, data=data)
    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.post("/~empty-table")
def empty_table():
    if "table" in request.form:
        table = request.form.get("table")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        query = conn.execute(f''' DELETE FROM {table} ''')
        conn.commit()
        if query:
            returnData = {
                "status": "success"
            }
        else:
            returnData = {
                "status": "failure"
            }
        return sendJson(returnData, 200)

    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.post("/~delete-table")
def delete_table():
    if "table" in request.form:
        table = request.form.get("table")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        query = conn.execute(f''' DROP TABLE {table} ''')
        conn.commit()
        if query:
            returnData = {
                "status": "success"
            }
        else:
            returnData = {
                "status": "failure"
            }
        return sendJson(returnData, 200)

    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.post("/~rename-table")
def rename_table():
    if "pre_table_name" in request.form and "changed_table_name" in request.form:
        pre_table_name = request.form.get("pre_table_name")
        changed_table_name = request.form.get("changed_table_name")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{pre_table_name}' ''')) == [] or changed_table_name == "sqlite_sequence":
            return sendJson({"status": "failure"}, 500)
        query = conn.execute(f''' ALTER TABLE `{pre_table_name}` RENAME TO `{secure_filename(changed_table_name).replace(" ", "").replace("-", "_")}` ''')
        conn.commit()
        if query:
            returnData = {
                "status": "success"
            }
        else:
            returnData = {
                "status": "failure"
            }
        return sendJson(returnData, 200)

    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.route("/execute")
def execute_sql():
    return render_template("executesql.sqliteExplorer", basicdata=basicdata)

@app.post("/~sql-executer")
def sql_executer():
    if "query" in request.form:
        query = request.form.get("query")
        sqlQuery = conn.execute(query)
        conn.commit()
        if sqlQuery or sqlQuery.rowcount >= 1:
            returnData = {
                "status": "success",
                "data": sqlQuery.fetchall()
            }
        else:
            returnData = {
                "status": "failure",
                "message": "Can't execute this query"
            }
        return sendJson(returnData, 200)
    else:
        return sendJson({"status": "failure"}, 405)


@app.route("/addcolumn")
def add_column():
    if "table" in request.args and "col" in request.args:
        table = request.args.get("table")
        col = request.args.get("col")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        data = get_table_info(table)
        col = int(col)
        if col <= 0:
            col = 1
        elif col >= 100:
            col = 100
        return render_template("addcolumn.sqliteExplorer", basicdata=basicdata, selected_table=table, data=data, col=col)
    else:
        return render_template("error.sqliteExplorer", basicdata=basicdata), 404

@app.route("/editrow")
def edit_row():
    if "table" in request.args and "key" in request.args and "index" in request.args:
        table = request.args.get("table")
        key = request.args.get("key")
        index = request.args.get("index")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        table_data = get_table_info(table)
        column_data_fetched = sqliteFetch(f''' SELECT * FROM {table} WHERE {key} = '{index}' LIMIT 1 ''')
        if column_data_fetched == []:
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
        column_data = column_data_fetched[0]

        return render_template("editrow.sqliteExplorer", basicdata=basicdata, selected_table=table, table_data=table_data, column_data=column_data, key=key, index=index)

@app.route("/renamecolumn")
def rename_column():
    if "table" in request.args and "column" in request.args:
        table = request.args.get("table")
        column = request.args.get("column")
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template("error.sqliteExplorer", basicdata=basicdata), 404
    table_data = get_table_info(table)
    for data in table_data:
        if data[1] == column:
            column_data = data
            break
    return render_template("renamecolumn.sqliteExplorer", basicdata=basicdata, selected_table=table, column_data=column_data)



@app.route("/favicon.ico")
def favicon():
    return redirect("media/images/favicon.ico")

@app.errorhandler(404)
def errorhandler(error):
    return render_template("error.sqliteExplorer", basicdata=basicdata), 404



webbrowser_open("http://127.0.0.1:6068")
print("Started SQLite Explorer on http://127.0.0.1:6068")

app.run(port=6068)

