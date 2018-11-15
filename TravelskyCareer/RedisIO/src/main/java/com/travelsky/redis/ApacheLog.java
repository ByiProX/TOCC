package com.travelsky.redis;


import java.util.ArrayList;
import java.util.List;

/**
 * key:IP|ApacheLog|访问类型
 * value:时间戳|主机名|TPS|最小响应时间|最大响应时间|平均响应时间|平均流量
 * 122.119.180.82|ApacheLog|new.hnair.com   20180517-23:46:01|vm-vmw97020-apc|90.3|0.6|35786.1|185.1|24079.4
 * 122.119.180.82|ApacheLog|new.hnair.com   20180517-23:48:01|vm-vmw97020-apc|83.9|0.5|14656.7|169.1|27589.8
 */

public class ApacheLog implements Metric{
    private String ip;
    private String metric;
    private String visitType;
    private List<ApacheLogValue> apacheLogValues = new ArrayList<>();

    public ApacheLog(Object redisKey, List<String> redisValue){
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        visitType = argList[2];

        for (String value: redisValue){
            String[] valueList = value.split("[|]");

            ApacheLogValue apacheLogValue = new ApacheLogValue();
            apacheLogValue.setTime(valueList[0]);
            apacheLogValue.setHostname(valueList[1]);
            apacheLogValue.setTps(Double.parseDouble(valueList[2]));
            apacheLogValue.setMinResponseTime(Double.parseDouble(valueList[3]));
            apacheLogValue.setMaxResponseTime(Double.parseDouble(valueList[4]));
            apacheLogValue.setAveResponseTime(Double.parseDouble(valueList[5]));
            apacheLogValue.setAveNetFlow(Double.parseDouble(valueList[6]));

            apacheLogValues.add(apacheLogValue);
        }
    }

    public ApacheLog(){}

    @Override
    public void addValue(MetricValue metricValue) {
        apacheLogValues.add((ApacheLogValue) metricValue);
    }

    public List<ApacheLogValue> getApacheLogValues() {
        return apacheLogValues;
    }

    public String getIp() {
        return ip;
    }

    @Override
    public void setIp(String ip) {
        this.ip = ip;
    }

    public String getMetric() {
        return metric;
    }

    @Override
    public void setMetric(String metric) {
        this.metric = metric;
    }

    public String getVisitType() {
        return visitType;
    }

    public void setVisitType(String visitType) {
        this.visitType = visitType;
    }
}

class ApacheLogValue implements MetricValue{
    private String time;
    private String hostname;
    private double tps;
    private double minResponseTime;
    private double maxResponseTime;
    private double aveResponseTime;
    private double aveNetFlow;


    public String getTime() {
        return time;
    }

    @Override
    public void setTime(String time) {
        this.time = time;
    }

    public String getHostname() {
        return hostname;
    }

    @Override
    public void setHostname(String hostname) {
        this.hostname = hostname;
    }

    public double getTps() {
        return tps;
    }

    public void setTps(double tps) {
        this.tps = tps;
    }

    public double getMinResponseTime() {
        return minResponseTime;
    }

    public void setMinResponseTime(double minResponseTime) {
        this.minResponseTime = minResponseTime;
    }

    public double getMaxResponseTime() {
        return maxResponseTime;
    }

    public void setMaxResponseTime(double maxResponseTime) {
        this.maxResponseTime = maxResponseTime;
    }

    public double getAveResponseTime() {
        return aveResponseTime;
    }

    public void setAveResponseTime(double aveResponseTime) {
        this.aveResponseTime = aveResponseTime;
    }

    public double getAveNetFlow() {
        return aveNetFlow;
    }

    public void setAveNetFlow(double aveNetFlow) {
        this.aveNetFlow = aveNetFlow;
    }
}
