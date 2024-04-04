// ==UserScript==
// @name        FUCK 163.com
// @namespace   JUST DONWLOAD THE FUCKING MUSIC
// @description JUST DONWLOAD THE FUCKING MUSIC WITH META DATA
// @match       *://music.163.com/*
// @grant       GM_download
// @grant       GM_xmlhttpRequest
// @version     1.0
// @author      JUST DONWLOAD THE FUCKING MUSIC TM
// @description 2024/3/26 15:39:58
// @require           https://cdn.bootcdn.net/ajax/libs/crypto-js/3.1.9/core.min.js
// @require           https://cdn.bootcdn.net/ajax/libs/crypto-js/3.1.9/crypto-js.min.js
// @require           https://cdn.bootcdn.net/ajax/libs/crypto-js/3.1.9/aes.min.js
// @require           https://cdn.bootcdn.net/ajax/libs/crypto-js/3.1.9/enc-utf8.min.js
// @require           https://cdn.bootcdn.net/ajax/libs/crypto-js/3.1.9/enc-base64.min.js
// ==/UserScript==


// 参考(copy) https://greasyfork.org/zh-CN/scripts/33046-%E7%BD%91%E6%98%93%E4%BA%91%E9%9F%B3%E4%B9%90%E7%9B%B4%E6%8E%A5%E4%B8%8B%E8%BD%BD/code
var GM__xmlHttpRequest;
if("undefined" != typeof(GM_xmlhttpRequest)){
    GM__xmlHttpRequest = GM_xmlhttpRequest;
} else {
    GM__xmlHttpRequest = GM.xmlHttpRequest;
}

let COOKIE = {
    set: function(name, value, will_expire_ms) {
        let expire = new Date();
        if (will_expire_ms) {
            expire.setTime(expire.getTime() + will_expire_ms);
        } else {
            expire.setTime(expire.getTime() + 180 * 24 * 60 * 60 * 1000);
        }
        document.cookie = name + "=" + JSON.stringify(value) + ";expires=" + expire.toGMTString() + ';path=\/';
    },
    get: function(name) {
        let arr, reg = new RegExp("(^| )" + name + "=([^;]*)(;|$)");
        if (arr = document.cookie.match(reg)) {
            return unescape(arr[2]);
        }
        return null;
    },
};

let BITRATE = {
    FLAC: 999000,
    B320: 320000,
    B192: 192000,
    B128: 128000,
};
let g_bitrate = BITRATE.FLAC;
function setBitrate(bitrate) {
    g_bitrate = bitrate;
    COOKIE.set('bitrate', g_bitrate);
}
if (COOKIE.get('bitrate')) {
    g_bitrate = parseInt(COOKIE.get('bitrate'));
    COOKIE.set('bitrate', g_bitrate);
}

