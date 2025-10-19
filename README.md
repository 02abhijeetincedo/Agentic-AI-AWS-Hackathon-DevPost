Agentic Expense Guardian is an intelligent, serverless AI agent built on AWS to empower users with financial management through natural language processing.
It processes queries to track expenses, calculate savings, generate personalized budget tips, and suggest investments based on savings history.
The agent leverages AWS Bedrock with Anthropic Claude for agentic reasoning, AWS Lambda for processing, AWS S3 for storage, and API Gateway for user interaction.
Key Features

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
