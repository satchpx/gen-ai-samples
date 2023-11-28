import os
import json
import boto3
import streamlit as st
from typing import Optional
from botocore.config import Config
from langchain.llms import Bedrock

# Use Instance role instead
# os.environ['AWS_PROFILE'] = 'xxx'

def get_bedrock_client(
    assumed_role: Optional[str] = None,
    endpoint_url: Optional[str] = None,
    region: Optional[str] = None,
):
    """Create a boto3 client for Amazon Bedrock, with optional configuration overrides

    Parameters
    ----------
    assumed_role :
        Optional ARN of an AWS IAM role to assume for calling the Bedrock service. If not
        specified, the current active credentials will be used.
    endpoint_url :
        Optional override for the Bedrock service API Endpoint. If setting this, it should usually
        include the protocol i.e. "https://..."
    region :
        Optional name of the AWS Region in which the service should be called (e.g. "us-east-1").
        If not specified, AWS_REGION or AWS_DEFAULT_REGION environment variable will be used.
    """
    if region is None:
        target_region = os.environ.get("AWS_REGION", os.environ.get("AWS_DEFAULT_REGION"))
    else:
        target_region = region

    print(f"Create new client\n  Using region: {target_region}")
    session_kwargs = {"region_name": target_region}
    client_kwargs = {**session_kwargs}

    profile_name = os.environ.get("AWS_PROFILE")
    if profile_name:
        print(f"  Using profile: {profile_name}")
        session_kwargs["profile_name"] = profile_name

    retry_config = Config(
        region_name=target_region,
        retries={
            "max_attempts": 10,
            "mode": "standard",
        },
    )
    session = boto3.Session(**session_kwargs)

    if assumed_role:
        print(f"  Using role: {assumed_role}", end='')
        sts = session.client("sts")
        response = sts.assume_role(
            RoleArn=str(assumed_role),
            RoleSessionName="langchain-llm-1"
        )
        print(" ... successful!")
        client_kwargs["aws_access_key_id"] = response["Credentials"]["AccessKeyId"]
        client_kwargs["aws_secret_access_key"] = response["Credentials"]["SecretAccessKey"]
        client_kwargs["aws_session_token"] = response["Credentials"]["SessionToken"]

    if endpoint_url:
        client_kwargs["endpoint_url"] = endpoint_url

    bedrock_client = session.client(
        service_name="bedrock",
        config=retry_config,
        **client_kwargs
    )

    print("boto3 Bedrock client successfully created!")
    print(bedrock_client._endpoint)
    return bedrock_client


def generate_prompt(template, json_file):
    # load json data from file
    with open(json_file, 'r') as f:
        json_data = json.load(f)
    
    # replace the placeholder in the template with actual json data
    return template.replace("<<JSON_DATA>>", json.dumps(json_data))


if __name__ == '__main__':
    st.title('Get help on your security findings here')
    uploaded_file = st.file_uploader("Upload your file here...", type="json")

    prompt = st.text_input('This tool analyzes findings in the uploaded json file. Ask any related questions here')

    st.write("If the remedial action look good to you, I can attempt to fix it. Would you like me to?")
    st.button("No", type="primary")
    if st.button("Yes! Fix it!"):
        st.write("Okay.. Fixing it...")
        # Call the auto-fix function here
    else:
        st.write("Waiting for your command!")

    if uploaded_file:
        # Run inference
        # template with a placeholder for json data

        template = """
        Human: As security specialists, we want to identify threats and incidents and take proactive remedial measures to respond to these threats. 
        We review threats identified by Amazon GuardDuty and want prescriptive guidance on how to fix these issues. The recommendations should be actionable and fixable by the user. 
        Here is a finding from GuarDuty. After going through the json file, provide a detailed description of the finding to the user. Then provide step-by-step instructions for an actionable remedy. 
        <<JSON_DATA>>

        Assistant: 
        """

        # generate the prompt
        prompt = generate_prompt(template, uploaded_file)

        inference_modifier = {
            "max_tokens_to_sample": 4096,
            "temperature": 0.5,
            "top_k": 250,
            "top_p": 1,
        }

        boto3_bedrock = get_bedrock_client(
            region=os.environ.get("AWS_DEFAULT_REGION", 'us-west-2'),
        )

        llm = Bedrock(model_id="anthropic.claude-v2", 
                    client=boto3_bedrock, 
                    model_kwargs=inference_modifier)


        result = llm.predict(prompt)
        print (result)

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
