import requests
from bs4 import BeautifulSoup
import re
import os
import jieba
import jieba.analyse
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

plt.rcParams['savefig.dpi'] = 300  # 图片像素
plt.rcParams['figure.dpi'] = 300  # 分辨率

path_comment = './评论TXT文件保存/'
stopWordsFile = './stopwords.txt'
path_wordcloud_template = './词云图模板/'
path_wordcloud = './词云图完成/'


# 获取电影的id及电影名,返回字典 {ID:电影名}
def get_ID_movieName():
    # 获取当前上映电影网页的网页数据
    base_url = 'https://movie.douban.com/cinema/nowplaying/qingdao/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
    }
    html_data = requests.get(base_url, headers=headers)
    html_data.encoding = 'utf-8'
    html_content_text = html_data.text

    # beautifulsoup 解析
    bs = BeautifulSoup(html_content_text, 'html.parser')
    nowplaying_movie = bs.find_all('div', id='nowplaying')  # find_all 获取的是一个列表
    movie_list = nowplaying_movie[0].find_all('li', attrs={'class': 'list-item'})  # 获取标签为 li ，其中有class属性值为 list-item

    # 字典形式保存ID和名称
    id = []
    name = []

    for movie in movie_list:
        id.append(movie['id'])
        name.append(movie['data-title'])
    movie_dic = dict(zip(id, name))  # 字典形式为    id:name

    # print(len(movie_list))   # 5个
    print('电影ID和名称：')
    print(movie_dic)

    return movie_dic


# 获取电影的短评,传入电影id 名称字典和要爬的总页数
def get_comments(movie_dic, count):
    for id, name in movie_dic.items():  # 迭代字典，遍历每个电影
        # print(id)
        each_movie_comments = []  # 存储短评

        for page_num in range(count):  # 遍历每个电影的每个短评页面，共10页
            start = page_num * 20
            comment_url = 'https://movie.douban.com/subject/' + id + '/comments?start=' + str(start) + '&limit=20'
            # print(comment_url)

            # 获取评论页数据
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
            }
            html_data = requests.get(comment_url, headers=headers)
            html_data.encoding = 'utf-8'
            html_content_text = html_data.text

            bs = BeautifulSoup(html_content_text, 'html.parser')
            comment_div_list = bs.find_all('div', attrs={'class': 'comment'})  # 每页评论的div标签形成的列表

            # 获取评论内容
            for item in comment_div_list:
                comment = item.find('p').find('span')
                if comment:
                    each_movie_comments.append(comment.string)

        # 数据清洗
        comment_string = ''.join(each_movie_comments)  # 评论字符串

        pattern = re.compile(r'[\u4e00-\u9fa5]')  # \u4e00-\u9fa5 是unicode编码,是中文编码的开始和结束的两个值,这里用来选取所有字符
        filter_data = re.findall(pattern, comment_string)
        cleaned_comments = ''.join(filter_data)  # 过滤后

        # print(id,name)
        # print(len(each_movie_comments))
        # print(each_movie_comments)
        # print(cleaned_comments)

        # 每个电影的评论写入txt文件暂存

        if not os.path.exists(path_comment):
            os.makedirs(path_comment)

        file = path_comment + name + '.txt'
        with open(file, 'w') as f:
            f.write(cleaned_comments)
        print(name + '  写入完成')


# jieba 分词，确定出现频率高的词,生成词云图
def jieba_and_wordCloud(topK):
    # 读入停用词
    stop_words = []
    for line in open(stopWordsFile, 'r', encoding='utf-8'):
        stop_words.append(line.rstrip('\n'))

    comment_txt_list = os.listdir('./评论TXT文件保存')  # 获取评论TXT的文件名列表

    # 获取词云图模板
    template_list = os.listdir(path_wordcloud_template)

    count = 0

    for file in comment_txt_list:

        # 词云图图案
        template_file = path_wordcloud_template + template_list[count]
        pic = np.array(Image.open(template_file))

        file_path = path_comment + file
        with open(file_path, 'r') as f:
            txt = f.read()

        jieba_analyse_result = jieba.analyse.textrank(txt, topK=topK, withWeight=True)

        keywords_weight = {}  # 字典 ， 格式为  {关键词:权重}

        for i in jieba_analyse_result:
            keywords_weight[i[0]] = i[1]

        # 删除停用词
        keywords_weight_no_stopwords = {x: keywords_weight[x] for x in keywords_weight if x not in stop_words}
        wordCloud = WordCloud(font_path='./simhei.ttf',
                              background_color='white',
                              max_font_size=80,
                              stopwords=stop_words,
                              mask=pic)
        word_weight = keywords_weight_no_stopwords
        cloud = wordCloud.fit_words(word_weight)

        # 词云图文件名构成  电影名+图片模板名
        wordCloudFileName = file.replace('.txt', '') + '_使用[' + template_list[count].replace('.jpg', '') + ']模板'

        print('词云图模板', template_list[count])
        count = count + 1
		
		# 保存图片及显示
        if not os.path.exists(path_wordcloud):
            os.makedirs(path_wordcloud)

        plt.imshow(cloud)
        plt.axis('off')

        plt.savefig(path_wordcloud + wordCloudFileName)

        plt.show()


if __name__ == '__main__':
    count = 10  # 每个电影要获取多少页评论
    topK=50     # 保留权重最高的k个词
    movie_dic = get_ID_movieName()
    get_comments(movie_dic, count)
    jieba_and_wordCloud(topK)
    print('-----------END------------')
