from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd
from pydantic import BaseModel
from database import SessionLocal, engine
from sqlalchemy import text, inspect
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import models
from dotenv import load_dotenv
from openai import OpenAI
import os 
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()  # Load environment variables from .env file


app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


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
    
    print(f"Received query: {request.query}")

    # check if the request.query is in natural language or SQL
    if not request.query.strip().lower().startswith("select"):
        print("The query is in natural language, passing to the agent")
        # get table column and pass to the agent. this helps to generate appropriate queries.
        columns, table_name = get_table_columns(db)
        
        request.query = simple_agent(request.query, columns, table_name)
        print(f"Transformed query: {request.query}")


    # Basic query safety check
    forbidden_keywords = ["drop", "delete", "update", "insert", "alter"]
    lowered = request.query.lower()
    if any(keyword in lowered for keyword in forbidden_keywords):
        raise HTTPException(status_code=403, detail="Destructive SQL commands are not allowed.")
    try:
        result = db.execute(text(request.query))
        # Fetch all results     
        rows = result.fetchall()

        columns = result.keys()      

        # In a case of invalid query
        if not columns:
            raise HTTPException(status_code=400, detail="The query did not return any columns. Please check your SQL syntax.")
        
        columns = [col for col in result.keys() if col.lower() != 'id']        
        
        
        
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
    except OperationalError as e:
        raise HTTPException(status_code=422, detail=f"SQL syntax error: {str(e)}")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"An error occurred while executing the query: {str(e)}")
    
    
def simple_agent(prompt: str, columns: list[str], table_name) -> str:
    """ A simple agent that uses openai to transform the prompt into a SQL query """

    #schema_description = ", ".join(columns)
    system_prompt = """ Use a small agent on the backend to convert simple queries written in natural language from the frontend into SQL.
                Example rule-based agent:
                Python

                def simple_agent(prompt: str) -> str:
                if "shift a" in prompt.lower():
                return 'SELECT * FROM data WHERE VARDIYA = "A";'
                elif "average" in prompt.lower():
                return 'SELECT AVG(Value) FROM data;'
                else:
                return "SELECT * FROM data LIMIT 10;"
        """ 
    secondary_prompt = f"this is the schema of the table: {columns}. and the name of the table is {table_name}, use this to generate appropriate queries, for example if they imply company, in the query it should be company_name as per the schema also replace double quotes with single quotes in the query. Do not add any other text, only return the SQL query"
    try:
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are an assistant that helps to transform natural language to sql queries. for example {system_prompt}, {secondary_prompt}"},
                {"role": "user", "content": f"Convert this natural language request into an SQL query: {prompt}"}
            ]
        )
        sql_query = response.choices[0].message.content.strip()
        if sql_query.startswith("```sql"):
            sql_query = sql_query[7:-3].strip()  # Remove ```sql and ```
        return sql_query
    except Exception as e:
        print(f"Error in OpenAI API call: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating SQL query from natural language.")
    
def get_table_columns(db: Session) -> list:
    """ Get the column names of a table """
    inspector = inspect(engine)
    table_name = inspector.get_table_names()[0] #Since we have only one table
    columns = inspector.get_columns(table_name)
    column_names = [column['name'] for column in columns if column['name'].lower() != 'id']
    return column_names, table_name
