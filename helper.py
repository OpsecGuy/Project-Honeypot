from datetime import datetime, timezone
from collections import deque

import os
import json
import asyncio
import logging


class Config:
    def __init__(self):
        if not os.path.exists("config.json"):
            print('Config file does not exist. Creating new one...')
            self.create_config_file()
            os._exit(1)
        
        self.options = self.read_config_file()
    

    def create_config_file(self):
        data = {
            "ip_addr": "0.0.0.0",
            "start_port": 15,
            "end_port": 1000,
            "db_ip": "XXX.XXX.XXX.XXX",
            "db_name": "XXXXXXXXXXXX",
            "db_user": "XXXXXXXXXXXX",
            "db_pwd": "XXXXXXXXXXXXXX",
        }
        
        with open("config.json", 'w') as file:
            file.write(json.dumps(data))

    def read_config_file(self):
        with open("config.json", "r") as file:
            return json.load(file)


def is_potential_botnet(data: bytes):
    payloads = ["776765742068747470", "6375726C2068747470", "63686D6F6420"]
    payload_bytes = [bytes.fromhex(payload) for payload in payloads]

    for payload in payload_bytes:
        if payload.hex() in data.hex():
            return True
    return False


known_payloads = {
    "53": {
        "DNS1": b"\x45\x67\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x02\x73\x6c\x00\x00\xff\x00\x01\x00\x00\x29\xff\xff\x00\x00\x00\x00\x00\x00",
        "DNS2": b"\x0E\x14\x00\x20\x00\x01\x00\x00\x00\x00\x00\x01\x0F\x63\x79\x62\x65\x72\x72\x65\x73\x69\x6C\x69\x65\x6E\x63\x65\x02\x69\x6F\x00\x00\x01\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x00",
        "DNS3": b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x04\x62\x69\x6E\x67\x03\x63\x6F\x6D\x00\x00\x01\x00\x01",
        "DNS4": b"\xAD\x7A\x01\x00\x00\x01\x00\x00\x00\x00\x00\x01\x08\x63\x6F\x6C\x6C\x65\x63\x74\x64\x03\x6F\x72\x67\x00\x00\xFF\x00\x01\x00\x00\x29\xFF\xF7\x00\x00\x00\x00\x00\x00",
        "DNS5": b"\x0F\xAF\x01\x20\x00\x01\x00\x00\x00\x00\x00\x00\x07\x76\x65\x72\x73\x69\x6F\x6E\x04\x62\x69\x6E\x64\x00\x00\x10\x00\x03\x00",
        "DNS6": b"\x51\xFF\x01\x20\x00\x01\x00\x00\x00\x00\x00\x01\x04\x68\x69\x67\x69\x03\x63\x6F\x6D\x00\x00\xFF\x00\x01\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00\x00",
        "DNS7": b"\x34\xEF\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07\x56\x45\x52\x53\x49\x4F\x4E\x04\x42\x49\x4E\x44\x00\x00\x10\x00\x03",
        "DNS8": b"\x55\x91\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06\x79\x61\x6E\x64\x65\x78\x02\x72\x75\x00\x00\x01\x00\x01",
    },
    "69": {
        "TFTP": b"\x00\x01\x61\x2E\x70\x64\x66\x00\x6F\x63\x74\x65\x74\x00",
    },
    "10001": {
        "Ubiquiti": b"\x01\x00\x00\x00"
    },
    "10074": {
        "TP240 Mitel Phone System": b"\x63\x61\x6c\x6c\x2e\x73\x74\x61\x72\x74\x62\x6c\x61\x73\x74\x20\x32\x30\x30\x30\x20\x33\x00"
    },
    "111": {
        "Portmap": b"\x65\x72\x0a\x37\x00\x00\x00\x00\x00\x00\x00\x02\x00\x01\x86\xa0\x00\x00\x00\x02\x00\x00\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    },
    "11211": {
        "MemcacheD": b"\x00\x01\x00\x00\x00\x01\x00\x00gets p h e\n"
    },
    "1194": {
        "OpenVPN1": b"\x38",
        "OpenVPN2": b"\x38\x12\x12\x12\x12\x12\x12\x12\x12\x00\x00\x00\x00\x00\x38\xB1\x26\xDE"
    },
    "137": {
        "NetBIOS": b"\xe5\xd8\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21\x00\x01"
    },
    "138": {
        "NetBIOS": b"\xe5\xd8\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21\x00\x01"
    },
    "139": {
        "NetBIOS": b"\xe5\xd8\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21\x00\x01"
    },
    "1433": {
        "MSSQL": b"\x02"
    },
    "1434": {
        "MSSQL": b"\x02"
    },
    "1604": {
        "Citrix": b"\x2a\x00\x01\x32\x02\xfd\xa8\xe3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x21\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "161": {
        "SNMP1": b"\x30\x20\x02\x01\x01\x04\x06\x70\x75\x62\x6c\x69\x63\xa5\x13\x02\x02\x00\x01\x02\x01\x00\x02\x01\x46\x30\x07\x30\x05\x06\x01\x28\x05\x00",
        "SNMP2": b"\x30\x26\x02\x01\x01\x04\x06\x70\x75\x62\x6C\x69\x63\xA1\x19\x02\x04\xDC\x63\xC2\x9A\x02\x01\x00\x02\x01\x00\x30\x0B\x30\x09\x06\x05\x2B\x06\x01\x02\x01\x05\x00",
    },
    "17": {
        "QOTD": b"\x0d"
    },
    "17185": {
        "vxWorks WDB ONCRPC": b"\x1a\x09\xfa\xba\x00\x00\x00\x00\x00\x00\x00\x02\x55\x55\x55\x55\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x55\x12\x00\x00\x00\x3c\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "177": {
        "XDMCP": b"\x00\x01\x00\x02\x00\x01\x00"
    },
    "1900": { # ???
        "SSDP": b"M-SEARCH\r\nST:ssdp:all\r\nMAN:\"ssdp:discover\"\r\n"
    },
    "20811": {
        "PHMGMT": b"\x00"
    },
    "2362": {
        "Digiman": b"\x44\x49\x47\x49\x00\x01\x00\x06\xff\xff\xff\xff\xff\xff"
    },
    "27036": {
        "Steam Remote Play": b"\xff\xff\xff\xff\x21\x4c\x5f\xa0\x05\x00\x00\x00\x08\xd2\x09\x10\x00"
    },
    "30120": {
        "FiveM": b"\xff\xff\xff\xffgetstatus",
    },
    "30718": {
        "Lantronix": b"\x00\x00\x00\xf8",
    },
    "32412": {
        "Plex Media Server": b"\x4d",
    },
    "32414": {
        "Plex Media Server": b"\x4d",
    },
    "3283": {
        "ARD (Apple Remote Desktop)": b"\x00\x14\x00\x00",
    },
    "33848": {
        "Jenkins": b"",
    },
    "3389": {
        "RDP": b"\x00\x00\x00\x00\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "3478": {
        "STUN": b"\x00\x01\x00\x00\x21\x12\xa4\x42\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "8088": {
        "STUN": b"\x00\x01\x00\x00\x21\x12\xa4\x42\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "37833": {
        "STUN": b"\x00\x01\x00\x00\x21\x12\xa4\x42\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "3702": {
        "WSD1": b"\x3C\x74\x64\x73\x3A\x47\x65\x74\x44\x65\x76\x69\x63\x65\x49\x6E\x66\x6F\x72\x6D\x61\x74\x69\x6F\x6E\x20\x2F\x3E",
        "WSD2": b"\x3C\x74\x64\x73\x3A\x47\x65\x74\x53\x65\x72\x76\x69\x63\x65\x73\x20\x2F\x3E",
        "WSD3": b"\x3C\x74\x64\x73\x3A\x47\x65\x74\x43\x61\x70\x61\x62\x69\x6C\x69\x74\x69\x65\x73\x20\x2F\x3E",
        "WSD4": b"\x3C\x74\x72\x74\x3A\x47\x65\x74\x50\x72\x6F\x66\x69\x6C\x65\x73\x20\x2F\x3E",
        "WSD5": b"\x3C\x3A\x3E",
        "WSD6": b"\x3C\x3A\x2F\x3E",
        "WSD7": b"\x3A\x3C\x3E\x2F\x0A"
    },
    "37810": {
        "DVR": b"\xff",
    },
    "3784": {
        "BFD": b"\x56\xc8\xf4\xf9\x60\xa2\x1e\xa5\x4d\xfb\x03\xcc\x51\x4e\xa1\x10\x95\xaf\xb2\x67\x17\x67\x81\x32\xfb\x57\xfd\x8e\xd2\x22\x72\x03\x34\x7a\xbb\x98",
    },
    "389": {
        "cLDAP": b"\x30\x25\x02\x01\x01\x63\x20\x04\x00\x0a\x01\x00\x0a\x01\x00\x02\x01\x00\x02\x01\x00\x01\x01\x00\x87\x0b\x6f\x62\x6a\x65\x63\x74\x63\x6c\x61\x73\x73\x30\x00",
    },
    "41794": {
        "Crestron": b"\x14",
    },
    "427": {
        "SLP1": b"\x02\t\x00\x00\x1d\x00\x00\x00\x00\x00s_\x00\x02en\x00\x00\xff\xff\x00\x07default",
        "SLP2": b"\x02\x01\x00\x00\x22\x00\x00\x00\x00\x00\x00\x05\x00\x02\x65\x6E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x41\x41\x41\x41\x41\x41\x41\x41"
    },
    "443": {
        "DTLS": b"\x0a\x00\x00\x00\x00\x00\x00\x00\x00",
        "QUIC": b"\x0e\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "500": {
        "IPSec": b"\x21\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01",
    },
    "5060": {
        "SIP1": b"\xaa",
        "SIP2": b"\x4F\x50\x54\x49\x4F\x4E\x53",
    },
    "5093": {
        "Sentinel": b"\x7a\x00\x00\x00\x00\x00",
    },
    "53413": {
        "Netis": b"\x0a",
    },
    "5351": {
        "NAT-PMP": b"\x00\x00",
    },
    "5683": {
        "CoAP1": b"\x40\x01\x01\x01\xbb\x2e\x77\x65\x6c\x6c\x2d\x6b\x6e\x6f\x77\x6e\x04\x63\x6f\x72\x65",
        "CoAP2": b"\x40\x01\x7D\x70\xBB\x2E\x77\x65\x6C\x6C\x2D\x6B\x6E\x6F\x77\x6E\x04\x63\x6F\x72\x65",
        "CoAP3": b"\x40\x01\x01\xCE\xBB\x2E\x77\x65\x6C\x6C\x2D\x6B\x6E\x6F\x77\x6E\x04\x63\x6F\x72\x65",
        "CoAP4": b"\x40\x01\x72\x57\xBB\x2E\x77\x65\x6C\x6C\x2D\x6B\x6E\x6F\x77\x6E\x04\x63\x6F\x72\x65",
        "CoAP5": b"\x40\x01\x4B\x70\xBB\x2E\x77\x65\x6C\x6C\x2D\x6B\x6E\x6F\x77\x6E\x04\x63\x6F\x72\x65",
        "CoAP6": b"\x40\x01\x65\x70\xBB\x2E\x77\x65\x6C\x6C\x2D\x6B\x6E\x6F\x77\x6E\x04\x63\x6F\x72\x65",
        "CoAP7": b"\x40\x01\x01\x01\xBB\x2E\x77\x65\x6C\x6C\x2D\x6B\x6E\x6F\x77\x6E\x04\x63\x6F\x72\x65",
        "CoAP8": b"\x40\x01\x54\x77\xBB\x2E\x77\x65\x6C\x6C\x2D\x6B\x6E\x6F\x77\x6E\x04\x63\x6F\x72\x65",
    },
    "7001": {
        "Andrew File System (AFS)": b"\x00\x00\x03\xe7\x00\x00\x00\x00\x00\x00\x00\x65\x00\x00\x00\x00\x00\x00\x00\x00\x0d\x05\x00\x00\x00\x00\x00\x00\x00",
    },
    "80": {
        "QUIC": b"\x0e\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "123": {
        "NTP1": b"\x17\x00\x03\x2a\x00\x00\x00\x00",
        "NTP2": b"\x17\x00\x03\x2A\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
    },
    "37020": {
        "SADP1": b"\x3C\x3F\x78\x6D\x6C\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x27\x31\x2E\x30\x27\x20\x65\x6E\x63\x6F\x64\x69\x6E\x67\x3D\x27\x75\x74\x66\x2D\x38\x27\x3F\x3E\x3C\x50\x72\x6F\x62\x65\x3E\x3C\x55\x75\x69\x64\x3E\x73\x74\x72\x69\x6E\x67\x3C\x2F\x55\x75\x69\x64\x3E\x3C\x54\x79\x70\x65\x73\x3E\x69\x6E\x71\x75\x69\x72\x79\x3C\x2F\x54\x79\x70\x65\x73\x3E\x3C\x2F\x50\x72\x6F\x62\x65\x3E",
        "SADP2": b"\x3C\x3F\x78\x6D\x6C\x20\x76\x65\x72\x73\x69\x6F\x6E\x3D\x22\x31\x2E\x30\x22\x20\x65\x6E\x63\x6F\x64\x69\x6E\x67\x3D\x22\x75\x74\x66\x2D\x38\x22\x3F\x3E\x0A\x3C\x50\x72\x6F\x62\x65\x3E\x0A\x3C\x55\x75\x69\x64\x3E\x73\x74\x72\x69\x6E\x67\x3C\x2F\x55\x75\x69\x64\x3E\x0A\x3C\x54\x79\x70\x65\x73\x3E\x69\x6E\x71\x75\x69\x72\x79\x3C\x2F\x54\x79\x70\x65\x73\x3E\x0A\x3C\x2F\x50\x72\x6F\x62\x65\x3E\x0A"
    },
    "5353": {
        "MDNS": b"\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09\x5F\x73\x65\x72\x76\x69\x63\x65\x73\x07\x5F\x64\x6E\x73\x2D\x73\x64\x04\x5F\x75\x64\x70\x05\x6C\x6F\x63\x61\x6C\x00\x00\x0C\x00\x01",
    },
    "27015": {
        "Source Engine": b"\xFF\xFF\xFF\xFF\x54\x53\x6F\x75\x72\x63\x65\x20\x45\x6E\x67\x69\x6E\x65\x20\x51\x75\x65\x72\x79\x00"
    },
    "27019": {
        "Source Engine": b"\xFF\xFF\xFF\xFF\x54\x53\x6F\x75\x72\x63\x65\x20\x45\x6E\x67\x69\x6E\x65\x20\x51\x75\x65\x72\x79\x00"
    },
    "27105": {
        "Source Engine": b"\xFF\xFF\xFF\xFF\x54\x53\x6F\x75\x72\x63\x65\x20\x45\x6E\x67\x69\x6E\x65\x20\x51\x75\x65\x72\x79\x00"
    },
    "28015": {
        "Source Engine": b"\xFF\xFF\xFF\xFF\x54\x53\x6F\x75\x72\x63\x65\x20\x45\x6E\x67\x69\x6E\x65\x20\x51\x75\x65\x72\x79\x00"
    },
    "4500": {
        "IPSec": b"\x48\x8B\x14\x72\x93\x5D\x70\x21"
    },
    "554": {
        "RTSP": b"\x44\x45\x53\x43\x52\x49\x42\x45\x20\x2F\x20\x52\x54\x53\x50\x2F\x31\x2E\x30\x0D\x0A\x0D\x0A"
    }
}

