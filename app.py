# daily_work_report_app/app.py

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class DailyReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(20), default=str(date.today()))
    category = db.Column(db.String(50))
    issue = db.Column(db.Text)
    root_cause = db.Column(db.Text)
    action_taken = db.Column(db.Text)
    status = db.Column(db.Text)

@app.route('/')
def index():
    reports = DailyReport.query.order_by(DailyReport.date.desc()).all()
    return render_template('index.html', reports=reports)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        date_input = request.form['date']
        category = request.form['category']
        issue = request.form['issue']
        root_cause = request.form['root_cause']
        action_taken = request.form['action_taken']
        status = request.form['status']

        report = DailyReport(
            date=date_input,
            category=category,
            issue=issue,
            root_cause=root_cause,
            action_taken=action_taken,
            status=status
        )
        db.session.add(report)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    report = DailyReport.query.get_or_404(id)
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)