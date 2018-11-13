package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|TUXSerCall|service名称
 * value:时间|主机名|TPS
 * 10.6.156.9|TUXSerCall|TUMSINTAVSE   20180517-23:44:33|v490a9-tux|0.00
 * 10.6.156.9|TUXSerCall|TUMSINTAVSE   20180517-23:46:39|v490a9-tux|0.00
 */

public class TUXSerCall implements Metric{
    private String ip;
    private String metric;
    private String service;
    private List<TUXSerCallValue> tuxSerCallValues = new ArrayList<>();


    @Override
    public void addValue(MetricValue metricValue) {
        tuxSerCallValues.add((TUXSerCallValue) metricValue);
    }

    public List<TUXSerCallValue> getTuxSerCallValues() {
        return tuxSerCallValues;
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

    public String getService() {
        return service;
    }

    public void setService(String service) {
        this.service = service;
    }
}

class TUXSerCallValue implements MetricValue{
    private String time;
    private String hostname;
    private double tps;


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
}
