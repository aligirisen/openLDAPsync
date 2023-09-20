from ldap3 import *
import os, re, ldif
from io import StringIO


#ACTIVE DIRECTORY CONNECTION BLOCK
ad_server = 'win-l9up83kacsi.ornek.local'
ad_port = 389
ad_username = 'cn=Administrator,cn=Users,dc=ornek,dc=local'
ad_password = '123456A.'
base_dn = 'cn=Users,dc=ornek,dc=local'

server_ad = Server(ad_server, port=ad_port, get_info=ALL)
conn_ad = Connection(server_ad, user=ad_username, password=ad_password, auto_bind=True)
search_filter_ad = '(&(objectClass=Person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )'
entry_generator_ad = conn_ad.extend.standard.paged_search(search_base = base_dn, search_filter = search_filter_ad,search_scope=SUBTREE, attributes = ['cn', 'sn','sAMAccountName', 'telephoneNumber', 'mail','objectClass'])


#OPENLDAP CONNECTION BLOCK
ldap_server = 'localhost'
ldap_port = 389
ldap_admin_username = 'cn=admin,dc=alidap,dc=com'
ldap_admin_password = '123456'
ldap_base_dn = 'ou=Users,dc=alidap,dc=com'

server_ldap = Server(ldap_server, port=ldap_port)
conn_ldap = Connection(server_ldap, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
search_filter_ldap = '(objectClass=Person)'
entry_generator_ldap = conn_ldap.extend.standard.paged_search(search_base = ldap_base_dn, search_filter = search_filter_ldap,search_scope=SUBTREE, attributes = ['cn', 'sn', 'telephoneNumber','mail','objectClass','uid'])



class User:
    def __init__(self, name='', surname='',samaccountname='', phone_number='', mail=None, object_class=None):
        self.name = name
        self.surname = surname if surname !=[] else " "
        self.phone_number = phone_number if phone_number !=[] else " "
        self.mail = mail if mail != [] else " "
        self.samaccountname = samaccountname
        self.object_class = object_class

    def toString(self):
       return f"cn={user_cn}+sn={user_sn},phoneNumber={phone_number},mail={mail},ou=Users,dc=alidap,dc=com"

def addLDAP(user):# convert objectGUID to uid activedirectory to openldap
    user_dn = f"cn={user.name}+sn={user.surname},ou=Users,dc=alidap,dc=com"
    new_attributes = {
            'objectClass': user.object_class,
            'ou': 'Users',
            'cn': user.name,
            'sn': user.surname,
            'uid': user.samaccountname,
            'mail': user.mail,
            'telephoneNumber': user.phone_number,
            }
    server = Server(ldap_server, port=ldap_port)
    conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password)
    if not conn.bind():
        print(f" Failed to bind to LDAP server: {conn.result}")
    else:
        result = conn.add(user_dn, attributes=new_attributes)
    if result:
        print(f"{user_dn.split()[0]} added successfully. ")
    else:
        print(f"Failed to add user: {conn.result}")
    conn.unbind()
    createLDIF(user)


