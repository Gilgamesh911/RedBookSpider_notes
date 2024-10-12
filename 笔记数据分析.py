import re
import pandas as pd
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']

from collections import Counter

# Function to load custom dictionary and add it to Jieba
def load_custom_dictionary(custom_dict_file):
    jieba.load_userdict(custom_dict_file)

# 加载自定义词典
custom_dict_file = 'custom_dict.txt'
load_custom_dictionary(custom_dict_file)

# Function to segment text using Jieba with custom dictionary
def segment_text_with_custom_dict(texts):
    segmented_texts = []
    for text in texts:
        if len(text) == 0:
            continue
        seg_list = ' '.join(jieba.lcut(text, cut_all=True))
        segmented_texts.append(seg_list)
    return segmented_texts

# Function to clean text using stopwords
def clean_text(text):
    text = str(text)
    text = re.sub(r"(回复)?(//)?\s*@\S*?\s*(:| |$)", " ", text)
    text = re.sub(r"\[\S+\]", "", text)
    URL_REGEX = re.compile(r'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'
                           r'(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|'
                           r'(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', re.IGNORECASE)
    text = re.sub(URL_REGEX, "", text)
    for word in stopwords:
        text = text.replace(word, '')
    text = re.sub(r"\s+", " ", text)
    text = text.strip().replace(' ', '')
    return text.strip()

# 加载停用词表
stopwords_file = 'stopwords.txt'
with open(stopwords_file, "r", encoding='utf-8') as words:
    stopwords = [i.strip() for i in words]

# 绘制词云图
def generate_wordcloud(text):
    wordcloud = WordCloud(font_path="simhei.ttf",
                          background_color='white',
                          ).generate(text)
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()

# 保存词频到本地表格文件
def save_word_frequency_to_csv(word_freq):
    df = pd.DataFrame(word_freq, columns=['词语', '频次'])
    df.to_csv('word_frequency.csv', index=False)

# 绘制总的词频图
def plot_word_frequency_and_save(text):
    word_list = jieba.cut(text)
    word_list = [word for word in word_list if word.strip()]
    word_counter = Counter(word_list)
    word_freq = word_counter.most_common(20)  # 取出现频率最高的前20个词语及其频次
    words, freqs = zip(*word_freq)

    plt.figure(figsize=(10, 8))
    plt.bar(words, freqs)
    plt.xticks(rotation=45)
    plt.xlabel('词语')
    plt.ylabel('频次')
    plt.title('笔记内容词语频次图')
    plt.show()

# 保存词频到本地表格文件
    save_word_frequency_to_csv(word_freq)

data = pd.read_csv('话题笔记数据.csv')

xhs_content = data['笔记内容']

xhs_content = xhs_content.drop_duplicates()
print(xhs_content.head())

# 数据清洗
xhs_content = xhs_content.apply(clean_text)

# 对微博内容进行分词
segment_content = segment_text_with_custom_dict(xhs_content)

# 绘制词云图
content_text = ' '.join(segment_content)
generate_wordcloud(content_text)

# 绘制总的词频图
total_text = ' '.join(xhs_content)
plot_word_frequency_and_save(total_text)
