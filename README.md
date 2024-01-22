# CQU Timetable

Python实现的命令行查询CQU课表，自用小玩具。可以浏览课表和导出ics文件至日历。

## 效果

### 命令行

<img src="./assets/example.png" alt="img1" style="zoom: 67%;" />

### 导入日历（以iOS为例）

<img src="./assets/example2.jpg" alt="img2" style="zoom:50%;" />

## 使用方法

1. **选课界面**（链接：[选课管理 - 重庆大学 (cqu.edu.cn)](https://my.cqu.edu.cn/enroll/CourseStuSelectionList)）- **查看课表** - **下载Excel**

2. 将下载的Excel（文件名为：“**课表.xlsx**”）放在根目录下。

3. 安装需要的依赖

   ```
   pip install -r requirements.txt
   ```

4. 运行main.py

### 导入iOS日历

iOS日历导入ics文件比较麻烦（需要给自己发邮件），所以提供一种简单的方法来导入iOS日历：

1. 在运行后，选择“5. 导出ics文件”，此时会生成2个文件：“CQUTimetable.ics” 和 “url.txt”

2. 将url.txt这个文件传输至iPhone

3. 在iPhone上拷贝url.txt的所有内容，粘贴到Safari并打开链接。

如果你是其他平台，比如Windows的Outlook，直接双击ics文件导入就可以了。