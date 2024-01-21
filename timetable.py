import pandas as pd
import re
import warnings
import shutil
import os

from course import Course
from course import configparser
from course import datetime, timedelta
from icalendar import Calendar
from urllib.parse import quote

config = configparser.ConfigParser()
config.read("config.ini")
date_str = config["database"]["weekone"]
semester_start = datetime.strptime(date_str, "%Y-%m-%d")
semester_end = semester_start + timedelta(weeks=21)


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
            this_course.create_event_in_ical(self.cal)
            self.courses += [this_course]

    def course_in_week(self, week: int) -> list[Course]:
        return [c for c in self.courses if week in c.week_range]

    def course_in_day(self, week: int, day: int) -> list[Course]:
        return [c for c in self.course_in_week(week) if c.weekday == day]

    def find_one_day(self, string: str) -> None:
        pre_lst = re.split(r"[-./ ]", string)
        lst = [int(item) if item.isdigit() else -1 for item in pre_lst]
        year = int(datetime.now().year)
        if len(lst) == 3 or len(lst) == 2:
            year = lst[0] if len(lst) == 3 else year
            if year > 2100 or year < 1900:
                print("\033[31m格式错误!\033[0m")
                return
            month = lst[1] if len(lst) == 3 else lst[0]
            day = lst[2] if len(lst) == 3 else lst[1]
            if month < 1 or month > 12:
                print("\033[31m格式错误!\033[0m")
                return
            else:
                if (
                    (month == 2 and (day < 1 or day > 29))
                    or ((month in [4, 6, 9, 11]) and (day < 1 or day > 30))
                    or (day < 1 or day > 31)
                ):
                    print("\033[31m格式错误!\033[0m")
                    return
            date = datetime(year, month, day)
            if date > semester_end or date < semester_start:
                print(f"\033[93m{year}年{month}月{day}日的课表🚀\033[0m")
                print("这一天不在这学期!")
                return
            this_delta = date - semester_start
            this_week = this_delta.days // 7 + 1
            this_weekday = date.weekday()
            course_list = self.course_in_day(this_week, this_weekday)
            if course_list:
                weekday_lst = ["一", "二", "三", "四", "五", "六", "日"]
                course_list.sort(key=lambda x: x.start)
                print("\033[93m-------------------------------------\033[0m")
                print(
                    f"\033[93m{year}年{month}月{day}日的课表🚀 - 第{this_week}周 星期{weekday_lst[this_weekday]}\033[0m"
                )
                for c in course_list:
                    print()
                    start = c.start.strftime("%H:%M")
                    end = c.end.strftime("%H:%M")
                    print(f"\033[93m{start}~{end}\033[0m")
                    c.view(time=False, week=False, day=False)
                print("\033[93m-------------------------------------\033[0m")
            else:
                weekday_lst = ["一", "二", "三", "四", "五", "六", "日"]
                print("\033[93m-------------------------------------\033[0m")
                print(
                    f"\033[93m{year}年{month}月{day}日的课表🚀 - 第{this_week}周 星期{weekday_lst[this_weekday]}\033[0m"
                )
                print("\033[33m\n            这一天没课🎉\n\033[0m")
                print("\033[93m-------------------------------------\033[0m")
        else:
            print("\033[31m格式错误!\033[0m")

    def today(self) -> None:
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.find_one_day(date_str)

    def tomorrow(self) -> None:
        date = datetime.now() + timedelta(days=1)
        date_str = date.strftime("%Y-%m-%d")
        self.find_one_day(date_str)

    def next_class(self, date: datetime = datetime.now()) -> None:
        current_date = datetime.now()
        delta = current_date - semester_start
        current_week = delta.days // 7 + 1
        current_weekday = current_date.weekday()
        today_class = self.course_in_day(current_week, current_weekday)
        today_class.sort(key=lambda x: x.start)
        is_today = False
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
            if current_weekday == 6:
                current_week += 1
                current_weekday = 0
            else:
                current_weekday += 1
            tomorrow_class = self.course_in_day(current_week, current_weekday)
            if tomorrow_class:
                min_index = 0
                for i in range(len(tomorrow_class)):
                    min_index = (
                        i
                        if tomorrow_class[i].start < tomorrow_class[min_index].start
                        else min_index
                    )
                next_class = tomorrow_class[min_index]
        if next_class:
            print("\033[93m-------------------------------------\033[0m")
            print("\033[93m下一节课🚀\033[0m")
            next_class.view(time=False, week=False, day=False)
            print("开始时间：今天", next_class.start.strftime("%H:%M")) if is_today else print(
                "开始时间：明天", next_class.start.strftime("%H:%M")
            )
            print("结束时间：今天", next_class.end.strftime("%H:%M")) if is_today else print(
                "结束时间：明天", next_class.end.strftime("%H:%M")
            )
            print("\033[93m-------------------------------------\033[0m")
        else:
            print("\033[93m今明两天都没有课, 好好休息吧!\033[0m")

    def detect_end(self, now):
        if now > semester_end:
            print("检测到有可能是新学期，是否更新学期开始时间？[Y/n]")
            choice = input()
            if choice == "Y" or choice == "y":
                print("请输入新学期开始时间（格式：2024-02-26）：")
                date_str = input()
                config.set("database", "weekone", date_str)
                with open("config.ini", "w") as configfile:
                    config.write(configfile)
                return True

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
            print(f'删除文件时出错: {e}')