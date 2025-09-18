# Kubernetes deployment script for Windows
Write-Host "🚀 Deploying Vision AI to Kubernetes..." -ForegroundColor Green

# Create namespace
kubectl apply -f kubernetes/namespace.yaml

# Get API key securely
$API_KEY = Read-Host -Prompt "Enter your OpenRouter API key" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($API_KEY)
$PlainKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
$Base64Key = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($PlainKey))

# Create secrets file
@"
apiVersion: v1
kind: Secret
metadata:
  name: vision-ai-secrets
  namespace: vision-ai
type: Opaque
data:
  openrouter-api-key: $Base64Key
"@ | Out-File -FilePath "kubernetes\secrets-temp.yaml" -Encoding UTF8

# Apply configurations
kubectl apply -f kubernetes\secrets-temp.yaml
kubectl apply -f kubernetes\configmap.yaml
kubectl apply -f kubernetes\deployment.yaml
kubectl apply -f kubernetes\service.yaml

# Cleanup temporary files
Remove-Item -Path "kubernetes\secrets-temp.yaml" -Force

Write-Host "✅ Deployment complete!" -ForegroundColor Green
Write-Host "📊 Check status with: kubectl get all -n vision-ai" -ForegroundColor Cyan
Write-Host "🌐 Get external IP: kubectl get svc vision-ai-service -n vision-ai" -ForegroundColor Cyan 