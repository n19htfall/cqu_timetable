import os
import sys
import re
import pandas as pd
import warnings

from datetime import datetime, timedelta
from timetable import Timetable, str_to_date, set_semester_start
from pathlib import Path
from typing import List


def find_xlsx_files(root_dir=".") -> List[str]:
    xlsx_files = []
    root_path = Path(root_dir)
    try:
        for file_path in root_path.rglob("*.xlsx"):
            xlsx_files.append(str(file_path.absolute()))
    except PermissionError as e:
        print(f"警告: 无法访问某些目录: {e}")
    except Exception as e:
        print(f"发生错误: {e}")
    return xlsx_files


def init() -> Timetable:
    tt = load_timetable()
    if tt is None or tt.courses == []:
        print("\033[31m课表为空! 请确认课表配置。\033[0m")
        sys.exit()
    return tt


def read_excel_first_row(file_path):
    try:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = pd.read_excel(file_path)
        headers = df.columns.tolist()
        first_row = df.iloc[0].tolist()
        first_row_with_headers = df.iloc[0].to_dict()
        return {
            "headers": headers,
            "first_row": first_row,
            "first_row_with_headers": first_row_with_headers,
        }
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return None


def find_timetable_manually():
    print("\033[31m课表读取失败! (输入“q”退出)\033[0m")
    tt_path = input("课表文件路径: ")
    if tt_path == "q" or tt_path == "quit":
        sys.exit()
    if os.name == "nt":
        path = tt_path
        if tt_path[0] == "&":
            pattern = r"'(.*)'"
            match = re.search(pattern, tt_path)
            if match:
                path = match.group(1)
        elif tt_path[0] in ['"', "'"] and tt_path[-1] == tt_path[0]:
            path = tt_path[1:-1]
        os.system('copy "' + path + '" "timetable.xlsx"')
    else:
        os.system("cp " + tt_path + " timetable.xlsx")
    return Timetable("timetable.xlsx")


def load_timetable() -> Timetable:
    if os.path.exists("timetable.xlsx"):
        return Timetable("timetable.xlsx")
    xlsx_files = find_xlsx_files()
    if not xlsx_files:
        return find_timetable_manually()
    for f in xlsx_files:
        res = read_excel_first_row(f)
        if "课表" not in res["headers"] or res["first_row"] != [
            "课程名称",
            "教学班号",
            "上课时间",
            "上课地点",
            "上课教师",
        ]:
            continue
        return Timetable(f)
    return find_timetable_manually()


def menu(timetable: Timetable) -> str:
    print(f"\033[93mCQU Timetable " + datetime.now().strftime("%Y-%m-%d") + "\033[0m")
    print("1. 浏览课表")
    print("2. 下一节课")
    print("3. 查询某天的课")
    print("4. 导出ics文件")
    print("5. 设置学期时间")
    print("q. 退出\n")
    print(
        f"\033[93m{timetable.get_semester_name()}: {tt.get_semester_start_in_config()}开始"
    )
    print("-------------------------------------\033[0m")
    choice = input("输入：")
    return choice


def browse() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    now = datetime.now()
    tt.find_one_day(now.strftime("%Y-%m-%d"))
    while True:
        print("\033[93m-------------------------------------\033[0m")
        print("\033[93m浏览课表🚩\033[0m")
        print("输入日期 或者")
        print("h: 上一周 j: 上一天 k: 下一天 l: 下一周 ~: 回到今天 q: 退出")
        op = input("输入：")
        os.system("cls" if os.name == "nt" else "clear")
        if str_to_date(op) is not None:
            tt.find_one_day(op)
            now = str_to_date(op)
        else:
            match_rule = re.match(r"^[hjkl]+$", op)
            if op == "~" or op == ".":
                now = datetime.now()
                tt.find_one_day(now.strftime("%Y-%m-%d"))
            elif op == "q" or op == "quit":
                break
            elif match_rule:
                delta = 0
                for ch in op:
                    delta += {"h": -7, "j": -1, "k": 1, "l": 7}[ch]
                now += timedelta(days=delta)
                tt.find_one_day(now.strftime("%Y-%m-%d"))
            elif len(op) == 0:
                tt.find_one_day(now.strftime("%Y-%m-%d"))
            elif len(op) > 1:
                if op[:-1].rstrip().isdigit() and op[-1] in ["h", "j", "k", "l"]:
                    delta = 1 if op[-1] in ["j", "k"] else 7
                    now += timedelta(
                        days=int(op[:-1])
                        * (delta if op[-1] == "k" or op[-1] == "l" else -delta)
                    )
                    tt.find_one_day(now.strftime("%Y-%m-%d"))
                else:
                    tt.find_one_day(now.strftime("%Y-%m-%d"))
                    print("\033[31m输入错误!\033[0m")
            else:
                tt.find_one_day(now.strftime("%Y-%m-%d"))
                print("\033[31m输入错误!\033[0m")


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    tt = init()
    os.system("cls" if os.name == "nt" else "clear")
    menu_choice = menu(tt)
    while menu_choice != "q" and menu_choice != "quit":
        need_confirm = True
        if menu_choice == "":
            need_confirm = False
        elif menu_choice == "1":
            browse()
            need_confirm = False
        elif menu_choice == "2":
            tt.next_class()
        elif menu_choice == "3":
            tt.find_one_day(input(f"请输入日期 (如2.26)\n"))
        elif menu_choice == "4":
            tt.export_ics()
            print("\033[93m导出成功!\033[0m")
        elif menu_choice == "5":
            old_day = tt.get_semester_start_in_config()
            os.system("cls" if os.name == "nt" else "clear")
            print(f"\033[93m学期: \033[0m{tt.get_semester_name()}")
            print(
                f"\033[93m第一周的周一日期: \033[0m{tt.get_semester_start_in_config()}"
            )
            print("\033[93m-------------------------------------\033[0m")
            set_semester_start()
            new_day = tt.get_semester_start_in_config()
            if old_day != new_day:
                os.system("cls" if os.name == "nt" else "clear")
                print("检测到时间改变，请重新启动。")
                sys.exit()
        else:
            print("\033[31m输入错误!\033[0m")
        if need_confirm:
            _ = input("输入任意继续...")
        os.system("cls" if os.name == "nt" else "clear")
        menu_choice = menu(tt)
