
Agentic Expense Guardian is an intelligent, serverless AI agent built on AWS to empower users with financial management through natural language processing.
It processes queries to track expenses, calculate savings, generate personalized budget tips, and suggest investments based on savings history.
The agent leverages AWS Bedrock with Anthropic Claude for agentic reasoning, AWS Lambda for processing, AWS S3 for storage, and API Gateway for user interaction.


### Project Architecture: 
                        Go to git file and open ***Expenses_Agent_structure.drawio.png*** 
                        
### Project Videos: 
                        Go to git file and open ***.mp4 files*** 

### Key Features

**Natural Language Processing:** Parses queries to extract expense details (date, item, amount) and categorize them (e.g., Food, Housing).

**Expense and Savings Tracking:** Stores expenses in S3 (expenses/YYYY-MM/), computes monthly savings (savings/YYYY-MM/), and tracks investment suggestions (investments/).

**Personalized Budget Tips:** Generates tips (e.g., "Please make food in home to save money!") for relatable financial advice.

**Investment Suggestions:** For users with 5+ months of savings, suggests diversified options (gold, shares, property) with estimated returns and risks.

**Serverless and Scalable:** Built on AWS Lambda, API Gateway, and S3, ensuring low cost (<$0.01/query at scale) and scalability.

### AWS Components:
**AWS Bedrock (Anthropic Claude-3):** Core AI for parsing queries, categorizing expenses, and generating tips and investment suggestions.

**AWS Lambda:** Serverless function to process queries, invoke Bedrock, and manage S3 operations.

**AWS API Gateway:** REST endpoint (POST /expense) for user queries.

**AWS S3:** Persistent storage with structured folders (expenses/, savings/, reports/, investments/).

**IAM Roles:** Permissions for Lambda to access S3 and Bedrock.


### Setup Instructions:
Step 1: Create an S3 Bucket
                            Set:-> Bucket name: job-agent-bucket.
                                   Region: ap-south-1.
                                   

Step 2: Create a Lambda Function
                                Set:-> Function name: resumeagent.
                                       Runtime: Python 3.11.9
                                       Region: ap-south-1.

Under Permissions, create a new IAM role (AbhijeetAgentBot):

```{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {
      "Sid": "resumeagentPolicy-001",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::876379899159:role/AbhijeetAgentBot"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:ap-south-1:876379899159:function:resumeagent"
    },
    {
      "Sid": "1da635d0-447d-58af-81a1-70e83ca4423e",
      "Effect": "Allow",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:ap-south-1:876379899159:function:resumeagent",
      "Condition": {
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:execute-api:ap-south-1:876379899159:b4ogptlmnl/*/POST/expense"
        }
      }
    }
  ]
}

```

Step 3: Copy the Lambda code from lambda_function.py from gihub and paste it into the Lambda editor.

Set General Configuration: Timeout: 60 seconds.
                           Memory: 512 MB.

Step 4: Set Up API Gateway

                          Set: API name: ExpenseAgentAPI.
                          
                               Endpoint: Regional (ap-south-1).
                               
                               Create a resource: /expense, method: POST.
                               
                               Integration: Lambda function (resumeagent).




