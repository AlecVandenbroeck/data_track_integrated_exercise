# Axxes integrated exercise

Welcome to the integrated exercise. Everything that you will learn over the 2 week course can be applied on this realistic pipeline.
In short what you will do is:
1. Ingest irceline open air quality data to S3 using their REST API. This can be accomplished through an ingest component written in python
2. Clean and transform the input data using pyspark and write the output to S3, Snowflake
3. Run and schedule the application code using Docker, AWS Batch and Airflow

## Getting started

We've set up a Gitpod environment containing all the tools required to complete this exercise (awscli, python, vscode, ...). You can access this environment by clicking the button below:

[![Open in Gitpod][gitpod logo]][this gitpod]

[this gitpod]: https://gitpod.io/#https://github.com/AlecVandenbroeck/data_track_integrated_exercise
[gitpod logo]: https://gitpod.io/button/open-in-gitpod.svg

NOTE: When you fork this repo to your own remote make sure to change the Gitpod URL to reflect your account in this README!

This is an ubuntu-based environment pre-installed with:

- VSCode
- A Python3 virtual environment: we recommend you always work inside this environment.
- The AWS CLI

Before you start data crunching, set up your $HOME/.aws/credentials file. This is required to access AWS services through the API. To do so, run aws configure in the terminal and enter the correct information:

```
AWS Access Key ID [None]: [YOUR_ACCESS_KEY]
AWS Secret Access Key [None]: [YOUR_SECRET_KEY]
Default region name [None]: eu-west-1
Default output format [None]: json
```
IMPORTANT: Create a new branch and periodically push your work to the remote. After 30min of inactivity this environment shuts down and you will likely lose unsaved progress. As stated before, change the Gitpod URL to reflect your remote.

## Task 1: extract air quality data

As mentioned, we will load open air quality data from irceline using their REST API.
For the documentation of their API, look at their [website](https://www.irceline.be/en/documentation/open-data).
In this step we will query the REST API and write the relevant information in our raw datalake using json files.
The reason for this is to mimic the REST API output as much as possible in our raw layer.

You can start from the provided project structure in this repository for bootstrapping your python project.

### Rest API information
We will use python to call the REST API and fetch the hourly values for specific stations.
We start from their raw data and build up our own dataset accordingly.
The parameters we are interested in are:
- ppm10 (5)
- ppm25 (6001)
- no2 (8)
- co2 (71)
- so2 (1)

The base url for their Rest API is: https://geo.irceline.be/sos/api/v1/

They have 2 interesting endpoints that you will need to combine:
- query stations: here you can query all stations or start by only looking at stations in a city of your choice (e.g. Antwerp).
 - use expanded=true to get the timeseries_ids, which you will need for the next API call.
- query timeseries: for every station, you get a list of timeserie_ids (containing values for every supported parameter of that station).
 - Fetch the data for the parameters we are interested in, the others you can ignore

**Endpoints**:
- stations: https://geo.irceline.be/sos/api/v1/api/v1/stations. Take a look at the near query parameter to filter certain stations
- timeseries: https://geo.irceline.be/sos/api/v1/timeseries look at the query parameters to see what can be useful here

**Extra tips**:

Think about the lessons you have learned about ingesting data for data pipelines like:
- make sure to include all relevant data in the raw input as it is the starting point for all our subsequent queries
- idempotency: rerunning the same job should yield the exact same result
- reproducability: read/write the raw json data from the REST API. Only afterwards clean the data, this allows you to rerun the cleaning without you needing to fetch all data again.

### Development steps

1. Start by experimenting with the API and getting the air quality data locally. This ensures a fast feedback cycle. Write the raw data as json to 1 or more files.
2. If you are confident in your solution, you may test the integration with AWS. For this you would need to make the following changes:
 - configure your aws credentials to a specific profile such that you can connect to the correct aws_account and use the correct credentials. You can then use AWS_PROFILE=... before executing your python code
 - write the files to your own path on the s3 bucket called: **data-track-integrated-exercise**. Prefix the path of the s3 bucket with your first name like: niels-data/...
3. create an aws batch job definition that allows you to run your code in AWS batch. Use the AWS role with name: **integrated-exercise-batch-job-role**.
 - Try wether you can get this working using Terraform: https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/batch_job_definition
 - You will need to create an ecr repository for the docker image that will be used in AWS batch. Before you can push to the ecr registry, you must be logged in:
   ```aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.eu-west-1.amazonaws.com```
 - you can use any python base image for your docker image
 - trigger a job from the AWS batch definition using the AWS console UI
4. create the Airflow dag for ingesting the data every day at midnight. For this I have setup a shared MWAA in the AWS account.
   You can trigger an AWS batch job using the [AwsBatchOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/batch/index.html) of Airflow
   Make sure you prefix your dag with your firstname. Upload your dag code using the aws cli/UI by placing it in the dags folder of the **data-track-integrated-exercise** directory.
   Use the AWS console and the MWAA UI to trigger your dag and test whether it works
5. (bis) make sure you handle timezones correctly
6. (bis) You can also write integration tests with the API and or s3 using localstack

**Important:**

Step 1 is required before moving along to task 2. Step 2-3-4 can be done at a later time if you want to combine it with Task 2, or you did not have the respective training session.

## Task 2: clean and transform the output data using pyspark
In this step we will use pyspark to read the raw json files and transform them to the required output and write the results in our clean layer.
The following transformations are required:
- add a datetime column that converts the epoch millis to a datatime (string representation)
- Calculate the average of the measurements for a specific station by day

You can write the output as parquet to S3 using the following path `<firstname>-data/clean/aggregate_station_by_day` partitioned by (what is the most logic partitioning here?)

### Development steps
1. For this job we will use pyspark instead of plain python. Start from the raw layer of task 1 and read the data as a spark dataframe. Write the output using the parquet format. Start by running the job locally as this allows for quick iterations
 - to select the filesystem in Spark: use s3a://<bucket>/<firstname-data>/clean/<path> as filepath in your code
 - to read from s3 with pyspark, make sure you configure the SparkSession with the aws credentials provider: fs.s3a.aws.credentials.provider = com.amazonaws.auth.DefaultAWSCredentialsProviderChain
 - The full config could look as follows:
```
SparkSession.builder.config(
    "spark.jars.packages",
    ",".join(
        [
            "org.apache.hadoop:hadoop-aws:3.3.1",
        ]
    ),
)
.config(
    "fs.s3a.aws.credentials.provider",
    "com.amazonaws.auth.DefaultAWSCredentialsProviderChain",
)
.getOrCreate()
```
Note: we add the extra hadoop-aws package to make sure it is downloaded before Spark starts. This is the quickest way to set it up for both the local and the remote execution environment.

Note2: export the AWS environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_SESSION_TOKEN) instead of only the aws_profile environment variable if you want to test your code locally.

