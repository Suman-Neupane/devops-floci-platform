import os
import pytest
from fastapi.testclient import TestClient

from src.main import app, S3_BUCKET, DYNAMODB_TABLE, SQS_QUEUE_NAME
from src.aws_client import get_s3_client, get_dynamodb_resource, get_sqs_client

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_floci_resources():
    """Ensure S3, DynamoDB, and SQS exist in Floci prior to running tests."""
    s3 = get_s3_client()
    try:
        s3.create_bucket(
            Bucket=S3_BUCKET,
            CreateBucketConfiguration={"LocationConstraint": os.getenv("AWS_DEFAULT_REGION", "eu-central-1")}
        )
    except Exception:
        pass

    dynamodb = get_dynamodb_resource()
    try:
        dynamodb.create_table(
            TableName=DYNAMODB_TABLE,
            KeySchema=[{"AttributeName": "document_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "document_id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
    except Exception:
        pass

    sqs = get_sqs_client()
    try:
        sqs.create_queue(QueueName=SQS_QUEUE_NAME)
    except Exception:
        pass

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_upload_and_list_documents():
    # Test uploading a file
    file_content = b"DevOps test file content for Floci validation."
    response = client.post(
        "/upload",
        files={"file": ("test_doc.txt", file_content, "text/plain")}
    )
    assert response.status_code == 201
    data = response.json()
    assert "document_id" in data
    doc_id = data["document_id"]

    # Test listing documents
    list_res = client.get("/documents")
    assert list_res.status_code == 200
    docs = list_res.json()["documents"]
    assert any(d["document_id"] == doc_id for d in docs)

    # Test retrieving single document
    get_res = client.get(f"/documents/{doc_id}")
    assert get_res.status_code == 200
    assert get_res.json()["filename"] == "test_doc.txt"
