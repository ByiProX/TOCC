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
                    System.out.println("本条记录错误：" + line);
                } else {
                    Map kv = getKV(line);
                    jedis.rpush(kv.get("key").toString(), kv.get("value").toString());
                }

            }
        } catch (Exception e) {
            System.out.println(">>>>>" + e);
        }

    }

    private static void parseRedis2JsonTest(Jedis jedis) {
        Set<String> keys = jedis.keys("*");

        Out out;
        out = new Out("ans.json");
        Map<String, List> map = new HashMap<>();
        for (Object key : keys) {
            map.put(key.toString(), jedis.lrange(key.toString(), 0, -1));

        }
        String ans = JSON.toJSONString(map);
        out.println(ans);

        out.close();

    }

    private static void parseRedis2Json(Jedis jedis, String fileName) throws IllegalAccessException,
            InstantiationException, ClassNotFoundException, NoSuchMethodException, InvocationTargetException {
        Set redisKeys = jedis.keys("*");

        Out out = new Out(fileName);

        Map<String, Metric> metricMap = new HashMap<>();

        for (Object redisKey : redisKeys) {
            List<String> redisValue = jedis.lrange(redisKey.toString(), 0, -1);
            Metric metricObj = createMetricInstance(redisKey, redisValue);
            metricMap.put(redisKey.toString().trim().split("[|]")[1], metricObj);
        }
        String jsonString = JSON.toJSONString(metricMap);
        out.println(jsonString);

        out.close();

    }

    private static Metric createMetricInstance(Object redisKey, List<String> redisValue) throws ClassNotFoundException,
            IllegalAccessException, InstantiationException, NoSuchMethodException, InvocationTargetException {

        String metricMapKey = redisKey.toString().trim().split("[|]")[1];

        System.out.println(metricMapKey);
        String clsName = getTrueClsName(metricMapKey);

        System.out.println(clsName);

        Class cls = Class.forName(Config.PACKAGE_NAME + clsName);
        Constructor<?> constructor = cls.getDeclaredConstructor(Object.class, List.class);
//        System.out.println("i am in now ....");
//        Metric metric  = (Metric) constructor.newInstance(redisKey, redisValue);
//        System.out.println(metric.getMetric());
        return (Metric) constructor.newInstance(redisKey, redisValue);

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

        //1. 将txt数据导入redis
        RedisIO.parseTXT2Redis("localhost",6379,"./valuefull.txt");
        Jedis jedis = connectRedisDB("localhost", 6379);
        String fileName = "data.json";

        RedisIO.parseRedis2Json(jedis, fileName);




    }


}
