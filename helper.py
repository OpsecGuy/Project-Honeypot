from datetime import datetime, timezone
from collections import deque
from pathlib import Path

import os
import json
import httpx
import asyncio
import logging


VERSION = "1.1.4"


class Config:
    def __init__(self):
        if not Path("config.json").exists():
            print('Config file does not exist. Creating new one...')
            self.create_config_file()
            os._exit(1)
        self.options = self.read_config_file()

    def create_config_file(self):
        data = {
            "ip_addr": "0.0.0.0",
            "start_port": 15,
            "end_port": 1000,
            "udp_mode": True,
            "tcp_mode": False,
            "db_ip": "XXX.XXX.XXX.XXX",
            "db_name": "XXXXXXXXXXXX",
            "db_user": "XXXXXXXXXXXX",
            "db_pwd": "XXXXXXXXXXXXXX",
            "verbose": 0
        }
        
        with Path("config.json").open("w") as file:
            file.write(json.dumps(data, indent=4))

    def read_config_file(self):
        with Path("config.json").open("r") as file:
            return json.load(file)

def get_ip_address_details(ip_addr: str):
    try:
        with httpx.Client() as client:
            response = client.get(
                url=f"https://api.ipquery.io/{ip_addr}"
            ).json()
            return {"location": response["location"]["country"], "asn": response["isp"]["asn"], "organization": response["isp"]["org"], "isp": response["isp"]["isp"]}
    except Exception as err:
        logging.warning(f"Failed to fetch IP address data due to: {err}")
        return None, None, None, None

def find_protocol_by_data(data):
    for name in KNOWN_PAYLOADS.keys():
        for payload in KNOWN_PAYLOADS[name]["payloads"]:
            if payload["atomic_search"] == True and payload["data"].lower() in data:
                return name
            elif payload["atomic_search"] == False and data == payload["data"].lower():
                return name
    return "Unknown"


