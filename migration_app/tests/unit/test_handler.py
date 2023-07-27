import json
import pytest
import sys
sys.path.append('migration_app')
from migration import app


def event(arg):
    """ Generates API GW Event"""

    tests = {
        "jobs": 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/jobs.csv',
        "departments": 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/departments.csv',
        "hired_employees": 'C:/Users/Jean Palomeque/Documents/globant_test/data_challenge_files (2)/hired_employees.csv'
        }

    with open(tests[arg], 'rt') as file:
        csv_data = file.read()
    
    return {"body": json.dumps({"entity":arg, "data": csv_data})}


def test_lambda_handler(input):

    ret = app.lambda_handler(event(input), "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 200
    assert "message" in ret["body"]
    #assert data["message"] == "hello world"



if __name__ == '__main__':
    test_lambda_handler("jobs")
    test_lambda_handler("departments")
    test_lambda_handler("hired_employees")