from course import Course, datetime

def view(course: Course, display_time: bool = True, display_week: bool = True, display_day: bool = True) -> None:
        print("课程名：", course.name)
        print("教师：", course.teacher)
        print("教学班号：", course.number)
        print("地点：", course.place)
        if not course.is_all_week and display_time:
            print("开始时间：", course.start.strftime("%H:%M"))
            print("结束时间：", course.end.strftime("%H:%M"))
        if display_week:
            print("周数：", course.week_range)
        if not course.is_all_week and display_day:
            print("星期", course.weekday + 1)
            print("第", course.class_range, "节")

def view_timetable(year, month, day, this_week, this_weekday, course_list: list[Course]):
    print("\033[93m-------------------------------------\033[0m")
    print(
        f"\033[93m{year}年{month}月{day}日的课表🚀 - 第{this_week}周 星期{["一", "二", "三", "四", "五", "六", "日"][this_weekday]}\033[0m"
    )
    if not course_list:
        print("\033[33m\n            这一天没课🎉\n\033[0m")
    else:
        for c in course_list:
            print()
            start = c.start.strftime("%H:%M")
            end = c.end.strftime("%H:%M")
            print(f"\033[93m{start}~{end}\033[0m")
            view(c, display_time=False, display_week=False, display_day=False)
    print("\033[93m-------------------------------------\033[0m")
            
def view_next_class(course: Course, date: datetime):
    print("\033[93m-------------------------------------\033[0m")
    print("\033[93m下一节课🚀\033[0m")
    view(course, display_time=False, display_week=False, display_day=False)
    print("开始时间：", date.strftime("%Y-%m-%d"), course.start.strftime("%H:%M"))
    print("\033[93m-------------------------------------\033[0m")