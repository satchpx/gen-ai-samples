# Workshops on fine-tuning large language models

## Prerequisites
Before you begin, these labs use GPU instances (listed below). Please ensure that you have the quota to satisfy the training/ inference needs.
| Instance Type | Quantity | Purpose |
| ------------- | -------- | ------- |
| ml.g5.12xlarge | 1 | Training job usage |
| ml.g5.12xlarge | 1 | Endpoint usage |
| ml.g5.24xlarge | 1 | Training job usage |
| ml.g5.24xlarge | 1 | Endpoint usage |
| ml.p3.16xlarge | 1 | Training job usage |
| ml.p3.2xlarge  | 3 | Training job usage |
| ml.p3.2xlarge  | 3 | Endpoint usage |
| ml.g4dn.8xlarge | 1 | Training job usage |

To check you existing quota values, use AWS Management Console -> `Service Quotas` -> `AWS Services` -> `Amazon Sagemaker` -> search for the instance type above in the search bar.


If you do not have the required quota, [Request quota increase](https://docs.aws.amazon.com/servicequotas/latest/userguide/request-quota-increase.html).

## Lab 1 - Instruction fine-tune a text-to-text flan-t5-base model

## Lab 2 - Fine-tune llama-2-7b on SageMaker JumpStart

## Lab 3 - Domain adaptation fine-tune gpt-j-6b

## Lab 4 - Fine tune a text-to-image Stable Diffusion model


