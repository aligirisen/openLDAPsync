from ldap3 import *
ad_server = 'localhost'
ad_port = 389

ad_username = 'cn=admin,dc=alidap,dc=com'
ad_password = '123456'

base_dn = 'ou=Users,dc=alidap,dc=com'

server = Server(ad_server, port=ad_port, get_info=ALL)
conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)
conn.search(base_dn,'(objectClass=person)')

obj_person = ObjectDef('Person',conn)
r = Reader(conn,obj_person, base_dn)
r.search()
print(r.entries[0].sn.value)
#print(conn.entries[0].entry_to_ldif())


conn.unbind()
