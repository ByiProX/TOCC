package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|todtps|service
 * value:时间|主机名|TPS
 * 10.5.72.5|todtps|av_comm   20180517-23:48:01|tr730z53-tod|91.8083
 * 10.5.72.5|todtps|av_comm   20180517-23:50:01|tr730z53-tod|89.8333
 */

public class Todtps implements Metric{
    private String ip;
    private String metric;
    private List<TodtpsValue> todtpsValues = new ArrayList<>();

    @Override
    public void addValue(MetricValue metricValue) {
        todtpsValues.add((TodtpsValue) metricValue);
    }

    public List<TodtpsValue> getTodtpsValues(){
        return todtpsValues;
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


class TodtpsValue implements MetricValue{
    private String time;
    private String hostname;
    private String tps;

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

    public String getTps() {
        return tps;
    }

    public void setTps(String tps) {
        this.tps = tps;
    }
}
