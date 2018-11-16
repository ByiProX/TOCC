package com.travelsky.redis;

import javax.xml.bind.PrintConversionEvent;
import java.util.ArrayList;
import java.util.List;

/**
 * key:ip|ipcq
 * value:时间|主机名|user|qNum|qByte|进程号|process
 * 10.5.72.5|ipcq   20180517-22:26:02|tr730z53-tod|tode|5|6651|32644|av_comm
 * 10.5.72.5|ipcq   20180517-22:28:01|tr730z53-tod|tode|1|1786|23828|sc_u_svr
 */


public class Ipcq implements Metric {
    private String ip;
    private String metric;
    private List<IpcqValue> ipcqValues = new ArrayList<>();

    public Ipcq(Object redisKey, List<String> redisValue){
        String[] argList = redisKey.toString().split("[|]");
        ip = argList[0];
        metric = argList[1];
        for (String value: redisValue){
            String[] valueList = value.split("[|]");

            IpcqValue ipcqValue = new IpcqValue();
            ipcqValue.setTime(valueList[0]);
            ipcqValue.setHostname(valueList[1]);
            ipcqValue.setUser(valueList[2]);
            ipcqValue.setqNum(Integer.parseInt(valueList[3]));
            ipcqValue.setqByte(Integer.parseInt(valueList[4]));
            ipcqValue.setPid(Integer.parseInt(valueList[5]));
            ipcqValue.setProcess(valueList[6]);

            ipcqValues.add(ipcqValue);



        }
    }

    public Ipcq(){}

    @Override
    public void addValue(MetricValue metricValue) {
        ipcqValues.add((IpcqValue) metricValue);
    }

    public List<IpcqValue> getApachePortValues() {
        return ipcqValues;
    }

    @Override
    public String getIp() {
        return ip;
    }

    @Override
    public void setIp(String ip) {
        this.ip = ip;
    }

    @Override
    public String getMetric() {
        return metric;
    }

    @Override
    public void setMetric(String metric) {
        this.metric = metric;
    }
}


class IpcqValue implements MetricValue{
    private String time;
    private String hostname;
    private String user;
    private int qNum;
    private int qByte;
    private int pid;
    private String process;

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

    public String getUser() {
        return user;
    }

    public void setUser(String user) {
        this.user = user;
    }

    public int getqNum() {
        return qNum;
    }

    public void setqNum(int qNum) {
        this.qNum = qNum;
    }

    public int getqByte() {
        return qByte;
    }

    public void setqByte(int qByte) {
        this.qByte = qByte;
    }

    public int getPid() {
        return pid;
    }

    public void setPid(int pid) {
        this.pid = pid;
    }

    public String getProcess() {
        return process;
    }

    public void setProcess(String process) {
        this.process = process;
    }
}