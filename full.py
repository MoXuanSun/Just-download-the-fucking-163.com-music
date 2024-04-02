#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: omi
# @Date:   2014-08-24 21:51:57
"""
网易云音乐 Api
"""
from Cryptodome.Cipher import AES
import os
import binascii
import base64
import json
import platform
from collections import OrderedDict
from http.cookiejar import Cookie
from http.cookiejar import MozillaCookieJar
import requests


MODULUS = (
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7"
    "b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280"
    "104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932"
    "575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b"
    "3ece0462db0a22b8e7"
)
PUBKEY = "010001"
NONCE = b"0CoJUm6Qyw8W8jud"


# 登录加密算法, 基于https://github.com/stkevintan/nw_musicbox
def encrypted_request(text):
    # type: (str) -> dict
    data = json.dumps(text).encode("utf-8")
    secret = create_key(16)
    params = aes(aes(data, NONCE), secret)
    encseckey = rsa(secret, PUBKEY, MODULUS)
    return {"params": params, "encSecKey": encseckey}


def aes(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, 2, b"0102030405060708")
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16),
             int(pubkey, 16), int(modulus, 16))
    return format(rs, "x").zfill(256)


def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]


# 歌曲榜单地址
TOP_LIST_ALL = {
    0: ["云音乐新歌榜", "3779629"],
    1: ["云音乐热歌榜", "3778678"],
    2: ["网易原创歌曲榜", "2884035"],
    3: ["云音乐飙升榜", "19723756"],
    4: ["云音乐电音榜", "10520166"],
    5: ["UK排行榜周榜", "180106"],
    6: ["美国Billboard周榜", "60198"],
    7: ["KTV嗨榜", "21845217"],
    8: ["iTunes榜", "11641012"],
    9: ["Hit FM Top榜", "120001"],
    10: ["日本Oricon周榜", "60131"],
    11: ["韩国Melon排行榜周榜", "3733003"],
    12: ["韩国Mnet排行榜周榜", "60255"],
    13: ["韩国Melon原声周榜", "46772709"],
    14: ["中国TOP排行榜(港台榜)", "112504"],
    15: ["中国TOP排行榜(内地榜)", "64016"],
    16: ["香港电台中文歌曲龙虎榜", "10169002"],
    17: ["华语金曲榜", "4395559"],
    18: ["中国嘻哈榜", "1899724"],
    19: ["法国 NRJ EuroHot 30周榜", "27135204"],
    20: ["台湾Hito排行榜", "112463"],
    21: ["Beatport全球电子舞曲榜", "3812895"],
    22: ["云音乐ACG音乐榜", "71385702"],
    23: ["云音乐嘻哈榜", "991319590"],
}

DEFAULT_TIMEOUT = 20

BASE_URL = "http://music.163.com"


class NetEase(object):
    def __init__(self):
        self.header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip,deflate,sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'music.163.com',
            'Origin': 'http://music.163.com',
            'Referer': 'http://music.163.com/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            # 'Cookie': document.cookie + ';os=osx'
            # 'Cookie': 'os=osx'
        }

        # self.storage = Storage()
        cookie_jar = MozillaCookieJar("cookie.txt")
        # 新加入cookie时 手动取消注释 和下面的循环 将过期时间延长
        # cookie_jar.load(ignore_expires=True)
        cookie_jar.load()
        # for v in iter(cookie_jar):
        # v.expires += 180 * 24 * 60 * 60 * 1000
        # cookie_jar.save("cookie2.txt")
        self.session = requests.Session()
        self.session.cookies = cookie_jar
        # for cookie in cookie_jar:
        #     if cookie.is_expired():
        #         cookie_jar.clear()
        #         self.storage.database["user"] = {
        #             "username": "",
        #             "password": "",
        #             "user_id": "",
        #             "nickname": "",
        #         }
        #         self.storage.save()
        #         break

    @property
    def toplists(self):
        return [item[0] for item in TOP_LIST_ALL.values()]

    # def logout(self):
    #     self.session.cookies.clear()
    #     self.storage.database["user"] = {
    #         "username": "",
    #         "password": "",
    #         "user_id": "",
    #         "nickname": "",
    #     }
    #     self.session.cookies.save()
    #     self.storage.save()

    def _raw_request(self, method, endpoint, data=None):
        resp = None
        if method == "GET":
            resp = self.session.get(
                endpoint, params=data, headers=self.header, timeout=DEFAULT_TIMEOUT
            )
        elif method == "POST":
            resp = self.session.post(
                endpoint, data=data, headers=self.header, timeout=DEFAULT_TIMEOUT
            )
        return resp

    # 生成Cookie对象
    def make_cookie(self, name, value):
        return Cookie(
            version=0,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain="music.163.com",
            domain_specified=True,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest={},
        )

    def request(self, method, path, params={}, default={"code": -1}, custom_cookies={}):
        endpoint = "{}{}".format(BASE_URL, path)
        csrf_token = ""
        for cookie in self.session.cookies:
            if cookie.name == "__csrf":
                csrf_token = cookie.value
                break
        params.update({"csrf_token": csrf_token})
        data = default
        # print(csrf_token)

        for key, value in custom_cookies.items():
            cookie = self.make_cookie(key, value)
            self.session.cookies.set_cookie(cookie)

        params = encrypted_request(params)
        resp = None
        try:
            resp = self._raw_request(method, endpoint, params)
            data = resp.json()
        except requests.exceptions.RequestException as e:
            print(e)
        except ValueError:
            print("Path: {}, response: {}".format(path, resp.text[:200]))
        finally:
            return data

    def login(self, username, password):
        self.session.cookies.load()
        if username.isdigit():
            path = "/weapi/login/cellphone"
            params = dict(
                phone=username,
                password=password,
                countrycode="86",
                rememberLogin="true",
            )
        else:
            path = "/weapi/login"
            params = dict(
                username=username,
                password=password,
                rememberLogin="true",
            )
        data = self.request("POST", path, params, custom_cookies={"os": "pc"})
        # data = self.request("POST", path, params)
        print(data)
        self.session.cookies.save()
        return data

    # 每日签到
    def daily_task(self, is_mobile=True):
        path = "/weapi/point/dailyTask"
        params = dict(type=0 if is_mobile else 1)
        return self.request("POST", path, params)

    # 用户歌单
    def user_playlist(self, uid, offset=0, limit=50):
        path = "/weapi/user/playlist"
        params = dict(uid=uid, offset=offset, limit=limit)
        return self.request("POST", path, params).get("playlist", [])

    # 每日推荐歌单
    def recommend_resource(self):
        path = "/weapi/v1/discovery/recommend/resource"
        return self.request("POST", path).get("recommend", [])

    # 每日推荐歌曲
    def recommend_playlist(self, total=True, offset=0, limit=20):
        path = "/weapi/v1/discovery/recommend/songs"
        params = dict(total=total, offset=offset, limit=limit)
        return self.request("POST", path, params).get("recommend", [])

    # 私人FM
    def personal_fm(self):
        path = "/weapi/v1/radio/get"
        return self.request("POST", path).get("data", [])

    # like
    def fm_like(self, songid, like=True, time=25, alg="itembased"):
        path = "/weapi/radio/like"
        params = dict(
            alg=alg, trackId=songid, like="true" if like else "false", time=time
        )
        return self.request("POST", path, params)["code"] == 200

    # FM trash
    def fm_trash(self, songid, time=25, alg="RT"):
        path = "/weapi/radio/trash/add"
        params = dict(songId=songid, alg=alg, time=time)
        return self.request("POST", path, params)["code"] == 200

    # 搜索单曲(1)，歌手(100)，专辑(10)，歌单(1000)，用户(1002) *(type)*
    def search(self, keywords, stype=1, offset=0, total="true", limit=50):
        path = "/weapi/search/get"
        params = dict(s=keywords, type=stype, offset=offset,
                      total=total, limit=limit)
        return self.request("POST", path, params).get("result", {})

    # 新碟上架
    def new_albums(self, offset=0, limit=50):
        path = "/weapi/album/new"
        params = dict(area="ALL", offset=offset, total=True, limit=limit)
        return self.request("POST", path, params).get("albums", [])

    # 歌单（网友精选碟） hot||new http://music.163.com/#/discover/playlist/
    def top_playlists(self, category="全部", order="hot", offset=0, limit=50):
        path = "/weapi/playlist/list"
        params = dict(
            cat=category, order=order, offset=offset, total="true", limit=limit
        )
        return self.request("POST", path, params).get("playlists", [])

    def playlist_catelogs(self):
        path = "/weapi/playlist/catalogue"
        return self.request("POST", path)

    # 歌单详情
    def playlist_songlist(self, playlist_id):
        path = "/weapi/v3/playlist/detail"
        params = dict(id=playlist_id, total="true",
                      limit=1000, n=1000, offest=0)
        # cookie添加os字段
        custom_cookies = dict(os=platform.system())
        return (
            self.request("POST", path, params, {"code": -1}, custom_cookies)
            .get("playlist", {})
            .get("trackIds", [])
        )

    # 热门歌手 http://music.163.com/#/discover/artist/
    def top_artists(self, offset=0, limit=100):
        path = "/weapi/artist/top"
        params = dict(offset=offset, total=True, limit=limit)
        return self.request("POST", path, params).get("artists", [])

    # 热门单曲 http://music.163.com/discover/toplist?id=
    def top_songlist(self, idx=0, offset=0, limit=100):
        playlist_id = TOP_LIST_ALL[idx][1]
        return self.playlist_songlist(playlist_id)

    # 歌手单曲
    def artists(self, artist_id):
        path = "/weapi/v1/artist/{}".format(artist_id)
        return self.request("POST", path).get("hotSongs", [])

    def get_artist_album(self, artist_id, offset=0, limit=50):
        path = "/weapi/artist/albums/{}".format(artist_id)
        params = dict(offset=offset, total=True, limit=limit)
        return self.request("POST", path, params).get("hotAlbums", [])

    # album id --> song id set
    def album(self, album_id):
        path = "/weapi/v1/album/{}".format(album_id)
        # return self.request("POST", path).get("songs", [])
        return self.request("POST", path)

    def song_comments(self, music_id, offset=0, total="false", limit=100):
        path = "/weapi/v1/resource/comments/R_SO_4_{}/".format(music_id)
        params = dict(rid=music_id, offset=offset, total=total, limit=limit)
        return self.request("POST", path, params)

    # song ids --> song urls ( details )
    def songs_detail(self, ids):
        path = "/weapi/v3/song/detail"
        params = dict(c=json.dumps([{"id": _id}
                      for _id in ids]), ids=json.dumps(ids))
        return self.request("POST", path, params).get("songs", [])

    def songs_url(self, ids):
        # quality = Config().get("music_quality")
        # rate_map = {0: 320000, 1: 192000, 2: 128000}

        path = "/weapi/song/enhance/player/url"
        # params = dict(ids=ids, br=rate_map[quality])
        # 请求无损格式
        params = dict(ids=ids, br=999000)
        return self.request("POST", path, params).get("data", [])

    # lyric http://music.163.com/api/song/lyric?os=osx&id= &lv=-1&kv=-1&tv=-1
    def song_lyric(self, music_id):
        path = "/weapi/song/lyric"
        params = dict(os="osx", id=music_id, lv=-1, kv=-1, tv=-1)
        lyric = self.request("POST", path, params).get(
            "lrc", {}).get("lyric", [])
        if not lyric:
            return []
        else:
            return lyric.split("\n")

    def song_tlyric(self, music_id):
        path = "/weapi/song/lyric"
        params = dict(os="osx", id=music_id, lv=-1, kv=-1, tv=-1)
        lyric = self.request("POST", path, params).get(
            "tlyric", {}).get("lyric", [])
        if not lyric:
            return []
        else:
            return lyric.split("\n")

    # 今日最热（0）, 本周最热（10），历史最热（20），最新节目（30）
    def djRadios(self, offset=0, limit=50):
        path = "/weapi/djradio/hot/v1"
        params = dict(limit=limit, offset=offset)
        return self.request("POST", path, params).get("djRadios", [])

    def djprograms(self, radio_id, asc=False, offset=0, limit=50):
        path = "/weapi/dj/program/byradio"
        params = dict(asc=asc, radioId=radio_id, offset=offset, limit=limit)
        programs = self.request("POST", path, params).get("programs", [])
        return [p["mainSong"] for p in programs]

    def alldjprograms(self, radio_id, asc=False, offset=0, limit=500):
        programs = []
        ps = self.djprograms(radio_id, asc=asc, offset=offset, limit=limit)
        while ps:
            programs.extend(ps)
            offset += limit
            ps = self.djprograms(radio_id, asc=asc, offset=offset, limit=limit)
        return programs

    # 获取版本
    def get_version(self):
        action = "https://pypi.org/pypi/NetEase-MusicBox/json"
        try:
            return requests.get(action).json()
        except requests.exceptions.RequestException as e:
            print(e)
            return {}
