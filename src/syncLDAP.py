from ldap3 import Server, Connection, ALL

ad_server = 'localhost'
ad_port = 389

ad_username = 'cn=admin,dc=alidap,dc=com'
ad_password = '123456'

base_dn = 'dc=alidap,dc=com'

server = Server(ad_server, port=ad_port, get_info=ALL)
conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)
conn.search(base_dn,'(objectClass=person)')

for entry in conn.entries:
    print(f"DN: {entry.entry_dn}")
conn.unbind()
