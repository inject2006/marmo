# -*- coding:UTF-8 -*-
'''
    进行旁站拓展
    主要点:token,cookie可以只留下qHistory
    http://stool.chinaz.com/AjaxTool.ashx?action=getsameip&callback=jQuery1113015467048525929417_1622424025788
    {
        project_id:项目id,
        project_name:项目名称,
        asset_id:资产id,
        asset:资产,
        task_id:任务id
    }
    module_log={
        exists_data:是否存在数据
        error:"",



    }
    update_module_params = {
                "module_name": self.module_name,
                "module_status": 2,
                "module_log": json.dumps(self.data_info),
                "asset_type": self.asset_data["asset_type"],
                "asset_id": self.asset_data["asset_id"],
                "fail_reason": "获取旁站信息异常=="+str(e.__str__()),
                "project_name": self.asset_data["project_name"]
            }
            ModuleFunctionDao().update_module_function(update_module_params)
'''
import execjs
import time
import requests
import re
import json
from base64 import b64encode
from app.dao.sidestations_dao import SideStaionsDao
from .marmo_ping import MarmoPing
from app.dao.marmo_log_dao import MarmoLogDao
from app.utils.marmo_logger import Marmo_Logger
logger =Marmo_Logger()
class SideStations():
    def __init__(self,asset_data):
        self.vb =int(time.time())*1000
        self.ajax_url ="http://stool.chinaz.com/AjaxTool.ashx?action=getsameip&callback=%s"
        self.main_url ="http://stool.chinaz.com/same"
        self.error_reson=""
        self.cookies =""
        self.asset_data= asset_data
        self.exists_data=True #执行完是否存在数据
        self.host_list =[]  #网站返回的域名列表
        self.ping_host_list =[]  #经过ping的域名列表
        self.module_name = asset_data["module_name"]
        self.headers ={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Host":"stool.chinaz.com",
            "Cookie":"qHistory=c2FtZS9f5ZCMSVDnvZHnq5nmn6Xor6I="
        }
        self.ip = asset_data["asset"]  #输入的ip数据
        self.data_info = {
            "exists_data": False,
            "status_code": 2,
            "fail_reason": "",
            "data": "",
            "module_name": self.module_name,
            "asset_type": asset_data["asset_type"],
            "asset_id": asset_data["asset_id"],
            "project_id": asset_data["project_id"],
            "project_name": asset_data["project_name"]
        }
        self.marmo_log = {
            "datas": [],
            "exceptions": []
        }



    '''
        获取回调地址
    '''

    def expando(self):
        js = '''
            function getExpando(){
                return "jQuery" + ('1.11.3' + Math.random()).replace(/\D/g, "")
            }
        '''
        expando_compile = execjs.compile(js)
        return expando_compile.call("getExpando")


    '''
        获取token
    '''
    def getToken(self,ip):
        generate_key_js ="""
var _0xodv = 'jsjiami.com.v6'
  , _0x1e35 = [_0xodv, 'ExYSWMOk', 'ccKewrdWXsO0', 'TcKVCcKBE3w=', 'OMO6w6xKflsnw7zDmMOB', 'wrjDtMOvAhY=', 'wrDDvjFcw4DDrg==', 'FsOMwqPCv8Oi', 'w5jDsCsRFMOf', 'E8OeHAVG', 'w6jCn8K9w7NlwrXDl3NCBQ==', 'MsKCZsOZIGg=', 'wrAMFRTCsw==', 'wp0QAjTCnDE=', 'w6PCgxLDln5zAMKraXk=', 'w7TCjQXDsWk=', 'w5guQ8OiZMO/', 'T8OUKx5v', 'bWfCt8Kowqo=', 'F8Ohw4leVA==', 'wogBw4AtPw==', 'wrAVHgTColo=', 'wogywrPDiXBqw5RWw5XCi3DDg8OGw4AibsOtwrDDq8Oew4/DoTEwY8KPHMOf', 'DMKxwqHDisO2', 'wq0Tw584GEk=', 'w6PCgxLDlnxo', 'OMKcw43CgcOD', 'HMOBIhVk', 'DsOPwrvCjcOCZQ==', 'PMOCw7lxSQ==', 'McOXTmPCrA==', 'wohdesK1Qg==', 'w705w5AAaQ==', 'w7toZEBbW8KWJMKqwpI=', 'w6tsbFF9', 'w5VmwqHCn3g7', 'w69CalVM', 'wpFPVzDCiA==', 'wq/DtzZYw5E=', 'V8OxHzB7', 'w5bCuClIXw==', 'Z8KIHMKlHg==', 'w63Cr8Kvw5N8', 'X8KcHsKDIw==', 'TMOUJy/Dl18=', 'ScKhwofCmcKG', 'w47CicOyw4jDrzPDizQeCQ==', 'OGZNw793', 'ScOBw5jClMKpT8K2Ujw=', 'CMOYwpHCr8OS', 'w4fDpSkfFA==', 'w78Jw7UGbg==', 'wrsZFxPCpw==', 'F1rCpH3Dnw==', 'KjUfSsO6Kg==', 'b8K6wpddZQ==', 'wpzCtHJdHcOQwocEdcOVw4xzw6bCgzXCgnpYw7nDlMOPSsOkGcKBw7gCFw==', 'aVLCvMKCwog=', 'LsOZwpHCjMOf', 'C8KowrzDj8Ob', 'w6TDmRcjacKv', 'w4jCpMKow4tx', 'AcO0VkDCjw==', 'wpwLFgTClA==', 'wr/DosO1PjY=', 'RcKIDsKyTALDi8K0dCs=', 'DsK/w7vCqMOxwr0=', 'w4HChMO9w53DmDQ=', 'AsKDCAJ7', 'FCE7QcOk', 'CQM1UHQ=', 'aRvDvcKzesKy', 'jKsXjQiami.bYWggkcomnt.vF6QK=='];
(function(_0xc1d202, _0x2ddd24, _0x5169d9) {
    var _0x311c08 = function(_0x185643, _0x333ee6, _0x3476f0, _0x189d7a, _0x13f0a6) {
        _0x333ee6 = _0x333ee6 >> 0x8,
        _0x13f0a6 = 'po';
        var _0x4180fe = 'shift'
          , _0x30102a = 'push';
        if (_0x333ee6 < _0x185643) {
            while (--_0x185643) {
                _0x189d7a = _0xc1d202[_0x4180fe]();
                if (_0x333ee6 === _0x185643) {
                    _0x333ee6 = _0x189d7a;
                    _0x3476f0 = _0xc1d202[_0x13f0a6 + 'p']();
                } else if (_0x333ee6 && _0x3476f0['replace'](/[KXQbYWggkntFQK=]/g, '') === _0x333ee6) {
                    _0xc1d202[_0x30102a](_0x189d7a);
                }
            }
            _0xc1d202[_0x30102a](_0xc1d202[_0x4180fe]());
        }
        return 0x7a3f7;
    };
    return _0x311c08(++_0x2ddd24, _0x5169d9) >> _0x2ddd24 ^ _0x5169d9;
}(_0x1e35, 0x1e1, 0x1e100));
var _0x5a05 = function(_0x416042, _0x1a0c7a) {
    _0x416042 = ~~'0x'['concat'](_0x416042);
    var _0x68c327 = _0x1e35[_0x416042];
    if (_0x5a05['lFacjS'] === undefined) {
        (function() {
            var _0x87b5fb = typeof window !== 'undefined' ? window : typeof process === 'object' && typeof require === 'function' && typeof global === 'object' ? global : this;
            var _0x262a60 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
            _0x87b5fb['atob'] || (_0x87b5fb['atob'] = function(_0x56d076) {
                var _0x210445 = String(_0x56d076)['replace'](/=+$/, '');
                for (var _0x549973 = 0x0, _0x12d79e, _0x379544, _0x534666 = 0x0, _0x272b97 = ''; _0x379544 = _0x210445['charAt'](_0x534666++); ~_0x379544 && (_0x12d79e = _0x549973 % 0x4 ? _0x12d79e * 0x40 + _0x379544 : _0x379544,
                _0x549973++ % 0x4) ? _0x272b97 += String['fromCharCode'](0xff & _0x12d79e >> (-0x2 * _0x549973 & 0x6)) : 0x0) {
                    _0x379544 = _0x262a60['indexOf'](_0x379544);
                }
                return _0x272b97;
            }
            );
        }());
        var _0x4e2873 = function(_0xe35628, _0x1a0c7a) {
            var _0x2eadc5 = [], _0x5a1996 = 0x0, _0x349934, _0x11af25 = '', _0x1564f0 = '';
            _0xe35628 = atob(_0xe35628);
            for (var _0x47ac9d = 0x0, _0x1bbc0e = _0xe35628['length']; _0x47ac9d < _0x1bbc0e; _0x47ac9d++) {
                _0x1564f0 += '%' + ('00' + _0xe35628['charCodeAt'](_0x47ac9d)['toString'](0x10))['slice'](-0x2);
            }
            _0xe35628 = decodeURIComponent(_0x1564f0);
            for (var _0x39030c = 0x0; _0x39030c < 0x100; _0x39030c++) {
                _0x2eadc5[_0x39030c] = _0x39030c;
            }
            for (_0x39030c = 0x0; _0x39030c < 0x100; _0x39030c++) {
                _0x5a1996 = (_0x5a1996 + _0x2eadc5[_0x39030c] + _0x1a0c7a['charCodeAt'](_0x39030c % _0x1a0c7a['length'])) % 0x100;
                _0x349934 = _0x2eadc5[_0x39030c];
                _0x2eadc5[_0x39030c] = _0x2eadc5[_0x5a1996];
                _0x2eadc5[_0x5a1996] = _0x349934;
            }
            _0x39030c = 0x0;
            _0x5a1996 = 0x0;
            for (var _0x589ce6 = 0x0; _0x589ce6 < _0xe35628['length']; _0x589ce6++) {
                _0x39030c = (_0x39030c + 0x1) % 0x100;
                _0x5a1996 = (_0x5a1996 + _0x2eadc5[_0x39030c]) % 0x100;
                _0x349934 = _0x2eadc5[_0x39030c];
                _0x2eadc5[_0x39030c] = _0x2eadc5[_0x5a1996];
                _0x2eadc5[_0x5a1996] = _0x349934;
                _0x11af25 += String['fromCharCode'](_0xe35628['charCodeAt'](_0x589ce6) ^ _0x2eadc5[(_0x2eadc5[_0x39030c] + _0x2eadc5[_0x5a1996]) % 0x100]);
            }
            return _0x11af25;
        };
        _0x5a05['oFzxmD'] = _0x4e2873;
        _0x5a05['etdLjT'] = {};
        _0x5a05['lFacjS'] = !![];
    }
    var _0x3c97d0 = _0x5a05['etdLjT'][_0x416042];
    if (_0x3c97d0 === undefined) {
        if (_0x5a05['ZlksSu'] === undefined) {
            _0x5a05['ZlksSu'] = !![];
        }
        _0x68c327 = _0x5a05['oFzxmD'](_0x68c327, _0x1a0c7a);
        _0x5a05['etdLjT'][_0x416042] = _0x68c327;
    } else {
        _0x68c327 = _0x3c97d0;
    }
    return _0x68c327;
};
function generateKey() {
    var _0x2322bf = {
        'LuJoq': _0x5a05('0', 'vqcZ'),
        'KBcvq': function(_0x35dbd7, _0x4efc7f) {
            return _0x35dbd7 < _0x4efc7f;
        },
        'gcduC': function(_0x101bc6, _0x164c61) {
            return _0x101bc6 == _0x164c61;
        },
        'tfvUT': function(_0x2190d1, _0x4cae1c) {
            return _0x2190d1 - _0x4cae1c;
        },
        'ZZkSa': function(_0xd012b9, _0x5a1892) {
            return _0xd012b9 + _0x5a1892;
        },
        'jFnqD': function(_0x5e1a13, _0x4ee5ee) {
            return _0x5e1a13 + _0x4ee5ee;
        },
        'XXtRF': function(_0x4b3170, _0x31cbe6) {
            return _0x4b3170 >= _0x31cbe6;
        },
        'LsDfi': function(_0x1fbb84, _0x5d2973) {
            return _0x1fbb84(_0x5d2973);
        },
        'mUysH': '#IpValue',
        'doksg': function(_0x3edba1, _0x50fccd) {
            return _0x3edba1 + _0x50fccd;
        },
        'pOfAn': function(_0x151893, _0xb80394) {
            return _0x151893 + _0xb80394;
        },
        'CStJW': function(_0x3e935f, _0x45a479) {
            return _0x3e935f + _0x45a479;
        },
        'bsuBI': function(_0x443863, _0x56b5ff) {
            return _0x443863 + _0x56b5ff;
        },
        'HBCoM': function(_0x38ea3e, _0x1df81d) {
            return _0x38ea3e !== _0x1df81d;
        },
        'Mrvck': _0x5a05('1', ')s)6'),
        'vFxVM': function(_0x55387b, _0x428d5a) {
            return _0x55387b + _0x428d5a;
        },
        'SLBKV': function(_0x217ed4, _0x2fde1f) {
            return _0x217ed4 + _0x2fde1f;
        },
        'IwqrS': function(_0x3ca281, _0x370bd9) {
            return _0x3ca281 + _0x370bd9;
        }
    };
    var _0x217bb6 = '$_0x217bb6';
    if (!_0x217bb6)
        return '';
    var _0x3440e2 = _0x217bb6['split']('.');
    if (_0x3440e2[_0x5a05('4', 'R)GX')] != 0x4)
        return '';
    var _0x2a9264 = _0x2322bf['doksg'](_0x2322bf['pOfAn'](_0x2322bf[_0x5a05('5', 'R[Al')](_0x2322bf['CStJW'](_0x2322bf[_0x5a05('6', 'fYxT')](_0x2322bf[_0x5a05('7', '[l1]')](_0x3440e2[0x3], '.'), _0x3440e2[0x2]), '.'), _0x3440e2[0x1]), '.'), _0x3440e2[0x0]);
    var _0x27b1c2 = _0x2a9264[_0x5a05('8', 'aZW4')]('.');
    var _0x4c090a = '';
    var _0x3f57dd = '.'[_0x5a05('9', 'oIrC')]();
    var _0x27cb4c = getRandom(0xa, 0x63);
    for (var _0x5e7f82 = 0x0; _0x5e7f82 < _0x27b1c2[_0x5a05('a', 'CCvN')]; _0x5e7f82++) {
        var _0x8b820b = 0x0;
        for (var _0x241427 = 0x0; _0x241427 < _0x27b1c2[_0x5e7f82][_0x5a05('b', 'zC&y')]; _0x241427++) {
            if (_0x2322bf['HBCoM'](_0x2322bf['Mrvck'], _0x5a05('c', '*$u@'))) {
                var _0x1889a1 = _0x2322bf[_0x5a05('d', 'pfi9')][_0x5a05('e', '$QLB')]('|')
                  , _0x5635d6 = 0x0;
                while (!![]) {
                    switch (_0x1889a1[_0x5635d6++]) {
                    case '0':
                        for (var _0x4e4044 = 0x0; _0x4e4044 < _0x15af67[_0x5a05('f', 'u^Wg')]; _0x4e4044++) {
                            var _0x59f12c = 0x0;
                            for (var _0xd234e3 = 0x0; _0x2322bf[_0x5a05('10', 'pfi9')](_0xd234e3, _0x15af67[_0x4e4044][_0x5a05('11', '@A7i')]); _0xd234e3++) {
                                var _0x9417eb = _0x15af67[_0x4e4044][_0x5a05('12', 'A&7[')](_0xd234e3);
                                var _0x1f4ec3 = _0x9417eb[_0x5a05('13', 'S!#!')]();
                                _0x59f12c = _0x59f12c + _0x1f4ec3;
                            }
                            if (_0x2322bf['gcduC'](_0x4e4044, _0x2322bf[_0x5a05('14', 'aZW4')](_0x15af67[_0x5a05('15', '&zUM')], 0x1)))
                                _0x59f12c = _0x2322bf['ZZkSa'](_0x59f12c, _0x1e84b1);
                            else
                                _0x59f12c = _0x2322bf['jFnqD'](_0x2322bf['jFnqD'](_0x59f12c, _0x44a20c), _0x1e84b1);
                            _0x26db21 += ',' + _0x59f12c;
                        }
                        continue;
                    case '1':
                        var _0x1e84b1 = getRandom(0x64, 0x3e7);
                        continue;
                    case '2':
                        return _0x2322bf['jFnqD'](_0x2322bf['jFnqD'](_0x1e84b1, ','), _0x26db21);
                    case '3':
                        var _0x15af67 = _0x48b728['split']('.');
                        continue;
                    case '4':
                        for (var _0x4e4044 = _0x2322bf[_0x5a05('16', 'z(p!')](_0x2c69f1[_0x5a05('17', 'LgnZ')], 0x1); _0x2322bf[_0x5a05('18', 'OAsZ')](_0x4e4044, 0x0); _0x4e4044--) {
                            _0x48b728 += '.' + _0x2c69f1[_0x4e4044];
                        }
                        continue;
                    case '5':
                        var _0x44a20c = '.'[_0x5a05('19', 'R[Al')]();
                        continue;
                    case '6':
                        if (_0x2c69f1[_0x5a05('1a', 'baFT')] == 0x0)
                            return '';
                        continue;
                    case '7':
                        var _0x2c69f1 = host['split']('.');
                        continue;
                    case '8':
                        _0x26db21 = _0x26db21[_0x5a05('1b', '5#aN')](0x1);
                        continue;
                    case '9':
                        if (!host)
                            return '';
                        continue;
                    case '10':
                        var _0x48b728 = '';
                        continue;
                    case '11':
                        var _0x26db21 = '';
                        continue;
                    case '12':
                        _0x48b728 = _0x48b728['slice'](0x1);
                        continue;
                    }
                    break;
                }
            } else {
                var _0x3e90a5 = _0x27b1c2[_0x5e7f82][_0x5a05('1c', '[l1]')](_0x241427);
                var _0x339e6b = _0x3e90a5[_0x5a05('1d', 'zG(x')]();
                _0x8b820b = _0x2322bf['vFxVM'](_0x8b820b, _0x339e6b);
            }
        }
        if (_0x5e7f82 == _0x2322bf[_0x5a05('1e', 'zG(x')](_0x27b1c2[_0x5a05('1f', 'Spm(')], 0x1))
            _0x8b820b = _0x2322bf[_0x5a05('20', 'L[Nl')](_0x8b820b, _0x27cb4c);
        else
            _0x8b820b = _0x8b820b + _0x3f57dd + _0x27cb4c;
        _0x4c090a += _0x2322bf[_0x5a05('21', ')s)6')](_0x8b820b, ',');
    }
    return _0x2322bf[_0x5a05('22', 'S!#!')](encodeURIComponent, _0x2322bf[_0x5a05('23', 'H%%S')](_0x27cb4c, ',') + _0x4c090a[_0x5a05('24', '5#aN')](0x0, _0x4c090a['length'] - 0x1));
}
function generateHostKey(_0x370984) {
    var _0xcd587e = {
        'jLdve': _0x5a05('25', 'VHC]'),
        'ZFXNF': function(_0x13e333, _0x37e69d) {
            return _0x13e333 + _0x37e69d;
        },
        'WGJBd': function(_0x51f854, _0x4cf7f1) {
            return _0x51f854 == _0x4cf7f1;
        },
        'WzPqo': function(_0x1a980b, _0x1ce297) {
            return _0x1a980b + _0x1ce297;
        },
        'gPtIt': function(_0x4cc9cc, _0x119977) {
            return _0x4cc9cc + _0x119977;
        },
        'AhllQ': function(_0x4c251c, _0x2ce103, _0x4b360b) {
            return _0x4c251c(_0x2ce103, _0x4b360b);
        },
        'wBogT': function(_0x314901, _0x2615b3) {
            return _0x314901 >= _0x2615b3;
        },
        'lqDbh': function(_0x32c379, _0x28bb19) {
            return _0x32c379 == _0x28bb19;
        }
    };
    var _0x3aa676 = _0xcd587e[_0x5a05('26', 'H%a1')][_0x5a05('e', '$QLB')]('|')
      , _0x1df2a2 = 0x0;
    while (!![]) {
        switch (_0x3aa676[_0x1df2a2++]) {
        case '0':
            for (var _0x49e85c = 0x0; _0x49e85c < _0x45f389[_0x5a05('27', 'H%%S')]; _0x49e85c++) {
                var _0x1d0481 = 0x0;
                for (var _0x3c83dd = 0x0; _0x3c83dd < _0x45f389[_0x49e85c]['length']; _0x3c83dd++) {
                    var _0x408c22 = _0x45f389[_0x49e85c][_0x5a05('28', 'zG(x')](_0x3c83dd);
                    var _0x955034 = _0x408c22['charCodeAt']();
                    _0x1d0481 = _0xcd587e[_0x5a05('29', 'CCvN')](_0x1d0481, _0x955034);
                }
                if (_0xcd587e[_0x5a05('2a', 'OAsZ')](_0x49e85c, _0x45f389[_0x5a05('2b', 'z(p!')] - 0x1))
                    _0x1d0481 = _0xcd587e['WzPqo'](_0x1d0481, _0x35b217);
                else
                    _0x1d0481 = _0xcd587e[_0x5a05('2c', 'S!#!')](_0x1d0481, _0x40a98f) + _0x35b217;
                _0x7d14e2 += ',' + _0x1d0481;
            }
            continue;
        case '1':
            var _0x50e526 = _0x370984[_0x5a05('2d', 'fYxT')]('.');
            continue;
        case '2':
            return _0xcd587e[_0x5a05('2e', 'OBJD')](_0x35b217, ',') + _0x7d14e2;
        case '3':
            var _0x35b217 = _0xcd587e[_0x5a05('2f', 'cwGq')](getRandom, 0x64, 0x3e7);
            continue;
        case '4':
            var _0x40a98f = '.'[_0x5a05('30', 'Z2[y')]();
            continue;
        case '5':
            _0xdfc11d = _0xdfc11d[_0x5a05('31', 'Z2[y')](0x1);
            continue;
        case '6':
            for (var _0x49e85c = _0x50e526[_0x5a05('32', 'VHC]')] - 0x1; _0xcd587e[_0x5a05('33', 'Z2[y')](_0x49e85c, 0x0); _0x49e85c--) {
                _0xdfc11d += '.' + _0x50e526[_0x49e85c];
            }
            continue;
        case '7':
            var _0x45f389 = _0xdfc11d['split']('.');
            continue;
        case '8':
            var _0x7d14e2 = '';
            continue;
        case '9':
            if (_0xcd587e[_0x5a05('34', 'PXyf')](_0x50e526['length'], 0x0))
                return '';
            continue;
        case '10':
            var _0xdfc11d = '';
            continue;
        case '11':
            if (!_0x370984)
                return '';
            continue;
        case '12':
            _0x7d14e2 = _0x7d14e2[_0x5a05('35', '&zUM')](0x1);
            continue;
        }
        break;
    }
}
function generateWordKey(_0x4ff704) {
    var _0x1d418d = {
        'SadiC': function(_0x278cdf, _0x610b81) {
            return _0x278cdf < _0x610b81;
        },
        'qavpq': function(_0x51a814, _0xf6e974) {
            return _0x51a814 * _0xf6e974;
        },
        'qWSAi': function(_0x2a0442, _0x34b03e) {
            return _0x2a0442 - _0x34b03e;
        },
        'IutVL': function(_0x18e228, _0x40caee, _0x3d42a3) {
            return _0x18e228(_0x40caee, _0x3d42a3);
        },
        'fXsRZ': _0x5a05('36', 'L[Nl'),
        'aItUy': function(_0xebba79, _0x3e28b6) {
            return _0xebba79 + _0x3e28b6;
        },
        'rpaFG': function(_0xf0b7fa, _0x48c7c9) {
            return _0xf0b7fa + _0x48c7c9;
        }
    };
    if (!_0x4ff704)
        return '';
    var _0x580571 = _0x4ff704[_0x5a05('37', 'vqcZ')]('');
    var _0x220c6e = _0x1d418d[_0x5a05('38', 'A&7[')](getRandom, 0x64, 0x3e7);
    var _0x28fb29 = '';
    for (var _0x2959d3 = 0x0; _0x2959d3 < _0x580571['length']; _0x2959d3++) {
        if (_0x1d418d['fXsRZ'] !== _0x1d418d[_0x5a05('39', 'R[Al')]) {
            var _0x456d3f = max;
            var _0x60a8d2 = min;
            if (_0x1d418d['SadiC'](_0x456d3f, _0x60a8d2)) {
                _0x456d3f = min;
                _0x60a8d2 = max;
            }
            var _0x1e92cc = parseInt(_0x1d418d[_0x5a05('3a', 'A&7[')](Math[_0x5a05('3b', 'ePU*')](), _0x1d418d[_0x5a05('3c', 's]^c')](_0x456d3f, _0x60a8d2) + 0x1) + _0x60a8d2);
            return _0x1e92cc;
        } else {
            var _0x38e67a = _0x580571[_0x2959d3][_0x5a05('3d', 'zC&y')]();
            var _0x4d6da0 = _0x1d418d['aItUy'](_0x38e67a, _0x220c6e);
            _0x28fb29 += _0x1d418d['rpaFG'](',', _0x4d6da0);
        }
    }
    _0x28fb29 = _0x28fb29['slice'](0x1);
    return _0x1d418d[_0x5a05('3e', 'KH#v')](_0x220c6e + ',', _0x28fb29);
}
function getRandom(_0x4e55a8, _0x32f19d) {
    var _0x44dbb8 = {
        'jrDEd': _0x5a05('3f', 'gU%7'),
        'CXIjV': function(_0xba00af, _0x4f008a) {
            return _0xba00af < _0x4f008a;
        },
        'EatUz': function(_0x39dff0, _0x3e98dd) {
            return _0x39dff0(_0x3e98dd);
        },
        'eIlgU': function(_0x1c6179, _0x5c50b7) {
            return _0x1c6179 + _0x5c50b7;
        },
        'NhinH': function(_0x453957, _0x14be06) {
            return _0x453957 * _0x14be06;
        },
        'rANlO': function(_0x1b5b5b, _0x4abb5f) {
            return _0x1b5b5b - _0x4abb5f;
        }
    };
    var _0x367812 = _0x44dbb8[_0x5a05('40', 'z(p!')][_0x5a05('41', 'LgnZ')]('|')
      , _0x15cfd3 = 0x0;
    while (!![]) {
        switch (_0x367812[_0x15cfd3++]) {
        case '0':
            var _0x1761e1 = _0x32f19d;
            continue;
        case '1':
            var _0x2a4991 = _0x4e55a8;
            continue;
        case '2':
            return _0x20852c;
        case '3':
            if (_0x44dbb8[_0x5a05('42', 'cwGq')](_0x1761e1, _0x2a4991)) {
                _0x1761e1 = _0x4e55a8;
                _0x2a4991 = _0x32f19d;
            }
            continue;
        case '4':
            var _0x20852c = _0x44dbb8[_0x5a05('43', '[l1]')](parseInt, _0x44dbb8[_0x5a05('44', '82%Y')](_0x44dbb8['NhinH'](Math[_0x5a05('45', 'pfi9')](), _0x44dbb8[_0x5a05('46', '@A7i')](_0x1761e1, _0x2a4991) + 0x1), _0x2a4991));
            continue;
        }
        break;
    }
}
;_0xodv = 'jsjiami.com.v6';

"""
        token_js = execjs.compile(generate_key_js.replace("$_0x217bb6",ip))
        token = token_js.call("generateKey")
        if token:
            token = token.replace("%2C",",")
        self.marmo_log["datas"].append("side stations token =="+str(token))
        return token

    '''
        获取数据
    '''
    def getAjaxTool(self,ip):
            page = 1
            while True:

                ajax_headers =self.headers
                ajax_headers["cookies"]=self.cookies
                ajax_headers["X-Requested-With"]="XMLHttpRequest"
                callback = self.expando()
                url = self.ajax_url%(callback)
                self.marmo_log["datas"].append("getAjaxTool url =="+str(url))
                form_data ={
                    "page":(None,page),
                    "iplist":(None,b64encode(ip.encode(encoding="UTF-8")).decode(encoding="UTF-8")),
                    "token":(None,self.getToken(ip))
                }
                res = requests.post(url,headers=ajax_headers,files=form_data)
                if res.status_code ==200:
                    text = res.text
                    logger.log("旁站数据获取结果=="+str(text))
                    self.marmo_log["datas"].append("旁站数据获取结果=="+str(text))
                    has_exists_data =self.parse_chinaz(text)
                    if has_exists_data:
                        page += 1
                        time.sleep(2)
                        continue


                    else:
                        break
            logger.log("旁站获取完毕")
            logger.log(self.host_list)
            self.marmo_log["datas"].append("旁站hosts =="+str(self.host_list))
            if len(self.host_list) >=1:
                self.data_info["exists_data"]=True
                self.data_info["status_code"]=2
                self.data_info["data"]=str(self.host_list)
            else:
                self.data_info["status_code"] = 2
                self.data_info["exists_data"] = False




    '''
        解析数据
        jQuery111304818904455408477_1622427730365({"StateCode":1,"Message":"成功","Result":[{"index":1,"host":"11188.lnweb03.eastftp.net","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":2,"host":"27181.lnweb03.eastftp.net","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":3,"host":"24825.lnweb03.eastftp.net","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":4,"host":"26129.lnweb03.eastftp.net","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":5,"host":"www.cbid.com.cn","title":"北京中基亚太贸易有限公司","rank":0,"shoulu":"-","IPAddressList":[]},{"index":6,"host":"www.bfdq.com","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":7,"host":"www.bjhongda.com","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":8,"host":"www.lienhe.com.cn","title":"北京利恩和","rank":1,"shoulu":"-","IPAddressList":[]},{"index":9,"host":"www.lslock.com","title":"-","rank":1,"shoulu":"-","IPAddressList":[]},{"index":10,"host":"www.dsbl-cn.com","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":11,"host":"www.zky17.com","title":"培养箱|恒温摇床|干燥箱|冷冻离心机|LED冷光源|血液保存箱|分析检测仪器|实验室仪器|中科浩宇仪器","rank":0,"shoulu":"596","IPAddressList":[]},{"index":12,"host":"www.cntchina.com","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":13,"host":"www.northerncross.cn","title":"灌溉设备，草坪喷头，摇臂喷头，滴灌，喷灌，三通四联灌溉公司","rank":0,"shoulu":"81","IPAddressList":[]},{"index":14,"host":"www.solar.com.cn","title":"-","rank":1,"shoulu":"-","IPAddressList":[]},{"index":15,"host":"www.usky.com.cn","title":"-","rank":1,"shoulu":"-","IPAddressList":[]},{"index":16,"host":"www.baiao.com","title":"北京百奥药业有限责任公司","rank":1,"shoulu":"695","IPAddressList":[]},{"index":17,"host":"hmhrwj.com","title":"-","rank":1,"shoulu":"-","IPAddressList":[]},{"index":18,"host":"isuzu-china.com","title":"-","rank":1,"shoulu":"-","IPAddressList":[]},{"index":19,"host":"ihouse.cn","title":"-","rank":0,"shoulu":"-","IPAddressList":[]},{"index":20,"host":"accez.com.cn","title":"-","rank":0,"shoulu":"-","IPAddressList":[]}],"Total":135,"TotalPages":0})
        jQuery111308652390505405496_1623028885280({"StateCode":1,"Message":"成功","Result":[],"Total":135,"TotalPages":0})
    '''

    def parse_chinaz(self,data):
        # try:
            data_pattern = 'jQuery[\d\s]*\({(.*?)}\)'
            res = re.findall(data_pattern,data)
            if res and len(res) >=1:
                temp_data_string = res[0]
                logger.log("旁站json == "+str(temp_data_string))
                self.marmo_log["datas"].append("旁站json == "+str(temp_data_string))
                if "Message" in temp_data_string and "StateCode" in temp_data_string:
                    temp_data_string = "{" + temp_data_string
                    temp_data_string = temp_data_string + "}"
                    tool_json = json.loads(temp_data_string)
                    if tool_json.__contains__("Result"):
                        result = tool_json["Result"]
                        self.marmo_log["datas"].append("parse chinaz result =="+str(result))
                        if result and isinstance(result,list):
                            if len(result) >=1:
                                for each_side_stations in result:
                                    side_station_obj ={}
                                    host=each_side_stations["host"]
                                    side_station_obj["host"]=host
                                    title = each_side_stations["title"]
                                    side_station_obj["title"]=title
                                    # side_station_obj["create_time"]=datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),"%Y-%m-%d %H:%M:%S")
                                    self.host_list.append(side_station_obj)
                                return True
                            else:
                                return False
                        else:
                            logger.log("%s 没有旁站数据"%(str(self.ip)))
                            self.marmo_log["datas"].append("%s 没有旁站数据"%(str(self.ip)))
        # except Exception as e:
        #     print("parse chinaz 出现异常=="+str(e.__str__()))
        #     self.error_reson ="parse chinaz 出现异常=="+str(e.__str__())
        #     return False

    '''
        run函数
    '''
    def run(self):
        try:
            self.getAjaxTool(self.ip)
            marmo_ping = MarmoPing()
            for host in self.host_list:
                ip = marmo_ping.ping(host["host"])
                self.marmo_log["datas"].append("ping 返回的ip==="+str(ip)+",原本的host=="+str())
                if ip ==self.ip:
                    '''
                        解析ip和输入的ip一致
                    '''

                    self.ping_host_list.append(host)
            '''
                旁站入库
            '''
            side_station_dao = SideStaionsDao()
            for station in self.ping_host_list:
                add_params ={
                    "info":station,
                    "asset_id":self.asset_data["asset_id"],
                    "project_id":self.asset_data["project_id"]
                }
                side_station_dao.insert_side_station(add_params)

        except Exception as e:
            self.data_info["exists_data"] = False
            self.data_info["status_code"] = 3
            self.data_info["fail_reason"] = "获取旁站信息异常=="+str(e.__str__())
            self.marmo_log["exceptions"].append("获取旁站信息异常=="+str(e.__str__()))
        finally:
            '''
                marmo_log入库
            '''
            add_log_params = {
                "module": "SIDE_STATION",
                "type": '1',
                "module_log": str(self.marmo_log),
                "asset_id": int(self.asset_data["asset_id"])
            }
            MarmoLogDao().add_log(add_log_params)
            return self.data_info





if __name__ =="__main__":
    side_station = SideStations({"ip":"211.100.61.187"})
    side_station.run()









