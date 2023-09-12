from ldap3 import *
ad_server = 'localhost'
ad_port = 389

ad_username = 'cn=admin,dc=alidap,dc=com'
ad_password = '123456'

base_dn = 'ou=Users,dc=alidap,dc=com'

server = Server(ad_server, port=ad_port, get_info=ALL)
conn = Connection(server, user=ad_username, password=ad_password, auto_bind=True)


#search_filt = '(&(objectClass=Person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )'
search_filt = '(objectClass=Person)'

entry_generator = conn.extend.standard.paged_search(search_base = base_dn, search_filter = search_filt,search_scope=SUBTREE, attributes = ['cn', 'sn', 'telephoneNumber','entryUUID', 'mail','objectClass','uidnumber','description'])



for entry in entry_generator:
    print(entry['attributes']['description'])


conn.unbind()
