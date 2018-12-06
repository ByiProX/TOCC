import time
import random


def get_keys():
    keys = set()
    with open("valuefull.txt") as f:
        while True:
            line = f.readline()
            if len(line) == 0:
                break

            key = line.strip().split(" ")[0]
            keys.add(key)

    return keys


def generate_date():
    timeArray = time.localtime(time.time())
    formatTime = time.strftime("%Y%m%d-%H:%M:%S", timeArray)
    return formatTime


# 122.119.180.82|apache_port   20180517-00:02:08|vm-vmw97020-apc|148
# 10.5.73.45|Threadpool|AutoBOXServer|8109   20180517-00:06:34|VM-VMW85689-JBS|-1|-1|0|100.000000|0.000000
# 122.119.180.82|ApacheLog|new.hnair.com   20180517-00:00:01|vm-vmw97020-apc|66.1|0.7|93917.2|177.5|29192.0
# 10.5.72.5|ipcq   20180517-00:06:01|tr730z53-tod|tode|6|7791|32672|av_comm

def get_3keys():
    key1 = "122.119.180.82|apache_port"
    key2 = "10.5.73.45|Threadpool|AutoBOXServer|8109"
    key3 = "122.119.180.82|ApacheLog|new.hnair.com"
    key4 = "10.5.72.5|ipcq"

    return key1, key2, key3, key4


def generate_value(key):
    key1 = "122.119.180.82|apache_port"
    key2 = "10.5.73.45|Threadpool|AutoBOXServer|8109"
    key3 = "122.119.180.82|ApacheLog|new.hnair.com"
    key4 = "10.5.72.5|ipcq"
    if key == key1:
        return "vm-vmw97020-apc" + "|" + str(random.randint(1, 200))

    if key == key2:
        return "VM-VMW85689-JBS|-1|-1|0|100.000000|" + str(random.random())[:5]

    if key == key3:
        return "vm-vmw97020-apc|66.1|0.7|93917.2|177.5|" + str(random.random())[:5]

    if key == key4:
        return "tr730z53-tod|tode|6|7791|32672|av_comm"


def data_generator():
    keys = get_3keys()
    line_num = 2
    result = set()
    with open("newData.txt", "w") as f:

        for key in keys:
            for i in range(line_num):
                oneLine = key + "  " + generate_date() + "|" + generate_value(key) + "\n"
                result.add(key)
                f.write(oneLine)

    return result


if __name__ == "__main__":
    # print(generate_date())
    # print(get_keys().__len__())
    # print(get_keys())
    # result = data_generator()

    # for i in result:
    #     print(i)

    while True:
        data_generator()
        time.sleep(10)
