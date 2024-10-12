import re
import time
import requests
import execjs
import json
import csv

headers = {
    "authority": "edith.xiaohongshu.com",
    "accept": "application/json, text/plain, */*",
    "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "content-type": "application/json;charset=UTF-8",
    "origin": "https://www.xiaohongshu.com",
    "referer": "https://www.xiaohongshu.com/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.188"
}

cookies = {
     "sec_poison_id": "c9588d31-7535-4c63-aa42-0e3f8fbbffc9",
     "gid": "yYdWKyqyKyqfyYdWKyqyqyd7J4kF7vIYDCh4xdDlYJ6yxC28i1V2hE888qYY84j8SS08dyif",
     "a1": "18e76131324gruyn8bxv4o82m1hflj5v31hxweueb50000388049",
     "websectiga": "984412fef754c018e472127b8effd174be8a5d51061c991aadd200c69a2801d6",
     "webId": "9070c508aa6b67b80a221b0dd7cd5172",
     "web_session": "040069b1adc271d01465ee603d344b3d036599",
     "xsecappid": "xhs-pc-web",
     "webBuild": "4.8.0"
}


js = execjs.compile(open(r'info.js', 'r', encoding='utf-8').read())

note_count = 0

# 向csv文件写入表头  笔记数据csv文件
header = ["笔记标题", "笔记链接", "用户ID", "用户名", "头像链接", "IP属地", "笔记发布时间",
          "笔记收藏数量", "笔记评论数量", "笔记点赞数量", "笔记转发数量", "笔记内容"]
f = open(f"话题笔记数据.csv", "w", encoding="utf-8-sig", newline="")
writer = csv.DictWriter(f, header)
writer.writeheader()


# 时间戳转换成日期
def get_time(ctime):
    timeArray = time.localtime(int(ctime / 1000))
    otherStyleTime = time.strftime("%Y.%m.%d", timeArray)
    return str(otherStyleTime)


# 保存笔记数据
def sava_data(note_data, note_id):
    try:
        ip_location = note_data['note_card']['ip_location']
    except:
        ip_location = '未知'

    data_dict = {
        "笔记标题": note_data['note_card']['title'].strip(),
        "笔记链接": "https://www.xiaohongshu.com/explore/" + note_id,
        "用户ID": note_data['note_card']['user']['user_id'].strip(),
        "用户名": note_data['note_card']['user']['nickname'].strip(),
        "头像链接": note_data['note_card']['user']['avatar'].strip(),
        "IP属地": ip_location,
        "笔记发布时间": get_time(note_data['note_card']['time']),
        "笔记收藏数量": note_data['note_card']['interact_info']['collected_count'],
        "笔记评论数量": note_data['note_card']['interact_info']['comment_count'],
        "笔记点赞数量": note_data['note_card']['interact_info']['liked_count'],
        "笔记转发数量": note_data['note_card']['interact_info']['share_count'],
        "笔记内容": note_data['note_card']['desc'].strip().replace('\n', '')
    }

    # 笔记数量+1
    global note_count
    note_count += 1

    print(f"当前笔记数量: {note_count}\n",
          f"笔记标题：{data_dict['笔记标题']}\n",
          f"笔记链接：{data_dict['笔记链接']}\n",
          f"用户ID：{data_dict['用户ID']}\n",
          f"用户名：{data_dict['用户名']}\n",
          f"头像链接：{data_dict['头像链接']}\n",
          f"IP属地：{data_dict['IP属地']}\n",
          f"笔记发布时间：{data_dict['笔记发布时间']}\n",
          f"笔记收藏数量：{data_dict['笔记收藏数量']}\n",
          f"笔记评论数量：{data_dict['笔记评论数量']}\n",
          f"笔记点赞数量：{data_dict['笔记点赞数量']}\n",
          f"笔记转发数量：{data_dict['笔记转发数量']}\n",
          f"笔记内容：{data_dict['笔记内容']}\n"
          )
    writer.writerow(data_dict)


def get_note_info(note_id):
    note_url = 'https://edith.xiaohongshu.com/api/sns/web/v1/feed'

    data = {
        "source_note_id": note_id,
        "image_scenes": [
            "CRD_PRV_WEBP",
            "CRD_WM_WEBP"
        ]
    }

    data = json.dumps(data, separators=(',', ':'))
    ret = js.call('get_xs', '/api/sns/web/v1/feed', data, cookies['a1'])
    headers['x-s'], headers['x-t'] = ret['X-s'], str(ret['X-t'])
    response = requests.post(note_url, headers=headers, cookies=cookies, data=data)
    json_data = response.json()

    try:
        note_data = json_data['data']['items'][0]
    except:
        print(f'笔记 {note_id} 不允许查看')
        return
    sava_data(note_data, note_id)


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

            get_note_info(note_id)


def main():
    keyword = '新繁'  # 搜索的关键词

    keyword_search(keyword)


if __name__ == "__main__":
    main()





