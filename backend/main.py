from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
from pydantic import BaseModel
from database import SessionLocal, engine
from sqlalchemy import text
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    # Add your frontend URL here, THIS IS IMPORTANT FOR CORS
    # It indicates which domains/urls are allowed to make requests to this backend
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Queryrequest(BaseModel):
    query: str
    
# creating the database dependencies

def get_db():
    # Try to get a databse connection
    # We open a connection, yield it, and then close it after the request is done
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# we use the metadata from models to create the database tables
models.Base.metadata.create_all(bind=engine)


# API endpoints
""" Definition of the endpoints are as follows """

@app.post("/uploadfile/", response_model=dict)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith('.csv'):
        print("This is not a csv file")
        raise HTTPException(status_code=400, detail="Invalid file type. Only CSV files are allowed.")
    try:
        # Read the CSV file into a pandas DataFrame
        contents = await file.read()
        df = pd.read_csv(pd.io.common.BytesIO(contents))
        print(df.head())
        # Assuming the CSV has columns: company_name, city, employees, revenue
        required_columns = { 'id','company_name', 'city', 'employees', 'revenue'}
        if not required_columns.issubset(df.columns):
            raise HTTPException(status_code=400, detail=f"CSV file must contain the following columns: {', '.join(required_columns)}")

        for _, row in df.iterrows():
            db_file = models.Files(
                company_name=row['company_name'],
                city=row['city'],
                employees=row['employees'],
                revenue=row['revenue']
            )
            db.add(db_file)
        db.commit()
        return {"message": "File uploaded and data saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {str(e)}")
    
@app.post("/sqlquery/")
# the query is passed as a string in the body of the request
async def sql_query(request:Queryrequest , db: Session = Depends(get_db)):
    # convert to sql alchemy query and send the result in JSON format
    print(f"Received query: {request.query}")
    try:
        result = db.execute(text(request.query))
        # Fetch all results     
        rows = result.fetchall()

        columns = result.keys()      

        # In a case of invalid query
        if not columns:
            raise HTTPException(status_code=400, detail="The query did not return any columns. Please check your SQL syntax.")
        
        columns = [col for col in result.keys() if col.lower() != 'id']        
        print(f"column list : {columns}")
        
        
        # Convert to list of dicts (normal format)
        # Convert each row to dict but skip the id key
        normal_results = []
        for row in rows:
            row_dict = dict(zip(result.keys(), row))
            # Remove the ID key if it exists
            row_dict.pop("id", None)
            normal_results.append(row_dict)
        # represented format [
        #   {"Name": "John", "Last Name": "Doe", "Age": "25", "Occupation": "driver"},
        #   {"Name": "Jack", "Last Name": "Brown", "Age": "24", "Occupation": "it"},
        #   {"Name": "Oliver", "Last Name": "Black", "Age": "30", "Occupation": "cto"}
        #]

        # In a case of no results
        if not normal_results:
            # print the columns names only!
            return {
                "columns": columns,
                "data": []
            }
    
        
        # return column_data
        return {
            "columns": columns,
            "data": normal_results
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred while executing the query: {str(e)}")
    
    
        
