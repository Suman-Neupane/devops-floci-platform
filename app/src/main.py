import os
import uuid
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from src.aws_client import get_s3_client, get_dynamodb_resource, get_sqs_client

app = FastAPI(
    title="CloudOps Floci Document Service",
    description="Microservice processing document uploads using local Floci AWS emulator (S3, DynamoDB, SQS)",
    version="1.0.0",
)

# Instrument Prometheus metrics
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "user-documents-bucket")
DYNAMODB_TABLE = os.getenv("DYNAMODB_TABLE_NAME", "document-metadata")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "document-processing-events")

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Healthcheck testing connectivity to Floci AWS Emulator."""
    try:
        s3 = get_s3_client()
        s3.list_buckets()
        return {"status": "healthy", "floci_connection": "active"}
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "error": str(e)},
        )

@app.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...)):
    """Uploads a file to Floci S3, saves metadata to DynamoDB, and emits event to SQS."""
    doc_id = str(uuid.uuid4())
    s3_key = f"uploads/{doc_id}_{file.filename}"
    file_content = await file.read()
    file_size = len(file_content)
    upload_time = datetime.utcnow().isoformat()

    try:
        # 1. Upload to Floci S3
        s3 = get_s3_client()
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=s3_key,
            Body=file_content,
            ContentType=file.content_type,
        )

        # 2. Save metadata in Floci DynamoDB
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(
            Item={
                "document_id": doc_id,
                "filename": file.filename,
                "s3_key": s3_key,
                "file_size_bytes": file_size,
                "content_type": file.content_type,
                "uploaded_at": upload_time,
            }
        )

        # 3. Publish event to Floci SQS
        sqs = get_sqs_client()
        queue_url_response = sqs.get_queue_url(QueueName=SQS_QUEUE_NAME)
        queue_url = queue_url_response["QueueUrl"]
        
        event_message = {
            "event_type": "DOCUMENT_UPLOADED",
            "document_id": doc_id,
            "filename": file.filename,
            "s3_key": s3_key,
            "timestamp": upload_time,
        }
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(event_message),
        )

        return {
            "message": "Document processed successfully",
            "document_id": doc_id,
            "s3_key": s3_key,
            "file_size": file_size,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process upload: {str(e)}",
        )

@app.get("/documents")
def list_documents():
    """Retrieve all document metadata records from Floci DynamoDB."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE)
        response = table.scan()
        return {"documents": response.get("Items", []), "count": len(response.get("Items", []))}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list documents: {str(e)}",
        )

@app.get("/documents/{document_id}")
def get_document(document_id: string if False else str):
    """Retrieve specific document metadata by ID."""
    try:
        dynamodb = get_dynamodb_resource()
        table = dynamodb.Table(DYNAMODB_TABLE)
        response = table.get_item(Key={"document_id": document_id})
        item = response.get("Item")
        if not item:
            raise HTTPException(status_code=404, detail="Document not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching document: {str(e)}",
        )
