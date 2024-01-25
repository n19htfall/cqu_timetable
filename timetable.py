import pandas as pd
import re
import warnings
import shutil
import os
import sys

from course import Course
from course import configparser
from course import datetime, timedelta
from icalendar import Calendar
from urllib.parse import quote
from visualization import view_timetable, view_next_class


class Timetable:
    def __init__(self, path: str) -> None:
        self.courses: list[Course] = []
        self.cal = Calendar()
        timetable_file = path
        try:
            with open(timetable_file):
                pass
        except FileNotFoundError:
            print("\033[31m课表文件不存在!\033[0m")
            return
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            df = pd.read_excel(timetable_file, engine="openpyxl")
        if detect_end(datetime.now()):
            os.system("cls" if os.name == "nt" else "clear")
            os.system("python main.py")
            sys.exit()
        rows_as_lists = []
        for _, row in df.iterrows():
            row_list = list(row)
            rows_as_lists.append(row_list)
        for row in rows_as_lists:
            if row[0] == "课程名称":
                continue
            if len(row) != 5:
                continue
            lst = [str(item) if isinstance(item, str) else "" for item in row]
            this_course = Course(lst[0], lst[1], lst[2], lst[3], lst[4])
            this_course.create_event_in_ical(self.cal, SEMESTER_START)
            self.courses += [this_course]

    def course_in_week(self, week: int) -> list[Course]:
        return [c for c in self.courses if week in c.week_range]

    def course_in_day(self, week: int, day: int) -> list[Course]:
        return [c for c in self.course_in_week(week) if c.weekday == day]

    def str_to_date(self, string: str) -> datetime:
        lst = [int(i) if i.isdigit() else -1 for i in re.split(r"[-./ ]", string)]
        if len(lst) != 2 and len(lst) != 3:
            return None
        try:
            date = (
                datetime(lst[0], lst[1], lst[2])
                if len(lst) == 3
                else datetime(int(datetime.now().year), lst[0], lst[1])
            )
        except:
            return None
        return date

    def find_one_day(self, string: str, display: bool = True) -> list[Course]:
        date = self.str_to_date(string)
        if date is None:
            print("\033[31m输入错误!\033[0m")
            return None
        if date > SEMESTER_END or date < SEMESTER_START:
            if display:
                print("\033[93m-------------------------------------\033[0m")
                print(f"\033[93m{date.year}年{date.month}月{date.day}日的课表🚀\033[0m")
                print("\n         这一天不在这学期!\n")
                print("\033[93m-------------------------------------\033[0m")
            return None
        this_week = (date - SEMESTER_START).days // 7 + 1
        this_weekday = date.weekday()
        course_list = self.course_in_day(this_week, this_weekday)
        course_list.sort(key=lambda x: x.start)
        if display:
            view_timetable(
                date.year, date.month, date.day, this_week, this_weekday, course_list
            )
        return course_list

    def today(self) -> None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.find_one_day(date_str, display=True)

    def next_class(self, date: datetime = datetime.now()) -> None:
        current_date = datetime.now()
        delta = current_date - SEMESTER_START
        current_week = delta.days // 7 + 1
        current_weekday = current_date.weekday()
        today_class = self.course_in_day(current_week, current_weekday)
        today_class.sort(key=lambda x: x.start)
        is_today = False
        class_day = datetime.now()
        next_class = None
        for i in range(len(today_class)):
            tmp = today_class[i].start.replace(
                year=date.year, month=date.month, day=date.day
            )
            if tmp > date:
                next_class = today_class[i]
                is_today = True
                break
        if not is_today:

            def date_range(start_date, end_date):
                urrent_date = start_date
                while current_date <= end_date:
                    yield current_date
                    current_date += timedelta(days=1)

            for date in date_range(date + timedelta(days=1), SEMESTER_END):
                course_list = self.find_one_day(
                    date.strftime("%Y-%m-%d"), display=False
                )
                class_day = date
                if course_list is not None:
                    break
            next_class = course_list[0]
        if next_class:
            view_next_class(next_class, class_day)
        else:
            print("\033[93m最近没有课, 好好休息!\033[0m")

    def export_ics(self):
        with open("CQUTimetable.ics", "wb") as f:
            f.write(self.cal.to_ical())
        shutil.copy("CQUTimetable.ics", "Event.txt")
        with open("Event.txt", "r", encoding="utf-8") as f:
            content = f.read()
        encoded_content = quote(content)
        with open("url.txt", "w", encoding="utf-8") as f:
            f.write("data:text/calendar," + encoded_content)
        try:
            os.remove("Event.txt")
        except OSError as e:
            print(f"删除文件时出错: {e}")


def get_semester_start() -> bool:
    print("请输入学期第一周的周一日期（格式：2024-02-26）：")
    date_str = input()
    try:
        new_day = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print("日期格式错误！")
        get_semester_start()
    if new_day.weekday() != 0:
        print("输入的日期不是周一！")
        get_semester_start()
    config.set("database", "weekone", date_str)
    with open("config.ini", "w") as configfile:
        config.write(configfile)


def detect_end(now):
    if now > SEMESTER_END or SEMESTER_START.weekday() != 0:
        print("检测到学期开始时间异常，是否更新学期开始时间？[Y/n]")
        choice = input()
        if choice == "Y" or choice == "y":
            print("请输入学期第一周的周一日期（格式：2024-02-26）：")
            date_str = input()
            try:
                new_day = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                print("日期格式错误！")
                get_semester_start()
            if new_day.weekday() != 0:
                print("输入的日期不是周一！")
                get_semester_start()
            config.set("database", "weekone", date_str)
            with open("config.ini", "w") as configfile:
                config.write(configfile)
            return True
        elif choice == "N" or choice == "n":
            return False
        else:
            get_semester_start()
    return False


config = configparser.ConfigParser()
config.read("config.ini")
try:
    SEMESTER_START = datetime.strptime(config["database"]["weekone"], "%Y-%m-%d")
    SEMESTER_END = SEMESTER_START + timedelta(weeks=20, days=-1)
except ValueError:
    print("学期开始时间格式错误！")
    get_semester_start()
    os.system("cls" if os.name == "nt" else "clear")
    os.system("python main.py")
    sys.exit()
