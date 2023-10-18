from ldap3 import *
import  os

ad_server = 'win-l9up83kacsi.ornek.local'
ad_port = 389
ad_username = 'cn=Administrator,cn=Users,dc=ornek,dc=local'
ad_password = '123456A.'
base_dn = 'cn=Users,dc=ornek,dc=local'


ldap_server = 'localhost'
ldap_port = 389
ldap_admin_username = 'cn=admin,dc=alidap,dc=com'
ldap_admin_password = '123456'
ldap_base_dn = 'ou=Users,dc=alidap,dc=com'


server_ldap = Server(ldap_server, port=ldap_port)
conn_ldap = Connection(server_ldap, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
search_filter_ldap = '(objectClass=Person)'


'''def createAdministrators():

    try:
        server = Server(ldap_server)
        conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password)

        if conn.bind():
            if not conn.search('ou=Administrators,ou=Groups,dc=alidap,dc=com', '(objectClass=*)'):
                groups_attributes = {
                    'objectClass': ['top', 'organizationalUnit'],
                }
                conn.add('ou=Administrators,ou=Groups,dc=alidap,dc=com', attributes=groups_attributes)
                print('Groups OU entry "ou=Administrators,ou=Groups,dc=alidap,dc=com" created successfully.')
            else:
                print('Groups OU entry "ou=Administrators,ou=Groups,dc=alidap,dc=com" already exists.')

            conn.unbind()
        else:
            print('Failed to bind to the LDAP server.')

    except Exception as e:
        print(f'An error occurred: {str(e)}')'''

def createAdministrators():
    group_dn = 'cn=Administrators,ou=Groups,dc=alidap,dc=com'
    group_attributes = {
            'objectClass': ['top', 'groupOfNames'],
            'cn': 'Administrators',
            'member': [
                'cn=Administrator,ou=Users,ou=Groups,dc=alidap,dc=com'
                ]
    }
    try:
        with Connection(Server(ldap_server), user=ldap_admin_username, password=ldap_admin_password, auto_bind=True) as conn:
            if not conn.search('cn=Administrators,ou=Groups,dc=alidap,dc=com', '(objectClass=*)'):
                conn.add(group_dn, attributes = group_attributes)
                print(f"Group {group_dn} added sucesfully.")
            else:
                print('Entry "cn=Administrators,ou=Groups,dc=alidap,dc=com" already exists.')

    except LDAPExceptionError as e:
        print(f"Error adding group: {e}")

def create_DnsAdmins():
    group_dn = 'cn=DnsAdmins,ou=Groups,dc=alidap,dc=com'
    group_attributes = {
            'objectClass': ['top', 'groupOfNames'],
            'cn': 'DnsAdmins',
            'member': [
                'cn=DnsAdmin,ou=Users,ou=Groups,dc=alidap,dc=com'
                ]
    }
    try:
        with Connection(Server(ldap_server), user=ldap_admin_username, password=ldap_admin_password, auto_bind=True) as conn:
            if not conn.search('cn=DnsAdmins,ou=Groups,dc=alidap,dc=com', '(objectClass=*)'):
                conn.add(group_dn, attributes = group_attributes)
                print(f"Group {group_dn} added sucesfully.")
            else:
                print('Entry "cn=DnsAdmins,ou=Groups,dc=alidap,dc=com" already exists.')

    except LDAPExceptionError as e:
        print(f"Error adding group: {e}")



def create_groups_entry():
    try:
        server = Server(ldap_server)
        conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password)
        if conn.bind():
            if not conn.search('ou=Groups,dc=alidap,dc=com', '(objectClass=*)'):
                groups_attributes = {
                    'objectClass': ['top', 'organizationalUnit'],
                }
                conn.add('ou=Groups,dc=alidap,dc=com', attributes=groups_attributes)
                print('Groups OU entry "ou=Groups,dc=alidap,dc=com" created successfully.')
            else:
                print('Groups OU entry "ou=Groups,dc=alidap,dc=com" already exists.')

            conn.unbind()
        else:
            print('Failed to bind to the LDAP server.')

    except Exception as e:
        print(f'An error occurred: {str(e)}')

def create_users_entry():
    try:
        server = Server(ldap_server)
        conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password)
        if conn.bind():
            if not conn.search('ou=Users,ou=Groups,dc=alidap,dc=com', '(objectClass=*)'):
                users_attributes = {
                    'objectClass': ['top', 'organizationalUnit'],
                }
                conn.add('ou=Users,ou=Groups,dc=alidap,dc=com', attributes=users_attributes)
                print('Users OU entry "ou=Users,ou=Groups,dc=alidap,dc=com" created successfully.')
            else:
                print('Users OU entry "ou=Users,ou=Groups,dc=alidap,dc=com" already exists.')

            # Unbind from the LDAP server
            conn.unbind()
        else:
            print('Failed to bind to the LDAP server.')

    except Exception as e:
        print(f'An error occurred: {str(e)}')


def createAclLDIF():
    groupName = "Administrators"

    ldif_content = f"""
dn: olcDatabase={{1}}mdb,cn=config
changetype: modify
add: olcAccess
olcAccess: {{0}}to * 
  by group/groupOfNames/member="ou={groupName},ou=Groups,dc=alidap,dc=com" write by * read
""" 

    ldif_filename = f"{groupName}_access.ldif"
    ldif_directory = "ldif_acl"
    if not os.path.exists(ldif_directory):
        os.makedirs(ldif_directory)
    ldif_path = os.path.join(ldif_directory, ldif_filename)
    with open(ldif_path, "w") as ldif_file:
        ldif_file.write(ldif_content)

createAclLDIF()
create_groups_entry()
create_users_entry()
createAdministrators()
create_DnsAdmins()
