from ldap3 import Server, Connection, ALL

ad_server = 'win-l9up83kacsi.ornek.local'
ad_port = 389

ad_username = 'cn=Administrator,cn=Users,dc=ornek,dc=local'
ad_password = '123456A.'

base_dn = 'cn=Users,dc=ornek,dc=local'

server = Server(ad_server, port=ad_port, get_info=ALL)
conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)

search_filter = '(objectClass=user)'

conn.search(base_dn, search_filter)
for entry in conn.entries:
    print(f"DN: {entry.entry_dn}")

conn.unbind()





def addLDAP():
        ldap_server = 'localhost'
        ldap_port = 389

        admin_username = 'cn=admin,dc=alidap,dc=com'
        admin_password = '123456'
        
        user_dn = 'cn=yasin+sn=yasin,dc=alidap,dc=com'
        #user_attributes = {
         #   'objectClass' : ['user','person','top','organizationalPerson'],
            
          #  'objectClass' : 'organizationalPerson',
           # 'cn' :'Yasin',
            #'sn' : 'Elma',
            
            #}
        
        server = Server(ldap_server, port=ldap_port)
        conn = Connection(server, user=admin_username, password=admin_password)

        if not conn.bind():
            print(f" Failed to bind to LDAP server: {conn.result}")
        else:
            result = conn.add(user_dn, ['person'], { 'cn':'yasin'})
        if result:
            print("Users added successfully. ")
        else:
            print(f"Failed to add user: {conn.result}")

class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email
        self.objectClass = ['top', 'person', 'inetOrgPerson']


addLDAP()
