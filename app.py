# daily_work_report_app/app.py

from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_
from datetime import date
from dotenv import load_dotenv
import pandas as pd
import os
import io

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

EXCEL_FILE = 'Daily_Work_Report.xlsx'

@app.route('/add', methods=['GET', 'POST'])
def add():
    categories = ['Compliance', 'Broker Management', 'Database', 'AWS DevOps', 'Git', 'Postman', 'Other']
    statuses = ['Pending', 'In Progress', 'Completed', 'Blocked']

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

        # Append to Excel file
        new_row = {
            'Date': date_input,
            'Category': category,
            'Issue': issue,
            'Root Cause': root_cause,
            'Action Taken': action_taken,
            'Status': status
        }

        try:
            if os.path.exists(EXCEL_FILE):
                df_existing = pd.read_excel(EXCEL_FILE)
                df_updated = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
            else:
                df_updated = pd.DataFrame([new_row])

            df_updated.to_excel(EXCEL_FILE, index=False)
        except PermissionError:
            print("⚠️ Please close the Excel file before submitting a new report.")

        return redirect(url_for('index'))

    return render_template('add.html', categories=categories, statuses=statuses)


@app.route('/generate')
def generate_report():
    reports = DailyReport.query.order_by(DailyReport.date.desc()).all()

    data = [{
        "Date": r.date,
        "Category": r.category,
        "Issue": r.issue,
        "Root Cause": r.root_cause,
        "Action Taken": r.action_taken,
        "Status": r.status
    } for r in reports]

    df = pd.DataFrame(data)
    file_path = EXCEL_FILE
    df.to_excel(file_path, index=False)

    return send_file(file_path, as_attachment=True)

@app.route('/view', methods=['GET'])
def view_reports():
    # Use predefined categories and statuses (for consistent dropdowns)
    categories = ['Compliance', 'Broker Management', 'Database', 'AWS DevOps', 'Git', 'Postman', 'Other']
    statuses = ['Pending', 'In Progress', 'Completed', 'Blocked']

    query = DailyReport.query

    selected_category = request.args.get('category')
    selected_status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if selected_category:
        query = query.filter(DailyReport.category == selected_category)
    if selected_status:
        query = query.filter(DailyReport.status == selected_status)
    if start_date and end_date:
        query = query.filter(
            and_(DailyReport.date >= start_date, DailyReport.date <= end_date)
        )

    filtered_reports = query.order_by(DailyReport.date.desc()).all()

    return render_template(
        'view.html',
        reports=filtered_reports,
        categories=categories,
        statuses=statuses,
        selected_category=selected_category,
        selected_status=selected_status,
        start_date=start_date,
        end_date=end_date
    )

@app.route('/download')
def download_report():
    reports = DailyReport.query.order_by(DailyReport.date.desc()).all()
    data = [{
        "Date": r.date,
        "Category": r.category,
        "Issue": r.issue,
        "Root Cause": r.root_cause,
        "Action Taken": r.action_taken,
        "Status": r.status
    } for r in reports]

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Daily Report")
    output.seek(0)

    return send_file(output, download_name="Daily_Work_Report.xlsx", as_attachment=True)

@app.route('/delete/<int:report_id>', methods=['POST'])
def delete_report(report_id):
    report = DailyReport.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)