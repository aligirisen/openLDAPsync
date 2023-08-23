from ldap3 import *

ad_server = 'win-l9up83kacsi.ornek.local'
ad_port = 389

ad_username = 'cn=Administrator,cn=Users,dc=ornek,dc=local'
ad_password = '123456A.'

base_dn = 'cn=Users,dc=ornek,dc=local'

server = Server(ad_server, port=ad_port, get_info=ALL)
conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)

search_filter = '(&(objectClass=Person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )'



conn.search(base_dn, search_filter)


obj_inetorgperson = ObjectDef('Person',conn)
r = Reader(conn, obj_inetorgperson, base_dn, search_filter)
r.search()
#entry = r.entries[0].entry_to_ldif()

#print(r.entries[5].memberOf[1])


for i in range(len(r.entries)):
    if (r.entries[i].cn.value is not None):
        print(r.entries[i].cn.value)
        #conn.add()  add user
        for j in range(len(r.entries[i].memberOf)):
            print(r.entries[i].memberOf[j])
            #conn.add() add group

    else:
        print("Null deger atlandi...")


conn.unbind()




def addLDAP():
        ldap_server = 'localhost'
        ldap_port = 389

        admin_username = 'cn=admin,dc=alidap,dc=com'
        admin_password = '123456'
        
        user_dn = 'cn=ali+sn=utku,dc=alidap,dc=com'
        user_attributes = {
            'objectClass' : ['person'],
            'cn' :'Ali',
            'sn' : 'Utku'
            
            }
        
        server = Server(ldap_server, port=ldap_port)
        conn = Connection(server, user=admin_username, password=admin_password)

        if not conn.bind():
            print(f" Failed to bind to LDAP server: {conn.result}")
        else:
            result = conn.add(user_dn, attributes=user_attributes)
        if result:
            print("Users added successfully. ")
        else:
            print(f"Failed to add user: {conn.result}")
#addLDAP()
