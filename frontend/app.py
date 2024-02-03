from flask import Flask, render_template, request, redirect, url_for, flash, session
import datetime
import os
import requests
from Helpers.userMethods import check_user_credentials, check_user_name, get_user_by_id
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

# ///////////////////// Configuration block ///////////////////// #

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))
app.config['SECRET_KEY'] = f'{os.environ.get("secret")}'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=15)
host_ip = f'{os.environ.get("host_ip")}'
backendapi_port = f'{os.environ.get("backendapi_port", 3001)}'
BACKEND_API_BASE_URL = f"http://{host_ip}:{backendapi_port}"

# ///////////////////// Application routes ///////////////////// #


@app.route("/", methods=['GET'])
def home():
    if request.method == 'GET':
        return redirect(url_for('record'))


@app.route("/record", methods=['GET', 'POST'])
def record():
    if 'userName' in session:
        if request.method == 'GET':
            transaction_list = requests.get(
                f"{BACKEND_API_BASE_URL}/api/v2/Transaction/transactionlists", verify=False).json()
            current_year = datetime.datetime.now().year
            return render_template('index.html', current_year=current_year,
                                   transactionList=transaction_list, is_logedIn=True)
        else:
            request_body = {
                "amount": f"{request.form['amount']}",
                "type": f"{request.form['type']}",
                "tag": f"{request.form['tag']}",
                "note": f"{request.form['note']}"
            }
            response_data = requests.post(
                f"{BACKEND_API_BASE_URL}/api/v2/Transaction/addtransaction", json=request_body)
            if response_data.status_code == 200:
                return redirect(url_for('record'))
            else:
                flash(
                    "Error recording transaction. Please check you input and try again!", 'error')
                return redirect(url_for('record'))
    return render_template('login.html', is_logedIn=False)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', is_logedIn=False)
    else:
        username = request.form['userName']
        password = request.form['password']
        if check_user_credentials(username, password):
            session['userName'] = username
            session.permanent = True
            return redirect(url_for('record'))

        return redirect(url_for('login'))


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.pop('userName', None)
    return redirect(url_for('home'))


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    request_body = {
        "userName": f"{request.form['userName']}",
        "password": f"{request.form['password']}"
    }
    response_data = requests.post(
        f"{BACKEND_API_BASE_URL}/api/v2/auth/user/register", verify=False, json=request_body)
    if response_data.status_code == 200:
        return redirect(url_for('record'))
    else:
        flash("Error creating account. Please check your input or try again!", "error")
    return redirect(url_for('register'))


@app.route("/edit/<int:id>", methods=['GET', 'POST'])
def edit(id):
    if 'userName' in session:
        if request.method == 'GET':
            response_data = requests.get(
                f"{BACKEND_API_BASE_URL}/api/v2/Transaction/{id}", verify=False)
            if response_data.status_code == 200:
                json_content = response_data.json()
                return render_template('edit.html', record=json_content["data"], is_logedIn=True)
            else:
                flash(
                    f"Error editing record with id {id}. Please try again!", "error")
                return redirect(url_for("record"))
        else:
            request_body = {
                "amount": f"{request.form['amount']}",
                "transactionType": f"{request.form['type']}",
                "transactionTag": f"{request.form['tag']}",
                "note": f"{request.form['note']}"
            }
            response_data = requests.put(
                f"{BACKEND_API_BASE_URL}/api/v2/Transaction/updatetransaction/{id}", json=request_body)
            if response_data.status_code == 200:
                return redirect(url_for('record'))
            else:
                flash(
                    f"Error editing record with id {id}. Please check your input and try again", "error")
                return redirect(url_for('edit', id=id))
    return render_template('login.html', is_logedIn=False)


@app.route("/summary", methods=['GET', 'POST'])
def summary():
    if 'userName' in session:
        if request.method == 'GET':
            return render_template('stats.html', is_logedIn=True)
        else:
            request_body = {
                "startTime": f"{request.form['startDate']}",
                "endtime": f"{request.form['endDate']}"
            }
            respose_data = requests.post(
                f"{BACKEND_API_BASE_URL}/api/v2/Transaction/summary", verify=False, json=request_body)
            if respose_data.status_code == 200:
                json_content = respose_data.json()
                record_summary = json_content['data']
                return render_template('stats.html',
                                       record_summary=record_summary,
                                       start_date=request.form['startDate'],
                                       end_date=request.form['endDate'],
                                       is_logedIn=True
                                       )
            else:
                flash("Error retiving transaction summary. Please try again!", "error")
                return redirect(url_for('summary'))
    return render_template('login.html', is_logedIn=False)


@app.errorhandler(404)
def page_neot_found(error):
    if 'usrName' in session:
        return render_template('notfound.html', is_logedIn=True)
    return render_template('notfound.html', is_logedIn=False)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
