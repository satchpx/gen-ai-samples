import os
import json
import boto3
import botocore
import streamlit as st
from typing import Optional
from botocore.config import Config
import openai
from apikey import apikey
from langchain.llms import OpenAI


# Use Instance role instead
# os.environ['AWS_PROFILE'] = 'xxx'
os.environ['OPENAI_API_KEY'] = apikey


# Functions for OpenAI function calling
def get_account_id():
    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]
    return account_id

def build_kms_policy_for_cloudtrail(account_id):
    policy = {
        "Version": "2012-10-17",
        "Id": "Key policy created by CloudTrail",
        "Statement": [
            {
            "Sid": "Enable IAM User Permissions",
            "Effect": "Allow",
            "Principal": {
                "AWS": [
                "arn:aws:iam::account_id:root",
                "arn:aws:sts::account_id:assumed-role/Admin/adminUser"
                ]
            },
            "Action": "kms:*",
            "Resource": "*"
            },
            {
            "Sid": "Allow CloudTrail to encrypt logs",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "kms:GenerateDataKey*",
            "Resource": "*",
            "Condition": {
                "StringLike": {
                "kms:EncryptionContext:aws:cloudtrail:arn": "arn:aws:cloudtrail:*:account_id:trail/*"
                }
            }
            },
            {
            "Sid": "Allow CloudTrail to describe key",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "kms:DescribeKey",
            "Resource": "*"
            },
            {
            "Sid": "Allow principals in the account to decrypt log files",
            "Effect": "Allow",
            "Principal": {
                "AWS": "*"
            },
            "Action": [
                "kms:Decrypt",
                "kms:ReEncryptFrom"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                "kms:CallerAccount": "account_id"
                },
                "StringLike": {
                "kms:EncryptionContext:aws:cloudtrail:arn": "arn:aws:cloudtrail:*:account_id:trail/*"
                }
            }
            }
        ]
    }

    return policy

def list_cloudtrails():
    client = boto3.client('cloudtrail')
    cloudtrails = client.list_trails(
        NextToken='string'
    )
    return cloudtrails

def create_kms_key():
    client = boto3.client('kms')
    account_id = get_account_id()
    resp = client.create_key(policy=build_kms_policy_for_cloudtrail(account_id=account_id))
    key_id = resp['KeyMetadata']['KeyId']
    key_arn = resp['KeyMetadata']['Arn']
    return key_arn

def enable_encryption_on_cloudtrail(cloudtrail):
    client = boto3.client('cloudtrail')
    # Create a KMS key
    key_arn = create_kms_key()
    
    # Update trail
    try:
        resp = client.update_trail(Name=cloudtrail, KmsKeyId=key_arn)
    except botocore.exceptions.ClientError as error:
        print("An error occurred")
        raise(error)
    return

if __name__ == '__main__':
    st.title('Cloud Security Analytics Workshop 2023 - Enhance Security Findings with Generative AI')
    uploaded_file = st.file_uploader("Upload your finding(s) JSON file here...", type="json")

    prompt = st.text_input('This tool analyzes findings in the uploaded json file. Ask any related questions below')

    if uploaded_file:
        # Run inference
        # template with a placeholder for json data

        bytes_data = uploaded_file.read()
        json_data = json.loads(bytes_data)
        # st.write(json_data) #debugging

        template = """
        Human: As security specialists, we want to identify threats and incidents and take proactive remedial measures to respond to these threats. 
        We review threats identified by Amazon GuardDuty and want prescriptive guidance on how to fix these issues. The recommendations should be actionable and fixable by the user. 
        Here is a finding from GuarDuty. After going through the json file, provide a detailed description of the finding to the user. Then provide step-by-step instructions for an actionable remedy. 
        <<JSON_DATA>>

        Assistant: 
        """

        prompt = template.replace("<<JSON_DATA>>", json.dumps(json_data))

        llm = OpenAI(temperature=0.9)

        result = llm.predict(prompt)
        st.write(result)

        ## Add auto fix code below
        st.write("If the remedial action look good to you, I can attempt to fix it. Would you like me to?")
        st.button("No", type="primary")
        if st.button("Yes! Fix it!"):
            st.write("Okay.. Fixing it...")
            # Call the auto-fix function here
        else:
            st.write("Waiting for your command!")
#    else:
        # Get findings from Security Hub
        # findings_raw = os.pope(f'aws securityhub get-findings --filters {filterstr} --sort-criteria {sortcriteria} --page-size 100 --max-items 1000')
        # findings_json = json.loads(findings_raw.read())['Findings']

        # Ref: https://github.com/aws-samples/aws-security-hub-findings-historical-export/blob/main/security_hub_export_cdk/lambdas/load_sh_finding/get_sh_finding.py
