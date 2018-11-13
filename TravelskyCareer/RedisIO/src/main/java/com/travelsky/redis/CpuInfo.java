package com.travelsky.redis;


import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|cpuinfo
 * value: 时间|主机名|user|sys|iowait|idle
 * 10.5.72.5|cpuinfo   20180517-23:46:01|tr730z53-tod|42.14|4.56|0.00|53.30
 * 10.5.72.5|cpuinfo   20180517-23:48:01|tr730z53-tod|43.32|4.52|0.00|52.16
 */

public class CpuInfo implements Metric{
    private String ip;
    private String metric;
    private List<CpuInfoValue> cpuInfoValues = new ArrayList<>();

    @Override
    public void addValue(MetricValue metricValue) {
        cpuInfoValues.add((CpuInfoValue) metricValue);
    }

    public List<CpuInfoValue> getCpuInfoValues(){
        return cpuInfoValues;
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
}

class CpuInfoValue implements MetricValue{
    private String time;
    private String hostname;
    private double user;
    private double sys;
    private double iowait;
    private double idle;

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

    public double getUser() {
        return user;
    }

    public void setUser(double user) {
        this.user = user;
    }

    public double getSys() {
        return sys;
    }

    public void setSys(double sys) {
        this.sys = sys;
    }

    public double getIowait() {
        return iowait;
    }

    public void setIowait(double iowait) {
        this.iowait = iowait;
    }

    public double getIdle() {
        return idle;
    }

    public void setIdle(double idle) {
        this.idle = idle;
    }
}
