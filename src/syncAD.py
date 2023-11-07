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

ldap_existing_groups = []
spec_search = False
input_dn = ""
group_name = ""


def search_lines(filename_ad, total_lines_ad, input_dn):
    user_counter,new_user_counter = 0,0
    group_match = True

    global spec_search
    global group_name

    server = Server(ldap_server, port=ldap_port)
    conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
    dn,cn,sn,givenName,email,phoneNumber,homePostalAddress,sAMAccountName,memberOf = " " , " ", " ", " ", " ", " ", " ", " ", []
    with open(filename_ad, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if line.startswith('#') or line.startswith(' '):
                if dn != " " and sAMAccountName != " " and cn != " " :
                    if input_dn and spec_search:
                        search_result = conn.search(dn, '(objectClass=person)')
                        if search_result:                           
                            modification_dict = {}
                            attributes_to_compare = {
                            'givenName': givenName,
                            'sn': sn,
                            'telephoneNumber': phoneNumber,
                            'mail': mail,
                            'homePostalAddress':homePostalAddress,
                            }
                            for attribute_name, expected_value in attributes_to_compare.items():
                                comparison = conn.compare(dn, attribute_name, expected_value)
                                if comparison is False:
                                    modification_dict[attribute_name] = [(MODIFY_REPLACE, expected_value)]
                                else:
                                    pass        
                            if modification_dict:
                                try:
                                    conn.modify(dn, modification_dict)
                                    print(f"Successfully modified the LDAP entry: {cn}")
                                except Exception as e:
                                    print(f"Failed to modify the LDAP entry: {e}")
                            else:
                                print("No attribute modifications to perform for ",cn)
                            
                            for group in memberOf:
                                group_dn = f"cn={group},{ldap_user_group_dn}"
                                result = conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})
                                print(f"Successfully modified membership of the LDAP entry: {cn}")
                            search_filter_groups = f"(&(objectClass=groupOfNames)(member={dn}))"
                            user_membership = conn.search(ldap_user_group_dn, search_filter=search_filter_groups)
                            if user_membership:
                                for group in ldap_existing_groups:
                                    group_dn = f"cn={group},{ldap_user_group_dn}"
                                    group_existing = conn.compare(group_dn, "member", dn)
                                    if group_existing:
                                        if group not in memberOf:
                                            print(f"Successfully modified membership of the LDAP entry: {cn}")
                                            group_changes = {
                                                    'member': [(MODIFY_DELETE, [dn])]
                                                    }
                                            result = conn.modify(group_dn, changes=group_changes)
                        else:
                            print("user is not existing on ldap")
                            break
                    elif not input_dn:
                        search_result = conn.search(dn, '(objectClass=person)')
                        if search_result:
                            user_counter = user_counter + 1
                            modification_dict = {}
                            attributes_to_compare = {
                            'givenName': givenName,
                            'sn': sn,
                            'telephoneNumber': phoneNumber,
                            'mail': mail,
                            'homePostalAddress':homePostalAddress,
                            }

                            for attribute_name, expected_value in attributes_to_compare.items():
                                comparison = conn.compare(dn, attribute_name, expected_value)
                                if comparison is False:
                                    modification_dict[attribute_name] = [(MODIFY_REPLACE, expected_value)]
                            if modification_dict:
                                try:
                                    conn.modify(dn, modification_dict)

                                except Exception as e:
                                    print(f"Failed to modify the LDAP entry: {e}")

                            for group in memberOf:
                                group_dn = f"cn={group},{ldap_user_group_dn}"
                                result = conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})

                            search_filter_group = f"(&(objectClass=groupOfNames)(member={dn}))"
                            user_membership = conn.search(ldap_user_group_dn, search_filter=search_filter_group)
                            if user_membership:
                                for group in ldap_existing_groups:
                                    group_dn = f"cn={group},{ldap_user_group_dn}"
                                    group_existing = conn.compare(group_dn, "member", dn)
                                    if group_existing:
                                        if group not in memberOf:
                                            group_changes = {
                                                    'member': [(MODIFY_DELETE, [dn])]
                                                    }
                                            result = conn.modify(group_dn, changes=group_changes)
                                    else:
                                        pass
                        else:
                            if conn.search(f'{group_name},{ldap_group_dn}', '(objectClass=*)'):
                                filter_str = f'(uid={sAMAccountName})'
                                exist_uid = conn.search(search_base=ldap_base_dn, search_filter=filter_str, search_scope=SUBTREE, attributes=['cn'])
                                if exist_uid:
                                    entry = conn.entries[0]
                                    conn.delete(entry.entry_dn)
                                object_class = ['inetOrgPerson','organizationalPerson','top','person']
                                new_attributes = {
                                'objectClass': object_class,
                                'cn': cn,
                                'givenName': givenName,
                                'sn': sn,
                                'uid': sAMAccountName,
                                'mail': mail,
                                'homePostalAddress': homePostalAddress,
                                'telephoneNumber': phoneNumber,
                                }
                                result = conn.add(dn, attributes=new_attributes)
                                if not result:
                                    print(f"Failed to add user: {conn.result}")
                                else:
                                    new_user_counter = new_user_counter + 1
                            elif sync_group_mode:
                                groups_dn = ldap_group_dn 
                                for directory in reversed(org_unit_list):
                                    group_str = f"{directory},{groups_dn}"
                                    groups_dn = group_str
                                    groups_attributes = {
                                            'objectClass': ['top', 'organizationalUnit'],
                                            'description': directory,
                                            }
                                    result = conn.add(group_str, attributes=groups_attributes)
                                new_user_counter = new_user_counter + 1
                                object_class = ['inetOrgPerson','organizationalPerson','top','person']
                                new_attributes = {
                                'objectClass': object_class,
                                'cn': cn,
                                'givenName': givenName,
                                'sn': sn,
                                'uid': sAMAccountName,
                                'mail': mail,
                                'homePostalAddress': homePostalAddress,
                                'telephoneNumber': phoneNumber,
                                }
                                result = conn.add(dn, attributes=new_attributes)
                                for group in memberOf:
                                    group_dn = f"cn={group},{ldap_user_group_dn}"
                                    conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})
                    dn,cn,sn,givenName,email,homePostalAddress,phoneNumber,sAMAccountName,memberOf = " ", " ", " ", " ", " ", " ", " ", " ", []

                elif input_dn and total_lines_ad == line_number:
                    print(f"User is not found !!")
                elif total_lines_ad == line_number:
                    print ("Number of users : ",user_counter)
                    print ("Number of new users : ",new_user_counter)

            elif line.startswith('dn') and not spec_search :
                dn = line.strip()
                str_dn = dn.split(':',1)[1].strip()
                components = str_dn.split(',')
                formatted_components = []
                org_unit_list = []
                cn_counter = 0
                for component in components:
                    component = component.strip()
                    if component.startswith('CN='):
                        cn_counter = cn_counter + 1
                        if cn_counter >= 2 :
                            formatted_components.append('ou=' + component[3:])
                            group_name = ('ou=' + component[3:] + ',ou=Groups')
                            if component[3:] not in org_unit_list:
                                org_unit_list.append('ou=' + component[3:])
                        else:
                            formatted_components.append('cn=' + component[3:])
                    elif component.startswith('OU='):
                        formatted_components.append('ou=' + component[3:])

                group_name = ','.join(org_unit_list)
                new_dn = ','.join(formatted_components)
                dn = (new_dn+","+ldap_base_dn)
                 
                if  input_dn == dn:
                    spec_search = True
                    dn = input_dn
            elif line.startswith('cn'):
                cn = line.strip()
                cn = content(cn)
            elif line.startswith('sn'):
                sn = line.strip()
                sn = content(sn)
            elif line.startswith('givenName'):
                givenName = line.strip()
                givenName = content(givenName)
            elif line.startswith('sAMAccountName'):
                sAMAccountName = line.strip()
                sAMAccountName = content(sAMAccountName)
            elif line.startswith('mail'):
                mail = line.strip()
                mail = content(mail)
            elif line.startswith('homePostalAddress'):
                homePostalAddress = line.strip()
                homePostalAddress = content(homePostalAddress)
            elif line.startswith('telephoneNumber'):
                phoneNumber = line.strip()
                phoneNumber = content(phoneNumber)
            elif line.startswith('memberOf'):
                group = line.strip()
                components = group.split(",")
                group = components[0].split('=')[1]
                if group == "Administrators":
                    group = "adminGroups"
                elif group == "Domain Admins":
                    group = "domainAdminGroup"
                else:
                    group = ""
                
                if group:
                    memberOf.append(group)

            progress = (line_number + 1) / total_lines_ad * 100
            print(f"Progress: {progress:.0f}%", end='', flush=True)
            backspaces = len(f"Progress ({progress:.0f}%)")
            print('\b' * backspaces, end='', flush=True)
        print()
    conn.unbind()


