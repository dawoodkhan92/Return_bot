#!/bin/bash

# Shopify Returns Agency Deployment Script
# This script automates the deployment process for different environments

set -e  # Exit on any error

# Default values
ENVIRONMENT="development"
BUILD_DOCKER=false
RESTART_SERVICES=false
RUN_TESTS=false

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Set environment (development|testing|production) [default: development]"
    echo "  -d, --docker             Build and deploy using Docker"
    echo "  -r, --restart            Restart services after deployment"
    echo "  -t, --test               Run tests before deployment"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e production -d -t    Deploy to production with Docker and tests"
    echo "  $0 -e development -r      Deploy to development and restart services"
    echo "  $0 --docker --test        Build Docker image and run tests"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--docker)
            BUILD_DOCKER=true
            shift
            ;;
        -r|--restart)
            RESTART_SERVICES=true
            shift
            ;;
        -t|--test)
            RUN_TESTS=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|testing|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    print_error "Must be one of: development, testing, production"
    exit 1
fi

print_status "Starting deployment for environment: $ENVIRONMENT"

# Check if .env file exists
if [[ ! -f ".env" && "$ENVIRONMENT" == "production" ]]; then
    print_warning ".env file not found. Creating from template..."
    if [[ -f ".env.example" ]]; then
        cp .env.example .env
        print_warning "Please edit .env file with your production settings before continuing"
        exit 1
    else
        print_error ".env.example file not found"
        exit 1
    fi
fi

# Run tests if requested
if [[ "$RUN_TESTS" == true ]]; then
    print_status "Running tests..."
    
    # Check if virtual environment exists
    if [[ -d "venv" ]]; then
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    fi
    
    # Run test suite
    python run_tests.py
    if [[ $? -eq 0 ]]; then
        print_success "All tests passed"
    else
        print_error "Tests failed. Aborting deployment."
        exit 1
    fi
fi

# Docker deployment
if [[ "$BUILD_DOCKER" == true ]]; then
    print_status "Building Docker image..."
    
    # Build Docker image
    docker build -t shopify-returns-agency:latest .
    if [[ $? -eq 0 ]]; then
        print_success "Docker image built successfully"
    else
        print_error "Docker build failed"
        exit 1
    fi
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    
    # Start services
    print_status "Starting services with Docker Compose..."
    if [[ "$ENVIRONMENT" == "production" ]]; then
        docker-compose --profile production up -d
    else
        docker-compose up -d shopify-returns-agency
    fi
    
    if [[ $? -eq 0 ]]; then
        print_success "Services started successfully"
    else
        print_error "Failed to start services"
        exit 1
    fi
    
else
    # Traditional deployment
    print_status "Deploying without Docker..."
    
    # Check if virtual environment exists
    if [[ ! -d "venv" ]]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    
    # Install/update dependencies
    print_status "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create logs directory
    mkdir -p logs
    
    # Set environment variables
    export FLASK_ENV=$ENVIRONMENT
    
    if [[ "$RESTART_SERVICES" == true ]]; then
        # Stop existing processes (if any)
        print_status "Stopping existing processes..."
        pkill -f "python app.py" 2>/dev/null || true
        
        # Start the application
        print_status "Starting application..."
        if [[ "$ENVIRONMENT" == "production" ]]; then
            nohup python app.py > logs/app.log 2>&1 &
            print_success "Application started in background (PID: $!)"
        else
            python app.py &
            print_success "Application started (PID: $!)"
        fi
    fi
fi

# Health check
print_status "Performing health check..."
sleep 5  # Wait for application to start

# Determine the URL to check
if [[ "$BUILD_DOCKER" == true ]]; then
    HEALTH_URL="http://localhost:5000/health"
else
    HEALTH_URL="http://localhost:5000/health"
fi

# Check health endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL 2>/dev/null || echo "000")
if [[ "$response" == "200" ]]; then
    print_success "Health check passed"
else
    print_warning "Health check failed (HTTP $response). Application may still be starting..."
fi

# Show deployment summary
echo ""
print_success "Deployment completed!"
echo ""
echo "Environment: $ENVIRONMENT"
echo "Docker: $BUILD_DOCKER"
echo "Tests run: $RUN_TESTS"
echo "Services restarted: $RESTART_SERVICES"
echo ""

if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "Production deployment checklist:"
    echo "- [ ] Verify SHOPIFY_WEBHOOK_SECRET is set"
    echo "- [ ] Confirm SSL certificates are in place"
    echo "- [ ] Test webhook endpoint from Shopify"
    echo "- [ ] Monitor logs for any issues"
    echo "- [ ] Set up monitoring and alerting"
fi

print_status "Application should be available at: http://localhost:5000"
print_status "Health check: $HEALTH_URL"
print_status "Logs location: ./logs/"

if [[ "$BUILD_DOCKER" == true ]]; then
    echo ""
    print_status "Docker commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart: docker-compose restart"
fi 