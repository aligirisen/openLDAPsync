import subprocess, time, configparser, sys
from ldap3 import *

config = configparser.ConfigParser()
config.read('config.ini')

argc = len(sys.argv)

config_pref = configparser.ConfigParser()
config_pref.read('pref_config.ini')
sync_group_mode = config_pref.get('PREF','sync_group')

#ACTIVE DIRECTORY CONNECTION BLOCK
ad_server = config.get('AD','ad_server')
ad_port = int(config.get('AD','ad_port'))
ad_username = config.get('AD','ad_username')
ad_password = config.get('AD', 'ad_password')
ad_base_dn = config.get('AD','ad_base_dn')

#OPENLDAP CONNECTION BLOCK
ldap_server = config.get('LDAP','ldap_server')
ldap_port = int(config.get('LDAP','ldap_port'))
ldap_admin_username = config.get('LDAP','ldap_admin_username')
ldap_admin_password = config.get('LDAP','ldap_admin_password')
ldap_base_dn = config.get('LDAP','ldap_base_dn')
ldap_group_dn = config_pref.get('PREF','ldap_default_directory_dn')
ldap_user_group_dn = config_pref.get('PREF','ldap_user_group_dn')


counter = 0
def delet():
    global counter
    directory = f"ou=Users,{ldap_base_dn}"
    search_filter = '(objectClass=inetOrgPerson)'
    conn.search(directory,search_filter, SUBTREE)
    for entry in conn.entries:
        user_dn = entry.entry_dn
        if user_dn != "uid=AC287605,ou=Users,dc=lider,dc=com":
            if conn.delete(user_dn):
                counter = counter + 1
            else:
                print(f"failed : {user_dn}")
        else:
            print(user_dn)
    delet()



server = Server(ldap_server, ldap_port)
conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)


delet()
print(counter)
conn.unbind()
