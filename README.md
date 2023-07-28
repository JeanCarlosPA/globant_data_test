# Migration App

This project contains source code and supporting files for a serverless application that can be deployed with the SAM CLI. The most important files and folders included are:

- migration - Code for the migration Lambda function and Project Dockerfile.
- requirement1 - Code for the requirement 1 Lambda function and Project Dockerfile.
- requirement2 - Code for the requirement 2 Lambda function and Project Dockerfile.
- template.yaml - A template that defines the application's AWS resources (Lambda Functions, Api Gateways, Roles and Policies)
- tests - Code to run functions locally.

The functions inside this project are intended to achieve a serie of tasks in order to upload data to a PostgreSQL database and answer two different questions running some SQL queries and returning the result through an Rest API response.

The application uses several AWS resources, including Lambda functions, API Gateway APIs, Roles and Policies. These resources are defined in the `template.yaml` file in this project. The template can be updated to add AWS resources through the same deployment process that updates the application code.

## Deploy the migration_app application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. 
It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

You may need the following for local testing.
* [Python 3 installed](https://www.python.org/downloads/)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build a docker image from a Dockerfile and then copy the source of your application inside the Docker image

The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: This AWS SAM templates creates AWS IAM roles required for the AWS Lambda functions and Api Gateways to access AWS services
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoints URL for MigrationFunction, Requirement1Function and Requirement2Function in the output values displayed in the console after deployment.

The SAM CLI reads the application template to determine the Environment Variables, MemorySize and Timeout to be set in the functions. The `Globals` property on the template includes this information. The environment Variables values need to provided before to run `sam build` and `sam deploy --guided` commands.

```yaml
      Globals:
        Function:
            Timeout: 60
            MemorySize: 256
            Environment:  # Add Environment property to specify environment variables
            Variables:
                HOST: ""
                PORT: ""
                DB_NAME: ""
                DB_USER: ""
                DB_PASSWORD: ""
                ENV: "aws"
```

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
migration_app$ sam build
```

The SAM CLI builds docker image from a Dockerfile and then installs dependencies defined in `{functionName}/requirements.txt` inside the docker image. The processed template file is saved in the `.aws-sam/build` folder.

Test all functions by invoking unit/test_handler.py and setting environment variables and arguments as shown below:

```bash
"args": ["s3"],
"env": {
    "HOST": "...",
    "PORT": "...",
    "DB_NAME": "...",
    "DB_USER": "...",
    "DB_PASSWORD": "...",
    "ENV": "local"
}

Note: It is needed to be provided the right value to HOST, PORT, DB_NAME, DB_USER and DB_PASSWORD. Those values are to the PostgreSQL connection.
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
migration_app$ sam local start-api
migration_app$ curl http://localhost:3000/
```

## Use Rest API requests to use the hosted application

Once the Application is deployed and running in the AWS account, it can be used by sending some http requests to the different endpoints depending on the task that need to be perform.

Here are some example using python with requests library locally to call those endpoints

# MigrationFunction: 
Respond to a POST call
```bash
import requests

#URL to make the request, this is provided by the output of the deployment
url_post = f"https://{api_gateway_id}.execute-api.us-east-1.amazonaws.com/Prod/insert/"

#S3 URI where input file is located
csv_data = f"s3://{bucket}/departments.csv"

#Make request
response = requests.post(url_post, json={"entity":"departments", "s3_uri": csv_data}, timeout=60)
print(response, response.json())

OUTPUT>> <Response [200]>, {'message': 'success running the application'}
```

# Requirement1Function:
Respond to a GET call
```bash
import requests

#URL to make the request, this is provided by the output of the deployment
url_post = f"https://{api_gateway_id}.execute-api.us-east-1.amazonaws.com/Prod/requirement1/"

#Make request
response = requests.get(url_get, timeout=60)
print(response, response.json())

OUTPUT>> <Response [200]>, {'message': 'success getting number of employees hired for each job and department in 2021 divided by quarter',
                            'query_result': 'job,department,q1,q2,q3,q4\nAccount Representative IV,Accounting,1,0,0,0\n'}
```

# Requirement2Function:
Respond to a GET call
```bash
import requests

#URL to make the request, this is provided by the output of the deployment
url_post = f"https://{api_gateway_id}.execute-api.us-east-1.amazonaws.com/Prod/requirement2/"

#Make request
response = requests.get(url_get, timeout=60)
print(response, response.json())

OUTPUT>> <Response [200]>, {'message': 'success getting number of employees hired for each job and department in 2021 divided by quarter',
                            'query_result': 'id,department,count\n8,Support,256\n6,Human Resources,249\n'}
```

# Note:
Keep in mind that the values for test endpoints hosted in AWS the right URL need to be provided in the request.

## Cleanup

To delete the sample application that you created, use the AWS CLI. Once inside the project folder, run the following command and confirm the prompts:

```bash
migration_app$ sam delete
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
