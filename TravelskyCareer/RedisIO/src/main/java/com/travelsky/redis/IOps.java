package com.travelsky.redis;

import org.omg.CORBA.PUBLIC_MEMBER;

import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|iops
 * value: 时间|主机名|读|写|util
 * 0.5.72.5|iops   20180517-23:46:01|tr730z53-tod|13.93|288.42|0.92
 * 10.5.72.5|iops   20180517-23:48:01|tr730z53-tod|13.93|288.42|0.92
 *
 * */

public class IOps implements Metric{

    private String ip;
    private String metric;
    private List<IOpsValue> iOpsValues = new ArrayList<>();

    public IOps(Object redisKey, List<String> redisValue){
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        for (String value: redisValue) {
            String[] valueList = value.split("[|]");

            IOpsValue iOpsValue = new IOpsValue();
            iOpsValue.setTime(valueList[0]);
            iOpsValue.setHostname(valueList[1]);
            iOpsValue.setRead(Double.parseDouble(valueList[2]));
            iOpsValue.setWrite(Double.parseDouble(valueList[3]));
            iOpsValue.setUtil(Double.parseDouble(valueList[4]));

            iOpsValues.add(iOpsValue);

        }
    }

    public IOps(){}


    @Override
    public void addValue(MetricValue metricValue) {
        iOpsValues.add((IOpsValue) metricValue);
    }

    public List<IOpsValue> getiOpsValues(){
        return iOpsValues;
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

class IOpsValue implements MetricValue{
    private String time;
    private String hostname;
    private double read;
    private double write;
    private double util;


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

    public double getRead() {
        return read;
    }

    public void setRead(double read) {
        this.read = read;
    }

    public double getWrite() {
        return write;
    }

    public void setWrite(double write) {
        this.write = write;
    }

    public double getUtil() {
        return util;
    }

    public void setUtil(double util) {
        this.util = util;
    }
}
