import json
from sqlalchemy import create_engine, text
import pandas as pd
import os

"""
This functions will calculate and return the list of ids, name and number of 
employees hired of each department that hired more employees than the mean of employees hired in 2021 for all the departments
"""

def lambda_handler(event, context):
    
    try:
        #Read DB connection params from environment variables
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")

        #Create SQLAlchemy engine
        connection_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        engine = create_engine(connection_url)

        query = f"""
            SELECT dp.id, dp.department, COUNT(*) AS count
            FROM hired_employees he
            INNER JOIN departments dp ON dp.id = he.department_id
            GROUP BY dp.id, dp.department
            HAVING count(*) > (SELECT AVG(count) FROM (SELECT dp.id, dp.department, COUNT(*) AS count
                                FROM hired_employees he
                                INNER JOIN departments dp ON dp.id = he.department_id
                                WHERE EXTRACT(YEAR FROM TO_DATE(datetime, 'YYYY-MM-DD')) = 2021
                                GROUP BY dp.id, dp.department) AS sub1)
            ORDER BY count DESC
        """

        #Convert query format for SQLAlchemy 
        sql_query = text(query) 

        #Create a connection and read data into a pandas DataFrame
        with engine.connect() as connection:
            df = pd.read_sql(sql_query, connection)
        
        print(df)
        data = df.to_csv(index=False)

    except Exception as e:
        print(e)
        return {"statusCode": 400, "body": json.dumps({"message": str(e)})}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "success getting list of ids, name and number of employees hired of each department that hired more employees than the mean of employees hired in 2021 for all the departments",
                "query_result": data
            }
        ),
    }
