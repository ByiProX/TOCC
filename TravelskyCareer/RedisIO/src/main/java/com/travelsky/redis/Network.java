package com.travelsky.redis;


import com.alibaba.fastjson.JSON;

import java.util.ArrayList;
import java.util.List;

/**
 * network demo
 * key:ip|network
 * value: 时间|主机名|rxre|txre
 * 10.5.72.5|network   20180517-00:00:01|tr730z53-tod|7078.19|6458.21
 * 10.5.72.5|network   20180517-00:02:01|tr730z53-tod|7974.95|6728.77
*/

public class Network implements Metric {
    private String ip;
    private String metric;
    private List<NetworkValue> networkValues = new ArrayList<>();

    public static void main(String[] args){
        Network network = new Network();
        network.setIp("1.1.1.1");
        network.setMetric("network");
        System.out.println(network.getMetric());

        NetworkValue networkValue1 = new NetworkValue();
        networkValue1.setHostname("wkx");
        networkValue1.setTime("2018");
        networkValue1.setRxre(1.);
        networkValue1.setTxre(2.);

        NetworkValue networkValue2 = new NetworkValue();
        networkValue2.setHostname("pyy");
        networkValue2.setTime("2017");
        networkValue2.setRxre(10.);
        networkValue2.setTxre(20.);

        network.addValue(networkValue1);
        network.addValue(networkValue2);

        String jsonString = JSON.toJSONString(network);
        System.out.println(jsonString);
    }

    public void addValue(MetricValue metricValue) {
        networkValues.add((NetworkValue) metricValue);
    }



    public List<NetworkValue> getNetworkValues() {
        return networkValues;
    }

    public String getIp() {
        return ip;
    }

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


class NetworkValue implements MetricValue{

    private String time;
    private String hostname;
    private double rxre;
    private double txre;

    public String getTime() {
        return time;
    }

    public void setTime(String time) {
        this.time = time;
    }

    public String getHostname() {
        return hostname;
    }

    public void setHostname(String hostname) {
        this.hostname = hostname;
    }

    public double getRxre() {
        return rxre;
    }

    public void setRxre(double rxre) {
        this.rxre = rxre;
    }

    public double getTxre() {
        return txre;
    }

    public void setTxre(double txre) {
        this.txre = txre;
    }
}
