from database import DatabaseController
from helper import *


logging.basicConfig(filename="application.log", level=logging.INFO, format='%(asctime)s - %(message)s') # Set up logging
cfg = Config()


class UDPServerProtocol(asyncio.DatagramProtocol):
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
        orginal_data = data
        data = data.hex()
        if data in self.last_five_packets:
            # print("Duplicate packet found, skipping database entry.")
            return
        
        self.last_five_packets.append(data)
        print(f"[{self.port}] Received data from {addr}: {data}")

        try:
            protocol = find_protocol_by_data(data)
        except Exception as err:
            logging.warning(f"Protocol match failed due to: {err}")
            protocol = "Unknown"

        try:
            db.add_payload_stats(protocol, self.port, self.protocol_type)
            db.add_new_payload(addr[0], self.port, protocol, data, datetime.now().timestamp(), self.protocol_type, True if protocol == "POTENTIAL BOTNETS" else False)
        except Exception as err:
            logging.warning(f"Failed to log data. Reason: {err}")

    def error_received(self, exc):
        print(f"Error on port {self.port}: {exc}")

    def connection_lost(self, exc):
        # print(f"Connection closed on port {self.port}")
        # logging.info(f"Connection closed on port {self.port}")
        pass


async def start_udp_server(port):
    loop = asyncio.get_running_loop()
    protocol = UDPServerProtocol(port)
    transport, _ = await loop.create_datagram_endpoint(
        lambda: protocol,
        local_addr=(cfg.options["ip_addr"], port)
    )
    return transport, protocol


async def main():
    transports = []
    protocols = []
    try:
        # Create UDP server endpoints for each port in the range
        for port in range(cfg.options["start_port"], cfg.options["end_port"] + 1):
            try:
                transport, protocol = await start_udp_server(port)
                transports.append(transport)
                protocols.append(protocol)
            except Exception as err:
                print(f"Failed to start listener on port {port}")
                logging.warning(f"Failed to start listener on port {port}. Reason: {err}")

        print(f"UDP servers are running on ports {cfg.options['start_port']} to {cfg.options['end_port']}...")
        
        # Keep the servers running indefinitely
        await asyncio.sleep(float('inf'))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close all transports gracefully
        for transport in transports:
            transport.close()
        print("All UDP servers have been closed.")


if __name__ == "__main__":
    logging.info(f"-=- HoneyPot v{VERSION} is starting -=-")
    try:
        db = DatabaseController(cfg.options["db_ip"], cfg.options["db_name"], cfg.options["db_user"], cfg.options["db_pwd"], cfg.options["ip_addr"])
        logging.info(f"Connected to database {cfg.options['db_name']} as {cfg.options['db_user']}")
    except Exception as err:
        logging.error(f"Failed to establish database connection! Reason: {err}")
        os._exit(1)
    
    logging.info(f"{cfg.options['ip_addr']} is listening on ports {cfg.options['start_port']}:{cfg.options['end_port']}")
    asyncio.run(main())


