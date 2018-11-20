package com.travelsky.redis;

public class RedisOffsetRecorder {
    private long apacheLog;
    private long apachePort;
    private long cpuInfo;
    private long ibeLog;
    private long iops;
    private long ipcq;
    private long jbosstcp;
    private long jdbc;
    private long memInfo;
    private long network;
    private long swapInfo;
    private long threadPool;
    private long todtps;
    private long tuxserCall;


    public long getValueOffset(String metricMapKey) {
        switch (metricMapKey) {
            case "ApacheLog":
                return getApacheLogOffset();
            case "apache_port":
                return getApachePortOffset();
            case "cpuinfo":
                return getCpuInfoOffset();
            case "ibelog":
                return getIbeLogOffset();
            case "iops":
                return getIopsOffset();
            case "ipcq":
                return getIpcqOffset();
            case "jboss_tcp":
                return getJbosstcpOffset();
            case "jdbcpool":
                return getJdbcOffset();
            case "jdbc":
                return getJdbcOffset();
            case "meminfo":
                return getMemInfoOffset();
            case "network":
                return getNetworkOffset();
            case "swapinfo":
                return getSwapInfoOffset();
            case "Threadpool":
                return getThreadPoolOffset();
            case "todtps":
                return getTodtpsOffset();
            case "TUXSerCall":
                return getTuxserCallOffset();

            default:
                System.out.println("么有匹配到类对象的名字");
                return Long.parseLong(null);
        }
    }


    public Long getApacheLogOffset() {
        return apacheLog;
    }

    public void setApacheLog(Long apacheLog) {
        this.apacheLog = apacheLog;
    }

    public Long getApachePortOffset() {
        return apachePort;
    }

    public void setApachePort(Long apachePort) {
        this.apachePort = apachePort;
    }

    public Long getCpuInfoOffset() {
        return cpuInfo;
    }

    public void setCpuInfo(Long cpuInfo) {
        this.cpuInfo = cpuInfo;
    }

    public Long getIbeLogOffset() {
        return ibeLog;
    }

    public void setIbeLog(Long ibeLog) {
        this.ibeLog = ibeLog;
    }

    public Long getIopsOffset() {
        return iops;
    }

    public void setIops(Long iops) {
        this.iops = iops;
    }

    public Long getIpcqOffset() {
        return ipcq;
    }

    public void setIpcq(Long ipcq) {
        this.ipcq = ipcq;
    }

    public Long getJbosstcpOffset() {
        return jbosstcp;
    }

    public void setJbosstcp(Long jbosstcp) {
        this.jbosstcp = jbosstcp;
    }

    public Long getJdbcOffset() {
        return jdbc;
    }

    public void setJdbc(Long jdbc) {
        this.jdbc = jdbc;
    }

    public Long getMemInfoOffset() {
        return memInfo;
    }

    public void setMemInfo(Long memInfo) {
        this.memInfo = memInfo;
    }

    public Long getNetworkOffset() {
        return network;
    }

    public void setNetwork(Long network) {
        this.network = network;
    }

    public Long getSwapInfoOffset() {
        return swapInfo;
    }

    public void setSwapInfo(Long swapInfo) {
        this.swapInfo = swapInfo;
    }

    public Long getThreadPoolOffset() {
        return threadPool;
    }

    public void setThreadPool(Long threadPool) {
        this.threadPool = threadPool;
    }

    public Long getTodtpsOffset() {
        return todtps;
    }

    public void setTodtps(Long todtps) {
        this.todtps = todtps;
    }

    public Long getTuxserCallOffset() {
        return tuxserCall;
    }

    public void setTuxserCall(Long tuxserCall) {
        this.tuxserCall = tuxserCall;
    }

}
