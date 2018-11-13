package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key:IP|jboss_tcp|8109
 * value:时间戳|主机名|连接数
 * 10.5.73.45|jboss_tcp|8109   20180517-23:44:01|vm-vmw85689-jbs|1
 * 10.5.73.45|jboss_tcp|8109   20180517-23:46:01|vm-vmw85689-jbs|1
 */

public class JbossTcp implements Metric{
    private String ip;
    private String metric;
    private int port;
    private List<JbossTcpValue> jbossTcpValues = new ArrayList<>();


    @Override
    public void addValue(MetricValue metricValue) {
        jbossTcpValues.add((JbossTcpValue) metricValue);
    }

    public List<JbossTcpValue> getJbossTcpValues() {
        return jbossTcpValues;
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

    public int getPort() {
        return port;
    }

    public void setPort(int port) {
        this.port = port;
    }
}


class JbossTcpValue implements MetricValue{
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