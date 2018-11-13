package com.travelsky.redis;

import java.util.ArrayList;
import java.util.List;

/**
 * key: ip|ibelog|指令
 * value: 时间|主机名|时间周期|TPS|最大响应时间|最小响应时间|平均响应时间
 * 10.6.151.21|ibelog|AVH   20180517-23:46:01|pe6850d-vmwc5-ibe|60|63.02|1911|130|404
 * 10.6.151.21|ibelog|AVH   20180517-23:48:01|pe6850d-vmwc5-ibe|60|59.25|4451|166|424
 */

public class IbeLog implements Metric{
    private String ip;
    private String metric;
    private String command;
    private List<IbeLogValue> ibeLogValues = new ArrayList<>();


    @Override
    public void addValue(MetricValue metricValue) {
        ibeLogValues.add((IbeLogValue) metricValue);
    }

    public List<IbeLogValue> getIbeLogValues(){
        return ibeLogValues;
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

    public String getCommand() {
        return command;
    }

    public void setCommand(String command) {
        this.command = command;
    }
}

class IbeLogValue implements MetricValue{

//    value: 时间|主机名|时间周期|TPS|最大响应时间|最小响应时间|平均响应时间
//    0.6.151.21|ibelog|AVH   20180517-23:46:01|pe6850d-vmwc5-ibe|60|63.02|1911|130|404

    private String time;
    private String hostname;

}
