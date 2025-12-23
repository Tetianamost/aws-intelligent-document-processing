#!/bin/bash

# AWS Intelligent Document Processing - Quick Setup Script
# This script helps you deploy the application quickly

set -e

echo "🚀 AWS Intelligent Document Processing - Quick Setup"
echo "=================================================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi
echo "  ✓ AWS CLI installed"

# Check SAM CLI
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI not found. Please install it first:"
    echo "   https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi
echo "  ✓ SAM CLI installed"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install it first:"
    echo "   https://www.python.org/downloads/"
    exit 1
fi
echo "  ✓ Python installed"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first"
    exit 1
fi
echo "  ✓ AWS credentials configured"

echo ""
echo "✓ All prerequisites met!"
echo ""

# Get user input
read -p "Enter your email for notifications: " EMAIL
read -p "Enter stack name (default: doc-processing-dev): " STACK_NAME
STACK_NAME=${STACK_NAME:-doc-processing-dev}

read -p "Enter AWS region (default: us-east-1): " REGION
REGION=${REGION:-us-east-1}

echo ""
echo "📝 Configuration:"
echo "   Stack Name: $STACK_NAME"
echo "   Region: $REGION"
echo "   Email: $EMAIL"
echo ""

read -p "Proceed with deployment? (y/n): " CONFIRM
if [[ $CONFIRM != "y" ]]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "🔨 Building application..."
sam build

echo ""
echo "🚀 Deploying to AWS..."
sam deploy \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --parameter-overrides NotificationEmail="$EMAIL" \
    --capabilities CAPABILITY_IAM \
    --resolve-s3 \
    --no-confirm-changeset

echo ""
echo "✅ Deployment complete!"
echo ""

# Get outputs
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentBucket`].OutputValue' \
    --output text)

TABLE_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentTable`].OutputValue' \
    --output text)

echo "📦 Resources created:"
echo "   S3 Bucket: $BUCKET_NAME"
echo "   DynamoDB Table: $TABLE_NAME"
echo ""

echo "📧 IMPORTANT: Check your email ($EMAIL) and confirm the SNS subscription!"
echo ""

echo "🎉 Setup complete! To upload a document, run:"
echo "   aws s3 cp sample_documents/sample_invoice.pdf s3://$BUCKET_NAME/incoming/"
echo ""

echo "📊 To view extracted data, run:"
echo "   aws dynamodb scan --table-name $TABLE_NAME --max-items 5"
echo ""

# Save config for future use
cat > .env << EOF
STACK_NAME=$STACK_NAME
REGION=$REGION
BUCKET_NAME=$BUCKET_NAME
TABLE_NAME=$TABLE_NAME
EMAIL=$EMAIL
EOF

echo "💾 Configuration saved to .env file"
echo ""
echo "🚀 Happy processing!"
