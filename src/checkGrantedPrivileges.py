from ldap3 import *
import os, re
from io import StringIO


ldap_server = config.get('LDAP','ldap_server')
ldap_port = int(config.get('LDAP','ldap_port'))
ldap_admin_username = config.get('LDAP','ldap_admin_username')
ldap_admin_password = config.get('LDAP','ldap_admin_password')
ldap_group_dn = config.get('LDAP','ldap_group_dn')
ldap_users_dn = config.get('LDAP','ldap_users_dn')


server_ldap = Server(ldap_server, port=ldap_port)

conn_ldap = Connection(server_ldap, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)


with Connection(Server(ldap_server), user=ldap_admin_username, password=ldap_admin_password) as conn:
    user_dn = ''
    entry_changes = {
            'mail': [(MODIFY_REPLACE, ['lllkkkkkk@gmailcom'])]
            }
    conn.modify(user_dn, entry_changes)
    if not conn.result['result']:
        print("Succeeded")
    else:
        print("Failed")
