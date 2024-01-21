from datetime import datetime, timedelta
from icalendar import Calendar, Event

import configparser

config = configparser.ConfigParser()
config.read("config.ini")
date_str = config["database"]["weekone"]
semester_start = datetime.strptime(date_str, "%Y-%m-%d")

class Course:
    def __init__(
        self, _name: str, _number: str, _time: str, _place: str = "", _teacher: str = ""
    ) -> None:
        self.name = _name
        self.number = _number
        self.place = _place
        self.teacher = _teacher
        self.week_range: list[int] = []
        self.weekday: int = -1
        self.class_range: list[int] = []
        self.is_all_week = False
        self.build_time(_time)

    def build_time(self, string: str) -> None:
        """
        通过课程时间的描述获取上课的周数、星期几和第几节课。
        """
        zhou = string.find("周")
        if zhou == -1:
            return
        qi = string.find("期")
        week_range_str = string[:zhou]
        if "," in week_range_str:
            week_range_list = week_range_str.split(",")
            for item in week_range_list:
                self.week_range += self.append_start_end(item)
        else:
            self.week_range = self.append_start_end(week_range_str)
        if qi == -1:
            self.is_all_week = True
        else:
            self.weekday = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6}.get(
                string[qi + 1], -1
            )
            class_range_str = string[qi + 2 : -1]
            self.class_range = self.append_start_end(class_range_str)
        if not self.is_all_week:
            start_class = self.class_range[0]
            end_class = self.class_range[-1]
            self.start = datetime.strptime(
                config["database"][str(start_class)], "%H:%M"
            )
            self.end = datetime.strptime(
                config["database"][str(end_class)], "%H:%M"
            ) + timedelta(minutes=int(config["database"]["duration"]))

    def append_start_end(self, string: str) -> list[int]:
        """
        获取一个字符串中'-'两边的数字作为遍历范围，使之成为一个列表。

        例如：
        >>> self.append_start_end(stirng='XXXXX2-4XXX')
        [2, 3, 4]
        """
        lst = []
        if "-" not in string and string.isdigit():
            lst += [int(string)]
        else:
            splited_string = string.split(",")
            for s in splited_string:
                idx = s.find("-")
                start = s[:idx]
                end = s[idx + 1 :]
                if start:
                    if end.isdigit() and start.isdigit():
                        start_i = int(start)
                        end_i = int(end)
                    else:
                        return lst
                    lst += [i for i in range(start_i, end_i + 1)]
                else:
                    lst += [int(end) if end.isdigit() else None]
        return lst

    def view(self, time: bool = True, week: bool = True, day: bool = True) -> None:
        print("课程名：", self.name)
        print("教师：", self.teacher)
        print("教学班号：", self.number)
        print("地点：", self.place)
        if not self.is_all_week and time:
            print("开始时间：", self.start.strftime("%H:%M"))
            print("结束时间：", self.end.strftime("%H:%M"))
        if week:
            print("周数：", self.week_range)
        if not self.is_all_week and day:
            print("星期", self.weekday + 1)
            print("第", self.class_range, "节")
            
    def create_event_in_ical(self, ical: Calendar):
        if not self.is_all_week:
            for week_num in self.week_range:
                event = Event()
                start_time = semester_start + timedelta(weeks=week_num-1, days=self.weekday) + timedelta(hours=self.start.hour, minutes=self.start.minute)
                end_time = semester_start + timedelta(weeks=week_num-1, days=self.weekday) + timedelta(hours=self.end.hour, minutes=self.end.minute)
                event.add('summary', self.name)
                event.add('dtstart', start_time)
                event.add('dtend', end_time)
                event.add('location', self.place)
                ical.add_component(event)