function _WEAPI() {
    function _REQUEST() {
        let _base_url = 'https://music.163.com';
        let _send_request = function(url, method, headers, data) {
            return new Promise(function(resolve, reject) {
                GM__xmlHttpRequest({
                    method: method,
                    url: url,
                    headers: headers,
                    data: data,
                    onreadystatechange: function(res) {
                        if (res.readyState == 4) {
                            if (res.status == 200) {
                                resolve(res.response);
                                return;
                            }
                            reject(res.status);
                        }
                    }
                });
            });
        };
        let _headers = {
            'Accept':'*/*',
            'Accept-Encoding':'gzip,deflate,sdch',
            'Accept-Language':'zh-CN,zh;q=0.8,gl;q=0.6,zh-TW;q=0.4',
            'Connection':'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded',
            'Host':'music.163.com',
            'Origin':'http://music.163.com',
            'Referer':'http://music.163.com/',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            //'Cookie': document.cookie + ';os=osx'
            'Cookie': 'os=osx'
        };

        this.sendRequest = function(path, data) {
            return _send_request(_base_url + path, 'POST', _headers, data);
        };
        //response_process是用于处理resp的函数,这里data = response_process(data);是为了处理数据 不得不说是一个很好的办法
        this.sendRequestWrapped = function(path, data, response_process) {
            let sendRequest = this.sendRequest;
            return new Promise(function(resolve) {
                sendRequest(path, data)
                    .then(function(response) {
                    // console.log("resp:\n"+response)
                    let data = JSON.parse(response);
                    data = response_process(data);

                    resolve(data);
                })
                    .catch(function(status) {
                    console.log("sendRequestWrapped error"+status)
                    resolve([]);
                });
            });
        };
        this.sendRequestWithMethod = function(path, method, data) {
            return _send_request(_base_url + path, method, _headers, data);
        }
    }
    function _ENCRYPT() {
        let _MODULUS = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7' +
            'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280' +
            '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932' +
            '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b' +
            '3ece0462db0a22b8e7';
        let _NONCE = '0CoJUm6Qyw8W8jud';
        let _PUBKEY = '010001';
        let _create_key = function() {
            return (Math.random().toString(16).substring(2) + Math.random().toString(16).substring(2)).substring(0,16);
        };
        let _rsaEncrypt = function(text, pubKey, modulus) {
            setMaxDigits(256);
            var keys = new RSAKeyPair(pubKey, '', modulus);
            var encText = encryptedString(keys, text);
            return encText;
        }
        let _aesEncrypt = function (text, secKey){
            secKey = CryptoJS.enc.Utf8.parse(secKey);
            text = CryptoJS.enc.Utf8.parse(text);
            var encrypted = CryptoJS.AES.encrypt(text, secKey, {
                iv: CryptoJS.enc.Utf8.parse('0102030405060708'),
                mode: CryptoJS.mode.CBC
            });
            encrypted = encrypted.toString();
            return encrypted;
        }

        this.encryptedId = function(id) {
            throw('not impl!');
        };
        this.encryptedRequest = function(map) {
            let text = JSON.stringify(map);
            let secret = _create_key();
            let params = _aesEncrypt(_aesEncrypt(text, _NONCE), secret);
            let encseckey = _rsaEncrypt(secret, _PUBKEY, _MODULUS);
            return 'params=' + encodeURIComponent(params) + '&encSecKey=' + encodeURIComponent(encseckey);
        };
    };

    let REQUEST = new _REQUEST();
    let ENCREYPT = new _ENCRYPT();

    let QENC = function(map) {
        return ENCREYPT.encryptedRequest(map);
    }
    let QREQ = function(path, data, response_process) {
        return REQUEST.sendRequestWrapped(path, data, response_process);
    }

    this.songsDetail = function(ids) {
        let path = '/weapi/v3/song/detail';
        let c = [];
        for (let i = 0; i < ids.length; ++i) {
            c.push({'id': ids[i]});
        }
        let map = {
            'ids': ids,
            'c': JSON.stringify(c)
        }
        let data = QENC(map);
        return QREQ(path, data, function(data) {
            try {
                return data.songs;
            } catch (e) {
                return [];
            }
        });
    }

    //api
    this.songsUrl = function(ids) {
        let path = '/weapi/song/enhance/player/url/';
        let data = QENC({'ids': ids, 'br': g_bitrate});
        return QREQ(path, data, function(data) {
            try {
                // console.log(data)
                return data.data;
            } catch (e) {
                return [];
            }
        });
    };
    this.songLyric = function(music_id) {
        let path = '/weapi/song/lyric';
        let data = QENC({'os': 'osx', 'id': music_id, 'lv': '-1', 'kv': '-1', 'tv': '-1'});
        return QREQ(path, data);
    }

    this.playlistDetail = function(playlist_id) {
        let path = '/weapi/v3/playlist/detail';
        let data = QENC({'id': playlist_id, 'total': 'true', 'limit': 1000, 'n': 1000, 'offest': 0});
        return QREQ(path, data, function(data) {
            try {
                // console.log(data)
                return data.playlist;
            } catch (e) {
                return null;
            }
        });
    };
    this.albumDetail = function(album_id) {
        let path = '/weapi/v1/album/' + album_id;
        return QREQ(path, QENC({}), function(data) {
            try {
                return {
                    'album': data.album,
                    'songs': data.songs
                };
                // console.log(data)

            } catch (e) {
                return null;
            }
        });
    };
    this.radioDetail = function(radio_id,offset,limit) {
        let path = '/weapi/dj/program/byradio/';
        return QREQ(path, QENC({'asc':'False','radioId':radio_id,'offset':offset, 'limit':limit}), function(data) {
            try {

                // console.log(data)
                return data
            } catch (e) {
                return null;
            }
        });
    };
    //获取真实id
    this.programDetail = function(id) {
        let path = '/weapi/dj/program/detail';
        // let c = [];
        // for (let i = 0; i < ids.length; ++i) {
            // c.push({'id': ids[i]});
        // }
        let map = {
            'id': id,
            // 'c': JSON.stringify(c)
        }
        let data = QENC(map);
        return QREQ(path, data, function(data) {
            // console.log(data)
            return data
        });
    }
    this.artistDetail = function(artist_id,offset,limit) {
        let path = '/weapi/artist/albums/'+ artist_id;
        return QREQ(path, QENC({'total':'True','radioId':artist_id,'offset':offset, 'limit':limit}), function(data) {
            try {

                console.log(data)
                return data
            } catch (e) {
                return null;
            }
        });
    };
    // this.artistAlbums = function(artist_id) {
    //     let path = '/artist/album?id=' + artist_id;
    //     console.log(11)
    //     REQUEST.sendRequestWrapped(path,'GET',function(res){
    //         console.log(res)
    //     })
    // };
    // this.test = function() {
    //     function funcLog(data) {
    //         console.log(data);
    //     }
    //     this.songsUrl([1333340512, 1308363066]).then(funcLog);
    //     this.playlistDetail(4945521505).then(funcLog);
    //     this.playlistDetail(2659719519).then(funcLog);
    //     this.songLyric(1333340512).then(funcLog);
    //     this.songsDetail([1341532699]).then(funcLog);
    //     this.mvUrl(10847631).then(funcLog);
    //     this.album(75292754).then(funcLog);
    // }
}

