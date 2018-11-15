package com.travelsky.redis;

import java.net.Inet4Address;
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

    public JbossTcp(Object redisKey, List<String> redisValue){
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        port = Integer.parseInt(argList[2]);
        for (String value: redisValue) {
            String[] valueList = value.split("[|]");

            JbossTcpValue jbossTcpValue = new JbossTcpValue();

            jbossTcpValue.setTime(valueList[0]);
            jbossTcpValue.setHostname(valueList[1]);
            jbossTcpValue.setConnectNum(Integer.parseInt(valueList[2]));

            jbossTcpValues.add(jbossTcpValue);

        }
    }

    public JbossTcp(){}

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
    private int connectNum;

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

    public int getConnectNum() {
        return connectNum;
    }

    public void setConnectNum(int connectNum) {
        this.connectNum = connectNum;
    }
}