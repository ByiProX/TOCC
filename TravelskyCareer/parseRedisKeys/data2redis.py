import time

import redis
import rediscluster
from testRedisDataGenerator import data_generator


def data2rediscluster():
    redisHost = "10.221.170.167"
    redisPort = 7001

    client = rediscluster.StrictRedisCluster(redisHost, redisPort)

    filePath = "newData.txt"

    with open(filePath, "r") as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break

            try:
                key, value = line.strip().split()
                client.rpush(key, value)
                print(key + ":  " + str(client.llen(key)))
            except ValueError:
                continue

        print(">>>>>>>>>>>>>>data2rediscluster finished")
        print()


def data2redis():
    redisHost = "10.221.170.167"
    redisPort = 6379
    client = redis.StrictRedis(redisHost, redisPort)

    filePath = "newData.txt"

    with open(filePath, "r") as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break

            try:
                key, value = line.strip().split()
                client.rpush(key, value)
                print(key + ":  " + str(client.llen(key)))
            except ValueError:
                continue

        print(">>>>>>>>>>>>>>data2redis finished")
        print()


if __name__ == "__main__":
    while True:
        data_generator()
        time.sleep(4)
        data2redis()
        time.sleep(0.1)
        data2rediscluster()
        time.sleep(5)
