import bisect
import json
import sys

import matplotlib.pyplot as plt


def get_data() -> list:
    with open("data/20200422.json", "r", encoding="UTF-8") as file:
        json_array = json.loads(file.read())
    return json_array


def analyze_zone():
    json_array = get_data()

    # 绘制小姐姐区域分布柱状图,x轴为地区，y轴为该区域的小姐姐数量

    zones = []
    for star in json_array:
        zone = star["zone"]
        zones.append(zone)
    print(len(zones))
    print(zones)

    zone_list = []
    count_list = []

    for zone in zones:
        if zone not in zone_list:
            count = zones.count(zone)
            zone_list.append(zone)
            count_list.append(count)

    print(zone_list)
    print(count_list)

    # 设置显示中文
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 指定默认字体

    plt.figure(figsize=(20, 15))

    plt.bar(
        range(len(count_list)),
        count_list,
        color="r",
        tick_label=zone_list,
        facecolor="#9999ff",
        edgecolor="white",
        label="Bar Chart",
    )

    # 这里是调节横坐标的倾斜度，rotation是度数，以及设置刻度字体大小
    plt.xticks(rotation=45, fontsize=20)
    plt.yticks(fontsize=20)

    plt.legend()
    plt.title("""《青春有你2》参赛选手""", fontsize=24)
    plt.savefig("work/result/bar_result.jpg")
    plt.show()


def find_position(nums, target):
    position = bisect.bisect_left(nums, target)
    return position


def analyze_weight():
    json_array: list = get_data()

    weight = []
    for star in json_array:
        weight.append(star["weight"][:-2])

    print(weight)
    weight_legend = [0, 45, 50, 55, sys.maxsize]

    weight_list = ["<=45", "45-50", "50-55", ">55"]
    count_list = [0 for _ in range(len(weight_legend))]
    for i in range(len(weight)):
        count_list[find_position(weight_legend, float(weight[i]))] += 1

    count_list = [count / len(weight) for count in count_list]
    count_list = count_list[1:]
    print(count_list)

    # 设置显示中文
    plt.rcParams["font.sans-serif"] = ["SimHei"]  # 指定默认字体

    plt.figure(figsize=(20, 15))

    patches, texts, autotexts = plt.pie(
        count_list,
        labels=weight_list,
        autopct="%1.2f%%",
        shadow=True,
        explode=(0.05, 0.05, 0, 0),
    )

    # 设置刻度字体大小
    plt.setp(texts, fontsize=24)
    plt.setp(autotexts, fontsize=24)

    plt.legend()
    plt.title("""《青春有你2》参赛选手""", fontsize=24)
    plt.savefig("work/result/pie_result.jpg")
    plt.show()


if __name__ == "__main__":
    analyze_zone()
    analyze_weight()
