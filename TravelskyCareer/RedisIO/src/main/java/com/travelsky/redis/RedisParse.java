package com.travelsky.redis;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import redis.clients.jedis.Jedis;

import javax.sound.midi.Soundbank;
import java.io.File;
import java.io.IOException;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;


public class RedisParse {

    private static void saveRedisValueOffset2Local(Jedis jedis, Set redisKeys) {
        JSONObject json = JSONObject.parseObject("{}");

        for (Object redisKey : redisKeys) {
            String realRedisKey = redisKey.toString().split("[|]")[1];
            json.put(realRedisKey, jedis.llen(redisKey.toString()));
        }
        String fileName = "./redisValueOffsetRecord.db";
        Out out = new Out(fileName);

        String jsonString = JSON.toJSONString(json);
        out.println(jsonString);

        out.close();


    }

    private static Map<String, Object> createRedisMetricMap(String redisHost, int redisPort) throws
            ClassNotFoundException, NoSuchMethodException, InvocationTargetException,
            InstantiationException, IllegalAccessException {

        Map<String, Metric> metricMap = createMetricMap(redisHost, redisPort);
        HashMap<String, Object> redisMetricMap = new HashMap<>();
        redisMetricMap.put("redisHost", redisHost);
        redisMetricMap.put("redisPort", redisPort);
        redisMetricMap.put("msgData", metricMap);

        return redisMetricMap;
    }

    private static Map<String, Metric> createMetricMap(String redisHost, int redisPort) throws
            ClassNotFoundException, NoSuchMethodException, InvocationTargetException,
            InstantiationException, IllegalAccessException {

        Jedis jedis = connectRedisDB(redisHost, redisPort);
        Set redisKeys = jedis.keys("*");
        saveRedisValueOffset2Local(jedis, redisKeys);
        Map<String, Metric> metricMap = new HashMap<>();

        for (Object redisKey : redisKeys) {
            List<String> redisValue = jedis.lrange(redisKey.toString(), 0, -1);
            Metric metricObj = createMetricInstance(redisKey, redisValue);
            metricMap.put(redisKey.toString().trim().split("[|]")[1], metricObj);
        }
        jedis.close();
        return metricMap;
    }

    private static Metric createMetricInstance(Object redisKey, List<String> redisValue) throws ClassNotFoundException,
            IllegalAccessException, InstantiationException, NoSuchMethodException, InvocationTargetException {

        String metricMapKey = redisKey.toString().trim().split("[|]")[1];
//        System.out.println(metricMapKey);

        String clsName = getTrueClsName(metricMapKey);
//        System.out.println(clsName);


        Class cls = Class.forName(Config.PACKAGE_NAME + clsName);
        Constructor<?> constructor = cls.getDeclaredConstructor(Object.class, List.class);
        return (Metric) constructor.newInstance(redisKey, redisValue);

    }


    private static void parseRedis2JsonFile(String redisHost, int redisPort, String fileName) throws
            IllegalAccessException, InstantiationException,
            ClassNotFoundException, NoSuchMethodException, InvocationTargetException {

        Map<String, Object> metricMap = createRedisMetricMap(redisHost, redisPort);

        Out out = new Out(fileName);

        String jsonString = JSON.toJSONString(metricMap);
        out.println(jsonString);

        out.close();

    }

    private static String parseRedis2JsonString(String redisHost, int redisPort) throws
            ClassNotFoundException, NoSuchMethodException, InstantiationException,
            IllegalAccessException, InvocationTargetException {

        Map<String, Object> metricMap = createRedisMetricMap(redisHost, redisPort);
        return JSON.toJSONString(metricMap);
    }


    private static JSON parseRedis2JsonObj(String redisHost, int redisPort) throws
            IllegalAccessException, InstantiationException,
            ClassNotFoundException, NoSuchMethodException, InvocationTargetException {

        Map<String, Object> metricMap = createRedisMetricMap(redisHost, redisPort);

        return (JSON) JSON.toJSON(metricMap);
    }


    private static String getTrueClsName(String metricMapKey) {
        switch (metricMapKey) {
            case "ApacheLog":
                return "ApacheLog";
            case "apache_port":
                return "ApachePort";
            case "cpuinfo":
                return "CpuInfo";
            case "ibelog":
                return "IbeLog";
            case "iops":
                return "IOps";
            case "ipcq":
                return "Ipcq";
            case "jboss_tcp":
                return "JbossTcp";
            case "jdbcpool":
                return "JdbcPool";
            case "jdbc":
                return "JdbcPool";
            case "meminfo":
                return "MemInfo";
            case "network":
                return "Network";
            case "swapinfo":
                return "SwapInfo";
            case "Threadpool":
                return "ThreadPool";
            case "todtps":
                return "Todtps";
            case "TUXSerCall":
                return "TUXSerCall";

            default:
                System.out.println("么有匹配到类对象的名字");
                return null;
        }
    }


    private static Jedis connectRedisDB(String host, int port) {
        return new Jedis(host, port);
    }


    public static void main(String[] args) throws ClassNotFoundException,
            NoSuchMethodException, InvocationTargetException,
            IllegalAccessException, InstantiationException, IOException {


        String redisHost = "127.0.0.1";
        int redisPort = 6379;
        String fileName = "data.json";

        RedisParse.parseRedis2JsonFile(redisHost, redisPort, fileName);

        System.out.println(RedisParse.parseRedis2JsonString(redisHost, redisPort));
        System.out.println(">>>>>>>>>>>>>");
//        System.out.println(RedisIO.parseRedis2JsonObj(redisHost, redisPort));

        String str = "{\"redisPort\":6379,\"redis_Host\":\"127.0.0.1\"}";
        JSONObject json = JSONObject.parseObject(str);
        JSONObject json1 = JSONObject.parseObject("{}");
        json1.put("a", 1);
        System.out.println(json1);
        ToObj o = JSON.toJavaObject(json, ToObj.class);
        System.out.println(o.getRedisHost());
        System.out.println(o.getRedisPortrrrrrrrrrr());

//        In read = new In("./redisValueOffsetRecord.db");
//        String jsonString = read.readAll();
//        System.out.println(jsonString);
//
//        JSONObject jsonObject = JSONObject.parseObject(jsonString);
//
//        System.out.println(jsonObject.containsKey("jboss_tcp"));

//
//        RedisOffsetRecorder ob = JSON.toJavaObject(jsonObject, RedisOffsetRecorder.class);
//        System.out.println(ob.getApacheLogOffset());
//        System.out.println(ob.getIopsOffset());
//        System.out.println(ob.getThreadPoolOffset());
//
//
//        System.out.println(ob.getCpuInfoOffset());



//        String separator = File.separator;
//        String dir = "." + separator + "temp02";
//        String fileNameName = "hello.txt";
//        File file = new File(fileNameName);
//        if (file.exists()) {
//            System.out.println(file.getAbsolutePath());
//            System.out.println(file.getName());
//            System.out.println(file.length());
//        }
//        else {
//            System.out.println(file.getAbsolutePath());
//
//        }
    }


}

class ToObj {
    private String redisHostyy;
    private String redisPort;


    public String getRedisHost() {
        return redisHostyy;
    }

    public void setRedisHost(String redisHost) {
        this.redisHostyy = redisHost;
    }

    public String getRedisPortrrrrrrrrrr() {
        return redisPort;
    }

    public void setRedisPortrrrrrrrrrr(String redisPort) {
        this.redisPort = redisPort;
    }
}