KNOWN_PAYLOADS = {
    "DNS": {
        "ports": [53],
        "payloads": [
            {
                "data": "45670100000100000000000102736c0000ff0001000029ffff000000000000",
                "atomic_search": False
            },
            {
                "data": "0E14002000010000000000010F6379626572726573696C69656E636502696F00000100010000291000000000000000",
                "atomic_search": False
            },
            {
                "data": "1234010000010000000000000462696E6703636F6D0000010001",
                "atomic_search": False
            },
            {
                "data": "AD7A0100000100000000000108636F6C6C65637464036F72670000FF0001000029FFF7000000000000",
                "atomic_search": False
            },
            {
                "data": "0FAF012000010000000000000776657273696F6E0462696E64000010000300",
                "atomic_search": False
            },
            {
                "data": "51FF01200001000000000001046869676903636F6D0000FF00010000291000000000000000",
                "atomic_search": False
            },
            {
                "data": "34EF010000010000000000000756455253494F4E0442494E440000100003",
                "atomic_search": False
            },
            {
                "data": "5591010000010000000000000679616E6465780272750000010001",
                "atomic_search": False
            },
            {
                "data": "6578616D706C6503636F6D",
                "atomic_search": True
            },
            {
                "data": "697009706172726F74646E7303636F6D",
                "atomic_search": True
            }
        ]
    },
    "TFTP": {
        "ports": [69],
        "payloads": [
            {
                "data": "0001612E706466006F6374657400",
                "atomic_search": False
            },
            {
                "data": "00014c54456b63474a48006e6574617363696900",
                "atomic_search": False
            }
        ]
    },
    "Ubiquiti": {
        "ports": [10001],
        "payloads": [
            {
                "data": "01000000",
                "atomic_search": False
            }
        ]
    },
    
    "NFS": {
        "ports": [2049],
        "payloads": [
            {
                "data": "02000186a00000000400",
                "atomic_search": True
            }
        ]
    },
    "Portmap": {
        "ports": [111],
        "payloads": [
            {
                "data": "65720a370000000000000002000186a0000000020000000400000000000000000000000000000000",
                "atomic_search": True
            }
        ]
    },
    "MemcacheD": {
        "ports": [11211],
        "payloads": [
            {
                "data": "0001000000010000676574732070206820650a",
                "atomic_search": False
            },
            {
                "data": "00010000000100007374617473206974656D730D0a",
                "atomic_search": False
            },
            {
                "data": "5a4d0000000100007374617473206974656d730d0a",
                "atomic_search": False
            },
            {
                "data": "5a4d00000001000073746174730d0a",
                "atomic_search": False
            },
            {
                "data": "000000000001000073746174730a",
                "atomic_search": False
            },
            {
                "data": "000100000001000073746174730d0a",
                "atomic_search": False
            },
        ]
    },
    "OpenVPN": {
        "ports": [1194],
        "payloads": [
            {
                "data": "38",
                "atomic_search": False
            },
            {
                "data": "3812121212121212000000000038B126DE",
                "atomic_search": False
            }
        ]
    },
    "NetBIOS": {
        "ports": [137, 138, 139],
        "payloads": [
            {
                "data": "000100000000000020434b414141414141414141414141414141414141414141414141414141414141",
                "atomic_search": True
            }
        ]
    },
    "MSSQL": {
        "ports": [1433, 1434],
        "payloads": [
            {
                "data": "02",
                "atomic_search": False
            }
        ]
    },
    "Citrix": {
        "ports": [1604],
        "payloads": [
            {
                "data": "2a00013202fda8e300000000000000000000000000000000000000002100020000000000000000000000",
                "atomic_search": False
            }
        ]
    },
    "SNMP": {
        "ports": [161],
        "payloads": [
            {
                "data": "302002010104067075626c6963a51302020001020100020146300730050601280500",
                "atomic_search": False
            },
            {
                "data": "302602010104067075626C6963A1190204DC63C29A020100020100300B300906052B060102010500",
                "atomic_search": False
            }
        ]
    },
    "QOTD": {
        "ports": [17],
        "payloads": [
            {
                "data": "0d",
                "atomic_search": False
            }
        ]
    },
    "XDMCP": {
        "ports": [177],
        "payloads": [
            {
                "data": "00010002000100",
                "atomic_search": False
            }
        ]
    },
    "Steam Remote Play": {
        "ports": [27036],
        "payloads": [
            {
                "data": "ffffffff214c5fa00500000008d2091000",
                "atomic_search": False
            }
        ]
    },
    "Digiman": {
        "ports": [2362],
        "payloads": [
            {
                "data": "4449474900010006ffffffffffff",
                "atomic_search": False
            }
        ]
    },
    "Plex Media Server": {
        "ports": [32412, 32414],
        "payloads": [
            {
                "data": "x4d",
                "atomic_search": False
            }
        ]
    },
    "RDP": {
        "ports": [3389],
        "payloads": [
            {
                "data": "00000000000000ff0000000000000000",
                "atomic_search": False
            }
        ]
    },
    "WSD": {
        "ports": [3702],
        "payloads": [
            {
                "data": "3C7464733A476574",
                "atomic_search": True
            },
            {
                "data": "3C7472743A47657450726F66696C6573202F3E",
                "atomic_search": False
            },
            {
                "data": "3C3A3E",
                "atomic_search": False
            },
            {
                "data": "3C3A2F3E",
                "atomic_search": False
            },
            {
                "data": "3A3C3E2F0A",
                "atomic_search": False
            },
            {
                "data": "3C7773643A54797065733E777364703A4465766963653C2F7773643A54797065733E",
                "atomic_search": True
            }
        ]
    },
    "cLDAP": {
        "ports": [389],
        "payloads": [
            {
                "data": "3025020101632004000A01000A0100020100020100010100870B6F626A656374636C6173733000",
                "atomic_search": False
            }
        ]
    },
    "Lantronix": {
        "ports": [30718],
        "payloads": [
            {
                "data": "000000f8",
                "atomic_search": False
            }
        ]
    },
    "ARD (Apple Remote Desktop)": {
        "ports": [3283],
        "payloads": [
            {
                "data": "00140000",
                "atomic_search": False
            }
        ]
    },
    "STUN": {
        "ports": [3478, 8088, 37833],
        "payloads": [
            {
                "data": "000100002112a442000000000000000000000000",
                "atomic_search": False
            }
        ]
    },
    "CoAP": {
        "ports": [5683],
        "payloads": [
            {
                "data": "40010101bb2e77656c6c2d6b6e6f776e04636f7265",
                "atomic_search": False
            },
            {
                "data": "40017D70BB2E77656C6C2D6B6E6F776E04636F7265",
                "atomic_search": False
            },
            {
                "data": "400101CEBB2E77656C6C2D6B6E6F776E04636F7265",
                "atomic_search": False
            },
            {
                "data": "40017257BB2E77656C6C2D6B6E6F776E04636F7265",
                "atomic_search": False
            },
            {
                "data": "40014B70BB2E77656C6C2D6B6E6F776E04636F7265",
                "atomic_search": False
            },
            {
                "data": "40016570BB2E77656C6C2D6B6E6F776E04636F7265",
                "atomic_search": False
            },
            {
                "data": "40015477BB2E77656C6C2D6B6E6F776E04636F7265",
                "atomic_search": False
            },
        ]
    },
    "NTP": {
        "ports": [123],
        "payloads": [
            {
                "data": "1700032a00000000",
                "atomic_search": True
            }
        ]
    },
    "SADP": {
        "ports": [37020],
        "payloads": [
            {
                "data": "3C3F786D6C2076657273696F6E3D27312E302720656E636F64696E673D277574662D38273F3E3C50726F62653E3C557569643E737472696E673C2F557569643E3C54797065733E696E71756972793C2F54797065733E3C2F50726F62653E",
                "atomic_search": False
            },
            {
                "data": "3C3F786D6C2076657273696F6E3D22312E302220656E636F64696E673D227574662D38223F3E0A3C50726F62653E0A3C557569643E737472696E673C2F557569643E0A3C54797065733E696E71756972793C2F54797065733E0A3C2F50726F62653E0A",
                "atomic_search": False
            }
        ]
    },
    "Source Engine": {
        "ports": [27015, 27019, 27105, 28015],
        "payloads": [
            {
                "data": "FFFFFFFF54536F7572636520456E67696E6520517565727900",
                "atomic_search": False
            }
        ]
    },
    "MDNS": {
        "ports": [5353],
        "payloads": [
            {
                "data": "000000000001000000000000095F7365727669636573075F646E732D7364045F756470056C6F63616C00000C0001",
                "atomic_search": False
            }
        ]
    },
    "DVR": {
        "ports": [37810],
        "payloads": [
            {
                "data": "ff",
                "atomic_search": False
            }
        ]
    },
    "RTSP": {
        "ports": [554],
        "payloads": [
            {
                "data": "4445534352494245202F20525453502F312E30",
                "atomic_search": True
            }
        ]
    },
    "SIP": {
        "ports": [5060],
        "payloads": [
            {
                "data": "4F5054494F4E53",
                "atomic_search": True
            }
        ]
    },
    "SLP": {
        "ports": [427],
        "payloads": [
            {
                "data": "0201000022000000000000050002656E0000000000000000000841",
                "atomic_search": True
            }
        ]
    },
    "Sentinel": {
        "ports": [5093],
        "payloads": [
            {
                "data": "7a0000000000",
                "atomic_search": False
            }
        ]
    },
    "IPSec": {
        "ports": [500, 4500],
        "payloads": [
            {
                "data": "488B1472935D7021",
                "atomic_search": False
            },
            {
                "data": "2100000000000000000000000000000001",
                "atomic_search": False
            }
        ]
    },
    "RADIUS": {
        "ports": [1645, 1646, 1812, 1813],
        "payloads": [
            {
                "data": "001400000000000000000000000000000000",
                "atomic_search": True
            }
        ]
    },
    "Chargen": {
        "ports": [19],
        "payloads": [
            {
                "data": "01",
                "atomic_search": False
            }
        ]
    },
    # ! Not fully checked
    # "MATIP": {
    #     "ports": [351],
    #     "payloads": [
    #         {
    #             "data": "000000010000000100000004000000080000000100000000",
    #             "atomic_search": False
    #         }
    #     ]
    # },
    "POTENTIAL BOTNETS": {
        "ports": [],
        "payloads": [
            {
                "data": "776765742068747470",
                "atomic_search": True
            },
            {
                "data": "6375726C2068747470",
                "atomic_search": True
            },
            {
                "data": "63686D6F6420",
                "atomic_search": True
            }
        ]
    }
}

#? "1900": { 
#?        "SSDP": b"M-SEARCH\r\nST:ssdp:all\r\nMAN:\"ssdp:discover\"\r\n"
#?    },

