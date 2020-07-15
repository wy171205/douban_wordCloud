# douban_wordCloud

爬取豆瓣影评、清洗、jieba分词、做词云图

本程序主要分为3个过程。
1、抓取网页数据
使用Python爬虫技术获取豆瓣电影中最新上映电影的网页，其网址如下：
https://movie.douban.com/cinema/nowplaying/qingdao/

![正在上映的电影](https://imgchr.com/i/Uw0DBT)
![每个电影的ID和名称](https://imgchr.com/i/Uw0BuV)
通过其HTML解析出每部电影的ID号和电影名，获取某ID号就可以得到该部电影的影评网址，形势如下：
https://movie.douban.com/subject/26900949/comments
https://movie.douban.com/subject/26871938/comments
其中，26900949、26871938就是电影《天使陷落》、《灭绝》的ID号，这样仅仅获取了20哥影评，可以指定开始号start来获取更多影评，例如：
https://movie.douban.com/subject/26900949/comments?start=40&limit=20
这意味着获取从第40条开始得20个影评。

![](https://imgchr.com/i/Uw0wj0)
![](https://imgchr.com/i/Uw0dcq)

2、清理数据
通常将某部影评信息存入eachCommentList列表中。为便于数据清理和词频统计，把eachCommentList列表形成字符串comments，将comments字符串中的“也”“太”“ 的”等虚词（停用词）清理掉后进行词频统计。

3、用词云进行展示
最后使用词云包对影评信息进行词云展示。
