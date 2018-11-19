package com.travelsky.redis;

public class RedisOffsetRecorder {
    private Long apacheLog;
    private Long appachePort;
    private Long cpuInfo;
    private Long ibeLog;
    private Long iops;
    private Long ipcq;
    private Long jboss;
    private Long jbosstcp;
    private Long jdbc;
    private Long memInfo;
    private Long network;
    private Long swapInfo;
    private Long threadPool;
    private Long todtps;
    private Long tuxserCall;


    public Long getApacheLogOffset() {
        return apacheLog;
    }

    public void setApacheLog(Long apacheLog) {
        this.apacheLog = apacheLog;
    }

    public Long getAppachePortOffset() {
        return appachePort;
    }

    public void setAppachePort(Long appachePort) {
        this.appachePort = appachePort;
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

    public Long getJbossOffset() {
        return jboss;
    }

    public void setJboss(Long jboss) {
        this.jboss = jboss;
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
