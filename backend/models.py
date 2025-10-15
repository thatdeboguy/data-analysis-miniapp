from database import Base
from sqlalchemy import Column, Integer, String, Float

# Assume that the structure of the CSV files are all the same;
# for example, they all have id, company_name, city, employees, and revenue columns.
class Files(Base):
    __tablename__ = "csv_files"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, index=True)
    city = Column(String, index=True)
    employees = Column(Integer)
    revenue = Column(Float)