let WEAPI = new _WEAPI();
// WEAPI.test();

fuckingfuncs = {};

async function download0(ids){
    let res = await WEAPI.songsUrl(ids)
    return new Promise(function(resolve){
          let index = 0;
          console.log(ids)

          GM_download({'url':res[index].url,'name':res[index].id+"."+res[index].type,
              'onerror':function onerror(result){
                  console.error("下载错误");
                  resolve('error')
                  return 'error';
              },
              'onload':function onsuccess(result){
              console.log("正在下载 "+ (index + 1) + "/" + res.length);
              if (index == res.length -1){
                  console.log("全部下载完成");
                  resolve('success')
                  return;
              }
              index++;
              GM_download({'url':res[index].url,'name':res[index].id+"."+res[index].type,'onload':onsuccess,'onerror':onerror})
          }})
    })
}

fuckingfuncs.downloadSingleMusic = async function test(id){
    console.log(await download0([id]))

}


//传入[id1,id2....]
fuckingfuncs.downloadPlayLists = async function downloadPlayLists(ids) {
    for (let id of ids){
        let res = await WEAPI.playlistDetail(id)
        console.log("准备开始下载")
        console.log("歌单信息\n==================\n歌单id：" + res.id + "\n歌单名：" + res.name + "\n歌单介绍：" + res.description)
        let songids = [];
        for (let t of res.trackIds){
            songids.push(t.id);
        }
        await download0(songids);
        // addToQueue(songids)
        // notify()
    }
}



fuckingfuncs.downloadPlayListWithOffSet = async function downloadPlayLists(id,start,end) {
    let res = await WEAPI.playlistDetail(id)
    console.log("准备开始下载")
    console.log("歌单信息\n==================\n歌单id：" + res.id + "\n歌单名：" + res.name + "\n歌单介绍：" + res.description)
    let songids = [];
    for (let t of res.trackIds.slice(start,end)){
        songids.push(t.id);
    }
    await download0(songids);
    // addToQueue(songids)
    // notify()
}


//传入[id1,id2....]
fuckingfuncs.downloadAlbums  = async function downloadAlbums(ids){
  for (let id of ids){
        let res = await WEAPI.albumDetail(id)
        console.log("准备开始下载")
        console.log(res)
        console.log("专辑信息\n==================\n专辑id：" + res.album.id + "\n专辑名：" + res.album.name + "\n专辑介绍：" + res.album.description)
        let songids = [];
        for (let t of res.songs){
            if (t.id == undefined || t.id == null){
                // fuck 163
                songids.push(t.privilege.id);
            }else{
                songids.push(t.id);
            }
        }
        await download0(songids);
        // notify()
    }
}


fuckingfuncs.downloadArtists = async function downloadArtists(ids,alstart,alend){

    for (let id of ids){
        let Albumid = []
        let res = await WEAPI.artistDetail(id,alstart,alend)
        console.log("准备开始下载")
        console.log(res)
        console.log("艺术家信息\n==================\n"+ "艺术家id：" + res.artist.id + "\n艺术家名：" + res.artist.name)
        console.table(res.hotAlbums.map(v => v.id))
        await fuckingfuncs.downloadAlbums(res.hotAlbums.map(v => v.id))
    }

}

fuckingfuncs.downloadDJs = async function downloadDJs(ids,start,end){
    for (let id of ids){
        let res = await WEAPI.radioDetail(id,start,end)
        console.log("准备开始下载")
        console.log(res)
        console.log("电台信息\n==================\n"+ "电台id：" + res.programs[0].radio.id + "\n电台名：" + res.programs[0].radio.name + "\n电台介绍：" + res.programs[0].radio.desc)
        let songids = [];
        console.log("开始获取DJid")
        for (v of res.programs){
            let data = await WEAPI.programDetail(v.id)
            songids.push(data.program.mainSong.id)
        }
        await download0(songids);

    }
}


// function resumeDownloadProgress() 断点继续下载


window.fuckingfuncs = fuckingfuncs
