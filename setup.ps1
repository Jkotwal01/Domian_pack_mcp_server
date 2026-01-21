# Setup script for Domain Pack MCP Server (Windows PowerShell)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Domain Pack MCP Server - Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check Python version
Write-Host ""
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
Write-Host ""
Write-Host "Setting up environment configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ Created .env file (please configure your database settings)" -ForegroundColor Green
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Check PostgreSQL
Write-Host ""
Write-Host "Checking PostgreSQL..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version
    Write-Host "✓ PostgreSQL is installed" -ForegroundColor Green
    Write-Host $pgVersion
} catch {
    Write-Host "⚠ PostgreSQL not found. Please install PostgreSQL 12+" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup completed!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure database settings in .env file"
Write-Host "2. Create database: createdb domain_pack_mcp"
Write-Host "3. Run tests: python test_server.py"
Write-Host "4. Start server: python main.py"
Write-Host ""
