import json
import pandas as pd
import io

#Columns format definition for every table
COLUMNS = {
    "departments": {"id": int, "department": str},
    "jobs": {"id": int, "job": str},
    "hired_employees": {"id": int, "name": str, "datetime": str, "department_id": int, "job_id": int}
}

def lambda_handler(event, context):

    keys = list(event.keys())

    #If this keys are send by the user, it means that data comes inside the payload
    if "entity" in keys and "data" in keys:
        try:
            entity = event["entity"].lower()
            data = event["data"]

            #Validate if data comes in any expected format when data is sent directly in the payload
            #Data should be string, bytes or binary objects (BufferedReader or TextIOWrapper)
            if isinstance(data, str):
                print("data came as string")

            elif isinstance(data, bytes):
                print("data came as bytes")
                data = event["data"].decode()

            elif isinstance(data, io.BufferedReader):
                print("data came as BufferedReader")
                data = data.read().decode()
            
            elif isinstance(data, io.TextIOWrapper):
                print("data came as TextIOWrapper")
                data = data.read()
            
            else:
                return {"statusCode": 400, "body": json.dumps({"message": "wrong data format"})}
            
            #Validate which table in the user trying to store using the entity parameter that need to be send in the payload
            if entity in ["departments", "jobs", "hired_employees"]:
                #Take the first 1000 rows from the entire data
                data = "\n".join(data.split("\n")[:1000])

                #Write incoming data to local storage 
                local_path = "/tmp/data.csv"
                with open(local_path, 'w') as file:
                    file.write(data)
                del(data)

                #Read data into a pandas dataframe
                headers = list(COLUMNS[entity].keys())
                df = pd.read_csv(local_path, sep=",", names=headers)

                print(df)

                if len(df) > 0:
                    store_data(df)

            else:
                return {"statusCode": 400, "body": json.dumps({"message": "wrong entity"})}
        
        except Exception as e:
            raise e
        
    elif "entity" in keys and "s3_uri" in keys:
        try:
            pass
        except Exception as e:
            raise e
        
    else:
        return {"statusCode": 400, "body": json.dumps({"message": "wrong keys"})}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello glober...",
            }
        ),
    }

def store_data(df):
    pass

if __name__ == "__main__":

    data_type = ["str","bytes","csv","text"][1]
    input_entity = "hired_employees"

    #input_file = 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/jobs.csv'
    #input_file = 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/departments.csv'
    input_file = 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/hired_employees.csv'

    if data_type == "str":
        with open(input_file, 'rt') as file:
            csv_data = file.read()
        print(lambda_handler({"entity":input_entity, "data": csv_data}, ""))

    if data_type == "bytes":
        with open(input_file, 'rt') as file:
            csv_data = file.read().encode("utf-8")
        with open(input_file, 'rb') as file:
           csv_data = file.read()
        print(lambda_handler({"entity":input_entity, "data": csv_data}, ""))

    if data_type == "csv":
        csv_data = open(input_file, 'rb')
        print(lambda_handler({"entity":input_entity, "data": csv_data}, ""))

    if data_type == "text":
        csv_data = open(input_file, 'rt')
        print(lambda_handler({"entity":input_entity, "data": csv_data}, ""))