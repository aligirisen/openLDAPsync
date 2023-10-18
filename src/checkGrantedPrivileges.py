from ldap3 import *
import os, re
from io import StringIO


ldap_server = 'localhost'
ldap_port = 389
ldap_admin_username = 'cn=Recep Yilmaz+sn=Yilmaz,ou=Users,ou=Groups,dc=alidap,dc=com'
ldap_admin_password = '112233'
#ldap_admin_password = '123123'
#ldap_admin_username = 'cn=Osman Gultekin+sn=Gultekin,ou=Users,ou=Groups,dc=alidap,dc=com'
ldap_base_dn = 'ou=Users,ou=Groups,dc=alidap,dc=com'

server_ldap = Server(ldap_server, port=ldap_port)
conn_ldap = Connection(server_ldap, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)


with Connection(Server(ldap_server), user=ldap_admin_username, password=ldap_admin_password) as conn:
    user_dn = 'cn=Oktay Emre+sn=Emre,ou=Users,ou=Groups,dc=alidap,dc=com'
    entry_changes = {
            'mail': [(MODIFY_REPLACE, ['aaaa@gmailcom'])]
            }
    conn.modify(user_dn, entry_changes)
    if not conn.result['result']:
        print("Succeeded")
    else:
        print("Failed")
