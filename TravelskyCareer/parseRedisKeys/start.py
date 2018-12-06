ipList = set()
metricList = set()
with open("valuefull.txt") as f:
    while True:
        line = f.readline()
        if len(line) == 0:
            break

        key = line.strip().split(" ")[0]
        ipList.add(key.split("|", 1)[0])
        metricList.add(key.split("|", 1)[1])

print(ipList)

print(metricList)

# a = "10.5.73.45|jdbc|AutoBOXServer|java:/datasources/AutoBOX   20180517-00:00:59|VM-VMW85689-JBS|50|0|50|0.000000|100.000000"
# print(a.split("   ")[0].split("|", 1))
