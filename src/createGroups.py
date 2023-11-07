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
ldap_group_dn = config.get('LDAP','ldap_group_dn')
ldap_user_group_dn = config.get('LDAP','ldap_user_group_dn')


def createOuAdministrators():
    try:
        server = Server(ldap_server)
        conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password,auto_bind=True)

        if conn.bind():
            if not conn.search(f'ou=Administrators,{ldap_base_dn}', '(objectClass=*)'):
                groups_attributes = {
                    'objectClass': ['top', 'organizationalUnit','pardusLider'],
                }
                ou = 'ou=Administrators,dc=lider,dc=com'
                result = conn.add(ou, attributes=groups_attributes)
                print(result)
            else:
                print('Groups OU entry "ou=Administrators,ou=Groups,dc=alidap,dc=com" already exists.')

            conn.unbind()
        else:
            print('Failed to bind to the LDAP server.')

    except Exception as e:
        print(f'An error occurred: {str(e)}')

createOuAdministrators()
