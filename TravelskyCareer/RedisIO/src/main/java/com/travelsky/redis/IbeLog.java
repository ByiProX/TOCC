package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key: ip|ibelog|指令
 * value: 时间|主机名|时间周期|TPS|最大响应时间|最小响应时间|平均响应时间
 * 10.6.151.21|ibelog|AVH   20180517-23:46:01|pe6850d-vmwc5-ibe|60|63.02|1911|130|404
 * 10.6.151.21|ibelog|AVH   20180517-23:48:01|pe6850d-vmwc5-ibe|60|59.25|4451|166|424
 */

public class IbeLog implements Metric{
    private String ip;
    private String metric;
    private String command;
    private List<IbeLogValue> ibeLogValues = new ArrayList<>();


    @Override
    public void addValue(MetricValue metricValue) {
        ibeLogValues.add((IbeLogValue) metricValue);
    }

    public List<IbeLogValue> getIbeLogValues(){
        return ibeLogValues;
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

    public String getCommand() {
        return command;
    }

    public void setCommand(String command) {
        this.command = command;
    }
}

class IbeLogValue implements MetricValue{

    private String time;
    private String hostname;
    private int period;
    private double tps;
    private int maxResponseTime;
    private int minResponseTime;
    private int aveResponseTime;

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

    public int getPeriod() {
        return period;
    }

    public void setPeriod(int period) {
        this.period = period;
    }

    public double getTps() {
        return tps;
    }

    public void setTps(double tps) {
        this.tps = tps;
    }

    public int getMaxResponseTime() {
        return maxResponseTime;
    }

    public void setMaxResponseTime(int maxResponseTime) {
        this.maxResponseTime = maxResponseTime;
    }

    public int getMinResponseTime() {
        return minResponseTime;
    }

    public void setMinResponseTime(int minResponseTime) {
        this.minResponseTime = minResponseTime;
    }

    public int getAveResponseTime() {
        return aveResponseTime;
    }

    public void setAveResponseTime(int aveResponseTime) {
        this.aveResponseTime = aveResponseTime;
    }
}
