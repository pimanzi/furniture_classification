${BLUE}🧪 Furniture AI Load Testing Suite${NC}
${PURPLE}=====================================

${GREEN}📊 Complete Load Testing Setup${NC}

This comprehensive load testing suite simulates real-world traffic patterns to test your Furniture AI model under various load conditions.

${YELLOW}🎯 Test Scenarios:${NC}

1. **Light Load Test** (5 users, 60s)

   - Simulates normal user behavior
   - Baseline performance measurement
   - Response time: < 2 seconds expected

2. **Medium Load Test** (15 users, 2 min)

   - Peak usage simulation
   - Concurrent user handling
   - Response time: < 5 seconds expected

3. **Heavy Load Test** (25 users, 3 min)

   - High traffic conditions
   - Aggressive request patterns
   - System stability testing

4. **Stress Test** (50 users, 5 min)

   - Maximum load capacity
   - Breaking point identification
   - Performance degradation analysis

5. **Spike Test** (40 users, rapid ramp-up)
   - Sudden traffic spikes
   - Auto-scaling behavior
   - Recovery time measurement

${BLUE}📈 Metrics Monitored:${NC}

**Application Metrics:**

- Response time (latency)
- Request success rate
- Throughput (requests/second)
- Error rate and types

**System Metrics:**

- CPU usage
- Memory consumption
- Disk I/O operations
- Network traffic
- Process monitoring

**Model-Specific Metrics:**

- Image processing time
- Prediction accuracy under load
- Model inference latency
- Memory usage during predictions

${GREEN}🚀 Quick Start:${NC}

1. Ensure your Streamlit app is running:
   ${YELLOW}streamlit run app.py --server.port 8515${NC}

2. Run complete load testing suite:
   ${YELLOW}chmod +x load_testing/run_load_tests.sh${NC}
   ${YELLOW}./load_testing/run_load_tests.sh${NC}

3. Monitor performance in real-time:
   ${YELLOW}python load_testing/performance_monitor.py${NC}

4. View results dashboard:
   ${YELLOW}streamlit run load_testing/dashboard.py${NC}

${BLUE}📊 Understanding Results:${NC}

**Response Time Thresholds:**

- Excellent: < 1 second
- Good: 1-3 seconds
- Acceptable: 3-5 seconds
- Poor: > 5 seconds

**Success Rate Targets:**

- Production Ready: > 99.5%
- Good Performance: > 99%
- Needs Improvement: < 99%

**Throughput Benchmarks:**

- Low Load: 1-5 RPS
- Medium Load: 5-15 RPS
- High Load: 15-30 RPS
- Stress Load: 30+ RPS

${YELLOW}⚠️ Performance Alerts:${NC}

The monitoring system will alert on:

- CPU usage > 80%
- Memory usage > 80%
- Response time > 5 seconds
- Application unavailability
- Error rate > 1%

${GREEN}📁 Output Files:${NC}

**Test Results:**

- load_testing/results/\*.html - Detailed Locust reports
- load_testing/results/\*.csv - Raw performance data

**Performance Monitoring:**

- load_testing/performance_monitoring/\*.json - System metrics
- load_testing/performance_monitoring/\*.csv - Time-series data

**Logs:**

- load_testing/logs/\*.log - Detailed execution logs

${PURPLE}🔧 Customization:${NC}

Edit ${YELLOW}load_testing/locustfile.py${NC} to:

- Modify user behavior patterns
- Adjust request frequencies
- Add custom test scenarios
- Change image types/sizes

Edit ${YELLOW}load_testing/run_load_tests.sh${NC} to:

- Modify test durations
- Change user counts
- Adjust spawn rates
- Add new test scenarios

${BLUE}💡 Best Practices:${NC}

1. **Baseline Testing:** Always run light load first
2. **Gradual Scaling:** Increase load incrementally
3. **Monitor Resources:** Watch CPU, memory, disk during tests
4. **Document Results:** Keep test results for comparison
5. **Regular Testing:** Run load tests after model updates

${GREEN}🎯 Expected Performance:${NC}

**Furniture AI Model Performance Targets:**

- Image classification: 200-800ms per image
- Concurrent users: 10-20 without degradation
- Memory usage: < 2GB under normal load
- CPU usage: < 70% during peak load

${RED}🚨 Troubleshooting:${NC}

**Common Issues:**

- High response times → Check model optimization
- High CPU usage → Consider model quantization
- Memory leaks → Monitor TensorFlow memory usage
- Connection errors → Verify Streamlit port availability

**Solutions:**

- Use smaller model variants for better speed
- Implement request queuing for high load
- Add caching for frequently requested predictions
- Consider horizontal scaling with load balancers

${YELLOW}🔍 Advanced Analysis:${NC}

For deeper analysis:

1. Export results to external tools (Grafana, ELK stack)
2. Set up continuous performance monitoring
3. Implement A/B testing for model variants
4. Add business metrics (user satisfaction, conversion rates)

${GREEN}✅ Success Criteria:${NC}

Your load testing is successful when:

- All test scenarios complete without critical failures
- Response times stay within acceptable limits
- System resources remain stable
- Error rates stay below 1%
- Application remains available throughout testing

${BLUE}📞 Support:${NC}

For issues or questions:

- Check logs in load_testing/logs/
- Review HTML reports for detailed metrics
- Monitor system resources during testing
- Adjust test parameters based on your hardware

${PURPLE}Happy Load Testing! 🧪📊${NC}
