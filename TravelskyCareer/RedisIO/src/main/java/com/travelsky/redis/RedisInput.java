package com.travelsky.redis;

import redis.clients.jedis.Jedis;

import java.util.HashMap;
import java.util.Map;

public class RedisInput {

    public static void main(String[] args) {

        String redisHost = "localhost";
        int redisPort = 6379;
        String pathOfValueFile = "value.txt";
        RedisInput.parseTXT2Redis(redisHost,redisPort,pathOfValueFile);
    }

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

    private static Map getKV(String line) {
        String[] parseList = line.trim().split("[ \t]+");
        Map<String, String> hashMap = new HashMap<>();
        hashMap.put("key", parseList[0]);
        hashMap.put("value", parseList[1]);
        return hashMap;
    }



    private static boolean isCorrectLineFormat(String line) {
        String[] parseList = line.trim().split("[ \t]+");
        return parseList.length == 2;
    }


    private static Jedis connectRedisDB(String host, int port) {
        return new Jedis(host, port);
    }
}
