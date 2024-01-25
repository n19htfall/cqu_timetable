import os
import sys

from course import datetime, timedelta
from timetable import Timetable, re


def init() -> Timetable:
    tt = load_timetable()
    if tt.courses == []:
        print("\033[31m课表为空! 请确认课表配置。\033[0m")
        sys.exit()
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
    print(f"\033[93mCQU Timetable " + datetime.now().strftime("%Y-%m-%d") + "\033[0m")
    print("1. 浏览课表")
    print("2. 最近的课")
    print("3. 今天的课")
    print("4. 查询某天的课")
    print("5. 导出ics文件")
    print("q. 退出")
    print("\033[93m-------------------------------------\033[0m")
    choice = input("请输入：")
    return choice


def browse() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.now()
    tt.find_one_day(now.strftime("%Y-%m-%d"), display=True)
    while True:
        print("\033[93m-------------------------------------\033[0m")
        print("\033[93m浏览课表🚩\033[0m")
        print("输入日期 或者")
        print("h: 上一周 j: 上一天 k: 下一天 l: 下一周 ~: 回到今天 q: 退出")
        operation = input("输入：")
        os.system("cls" if os.name == "nt" else "clear")
        if tt.str_to_date(operation) is not None:
            tt.find_one_day(operation, display=True)
            now = tt.str_to_date(operation)
        else:
            match_rule = re.match(r"^[hjkl]+$", operation)
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
                tt.find_one_day(now.strftime("%Y-%m-%d"), display=True)
            elif len(operation) == 0:
                tt.find_one_day(now.strftime("%Y-%m-%d"), display=True)
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
                    tt.find_one_day(now.strftime("%Y-%m-%d"), display=True)
                    print("\033[31m输入错误!\033[0m")
            else:
                tt.find_one_day(now.strftime("%Y-%m-%d"), display=True)
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
                tt.find_one_day(input(f"请输入日期: "), display=True)
            elif menu_choice == "5":
                tt.export_ics()
                print("\033[93m导出成功!\033[0m")
            else:
                print("\033[31m输入错误!\033[0m")
            if need_confirm:
                _ = input("输入任意继续...")
            os.system("cls" if os.name == "nt" else "clear")
            menu_choice = menu()
    except KeyboardInterrupt:
        sys.exit()
