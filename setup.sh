#!/bin/bash
# Setup script for Domain Pack MCP Server

echo "=========================================="
echo "Domain Pack MCP Server - Setup"
echo "=========================================="

# Check Python version
echo ""
echo "Checking Python version..."
python --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate  # Windows Git Bash
elif [ -f "venv/bin/activate" ]; then
    source venv/bin/activate  # Linux/Mac
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
echo ""
echo "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env file (please configure your database settings)"
else
    echo "✓ .env file already exists"
fi

# Check PostgreSQL
echo ""
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✓ PostgreSQL is installed"
    psql --version
else
    echo "⚠ PostgreSQL not found. Please install PostgreSQL 12+"
fi

echo ""
echo "=========================================="
echo "Setup completed!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Configure database settings in .env file"
echo "2. Create database: createdb domain_pack_mcp"
echo "3. Run tests: python test_server.py"
echo "4. Start server: python main.py"
echo ""
