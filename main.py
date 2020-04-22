import api
import datetime
import pickle
from collections import Counter

test_song_id = 1420022624


def hotComments(song_id, isPrint=False):
    if isPrint:
        print("Song Id=%d" % song_id)

    hot = api.getHotComment(song_id)
    if isPrint:
        for comment in hot:
            print("===Comment Start===\n%s %s: \n    %s \n===Comment End===\n" % (
                comment["time"], comment["name"], comment["content"]))
    return hot


def localBirthday(timestamp):
    birthday = datetime.date.fromtimestamp(timestamp).strftime("%Y")
    if birthday == "1899":
        return None
    else:
        if int(birthday[-1]) >= 5:
            return birthday[2] + "5"
        else:
            return birthday[2] + "0"


def usersPaint(song_id, num):
    songinfo = api.getSongInfo(song_id)
    print("歌曲：" + songinfo[0]["name"] + " 开始抓取")

    comments = api.getComment(song_id, num=num)
    users = [comment["uid"] for comment in comments]
    users = list(set(users))

    print("评论抓取成功， 数量:", len(users))

    users_info = []

    for uid in users:
        info = api.getUserInfo(uid)
        users_info.append(info)
        print("用户数据抓取进度: ", round(len(users_info) /
                                  len(users) * 1000) / 10, "％", end="\r")

    print("用户数据抓取成功\n\n")

    length = len(users_info)

    genders = Counter([user["gender"] for user in users_info])
    birthdays = Counter([localBirthday(user["birthday"])
                         for user in users_info if user["birthday"] > 0])
    provinces = Counter([user["province"] for user in users_info])

    most_gender = genders.most_common(1)[0]
    most_birth = birthdays.most_common(1)[0]
    most_prov = provinces.most_common(2)
    most_prov = [prov for prov in most_prov if prov[0] != "其他"][0]

    ret = """%s - %s 听众数据:

性别: %s性偏多，占 %d ％
年龄: %s后偏多，占 %d ％
地区: %s省偏多，占 %d ％

样本数量: %d""" % (songinfo[0]["name"],
               songinfo[0]["artists"][0],
               "男" if most_gender[0] == 1 else "女",
               most_gender[1] / length * 100,
               most_birth[0],
               most_birth[1] / length * 100,
               most_prov[0],
               most_prov[1] / length * 100,
               length
               )

    return {"ret": ret, "genders": genders, "births": birthdays, "prov": provinces}


if __name__ == '__main__':
    id = 0

    # 用 pickle 保存用户画像到 {id}.pkl
    # paint = usersPaint(id, 20)
    # print(paint["ret"])
    # pickle.dump(paint, open(str(id) + ".pkl", "wb"))
