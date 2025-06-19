import boto3
import json

def call_bedrock(system_prompt, user_prompt):
    # Initialize the Bedrock client
    bedrock_client = boto3.client(
        service_name='bedrock-runtime',
        region_name='eu-north-1',  # Replace with your AWS region
    )

    # Define the model ID and input payload
    model_id = "eu.amazon.nova-micro-v1:0"  # Replace with the specific model ID you want to invoke

    system_prompts = [
        {
            "text": f"""{system_prompt}"""    
            
        }
    ]

    messages = [
        {
            "role": "user", 
            "content": [
                {
                    "text": f"""{user_prompt}"""
                }
            ]
        }
    ]

    inference_config = {
        
        "top_p": 0.9,
        
        "temperature": 0.1
    }

    request_body = {
        
        "messages": messages,
        "system": system_prompts,
        "inferenceConfig": inference_config
    }

    # Invoke the model
    try:
        # Invoke the model
        response = bedrock_client.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response['body'].read())
        print("Full Response:", json.dumps(response_body, indent=2))
        #j=json.dumps(response_body, indent=2)
        print("Model Response:",response_body["output"]["message"]["content"][0]["text"])

        return response_body["output"]["message"]["content"][0]["text"]

    except Exception as e:
        print(f"Error invoking model: {str(e)}")
        return "Error invoking model: {str(e)}"