def createLDIF(user):

    user_dn = f"cn={user.name}+sn={user.surname},ou=Users,dc=alidap,dc=com"

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
""" 

    ldif_filename = f"{user.samaccountname}.ldif"
    ldif_directory = "ldif"
    if not os.path.exists(ldif_directory):
        os.makedirs(ldif_directory)
    ldif_path = os.path.join(ldif_directory, ldif_filename)
    with open(ldif_path, "w") as ldif_file:
        ldif_file.write(ldif_content)


def getLDAPdns():# Ldap tarafındaki userların dn'lerini ceker
    ldap_dn_list = []
    for entry in entry_generator_ldap:
        ldap_dn_list.append(entry['dn'])
    return ldap_dn_list

def getLDAPAttributes(original_dn):
    entry_generator_ldap = conn_ldap.extend.standard.paged_search(search_base = ldap_base_dn, search_filter = search_filter_ldap,search_scope=SUBTREE, attributes = ['cn', 'sn', 'telephoneNumber','mail','objectClass','uid'])
    for entry in entry_generator_ldap:
        if entry['dn'] == original_dn:
            return entry['attributes']


def updateLDAP(user_attributes, user_ldap, user):
    user_dn = f"cn={user.name}+sn={user.surname},ou=Users,dc=alidap,dc=com"
    #print("old one: ",user_attributes['mail'])
    #print("new one: ",user_ldap['mail'])

    server = Server(ldap_server, port=ldap_port)
    conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password)
 
    if conn.bind():
        modification_dict = {}
        for key, value in user_attributes.items():
            if key in user_ldap and key != "objectClass" and key != "uid": 
                if value:
                    if value[0] != user_ldap[key]:
                        if key == "sn":
                            addLDAP(user)
                        elif value == [' '] and user_ldap[key] == []:
                            pass
                        else:
                            modification_dict[key] = [(MODIFY_REPLACE, user_ldap[key])]
                            createLDIF(user)
                elif value == []:
                    if user_ldap[key] != []:
                        modification_dict[key] = [(MODIFY_REPLACE, user_ldap[key])]
                        createLDIF(user)
        if modification_dict:
            try:
                conn.modify(user_dn, modification_dict)
                print(f"Successfully modified the LDAP entry: {user_dn.split()[0]}")
            except Exception as e:
                print(f"Failed to modify the LDAP entry: {e}")
        else:
            print("No modifications to perform. for",user_attributes['cn'][0])

        conn.unbind()
    else:
        print(f"Failed to bind to the LDAP server: {conn.result}")


def normalize_ldap_dn(ad_dn, ldap_dn): # DN equalizer
    
    original_ldap_dn = ldap_dn
    original_ad_dn = ad_dn

    rdn_parts_ad = ad_dn.split(',')
    rdn_parts_ldap = ldap_dn.split(',')

    normalized_rdns_ad = []
    normalized_rdns_ldap = []

    for rdn in rdn_parts_ad:
        rdn = rdn.strip()
        if rdn.lower().startswith("ou="):
            rdn = "cn" + rdn[2:]
        if "+sn=" in rdn.lower():
            rdn = rdn.split("+sn=")[0]
        normalized_rdns_ad.append(rdn.lower())

    filtered_rdns_ad = list(filter(lambda rdn: not rdn.startswith("dc="), normalized_rdns_ad))
    filtered_rdns_ad.sort()
    filtered_dn_ad = ','.join(filtered_rdns_ad)

    for rdn in rdn_parts_ldap:
        rdn = rdn.strip()
        if rdn.lower().startswith("ou="):
            rdn = "cn" + rdn[2:]
        if "+sn=" in rdn.lower():
            rdn = rdn.split("+sn=")[0]
        normalized_rdns_ldap.append(rdn.lower())

    filtered_rdns_ldap = list(filter(lambda rdn: not rdn.startswith("dc="), normalized_rdns_ldap))
    filtered_rdns_ldap.sort()
    filtered_dn_ldap = ','.join(filtered_rdns_ldap)


    if (filtered_dn_ad == filtered_dn_ldap):
        return original_ldap_dn
    else:
        return False

object_class = []
uuid_list = []
ldap_dn_list = []
ldap_dn_list = getLDAPdns()

for entry in entry_generator_ad:

        
    object_class += entry['attributes']['objectClass']
    user_cn = entry['attributes']['cn']
    user_sn = entry['attributes']['sn']
    phone_number = entry['attributes']['telephoneNumber']
    mail = entry['attributes']['mail']
    samaccountname = entry['attributes']['sAMAccountName']
    user = User(name=user_cn, surname=user_sn, samaccountname = samaccountname, phone_number=phone_number, mail=mail, object_class=object_class)
    object_class.remove('user')#ldap doesn't has a user object class
    object_class.append('inetOrgPerson')# it is mandatory to use adding uid attribute
    new_attributes = entry['attributes']
    flag = False

    if ldap_dn_list:
        for ldap_dn in ldap_dn_list:
            existing_dn= normalize_ldap_dn(entry['dn'],ldap_dn)
            if existing_dn  == ldap_dn:
                old_attributes = getLDAPAttributes(ldap_dn)
                updateLDAP(old_attributes, new_attributes,user)
                flag = True
    if not flag:
        addLDAP(user)

    object_class = []
conn_ad.unbind()
conn_ldap.unbind()   
