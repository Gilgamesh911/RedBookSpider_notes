import re
import time
import requests
import execjs
import json
import csv

from bs4 import BeautifulSoup

headers = {
    "authority": "edith.xiaohongshu.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.xiaohongshu.com",
    "referer": "https://www.xiaohongshu.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

cookies = {
     "sec_poison_id": "d8193bb3-6605-47f0-980e-c7ba7b889349",
     "gid": "yYSKYWyfyW34yYSKYWySKI870KAK6uj7Y90KWKhCldW9E7286MdiWf888qW4W2j8qifSf884",
     "a1": "18c6871c6a6q6mz9u8ta6xoe7twmsef7in7ud0u6v50000374759",
     "websectiga": "3fff3a6f9f07284b62c0f2ebf91a3b10193175c06e4f71492b60e056edcdebb2",
     "webId": "a0f12a8433f12419df766d791ed3137e",
     "web_session": "0400698c10b7e956546662c3d8374b6a2065d6",
     "xsecappid": "xhs-pc-web",
     "webBuild": "4.5.1"
}


js = execjs.compile(open(r'info.js', 'r', encoding='utf-8').read())

note_count = 0

# 向csv文件写入表头  笔记数据csv文件
header = ["笔记标题", "笔记链接", "用户ID", "用户头像", "用户名", "IP属地", "笔记发布时间",
          "笔记收藏数量", "笔记评论数量", "笔记点赞数量", "笔记内容"]
f = open(f"话题笔记数据.csv", "w", encoding="utf-8-sig", newline="")
writer = csv.DictWriter(f, header)
writer.writeheader()


# 时间戳转换成日期
def get_time(ctime):
    timeArray = time.localtime(int(ctime / 1000))
    otherStyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherStyleTime)


# 保存笔记数据
def get_note_info(note_id, title, user_avatar, user_name, user_id):
    note_url = f'https://www.xiaohongshu.com/explore/{note_id}'

    res = requests.get(note_url, headers=headers, cookies=cookies)
    bs = BeautifulSoup(res.text, "html.parser")  # 创建BeautifulSoup对象

    data_dict = {
        "笔记标题": title.strip(),
        "笔记链接": "https://www.xiaohongshu.com/explore/" + note_id,
        "用户ID": user_id.strip(),
        "用户头像": user_avatar.strip(),
        "用户名": user_name.strip(),
        "IP属地": bs.find('div', {'class': 'bottom-container'}).get_text().split(' ')[1],
        "笔记发布时间": bs.find('div', {'class': 'bottom-container'}).get_text().split(' ')[0],
        "笔记收藏数量": bs.find('meta', {'name': 'og:xhs:note_collect'})['content'],
        "笔记评论数量": bs.find('meta', {'name': 'og:xhs:note_comment'})['content'],
        "笔记点赞数量": bs.find('meta', {'name': 'og:xhs:note_like'})['content'],
        "笔记内容": bs.find('div', {'class': 'desc'}).get_text().strip().replace('\n', '')
    }

    time.sleep(1)
    # 笔记数量+1
    global note_count
    note_count += 1

    print(f"当前笔记数量: {note_count}\n",
          f"笔记标题：{data_dict['笔记标题']}\n",
          f"笔记链接：{data_dict['笔记链接']}\n",
          f"用户ID：{data_dict['用户ID']}\n",
          f"用户头像：{data_dict['用户头像']}\n",
          f"用户名：{data_dict['用户名']}\n",
          f"IP属地：{data_dict['IP属地']}\n",
          f"笔记发布时间：{data_dict['笔记发布时间']}\n",
          f"笔记收藏数量：{data_dict['笔记收藏数量']}\n",
          f"笔记评论数量：{data_dict['笔记评论数量']}\n",
          f"笔记点赞数量：{data_dict['笔记点赞数量']}\n",
          f"笔记内容：{data_dict['笔记内容']}\n"
          )
    writer.writerow(data_dict)


def keyword_search(keyword):
    api = '/api/sns/web/v1/search/notes'

    search_url = "https://edith.xiaohongshu.com/api/sns/web/v1/search/notes"

    # 排序方式 general: 综合排序 popularity_descending: 热门排序 time_descending: 最新排序
    data = {
        "image_scenes": "FD_PRV_WEBP,FD_WM_WEBP",
        "keyword": "",
        "note_type": "0",
        "page": "",
        "page_size": "20",
        "search_id": "2c7hu5b3kzoivkh848hp0",
        "sort": "general"
    }

    data = json.dumps(data, separators=(',', ':'))
    data = re.sub(r'"keyword":".*?"', f'"keyword":"{keyword}"', data)

    page_count = 20  # 爬取的页数, 一页有 20 条笔记 最多只能爬取220条笔记
    for page in range(1, page_count):
        data = re.sub(r'"page":".*?"', f'"page":"{page}"', data)

        ret = js.call('get_xs', api, data, cookies['a1'])
        headers['x-s'], headers['x-t'] = ret['X-s'], str(ret['X-t'])

        response = requests.post(search_url, headers=headers, cookies=cookies, data=data.encode('utf-8'))
        json_data = response.json()
        try:
            notes = json_data['data']['items']
        except:
            print('================爬取完毕================'.format(page))
            break

        for note in notes:
            note_id = note['id']
            if len(note_id) != 24:
                continue
            try:
                title = note['note_card']['display_title']
            except:
                title = ''

            user_avatar = note['note_card']['user']['avatar']
            user_name = note['note_card']['user']['nick_name']
            user_id = note['note_card']['user']['user_id']

            get_note_info(note_id, title, user_avatar, user_name, user_id)


def main():
    keyword = '公园 香气'  # 搜索的关键词

    keyword_search(keyword)


if __name__ == "__main__":
    main()





