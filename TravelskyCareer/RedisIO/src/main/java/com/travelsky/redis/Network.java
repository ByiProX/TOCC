package com.travelsky.redis;


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
    private String IP;
    private String metric;
    private List<NetworkValue> networkValues = new ArrayList<>();

    public void addValue(NetworkValue networkValue) {
        networkValues.add(networkValue);
    }

    public void setIP(String IP) {
        this.IP = IP;
    }

    public void setMetric(String metric) {
        this.metric = metric;
    }


    public String getIP() {
        return IP;
    }

    public String getMetric() {
        return metric;
    }

    public List<NetworkValue> getNetworkValues() {
        return networkValues;
    }
}


class NetworkValue{

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
