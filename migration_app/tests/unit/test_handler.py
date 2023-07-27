import json
import pytest
import sys
sys.path.append('migration_app')
from migration import app


def event(arg):
    """ Generates API GW Event"""
    if sys.argv[1] == 'str':
        tests_data = {
            "jobs": 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/jobs.csv',
            "departments": 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/departments.csv',
            "hired_employees": 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/hired_employees.csv'
            }
        
        with open(tests_data[arg], 'rt') as file:
            data = file.read()

        return {"body": json.dumps({"entity":arg, "data": data})}
    
    if sys.argv[1] == 's3':
        tests_s3 = {
            "jobs": 's3://globant-test-storage/jobs.csv',
            "departments": 's3://globant-test-storage/departments.csv',
            "hired_employees": 's3://globant-test-storage/hired_employees.csv'
            }
        
        data = tests_s3[arg]

        return {"body": json.dumps({"entity":arg, "s3_uri": data})}

def test_lambda_handler(input):

    ret = app.lambda_handler(event(input), "")


if __name__ == '__main__':
    test_lambda_handler("jobs")
    test_lambda_handler("departments")
    test_lambda_handler("hired_employees")