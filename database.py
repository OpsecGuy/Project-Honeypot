import psycopg2


class DatabaseController:
    def __init__(self, host: str, database: str, login: str, password: str, server: str):
        self.server = server
        self.conn = self.connect_to_database(host, database, login, password)
        self.cur = self.conn.cursor()

    def connect_to_database(self, host, database, login, password):
        conn = psycopg2.connect(
            host=host,
            database=database,
            user=login,
            password=password
        )
        conn.autocommit = False
        return conn

    def add_new_payload(self, ipaddr: str, port: str, protocol: str, payload: bytes, creation_date: str, protocol_type: str, is_botnet: int, ip_country: str|None, ip_asn: str|None, ip_organization: str|None, ip_isp: str|None):
        sql_query = "INSERT INTO data (id, ipaddr, port, protocol, payload, server, creation_date, protocol_type, is_botnet, ip_country, ip_asn, ip_organization, ip_isp) VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM data), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        data = (ipaddr, port, protocol, payload, self.server, creation_date, protocol_type, is_botnet, ip_country, ip_asn, ip_organization, ip_isp,)
        self.cur.execute(sql_query, data)
        self.conn.commit()

    def add_payload_stats(self, name: str, port: str, protocol_type: str):
        sql_query = "UPDATE protocols SET count = count + 1 WHERE name = %s AND port = %s AND protocol_type = %s"
        self.cur.execute(sql_query, (name, port, protocol_type,))

        if self.cur.rowcount == 0:
            sql_query = "INSERT INTO protocols (id, name, count, port, protocol_type) VALUES ((SELECT COALESCE(MAX(id), 0) + 1 FROM protocols), %s, 1, %s, %s)"
            self.cur.execute(sql_query, (name, port, protocol_type,))
        self.conn.commit()

    def close_connection(self):
        self.cur.close()
        self.conn.close()

