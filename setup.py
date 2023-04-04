from base64 import b64encode, b64decode

encodedCode= b64encode("""
from logging import getLogger
from tkinter.messagebox import showerror, showinfo
from flask import Flask, request, render_template_string
import sqlite3
from os import path as os_path
from json import dumps as json_dumps
from werkzeug.utils import secure_filename
from webbrowser import open as webbrowser_open
from pickle import load as pickle_load, dumps as pickle_dumps 
from tkinter import *
import tkinter.filedialog as filedialog
from math import ceil
import flask.cli
from base64 import b64decode

template_folder = os_path.abspath("includes")
app = Flask(__name__, template_folder=template_folder)


getLogger('werkzeug').disabled = True
flask.cli.show_server_banner = lambda *args: None


file_for_storing = "includes/data.sqliteExplorer"

pages = {
    "addcolumn": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .table-name-box {
        display: flex;
        align-items: center;
        margin-top: 5px;
    }

    .table-name-box p {
        margin-right: 10px;
    }

    .input {
        margin-right: 10px;
        box-shadow: none;
        outline: solid 2px transparent;
        transition: 0.2s;
    }

    .input:not([type=checkbox]):focus {
        outline: solid 2px rgb(226, 226, 226);
    }


    .input-full {
        width: 100%;
    }

    .input:focus {
        box-shadow: none;
        transform: none;
    }

    .table-container {
        margin-top: 12px;
    }

    select {
        width: 100%;
    }

    .save-button {
        margin-top: 15px;
        margin-bottom: 20px;
    }
</style>
<div class="table-container">
    <form id="data-form">
    <table class="db-table">
        <thead>
            <tr>
                <th style="width: 160px;">Name</th>
                <th style="width: 120px;">Type</th>
                <th style="width: 160px;">Default</th>
                <th style="width: 40px;">Null</th>
                <th style="width: 140px;">Index</th>
                <th>AutoIncrement</th>
            </tr>
        </thead>
        <tbody id="rows">
            <tr>
                <td><input type="text" class="input input-full get_column_name"></td>
                <td>
                    <select class="input input-full get_column_type">
                        <option
                            title="The value is a signed integer, stored in 0, 1, 2, 3, 4, 6, or 8 bytes depending on the magnitude of the value.">
                            INTEGER</option>
                        <option
                            title="The value is a text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE).">
                            TEXT</option>
                        <option title="The value is a blob of data, stored exactly as it was input.">BLOB</option>
                        <option
                            title="The value is a floating point value, stored as an 8-byte IEEE floating point number.">
                            REAL</option>
                    </select>
                </td>
                <td><input type="text" class="input input-full get_default" list="defaultList"></td>
                <td><input type="checkbox" class="input-full get_null"></td>
                <td>
                    <select class="input select-index get_index">
                        <option value="">---</option>
                        <option value="PRIMARY">PRIMARY</option>
                    </select>
                </td>
                <td><input type="checkbox" class="input autoincrement-input get_autoincrement"
                        data-autoincrementpointer="{{i}}"></td>
            </tr>
        </tbody>
    </table>
    <button class="btn save-button" id="save-button">Save</button>
</form>
</div>
<datalist id="defaultList">
    <option value="NULL">
</datalist>
<script>
    function _(elms) {
        return document.querySelectorAll(elms);
    }
    function _id(elm) {
        return document.getElementById(elm);
    }

    function check() {
        _(".autoincrement-input").forEach(element => {
            element.addEventListener("click", (e) => {
                let check = element.checked;
                if (check) {
                    let pointer = element.getAttribute("data-autoincrementpointer");
                    _(".select-index")[pointer].value = "PRIMARY";
                }
            })
        })
    }
    check();


    _id("save-button").addEventListener("click", (e) => {
        const formData = new FormData();
        let query = "";
        let primary_key = "";
        let looped = 0;
        _("#rows tr").forEach(element => {
            if (element.getElementsByClassName("get_column_name")[0].value != "") {
                let column_name = element.getElementsByClassName("get_column_name")[0].value;
                let column_type = element.getElementsByClassName("get_column_type")[0].value;
                let column_default = element.getElementsByClassName("get_default")[0].value;
                let column_null = element.getElementsByClassName("get_null")[0].checked;
                let column_index = element.getElementsByClassName("get_index")[0].value;
                let column_autoIncrement = element.getElementsByClassName("get_autoincrement")[0].checked;

                // Column Null
                if (column_null) {
                    column_null = "NULL";
                }
                else {
                    column_null = "NOT NULL";
                }
                // Column default
                if (column_default == "") {
                    column_default = "";
                }
                else if (column_default == "NULL") {
                    column_default = "DEFAULT NULL";
                }
                else {
                    if (column_type == "INTEGER") {
                        column_default = `DEFAULT ${parseInt(column_default)}`;
                    }
                    else {
                        column_default = `DEFAULT '${column_default}'`;
                    }
                }

                // Auto Increment
                if (column_autoIncrement) {
                    column_autoIncrement = "AUTOINCREMENT";
                }
                else {
                    column_autoIncrement = "";
                }
                // Primary Key
                if (column_index == "PRIMARY") {
                    primary_key = ` PRIMARY KEY`;
                }
                else {
                    primary_key = "";
                }

                let comma = ""
                if (looped != 0) {
                    comma = ","
                }
                query += `${comma} \`${column_name.replace(" ", "_").replace("-", "_")}\` ${column_type} ${column_null}${primary_key} ${column_autoIncrement} ${column_default}`;
                looped++;
            }
        })

        let sqlQuery = `ALTER TABLE \`{{ selected_table }}\` ADD ${query}`;
        formData.append("query", sqlQuery);
        fetch("/~sql-executer", {
            method: "POST",
            body: formData
        }).then(response => response.json()).then((data) => {
            if (data.status == "success") {
                showAlert("Column added successfully", "green")
                _id("data-form").reset();
                setTimeout(() => {
                    window.open(`/structure?table={{ selected_table }}`, "_self").focus();
                }, 5000);
            }
            else {
                showAlert("Error: Failed to add column", "red")
            }
        }).catch((err) => {
            if (err) {
                showAlert("Error: Failed to add column", "red")
            }
        })

    })

    _id("data-form").addEventListener("submit", (e)=> {
        e.preventDefault();
    })



</script>
{% endblock %}''',


    "browse": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .db-table tbody tr td:first-child {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.db-table tbody tr td:first-child span a {
    text-decoration: none;
    color: #000;
    margin-left: 3px;
    margin-right: 3px;
    cursor: pointer;
}
.db-table tbody tr td:first-child span a:hover {
    text-decoration: underline;
}
</style>
<nav class="data-navbar">
    <ul>
        <a href="/browse?table={{ selected_table }}" class="active">
            <li>Browse</li>
        </a>
        <a href="/structure?table={{ selected_table }}">
            <li>Structure</li>
        </a>
        <a href="/insert?table={{ selected_table }}">
            <li>Insert</li>
        </a>
        <a href="/operations?table={{ selected_table }}">
            <li>Operations</li>
        </a>
    </ul>
</nav>
<div class="table-container">
    <table class="db-table">
        <thead>
            <tr>
                {% if data["primary_key"] != None %}
                <th style="width: 140px;">Actions</th>
                {% endif %}
                {% for i in data["column_names"] %}
                <th>{{ i[1] }}</th>
                {% endfor %}
            </tr>
        </thead>
        <tbody id="rows">
            {% for i in data["rows"] %}
            <tr>
                {% if data["primary_key"] != None %}
                <td><input type="checkbox" data-index="{{ i[data["primary_key_index"]] }}" class="row-checkbox"><span><a href="/editrow?table={{ selected_table }}&key={{ data["primary_key"] }}&index={{ i[data["primary_key_index"]] }}">Edit</a><a onclick="deleteRow('{{ i[data["primary_key_index"]]}}', this)">Delete</a></span></td>
                {% endif %}
                {% for j in i %}
                <td>{{ (j | string).replace("<", "&#60;").replace(">", "&#62;")[0:200] }}</td>
                {% endfor %}
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="controlls">
    {% if data["primary_key"] != None %}
    <div>
        <button class="btn" id="checkAllButton">Check All</button>
        <button class="btn" id="deleteCheckedRowsButton">Delete</button>
    </div>
    {% endif %}
    <div>
        {% if not buttonDisabled %}
        <div class="btnGroup">
            {{ buttons | safe }}
        </div>
        {% endif %}
    </div>
    <form id="search-form">
        <input type="text" id="query" class="input" placeholder="Search..." required>
        <button type="submit" class="btn">Search</button>
    </form>
</div>
<script>
    function _id(elm) {
        return document.getElementById(elm);
    }
    function _(selector) {
        return document.querySelectorAll(selector);
    }
    {% if data["primary_key"] != None %}
    let checkedAll = false;
    _id("checkAllButton").addEventListener("click", (e)=> {
        if (!checkedAll) {
            _(".row-checkbox").forEach(element=> {
                element.checked = true;
            })
            e.target.innerHTML = "Uncheck All";
            checkedAll = true;
        }
        else {
            _(".row-checkbox").forEach(element=> {
                element.checked = false;
            })
            e.target.innerHTML = "Check All";
            checkedAll = false;
        }
    })
    {% endif %}

    _id("search-form").addEventListener("submit", (e)=> {
        e.preventDefault();
        let query = _id("query").value;
        window.open(`/browse?table={{ selected_table }}&search_query=${query}`, "_self").focus();
    })
    function deleteRow(index, element) {
        if (confirm("Do you want to delete this row?")) {
            let query = `DELETE FROM \`{{ selected_table }}\` WHERE {{ data["primary_key"] }} = '${index}'`;
            let formData = new FormData();
            formData.append("query", query);
            fetch("/~sql-executer", {
                method: "POST",
                body: formData
            }).then(response=>response.json()).then(data=>{
                if (data.status == "success") {
                    showAlert("Row deleted successfully", "green");
                    _id("rows").removeChild(element.parentNode.parentNode.parentNode);
                }
                else {
                    showAlert("Can't delete this row", "red");
                }
            }).catch(err=>{
                showAlert("Can't delete this row", "red");
            })
        }
    }

    {% if data["primary_key"] != None %}
    _id("deleteCheckedRowsButton").addEventListener("click", (e)=> {
        let indexes = "";
        let i = 0;
        let willDelete = false;
        _(".row-checkbox").forEach(element=>{
            if (element.checked) {
                willDelete = true;
                let data_index = element.getAttribute("data-index");
                let comma = ",";
                if (i == 0) {
                    comma = "";
                }
                else {
                    comma = ","
                }
                indexes += comma + data_index;
                i++;
            }
        })
        if (willDelete) {
            let sqlQuery = `DELETE FROM {{ selected_table }} WHERE \`{{ data["primary_key"] }}\` IN (${indexes})`;
            let randomNumber = Math.floor(Math.random() * (9999 - 1000)) + 1000;
            if (prompt(`Enter ${randomNumber} to delete the rows`) == randomNumber) {
                let formData = new FormData();
                formData.append("query", sqlQuery);
                fetch("/~sql-executer", {
                    method: "POST",
                    body: formData
                }).then(response=>response.json()).then(data=>{
                    if (data.status == "success") {
                    showAlert("Selected rows has been deleted successfully", "green");
                    setTimeout(() => {
                        location.reload();
                    }, 5000);
                    }
                    else {
                        showAlert("Error: Can't delete the rows", "red");
                    }
                }).catch(err=>{
                    showAlert("Error: Can't delete the rows", "red");
                })
            }
        }
    })
    {% endif %}

</script>
{% endblock %}''',

    "editrow": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .input {
        width: 100%;
        margin-right: 10px;
        box-shadow: none !important;
        outline: solid 2px transparent;
        resize: vertical;
        transition: outline 0.2s;
    }

    .input:focus {
        box-shadow: none;
        transform: none;
        outline: solid 2px #eee;
    }

    .input {
        font-size: 14px;
    }

    textarea {
        font-family: monospace;
    }

    .btnInsert {
        margin-top: 12px;
        margin-bottom: 12px;
    }
</style>
<nav class="data-navbar">
    <ul>
        <a href="/browse?table={{ selected_table }}">
            <li>Browse</li>
        </a>
        <a href="/structure?table={{ selected_table }}">
            <li>Structure</li>
        </a>
        <a href="/insert?table={{ selected_table }}">
            <li>Insert</li>
        </a>
        <a href="/operations?table={{ selected_table }}">
            <li>Operations</li>
        </a>
    </ul>
</nav>

<div class="table-container">
    <form id="data-inserter-form">
        <table class="db-table">
            <thead>
                <tr>
                    <th style="width: 140px;">Column</th>
                    <th style="width: 140px;">Type</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                {% for i in table_data %}
                <tr class="get_column_data">
                    <td class="get_column_name">{{ i[1] }}</td>
                    <td class="get_column_type" data-primarykey="{{ i[5] }}">{{ i[2] }}</td>
                    <td>
                        {% if i[2] in ["TEXT", "BLOB", "LONGTEXT", "LONGBLOB"] %}
                        <textarea cols="30" rows="10" class="input get_column_value">{{ (column_data[loop.index-1] | string ).replace("<", "&#60;").replace(">", "&#62;").replace('"', '&#34;') }}</textarea>
                        {% else %}
                        <input type="text" class="input get_column_value" value="{{ (column_data[loop.index-1] | string ).replace("<", "&#60;").replace(">", "&#62;").replace('"', '&#34;') }}">
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </form>
    <button type="button" class="btn btnInsert" id="updateButton">Update</button>
</div>
<script>
    function _(elms) {
        return document.querySelectorAll(elms);
    }
    function _id(elm) {
        return document.getElementById(elm);
    }

    _id("updateButton").addEventListener("click", () => {
        let keys = [];
        let values = [];
        _(".get_column_data").forEach(element => {
            let column_name = element.getElementsByClassName("get_column_name")[0].innerText;
            let column_value = element.getElementsByClassName("get_column_value")[0].value;
            keys.push(column_name);
            values.push(column_value);
        })
        let set = "";
        let j = 0;
        let updateRow = false;
        for (let i = 0; i < keys.length; i++) {
                updateRow = true;
                let comma = "";
                if (j == 0) {
                    comma = "";
                }
                else {
                    comma = ",";
                }
                set += `${comma} \`${keys[i]}\` = '${values[i].replace("'", "&apos;")}'`;
                j++;
        }
        if (updateRow) {
            let sqlQuery = `UPDATE \`{{selected_table}}\` SET ${set} WHERE {{ key }} = '{{ index }}' `;
            let formData = new FormData();
            formData.append("query", sqlQuery);
            fetch("/~sql-executer", {
                method: "POST",
                body: formData
            }).then(response => response.json()).then(data => {
                if (data.status == "success") {
                    showAlert("Row updated successfully", "green");
                }
                else {
                    showAlert("Error: Can't update the row", "red");
                }
            }).catch(err => {
                if (err) {
                    showAlert("Error: Can't update the row", "red");
                }
            })
        }
    })
    _id("data-inserter-form").addEventListener("submit", (e) => {
        e.preventDefault();
    })

</script>
{% endblock %}''',

    "error": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
.error-container {
    width: 100%;
    height: calc(100% - 140px);
    display: flex;
    justify-content: center;
    align-items: center;
}
.error-container h1 {
    font-size: 40px;
    margin-right: 20px;
}
</style>
<div class="error-container">
    <h1>404</h1>
    <p>Sorry, the requested URL was not found on this server.</p>
</div>
{% endblock %}''',

    "servererror": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
.error-container {
    width: 100%;
    height: calc(100% - 140px);
    display: flex;
    justify-content: center;
    align-items: center;
}
.error-container h1 {
    font-size: 40px;
    margin-right: 20px;
}
</style>
<div class="error-container">
    <h1>500</h1>
    <p>Internal server error.</p>
</div>
{% endblock %}''',



    "executesql": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
.sqlTextArea {
    width: 100%;
    outline: none;
    border: solid 1px #eee;
    resize: vertical;
    padding: 5px;
    border-radius: 4px;
    font-family: monospace;
    outline: solid 2px transparent;
    transition: outline 0.2s;
}
.sqlTextArea:focus {
    outline: solid 2px #eee;
}
.margin-top-10 {
    margin-top: 10px;
}
.margin-top-5 {
    margin-top: 5px;
}
</style>
<div class="table-container" style="padding-bottom: 10px;">
    <textarea id="sqlQuery" cols="30" rows="10" class="sqlTextArea"></textarea>
    <button class="btn" onclick="clearText('#sqlQuery')">Clear</button>
    <button class="btn" id="executeButton">Execute</button>
    <div id="output" class="margin-top-10">
    </div>
</div>
<script>
    function _id(elm) {
        return document.getElementById(elm);
    }
    _id("executeButton").addEventListener("click", (e)=> {
        const formData = new FormData();
        let query = _id("sqlQuery").value;
        if (query != "") {
        formData.append("query", query);
        fetch("/~sql-executer", {
            method: "POST",
            body: formData
        }).then(response=>response.json()).then(data=>{
            if (data.status == "success") {
                showAlert("Query executed successfully", "green");
                if (data.data.length > 0) {
                    _id("output").innerHTML = `<h4>Output:</h4>
                    <textarea cols="30" rows="10" class="sqlTextArea margin-top-5" id="sqlOutput">${JSON.stringify(data.data)}</textarea>
                    <button class="btn" onclick="clearText('#sqlOutput')"">Clear</button>
                    <button class="btn" onclick="copyText(this, '#sqlOutput')">Copy</button>`;
                }
                else {
                    _id("output").innerHTML = "";
                    refreshData();
                }
            }
            else {
                showAlert("Error: Can't execute this query", "red");
            }
        }).catch(err=> {
            if (err) {
                showAlert("Error: Can't execute this query", "red");
            }
        })
    }
    })
</script>
{% endblock %}''',


    "index": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .home-container {
        width: 100%;
        height: calc(100% - 146px);
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 20px;
    }

    .homeImage {
        width: 200px;
        user-select: none;
        pointer-events: none;
    }

</style>
<div class="home-container">
    <div class="home-imagebox">
        <img src="/media/images/logo.jpg" alt="SQLite Explorer" class="homeImage">
    </div>
</div>
</div>
{% endblock %}''',

    "insert": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .input {
        width: 100%;
        margin-right: 10px;
        box-shadow: none !important;
        outline: solid 2px transparent;
        resize: vertical;
        transition: outline 0.2s;
    }

    .input:focus {
        box-shadow: none;
        transform: none;
        outline: solid 2px #eee;
    }

    .input {
        font-size: 14px;
    }

    textarea {
        font-family: monospace;
    }

    .btnInsert {
        margin-top: 12px;
        margin-bottom: 12px;
    }
</style>
<nav class="data-navbar">
    <ul>
        <a href="/browse?table={{ selected_table }}">
            <li>Browse</li>
        </a>
        <a href="/structure?table={{ selected_table }}">
            <li>Structure</li>
        </a>
        <a href="/insert?table={{ selected_table }}" class="active">
            <li>Insert</li>
        </a>
        <a href="/operations?table={{ selected_table }}">
            <li>Operations</li>
        </a>
    </ul>
</nav>

<div class="table-container">
    <form id="data-inserter-form">
        <table class="db-table">
            <thead>
                <tr>
                    <th style="width: 140px;">Column</th>
                    <th style="width: 140px;">Type</th>
                    <th>Value</th>
                </tr>
            </thead>
            <tbody>
                {% for i in data %}
                <tr class="get_column_data">
                    <td class="get_column_name">{{ i[1] }}</td>
                    <td class="get_column_type" data-primarykey="{{ i[5] }}">{{ i[2] }}</td>
                    <td>
                        {% if i[2] in ["TEXT", "BLOB"] %}
                        <textarea cols="30" rows="10"
                            class="input get_column_value">{% if i[4] in [None, NULL, "None", "NULL"] %}{% else %}{{ i[4].replace("'", "") }}{% endif %}</textarea>
                        {% else %}
                        <input type="text" class="input get_column_value"
                            value='{% if i[4] == "CURRENT_TIMESTAMP" %}current_timestamp(){% elif i[4] in [None, NULL, "None", "NULL"] %}{% else %}{{ i[4].replace("'", "") }}{% endif %}'>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </form>
    <button type="button" class="btn btnInsert" id="insertButtton">Insert</button>
</div>
<script>
    function _(elms) {
        return document.querySelectorAll(elms);
    }
    function _id(elm) {
        return document.getElementById(elm);
    }

    _id("insertButtton").addEventListener("click", () => {
        let keys = [];
        let values = [];
        _(".get_column_data").forEach(element => {
            let column_name = element.getElementsByClassName("get_column_name")[0].innerText;
            let column_value = element.getElementsByClassName("get_column_value")[0].value;
            keys.push(column_name);
            values.push(column_value);
        })
        let bracket1 = `(`;
        for (let i = 0; i < keys.length; i++) {
            let comma = ","
            if (i == 0) {
                comma = "";
            }
            bracket1 += comma + keys[i];
        }
        bracket1 += `)`;

        let bracket2 = `(`;
        for (let i = 0; i < values.length; i++) {
            let comma = ",";
            if (i == 0) {
                comma = "";
            }

            let valueQuery = `'${parseText(values[i])}'`;
            if (_(".get_column_type")[i].getAttribute("data-primarykey") == 1 && values[i] == "") {
                valueQuery = "NULL";
            }

            bracket2 += comma + valueQuery;
        }
        bracket2 += `)`;
        let sqlQuery = `INSERT INTO \`{{selected_table}}\` ${bracket1} VALUES ${bracket2}`;
        let formData = new FormData();
        formData.append("sql", sqlQuery);
        fetch("/~insert-data", {
            method: "POST",
            body: formData
        }).then(response => response.json()).then((data) => {
            if (data.status == "success") {
                showAlert("Data inserted successfully", "green")
                _id("data-inserter-form").reset();
            }
        }).catch(err => {
            if (err) {
                showAlert("Error: The server is facing some internal issues", "red");
            }
        })

    })
    _id("data-inserter-form").addEventListener("submit", (e) => {
        e.preventDefault();
    })

</script>
{% endblock %}''',

    "operations": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<nav class="data-navbar">
    <ul>
        <a href="/browse?table={{ selected_table }}">
            <li>Browse</li>
        </a>
        <a href="/structure?table={{ selected_table }}">
            <li>Structure</li>
        </a>
        <a href="/insert?table={{ selected_table }}">
            <li>Insert</li>
        </a>
        <a href="/operations?table={{ selected_table }}" class="active">
            <li>Operations</li>
        </a>
    </ul>
</nav>
<style>
    .operations-card {
        max-width: 100%;
        width: 100%;
        padding: 20px;
        background: #fbfbfb;
        border-radius: 4px;
        margin: auto;
    }
    .operations-card-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .operations-card-column-3 {
        flex: 60%;
        max-width: 60%;
        margin-right: 10px;
    }
    .operations-card-column-1 {
        flex: 40%;
        max-width: 40%;
        margin-left: 10px;
        display: flex;
        flex-direction: column;
    }
    .input {
        width: 100%;
        box-shadow: none;
        padding: 8px;
        outline: solid 2px transparent;
        transition: 0.2s;
    }
    .input:focus {
        box-shadow: none;
        transform: none;
        outline: solid 2px #eee;
    }
    .operation-rename-btn {
        margin-top: 10px;
    }
    .operation-red-text {
        color: rgb(255, 0, 36);
        text-decoration: none;
        display: block;
        margin-bottom: 6px;
        text-align: center;
        cursor: pointer;
    }
    .operation-red-text:hover {
        text-decoration: underline;
    }
</style>
<div class="operations-card">
    <div class="operations-card-row">
        <div class="operations-card-column-3">
            <input type="text" class="input" id="get_table_name" value="{{ selected_table }}" placeholder="Table Name">
            <button class="btn operation-rename-btn" id="renameButton">Rename</button>
        </div>
        <div class="operations-card-column-1">
            <p href="#" class="operation-red-text" id="empty-table">Empty The Table</p>
            <p href="#" class="operation-red-text" id="delete-table">Delete The Table</p>
        </div>
    </div>
</div>
<script>
    function _id(elm) {
        return document.getElementById(elm);
    }
    _id("empty-table").addEventListener("click", (e)=> {
        let randomNumber = Math.floor(Math.random() * (9999 - 1000)) + 1000;
        if (prompt(`Enter ${randomNumber} to empty the table`) == randomNumber) {
            const formData = new FormData();
            formData.append("table", `{{ selected_table }}`);
            fetch("/~empty-table", {
                method: "POST",
                body: formData
            }).then(response=>response.json()).then(data=>{
                if (data.status == "success") {
                    showAlert("{{ selected_table }} has been blanked successfully", "green");
                }
                else {
                    showAlert("Error: The server is facing some internal issues", "red");
                }
            }).catch(err=> {
                if (err) {
                    showAlert("Error: The server is facing some internal issues", "red");
                }
            })
        }
    })
    _id("delete-table").addEventListener("click", (e)=> {
        let randomNumber = Math.floor(Math.random() * (9999 - 1000)) + 1000;
        if (prompt(`Enter ${randomNumber} to delete the table`) == randomNumber) {
            const formData = new FormData();
            formData.append("table", `{{ selected_table }}`);
            fetch("/~delete-table", {
                method: "POST",
                body: formData
            }).then(response=>response.json()).then(data=>{
                if (data.status == "success") {
                    showAlert("{{ selected_table }} has been deleted successfully!", "green");
                    refreshData();
                    setTimeout(() => {
                        window.open("/", "_self").focus();
                    }, 5000);
                }
                else {
                    showAlert("Error: The server is facing some internal issues", "red");
                }
            }).catch(err=> {
                if (err) {
                    showAlert("Error: The server is facing some internal issues", "red");
                }
            })
        }
    })
    _id("renameButton").addEventListener("click", ()=> {
        let randomNumber = Math.floor(Math.random() * (9999 - 1000)) + 1000;
        if (prompt(`Enter ${randomNumber} to rename the table`) == randomNumber) {
            const formData = new FormData();
            formData.append("pre_table_name", `{{ selected_table }}`);
            let new_table_name = _id("get_table_name").value.replace(" ", "_").replace("-", "_");
            formData.append("changed_table_name", new_table_name);
            fetch("/~rename-table", {
                method: "POST",
                body: formData
            }).then(response=>response.json()).then(data=>{
                if (data.status == "success") {
                    showAlert(`{{ selected_table }} has been renamed to ${new_table_name}!`, "green");
                    refreshData();
                    setTimeout(() => {
                        window.open(`/operations?table=${new_table_name}`, "_self").focus();
                    }, 5000);
                }
                else {
                    showAlert("Error: Can't rename", "red");
                }
            }).catch(err=> {
                if (err) {
                    showAlert("Error: Can't rename", "red");
                }
            })
        }
        
    })
</script>
{% endblock %}''',

    "renamecolumn": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .table-name-box {
        display: flex;
        align-items: center;
        margin-top: 5px;
    }

    .table-name-box p {
        margin-right: 10px;
    }

    .input {
        margin-right: 10px;
        box-shadow: none;
        outline: solid 2px transparent;
        transition: 0.2s;
    }

    .input:not([type=checkbox]):focus {
        outline: solid 2px rgb(226, 226, 226);
    }


    .input-full {
        width: 100%;
    }

    .input:focus {
        box-shadow: none;
        transform: none;
    }

    .table-container {
        margin-top: 12px;
    }

    select {
        width: 100%;
    }

    .save-button {
        margin-top: 15px;
        margin-bottom: 20px;
    }
</style>
<div class="table-container">
    <form id="data-form">
    <table class="db-table">
        <thead>
            <tr>
                <th>Name</th>
            </tr>
        </thead>
        <tbody id="rows">
            <tr>
                <td><input style="width: 260px;" type="text" id="get_column_name" class="input input-full" value="{{ column_data[1] }}"></td>
            </tr>
        </tbody>
    </table>
    <button class="btn save-button" id="update-button">Rename</button>
</form>
</div>
<datalist id="defaultList">
    <option value="NULL">
</datalist>
<script>
    function _(elms) {
        return document.querySelectorAll(elms);
    }
    function _id(elm) {
        return document.getElementById(elm);
    }


    _id("update-button").addEventListener("click", (e) => {
        let formData = new FormData();
        let pre_column_name = `{{ column_data[1] }}`;
        let new_column_name = _id("get_column_name").value;
        if (pre_column_name != new_column_name) {
        let sqlQuery = `ALTER TABLE \`{{ selected_table }}\` RENAME \`${pre_column_name}\` TO \`${new_column_name}\``;
        formData.append("query", sqlQuery);
        fetch("/~sql-executer", {
            method: "POST",
            body: formData
        }).then(response => response.json()).then((data) => {
            if (data.status == "success") {
                showAlert("Column renamed successfully", "green");
                setTimeout(() => {
                    window.open("/structure?table={{ selected_table }}", "_self").focus();
                }, 5000);
            }
            else {
                showAlert("Error: Can't rename", "red");
            }
        }).catch(err=>{
            if (err) {
                showAlert("Error: Can't rename", "red");
            }
        })               
    }

    })

    _id("data-form").addEventListener("submit", (e)=> {
        e.preventDefault();
    })



</script>
{% endblock %}''',


    "structure": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .db-table tbody tr td:last-child {
        display: flex;
        justify-content: flex-start;
        align-items: center;
    }

    .db-table tbody tr td:last-child a {
        text-decoration: none;
        color: #000;
        margin-left: 3px;
        margin-right: 3px;
        cursor: pointer;
    }

    .db-table tbody tr td:last-child a:hover {
        text-decoration: underline;
    }
    .addColumnBox {
        display: flex;
        align-items: center;
    }
    .addColumnBox * {
        margin-right: 5px;
    }
</style>
<nav class="data-navbar">
    <ul>
        <a href="/browse?table={{ selected_table }}">
            <li>Browse</li>
        </a>
        <a href="/structure?table={{ selected_table }}" class="active">
            <li>Structure</li>
        </a>
        <a href="/insert?table={{ selected_table }}">
            <li>Insert</li>
        </a>
        <a href="/operations?table={{ selected_table }}">
            <li>Operations</li>
        </a>
    </ul>
</nav>
<div class="table-container">
    <table class="db-table">
        <thead>
            <tr>
                <th style="width: 20px;">#</th>
                <th style="width: 200px;">Name</th>
                <th style="width: 140px;">Type</th>
                <th style="width: 80px;">Null</th>
                <th style="width: 120px;">Default</th>
                <th style="width: 200px;">Index</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for i in data %}
            <tr>
                <td>{{ i[0]+1 }}</td>
                <td>{{ i[1] }}</td>
                <td>{{ i[2] }}</td>
                {% if i[3] == 0 %}
                <td>Yes</td>
                {% else %}
                <td>No</td>
                {% endif %}
                <td>{{ i[4] }}</td>
                {% if i[5] == 1 %}
                <td>Primary Key</td>
                {% else %}
                <td></td>
                {% endif %}
                <td><a href="/renamecolumn?table={{ selected_table }}&column={{ i[1] }}">Rename</a><a onclick="deleteColumn('{{ i[1] }}')">Drop</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
<form class="addColumnBox" id="addColumnForm">
    <a href="/addcolumn?table={{ selected_table }}" class="btn">Add a Column</a>
</form>
<script>
    document.getElementById("addColumnForm").addEventListener("submit", (e)=>{
        e.preventDefault();
        let columnsToAdd = document.getElementById("columnsToAdd").value;
        window.open(`/addcolumn?table={{ selected_table }}&col=${columnsToAdd}`, "_self").focus();
    })
function deleteColumn(columnName) {
    let randomNumber = Math.floor(Math.random() * (9999 - 1000)) + 1000;
    if (prompt(`Enter ${randomNumber} to delete the column`) == randomNumber) {
        const table = `{{ selected_table }}`;
        const sqlQuery = `ALTER TABLE \`${table}\` DROP \`${columnName}\``;
        const formData = new FormData();
        formData.append("query", sqlQuery);
        fetch("/~sql-executer", {
            method: "POST",
            body: formData
        }).then(response=>response.json()).then(data=>{
            if (data.status == "success") {
                showAlert(`${columnName} deleted successfully`, "green");
                setTimeout(() => {
                    location.reload();
                }, 5000);
            }
            else {
                showAlert("Error: Can't delete the column", "red");
            }
        }).catch(err=> {
            if (err) {
                showAlert("Error: Can't delete the column", "red");
            }
        })
    }
}
</script>
{% endblock %}''',

    "table": '''{% extends "viewlayout.sqliteExplorer" %}
{% block view %}
<style>
    .table-name-box {
        display: flex;
        align-items: center;
        margin-top: 5px;
    }

    .table-name-box p {
        margin-right: 10px;
    }

    .input {
        margin-right: 10px;
        box-shadow: none;
        outline: solid 2px transparent;
        transition: 0.2s;
    }

    .input:not([type=checkbox]):focus {
        outline: solid 2px rgb(226, 226, 226);
    }


    .input-full {
        width: 100%;
    }

    .input:focus {
        box-shadow: none;
        transform: none;
    }

    .table-container {
        margin-top: 12px;
    }

    select {
        width: 100%;
    }

    .save-button {
        margin-top: 15px;
        margin-bottom: 120px;
    }
</style>
<form id="data-form">
<div class="table-name-box">
    <p>Table Name: </p><input type="text" class="input" id="get_table_name">
    <p>Add: </p>
    <input type="number" class="input" min="1" id="columnsToAdd">
    <p>Column(s)</p>
    <button class="btn" id="columnAddButton">Go</button>
</div>

<div class="table-container">
    <table class="db-table">
        <thead>
            <tr>
                <th style="width: 160px;">Name</th>
                <th style="width: 120px;">Type</th>
                <th style="width: 160px;">Default</th>
                <th style="width: 40px;">Null</th>
                <th style="width: 140px;">Index</th>
                <th>AutoIncrement</th>
            </tr>
        </thead>
        <tbody id="rows">
            {% for i in range(4) %}
            <tr>
                <td><input type="text" class="input input-full get_column_name"></td>
                <td>
                    <select class="input input-full get_column_type">
                        <option
                            title="The value is a signed integer, stored in 0, 1, 2, 3, 4, 6, or 8 bytes depending on the magnitude of the value.">
                            INTEGER</option>
                        <option
                            title="The value is a text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE).">
                            TEXT</option>
                        <option title="The value is a blob of data, stored exactly as it was input.">BLOB</option>
                        <option
                            title="The value is a floating point value, stored as an 8-byte IEEE floating point number.">
                            REAL</option>
                    </select>
                </td>
                <td><input type="text" class="input input-full get_default" list="defaultList"></td>
                <td><input type="checkbox" class="input-full get_null"></td>
                <td>
                    <select class="input select-index get_index">
                        <option value="">---</option>
                        <option value="PRIMARY">PRIMARY</option>
                    </select>
                </td>
                <td><input type="checkbox" class="input autoincrement-input get_autoincrement"
                        data-autoincrementpointer="{{i}}"></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <button class="btn save-button" id="save-button">Save</button>
</div>
<datalist id="defaultList">
    <option value="NULL">
    </datalist>
</form>
<script>
    function _(elms) {
        return document.querySelectorAll(elms);
    }
    function _id(elm) {
        return document.getElementById(elm);
    }

    function check() {
        _(".autoincrement-input").forEach(element => {
            element.addEventListener("click", (e) => {
                let check = element.checked;
                if (check) {
                    let pointer = element.getAttribute("data-autoincrementpointer");
                    _(".select-index")[pointer].value = "PRIMARY";
                }
            })
        })
    }
    check();


    _id("save-button").addEventListener("click", (e) => {
        const formData = new FormData();
        let query = "";
        let primary_key = "";
        let looped = 0;
        _("#rows tr").forEach(element => {
            if (element.getElementsByClassName("get_column_name")[0].value != "" && _id("get_table_name").value != "") {
                let column_name = element.getElementsByClassName("get_column_name")[0].value;
                let column_type = element.getElementsByClassName("get_column_type")[0].value;
                let column_default = element.getElementsByClassName("get_default")[0].value;
                let column_null = element.getElementsByClassName("get_null")[0].checked;
                let column_index = element.getElementsByClassName("get_index")[0].value;
                let column_autoIncrement = element.getElementsByClassName("get_autoincrement")[0].checked;

                // Column Null
                if (column_null) {
                    column_null = "NULL";
                }
                else {
                    column_null = "NOT NULL";
                }
                // Column default
                if (column_default == "") {
                    column_default = "";
                }
                else if (column_default == "NULL") {
                    column_default = "DEFAULT NULL";
                }
                else {
                    if (column_type == "INTEGER") {
                        column_default = `DEFAULT ${parseInt(column_default)}`;
                    }
                    else {
                        column_default = `DEFAULT '${column_default}'`;
                    }
                }

                // Auto Increment
                if (column_autoIncrement) {
                    column_autoIncrement = "AUTOINCREMENT";
                }
                else {
                    column_autoIncrement = "";
                }
                // Primary Key
                if (column_index == "PRIMARY") {
                    primary_key = ` PRIMARY KEY`;
                }
                else {
                    primary_key = "";
                }

                let comma = ""
                if (looped != 0) {
                    comma = ","
                }
                query += `${comma} \`${column_name.replace(" ", "_").replace("-", "_")}\` ${column_type} ${column_null}${primary_key} ${column_autoIncrement} ${column_default}`;
                looped++;
            }
        })
        let tableName = _id("get_table_name").value.replace(" ", "_");
        let sqlQuery = `CREATE TABLE \`${tableName}\` (${query + primary_key})`;
        formData.append("sql", sqlQuery);
        fetch("/~create-table", {
            method: "POST",
            body: formData
        }).then(response => response.json()).then((data) => {
            if (data.status == "success") {
                showAlert("Table created successfully!", "green");
                refreshData();
                _id("dbTables").innerHTML += `<a href="/browse?table=${tableName}"><li>${tableName}</li></a>`;
                _id("data-form").reset();
            }
            else {
                showAlert("Error: Failed to create table", "red")
            }
        }).catch((err) => {
            if (err) {
                console.log(err);
                showAlert("Error: Failed to create table", "red")
            }
        })

    })

    _id("columnAddButton").addEventListener("click", (e) => {
        let columnsToAdd = _id("columnsToAdd").value;
        let i = _(".autoincrement-input").length;
        for (let j = 0; j < columnsToAdd; j++) {
            if (columnsToAdd >= 1) {
                let tr = document.createElement("tr");
                tr.innerHTML += `<td><input type="text" class="input input-full get_column_name"></td>
                <td>
                    <select class="input input-full get_column_type">
                        <option
                            title="The value is a signed integer, stored in 0, 1, 2, 3, 4, 6, or 8 bytes depending on the magnitude of the value.">
                            INTEGER</option>
                            <option
                                title="The value is a text string, stored using the database encoding (UTF-8, UTF-16BE or UTF-16LE).">
                                TEXT</option>
                            <option title="The value is a blob of data, stored exactly as it was input.">BLOB</option>
                        <option
                            title="The value is a floating point value, stored as an 8-byte IEEE floating point number.">REAL</option>
                    </select>
                </td>
                <td><input type="text" class="input input-full get_default"></td>
                <td><input type="checkbox" class="input-full get_null"></td>
                <td>
                    <select class="input select-index get_index">
                        <option value="">---</option>
                        <option value="PRIMARY">PRIMARY</option>
                    </select>
                </td>
                <td><input type="checkbox" class="input autoincrement-input get_autoincrement"
                        data-autoincrementpointer="${i + j}"></td>`;
                _id("rows").appendChild(tr);
            }
        }
        check();
        _id("columnsToAdd").value = "";

    })
    _id("data-form").addEventListener("submit", (e)=> {
        e.preventDefault();
    })



</script>
{% endblock %}''',

}

media = {
    "favicon.ico": "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",

    "fontface.css": "LyogY3lyaWxsaWMtZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDIwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMkpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzA0NjAtMDUyRiwgVSsxQzgwLTFDODgsIFUrMjBCNCwgVSsyREUwLTJERkYsIFUrQTY0MC1BNjlGLCBVK0ZFMkUtRkUyRjsNCn0NCi8qIGN5cmlsbGljICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDIwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMFpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAzMDEsIFUrMDQwMC0wNDVGLCBVKzA0OTAtMDQ5MSwgVSswNEIwLTA0QjEsIFUrMjExNjsNCn0NCi8qIGdyZWVrLWV4dCAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiAyMDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTJaTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSsxRjAwLTFGRkY7DQp9DQovKiBncmVlayAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiAyMDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTFwTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMzcwLTAzRkY7DQp9DQovKiB2aWV0bmFtZXNlICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDIwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMnBMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAxMDItMDEwMywgVSswMTEwLTAxMTEsIFUrMDEyOC0wMTI5LCBVKzAxNjgtMDE2OSwgVSswMUEwLTAxQTEsIFUrMDFBRi0wMUIwLCBVKzFFQTAtMUVGOSwgVSsyMEFCOw0KfQ0KLyogbGF0aW4tZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDIwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMjVMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAxMDAtMDI0RiwgVSswMjU5LCBVKzFFMDAtMUVGRiwgVSsyMDIwLCBVKzIwQTAtMjBBQiwgVSsyMEFELTIwQ0YsIFUrMjExMywgVSsyQzYwLTJDN0YsIFUrQTcyMC1BN0ZGOw0KfQ0KLyogbGF0aW4gKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogMjAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWExWkw3LndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDAwMC0wMEZGLCBVKzAxMzEsIFUrMDE1Mi0wMTUzLCBVKzAyQkItMDJCQywgVSswMkM2LCBVKzAyREEsIFUrMDJEQywgVSsyMDAwLTIwNkYsIFUrMjA3NCwgVSsyMEFDLCBVKzIxMjIsIFUrMjE5MSwgVSsyMTkzLCBVKzIyMTIsIFUrMjIxNSwgVStGRUZGLCBVK0ZGRkQ7DQp9DQovKiBjeXJpbGxpYy1leHQgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogMzAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEySkw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDQ2MC0wNTJGLCBVKzFDODAtMUM4OCwgVSsyMEI0LCBVKzJERTAtMkRGRiwgVStBNjQwLUE2OUYsIFUrRkUyRS1GRTJGOw0KfQ0KLyogY3lyaWxsaWMgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogMzAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEwWkw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDMwMSwgVSswNDAwLTA0NUYsIFUrMDQ5MC0wNDkxLCBVKzA0QjAtMDRCMSwgVSsyMTE2Ow0KfQ0KLyogZ3JlZWstZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDMwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMlpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzFGMDAtMUZGRjsNCn0NCi8qIGdyZWVrICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDMwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMXBMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAzNzAtMDNGRjsNCn0NCi8qIHZpZXRuYW1lc2UgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogMzAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEycEw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDEwMi0wMTAzLCBVKzAxMTAtMDExMSwgVSswMTI4LTAxMjksIFUrMDE2OC0wMTY5LCBVKzAxQTAtMDFBMSwgVSswMUFGLTAxQjAsIFUrMUVBMC0xRUY5LCBVKzIwQUI7DQp9DQovKiBsYXRpbi1leHQgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogMzAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEyNUw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDEwMC0wMjRGLCBVKzAyNTksIFUrMUUwMC0xRUZGLCBVKzIwMjAsIFUrMjBBMC0yMEFCLCBVKzIwQUQtMjBDRiwgVSsyMTEzLCBVKzJDNjAtMkM3RiwgVStBNzIwLUE3RkY7DQp9DQovKiBsYXRpbiAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiAzMDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTFaTDcud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMDAwLTAwRkYsIFUrMDEzMSwgVSswMTUyLTAxNTMsIFUrMDJCQi0wMkJDLCBVKzAyQzYsIFUrMDJEQSwgVSswMkRDLCBVKzIwMDAtMjA2RiwgVSsyMDc0LCBVKzIwQUMsIFUrMjEyMiwgVSsyMTkxLCBVKzIxOTMsIFUrMjIxMiwgVSsyMjE1LCBVK0ZFRkYsIFUrRkZGRDsNCn0NCi8qIGN5cmlsbGljLWV4dCAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA0MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTJKTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswNDYwLTA1MkYsIFUrMUM4MC0xQzg4LCBVKzIwQjQsIFUrMkRFMC0yREZGLCBVK0E2NDAtQTY5RiwgVStGRTJFLUZFMkY7DQp9DQovKiBjeXJpbGxpYyAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA0MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTBaTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMzAxLCBVKzA0MDAtMDQ1RiwgVSswNDkwLTA0OTEsIFUrMDRCMC0wNEIxLCBVKzIxMTY7DQp9DQovKiBncmVlay1leHQgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNDAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEyWkw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMUYwMC0xRkZGOw0KfQ0KLyogZ3JlZWsgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNDAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWExcEw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDM3MC0wM0ZGOw0KfQ0KLyogdmlldG5hbWVzZSAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA0MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTJwTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMTAyLTAxMDMsIFUrMDExMC0wMTExLCBVKzAxMjgtMDEyOSwgVSswMTY4LTAxNjksIFUrMDFBMC0wMUExLCBVKzAxQUYtMDFCMCwgVSsxRUEwLTFFRjksIFUrMjBBQjsNCn0NCi8qIGxhdGluLWV4dCAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA0MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTI1TDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMTAwLTAyNEYsIFUrMDI1OSwgVSsxRTAwLTFFRkYsIFUrMjAyMCwgVSsyMEEwLTIwQUIsIFUrMjBBRC0yMENGLCBVKzIxMTMsIFUrMkM2MC0yQzdGLCBVK0E3MjAtQTdGRjsNCn0NCi8qIGxhdGluICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDQwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMVpMNy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAwMDAtMDBGRiwgVSswMTMxLCBVKzAxNTItMDE1MywgVSswMkJCLTAyQkMsIFUrMDJDNiwgVSswMkRBLCBVKzAyREMsIFUrMjAwMC0yMDZGLCBVKzIwNzQsIFUrMjBBQywgVSsyMTIyLCBVKzIxOTEsIFUrMjE5MywgVSsyMjEyLCBVKzIyMTUsIFUrRkVGRiwgVStGRkZEOw0KfQ0KLyogY3lyaWxsaWMtZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDUwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMkpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzA0NjAtMDUyRiwgVSsxQzgwLTFDODgsIFUrMjBCNCwgVSsyREUwLTJERkYsIFUrQTY0MC1BNjlGLCBVK0ZFMkUtRkUyRjsNCn0NCi8qIGN5cmlsbGljICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDUwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMFpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAzMDEsIFUrMDQwMC0wNDVGLCBVKzA0OTAtMDQ5MSwgVSswNEIwLTA0QjEsIFUrMjExNjsNCn0NCi8qIGdyZWVrLWV4dCAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA1MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTJaTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSsxRjAwLTFGRkY7DQp9DQovKiBncmVlayAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA1MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTFwTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMzcwLTAzRkY7DQp9DQovKiB2aWV0bmFtZXNlICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDUwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMnBMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAxMDItMDEwMywgVSswMTEwLTAxMTEsIFUrMDEyOC0wMTI5LCBVKzAxNjgtMDE2OSwgVSswMUEwLTAxQTEsIFUrMDFBRi0wMUIwLCBVKzFFQTAtMUVGOSwgVSsyMEFCOw0KfQ0KLyogbGF0aW4tZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDUwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMjVMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAxMDAtMDI0RiwgVSswMjU5LCBVKzFFMDAtMUVGRiwgVSsyMDIwLCBVKzIwQTAtMjBBQiwgVSsyMEFELTIwQ0YsIFUrMjExMywgVSsyQzYwLTJDN0YsIFUrQTcyMC1BN0ZGOw0KfQ0KLyogbGF0aW4gKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNTAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWExWkw3LndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDAwMC0wMEZGLCBVKzAxMzEsIFUrMDE1Mi0wMTUzLCBVKzAyQkItMDJCQywgVSswMkM2LCBVKzAyREEsIFUrMDJEQywgVSsyMDAwLTIwNkYsIFUrMjA3NCwgVSsyMEFDLCBVKzIxMjIsIFUrMjE5MSwgVSsyMTkzLCBVKzIyMTIsIFUrMjIxNSwgVStGRUZGLCBVK0ZGRkQ7DQp9DQovKiBjeXJpbGxpYy1leHQgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNjAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEySkw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDQ2MC0wNTJGLCBVKzFDODAtMUM4OCwgVSsyMEI0LCBVKzJERTAtMkRGRiwgVStBNjQwLUE2OUYsIFUrRkUyRS1GRTJGOw0KfQ0KLyogY3lyaWxsaWMgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNjAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEwWkw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDMwMSwgVSswNDAwLTA0NUYsIFUrMDQ5MC0wNDkxLCBVKzA0QjAtMDRCMSwgVSsyMTE2Ow0KfQ0KLyogZ3JlZWstZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDYwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMlpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzFGMDAtMUZGRjsNCn0NCi8qIGdyZWVrICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDYwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMXBMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAzNzAtMDNGRjsNCn0NCi8qIHZpZXRuYW1lc2UgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNjAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEycEw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDEwMi0wMTAzLCBVKzAxMTAtMDExMSwgVSswMTI4LTAxMjksIFUrMDE2OC0wMTY5LCBVKzAxQTAtMDFBMSwgVSswMUFGLTAxQjAsIFUrMUVBMC0xRUY5LCBVKzIwQUI7DQp9DQovKiBsYXRpbi1leHQgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNjAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEyNUw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDEwMC0wMjRGLCBVKzAyNTksIFUrMUUwMC0xRUZGLCBVKzIwMjAsIFUrMjBBMC0yMEFCLCBVKzIwQUQtMjBDRiwgVSsyMTEzLCBVKzJDNjAtMkM3RiwgVStBNzIwLUE3RkY7DQp9DQovKiBsYXRpbiAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA2MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTFaTDcud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMDAwLTAwRkYsIFUrMDEzMSwgVSswMTUyLTAxNTMsIFUrMDJCQi0wMkJDLCBVKzAyQzYsIFUrMDJEQSwgVSswMkRDLCBVKzIwMDAtMjA2RiwgVSsyMDc0LCBVKzIwQUMsIFUrMjEyMiwgVSsyMTkxLCBVKzIxOTMsIFUrMjIxMiwgVSsyMjE1LCBVK0ZFRkYsIFUrRkZGRDsNCn0NCi8qIGN5cmlsbGljLWV4dCAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA3MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTJKTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswNDYwLTA1MkYsIFUrMUM4MC0xQzg4LCBVKzIwQjQsIFUrMkRFMC0yREZGLCBVK0E2NDAtQTY5RiwgVStGRTJFLUZFMkY7DQp9DQovKiBjeXJpbGxpYyAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA3MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTBaTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMzAxLCBVKzA0MDAtMDQ1RiwgVSswNDkwLTA0OTEsIFUrMDRCMC0wNEIxLCBVKzIxMTY7DQp9DQovKiBncmVlay1leHQgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNzAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWEyWkw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMUYwMC0xRkZGOw0KfQ0KLyogZ3JlZWsgKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogNzAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWExcEw3U1VjLndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDM3MC0wM0ZGOw0KfQ0KLyogdmlldG5hbWVzZSAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA3MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTJwTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMTAyLTAxMDMsIFUrMDExMC0wMTExLCBVKzAxMjgtMDEyOSwgVSswMTY4LTAxNjksIFUrMDFBMC0wMUExLCBVKzAxQUYtMDFCMCwgVSsxRUEwLTFFRjksIFUrMjBBQjsNCn0NCi8qIGxhdGluLWV4dCAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA3MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTI1TDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMTAwLTAyNEYsIFUrMDI1OSwgVSsxRTAwLTFFRkYsIFUrMjAyMCwgVSsyMEEwLTIwQUIsIFUrMjBBRC0yMENGLCBVKzIxMTMsIFUrMkM2MC0yQzdGLCBVK0E3MjAtQTdGRjsNCn0NCi8qIGxhdGluICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDcwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMVpMNy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAwMDAtMDBGRiwgVSswMTMxLCBVKzAxNTItMDE1MywgVSswMkJCLTAyQkMsIFUrMDJDNiwgVSswMkRBLCBVKzAyREMsIFUrMjAwMC0yMDZGLCBVKzIwNzQsIFUrMjBBQywgVSsyMTIyLCBVKzIxOTEsIFUrMjE5MywgVSsyMjEyLCBVKzIyMTUsIFUrRkVGRiwgVStGRkZEOw0KfQ0KLyogY3lyaWxsaWMtZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDgwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMkpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzA0NjAtMDUyRiwgVSsxQzgwLTFDODgsIFUrMjBCNCwgVSsyREUwLTJERkYsIFUrQTY0MC1BNjlGLCBVK0ZFMkUtRkUyRjsNCn0NCi8qIGN5cmlsbGljICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDgwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMFpMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAzMDEsIFUrMDQwMC0wNDVGLCBVKzA0OTAtMDQ5MSwgVSswNEIwLTA0QjEsIFUrMjExNjsNCn0NCi8qIGdyZWVrLWV4dCAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA4MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTJaTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSsxRjAwLTFGRkY7DQp9DQovKiBncmVlayAqLw0KQGZvbnQtZmFjZSB7DQogIGZvbnQtZmFtaWx5OiAnSW50ZXInOw0KICBmb250LXN0eWxlOiBub3JtYWw7DQogIGZvbnQtd2VpZ2h0OiA4MDA7DQogIGZvbnQtZGlzcGxheTogc3dhcDsNCiAgc3JjOiB1cmwoaHR0cHM6Ly9mb250cy5nc3RhdGljLmNvbS9zL2ludGVyL3YxMS9VY0M3M0Z3ckszaUxUZUh1U19mdlF0TXdDcDUwS25NYTFwTDdTVWMud29mZjIpIGZvcm1hdCgnd29mZjInKTsNCiAgdW5pY29kZS1yYW5nZTogVSswMzcwLTAzRkY7DQp9DQovKiB2aWV0bmFtZXNlICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDgwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMnBMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAxMDItMDEwMywgVSswMTEwLTAxMTEsIFUrMDEyOC0wMTI5LCBVKzAxNjgtMDE2OSwgVSswMUEwLTAxQTEsIFUrMDFBRi0wMUIwLCBVKzFFQTAtMUVGOSwgVSsyMEFCOw0KfQ0KLyogbGF0aW4tZXh0ICovDQpAZm9udC1mYWNlIHsNCiAgZm9udC1mYW1pbHk6ICdJbnRlcic7DQogIGZvbnQtc3R5bGU6IG5vcm1hbDsNCiAgZm9udC13ZWlnaHQ6IDgwMDsNCiAgZm9udC1kaXNwbGF5OiBzd2FwOw0KICBzcmM6IHVybChodHRwczovL2ZvbnRzLmdzdGF0aWMuY29tL3MvaW50ZXIvdjExL1VjQzczRndySzNpTFRlSHVTX2Z2UXRNd0NwNTBLbk1hMjVMN1NVYy53b2ZmMikgZm9ybWF0KCd3b2ZmMicpOw0KICB1bmljb2RlLXJhbmdlOiBVKzAxMDAtMDI0RiwgVSswMjU5LCBVKzFFMDAtMUVGRiwgVSsyMDIwLCBVKzIwQTAtMjBBQiwgVSsyMEFELTIwQ0YsIFUrMjExMywgVSsyQzYwLTJDN0YsIFUrQTcyMC1BN0ZGOw0KfQ0KLyogbGF0aW4gKi8NCkBmb250LWZhY2Ugew0KICBmb250LWZhbWlseTogJ0ludGVyJzsNCiAgZm9udC1zdHlsZTogbm9ybWFsOw0KICBmb250LXdlaWdodDogODAwOw0KICBmb250LWRpc3BsYXk6IHN3YXA7DQogIHNyYzogdXJsKGh0dHBzOi8vZm9udHMuZ3N0YXRpYy5jb20vcy9pbnRlci92MTEvVWNDNzNGd3JLM2lMVGVIdVNfZnZRdE13Q3A1MEtuTWExWkw3LndvZmYyKSBmb3JtYXQoJ3dvZmYyJyk7DQogIHVuaWNvZGUtcmFuZ2U6IFUrMDAwMC0wMEZGLCBVKzAxMzEsIFUrMDE1Mi0wMTUzLCBVKzAyQkItMDJCQywgVSswMkM2LCBVKzAyREEsIFUrMDJEQywgVSsyMDAwLTIwNkYsIFUrMjA3NCwgVSsyMEFDLCBVKzIxMjIsIFUrMjE5MSwgVSsyMTkzLCBVKzIyMTIsIFUrMjIxNSwgVStGRUZGLCBVK0ZGRkQ7DQp9",

    "style.css": "OnJvb3Qgew0KICAgIC0taGVhZGVyLWhlaWdodDogNzBweDsNCiAgICAtLWJvcmRlcjogc29saWQgMnB4ICNlZWU7DQp9DQoqIHsNCiAgICBtYXJnaW46IDA7DQogICAgcGFkZGluZzogMDsNCiAgICBib3gtc2l6aW5nOiBib3JkZXItYm94Ow0KICAgIGZvbnQtZmFtaWx5OiAnSW50ZXInLCBzYW5zLXNlcmlmOw0KfQ0KOjotd2Via2l0LXNjcm9sbGJhciB7DQogICAgd2lkdGg6IDEycHg7DQogICAgaGVpZ2h0OiAxMnB4Ow0KICAgIGJhY2tncm91bmQ6ICNmZmY7DQp9DQo6Oi13ZWJraXQtc2Nyb2xsYmFyLXRodW1iIHsNCiAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjZjJmMmYyOw0KICAgIGJvcmRlci1yYWRpdXM6IDEwcHg7DQp9DQpib2R5IHsNCiAgICBtaW4taGVpZ2h0OiAxMDB2aDsNCiAgICBiYWNrZ3JvdW5kOiBsaW5lYXItZ3JhZGllbnQodG8gYm90dG9tLCByZ2IoMjU1LCAxNTQsIDcyKSAwJSwgcmdiKDI1NSwgMTU0LCA3MikgNTAlLCB3aGl0ZSA1MCUsIHdoaXRlIDEwMCUpOw0KICAgIGJhY2tncm91bmQ6IGxpbmVhci1ncmFkaWVudCh0byBib3R0b20sICMwMDA3ODYgMCUsICMwMDA3ODYgNTAlLCB3aGl0ZSA1MCUsIHdoaXRlIDEwMCUpOw0KICAgIGRpc3BsYXk6IGZsZXg7DQogICAganVzdGlmeS1jb250ZW50OiBjZW50ZXI7DQogICAgYWxpZ24taXRlbXM6IGNlbnRlcjsNCn0NCi5jb250YWluZXIgew0KICAgIG1heC13aWR0aDogY2FsYygxMDB2dyAtIDUwcHgpOw0KICAgIHdpZHRoOiAxMDAlOw0KICAgIGhlaWdodDogY2FsYygxMDB2aCAtIDUwcHgpOw0KICAgIGJhY2tncm91bmQ6IHdoaXRlOw0KICAgIGJveC1zaGFkb3c6IDAgMTBweCAyMHB4IHJnYmEoNzAsIDcwLCA3MCwgMC4yNik7DQogICAgYm9yZGVyLXJhZGl1czogMnB4Ow0KICAgIHBvc2l0aW9uOiByZWxhdGl2ZTsNCiAgICBvdmVyZmxvdzogaGlkZGVuOw0KfQ0KLm5hdmJhciB7DQogICAgd2lkdGg6IDEwMCU7DQogICAgaGVpZ2h0OiA3MHB4Ow0KICAgIGJvcmRlci1ib3R0b206IHZhcigtLWJvcmRlcik7DQogICAgZGlzcGxheTogZmxleDsNCiAgICBhbGlnbi1pdGVtczogY2VudGVyOw0KICAgIGp1c3RpZnktY29udGVudDogc3BhY2UtYmV0d2VlbjsNCiAgICBwYWRkaW5nOiAyMHB4IDIwcHg7DQp9DQoubmF2YmFyIHVsIHsNCiAgICBkaXNwbGF5OiBmbGV4Ow0KDQp9DQoubG9nbyB7DQogICAgd2lkdGg6IDEwMHB4Ow0KICAgIHVzZXItc2VsZWN0OiBub25lOw0KfQ0KLnNxbEl0ZW1zIHsNCiAgICBkaXNwbGF5OiBmbGV4Ow0KICAgIGFsaWduLWl0ZW1zOiBjZW50ZXI7DQp9DQouZXhlY3V0ZVNxbCB7DQogICAgbWFyZ2luLXJpZ2h0OiAxMHB4Ow0KICAgIGNvbG9yOiAjMjQyZGNhOw0KICAgIHRleHQtZGVjb3JhdGlvbjogbm9uZTsNCiAgICBmb250LXdlaWdodDogNDAwOw0KfQ0KLm1haW4gew0KICAgIGhlaWdodDogMTAwJTsNCiAgICBkaXNwbGF5OiBmbGV4Ow0KfQ0KLnNpZGViYXIgew0KICAgIHdpZHRoOiAxMDAlOw0KICAgIGhlaWdodDogY2FsYygxMDAlIC0gNzBweCk7DQogICAgYmFja2dyb3VuZDogI2ZmZjsNCiAgICBib3JkZXItcmlnaHQ6IHZhcigtLWJvcmRlcik7DQogICAgb3ZlcmZsb3c6IGF1dG87DQogICAgZmxleDogMTUlOw0KICAgIG1heC13aWR0aDogMTUlOw0KfQ0KLmRhdGEgew0KICAgIGZsZXg6IDg1JTsNCiAgICBtYXgtd2lkdGg6IDg1JTsNCiAgICBvdmVyZmxvdzogYXV0bzsNCiAgICBwYWRkaW5nOiA0cHg7DQp9DQouZGItbmFtZSB7DQogICAgZm9udC13ZWlnaHQ6IGJvbGQ7DQogICAgbWFyZ2luLXJpZ2h0OiAxMHB4Ow0KICAgIHRleHQtdHJhbnNmb3JtOiB1cHBlcmNhc2U7DQogICAgYmFja2dyb3VuZDogI2U4ZThlODsNCiAgICBwYWRkaW5nOiA4cHg7DQogICAgYm9yZGVyLXJhZGl1czogNXB4Ow0KICAgIGZvbnQtc2l6ZTogMTRweDsNCn0NCi5kYi10YWJsZXMgew0KICAgIGRpc3BsYXk6IGZsZXg7DQogICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjsNCn0NCi5kYi10YWJsZXMgYSB7DQogICAgZGlzcGxheTogZmxleDsNCiAgICBhbGlnbi1pdGVtczogY2VudGVyOw0KfQ0KLmRiLXRhYmxlcyBhIGxpIHsNCiAgICBsaXN0LXN0eWxlOiBub25lOw0KICAgIGxpbmUtaGVpZ2h0OiAyNXB4Ow0KICAgIGNvbG9yOiAjMDAwOw0KICAgIHRleHQtZGVjb3JhdGlvbjogbm9uZTsNCiAgICB3aWR0aDogMTAwJTsNCiAgICBwYWRkaW5nOiA2cHg7DQogICAgcGFkZGluZy1sZWZ0OiAxMnB4Ow0KICAgIHRyYW5zaXRpb246IDAuMnM7DQp9DQouZGItdGFibGVzIGEgbGk6aG92ZXIgew0KICAgIGJhY2tncm91bmQtY29sb3I6ICNkZGRlZmY7IA0KfQ0KLmRiLXRhYmxlcyBhIC5hY3RpdmUgew0KICAgIGJhY2tncm91bmQtY29sb3I6ICNlYmVjZmY7DQp9DQouZGItdGFibGVzIGEgew0KICAgIHRleHQtZGVjb3JhdGlvbjogbm9uZTsNCn0NCi5kYi1jcmVhdGUtdGFibGUgew0KICAgIGRpc3BsYXk6IGJsb2NrOw0KICAgIG1hcmdpbjogYXV0bzsNCiAgICB0ZXh0LWFsaWduOiBjZW50ZXI7DQogICAgdGV4dC1kZWNvcmF0aW9uOiBub25lOw0KICAgIHBhZGRpbmc6IDhweDsNCiAgICBiYWNrZ3JvdW5kOiAjMjQyZGNhOw0KICAgIGNvbG9yOiAjZmZmOw0KICAgIHdpZHRoOiAxMDBweDsNCiAgICBoZWlnaHQ6IDM1cHg7DQogICAgZm9udC1zaXplOiAxNHB4Ow0KICAgIG1hcmdpbi10b3A6IDEwcHg7DQogICAgbWFyZ2luLWJvdHRvbTogMTVweDsNCiAgICBib3JkZXItcmFkaXVzOiA1cHg7DQogICAgb3V0bGluZTogbm9uZTsNCiAgICBib3gtc2hhZG93OiAwIDRweCAjNmU3NGRkOw0KICAgIC8qIHRyYW5zaXRpb246IDAuMDVzOyAqLw0KfQ0KLmRiLWNyZWF0ZS10YWJsZTphY3RpdmUsIC5kYi1jcmVhdGUtdGFibGU6Zm9jdXMgew0KICAgIHRyYW5zZm9ybTogdHJhbnNsYXRlWSgycHgpOw0KICAgIGJveC1zaGFkb3c6IDAgMnB4ICM2ZTc0ZGQ7DQp9DQoudGFibGUtY29udGFpbmVyIHsNCiAgICBvdmVyZmxvdy14OiBhdXRvOw0KICAgIG1heC1oZWlnaHQ6IGNhbGMoMTAwJSAtIDE2MHB4KTsNCiAgICBtaW4taGVpZ2h0OiBjYWxjKDEwMCUgLSAxNjBweCk7DQp9DQouZGItdGFibGUgew0KICAgIG1heC13aWR0aDogMTAwJTsNCiAgICBib3JkZXItY29sbGFwc2U6IGNvbGxhcHNlOw0KICAgIHdpZHRoOiAxMDAlOw0KICAgIA0KfQ0KLmRiLXRhYmxlIHRoZWFkIHsNCiAgICBiYWNrZ3JvdW5kOiAjMjQyZGNhOw0KICAgIGhlaWdodDogNDBweDsNCiAgICB0ZXh0LWFsaWduOiBsZWZ0Ow0KICAgIGNvbG9yOiAjZmZmOw0KICAgIGJvcmRlcjogc29saWQgMXB4ICMyNDJkY2E7DQp9DQouZGItdGFibGUgdGJvZHkgdHIgew0KICAgIGhlaWdodDogMzVweDsNCn0NCi5kYi10YWJsZSB0aCwgLmRiLXRhYmxlIHRkIHsNCiAgICBwYWRkaW5nOiAxMHB4Ow0KfQ0KLmRiLXRhYmxlIHRib2R5IHRyOm50aC1jaGlsZChldmVuKSB7DQogICAgYmFja2dyb3VuZC1jb2xvcjogI2Y4ZjhmODsNCn0NCg0KLmNvbnRyb2xscyB7DQogICAgZGlzcGxheTogZmxleDsNCiAgICBqdXN0aWZ5LWNvbnRlbnQ6IHNwYWNlLWJldHdlZW47DQogICAgYWxpZ24taXRlbXM6IGNlbnRlcjsNCiAgICBwYWRkaW5nOiA0cHg7DQp9DQouaW5wdXQgew0KICAgIG91dGxpbmU6IG5vbmU7DQogICAgYm9yZGVyOiBzb2xpZCAxcHggI2VlZTsNCiAgICBib3gtc2hhZG93OiAwIDRweCAjZWVlOw0KICAgIHBhZGRpbmc6IDZweDsNCiAgICBib3JkZXItcmFkaXVzOiA0cHg7DQogICAgYmFja2dyb3VuZDogI2ZmZjsNCn0NCi5pbnB1dDpmb2N1cyB7DQogICAgdHJhbnNmb3JtOiB0cmFuc2xhdGVZKDJweCk7DQogICAgYm94LXNoYWRvdzogMCAycHggI2VlZTsNCn0NCi5idG4gew0KICAgIHBhZGRpbmc6IDZweCAxMHB4Ow0KICAgIGJvcmRlcjogbm9uZTsNCiAgICBiYWNrZ3JvdW5kOiAjMjQyZGNhOw0KICAgIGJvcmRlci1yYWRpdXM6IDRweDsNCiAgICBjdXJzb3I6IHBvaW50ZXI7DQogICAgY29sb3I6IHdoaXRlOw0KICAgIGZvbnQtc2l6ZTogMTRweDsNCiAgICB0ZXh0LWRlY29yYXRpb246IG5vbmU7DQogICAgZGlzcGxheTogaW5saW5lLWJsb2NrOw0KICAgIG91dGxpbmU6IG5vbmU7DQogICAgdXNlci1zZWxlY3Q6IG5vbmU7DQogICAgYm94LXNoYWRvdzogMCA0cHggIzY0NmFkODsNCn0NCi5idG5Hcm91cCB7DQogICAgZGlzcGxheTogZmxleDsNCiAgICBqdXN0aWZ5LWNvbnRlbnQ6IHNwYWNlLWJldHdlZW47DQogICAgYWxpZ24taXRlbXM6IGNlbnRlcjsNCiAgICBib3JkZXItcmFkaXVzOiA1cHg7DQp9DQouYnRuR3JvdXAgLmJ0biB7DQogICAgYm9yZGVyLXJhZGl1czogMDsNCn0NCi5idG4taGlkZGVuIHsNCiAgICBkaXNwbGF5OiBub25lOw0KfQ0KLmJ0bi1hY3RpdmUgew0KICAgIHRyYW5zZm9ybTogdHJhbnNsYXRlWSgycHgpOw0KICAgIGJveC1zaGFkb3c6IDAgMnB4ICM2NDZhZDg7DQogICAgY3Vyc29yOiBkZWZhdWx0Ow0KfQ0KLmJ0bi1zaW5nbGUgew0KICAgIGJvcmRlci1yYWRpdXM6IDVweCA1cHggNXB4IDVweCAhaW1wb3J0YW50Ow0KfQ0KLmJ0bi1sZWZ0IHsNCiAgICBib3JkZXItcmFkaXVzOiA1cHggMHB4IDBweCA1cHggIWltcG9ydGFudDsNCn0NCi5idG4tcmlnaHQgew0KICAgIGJvcmRlci1yYWRpdXM6IDBweCA1cHggNXB4IDBweCAhaW1wb3J0YW50Ow0KfQ0KLmJ0bi1kaXNhYmxlZCB7DQogICAgY3Vyc29yOiBkZWZhdWx0Ow0KICAgIHRyYW5zZm9ybTogdHJhbnNsYXRlWSgycHgpOw0KICAgIGJveC1zaGFkb3c6IDAgMnB4ICM2NDZhZDg7DQogICAgb3BhY2l0eTogMC44Ow0KfQ0KLmJ0bjphY3RpdmUsIC5idG46Zm9jdXMgew0KICAgIHRyYW5zZm9ybTogdHJhbnNsYXRlWSgycHgpOw0KICAgIGJveC1zaGFkb3c6IDAgMnB4ICM2NDZhZDg7DQp9DQouZGF0YS1uYXZiYXIgew0KICAgIHdpZHRoOiAxMDAlOw0KICAgIGhlaWdodDogNDBweDsNCiAgICBiYWNrZ3JvdW5kOiAjZjhmOGY4Ow0KICAgIG1hcmdpbi1ib3R0b206IDVweDsNCiAgICBib3JkZXItcmFkaXVzOiAycHg7DQogICAgb3ZlcmZsb3c6IGhpZGRlbjsNCn0NCi5kYXRhLW5hdmJhciB1bCB7DQogICAgZGlzcGxheTogZmxleDsNCiAgICBhbGlnbi1pdGVtczogY2VudGVyOw0KICAgIGhlaWdodDogMTAwJTsNCn0NCi5kYXRhLW5hdmJhciB1bCBsaSB7DQogICAgbGlzdC1zdHlsZTogbm9uZTsNCiAgICBsaW5lLWhlaWdodDogNDBweDsNCiAgICBwYWRkaW5nLWxlZnQ6IDEwcHg7DQogICAgcGFkZGluZy1yaWdodDogMTBweDsNCn0NCi5kYXRhLW5hdmJhciB1bCBhIHsNCiAgICB0ZXh0LWRlY29yYXRpb246IG5vbmU7DQogICAgY29sb3I6ICMwMDA7DQp9DQouZGF0YS1uYXZiYXIgdWwgLmFjdGl2ZSB7DQogICAgYmFja2dyb3VuZDogI2ZmZjsNCiAgICBib3gtc2hhZG93OiAwIDNweCByZ2IoMjA2LCAyMDYsIDIwNikgaW5zZXQ7DQp9DQouYWxlcnRib3ggew0KICAgIHBvc2l0aW9uOiBmaXhlZDsNCiAgICBib3R0b206IDYlOw0KICAgIGxlZnQ6IDQlOw0KICAgIHBhZGRpbmc6IDE1cHg7DQogICAgei1pbmRleDogMTA7DQogICAgYm9yZGVyLXJhZGl1czogMnB4Ow0KICAgIGNvbG9yOiAjZmZmOw0KICAgIGRpc3BsYXk6IGZsZXg7DQogICAganVzdGlmeS1jb250ZW50OiBzcGFjZS1iZXR3ZWVuOw0KICAgIGJveC1zaGFkb3c6IDAgMCAxMHB4IHJnYmEoNzAsIDcwLCA3MCwgMC4xMik7DQogICAgYW5pbWF0aW9uOiBhbGVydGJveHBsYXkgMC40czsNCn0NCi5hbGVydC1ncmVlbiB7DQogICAgYmFja2dyb3VuZDogZ3JlZW47DQp9DQouYWxlcnQtcmVkIHsNCiAgICBiYWNrZ3JvdW5kOiByZ2IoMjU1LCAwLCAzNCk7DQp9DQpAa2V5ZnJhbWVzIGFsZXJ0Ym94cGxheSB7DQogICAgMCUgew0KICAgICAgICBib3R0b206IC0yMCU7DQogICAgfQ0KICAgIDkwJSB7DQogICAgICAgIGJvdHRvbTogNyU7DQogICAgfQ0KICAgIDEwMCUgew0KICAgICAgICBib3R0b206IDYlOw0KICAgIH0NCn0NCi5hbGVydHRleHQgew0KICAgIG1hcmdpbi1yaWdodDogMjBweDsNCiAgICBtYXgtd2lkdGg6IDM1MHB4Ow0KfQ0KLmFsZXJ0Y2xvc2Ugew0KICAgIGRpc3BsYXk6IGJsb2NrOw0KICAgIGZvbnQtd2VpZ2h0OiBib2xkOw0KICAgIHVzZXItc2VsZWN0OiBub25lOw0KICAgIGN1cnNvcjogcG9pbnRlcjsNCn0=",

    "main.js": "ZnVuY3Rpb24gc2hvd0FsZXJ0KG1lc3NhZ2UsIGNvbG9yKSB7DQogICAgbGV0IGVsZW0gPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJkaXYiKTsNCiAgICBlbGVtLnNldEF0dHJpYnV0ZSgiY2xhc3MiLCAiYWxlcnRib3giKTsNCiAgICBlbGVtLmNsYXNzTGlzdC5hZGQoYGFsZXJ0LSR7Y29sb3J9YCk7DQogICAgZWxlbS5pbm5lckhUTUwgPSBgDQogICAgPHAgY2xhc3M9ImFsZXJ0dGV4dCI+JHttZXNzYWdlfTwvcD4NCiAgICA8c3BhbiBjbGFzcz0iYWxlcnRjbG9zZSIgb25jbGljaz0iZG9jdW1lbnQuYm9keS5yZW1vdmVDaGlsZCh0aGlzLnBhcmVudE5vZGUpIj4mdGltZXM7PC9zcGFuPg0KICAgIGA7DQogICAgd2luZG93LmFsZXJ0Qm94ID0gZWxlbTsNCiAgICBkb2N1bWVudC5ib2R5LmFwcGVuZENoaWxkKGVsZW0pOw0KICAgIHNldFRpbWVvdXQoKCkgPT4gew0KICAgICAgICBkb2N1bWVudC5ib2R5LnJlbW92ZUNoaWxkKGVsZW0pOw0KICAgIH0sIDQwMDApOw0KfQ0KDQpmdW5jdGlvbiBjb3B5VGV4dChidXR0b24sIHNlbGVjdG9yKSB7DQogICAgYnV0dG9uLmlubmVySFRNTCA9ICJDb3BpZWQhIjsNCiAgICBsZXQgdmFsdWUgPSBkb2N1bWVudC5xdWVyeVNlbGVjdG9yKHNlbGVjdG9yKS52YWx1ZTsNCiAgICBsZXQgdGV4dGFyZWEgPSBkb2N1bWVudC5jcmVhdGVFbGVtZW50KCJ0ZXh0YXJlYSIpOw0KICAgIHRleHRhcmVhLmlubmVySFRNTCA9IHZhbHVlOw0KICAgIGRvY3VtZW50LmJvZHkuYXBwZW5kQ2hpbGQodGV4dGFyZWEpOw0KICAgIHRleHRhcmVhLnNlbGVjdCgpOw0KICAgIGRvY3VtZW50LmV4ZWNDb21tYW5kKCJjb3B5Iik7DQogICAgZG9jdW1lbnQuYm9keS5yZW1vdmVDaGlsZCh0ZXh0YXJlYSk7DQogICAgc2V0VGltZW91dCgoKSA9PiB7DQogICAgICAgIGJ1dHRvbi5pbm5lckhUTUwgPSAiQ29weSINCiAgICB9LCAyMDAwKTsNCn0NCmZ1bmN0aW9uIGNsZWFyVGV4dChzZWxlY3Rvcikgew0KICAgIGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3Ioc2VsZWN0b3IpLnZhbHVlID0gIiI7DQp9DQoNCmZ1bmN0aW9uIHBhcnNlVGV4dChzdHJpbmcpIHsNCiAgICByZXR1cm4gc3RyaW5nLnJlcGxhY2VBbGwoIiciLCAiJmFwb3M7Iik7DQp9DQpmdW5jdGlvbiByZWZyZXNoRGF0YSgpIHsNCiAgICBmZXRjaCgiL35yZWZyZXNoIik7DQp9",
    
    "logo.jpg": "/9j/4AAQSkZJRgABAQEAYABgAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAIQAABtbnRyUkdCIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAABjAAAABRyVFJDAAABoAAAAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhZWiAAAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3BhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAAAAAAAA9tYAAQAAAADTLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAwADEANv/bAEMAAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAf/bAEMBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAf/AABEIAm4D9wMBIgACEQEDEQH/xAAfAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgv/xAC1EAACAQMDAgQDBQUEBAAAAX0BAgMABBEFEiExQQYTUWEHInEUMoGRoQgjQrHBFVLR8CQzYnKCCQoWFxgZGiUmJygpKjQ1Njc4OTpDREVGR0hJSlNUVVZXWFlaY2RlZmdoaWpzdHV2d3h5eoOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4eLj5OXm5+jp6vHy8/T19vf4+fr/xAAfAQADAQEBAQEBAQEBAAAAAAAAAQIDBAUGBwgJCgv/xAC1EQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/AP7+KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACigZxz174ORn64GfrgfSigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigA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6bPPrHiC7S51zWhbSXNh4U8MQXNtBqniPUzHtAtbAXcBMYcPNJKkaZOa+Z/B3hHxF488T6D4O8KaVd614j8S6rZaLomlWMMlxd32pajcJa2tvDDErSM8kzouApCglmIVWav9Dn9mX4L/AAe/4N1P+CZmsftC/GBNF1D9rT4taFYvf288cM+qjxVrFtLdaP4E0uN4lvE03wpHPHa69c2TG3uL62+2yHYYmH5X4mccS4bwVDKsrjHFcRZzNYTLcJBtz9pUsnWnypyhSopudSdvdUdFdq/o5fgvrM5VKt4YalHmq1NkrNaJtq7e1u/R9Pnj/gqT+1h8IP8AgiZ+xp4W/wCCdX7Fk9rp/wAc/Heij/hP/GdhJG+t6Dpd1p72+qa/qOown7S2u6heiC30+1uijQWlw8yHEe1vg/8A4Nu/+COF5+1R8R7P9s39obw/LdfBjwFryXXgXR9aR5V+IPiaFBcnVLpJpFe60W0lnjdLjLM99A7bi201+Yn7Ef7M3x3/AOC4P/BRDV73x9q2tarp/iHxKvj341+MXaSaHwx4KuNTYW3h2yugY/st1cWEU+j+HiVGV095XBdGc/6tvwU+DfgL4B/DPwn8Kfhrodl4d8IeD9JtNJ0rTbGFIIo4bWJIxIyxAKZZdgeZud7k5OMCv5m4+4hh4ecOy4dwOKeI4u4gg8Vn+Z3/AH1L26Tqe8neDs3SoQTShGOl4ws/oMBS+v11WnBxwuHajQp/Zbjbl2tdd3q2/K9vS7GxtNMs7WwsIIrWys4Ira2toEEcUMECCOKKNF+VEjRVRVUAKqhRwAKtYPryOhx+fGcc0tFfyq25SlKTcpSbcpSbbk27ttu7bbu23u23u2fTWSVunb9PTyCiiikMKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigBCcZJ6Cvzj/wCCp37dHhD/AIJ//sefE34169qFtH4n/sifw/8AD3SGnEd3q3i/WYpLTSxBGrrP5dlI32qaeNJI4WjiWYKkoYforcXMNpbz3VzLFBb28Mk8080iRwxRRRmSSSSRyqRxoilnd2VVUFiQMmv8vL/g5T/4KVz/ALZP7VTfBPwHrktz8Gf2f7/U9Hs47W4b7DrnjBpTbapqssUdxJG72wgNshy0bJ5MkRDqxH6b4T8D1uOOK8Jg3CTy/B1KeKzCdm4ulCcZRoy0teq4uNusFK255uZ4xYPCzmn+8mnGnFvVt7yXX3U7rp07H89nxe+KPiv40/Evxn8UfG+pXWreJ/G3iDU/EGrXt1I8kr3WoXMs5VS5fEcSukaquF+ViACxz5vn/P8An60d8nk+p9+f8+vfNFf6hYLCUcBhaGEw8I06WHpU6UIwXKkoRSVkrdup+dylKUnKTbk3dvzfXy2FUlTng89CPp09+OvPpiv9JP8A4Ndf+CocH7Q/wDf9jj4seI43+LfwPs4k8CXmq6kkl/4w+HJGLSzgilijlmu/CYCWbsJ7qSTTHt5JGja2k3/5tdfT37Hn7UvxE/Y2/aE+Hfx++GWp3Wna94J1yzvbmC2k8tdY0b7RG2raLcjIjkttQtBJCyyAgMQ2cjI/M/FvgKjx1wvisHGCWYYaLxOBqpXlGtBXik7Xakk4Sit4u2i1O7K8a8DiVUf8OVoT3+F2b8rrfr8rH9gv/B2v+zbqHw6+Lv7NX7cPhKwFrHNfxeCfFWp2iETJrugzw6z4aubl0RxGZ7OK7tIJJAMtbBVEjMqp/H5+19aWE3xt8ReLtGRRofxIttI+I2mSR+Y6PH4u0631e8USSbldo9RublJPKcxJICkbuixyP/pP/tQ+KPgn/wAFyP8Agjn8RdZ+EupaNr3ix/A6+MtP0dJbW71nwN8UPBVsNZl0e4tIp57iy1Am1vtMQCRHuba9McrSwyzW8n+Zr8S72+vvCHg7StbE6eIvh9ca14E1KK4iaOa3tbO8kn023lDhZA9vi6tirorhYxkPIXNfBeAWa4qeTz4fzKM6ObcOYmpl2JoVbqboc0XRlZvmcOSyjK3K1FuLtod+d04Or7eFnSxEI1IuNrcyjG+q0u9X0fU8Kooor+kjwAooooAKKKKACiiigAooooAKcqs7BVBJPAABJJ9ABknqMdyeMdCWEjOM5Pp3xxyR+P8AnIz+yH/BFX/gml4p/wCCjX7Wvhjwrd2M9v8AB3wDJB4w+LPiFoZPskWhaddW/laLC7wPDNea1eSQacIY5BNCs5umHkwu1eDxNxBgeGcmx2cY+rClRwlGc/fdk5xV4wV3q3oktW72SZrh6M8RVhRgm5Tlb0u0ruz0SV3e3q0fvx/wbP8A/BKvQfCugXP/AAU5/ak0Wy0zwz4c0rxBcfBTTvFUCQ2trDY+fpms/Em6t723VEito4NX0rSmnyDK41G3cGO3kH4tf8Frf+Ci3jL/AIKf/tmDwd8MotW1f4W+EfGUfw7+CXg6yDNN4i1u+1CLw5Z30FjhUbV9d1Gb7DbPHIYrgXURXCFcf0Q/8HKP/BSDwn+yx8EvBX/BNL9mS5t/Dmp3HhTTrDxzH4dkWGPwh4B0zT10rRPCm+CPy11C/hButTglCyzxNa3L75Hmz8Q/8Grv/BLtfi/8XZf27Pi34cW7+H3wlmvLL4R2epQ5tdb+Irg2D+Ioo3Zory28KW0moGEsgktPEH9m3cTCS23D+UsszWpSwmd+MnF0JRrV6dShwxl9R3VHDycY4f2cJNJVcRLllKVldNXcYqz+lrU4t0MnwjTiuWWKnH7Ula75k22oq6Stunvof1Tf8EQP+CZXhz/gnF+yV4f8O6np1jcfGv4ix2vi74t+JFiP2m41q6tovs2i200u6aLSdGtwsVvZlikV1JdzKC07M37RkgcZAPsO/rj3/wA9DSIAqqiKAigKvQYAGAAMdulPr+SM8znG8QZrjc2x9R1MTja0qs7ttQi37tOCe0IQtGK8ru7bv9RQoQw9KFKnpGEVFK972tdvTd2+7a1woooryTYKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoppPRjxjOR19u359K5nxt4w0D4f+EfEnjbxTqNvpHhzwrouo69rWpXUscUNpp2mWst3cys0rohYRRMETeGkkKomWYCqhCVScKcIuc6k4whGKbcpyajGKS1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Uia54whl0hbuNt2Q1hZzXd3GTFPC11FawXULW08hH6wAEdTn8MV/DD/weH/tSmHRPgB+ylo+pmIXd1qXxJ8W2EVwqtdC3C6foi3ECy58m0P2lopApDyX0kcyYWMn73wxyCfEnG+Q5coSlSjjaeKxFlzKNHDTjVbluuSU1CDT35rHDmVdYbBV6l9eRwj3bl7t1fXRNvvp3P4N7y5nvLu5u7lzJcXM0txM+B88szmSRsDAG52JwOB0AwAK/p9/4NQfgmfiN/wUUvfH1xbCbTvhN8OtU1aSURI/kahrU62ViXkbzPKVmgZgvlr57LiOeKaBQ/8ALz/n8T79sc+w6g4Ff38f8Gb/AMG/sXw7/ae+N1zbbX1fX/DfgrTbgRAB4rO3ur6+DTlgW2yRQKsUe+Is0jSrFPChf+8vG/M1kfhrmsabUJV8NTwFNRfLb2/s6Kt3tfVK7dtLXSPismh7XMKN7uzc27X216n9u4GPc8ZPril5yefoPSiiv80D9DCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigCN2KLI+NwVCwAIBO0Ekc8DPqfyr/JB/4OBf2gdY+P3/BTr9oG61GW4Nj8PNd/4VxotrKZPKtrDw0otmNvGxC7JnUSGYRRSzDaLhTJHuP+t7NgxyDjmNx2HVTjOT356gjua/x1/wDgtFodx4f/AOCoH7ZVhcRvG5+MOsXgEigM0d7bWc8bD5nby2SRGjZpZd0ewxMtuYkT+mfov4fD1OMMyrVIRdehl8PYNvVKpVfteVXV7uML6Xb9Un87xI5fVKSXwuprp1SVv19fU/MO3haZnIHEaF2OCQB7jHfoBg5OQOhFf6qX/Bsf8Gz8K/8Aglh8Ktcnthb33xV8QeK/Hk7CIRxy2s+of2NYzBxFD9qdodH/AHtyRvL5tHLGxEkn+XBouiTSeGNb1sx/LHe6Xo9uXZY0lur+cuId0hVBmKOVnkkKxRop3OGCA/7KH/BNP4br8I/2C/2Tvh4IjFL4e+B3w+tr1PJ+zA6lN4b0+61Jlt2Jktomvri4aGCaSa4hg8uG5mnuEkmf9M+lLm0ocP5RllOppiMx5qsOso0qcpq6926U1F32T7Wuefw1SbrVajXw07KXXVxT8v5r+W2p9zUUUV/DR9kFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFADDllYEEcEEEZBBBBHbOfwr/K6/4Of/g+Phj/AMFUvibrlvaNbad8VPCvgzxxAyCQxteS6NbaTqRDOxhLPe6ZNc7Y4LUKJwrpcyB7+8/1SBnuMe3Wv89L/g8b+Hiab+0H+zN8R47QIPE/gHxD4fnuwMedNoGsLcrGd7FndI9Rib90vlxjDOqSSpJP+6/R5zF4DxCw9Nz5YYzBYihZ3tKUZU6kdF1SjPo9L6q54mfU/aYGX/TucJeT1tvt/wADa9z+bX4GfDCTxHof7M2itFIZvi9+03pWklIY/Oln0nQLrw/ZtK7bJIYoWudZvI4oZX2NNZXF1qVulpZWU1x/si/D3RIvDfgXwhoFvEsEOjeG9G02KJCWCJaafbwKoLSzE7QgHM0o4wHYAGv8s/8AYZ+Fb6x+1B/wR7+HEtrG41jVbv4mXcTk+VNca1421jUFvHgAmnu5I7DTdNL3KeXcslvHZWsE2mWNhLdf6rluoSCFFAUJEiKAOFCKFAwAowABwMAdBxzX0/0lsz+tZvkuEUrqnRxdZxvs3KnCLs7rVc1r39bNHNw9BKlVe2sEtN7xUm1vo3v62erJqKKK/mM+kCiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigBCMjFfxm/8Hjnwum1r9mj9mr4pW1uz/wDCGfFbWdDvrhBJ+7tPE/hyZo0lEasHBudJjEZkG1WZkSe3aXyL7+zOv56P+DnH4Ut8Sv8Agld8VNRgtHurn4b+IfC3juJUWaRoY9PvJdPup0jizl1ttUlUM+DtZ0QkuYZv0Dwsx6y3j7hrESlyxlj4UJ2trHERlStrbTmnG/kcOZQ9pgcRH+5f/wABkm/wTP4xv+De3XvG3xy/4Ktfsn2PjLWLjWrP4U+FNf0/w4JobaIaP4Z8L6DfXOmaYsqCFFt7V1WG3Miy3RQx2dpLHO1ps/1ThhVBLZAHXHv+gHSv8u3/AINT9Fl1L/gqjomoLErp4f8Ag78RdRMvl72gluo9K0gSrmNlh8yHUZ7aSYSM4ine2MLpcyT23+op2wK/QfpH1IT46o06aSp08qw7Sj/NOpUk3bbVKLv167HBw+v9icm226jvf/BD8tvIKKKK/n490KKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACvif8A4KMfB7/hfH7Ef7S3wsjt1ubrxR8JfGVrp8TIJc6gmi3c9jhCkuW+1wxFQIZyTgLBcZNvJ9sVVvrODULK7sLlFkt722ntJ42G5XhuImikVl4BBRiCOhHFduW4yeXZhgcfT+PB4vD4mPm6NWNS2ndRa+ZFSHtKc4PVTi196t+ev4H+aL/wa5eGtT+G/wDwVh8UeCPElvJba7o/wy8daBeW0kSBor2yv9NedWEjMIpEa1ZRtBuFbdFDPte4huf9MSv5jfhP/wAEovib+z//AMF3dV/a3+Hmkafbfs5/ET4Y+I9X1m8sjtfQvGF7ZRadqWj3EEsK/ZY9WvxFf2AsLiWJ0llt54LW3j3D+m/BwACQOckYz7HnPU/zr9C8VuIsFxPnuAzbB1VUVbJ8HGsk3L2daKkpQl/LJN6p6rS55+V0JYahOlJNNVZbrdJK3ZdfuH0UUV+YHphRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUW/r7v8gEAwf/AK3uT/X0560HkcHHvS0UAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFABRRRQAUUUUAFFFFAH/2Q=="
}


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

# database = "jokerquotes.db"
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

def parseString(string):
    parsedString = string.replace("'", "&apos;").replace( "\\", "&bsol;")
    return parsedString

def decodeFile(string, type):
    returnData = app.response_class(
        response=b64decode(string),
        status=200,
        mimetype=type
    )
    return returnData

def createButtons(data):
    currentPage = data['currentPage']
    totalRow = data['totalRow']
    toBeShowed = data['toBeShowed']
    totalPages = data['totalPages']
    table = data['table']

    firstButton = button1 = button2 = button3 = button4 = button5 = lastButton = ""

    if currentPage == 1:
        if totalRow > toBeShowed:
            button1 = f'''<a class="btn btn-left btn-active" disabled>1</a>'''
            button2 = f'''<a href="/browse?table={table}&page=2" class="btn">2</a>'''
        if totalRow > (toBeShowed*2):
            button3 = f'''<a href="/browse?table={table}&page=3" class="btn">3</a>'''
        if totalRow > (toBeShowed*3):
            button4 = f'''<a href="/browse?table={table}&page=4" class="btn">4</a>'''
        if totalRow > (toBeShowed*4):
            button5 = f'''<a href="/browse?table={table}&page=5" class="btn">5</a>'''
        if totalRow > toBeShowed:
            lastButton = f'''<a href="/browse?table={table}&page={totalPages}" class="btn btn-right">&raquo;</a>'''

    elif currentPage >= totalPages:
        firstButton = f'''<a href="/browse?table={table}&page=1" class="btn btn-left">&laquo;</a>'''
        if currentPage-4 > 0:
            button1 = f'''<a href="/browse?table={table}&page={currentPage-4}" class="btn">{currentPage-4}</a>'''
        if currentPage-3 > 0:
            button2 = f'''<a href="/browse?table={table}&page={currentPage-3}" class="btn">{currentPage-3}</a>'''
        if currentPage-2 > 0:
            button3 = f'''<a href="/browse?table={table}&page={currentPage-2}" class="btn">{currentPage-2}</a>'''

        button4 = f'''<a href="/browse?table={table}&page={currentPage-1}" class="btn">{currentPage-1}</a>'''
        button5 = f'''<a class="btn btn-active btn-right">{currentPage}</a>'''
        
    else:
        firstButton = f'''<a href="/browse?table={table}&page=1" class="btn btn-left">&laquo;</a>'''
        if currentPage-2 > 0:
            button1 = f'''<a href="/browse?table={table}&page={currentPage-2}" class="btn">{currentPage-2}</a>'''
        button2 = f'''<a href="/browse?table={table}&page={currentPage-1}" class="btn">{currentPage-1}</a>'''
        button3 = f'''<a class="btn btn-active" disabled>{currentPage}</a>'''
        button4 = f'''<a href="/browse?table={table}&page={currentPage+1}" class="btn">{currentPage+1}</a>'''
        if totalPages >= currentPage+2:
            button5 = f'''<a href="/browse?table={table}&page={currentPage+2}" class="btn">{currentPage+2}</a>'''
            if currentPage == 2:
                if totalPages >= currentPage+3:
                    button5 += f'''<a href="/browse?table={table}&page={currentPage+3}" class="btn">{currentPage+3}</a>'''
        if currentPage == (totalPages-1):
            if currentPage-3 > 0:
                tem = button1
                button1 = f'''<a href="/browse?table={table}&page={currentPage-3}" class="btn">{currentPage-3}</a>''' + tem
        
        lastButton = f'''<a href="/browse?table={table}&page={totalPages}" class="btn btn-right">&raquo;</a>'''

        
    
        
    return (firstButton + button1 + button2 + button3 + button4 + button5 + lastButton)

basicdata = {
    "database_name": os_path.basename(database),
    "table_array": sqliteFetch(''' select `tbl_name` from sqlite_master WHERE `tbl_name` IS NOT 'sqlite_sequence' '''),
    "database_location": database
}

def refreshBasicData():
    global basicdata
    basicdata = {
    "database_name": os_path.basename(database),
    "table_array": sqliteFetch(''' select `tbl_name` from sqlite_master WHERE `tbl_name` IS NOT 'sqlite_sequence' '''),
    "database_location": database
    }


@app.route("/")
def index():
    return render_template_string(pages['index'], basicdata=basicdata)

@app.route("/browse")
def browse():
    if "table" in request.args:
        table = parseString(request.args.get("table"))
        if (sqliteFetch(f''' SELECT `tbl_name` from `sqlite_master` WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
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
            q += " LIMIT 100"
            query = sqliteFetch(q)
            createdButton = ""
        else:
            totalRow = sqliteFetch(f'''SELECT count(*) FROM {table} ''')[0][0]
            if totalRow <= 0:
                totalRow = 1
            toBeShowed = 50
            totalPages = ceil(totalRow/toBeShowed)
            if "page" not in request.args:
                pageCount = 1
            else:
                pageCount = request.args.get("page")
                try:
                    pageCount = int(pageCount)
                except ValueError:
                    pageCount = 1
                if pageCount <= 0:
                    pageCount = 1
                if pageCount >= totalPages:
                    pageCount = totalPages

            
            rowsAlreadyShowed = ((pageCount-1)*toBeShowed)
            data = {
                "currentPage": pageCount,
                "totalRow": totalRow,
                "toBeShowed": toBeShowed,
                "totalPages": totalPages,
                "table": table
            }
            createdButton = createButtons(data)
            query = sqliteFetch(f'''SELECT * FROM {table} LIMIT {rowsAlreadyShowed}, 50''')
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

        return render_template_string(pages['browse'], basicdata=basicdata, selected_table=table, data=data, buttons=createdButton)
    else:
        return render_template_string(pages['error'], basicdata=basicdata), 404


@app.route("/structure")
def structure():
    if "table" in request.args:
        table = parseString(request.args.get("table"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
        data = get_table_info(table)
        return render_template_string(pages["structure"], basicdata=basicdata, selected_table=table, data=data)
    else:
        return render_template_string(pages["error"], basicdata=basicdata), 404

@app.route("/create")
def create_table():
    return render_template_string(pages["table"], basicdata=basicdata)

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
        except sqlite3.Error as e:
            returnData = {
                "status": "failure",
                "message": e
            }
        return sendJson(returnData, 200)
    return render_template_string(pages["error"], basicdata=basicdata), 404

@app.route("/insert")
def insert():
    if "table" in request.args:
        table = parseString(request.args.get("table"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
        data = get_table_info(table)
        return render_template_string(pages["insert"], basicdata=basicdata, selected_table=table, data=data)
    else:
        return render_template_string(pages["error"], basicdata=basicdata), 404

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
        except sqlite3.Error as e:
            returnData = {
                "status": "failure",
                "message": e
            }
        return sendJson(returnData, 200)
    return render_template_string(pages["error"], basicdata=basicdata), 404

@app.route("/operations")
def operations():
    if "table" in request.args:
        table = parseString(request.args.get("table"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
        data = get_table_info(table)
        return render_template_string(pages["operations"], basicdata=basicdata, selected_table=table, data=data)
    else:
        return render_template_string(pages["error"], basicdata=basicdata), 404

@app.post("/~empty-table")
def empty_table():
    if "table" in request.form:
        table = parseString(request.form.get("table"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
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
        return render_template_string(pages["error"], basicdata=basicdata), 404

@app.post("/~delete-table")
def delete_table():
    if "table" in request.form:
        table = parseString(request.form.get("table"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
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
        return render_template_string(pages["error"], basicdata=basicdata), 404

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
        return render_template_string(pages["error"], basicdata=basicdata), 404

@app.route("/execute")
def execute_sql():
    return render_template_string(pages["executesql"], basicdata=basicdata)

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
    if "table" in request.args:
        table = parseString(request.args.get("table"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
        data = get_table_info(table)
        return render_template_string(pages["addcolumn"], basicdata=basicdata, selected_table=table, data=data)
    else:
        return render_template_string(pages["error"], basicdata=basicdata), 404

@app.route("/editrow")
def edit_row():
    if "table" in request.args and "key" in request.args and "index" in request.args:
        table = parseString(request.args.get("table"))
        key = parseString(request.args.get("key"))
        index = parseString(request.args.get("index"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
        table_data = get_table_info(table)
        column_data_fetched = sqliteFetch(f''' SELECT * FROM {table} WHERE {key} = '{index}' LIMIT 1 ''')
        if column_data_fetched == []:
            return render_template_string(pages["error"], basicdata=basicdata), 404
        column_data = column_data_fetched[0]

        return render_template_string(pages["editrow"], basicdata=basicdata, selected_table=table, table_data=table_data, column_data=column_data, key=key, index=index)

@app.route("/renamecolumn")
def rename_column():
    if "table" in request.args and "column" in request.args:
        table = parseString(request.args.get("table"))
        column = parseString(request.args.get("column"))
        if (sqliteFetch(f''' SELECT `tbl_name` from sqlite_master WHERE `name` = '{table}' ''')) == [] or table == "sqlite_sequence":
            return render_template_string(pages["error"], basicdata=basicdata), 404
    table_data = get_table_info(table)
    for data in table_data:
        if data[1] == column:
            column_data = data
            break
    return render_template_string(pages["renamecolumn"], basicdata=basicdata, selected_table=table, column_data=column_data)

@app.route("/~refresh")
def refresh_data():
    refreshBasicData()
    return ""

@app.route("/favicon.ico")
def favicon():
    return decodeFile(media['favicon.ico'], "image/x-icon")

@app.route("/media/images/logo.jpg")
def media_logo_jpg():
        return decodeFile(media['logo.jpg'], "image/jpeg")

@app.route("/media/styles/style.css")
def media_style_css():
    return decodeFile(media['style.css'], 'text/css')

@app.route("/media/styles/fontface.css")
def media_fontface_css():
    return decodeFile(media['fontface.css'], 'text/css')

@app.route("/media/js/main.js")
def media_main_js():
    return decodeFile(media['main.js'], 'application/javascript')

@app.errorhandler(404)
def errorhandler(error):
    return render_template_string(pages["error"], basicdata=basicdata), 404

@app.errorhandler(500)
def serverErrorHandler(error):
    return render_template_string(pages['servererror'], basicdata=basicdata), 500


webbrowser_open("http://127.0.0.1:6068")
print("Started SQLite Explorer on http://127.0.0.1:6068")

app.run(port=6068)


""".encode())

exec(b64decode(encodedCode).decode())


