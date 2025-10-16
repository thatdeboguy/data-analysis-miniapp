#  Data-Mini Application (Claridad Task)

##  Overview

**Data-Mini Application** is a lightweight web-based data analysis tool built with **FastAPI** (backend) and **React** (frontend).  

It allows users to:
- Upload **CSV files** of their choice.
- Store the uploaded data in a **SQLite database**.
- Run **custom SQL queries** on the uploaded data directly from the frontend.
- View the query results in a clean, paginated **data table**.

This project was developed as part of the **Claridad Part-Time Task** to demonstrate proficiency in:
- Python / FastAPI  
- SQL / SQLite  
- React (frontend)
- ETL (Extract, Transform, Load) concepts  
- Problem-solving and clean code practices  

---


##  Features

###  Core Features
- Upload CSV files to the backend.
- Data automatically gets stored in a SQLite database.
- Send and execute SQL queries via an API endpoint.
- Return query results as JSON and render them in a responsive table.

###  Optional Enhancements (Implemented / Planned)
- ✅ Meaningful error handling for invalid SQL queries.
- ✅ Bootstrap UI for better UX.
- ⏳ (Optional) Simple rule-based agent for converting natural language to SQL.
- ⏳ (Optional) Chart/Graph visualization of query results.

---

##  Setup & Installation

### 1️ Clone the Repository
```bash
git clone https://github.com/<thatdeboguy>/<data-analysis-miniapp>.git
cd <data-analysis-miniapp>
```
---
### 2 Backend Setup (FastAPI + SQLite)
```bash 
cd backend
python -m venv venv
source venv/bin/activate     # On macOS/Linux
venv\Scripts\activate        # On Windows
```
#### Install required backages 
```bash
Install required Python packages:
pip install -r requirements.txt
```
#### Run the FastAPI development server
```bash
uvicorn main:app --reload
The backend will be running on http://127.0.0.1:8000
```
---
### 3 Frontend Setup (React + Bootstrap)
```bash
cd frontend
cd claridad
npm install
npm install bootstrap react-data-table-component react-router-dom axios
```
#### Run the frontend
```bash
npm start
```
The frontend will be running on http://localhost:3000

---

### How to Use
- Open the web app in your browser (http://localhost:3000).
- Upload a CSV file (only .csv format is supported).
- Once uploaded, enter an SQL query such as:
```sql
    SELECT * FROM csv_files WHERE city = 'Lagos';
```
- click Run Query
- View the results displayed in a formatted, paginated table.
- Natural language could also be used, 'show all companies in lagos'
- click run and then view the same result.

