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


def addLDAP(user_cn, user_sn, object_class):

        if 'user' in object_class:
            object_class.remove('user')




        
        user_dn = "cn="+user_cn+"+sn="+user_sn+",ou=Users,dc=alidap,dc=com"    
        new_attributes = {
                'objectClass': object_class,
                'ou': 'Users',
                'cn': user_cn,
                'sn': user_sn
                }


        server = Server(ldap_server, port=ldap_port)
        conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password)

        if not conn.bind():
            print(f" Failed to bind to LDAP server: {conn.result}")
        else:
            result = conn.add(user_dn, attributes=new_attributes)
        if result:
            print("Users added successfully. ")
        else:
            print(f"Failed to add user: {conn.result}")




server = Server(ad_server, port=ad_port, get_info=ALL)
conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)

search_filter = '(&(objectClass=Person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )'


conn.search(base_dn, search_filter)


obj_inetorgperson = ObjectDef('Person',conn)
r = Reader(conn, obj_inetorgperson, base_dn, search_filter)
r.search()
#entry1 = r[0].entry_to_ldif()
#print(r.entries[5].memberOf[1])


object_class = []
for i in range(len(r.entries)):
    if (r.entries[i].cn.value is not None):
        object_class += r.entries[i].objectClass
        user_cn = r.entries[i].cn.value.split()[0]
        user_sn = r.entries[i].sn.value
        addLDAP(user_cn, user_sn, object_class)
        object_class = []
        #conn.add()  add user
        for j in range(len(r.entries[i].memberOf)):
            print(r.entries[i].memberOf[j])
            
            
            #conn.add() add group

    else:
        print("Isimsiz obje atlandi...")


conn.unbind()

