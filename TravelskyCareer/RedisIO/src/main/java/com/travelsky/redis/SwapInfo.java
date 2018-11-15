package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|swapinfo
 * value: 时间|主机名|总量|使用|剩余 |使用率|剩余率
 * 122.119.180.82|swapinfo   20180517-23:48:01|vm-vmw97020-apc|4095|0|4095|0.00|100.00
 * 122.119.180.82|swapinfo   20180517-23:50:01|vm-vmw97020-apc|4095|0|4095|0.00|100.00
 */

public class SwapInfo implements Metric{
    private String ip;
    private String metric;
    private List<SwapInfoValue> swapInfoValues = new ArrayList<>();

    public SwapInfo(Object redisKey, List<String> redisValue){
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        for (String value: redisValue) {
            String[] valueList = value.split("[|]");

            SwapInfoValue swapInfoValue = new SwapInfoValue();
            swapInfoValue.setTime(valueList[0]);
            swapInfoValue.setHostname(valueList[1]);
            swapInfoValue.setTotalNum(Long.parseLong(valueList[2]));
            swapInfoValue.setUsage(Long.parseLong(valueList[3]));
            swapInfoValue.setFree(Long.parseLong(valueList[4]));
            swapInfoValue.setUsageRatio(Double.parseDouble(valueList[5]));
            swapInfoValue.setSurplusRatio(Double.parseDouble(valueList[6]));

            swapInfoValues.add(swapInfoValue);
        }
    }

    public SwapInfo(){}


    @Override
    public void addValue(MetricValue metricValue) {
        swapInfoValues.add((SwapInfoValue) metricValue);
    }

    public List<SwapInfoValue> getSwapInfoValues() {
        return swapInfoValues;
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

class SwapInfoValue implements MetricValue{
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
