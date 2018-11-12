package com.travelsky.redis;

import com.alibaba.fastjson.JSON;
import redis.clients.jedis.Jedis;

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

    private static void parseRedis2Json(Jedis jedis){
        Set keys = jedis.keys("*");
        System.out.println(keys);

        Out out;
        out = new Out("ans.json");
        for (Object key : keys) {
            Map<String, List> map= new HashMap<>();
            map.put(key.toString(), jedis.lrange(key.toString(),0,-1));

            String ans = JSON.toJSONString(map);
            out.println(ans);
        }

        out.close();

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


    public static void main(String[] args) {
        //1. 将txt数据导入redis
//        RedisIO.parseTXT2Redis("localhost",6379,"./value.txt");

        Jedis jedis = connectRedisDB("localhost", 6379);

        RedisIO.parseRedis2Json(jedis);





    }


}
