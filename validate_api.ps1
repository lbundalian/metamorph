# API Validation Script for DNPM-DIP RD Schema (PowerShell version)
# This script validates transformed JSON files against the DNMP-DIP API endpoint.

param(
    [Parameter(Mandatory=$true)]
    [string]$JsonFilePath,
    
    [Parameter(Mandatory=$false)]
    [string]$ApiUrl = "https://preview.dnpm-dip.net/api/rd/etl/patient-record:validate"
)

function Validate-WithApi {
    param(
        [string]$JsonFile,
        [string]$Url
    )
    
    if (-not (Test-Path $JsonFile)) {
        Write-Error "File $JsonFile does not exist"
        return @{ error = "File not found" }
    }
    
    try {
        Write-Host "Validating $JsonFile against $Url" -ForegroundColor Yellow
        Write-Host ("-" * 50) -ForegroundColor Yellow
        
        # Read JSON content
        $jsonContent = Get-Content $JsonFile -Raw -Encoding UTF8
        
        # Make API request using Invoke-RestMethod
        $headers = @{
            "Content-Type" = "application/json"
            "Accept" = "application/json"
        }
        
        $response = Invoke-RestMethod -Uri $Url -Method POST -Body $jsonContent -Headers $headers -TimeoutSec 30
        
        return $response
    }
    catch {
        return @{
            error = "Request failed: $($_.Exception.Message)"
            details = $_.Exception
        }
    }
}

# Main execution
Write-Host "API Validation Script for DNPM-DIP RD Schema" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

$result = Validate-WithApi -JsonFile $JsonFilePath -Url $ApiUrl

Write-Host "API Validation Response:" -ForegroundColor Cyan
Write-Host ("=" * 50) -ForegroundColor Cyan
Write-Host ($result | ConvertTo-Json -Depth 10 -Compress:$false)

# Check validation result
if ($result.error) {
    Write-Host "`n❌ Validation failed with error: $($result.error)" -ForegroundColor Red
    exit 1
}
elseif ($result.errors -and $result.errors.Count -gt 0) {
    Write-Host "`n❌ Schema validation failed with $($result.errors.Count) errors" -ForegroundColor Red
    exit 1
}
else {
    Write-Host "`n✅ Validation successful!" -ForegroundColor Green
    exit 0
}