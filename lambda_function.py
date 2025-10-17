import json
import boto3
import os
import datetime
from dateutil.relativedelta import relativedelta

bedrock = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')

BUCKET_NAME = 'job-agent-bucket'  
DEFAULT_INCOME = 50000  

def get_monthly_summary(month_key):
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=f"savings/{month_key}/summary.json")
        return json.loads(response['Body'].read())
    except s3.exceptions.NoSuchKey:
        return None

def list_monthly_expenses(month_key):
    expenses = []
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=f"expenses/{month_key}/")
        for obj in response.get('Contents', []):
            data = s3.get_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            expenses.append(json.loads(data['Body'].read()))
        return expenses
    except:
        return []

def lambda_handler(event, context):
    try:
        body = event.get('body', '{}')
        if isinstance(body, str):
            body = json.loads(body)
        user_query = body.get('query', '')
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON format in request'}),
            'headers': {'Content-Type': 'application/json'}
        }

    if not user_query:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No query provided'}),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        
        current_date = datetime.datetime.now()
        yesterday = (current_date - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        current_month = current_date.strftime('%Y-%m')

        
        prompt = (
            f"User query: '{user_query}'. "
            "Do the following in English: "
            "1. Extract expense details (date, item, amount) in JSON format. "
            f"If date is not provided, assume yesterday ({yesterday}). "
            "For complex queries (e.g., EMI or down payment), consider the amount as the total expense or down payment. "
            "2. Categorize the expense (e.g., Food, Transport, Finance). "
            "3. Provide budget tips in English. "
            "4. Create a savings plan table in English with columns: Step Number, Action, Estimated Savings (in INR), Timeline. "
            "5. If user has savings from past months, suggest investments (gold, shares, land, property) based on total savings. "
            "Output strictly in JSON format, with no extra text, comments, or explanations outside the JSON: "
            "{\"expense\": {\"date\": \"YYYY-MM-DD\", \"item\": \"item_name\", \"amount\": number}, "
            "\"category\": \"category_name\", "
            "\"budget_tips\": \"English tips\", "
            "\"savings_plan\": [{\"step_number\": number, \"action\": \"action_description\", \"estimated_savings\": number, \"timeline\": \"timeline_description\"}], "
            "\"investment_suggestions\": \"Investment suggestions in English based on savings\"}"
        )
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
                "messages": [{"role": "user", "content": prompt}]
            })
        )

        # Bedrock response 
        response_body = response['body'].read().decode('utf-8')
        try:
            result = json.loads(response_body)['content'][0]['text']
            result = json.loads(result)
        except json.JSONDecodeError as e:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': f'Failed to parse Claude response: {str(e)}', 'raw_response': response_body}),
                'headers': {'Content-Type': 'application/json'}
            }

        expense_data = result.get('expense', {})
        category = result.get('category', 'Unknown')
        budget_tips = result.get('budget_tips', 'No tips provided')
        savings_plan = result.get('savings_plan', [])
        investment_suggestions = result.get('investment_suggestions', 'No investment suggestions')

        if not expense_data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Could not extract expense details'}),
                'headers': {'Content-Type': 'application/json'}
            }

        # Save in S3 Bucket
        month_key = expense_data['date'][:7]  # YYYY-MM
        file_key = f"expenses/{month_key}/{expense_data['date']}.json"
        s3.put_object(Bucket=BUCKET_NAME, Key=file_key, Body=json.dumps(expense_data))

        # Monthly salary updstion 
        expenses = list_monthly_expenses(month_key)
        total_expenses = sum(exp['amount'] for exp in expenses) + expense_data['amount']
        savings = DEFAULT_INCOME - total_expenses
        summary = {
            'month': month_key,
            'total_expenses': total_expenses,
            'income': DEFAULT_INCOME,
            'savings': max(savings, 0),
            'invested': False
        }
        s3.put_object(Bucket=BUCKET_NAME, Key=f"savings/{month_key}/summary.json", Body=json.dumps(summary))

        # Past 5-6 months chekers
        total_savings = 0
        months_checked = 0
        for i in range(6):
            past_month = (current_date - relativedelta(months=i)).strftime('%Y-%m')
            summary = get_monthly_summary(past_month)
            if summary and not summary.get('invested', False):
                total_savings += summary.get('savings', 0)
                months_checked += 1

        if months_checked >= 5 and total_savings > 0:
            investment_prompt = (
                f"User has saved {total_savings} INR over {months_checked} months. "
                "Suggest investment options (gold, shares, land, property) in English with estimated returns and risks. "
                "Output strictly in JSON: {\"investment_suggestions\": \"English suggestions\"}"
            )
            try:
                investment_response = bedrock.invoke_model(
                    modelId='anthropic.claude-3-sonnet-20240229-v1:0',
                    contentType='application/json',
                    accept='application/json',
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 500,
                        "messages": [{"role": "user", "content": investment_prompt}]
                    })
                )
                investment_result = json.loads(investment_response['body'].read().decode('utf-8'))['content'][0]['text']
                investment_suggestions = json.loads(investment_result).get('investment_suggestions', investment_suggestions)
            except Exception as e:
                investment_suggestions = f"Investment suggestion error: {str(e)}"

        # Analysis aur savings plan ko S3 me save karenge
        report_key = f"reports/{month_key}/{expense_data['date']}.json"
        s3.put_object(Bucket=BUCKET_NAME, Key=report_key, Body=json.dumps({
            'category': category,
            'budget_tips': budget_tips,
            'savings_plan': savings_plan,
            'investment_suggestions': investment_suggestions
        }))

        # Investment suggestions history save karenge
        if total_savings > 0:
            investment_key = f"investments/{expense_data['date']}.json"
            s3.put_object(Bucket=BUCKET_NAME, Key=investment_key, Body=json.dumps({
                'total_savings': total_savings,
                'months_checked': months_checked,
                'investment_suggestions': investment_suggestions
            }))

        return {
            'statusCode': 200,
            'body': json.dumps({
                'category': category,
                'budget_tips': budget_tips,
                'savings_plan': savings_plan,
                'investment_suggestions': investment_suggestions
            }),
            'headers': {'Content-Type': 'application/json'}
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }