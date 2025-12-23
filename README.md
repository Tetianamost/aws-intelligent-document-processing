# 🚀 AWS Intelligent Document Processing with Amazon Textract

[![AWS](https://img.shields.io/badge/AWS-Serverless-orange)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A production-ready, serverless document processing system built with AWS AI services. Extract text, tables, and form data from documents automatically using Amazon Textract, Lambda, and DynamoDB.

**Perfect for:** Learning AWS AI services, building portfolios, AWS certifications, or implementing automated document workflows.

## 🎯 What This Project Does

- ✅ **Automatic document processing** - Upload PDFs/images to S3, get structured data automatically
- ✅ **AI-powered extraction** - Uses Amazon Textract to extract text, tables, and form fields
- ✅ **Serverless architecture** - No servers to manage, scales automatically
- ✅ **Complete infrastructure** - One-command deployment using AWS SAM
- ✅ **Production-ready** - Includes error handling, monitoring, and notifications
- ✅ **Cost-optimized** - Pay only for what you use (~$16/month for 1000 documents)

## 🏗️ Architecture

```
User Upload → S3 Bucket → Lambda (Textract) → DynamoDB → SNS Notification
```

**AWS Services Used:**

- **Amazon S3** - Document storage with lifecycle policies
- **AWS Lambda** - Serverless compute for processing
- **Amazon Textract** - AI-powered document analysis
- **Amazon DynamoDB** - NoSQL database for extracted data
- **Amazon SNS** - Email notifications
- **AWS CloudWatch** - Monitoring and alarms
- **AWS X-Ray** - Distributed tracing

## ✅ Prerequisites

Before you begin, ensure you have:

1. **AWS Account** - [Create one here](https://aws.amazon.com/free/)
2. **AWS CLI** - [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
3. **AWS SAM CLI** - [Installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
4. **Python 3.11+** - [Download here](https://www.python.org/downloads/)

### Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter your default region (e.g., us-east-1)
# Enter your default output format (json)
```

### Required IAM Permissions

Your IAM user needs the following **AWS Managed Policies** to deploy this application.

**Recommended Approach: Use IAM User Groups**

1. **Create an IAM User Group** (e.g., `tania-builder-saml` or `sam-deployers`)
   - Go to IAM → User groups → Create group
   - Give it a descriptive name

2. **Attach the following managed policies to the group:**
   - `AWSCloudFormationFullAccess` - Create and manage CloudFormation stacks
   - `AWSLambda_FullAccess` - Create and manage Lambda functions
   - `IAMFullAccess` - Create IAM roles for Lambda execution
   - `AmazonS3FullAccess` - Manage S3 buckets and objects
   - `AmazonDynamoDBFullAccess` - Create and manage DynamoDB tables
   - `AmazonSNSFullAccess` - Create and manage SNS topics
   - `AmazonSQSFullAccess` - Create Dead Letter Queue
   - `CloudWatchLogsFullAccess` - Create and manage log groups
   - `AWSXRayFullAccess` - Enable X-Ray tracing

3. **Add your IAM user to the group**
   - IAM → Users → [Your User] → Groups → Add user to groups
   - Select the group you created

**Why use groups?** This is AWS best practice - it makes it easier to manage permissions for multiple users and maintain consistency.

**Alternative:** You can attach these policies directly to your IAM user, but using groups is recommended for better permission management.

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/Tetianamost/aws-intelligent-document-processing.git
cd aws-intelligent-document-processing

# Run the setup script
./setup.sh
```

The script will:

- Check all prerequisites
- Prompt for your email and configuration
- Build and deploy the application
- Display your S3 bucket name and usage commands

### Option 2: Manual Setup

```bash
# 1. Build the application
sam build

# 2. Deploy with guided prompts
sam deploy --guided

# You'll be prompted for:
# - Stack name: e.g., doc-processing-dev
# - AWS Region: e.g., us-east-1
# - NotificationEmail: your email address
# - Confirm changes: Y
# - Allow SAM CLI IAM role creation: Y
# - Save arguments to config file: Y
```

### 3. Confirm SNS Email Subscription

Check your email and **confirm the SNS subscription** to receive notifications.

### 4. Get Your S3 Bucket Name

```bash
aws cloudformation describe-stacks \
    --stack-name doc-processing-dev \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentBucket`].OutputValue' \
    --output text
```

## 📄 Sample Documents

The `sample_documents/` directory contains example documents for testing:

- **simple-invoice.png** - Business invoice with itemized services and calculations (✅ **Works perfectly**)
- **tax-form.png** - IRS Form 1040 converted to PNG (✅ **Works perfectly** - 1,412 blocks extracted)
- **sample-invoice.pdf** - IRS Form 1040 as PDF (❌ **Fails** - PDF format incompatible)
- **filled-invoice.pdf** - PDF invoice generated with reportlab (❌ **Fails** - PDF format incompatible)

### ⚠️ Important: Document Format Compatibility

**Textract works best with:**

- **PNG, JPG, TIFF images** - Most reliable format
- **Scanned PDFs** - PDFs created from scanned documents
- **Native PDFs** - PDFs from tools like Adobe, Microsoft Office

**May not work:**

- PDFs generated by some Python libraries (reportlab, fpdf) - these may use unsupported internal formats
- Heavily compressed or encrypted PDFs

**Recommendation:** If you're programmatically generating documents for Textract, create them as PNG/JPG images rather than PDFs to ensure compatibility.

**Great document sources for testing:**

- Your own receipts or invoices
- Bank statements
- Medical lab results
- Tax forms (W-2, 1040, etc.)

## 📝 Usage Examples

### Upload a Document for Processing

```bash
# Upload a PDF
aws s3 cp your-document.pdf s3://YOUR-BUCKET-NAME/incoming/

# Upload a PNG image
aws s3 cp your-image.png s3://YOUR-BUCKET-NAME/incoming/
```

**What happens next:**

1. S3 triggers Lambda automatically
2. Lambda calls Textract to analyze the document
3. Extracted data is saved to DynamoDB
4. Document is moved to `processed/` folder
5. You receive an email notification

### Query Extracted Data

```bash
# View all processed documents
aws dynamodb scan \
    --table-name doc-processing-dev-documents \
    --max-items 5

# Query by document ID
aws dynamodb get-item \
    --table-name doc-processing-dev-documents \
    --key '{"document_id": {"S": "your-doc-id"}, "upload_timestamp": {"S": "2024-01-15T10:30:00"}}'
```

### View Logs

```bash
# View Lambda logs
sam logs --stack-name doc-processing-dev --tail

# View specific function logs
aws logs tail /aws/lambda/doc-processing-dev-processor --follow
```

## 📁 Project Structure

```
aws-intelligent-document-processing/
├── README.md                           # This file
├── template.yaml                       # SAM/CloudFormation template
├── setup.sh                            # Automated setup script
├── .gitignore                          # Git ignore rules
│
├── src/
│   └── document_processor/
│       ├── app.py                      # Main Lambda handler
│       ├── requirements.txt            # Python dependencies
│       └── utils/
│           ├── __init__.py
│           ├── textract_parser.py      # Textract response parser
│           └── dynamo_handler.py       # DynamoDB operations
│
├── sample_documents/                   # Test documents
├── tests/                              # Unit and integration tests
└── docs/                               # Additional documentation
```

## 💰 Cost Estimation

Costs for processing **1,000 documents per month** in `us-east-1`:

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **Amazon S3** | 10GB storage + 1K PUT/GET | $0.25 |
| **AWS Lambda** | 1K invocations × 30s × 512MB | $0.10 |
| **Amazon Textract** | 1K pages analyzed | $15.00 |
| **DynamoDB** | 1K writes + 5K reads | $0.30 |
| **Amazon SNS** | 1K notifications | $0.50 |
| **CloudWatch Logs** | 1GB logs | $0.50 |
| **TOTAL** | | **~$16.65** |

**Free Tier Benefits:**

- Lambda: First 1M requests/month free
- DynamoDB: 25GB storage + 25 RCU/WCU free
- S3: First 5GB free

## 🐛 Troubleshooting

### Issue: SAM build fails

```bash
# Make sure you have Python 3.11+
python3 --version

# Install SAM CLI
pip install aws-sam-cli

# Try building with verbose output
sam build --use-container --debug
```

### Issue: Lambda timeout errors

Increase timeout in `template.yaml`:

```yaml
Globals:
  Function:
    Timeout: 600  # 10 minutes
```

### Issue: "Access Denied" errors

```bash
# Verify IAM permissions
aws sts get-caller-identity

# Ensure your AWS credentials have necessary permissions
```

### Issue: Not receiving SNS notifications

1. Check spam folder
2. Confirm SNS subscription in AWS Console
3. Verify email in `template.yaml` is correct

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📚 Learning Resources

- [Amazon Textract Documentation](https://docs.aws.amazon.com/textract/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

## 📄 License

This project is licensed under the MIT License.

## 📞 Contact

- **GitHub Issues**: [Report bugs or request features](https://github.com/Tetianamost/aws-intelligent-document-processing/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/Tetianamost/aws-intelligent-document-processing/discussions)

---

⭐ **Found this helpful?** Star the repo and share with others learning AWS!

🐛 **Found a bug?** Open an issue and let's fix it together!
