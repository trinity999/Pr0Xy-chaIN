# Install Proxy Chain Commands to PATH
# Run as Administrator: powershell -ExecutionPolicy Bypass -File install_commands.ps1

param(
    [switch]$User = $false
)

$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Write-Host "🔧 Installing Proxy Chain Commands" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Determine if we're adding to user or system PATH
if ($User) {
    $scope = "User"
    $envTarget = [System.EnvironmentVariableTarget]::User
    Write-Host "📍 Installing for current user only" -ForegroundColor Yellow
} else {
    $scope = "Machine" 
    $envTarget = [System.EnvironmentVariableTarget]::Machine
    Write-Host "📍 Installing system-wide (requires admin)" -ForegroundColor Yellow
}

try {
    # Get current PATH
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", $envTarget)
    
    # Check if directory is already in PATH
    if ($currentPath -split ';' -contains $currentDir) {
        Write-Host "✅ Directory already in PATH: $currentDir" -ForegroundColor Green
    } else {
        # Add directory to PATH
        $newPath = $currentPath + ";" + $currentDir
        [Environment]::SetEnvironmentVariable("PATH", $newPath, $envTarget)
        Write-Host "✅ Added to PATH: $currentDir" -ForegroundColor Green
    }
    
    # Refresh current session PATH
    $env:PATH = [Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [Environment]::GetEnvironmentVariable("PATH", "User")
    
    Write-Host "`n🎉 Installation complete!" -ForegroundColor Green
    Write-Host "🔧 Available commands:" -ForegroundColor Cyan
    Write-Host "  • init-proxy-chain-now  - Initialize and start proxy chain" -ForegroundColor White
    Write-Host "  • proxy-status          - Check daemon status" -ForegroundColor White  
    Write-Host "  • proxy-stop            - Stop the daemon" -ForegroundColor White
    Write-Host "  • proxy-scan            - Proxy-enabled scanning" -ForegroundColor White
    
    Write-Host "`n📋 Usage examples:" -ForegroundColor Yellow
    Write-Host "  init-proxy-chain-now" -ForegroundColor White
    Write-Host "  proxy-status" -ForegroundColor White
    Write-Host "  proxy-scan nmap target.com" -ForegroundColor White
    Write-Host "  proxy-scan curl https://httpbin.org/ip" -ForegroundColor White
    
    Write-Host "`n⚠️  Note: You may need to restart your terminal for commands to be available" -ForegroundColor Red
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 Try running as Administrator or use -User flag for user-only install" -ForegroundColor Yellow
}

Write-Host "`n🚀 Ready to use! Run 'init-proxy-chain-now' to get started!" -ForegroundColor Green
