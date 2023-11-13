import subprocess, time, configparser, sys
from ldap3 import *

config = configparser.ConfigParser()
config.read('config.ini')

argc = len(sys.argv)

config_pref = configparser.ConfigParser()
config_pref.read('pref_config.ini')

#PREF
ldap_user_group_dn = config_pref.get('PREF','ldap_user_group_dn')
ldap_spec_directory = config_pref.get('PREF','ldap_spec_directory_dn')
ldap_default_users = config_pref.get('PREF','ldap_default_users_dn')

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


test_user_dn = 'cn=testtestconnections,' + ldap_base_dn
test_ou_dn = 'ou=testtestOrganizationalUnit,' + ldap_base_dn


def addUser(dn):
    object_class = ['inetOrgPerson','organizationalPerson','top','person']
    new_attributes = {
        'objectClass': object_class,
        'cn': dn,
        'uid': dn,
        'sn': dn,
        }
            
    result_add = conn.add(dn, attributes=new_attributes)
    return result_add

# default test 
server = Server(ldap_server, ldap_port)
conn = Connection(server,user=ldap_admin_username,password=ldap_admin_password,auto_bind=True)

if not conn.bind():
    print('Failed to bind to the LDAP server.')
else:
    print('Connected to the LDAP server successfully. Necessary privileges are checking up...')
    try:
        if not conn.search(test_ou_dn, '(objectClass=*)'):
            groups_attributes = {
                  'objectClass': ['top', 'organizationalUnit','pardusLider'],
            }
            result_ou = conn.add(test_ou_dn, attributes=groups_attributes)
            if result_ou:
                print("Passed -add organiztional unit-")
                ou_test = conn.delete(test_ou_dn)
                if ou_test:
                    print("Passed -delete organizational unit-")
                else:
                    print("Failed -delete organizational unit-")
            else:
                print("Failed -add organizational unit-")
        else:
            ou_test = conn.delete(test_ou_dn)
            if ou_test:
                print("Passed -delete organizational unit-")
                groups_attributes = {
                    'objectClass': ['top', 'organizationalUnit','pardusLider'],
                }

                result = conn.add(test_ou_dn, attributes=groups_attributes)
                if result:
                    conn.delete(test_ou_dn)
                    print("Passed -add organiztional unit-")
                else:
                    print("Failed -add organizational unit-")
            else:
                print("Failed -delete organizational unit-")

        result = conn.search(test_user_dn, '(objectClass=person)')
        if result:
            result_delete = conn.delete(test_user_dn)
            if result_delete:
                print("Passed -delete entry-")
                result_add = addUser(test_user_dn)
                if result_add:
                    print("Passed -add entry-")
                    conn.delete(test_user_dn)
                else:
                    print("Failed -add entry-")
            else:
                print("Failed -delete entry-")

        else:
            result_add = addUser(test_user_dn)
            if result_add:
                print("Passed -add entry-")
                result_delete = conn.delete(test_user_dn)
                if result_delete:
                    print("Passed -delete entry-")
                else:
                    print("Failed -delete entry-")
            else:
                print(test_user_dn)
                print("Failed -add entry-")
    except Exception as e:
        print(f'An error occurred: {str(e)}')
    finally:
        conn.unbind()


server_ad = Server(ad_server, ad_port)
conn_ad = Connection(server_ad,user=ad_username,password=ad_password,auto_bind=True)

if not conn_ad.bind():
    print('Failed to bind to the Active Directory.')
else:
    print('Connected to the Active Directory successfully.')
    try:
        search_filter = '(objectClass=person)'
        search_base = ad_base_dn
        search_result_ad = conn_ad.search(search_base, search_filter, SUBTREE)

        if search_result_ad:
            print("Passed -Active Directory-")
        else:
            print("Failed -Active Directory-")
    except Exception as e:
        print(f'An error occured: {str(e)}')
    finally:
        conn_ad.unbind()

# Create your tests here
