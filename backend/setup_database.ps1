# Database Setup Script for Domain Pack Generator
# This script creates the database and runs the initialization SQL

param(
    [string]$DbName = "domain_pack_db",
    [string]$DbUser = "postgres",
    [string]$DbPassword = "postgres",
    [string]$DbHost = "localhost",
    [string]$DbPort = "5432"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Domain Pack Generator - Database Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PostgreSQL is installed
Write-Host "Checking PostgreSQL installation..." -ForegroundColor Yellow
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $psqlPath) {
    Write-Host "❌ PostgreSQL is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install PostgreSQL from: https://www.postgresql.org/download/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ PostgreSQL found at: $($psqlPath.Source)" -ForegroundColor Green
Write-Host ""

# Set environment variable for password
$env:PGPASSWORD = $DbPassword

# Check if database exists
Write-Host "Checking if database '$DbName' exists..." -ForegroundColor Yellow
$dbExists = & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$DbName'" 2>$null

if ($dbExists -eq "1") {
    Write-Host "⚠️  Database '$DbName' already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to drop and recreate it? (yes/no)"
    
    if ($response -eq "yes") {
        Write-Host "Dropping existing database..." -ForegroundColor Yellow
        & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "DROP DATABASE $DbName;" 2>$null
        Write-Host "✅ Database dropped" -ForegroundColor Green
    } else {
        Write-Host "Skipping database creation. Will run initialization script on existing database." -ForegroundColor Yellow
        $skipCreate = $true
    }
}

# Create database if needed
if (-not $skipCreate) {
    Write-Host "Creating database '$DbName'..." -ForegroundColor Yellow
    & psql -h $DbHost -p $DbPort -U $DbUser -d postgres -c "CREATE DATABASE $DbName;"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create database" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Run initialization script
Write-Host "Running database initialization script..." -ForegroundColor Yellow
$scriptPath = Join-Path $PSScriptRoot "init_db.sql"

if (-not (Test-Path $scriptPath)) {
    Write-Host "❌ Initialization script not found at: $scriptPath" -ForegroundColor Red
    exit 1
}

& psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -f $scriptPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Database initialized successfully" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to initialize database" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Verify setup
Write-Host "Verifying database setup..." -ForegroundColor Yellow
$tableCount = & psql -h $DbHost -p $DbPort -U $DbUser -d $DbName -tAc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';"

Write-Host "✅ Found $tableCount tables" -ForegroundColor Green

# Display connection string
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Database setup complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connection Details:" -ForegroundColor Yellow
Write-Host "  Host: $DbHost" -ForegroundColor White
Write-Host "  Port: $DbPort" -ForegroundColor White
Write-Host "  Database: $DbName" -ForegroundColor White
Write-Host "  User: $DbUser" -ForegroundColor White
Write-Host ""
Write-Host "Add this to your .env file:" -ForegroundColor Yellow
Write-Host "DATABASE_URL=postgresql://${DbUser}:${DbPassword}@${DbHost}:${DbPort}/${DbName}" -ForegroundColor Cyan
Write-Host ""

# Clean up
$env:PGPASSWORD = $null
