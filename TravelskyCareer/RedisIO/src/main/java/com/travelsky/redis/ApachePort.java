package com.travelsky.redis;


import java.util.ArrayList;
import java.util.List;

/**
 * key:IP|apache_port
 * value:时间戳|主机名|连接数
 * 122.119.180.82|apache_port   20180517-23:48:08|vm-vmw97020-apc|154
 * 122.119.180.82|apache_port   20180517-23:50:08|vm-vmw97020-apc|133
 */

public class ApachePort implements Metric{
    private String ip;
    private String metric;
    private List<ApachePortValue> apachePortValues = new ArrayList<>();

    public ApachePort(Object redisKey, List<String> redisValue){
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        for (String value: redisValue){
            String[] valueList = value.split("[|]");

            ApachePortValue apachePortValue = new ApachePortValue();
            apachePortValue.setTime(valueList[0]);
            apachePortValue.setHostname(valueList[1]);
            apachePortValue.setConnectNum(valueList[2]);

            apachePortValues.add(apachePortValue);
        }
    }

    public ApachePort(){}


    @Override
    public void addValue(MetricValue metricValue) {
        apachePortValues.add((ApachePortValue) metricValue);
    }

    public List<ApachePortValue> getApachePortValues() {
        return apachePortValues;
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

class ApachePortValue implements MetricValue{
    private String time;
    private String hostname;
    private String connectNum;

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

    public String getConnectNum() {
        return connectNum;
    }

    public void setConnectNum(String connectNum) {
        this.connectNum = connectNum;
    }
}
