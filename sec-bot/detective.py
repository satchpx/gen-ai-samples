import os
import json
import boto3
import streamlit as st

os.environ['AWS_PROFILE'] = 'xxx'

st.title('Get help on your security findings here')
uploaded_file = st.file_uploader("Upload your file here...", type="json")

prompt = st.text_input('This tool analyzes findings in the uploaded json file. Ask any related questions here')

if uploaded_file:
    # Run inference
    print("Nothing here for now")
else:
    findings_raw = os.pope(f'aws securityhub get-findings --filters {filterstr} --sort-criteria {sortcriteria} --page-size 100 --max-items 1000')
    findings_json = json.loads(findings_raw.read())['Findings']

    # https://github.com/aws-samples/aws-security-hub-findings-historical-export/blob/main/security_hub_export_cdk/lambdas/load_sh_finding/get_sh_finding.py