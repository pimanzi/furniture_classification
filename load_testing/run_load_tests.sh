#!/bin/bash

# Furniture AI Load Testing Script
# This script sets up and runs comprehensive load testing using Locust

echo "🧪 Furniture AI Load Testing Setup"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the furniture_classification directory${NC}"
    exit 1
fi

# Check if Streamlit app is running
echo -e "${BLUE}🔍 Checking if Streamlit app is running...${NC}"
if ! curl -s http://localhost:8515 > /dev/null; then
    echo -e "${YELLOW}⚠️ Streamlit app not detected on port 8515${NC}"
    echo -e "${YELLOW}📝 Please start the app first with: streamlit run app.py --server.port 8515${NC}"
    read -p "Press Enter when the app is running, or Ctrl+C to exit..."
fi

# Install Locust if not already installed
echo -e "${BLUE}📦 Checking Locust installation...${NC}"
if ! python -c "import locust" 2>/dev/null; then
    echo -e "${YELLOW}📥 Installing Locust...${NC}"
    pip install locust
    pip install Pillow numpy requests
else
    echo -e "${GREEN}✅ Locust is already installed${NC}"
fi

# Create results directory
mkdir -p load_testing/results
mkdir -p load_testing/logs

echo -e "${GREEN}🚀 Starting Load Testing Scenarios${NC}"
echo ""

# Function to run a load test scenario
run_load_test() {
    local scenario_name=$1
    local user_class=$2
    local users=$3
    local spawn_rate=$4
    local duration=$5
    local description=$6
    
    echo -e "${PURPLE}📊 Running: $scenario_name${NC}"
    echo -e "${BLUE}   $description${NC}"
    echo -e "${YELLOW}   Users: $users, Spawn Rate: $spawn_rate/sec, Duration: ${duration}s${NC}"
    
    # Create unique filename with timestamp
    timestamp=$(date +"%Y%m%d_%H%M%S")
    log_file="load_testing/logs/${scenario_name}_${timestamp}.log"
    csv_file="load_testing/results/${scenario_name}_${timestamp}"
    
    # Run Locust in headless mode
    locust \
        -f load_testing/locustfile.py \
        --user-class $user_class \
        --users $users \
        --spawn-rate $spawn_rate \
        --run-time ${duration}s \
        --host http://localhost:8515 \
        --headless \
        --csv=$csv_file \
        --html=load_testing/results/${scenario_name}_${timestamp}.html \
        --logfile=$log_file \
        --loglevel INFO
    
    echo -e "${GREEN}✅ $scenario_name completed${NC}"
    echo -e "${BLUE}📊 Results saved to: load_testing/results/${scenario_name}_${timestamp}.html${NC}"
    echo ""
    
    # Brief pause between tests
    sleep 5
}

# Test Scenario 1: Light Load - Normal User Behavior
run_load_test \
    "light_load" \
    "FurnitureAPIUser" \
    5 \
    1 \
    60 \
    "Simulates 5 concurrent users with normal behavior patterns"

# Test Scenario 2: Medium Load - Peak Usage
run_load_test \
    "medium_load" \
    "FurnitureAPIUser" \
    15 \
    2 \
    120 \
    "Simulates 15 concurrent users during peak usage"

# Test Scenario 3: Heavy Load - High Traffic
run_load_test \
    "heavy_load" \
    "HeavyLoadUser" \
    25 \
    3 \
    180 \
    "Simulates 25 aggressive users with rapid requests"

# Test Scenario 4: Stress Test - Maximum Load
run_load_test \
    "stress_test" \
    "StressTestUser" \
    50 \
    5 \
    300 \
    "Maximum stress test with 50 concurrent users"

# Test Scenario 5: Spike Test - Sudden Load Increase
echo -e "${PURPLE}📊 Running: spike_test${NC}"
echo -e "${BLUE}   Simulates sudden spike in traffic${NC}"
echo -e "${YELLOW}   Ramp up to 40 users quickly, then maintain${NC}"

timestamp=$(date +"%Y%m%d_%H%M%S")
log_file="load_testing/logs/spike_test_${timestamp}.log"
csv_file="load_testing/results/spike_test_${timestamp}"

locust \
    -f load_testing/locustfile.py \
    --user-class FurnitureAPIUser \
    --users 40 \
    --spawn-rate 8 \
    --run-time 240s \
    --host http://localhost:8515 \
    --headless \
    --csv=$csv_file \
    --html=load_testing/results/spike_test_${timestamp}.html \
    --logfile=$log_file \
    --loglevel INFO

echo -e "${GREEN}✅ spike_test completed${NC}"
echo ""

# Generate summary report
echo -e "${GREEN}📈 Load Testing Complete!${NC}"
echo -e "${PURPLE}================================${NC}"
echo -e "${BLUE}📊 Results Summary:${NC}"
echo ""

# Count result files
result_count=$(ls -1 load_testing/results/*.html 2>/dev/null | wc -l)
echo -e "${GREEN}✅ Total test scenarios completed: $result_count${NC}"

echo -e "${BLUE}📁 Results location: load_testing/results/${NC}"
echo -e "${BLUE}📋 Logs location: load_testing/logs/${NC}"
echo ""

# Show recent results
echo -e "${YELLOW}📊 Recent test results:${NC}"
ls -lt load_testing/results/*.html 2>/dev/null | head -5

echo ""
echo -e "${GREEN}🎉 Load testing completed successfully!${NC}"
echo -e "${BLUE}💡 Open the HTML reports in your browser to view detailed metrics${NC}"
echo -e "${BLUE}🔍 Check the logs for detailed timing and error information${NC}"

# Offer to open results
read -p "Would you like to open the latest test results? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    latest_result=$(ls -t load_testing/results/*.html 2>/dev/null | head -1)
    if [ -n "$latest_result" ]; then
        echo -e "${GREEN}🌐 Opening: $latest_result${NC}"
        xdg-open "$latest_result" 2>/dev/null || open "$latest_result" 2>/dev/null || echo "Please manually open: $latest_result"
    fi
fi
