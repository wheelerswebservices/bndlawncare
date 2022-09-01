import boto3
import mimetypes
import io
import os
import zipfile

from botocore.client import Config


def error(error_str, pipeline_job=None, sns_topic=None, s3_bucket=None):
    """
    handles errors in a gracefully
    :param error_str: error string that caused failure
    :param pipeline_job: CodePipeline job if initialized
    :param sns_topic: SNS Topic if initialized
    :param s3_bucket: S3 Bucket if initialized
    :return: nothing; raises an exception
    """

    # Publish Failure to the SNS Topic
    bucket = s3_bucket if s3_bucket else "Unknown"
    failure_message = f"Bucket: {bucket}\nStatus: Failure\nDetails:\n\n{error_str}"

    if sns_topic:
        sns_topic.publish(Subject='Code Deploy Failure', Message=failure_message)
    else:
        print("SNS Topic Not Initialized")
        print(failure_message)

    # Set CodePipeline Job to Failure
    if pipeline_job:
        pipeline = boto3.client('codepipeline')
        pipeline.put_job_failure_result(
            jobId=pipeline_job["id"],
            failureDetails={'type': 'JobFailed', 'message': error_str})
    else:
        print("CodePipeline Job Not Initialized")
        print(failure_message)

    # Throw Exception
    raise


def read_artifacts(environment_dict, resources_dict):
    """
    reads the build artifacts from S3 and downloads them into memory
    :param environment_dict: the environment variables provided to the function
    :param resources_dict: the aws resources found
    :return: the in-memory build artifacts
    """

    print("Reading Artifacts...")

    location = {
        "bucketName": environment_dict["s3_artifacts_name"],
        "objectKey": None
    }

    if resources_dict["codepipeline_job"]:
        # Read Location from CodePipeline Job
        for artifact in resources_dict["codepipeline_job"]["data"]["inputArtifacts"]:
            if artifact["name"] == "BuildArtifact":
                location = artifact["location"]["s3Location"]
    else:
        # Read Location from Latest Modified Time
        # Create last_modified List
        time_list = []
        for obj in resources_dict["s3_artifacts"].objects.all():
            time_list.append(obj.last_modified)

        # Find Max Time
        max_time = max(time_list)

        # Find Latest Key
        for obj in resources_dict["s3_artifacts"].objects.all():
            if max_time == obj.last_modified:
                location["objectKey"] = obj.key

    # Print Source
    print(f"\t'Bucket': {location['bucketName']}")
    print(f"\t'Object': {location['objectKey']}")

    # Download File into Memory
    artifacts_zip = io.BytesIO()
    resources_dict["s3_artifacts"].download_fileobj(location["objectKey"], artifacts_zip)
    return artifacts_zip


def read_environment():
    """
    reads the environment variables and sets them in a dictionary
    :return: an environment dictionary with the required values; or an exception will be raised
    """

    print("Reading Environment...")

    # Initialize Environment Dictionary
    environment_dict = {
        "s3_artifacts_name": os.environ['S3_ARTIFACTS_NAME'],
        "s3_website_name": os.environ['S3_WEBSITE_NAME'],
        "sns_topic_arn": os.environ['SNS_TOPIC_ARN']
    }

    for key, value in environment_dict.items():
        print(f"'{key}' : '{value}'")

    # Validate Environment Variables
    if not environment_dict["s3_artifacts_name"]:
        msg = "Environment Variable: 'S3_ARTIFACTS_NAME' is Required!"
        print(msg)
        error(msg)

    if not environment_dict["s3_website_name"]:
        msg = "Environment Variable: 'S3_WEBSITE_NAME' is Required!"
        print(msg)
        error(msg)

    if not environment_dict["sns_topic_arn"]:
        msg = "Environment Variable: 'SNS_TOPIC_ARN' is Required!"
        print(msg)
        error(msg)

    return environment_dict


def read_resources(event, environment_dict):
    """
    reads the aws resources and sets them in a dictionary
    :param event: the Lambda invocation event
    :param environment_dict: the environment variables provided to the function
    :return: the aws resources found
    """

    print("Reading Resources...")

    s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
    sns = boto3.resource('sns')

    # Initialize Resources Dictionary
    resources_dict = {
        "codepipeline_job": event.get("CodePipeline.job"),
        "s3_artifacts": s3.Bucket(environment_dict["s3_artifacts_name"]),
        "s3_website": s3.Bucket(environment_dict["s3_website_name"]),
        "sns_topic": sns.Topic(environment_dict["sns_topic_arn"])
    }

    for key, value in resources_dict.items():
        print(f"'{key}' : '{value}'")

    return resources_dict


def handler(event, context):
    """
    deploys artifacts stored in S3 to another S3 bucket hosting a website with SNS topics and CodePipeline integration
    :param event: the Lambda event to process
    :param context: the Context in which this Lambda function was invoked
    :return: an object with 200 status code or an exception
    """

    print(f"'context':{context}")
    print(f"'event':{event}")

    environment = {}
    resources = {}

    try:

        environment = read_environment()
        # keys:
        #   s3_artifacts_name
        #   s3_website_name
        #   sns_topic_arn

        resources = read_resources(event, environment)
        # keys:
        #   codepipeline_job
        #   s3_artifacts
        #   s3_website
        #   sns_topic

        artifacts = read_artifacts(environment, resources)

        # Extract and Upload Each File inside Zip
        print("Extracting Artifacts...")
        with zipfile.ZipFile(artifacts) as art:
            for name in art.namelist():
                obj = art.open(name)
                upload_args = {'ContentType': mimetypes.guess_type(name)[0]}
                resources["s3_website"].upload_fileobj(obj, name, ExtraArgs=upload_args)
                resources["s3_website"].Object(name).Acl().put(ACL='public-read')

        # Publish Success to the SNS Topic
        print("Publishing to SNS...")
        success_message = f"Bucket: {environment['s3_website_name']}\nStatus: Success"
        resources["sns_topic"].publish(Subject='Code Deploy Success', Message=success_message)

        # Set CodePipeline Job to Success
        if resources["codepipeline_job"]:
            print("Publishing to CodePipeline...")
            pipeline = boto3.client('codepipeline')
            pipeline.put_job_success_result(jobId=resources["codepipeline_job"]["id"])

        return {'statusCode': 200}

    except Exception as e:

        codepipeline_job = resources["codepipeline_job"] if "codepipeline_job" in resources else None
        sns_topic = resources["sns_topic"] if "sns_topic" in resources else None
        s3_website_name = environment["s3_website_name"] if "s3_website_name" in environment else None
        error(str(e), codepipeline_job, sns_topic, s3_website_name)
