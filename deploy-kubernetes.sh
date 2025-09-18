#!/bin/bash

# Kubernetes deployment script for Vision AI app

echo "🚀 Deploying Vision AI to Kubernetes..."

# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Create secrets (encode API key)
read -s -p "Enter your OpenRouter API key: " API_KEY
echo
BASE64_KEY=$(echo -n "$API_KEY" | base64)

# Create secrets file
cat > kubernetes/secrets-temp.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: vision-ai-secrets
  namespace: vision-ai
type: Opaque
data:
  openrouter-api-key: $BASE64_KEY
EOF

# Apply configurations
kubectl apply -f kubernetes/secrets-temp.yaml
kubectl apply -f kubernetes/configmap.yaml
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml

# Cleanup temporary files
rm -f kubernetes/secrets-temp.yaml

echo "✅ Deployment complete!"
echo "📊 Check status with: kubectl get all -n vision-ai"
echo "🌐 Get external IP: kubectl get svc vision-ai-service -n vision-ai"