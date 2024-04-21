import configparser

from datetime import datetime, timedelta
from icalendar import Calendar, Event


config = configparser.ConfigParser()
config.read("config.ini")


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
        zhou_index = string.find("周")
        qi_index = string.find("期")
        if zhou_index == -1:
            return
        week_range_str = string[:zhou_index]
        self.week_range = self.parse_range_string(week_range_str)
        if qi_index == -1:
            self.is_all_week = True
        else:
            self.weekday = {
                "一": 0,
                "二": 1,
                "三": 2,
                "四": 3,
                "五": 4,
                "六": 5,
                "日": 6,
            }.get(string[qi_index + 1], None)
            class_range_str = string[qi_index + 2 : -1]
            self.class_range = self.parse_range_string(class_range_str)
        if not self.is_all_week:
            start_class = self.class_range[0]
            end_class = self.class_range[-1]
            self.start = datetime.strptime(
                config["database"][str(start_class)], "%H:%M"
            )
            self.end = datetime.strptime(
                config["database"][str(end_class)], "%H:%M"
            ) + timedelta(minutes=int(config["database"]["duration"]))

    def parse_range_string(self, s: str) -> list[int]:
        """
        获取一个字符串中的数字，使之成为一个列表，同时解析“-”两边范围。

        例如：
        >>> self.append_start_end(stirng='1,2-4,5')
        [1, 2, 3, 4, 5]
        """
        result = []
        for part in s.split(","):
            if "-" in part:
                start, end = map(int, part.split("-"))
                result.extend(range(start, end + 1))
            else:
                result.append(int(part))
        return result

    def create_event_in_ical(self, ical: Calendar, semester_start: datetime):
        if not self.is_all_week:
            for week_num in self.week_range:
                event = Event()
                start_time = (
                    semester_start
                    + timedelta(weeks=week_num - 1, days=self.weekday)
                    + timedelta(hours=self.start.hour, minutes=self.start.minute)
                )
                end_time = (
                    semester_start
                    + timedelta(weeks=week_num - 1, days=self.weekday)
                    + timedelta(hours=self.end.hour, minutes=self.end.minute)
                )
                event.add("summary", self.name)
                event.add("dtstart", start_time)
                event.add("dtend", end_time)
                event.add("location", self.place)
                ical.add_component(event)
