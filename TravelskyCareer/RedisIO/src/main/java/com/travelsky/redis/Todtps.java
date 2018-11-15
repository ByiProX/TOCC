package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|todtps|service
 * value:时间|主机名|TPS
 * 10.5.72.5|todtps|av_comm   20180517-23:48:01|tr730z53-tod|91.8083
 * 10.5.72.5|todtps|av_comm   20180517-23:50:01|tr730z53-tod|89.8333
 */


public class Todtps implements Metric {
    private String ip;
    private String metric;
    private String service;
    private List<TodtpsValue> todtpsValues = new ArrayList<>();


    public Todtps(Object redisKey, List<String> redisValue) {
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        service = argList[2];
        for (String value : redisValue) {
            String[] valueList = value.split("[|]");

            TodtpsValue todtpsValue = new TodtpsValue();
            todtpsValue.setTime(valueList[0]);
            todtpsValue.setHostname(valueList[1]);
            todtpsValue.setTps(Double.parseDouble(valueList[2]));

            todtpsValues.add(todtpsValue);

        }
    }


    public Todtps() {
    }

    @Override
    public void addValue(MetricValue metricValue) {
        todtpsValues.add((TodtpsValue) metricValue);
    }

    public List<TodtpsValue> getTodtpsValues() {
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

    public String getService() {
        return service;
    }

    public void setService(String service) {
        this.service = service;
    }
}


class TodtpsValue implements MetricValue {
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
