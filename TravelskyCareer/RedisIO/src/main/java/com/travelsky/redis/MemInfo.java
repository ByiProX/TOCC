package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|meminfo
 * value:时间|主机名|总量|使用|剩余|使用率|剩余率
 * 10.5.72.5|meminfo 20180517-23:40:01|tr730z53-tod|128948|61874|67074|47.98|52.02
 * 10.5.72.5|meminfo   20180517-23:42:01|tr730z53-tod|128949|61875|67074|47.98|52.02
 */

public class MemInfo implements Metric {

    private String ip;
    private String metric;
    private List<MemInfoValue> memInfoValues = new ArrayList<>();

    public MemInfo(Object redisKey, List<String> redisValue) {
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        for (String value : redisValue) {
            String[] valueList = value.split("[|]");

            MemInfoValue memInfoValue = new MemInfoValue();
            memInfoValue.setTime(valueList[0]);
            memInfoValue.setHostname(valueList[1]);
            memInfoValue.setTotalNum(Integer.parseInt(valueList[2]));
            memInfoValue.setUsage(Integer.parseInt(valueList[3]));
            memInfoValue.setFree(Integer.parseInt(valueList[4]));
            memInfoValue.setUsageRatio(Double.parseDouble(valueList[5]));
            memInfoValue.setSurplusRatio(Double.parseDouble(valueList[6]));

            memInfoValues.add(memInfoValue);
        }
    }

    public MemInfo() {
    }


    @Override
    public void addValue(MetricValue metricValue) {
        memInfoValues.add((MemInfoValue) metricValue);
    }


    public List<MemInfoValue> getMemInfoValues() {
        return memInfoValues;
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

class MemInfoValue implements MetricValue {
    /**
     * value:时间|主机名|总量|使用|剩余|使用率|剩余率
     * 20180517-23:40:01|tr730z53-tod|128948|61874|67074|47.98|52.02
     */

    private String time;
    private String hostname;
    private long totalNum;
    private long usage;
    private long free;
    private double usageRatio;
    private double surplusRatio;


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

    public long getTotalNum() {
        return totalNum;
    }

    public void setTotalNum(long totalNum) {
        this.totalNum = totalNum;
    }

    public long getUsage() {
        return usage;
    }

    public void setUsage(long usage) {
        this.usage = usage;
    }

    public long getFree() {
        return free;
    }

    public void setFree(long free) {
        this.free = free;
    }

    public double getUsageRatio() {
        return usageRatio;
    }

    public void setUsageRatio(double usageRatio) {
        this.usageRatio = usageRatio;
    }

    public double getSurplusRatio() {
        return surplusRatio;
    }

    public void setSurplusRatio(double surplusRatio) {
        this.surplusRatio = surplusRatio;
    }
}
