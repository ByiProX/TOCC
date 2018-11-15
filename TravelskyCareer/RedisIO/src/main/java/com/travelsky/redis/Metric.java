package com.travelsky.redis;

public interface Metric {

    void setIp(String ip);
    String getIp();
    void setMetric(String metric);
    String getMetric();
    void addValue(MetricValue metricValue);
}

interface MetricValue{
    void setTime(String time);
    void setHostname(String hostname);

}
