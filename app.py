from database import DatabaseController
from helper import *


cfg = Config()
logging.basicConfig(filename="application.log",
                    level=logging.DEBUG if cfg.options["verbose"] == 1 else logging.INFO,
                    format="%(asctime)s - %(message)s")


class UDPServer(asyncio.DatagramProtocol):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.protocol_type = "UDP"
        self.transport = None
        self.last_five_packets = deque(maxlen=10)

    def connection_made(self, transport):
        self.transport = transport
        # print(f"UDP server is ready and listening on port {self.port}")

    def datagram_received(self, data, addr):
        data = data.hex()

        if data in self.last_five_packets:
            return
        self.last_five_packets.append(data)
        protocol = find_protocol_by_data(data)
        print(f"[UDP] [{self.port}] Received data from {addr}: {data} | Protocol: {protocol}")

        ip_data = get_ip_address_details(addr[0])
        try:
            db.add_payload_stats(protocol, self.port, self.protocol_type)
            db.add_new_payload(addr[0], self.port, protocol, data, datetime.now().timestamp(), self.protocol_type, True if protocol == "POTENTIAL BOTNETS" else False, ip_data["location"], ip_data["asn"], ip_data["organization"], ip_data["isp"])
        except Exception as err:
            logging.warning(f"Failed to log data. Reason: {err}")

    def error_received(self, exc):
        logging.error(f"Error on port {self.port} due to: {exc}")

    def connection_lost(self, exc):
        logging.warning(f"Connection closed on port {self.port} due to: {exc}")


async def start_udp_server(port):
    loop = asyncio.get_running_loop()
    protocol = UDPServer(port)
    transport, _ = await loop.create_datagram_endpoint(
        lambda: protocol,
        local_addr=(cfg.options["ip_addr"], port))
    return transport, protocol


class TCPServer(asyncio.Protocol):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.protocol_type = "TCP"
        self.transport = None
        self.last_five_packets = deque(maxlen=10)

    def connection_made(self, transport):
        self.transport = transport
        self.peername = transport.get_extra_info('peername')
        # print(f"TCP server is ready and listening on port {self.port}")

    def data_received(self, data: bytes):
        data = data.hex()

        if data in self.last_five_packets:
            return
        self.last_five_packets.append(data)
        protocol = find_protocol_by_data(data)
        print(f"[TCP] [{self.port}] Received data from {self.peername}: {data} | Protocol: {protocol}")

        ip_data = get_ip_address_details(self.peername[0])
        try:
            db.add_payload_stats(protocol, self.port, self.protocol_type)
            db.add_new_payload(self.peername[0], self.port, protocol, data, datetime.now().timestamp(), self.protocol_type, True if protocol == "POTENTIAL BOTNETS" else False, ip_data["location"], ip_data["asn"], ip_data["organization"], ip_data["isp"])
        except Exception as err:
            logging.warning(f"Failed to log data. Reason: {err}")

    def connection_lost(self, exc):
        if exc:
            logging.warning(
                f"Connection closed on port {self.port} due to: {exc}")
        else:
            logging.warning(f"Connection closed on port {self.port}")


async def start_tcp_server(port):
    loop = asyncio.get_running_loop()
    server = await loop.create_server(lambda: TCPServer(port), cfg.options["ip_addr"], port)
    async with server:
        await server.serve_forever()


async def main():
    udp_transports = []
    udp_protocols = []
    tcp_tasks = []
    for port in range(cfg.options["start_port"], cfg.options["end_port"] + 1):

        if cfg.options["udp_mode"]:
            try:
                transport, protocol = await start_udp_server(port)
                udp_transports.append(transport)
                udp_protocols.append(protocol)
            except Exception as err:
                logging.warning(f"[UDP] Failed to start listener on port {port}. Reason: {err}")

        if cfg.options["tcp_mode"]:
            try:
                task = asyncio.create_task(start_tcp_server(port))
                tcp_tasks.append(task)
            except Exception as err:
                logging.warning(f"[TCP] Failed to start listener on port {port}. Reason: {err}")

    if cfg.options["tcp_mode"]:
        asyncio.gather(*tcp_tasks)
    
    print(f"Honepot started on ports {cfg.options['start_port']} to {cfg.options['end_port']}...")
    await asyncio.sleep(float('inf'))


if __name__ == "__main__":
    if cfg.options["tcp_mode"] and cfg.options["udp_mode"]:
        print("Unfortunately running UDP and TCP honeypots at once is not supported yet!")
        os._exit(1)
    elif not cfg.options["tcp_mode"] and not cfg.options["udp_mode"]:
        print("No mode selected! Make sure to enable \"tcp_mode\" or \"udp_mode\" in config!")
        os._exit(2)

    logging.info(f"-=- HoneyPot v{VERSION} is starting -=-")
    try:
        db = DatabaseController(cfg.options["db_ip"], cfg.options["db_name"], cfg.options["db_user"], cfg.options["db_pwd"], cfg.options["ip_addr"])
        logging.info(f"Connected to database {cfg.options['db_name']} as {cfg.options['db_user']}")
    except Exception as err:
        logging.error(f"Failed to establish database connection! Reason: {err}")
        os._exit(3)
    
    logging.info(f"{cfg.options['ip_addr']} is listening on ports {cfg.options['start_port']}:{cfg.options['end_port']}")
    asyncio.run(main())


