"""
DynamoDB Handler
Manages document data storage and retrieval
"""
import boto3
from datetime import datetime
from decimal import Decimal
import json


class DynamoDBHandler:
    """Handle DynamoDB operations for document storage."""
    
    def __init__(self, table_name):
        """
        Initialize DynamoDB handler.
        
        Args:
            table_name: Name of the DynamoDB table
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
    
    def save_document(self, document_id, timestamp, extracted_data, 
                     source_bucket, source_key, status='completed'):
        """
        Save extracted document data to DynamoDB.
        
        Args:
            document_id: Unique document identifier
            timestamp: Upload timestamp
            extracted_data: Dictionary with fields, tables, and raw text
            source_bucket: S3 bucket name
            source_key: S3 object key
            status: Processing status
        """
        try:
            item = {
                'document_id': document_id,
                'upload_timestamp': timestamp,
                'status': status,
                'source_bucket': source_bucket,
                'source_key': source_key,
                'processed_at': datetime.utcnow().isoformat(),
                'extracted_data': self._convert_to_dynamo_format(extracted_data)
            }
            
            self.table.put_item(Item=item)
            
            print(f"Saved document {document_id} to DynamoDB")
            return True
            
        except Exception as e:
            print(f"Error saving to DynamoDB: {str(e)}")
            raise
    
    def update_status(self, document_id, timestamp, status, metadata=None, error=None):
        """
        Update document processing status.
        
        Args:
            document_id: Document identifier
            timestamp: Timestamp
            status: New status (processing, completed, failed)
            metadata: Optional metadata dictionary
            error: Optional error message
        """
        try:
            update_expression = "SET #status = :status, updated_at = :updated_at"
            expression_values = {
                ':status': status,
                ':updated_at': datetime.utcnow().isoformat()
            }
            expression_names = {
                '#status': 'status'
            }
            
            if metadata:
                update_expression += ", metadata = :metadata"
                expression_values[':metadata'] = self._convert_to_dynamo_format(metadata)
            
            if error:
                update_expression += ", error_message = :error"
                expression_values[':error'] = error
            
            self.table.update_item(
                Key={
                    'document_id': document_id,
                    'upload_timestamp': timestamp
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_names,
                ExpressionAttributeValues=expression_values
            )
            
            print(f"Updated status for {document_id} to {status}")
            return True
            
        except Exception as e:
            print(f"Error updating status: {str(e)}")
            raise
    
    def get_document(self, document_id, timestamp):
        """
        Retrieve document by ID and timestamp.
        
        Args:
            document_id: Document identifier
            timestamp: Upload timestamp
            
        Returns:
            dict: Document data or None if not found
        """
        try:
            response = self.table.get_item(
                Key={
                    'document_id': document_id,
                    'upload_timestamp': timestamp
                }
            )
            
            return response.get('Item')
            
        except Exception as e:
            print(f"Error retrieving document: {str(e)}")
            return None
    
    def query_by_status(self, status, limit=10):
        """
        Query documents by status.
        
        Args:
            status: Status to query (processing, completed, failed)
            limit: Maximum number of results
            
        Returns:
            list: List of documents
        """
        try:
            response = self.table.query(
                IndexName='status-index',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={':status': status},
                Limit=limit,
                ScanIndexForward=False
            )
            
            return response.get('Items', [])
            
        except Exception as e:
            print(f"Error querying by status: {str(e)}")
            return []
    
    def _convert_to_dynamo_format(self, data):
        """
        Convert Python data types to DynamoDB-compatible format.
        Specifically handles float to Decimal conversion.
        """
        if isinstance(data, dict):
            return {k: self._convert_to_dynamo_format(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_to_dynamo_format(item) for item in data]
        elif isinstance(data, float):
            return Decimal(str(data))
        else:
            return data
    
    def _convert_from_dynamo_format(self, data):
        """
        Convert DynamoDB format back to Python types.
        Specifically handles Decimal to float conversion.
        """
        if isinstance(data, dict):
            return {k: self._convert_from_dynamo_format(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._convert_from_dynamo_format(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)
        else:
            return data
