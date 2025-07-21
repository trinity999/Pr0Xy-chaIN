# Proxy Chain Setup Script for Windows
# Run with: powershell -ExecutionPolicy Bypass -File setup_proxy_chain.ps1

Write-Host "🔗 Setting up Proxy Chain Environment" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Check Python installation
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.7+" -ForegroundColor Red
    exit 1
}

# Install Python requirements
Write-Host "`n📦 Installing Python requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check for proxychains (if using WSL)
Write-Host "`n🔍 Checking for proxychains..." -ForegroundColor Yellow
if (Get-Command wsl -ErrorAction SilentlyContinue) {
    Write-Host "✅ WSL detected. You can use proxychains4 with:" -ForegroundColor Green
    Write-Host "   wsl sudo apt update && wsl sudo apt install proxychains4" -ForegroundColor Cyan
} else {
    Write-Host "ℹ️  For proxychains support, consider installing WSL" -ForegroundColor Blue
}

# Create directories
$dirs = @("logs", "output", "wordlists")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir
        Write-Host "✅ Created directory: $dir" -ForegroundColor Green
    }
}

# Download common wordlists
Write-Host "`n📚 Downloading common wordlists..." -ForegroundColor Yellow

$wordlists = @{
    "common.txt" = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt"
    "directory-list-2.3-medium.txt" = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/directory-list-2.3-medium.txt"
}

foreach ($filename in $wordlists.Keys) {
    $url = $wordlists[$filename]
    $filepath = "wordlists\$filename"
    
    if (!(Test-Path $filepath)) {
        try {
            Write-Host "  Downloading $filename..." -ForegroundColor Cyan
            Invoke-WebRequest -Uri $url -OutFile $filepath
            Write-Host "  ✅ Downloaded $filename" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ Failed to download $filename" -ForegroundColor Red
        }
    }
}

Write-Host "`n🚀 Setup complete! Next steps:" -ForegroundColor Green
Write-Host "1. Run: python proxy_chain_setup.py" -ForegroundColor Cyan
Write-Host "2. Test: python proxy_scanner.py test httpbin.org" -ForegroundColor Cyan
Write-Host "3. Scan: python proxy_scanner.py nmap target.com" -ForegroundColor Cyan

Write-Host "`n📋 Available tools integration:" -ForegroundColor Yellow
Write-Host "  • Nmap (via proxychains)" -ForegroundColor White
Write-Host "  • Gobuster" -ForegroundColor White
Write-Host "  • FFUF" -ForegroundColor White
Write-Host "  • Nuclei" -ForegroundColor White
Write-Host "  • cURL" -ForegroundColor White

Write-Host "`n⚠️  Important:" -ForegroundColor Red
Write-Host "  • Use only for authorized testing" -ForegroundColor Red
Write-Host "  • Free proxies may be unreliable" -ForegroundColor Red
Write-Host "  • Consider rate limiting for stability" -ForegroundColor Red
