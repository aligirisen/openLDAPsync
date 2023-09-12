from ldap3 import *
import os


#ACTIVE DIRECTORY CONNECTION BLOCK
ad_server = 'win-l9up83kacsi.ornek.local'
ad_port = 389
ad_username = 'cn=Administrator,cn=Users,dc=ornek,dc=local'
ad_password = '123456A.'
base_dn = 'cn=Users,dc=ornek,dc=local'

server_ad = Server(ad_server, port=ad_port, get_info=ALL)
conn_ad = Connection(server_ad, user=ad_username, password=ad_password, auto_bind=True)
search_filter_ad = '(&(objectClass=Person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )'
entry_generator_ad = conn_ad.extend.standard.paged_search(search_base = base_dn, search_filter = search_filter_ad,search_scope=SUBTREE, attributes = ['cn', 'sn','sAMAccountName', 'telephoneNumber', 'mail','objectGUID','objectClass'])


#OPENLDAP CONNECTION BLOCK
ldap_server = 'localhost'
ldap_port = 389
ldap_admin_username = 'cn=admin,dc=alidap,dc=com'
ldap_admin_password = '123456'
ldap_base_dn = 'ou=Users,dc=alidap,dc=com'

server_ldap = Server(ldap_server, port=ldap_port, get_info=ALL)
conn_ldap = Connection(server_ldap, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
search_filter_ldap = '(objectClass=Person)'
entry_generator_ldap = conn_ldap.extend.standard.paged_search(search_base = ldap_base_dn, search_filter = search_filter_ldap,search_scope=SUBTREE, attributes = ['cn', 'sn', 'telephoneNumber','entryUUID', 'mail','objectClass','uidnumber','description'])




class User: # active directory'de bos olan attribute'lar None olarak gelip, LDAP'a eklerken sorun cikartmasin diye empty string'e cevirildi
    def __init__(self, name='', surname='',samaccountname='', phone_number='', mail=None, object_guid='', object_class=None):
        self.name = name
        self.surname = surname if surname !=[] else " "
        self.phone_number = phone_number if phone_number !=[] else " "
        self.mail = mail if mail != [] else " "
        self.samaccountname = samaccountname
        self.object_guid = object_guid
        self.object_class = object_class

    def toString(self):
       return f"cn={user_cn}+sn={user_sn},phoneNumber={phone_number},mail={mail},object_guid={object_guid},ou=Users,dc=alidap,dc=com"

def addLDAP(user):# convert objectGUID to uid activedirectory to openldap
    user_dn = f"cn={user.name}+sn={user.surname},ou=Users,dc=alidap,dc=com"
    new_attributes = {
            'objectClass': user.object_class,
            'ou': 'Users',
            'cn': user.name,
            'sn': user.surname,
            'uid': user.samaccountname,
            'mail': user.mail,
            'description': user.object_guid,
            'telephoneNumber': user.phone_number,
            }
    if not conn_ad.bind():
        print(f" Failed to bind to LDAP server: {conn.result}")
    else:
        result = conn_ad.add(user_dn, attributes=new_attributes)
    if result:
        print("Users added successfully. ")
    else:
        print(f"Failed to add user: {conn.result}")
    ldif_content = f"""
dn: {user_dn}
changetype: add
objectClass: {user.object_class[0]}
objectClass: {user.object_class[1]}
objectClass: {user.object_class[2]}
objectClass: {user.object_class[3]}
ou: Users
uid: {user.samaccountname}
cn: {user.name}
sn: {user.surname}
mail: {user.mail}
telephoneNumber: {user.phone_number}
description: {user.object_guid}""" 

# description's type is string so we need it. Otherwise you can create and use CustomAttribute. But you cannot use entryUUID. cuz it is forbidden (default slapd schemas configurations)

    ldif_filename = f"{user.samaccountname}.ldif"
    ldif_directory = "ldif"
    if not os.path.exists(ldif_directory):
        os.makedirs(ldif_directory)
    ldif_path = os.path.join(ldif_directory, ldif_filename)
    with open(ldif_path, "w") as ldif_file:
        ldif_file.write(ldif_content)
    print(f"Created {ldif_filename} with the specified content.")


def getLDAPuuid(user):# Ldap tarafındaki userların 'description' değişkenine atanmış olan ve active directory'den gelen uuid'lerini çeker
    uuid_list = []
    for entry in entry_generator_ldap:
        uuid_list += entry['attributes']['description']
    return uuid_list


def updateLDAP(user):
    user_dn = f"cn={user.name}+sn={user.surname},ou=Users,dc=alidap,dc=com"
    
    conn.modify('cn=b.smith,ou=ldap3-tutorial,dc=demo1,dc=freeipa,dc=org', {'sn': [(MODIFY_DELETE, ['Johnson'])], 'givenname': [(MODIFY_REPLACE, ['Beatrix'])]} )#örnek modify



    conn_ldap.modify(user_dn)




object_class = []
uuid_list = []

for entry in entry_generator_ad:
        
    object_class += entry['attributes']['objectClass']
    user_cn = entry['attributes']['cn']
    user_sn = entry['attributes']['sn']
    phone_number = entry['attributes']['telephoneNumber']
    mail = entry['attributes']['mail']
    object_guid = entry['attributes']['objectGUID']
    samaccountname = entry['attributes']['sAMAccountName']
    user = User(name=user_cn, surname=user_sn, samaccountname = samaccountname, phone_number=phone_number, mail=mail, object_guid = object_guid, object_class=object_class)
    object_class.remove('user')#ldap doesn't has a user object class
    object_class.append('inetOrgPerson')# it is mandatory to use adding uid attribute
        
    flag = False
    uuid_list = getLDAPuuid(user)
    for uuid in uuid_list:
        if object_guid == uuid:
            updateLDAP(user)
            flag = True
            break
    if not flag:
        addLDAP(user)

    object_class = []
conn.unbind()        
