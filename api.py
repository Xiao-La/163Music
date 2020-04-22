import requests
import time
import pickle

test_song_id = 411315260
test_user_id = 1715781671

api_list = {
    "comment": "http://music.163.com/api/v1/resource/comments/R_SO_4_|song_id|",
    "song_info": "http://music.163.com/api/song/detail/?id=|song_id|&ids=%5B|song_id|%5D",
    "download-song": "http://music.163.com/song/media/outer/url?id=|song_id|.mp3",
    "download-lyric": "http://music.163.com/api/song/lyric?os=pc&id=|song_id|&lv=-1&kv=-1&tv=-1",
    "user_info": "https://music.163.com/api/v1/user/detail/|user_id|"}

header = {
    'user-agent': 'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/80.0.3987.163Safari/537.36'}

city_map = {
    '11': '北京',
    '12': '天津',
    '31': '上海',
    '50': '重庆',
    '5e': '重庆',
    '81': '香港',
    '82': '澳门',
    '13': '河北',
    '14': '山西',
    '15': '内蒙古',
    '21': '辽宁',
    '22': '吉林',
    '23': '黑龙江',
    '32': '江苏',
    '33': '浙江',
    '34': '安徽',
    '35': '福建',
    '36': '江西',
    '37': '山东',
    '41': '河南',
    '42': '湖北',
    '43': '湖南',
    '44': '广东',
    '45': '广西',
    '46': '海南',
    '51': '四川',
    '52': '贵州',
    '53': '云南',
    '54': '西藏',
    '61': '陕西',
    '62': '甘肃',
    '63': '青海',
    '64': '宁夏',
    '65': '新疆',
    '71': '台湾',
    '10': '其他',
}


def replaceAPI(url, param):
    if "|song_id|" in url:
        apiurl = url.replace("|song_id|", str(param["song_id"]))
    if "|user_id|" in url:
        apiurl = url.replace("|user_id|", str(param["user_id"]))
    return apiurl


def getComment(song_id, num=1000):
    ret = []

    api = api_list["comment"]
    url = replaceAPI(api, param={"song_id": song_id}) + "?limit=20&offset="

    for page in range(num // 20):
        nowurl = url + str(page * 20)
        req = requests.post(nowurl, headers=header)

        if req.status_code != 200:
            raise Exception("Request Error.")

        rjson = req.json()
        comments = rjson["comments"]
        for comment in comments:
            username = comment["user"]["nickname"]
            userid = comment["user"]["userId"]
            content = comment["content"]

            ret.append({"name": username, "uid": userid, "content": content})
    return ret


def getHotComment(song_id):
    ret = []

    api = api_list["comment"]
    url = replaceAPI(api, param={"song_id": song_id})

    req = requests.post(url, headers=header)

    if req.status_code != 200:
        raise Exception("Request Error.")

    rjson = req.json()
    try:
        hotcomments = rjson["hotComments"]
    except:
        raise Exception("No hotcomments.")

    for hotcomment in hotcomments:
        username = hotcomment["user"]["nickname"]
        content = hotcomment["content"]

        timestamp = int(hotcomment["time"])
        ctime = time.strftime("%Y-%m-%d %H:%M:%S",
                              time.localtime(timestamp / 1000))

        ret.append({"name": username, "content": content, "time": ctime})

    return ret


def getUserInfo(user_id):
    api = api_list["user_info"]
    url = replaceAPI(api, param={"user_id": user_id})

    req = requests.get(url, headers=header)

    if req.status_code != 200:
        raise Exception("Request Error.")

    rjson = req.json()

    name = rjson["profile"]["nickname"]
    gender = rjson["profile"]["gender"]

    birthday = rjson["profile"]["birthday"]
    timestamp = int(birthday / 1000)

    cityCode = str(rjson["profile"]["city"])
    province = city_map[cityCode[:2]]

    return {"id":user_id, "name": name, "gender":gender, "birthday": timestamp, "province":province}


def getSongInfo(song_id):
    ret = []

    api = api_list["song_info"]
    url = replaceAPI(api, param={"song_id": song_id})

    req = requests.get(url, headers=header)

    if req.status_code != 200:
        raise Exception("Request Error.")

    rjson = req.json()
    songs = rjson["songs"]

    for song in songs:
        try:
            songname = song["name"]
        except:
            raise Exception("Song Name Not Found.")

        try:
            artists = [artist["name"] for artist in song["artists"]]
        except:
            artists = None

        try:
            album = {"name": song["album"]["name"], "id": song["album"]["id"]}
        except:
            alum = None

        ret.append({"name": songname, "artists": artists, "album": album})

    return ret


def download(song_id, lyric=True, filename=None):
    if filename == None:
        songinfo = getSongInfo(song_id)[0]
        filename = ".\\downloads\\%s - %s.mp3" % (
            songinfo["name"], songinfo["artists"][0])

    song_api = api_list["download-song"]
    song_url = replaceAPI(song_api, param={"song_id": song_id})

    lyric_api = api_list["download-lyric"]
    lyric_url = replaceAPI(lyric_api, param={"song_id": song_id})
    lyric_filename = filename.replace(".mp3", ".lrc")

    song = requests.get(song_url, headers=header)
    with open(filename, "wb") as f:
        f.write(song.content)

    lyric = requests.get(lyric_url, headers=header)
    lyric = lyric.json()["lrc"]["lyric"]
    with open(lyric_filename, "w") as f:
        f.write(lyric)


if __name__ == '__main__':
    pass
