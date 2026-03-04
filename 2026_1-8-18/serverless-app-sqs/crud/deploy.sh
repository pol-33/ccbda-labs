#!/bin/bash

# We do not use 'set -e' because we want to handle "already exists" errors manually
# set -e 

source $1

ACCOUNT_ID=`aws sts get-caller-identity --query Account --output text`
# Recursive variable issue problem fixed
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE}"

ENVIRONMENT_VARIABLES=()
for var in REGION LOG_LEVEL; do
  ENVIRONMENT_VARIABLES+=($var=${!var})
done
ENVIRONMENT=$(IFS=, ; echo "${ENVIRONMENT_VARIABLES[*]}")

echo "ENVIRONMENT: ${ENVIRONMENT}"

# 1. Create DynamoDB (Suppresses error if it already exists)
echo "--- Checking DynamoDB ---"
aws dynamodb create-table \
  --table-name ${TABLE} \
  --attribute-definitions \
        AttributeName=thingID,AttributeType=S \
  --key-schema \
        AttributeName=thingID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region ${REGION} 2>/dev/null || echo "Table already exists, continuing..."

# 2. Deploy or Update Lambda
echo "--- Deploying Lambda ---"
pushd lambda
zip lambda_crud.zip lambda_crud.py requirements.txt

# Try to create. If it fails (already exists), update the code instead.
aws lambda create-function \
  --function-name ${LAMBDA} \
  --zip-file fileb://lambda_crud.zip \
  --handler lambda_crud.lambda_handler \
  --runtime python3.13 \
  --role ${ROLE_ARN} \
  --environment "Variables={${ENVIRONMENT}}" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "Function exists. Updating code..."
    aws lambda update-function-code --function-name ${LAMBDA} --zip-file fileb://lambda_crud.zip > /dev/null
fi

# Fetch the ARN fresh from AWS
LAMBDA_ARN=$(aws lambda get-function --function-name ${LAMBDA} --query 'Configuration.FunctionArn' --output text)
echo "LAMBDA_ARN: ${LAMBDA_ARN}"
popd

# 3. Permissions (Ignore error if exists)
STATEMENT_ID=`uuidgen`
echo "STATEMENT_ID: ${STATEMENT_ID}"

aws lambda add-permission \
    --function-name ${LAMBDA} \
    --principal apigateway.amazonaws.com \
    --statement-id "${STATEMENT_ID}" \
    --action lambda:InvokeFunction 2>/dev/null || echo "Permission probably already exists"

# 4. Create API Gateway (This always creates a NEW one)
echo "--- Creating API Gateway ---"
API_ID=`aws apigatewayv2 create-api \
  --name "CrudHttpAPI" \
  --protocol-type HTTP \
  --cors-configuration AllowOrigins="*",AllowHeaders=content-type,AllowMethods=GET,POST,OPTIONS,PUT,DELETE \
   | jq -r '.ApiId'`

echo "API_ID: ${API_ID}"

# 5. Integration
INTEGRATION_ID=`aws apigatewayv2 create-integration \
    --api-id ${API_ID} \
    --integration-type AWS_PROXY \
    --integration-uri ${LAMBDA_ARN} \
    --integration-method ANY \
    --payload-format-version 2.0 \
    | jq -r '.IntegrationId' `

echo "INTEGRATION_ID: ${INTEGRATION_ID}"

# 6. Routes
for ROUTE in GET POST OPTIONS PUT DELETE; do
    aws apigatewayv2 create-route \
        --api-id ${API_ID} \
        --route-key "${ROUTE} /" \
        --target "integrations/${INTEGRATION_ID}" > /dev/null
done

# --- LOGGING ---
LOG_GROUP_NAME="/aws/apiGW/LambdaCRUD"
LOG_FORMAT='{"requestId":"$context.requestId", "ip": "$context.identity.sourceIp", "httpMethod":"$context.httpMethod", "status":"$context.status"}'

# Create Log Group if not exists
aws logs create-log-group --log-group-name ${LOG_GROUP_NAME} --region ${REGION} 2>/dev/null || true
LOG_GROUP_ARN="arn:aws:logs:${REGION}:${ACCOUNT_ID}:log-group:${LOG_GROUP_NAME}"

STAGE="production"

# Create Stage with Logging
aws apigatewayv2 create-stage \
     --api-id ${API_ID} \
     --stage-name ${STAGE} \
     --no-auto-deploy \
     --access-log-settings "DestinationArn=${LOG_GROUP_ARN},Format='${LOG_FORMAT}'"

# 7. Deployment
aws apigatewayv2 create-deployment \
    --api-id ${API_ID} \
    --stage-name ${STAGE}

# 8. Output
URL="https://${API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE}/?TableName=${TABLE}"
echo "URL: ${URL}"
curl $URL

# Update variables.json
echo -e "{\"url\":\"https://${API_ID}.execute-api.${REGION}.amazonaws.com/${STAGE}/\",\"table\":\"${TABLE}\"}" > variables.json
cat variables.json
