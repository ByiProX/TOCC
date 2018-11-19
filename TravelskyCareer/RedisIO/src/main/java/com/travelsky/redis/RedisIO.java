package com.travelsky.redis;

import com.alibaba.fastjson.JSON;
import redis.clients.jedis.Jedis;


import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;


public class RedisIO {

    private static void parseTXT2Redis(String host, int port, String pathOfValueFile) {
        In in;
        in = new In(pathOfValueFile);
        try (Jedis jedis = connectRedisDB(host, port)) {
            while (!in.isEmpty()) {
                String line = in.readLine();
                if (!isCorrectLineFormat(line)) {
                    //此处可以打印错误日志
                    System.out.println("本条记录存在错误：" + line);
                } else {
                    Map kv = getKV(line);
                    jedis.rpush(kv.get("key").toString(), kv.get("value").toString());
                }

            }
        } catch (Exception e) {
            System.out.println(">>>>>" + e);
        }

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


    private static boolean isCorrectLineFormat(String line) {
        String[] parseList = line.trim().split("[ \t]+");
        return parseList.length == 2;
    }

    private static Map getKV(String line) {
        String[] parseList = line.trim().split("[ \t]+");
        Map<String, String> hashMap = new HashMap<>();
        hashMap.put("key", parseList[0]);
        hashMap.put("value", parseList[1]);
        return hashMap;
    }

    private static Jedis connectRedisDB(String host, int port) {
        return new Jedis(host, port);
    }


    public static void main(String[] args) throws ClassNotFoundException,
            NoSuchMethodException, InvocationTargetException,
            IllegalAccessException, InstantiationException {

//        Jedis jedis = connectRedisDB(redisHost, redisPort);
        //1. 将txt数据导入redis
//        RedisIO.parseTXT2Redis("localhost",6379,"./value.txt");

        String redisHost = "localhost";
        int redisPort = 6379;
        String fileName = "data.json";

        RedisIO.parseRedis2JsonFile(redisHost, redisPort, fileName);

        System.out.println(RedisIO.parseRedis2JsonString(redisHost, redisPort));
        System.out.println(">>>>>>>>>>>>>");
//        System.out.println(RedisIO.parseRedis2JsonObj(redisHost, redisPort));


    }


}

