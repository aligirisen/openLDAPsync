from ldap3 import *
ldap_server = 'localhost'
ldap_port = 389
ldap_admin_username = 'cn=admin,dc=alidap,dc=com'
ldap_admin_password = '123456'
ldap_base_dn = 'ou=Users,dc=alidap,dc=com'

ad_server = 'win-l9up83kacsi.ornek.local'
ad_port = 389
ad_username = 'cn=Administrator,cn=Users,dc=ornek,dc=local'
ad_password = '123456A.'
base_dn = 'cn=Users,dc=ornek,dc=local'


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
        
        if 'user' in user.object_class:
            object_class.remove('user')
            object_class.append('inetOrgPerson')
        user_dn = f"cn={user.name}+sn={user.surname},ou=Users,dc=alidap,dc=com"
        new_attributes = {
                'objectClass': user.object_class,
                'ou': 'Users',
                'cn': user.name,
                'sn': user.surname,
                'uid': user.samaccountname,
                'entryUUID': user.object_guid,
                'telephoneNumber': user.phone_number,
                }
        server = Server(ldap_server, port=ldap_port)
        conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password)
        if not conn.bind():
            print(f" Failed to bind to LDAP server: {conn.result}")
        else:
            print(user.toString())
            result = conn.add(user_dn, attributes=new_attributes)
        if result:
            print("Users added successfully. ")
        else:
            print(f"Failed to add user: {conn.result}")


server = Server(ad_server, port=ad_port, get_info=ALL)
conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)

search_filt = '(&(objectClass=Person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )'

entry_generator = conn.extend.standard.paged_search(search_base = base_dn, search_filter = search_filt,search_scope=SUBTREE, attributes = ['cn', 'sn','sAMAccountName', 'telephoneNumber', 'mail','objectGUID','objectClass'])
object_class = []

for entry in entry_generator:
    if (entry['attributes']['cn'] is not None):
        
        object_class += entry['attributes']['objectClass']
        user_cn = entry['attributes']['cn'].split()[0]# iki isimli olanlar konusunda bir sorun var ikinci ismi almıyor bu yöntem
        user_sn = entry['attributes']['sn']
        phone_number = entry['attributes']['telephoneNumber']
        mail = entry['attributes']['mail']
        object_guid = entry['attributes']['objectGUID']
        samaccountname = entry['attributes']['sAMAccountName']
        user = User(name=user_cn, surname=user_sn, samaccountname = samaccountname, phone_number=phone_number, mail=mail, object_guid = object_guid, object_class=object_class)
        addLDAP(user)
        object_class = []
    else:
        print("Isimsiz obje atlandi...")

conn.unbind()        
