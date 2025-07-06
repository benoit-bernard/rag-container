Write-Host "🧪 Tests du Backend RAG" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green

# Test 1: Health Check
Write-Host "1. Test Health Check..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    Write-Host "✅ Health: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health Check Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: Question Simple
Write-Host "2. Test Question Simple..." -ForegroundColor Yellow
try {
    $body = @{ question = "Hello" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method POST -Body $body -ContentType "application/json"
    Write-Host "✅ Réponse: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Question Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: Question Vide
Write-Host "3. Test Question Vide..." -ForegroundColor Yellow
try {
    $body = @{ question = "" } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method POST -Body $body -ContentType "application/json"
    Write-Host "⚠️ Unexpected success: $($response | ConvertTo-Json)" -ForegroundColor Yellow
} catch {
    Write-Host "✅ Erreur attendue: $($_.Exception.Message)" -ForegroundColor Green
}
Write-Host ""

# Test 4: Reload
Write-Host "4. Test Reload..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/reload" -Method POST
    Write-Host "✅ Reload: $($response | ConvertTo-Json)" -ForegroundColor Green
} catch {
    Write-Host "❌ Reload Failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "🎉 Tests terminés!" -ForegroundColor Green