package com.travelsky.redis;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import redis.clients.jedis.Jedis;


import java.io.*;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;


public class RedisParse {

    private static RedisOffsetRecorder loadRedisValueOffset() {
        In read = new In("./redisValueOffsetRecord.db");
        String jsonString = read.readAll();
        read.close();

        JSONObject jsonObject = JSONObject.parseObject(jsonString);

        return JSON.toJavaObject(jsonObject, RedisOffsetRecorder.class);
    }

    private static void saveRedisValueOffset2Local(Jedis jedis, Set redisKeys) {
        JSONObject json = JSONObject.parseObject("{}");

        for (Object redisKey : redisKeys) {
            String realRedisKey = redisKey.toString().split("[|]")[1];
            json.put(realRedisKey, jedis.llen(redisKey.toString()));
        }
        String fileName = "./redisValueOffsetRecord.db";

//        try {
//            File f = new File(fileName);
//            FileOutputStream fileOutputStream = new FileOutputStream(f);
//            OutputStreamWriter writer = new OutputStreamWriter(fileOutputStream);
//            String jsonString = JSON.toJSONString(json);
//            writer.write(jsonString);
//
//            fileOutputStream.close();
//
//
//        } catch (IOException e) {
//            e.printStackTrace();
//        }


        Out out = new Out(fileName);

//        String jsonString = JSON.toJSONString(json);
//        out.println(jsonString);
        out.print(json);

        out.close();


    }

    //外层添加Re


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

        //loadRedisValueOffset
        RedisOffsetRecorder redisOffsetRecorder = RedisParse.loadRedisValueOffset();

        Jedis jedis = connectRedisDB(redisHost, redisPort);
        Set redisKeys = jedis.keys("*");
        Map<String, Metric> metricMap = new HashMap<>();


        for (Object redisKey : redisKeys) {

            long offset = redisOffsetRecorder.getValueOffset(redisKey.toString().trim().split("[|]")[1]);
            System.out.println(">>>>>>>>>>>>>>>>>>>>>   " + redisKey.toString().trim().split("[|]")[1] + "  " + offset);
            List<String> redisValue = jedis.lrange(redisKey.toString(), offset, -1);
            Metric metricObj = createMetricInstance(redisKey, redisValue);
            metricMap.put(redisKey.toString().trim().split("[|]")[1], metricObj);
        }
        //saveRedisValueOffset2Local
        RedisParse.saveRedisValueOffset2Local(jedis, redisKeys);

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


    private static String getTrueClsName(String metricMapKey) throws ClassNotFoundException {
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
                throw new ClassNotFoundException("么有匹配到类对象的名字");
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

//        RedisParse.parseRedis2JsonFile(redisHost, redisPort, fileName);

        System.out.println(RedisParse.parseRedis2JsonString(redisHost, redisPort));
//        System.out.println(RedisIO.parseRedis2JsonObj(redisHost, redisPort));


//        RedisOffsetRecorder redisOffsetRecorder = RedisParse.loadRedisValueOffset();
//        System.out.println(redisOffsetRecorder.getJbosstcpOffset());





    }


}



