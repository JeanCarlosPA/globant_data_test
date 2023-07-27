import json
import pandas as pd
import os
from sqlalchemy import create_engine
import awswrangler as wr

print("Starting migration process")

def read_columns_config():
    """
    Read and return the list of columns configuration 
    to be used in the migration process
    """
    print("Reading columns configuration")

    if os.getenv("ENV") == 'aws':
        path = 'columns_config.json'
    elif os.getenv("ENV") == 'local':
        path = 'migration_app/migration/columns_config.json'

    with open(path, "r") as file:
        data = json.load(file)
    return data


COLUMNS = read_columns_config()


def lambda_handler(event, context):
    keys = list(json.loads(event["body"]).keys())
    print("Body keys", keys)

    if "entity" in keys and "data" in keys:
        """""
        Execute this statement if the payload has entity and data keys
        which means that the data is going to be read from the payload
        """""
        print("Reading data from request payload")

        try:
            #read data from payload request
            entity = json.loads(event["body"])["entity"].lower()#entity is the table name
            data = json.loads(event["body"])["data"]#data is the CSV

            #Validate if data comes in string format
            if isinstance(data, str):
                pass
            
            else:
                return {
                    "statusCode": 400, 
                    "body": json.dumps({
                        "message": "wrong data format, expected format should be string"
                        })
                    }
            
            #Entity must be in COLUMNS configuration
            if entity in list(COLUMNS.keys()):
                #Take the first 1000 rows from the entire data
                data = "\n".join(data.split("\n")[:1000])

                #Write incoming data to local storage 
                print("Writting data to local storage")
                local_path = "/tmp/data.csv"
                with open(local_path, 'w') as file:
                    file.write(data)
                del(data)

                #Read data into a pandas dataframe
                print("Reading data into pandas DataFrame")
                headers = list(COLUMNS[entity]["columns"].keys())
                df = pd.read_csv(local_path, sep=",", names=headers)

                #Call store_data function if data has more than 0 records
                if len(df) > 0:
                    store_data(df, entity)

            else:
                #Return error if provided entity does not exist in COLUMNS configuration
                return {"statusCode": 400, "body": json.dumps({"message": "entity/table does not exists"})}
        
        except Exception as e:
            print(e)
            return {"statusCode": 400, "body": json.dumps({"message": str(e)})}
    
    elif "entity" in keys and "s3_uri" in keys:
        """""
        Execute this statement if the payload has entity and s3_uri keys
        which means that the data is going to be read from AWS S3 
        """""
        print("Reading data from S3 bucket")

        try:
            #read data from s3 bucket
            entity = json.loads(event["body"])["entity"].lower()#entity is the table name
            data = json.loads(event["body"])["s3_uri"]#data is the CSV

            #Validate if s3 uri comes in string format
            if isinstance(data, str):
                pass
            
            else:
                return {
                    "statusCode": 400, 
                    "body": json.dumps({
                        "message": "wrong s3 uri param format, expected format should be string"
                        })
                    }
            
            #Entity must be in COLUMNS configuration
            if entity in list(COLUMNS.keys()):
                
                #Read data (first 1000 rows) directly from S3 into a pandas DataFrame
                print("Reading data into pandas DataFrame")
                headers = list(COLUMNS[entity]["columns"].keys())
                dfs = wr.s3.read_csv(path=data, sep=',', names=headers, chunksize=1000)
                for df_ in dfs:
                    df = df_
                    break

                #Call store_data function if data has more than 0 records
                if len(df) > 0:
                    store_data(df, entity)

            else:
                #Return error if provided entity does not exist in COLUMNS configuration
                return {"statusCode": 400, "body": json.dumps({"message": "entity/table does not exists"})}
            
        except Exception as e:
            print(e)
            return {"statusCode": 400, "body": json.dumps({"message": str(e)})}
        
    else:
        #Return error if keys in the payload doe not match with required keys
        return {"statusCode": 400, "body": json.dumps({"message": "wrong payload keys it needs to be entity and data or entity and s3_uri"})}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "success running the application",
            }
        ),
    }


def store_data(df, entity):
    """
    This function is in charge of receive data to be uploades to PostgreSQL, 
    read connection configuration, stablish connection to the engine
    and finally upload incoming data to the table defined in the entity argument
    """
    print("Store data to PostgreSQL table: ", entity)
    try:
        print("Connecting to PostgreSQL engine")

        #Read connection information
        host = os.getenv("HOST")
        port = os.getenv("PORT")
        dbname = os.getenv("DB_NAME")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        
        #Create SQLAlchemy engine
        connection_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        engine = create_engine(connection_url)

        print("Success connection to PostgreSQL")

        print("Insert data to PostgreSQL")

        #Identify table typo to know if replace table or insert new data
        mode = "replace" if COLUMNS[entity]["type"]=="catalog" else "append"

        #Connect and insert data
        with engine.connect() as connection:
            df.to_sql(entity, connection, if_exists=mode, index=False)
            connection.commit()

        print("Success storing data to PostgreSQL")

    except Exception as e:
        raise e
