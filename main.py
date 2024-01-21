from timetable import Timetable, re
from course import datetime, timedelta

import os
import random
import sys

tips = [
    "CQU Timetable",
    "喝杯咖啡吧~☕",
    "休息休息💤",
    "这显然是一个看课表的",
    "在黑暗的时代，群星是否也应熄灭？",
    "未来教会你独处",
    "时间在这里汹涌地流逝",
    "只是一种脆弱的感官把戏",
]

tips_week = [
    "周一周一，我的头七",
    "周二周二，命剩一半",
    "周三周三，续命上班",
    "周四周四，重见天日",
    "周五周五，敲锣打鼓",
    "周六周六，大鱼大肉",
    "周日周日，死期将至",
]


def init() -> Timetable:
    tt = load_timetable()
    if tt.courses == []:
        print("\033[31m课表为空! 请确认课表配置。\033[0m")
        sys.exit()
    if tt.detect_end(datetime.now()):
        os.system("cls" if os.name == "nt" else "clear")
        os.system("python main.py")
    tips.append(tips_week[datetime.now().weekday()])
    return tt


def load_timetable(path="课表.xlsx") -> Timetable:
    if not os.path.exists(path):
        print("\033[31m课表读取失败! (输入“q”退出)\033[0m")
        tt_path = input("请输入课表文件路径: ")
        if tt_path == "q" or tt_path == "quit":
            sys.exit()
        if os.name == "nt":
            os.system('copy "' + tt_path + '" "课表.xlsx"')
        else:
            os.system("cp " + tt_path + " 课表.xlsx")
        tt = load_timetable(tt_path)
    else:
        tt = Timetable(path)
    return tt


def menu() -> str:
    print(f"\033[93m{random.choice(tips)}\033[0m")
    print("1. 浏览课表")
    print("2. 下一节课")
    print("3. 今天的课")
    print("4. 明天的课")
    print("5. 查询某天的课")
    print("q. 退出")
    print("\033[93m-------------------------------------\033[0m")
    choice = input("请输入：")
    return choice


def browse() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.now()
    string = now.strftime("%Y-%m-%d")
    tt.find_one_day(string)
    while True:
        print("\033[93m-------------------------------------\033[0m")
        print("\033[93m浏览课表🚩\033[0m")
        print("h: 上一周 j: 上一天 k: 下一天 l: 下一周 ~: 回到今天 q: 退出")
        operation = input("输入：")
        match_rule = re.match(r"^[hjkl]+$", operation)
        os.system("cls" if os.name == "nt" else "clear")
        if operation == "~":
            now = datetime.now()
            tt.find_one_day(now.strftime("%Y-%m-%d"))
        elif operation == "q":
            break
        elif match_rule:
            delta = 0
            for ch in operation:
                delta += {"h": -7, "j": -1, "k": 1, "l": 7}[ch]
            now += timedelta(days=delta)
            tt.find_one_day(now.strftime("%Y-%m-%d"))
        elif len(operation) > 1:
            if operation[:-1].isdigit() and operation[-1] in [
                "h",
                "j",
                "k",
                "l",
            ]:
                delta = 1 if operation[-1] in ["j", "k"] else 7
                now += timedelta(
                    days=int(operation[:-1])
                    * (
                        delta
                        if operation[-1] == "k" or operation[-1] == "l"
                        else -delta
                    )
                )
                tt.find_one_day(now.strftime("%Y-%m-%d"))
            else:
                print("\033[31m输入错误!\033[0m")
        else:
            print("\033[31m输入错误!\033[0m")


if __name__ == "__main__":
    tt = init()
    try:
        menu_choice = menu()
        while menu_choice != "q" and menu_choice != "quit":
            need_confirm = True
            if menu_choice == "1":
                browse()
                need_confirm = False
            elif menu_choice == "2":
                tt.next_class()
            elif menu_choice == "3":
                tt.today()
            elif menu_choice == "4":
                tt.tomorrow()
            elif menu_choice == "5":
                tt.find_one_day(input(f"请输入日期: "))
            if need_confirm:
                _ = input("输入任意继续...")
            os.system("cls" if os.name == "nt" else "clear")
            menu_choice = menu()
    except KeyboardInterrupt:
        sys.exit()