2. (bis): you can write a couple of unit tests that verify the output of your pyspark transformation function. To make it simple, there is a test fixture provided that launches a local Spark cluster as follows:
The test should start from a dataframe with your test data, call your aggregate function and validate whether it produces the correct averages depending on the situation (e.g. different timestamps within 1 day, different parameters,...)
3. Create an aws batch job definition that allows you to run your job with AWS batch. Use the AWS role with name **integrated-exercise-batch-job-role**.
 - Try wether you can get this working using Terraform.
   You will need to create an ecr repository for your docker image that will be used in AWS batch. You can use 1 image for both jobs. The pyspark job should start from an image with python and java.
   To simplify, you can base your Dockerfile on the following:
```
FROM public.ecr.aws/dataminded/spark-k8s-glue:v3.2.1-hadoop-3.3.1

ENV PYSPARK_PYTHON python3
WORKDIR /opt/spark/work-dir

USER 0

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt --no-cache-dir
COPY . .

RUN pip install --no-cache-dir -e .
```
4. create the Airflow dag for ingesting the data every day at midnight. For this I have setup a shared MWAA in the AWS account.
   You can trigger an AWS batch job using the [AwsBatchOperator](https://airflow.apache.org/docs/apache-airflow-providers-amazon/stable/_api/airflow/providers/amazon/aws/operators/batch/index.html) of Airflow
   Make sure you prefix your dag with your firstname.
 - upload your dag code using the cli: `aws s3 cp dags/integrated_exercise.py s3://data-track-integrated-exercise/dags/integrated_exercise.py`
 - Use the AWS console and the MWAA UI to trigger your dag and test whether it works

### Troubleshooting issues
- If you get some weird error while running Spark with s3a, like: `py4j.protocol.Py4JJavaError: An error occurred while calling o42.json.`
  Make sure all hadoop jars have the same version as is specified in the hadoop-aws config (3.3.1 normally). This can be found under `venv_root/lib/python3.10/site-packages/pyspark/jars/hadoop-*.jar`
