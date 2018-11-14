package com.travelsky.redis;

import com.alibaba.fastjson.JSON;
import redis.clients.jedis.Jedis;


import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
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
            System.out.println(e);
        }

    }

    private static void parseRedis2JsonTest(Jedis jedis) {
        Set keys = jedis.keys("*");

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

    private static void parseRedis2Json(Jedis jedis) {
        Set keys = jedis.keys("*");

        Out out = new Out("data.json");

        Map<String, Metric> metricMap = new HashMap<>();

        for (Object key : keys) {
            String metricMapKey = key.toString().trim().split("[|]")[1];

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


    public static void main(String[] args) throws ClassNotFoundException, NoSuchMethodException, InvocationTargetException, IllegalAccessException, InstantiationException {
        //1. 将txt数据导入redis
//        RedisIO.parseTXT2Redis("localhost",6379,"./value.txt");

//        Jedis jedis = connectRedisDB("localhost", 6379);

//        RedisIO.parseRedis2JsonTest(jedis);


//        Map<String, Metric> metricMap = new HashMap<>();

        String netstring = "10.5.72.5|network   20180517-00:02:01|tr730z53-tod|7974.95|6728.77";

        String[] parseList = netstring.trim().split("[ \t]+");

        System.out.println(parseList[1]);

        Network network = new Network();
        NetworkValue networkValue = new NetworkValue();

        String ip = parseList[0].trim().split("[|]")[0];
        String cmd = parseList[0].trim().split("[|]")[1];
        String time = parseList[1].trim().split("[|]")[0];
        System.out.println(time);


        String hostname = parseList[1].trim().split("[|]")[1];
        String rxre = parseList[1].trim().split("[|]")[2];
        String txre = parseList[1].trim().split("[|]")[3];

        network.setIp(ip);
        network.setMetric(cmd);
        networkValue.setTime(time);
        networkValue.setHostname(hostname);
        networkValue.setRxre(Double.parseDouble(rxre));
        networkValue.setTxre(Double.parseDouble(txre));
        network.addValue(networkValue);


        String iopsString = "10.5.72.5|iops   20180517-23:48:01|tr730z53-tod|13.93|288.42|0.92";
        String[] parseList1 = iopsString.trim().split("[ \t]+");

        IOps iOps = new IOps();
        IOpsValue iOpsValue = new IOpsValue();
        String ip1 = parseList1[0].trim().split("[|]")[0];
        String cmd1 = parseList1[0].trim().split("[|]")[1];
        String time1 = parseList1[1].trim().split("[|]")[0];
        String hostname1 = parseList1[1].trim().split("[|]")[1];
        String read1 = parseList1[1].trim().split("[|]")[2];
        String write1 = parseList1[1].trim().split("[|]")[3];
        String util1 = parseList1[1].trim().split("[|]")[4];

        iOps.setIp(ip1);
        iOps.setMetric(cmd1);

        iOpsValue.setHostname(hostname1);
        iOpsValue.setTime(time1);
        iOpsValue.setRead(Double.parseDouble(read1));
        iOpsValue.setWrite(Double.parseDouble(write1));
        iOpsValue.setUtil(Double.parseDouble(util1));

        iOps.addValue(iOpsValue);


        Map<String, Metric> metricMap = new HashMap<>();
        metricMap.put("network", network);
        metricMap.put("iops", iOps);


        String jsonString = JSON.toJSONString(metricMap);

        System.out.println(jsonString);


        Class cls = null;

        cls = Class.forName("com.travelsky.redis.Network");
        Metric obj = (Metric) cls.newInstance();
        Method method = cls.getMethod("setIp", String.class);
        method.invoke(obj, "1.2.3.4");

        obj.getIp();
        System.out.println(obj.getIp());






    }


}
