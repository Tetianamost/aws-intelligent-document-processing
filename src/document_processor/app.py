"""
Document Processing Lambda Function
Extracts data from documents using Amazon Textract
"""
import json
import os
import boto3
from datetime import datetime
from decimal import Decimal
import traceback
from utils.textract_parser import TextractParser
from utils.dynamo_handler import DynamoDBHandler

s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
sns_client = boto3.client('sns')

TABLE_NAME = os.environ.get('TABLE_NAME')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')
BUCKET_NAME = os.environ.get('BUCKET_NAME')

parser = TextractParser()
db_handler = DynamoDBHandler(TABLE_NAME)


def lambda_handler(event, context):
    """
    Main Lambda handler triggered by S3 upload events.
    
    Args:
        event: S3 event notification
        context: Lambda context
        
    Returns:
        dict: Response with status and message
    """
    print(f"Event received: {json.dumps(event)}")
    
    try:
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        document_key = record['s3']['object']['key']
        file_size = record['s3']['object']['size']
        
        print(f"Processing document: {document_key} ({file_size} bytes)")
        
        document_id = generate_document_id(document_key)
        upload_timestamp = datetime.utcnow().isoformat()
        
        db_handler.update_status(
            document_id=document_id,
            timestamp=upload_timestamp,
            status='processing',
            metadata={
                'source_bucket': bucket,
                'source_key': document_key,
                'file_size': file_size
            }
        )
        
        if file_size > 5 * 1024 * 1024:
            return process_large_document(bucket, document_key, document_id, upload_timestamp)
        else:
            return process_document_sync(bucket, document_key, document_id, upload_timestamp)
            
    except Exception as e:
        error_message = f"Error processing document: {str(e)}"
        print(error_message)
        print(traceback.format_exc())
        
        send_notification(
            subject="Document Processing Failed",
            message=error_message,
            status="error"
        )
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_message})
        }


def process_document_sync(bucket, document_key, document_id, upload_timestamp):
    """
    Process document synchronously using Textract AnalyzeDocument.
    Used for documents under 5MB.
    """
    print(f"Starting synchronous processing for {document_key}")
    
    try:
        # Use S3 reference for synchronous processing (more efficient)
        response = textract_client.analyze_document(
            Document={
                'S3Object': {
                    'Bucket': bucket,
                    'Name': document_key
                }
            },
            FeatureTypes=['FORMS', 'TABLES']
        )
        
        print(f"Textract analysis completed. Blocks found: {len(response['Blocks'])}")
        
        extracted_data = parser.parse_response(response)
        
        print(f"Extracted data: {json.dumps(extracted_data, default=str)[:500]}...")
        
        db_handler.save_document(
            document_id=document_id,
            timestamp=upload_timestamp,
            extracted_data=extracted_data,
            source_bucket=bucket,
            source_key=document_key,
            status='completed'
        )
        
        move_to_processed(bucket, document_key)
        
        send_notification(
            subject="Document Processed Successfully",
            message=f"Document {document_key} has been processed.\n"
                   f"Document ID: {document_id}\n"
                   f"Fields extracted: {len(extracted_data.get('fields', {}))}\n"
                   f"Tables found: {len(extracted_data.get('tables', []))}",
            status="success",
            document_id=document_id
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Document processed successfully',
                'document_id': document_id,
                'fields_count': len(extracted_data.get('fields', {})),
                'tables_count': len(extracted_data.get('tables', []))
            })
        }
        
    except Exception as e:
        error_message = f"Error in synchronous processing: {str(e)}"
        print(error_message)
        
        db_handler.update_status(
            document_id=document_id,
            timestamp=upload_timestamp,
            status='failed',
            error=error_message
        )
        
        raise


def process_large_document(bucket, document_key, document_id, upload_timestamp):
    """
    Process large documents asynchronously using Textract StartDocumentAnalysis.
    Used for documents over 5MB.
    
    Note: This requires additional setup for async processing.
    For this tutorial, we'll keep it simple and process synchronously.
    """
    print(f"Large document detected: {document_key}")
    
    return process_document_sync(bucket, document_key, document_id, upload_timestamp)


def generate_document_id(document_key):
    """
    Generate a unique document ID from the S3 key.
    """
    import hashlib
    from datetime import datetime
    
    filename = document_key.split('/')[-1].split('.')[0]
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    
    hash_input = f"{document_key}_{timestamp}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    return f"{filename}_{timestamp}_{hash_value}"


def move_to_processed(bucket, document_key):
    """
    Move processed document from incoming/ to processed/ folder.
    """
    try:
        new_key = document_key.replace('incoming/', 'processed/')
        
        s3_client.copy_object(
            CopySource={'Bucket': bucket, 'Key': document_key},
            Bucket=bucket,
            Key=new_key
        )
        
        s3_client.delete_object(Bucket=bucket, Key=document_key)
        
        print(f"Moved document from {document_key} to {new_key}")
        
    except Exception as e:
        print(f"Warning: Could not move document: {str(e)}")


def send_notification(subject, message, status, document_id=None):
    """
    Send SNS notification about processing status.
    """
    try:
        notification_message = {
            'subject': subject,
            'message': message,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if document_id:
            notification_message['document_id'] = document_id
        
        sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=subject,
            Message=json.dumps(notification_message, indent=2)
        )
        
        print(f"Notification sent: {subject}")
        
    except Exception as e:
        print(f"Warning: Could not send notification: {str(e)}")


def convert_decimals(obj):
    """
    Convert Decimal objects to float for JSON serialization.
    """
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj
