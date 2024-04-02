from full import NetEase
import json
import os
import music_tag

# 用法示例：
# 1.使用脚本下载音乐，然后放入songs文件夹
# 2.修改脚本最后面的调用函数 按照需求调用（懒得做命令行了) 运行脚本识别并更新元数据
# 3.将songs文件夹复制到歌曲软件文件夹 比如D:/Syncthing/music/
# 4.[可选 添加播放列表] 打开上级文件夹，将playlist.playlist 拖入musicplayer2 然后可以改名

# 一次性不要处理太多 懒得做分批处理了

NetEaseinstance = NetEase()
ids = []

root_perfix = "D:/Syncthing/music/"

# 获取正常歌曲信息时调用


def fetchNormalMusicList():
    for v in os.listdir("songs"):
        ids.append(int(v.split(".")[0]))
    print("id数量：{}".format(len(ids)))

    albumbuffer = {}
    infos = NetEaseinstance.songs_detail(ids)
    print("获取到歌曲信息数量：{}".format(len(infos)))
    with open("json2.json", "w", encoding="utf-8") as f:
        json.dump(infos, f, indent=2, ensure_ascii=False)
    infos_cleared = {}

    for v in infos:

        # 名字为空时 说明是云盘的曲子  if k['name'] is not None
        print(v)
        if v['name'] is None:
            continue

        artist_list = [k['name'] for k in v['ar']]

        artist = "/".join(artist_list)
        for k in artist_list:
            if 'tns' in k and len(k['tns']) > 0:
                artist += " ({})".format("/".join(k['tns']))

        name = v['name']
        if 'tns' in v and len(v['tns']) > 0:
            name += " ({})".format("/".join(v['tns']))

        album = v['al']['name']

        if 'tns' in v['al'] and len(v['al']['tns']) > 0:
            album += " ({})".format("/".join(v['al']['tns']))

        if v['al']['id'] not in albumbuffer:
            albumbuffer[v['al']['id']] = NetEaseinstance.album(v['al']['id'])

        artist_list = []
        if 'album' in albumbuffer[v['al']['id']]:
            artist_list = [k['name']
                           for k in albumbuffer[v['al']['id']]['album']['artists']]
        albumartist = '/'.join(artist_list)

        for k in artist_list:
            if 'tns' in k and len(k['tns']) > 0:
                artist += " ({})".format("/".join(k['tns']))

        infos_cleared[v['id']] = {
            'name': name,
            'artist': artist,
            'album': album,
            'albumartist': albumartist,
        }
    return infos_cleared

# 获取电台歌曲信息时调用 需要输入电台ids


def fetchDJmusicList(djIds):

    infos = []
    for id in djIds:
        infos.append(NetEaseinstance.alldjprograms(id))
    with open("json2.json", "w", encoding="utf-8") as f:
        json.dump(infos, f, indent=2, ensure_ascii=False)
    infos_cleared = {}
    for i in infos:
        for v in i:
            artist_list = [k['name'] for k in v['artists']]

            artist = "/".join(artist_list)

            infos_cleared[v['id']] = {
                'name': v['name'],
                'album': v['album']['name'],
                'artist': artist,
                'albumartist': v['album']['artist']['name']
            }
    print(len(infos_cleared))
    return infos_cleared


def apllyMetadata(infos_cleared):
    # 修改音频元数据
    with open("json.json", "w", encoding="utf-8") as f:
        json.dump(infos_cleared, f, indent=2, ensure_ascii=False)
    for v in os.listdir("songs/"):
        print("songs/"+v)
        audio_tag = music_tag.load_file("songs/"+v)
        id = int(v.split(".")[0])
        audio_tag.remove_tag('title')
        audio_tag.remove_tag('album')
        audio_tag.remove_tag('artist')
        audio_tag.remove_tag('comment')
        audio_tag.remove_tag('albumartist')
        audio_tag.append_tag('title', infos_cleared[id]['name'])
        audio_tag.append_tag('album', infos_cleared[id]['album'])
        audio_tag.append_tag('artist', infos_cleared[id]['artist'])
        audio_tag.append_tag('comment', "id=" + str(id))
        audio_tag.append_tag(
            'albumartist', infos_cleared[id]['albumartist'])
        print(audio_tag)
        audio_tag.save()


# 分批 第二批开始获取时暂时修改为a 记得改回来
with open("playlist.playlist", "w", encoding="utf-8") as f:
    for v in os.listdir("songs/"):
        f.write(root_perfix+v+"\n")


# apllyMetadata(fetchDJmusicList([985693328]))


apllyMetadata(fetchNormalMusicList())
