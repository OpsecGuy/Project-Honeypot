import logging
import psycopg2


class DatabaseController:
    def __init__(self, host: str, database: str, login: str, password: str, server: str):
        self.host = host
        self.database = database
        self.login = login
        self.password = password
        self.server = server
        self.conn = self.connect_to_database()
        self.cur = self.conn.cursor()

    def connect_to_database(self):
        conn = psycopg2.connect(
            host=self.host,
            database=self.database,
            user=self.login,
            password=self.password
        )
        conn.autocommit = False
        return conn

    def add_new_payload(self, ipaddr: str, port: str, protocol: str, payload: bytes, creation_date: str, protocol_type: str, is_botnet: int, ip_country: str|None, ip_asn: str|None, ip_organization: str|None, ip_isp: str|None):
        sql_query = "INSERT INTO data (id, ipaddr, port, protocol, payload, server, creation_date, protocol_type, is_botnet, ip_country, ip_asn, ip_organization, ip_isp) VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM data), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data = (ipaddr, port, protocol, payload, self.server, creation_date, protocol_type, is_botnet, ip_country, ip_asn, ip_organization, ip_isp,)
        try:
            self.cur.execute(sql_query, data)
        except Exception as err:
            logging.warning(f"An error has occured while adding new data: {err}\nResetting db connection")
            self.conn = self.connect_to_database()
            self.cur = self.conn.cursor()
            self.cur.execute(sql_query, data)
        finally:
            if self.conn:
                self.conn.commit()

    def add_payload_stats(self, name: str, port: str, protocol_type: str):
        sql_query = "UPDATE protocols SET count = count + 1 WHERE name = %s AND port = %s AND protocol_type = %s"
        sql_query2 = "INSERT INTO protocols (id, name, count, port, protocol_type) VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM protocols), %s, 1, %s, %s)"
        try:
            self.cur.execute(sql_query, (name, port, protocol_type,))
            if self.cur.rowcount == 0:
                self.cur.execute(sql_query2, (name, port, protocol_type,))
        except Exception as err:
            logging.warning(f"An error has occured while updating stats: {err}\nResetting db connection")
            self.conn = self.connect_to_database()
            self.cur = self.conn.cursor()
            self.cur.execute(sql_query, (name, port, protocol_type,))
            if self.cur.rowcount == 0:
                self.cur.execute(sql_query2, (name, port, protocol_type,))
        finally:
            if self.conn:
                self.conn.commit()

    def close_connection(self):
        self.cur.close()
        self.conn.close()

