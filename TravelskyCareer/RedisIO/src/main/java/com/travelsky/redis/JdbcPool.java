package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|jdbcpool
 * value:时间|主机名|总量|使用|剩余|使用率|剩余率
 * 10.5.73.45|jdbc|AutoBOXServer|java:/datasources/AutoBOX   20180517-01:06:47|VM-VMW85689-JBS|50|0|50|0.000000|100.000000
 * 10.5.73.45|jdbc|AutoBOXServer|java:/datasources/AutoBOX   20180517-01:06:50|VM-VMW85689-JBS|50|0|50|0.000000|100.000000
 * 10.5.73.45|jdbc|AutoBOXServer|java:/datasources/AutoBOX   20180517-01:10:03||50|0|50|0.000000|100.000000
 * 10.5.73.45|jdbc|AutoBOXServer|java:/datasources/AutoBOX   20180517-01:10:12||50|0|50|0.000000|100.000000
 */

public class JdbcPool implements Metric{
    private String ip;
    private String metric;
    private List<JdbcPoolValue> jdbcPoolValues = new ArrayList<>();

    public JdbcPool(Object redisKey, List<String> redisValue){
        String[] argList = redisKey.toString().split("[|]", 2);

        ip = argList[0];
        metric = argList[1];
        for (String value: redisValue) {
            String[] valueList = value.split("[|]");

            JdbcPoolValue jdbcPoolValue = new JdbcPoolValue();
            jdbcPoolValue.setTime(valueList[0]);
            jdbcPoolValue.setHostname(valueList[1]);
            jdbcPoolValue.setTotalNum(Integer.parseInt(valueList[2]));
            jdbcPoolValue.setUsage(Integer.parseInt(valueList[3]));
            jdbcPoolValue.setFree(Integer.parseInt(valueList[4]));
            jdbcPoolValue.setUsageRatio(Double.parseDouble(valueList[5]));
            jdbcPoolValue.setSurplusRatio(Double.parseDouble(valueList[6]));

            jdbcPoolValues.add(jdbcPoolValue);


        }
    }

    public JdbcPool(){}


    @Override
    public void addValue(MetricValue metricValue) {
        jdbcPoolValues.add((JdbcPoolValue) metricValue);
    }

    public List<JdbcPoolValue> getJdbcPoolValues() {
        return jdbcPoolValues;
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

class JdbcPoolValue implements MetricValue{

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
