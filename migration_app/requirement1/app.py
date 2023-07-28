import json
from sqlalchemy import create_engine, text
import pandas as pd
import os

def lambda_handler(event, context):
    
    try:
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        connection_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        engine = create_engine(connection_url)

        query = f"""
            SELECT
                jb.job,
                dp.department,
                COUNT(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(datetime, 'YYYY-MM-DD')) = 1 THEN 1 END) AS Q1,
                COUNT(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(datetime, 'YYYY-MM-DD')) = 2 THEN 1 END) AS Q2,
                COUNT(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(datetime, 'YYYY-MM-DD')) = 3 THEN 1 END) AS Q3,
                COUNT(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(datetime, 'YYYY-MM-DD')) = 4 THEN 1 END) AS Q4
            FROM hired_employees he
            LEFT JOIN jobs jb ON jb.id = he.job_id
            LEFT JOIN departments dp ON dp.id = he.department_id
            WHERE EXTRACT(YEAR FROM TO_DATE(datetime, 'YYYY-MM-DD')) = 2021
            GROUP BY jb.job, dp.department
            ORDER BY jb.job, dp.department;
        """
  
        sql_query = text(query) 

        # Create a connection and read data into a pandas DataFrame
        with engine.connect() as connection:
            df = pd.read_sql(sql_query, connection)
        
        print(df)
        data = df.to_csv(index=False)

    except Exception as e:
        raise e

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "success getting number of employees hired for each job and department in 2021 divided by quarter",
                "query_result": data
            }
        ),
    }