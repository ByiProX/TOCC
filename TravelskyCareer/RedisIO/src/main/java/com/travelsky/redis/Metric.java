package com.travelsky.redis;

public interface Metric {

    void setIp(String ip);
    void setMetric(String metric);
    String getIp();
    void addValue(MetricValue metricValue);
}

interface MetricValue{
    void setTime(String time);
    void setHostname(String hostname);

}