def getLdapGroups():
    server = Server(ldap_server, port=ldap_port)
    conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)

    search_filter = "(objectClass=groupOfNames)"
    result = conn.search(ldap_user_group_dn,search_filter,attributes=["cn"])
    for entry in conn.entries:
        ldap_existing_groups.append(entry.cn)

    conn.unbind()

def content(content):
    converted = content.split(": ")
    content = converted[1]
    return content


start_time = time.time()
command_ad = f'ldapsearch -x -D {ad_username} -w {ad_password} -H ldap://{ad_server}:{ad_port} -b {ad_base_dn} "(&(objectClass=person)(objectCategory=person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )" -s sub -E pr=1000/noprompt  cn sn telephoneNumber mail homePostalAddress givenName sAMAccountName memberOf > ad_users.ldif'
print("Fetching - Active Directory Users...")
result_ad = subprocess.run(command_ad, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Check the result
if result_ad.returncode == 0:
    print("Successfully fetched.")
    total_lines_ad = int(subprocess.check_output(["wc", "-l", "ad_users.ldif"]).split()[0])
else:
    print("Failed with the following error:")
    print(result_ad.stderr)


file_path = 'ad_users.ldif'
print("Synchronization is in progress...")
getLdapGroups()
if argc == 1:
    search_lines(file_path, total_lines_ad, input_dn)
else:
    input_dn = sys.argv[1]
    print("mode : the single user search")
    search_lines(file_path, total_lines_ad, input_dn)

elapsed_time = time.time() - start_time 
print( """
___________________________________
                
    Elapsed time is {:.2f} minutes 
___________________________________  
                            """.format(elapsed_time/60))
