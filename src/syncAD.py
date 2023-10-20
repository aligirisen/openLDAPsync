import subprocess, time, configparser, sys
from ldap3 import *

config = configparser.ConfigParser()
config.read('config.ini')

argc = len(sys.argv)


#ACTIVE DIRECTORY CONNECTION BLOCK
ad_server = config.get('AD','ad_server')
ad_port = int(config.get('AD','ad_port'))
ad_username = config.get('AD','ad_username')
ad_password = config.get('AD', 'ad_password')
base_dn = config.get('AD','base_dn')
auto_bind = bool(config.get('PREF', 'auto_bind'))

#OPENLDAP CONNECTION BLOCK
ldap_server = config.get('LDAP','ldap_server')
ldap_port = int(config.get('LDAP','ldap_port'))
ldap_admin_username = config.get('LDAP','ldap_admin_username')
ldap_admin_password = config.get('LDAP','ldap_admin_password')
ldap_base_dn = config.get('LDAP','ldap_base_dn')
ldap_group_dn = config.get('LDAP','ldap_group_dn')


ldap_existing_groups = []
spec_search = False
input_dn = ""


def search_lines(filename_ad, total_lines_ad, input_dn):
    user_counter = 0
    global spec_search
    server = Server(ldap_server, port=ldap_port)
    conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
    dn,cn,sn,givenName,email,phoneNumber,sAMAccountName,memberOf = " " , " ", " ", " ", " ", " ", " ", []
    with open(filename_ad, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if line.startswith('#') or line.startswith(' '):
                if dn != " " and sAMAccountName != " " and cn != " " and givenName != " ":
                    if input_dn and spec_search:
                        search_result = conn.search(dn, '(objectClass=person)')
                        if search_result:
                            modification_dict = {}
                            attributes_to_compare = {
                            'givenName': givenName,
                            'sn': sn,
                            'telephoneNumber': phoneNumber,
                            'mail': mail,
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
                                group_dn = f"cn={group},{ldap_group_dn}"
                                result = conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})
                                print(f"Successfully modified membership of the LDAP entry: {cn}")
                            search_filter_groups = f"(&(objectClass=groupOfNames)(member={dn}))"
                            user_membership = conn.search(ldap_group_dn, search_filter=search_filter_groups)
                            if user_membership:
                                for group in ldap_existing_groups:
                                    group_dn = f"cn={group},{ldap_group_dn}"
                                    group_existing = conn.compare(group_dn, "member", dn)
                                    if group_existing:
                                        if group not in memberOf:
                                            print(f"Successfully modified membership of the LDAP entry: {cn}")
                                            group_changes = {
                                                    'member': [(MODIFY_DELETE, [dn])]
                                                    }
                                            result = conn.modify(group_dn, changes=group_changes)
                                        else:
                                            pass
                        break
                    elif not input_dn:
                        search_result = conn.search(dn, '(objectClass=person)')
                        if search_result:
                            modification_dict = {}
                            attributes_to_compare = {
                            'givenName': givenName,
                            'sn': sn,
                            'telephoneNumber': phoneNumber,
                            'mail': mail,
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

                                except Exception as e:
                                    print(f"Failed to modify the LDAP entry: {e}")
                            else:
                                pass

                        
                            for group in memberOf:
                                group_dn = f"cn={group},{ldap_group_dn}"
                                result = conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})

                            search_filter_groups = f"(&(objectClass=groupOfNames)(member={dn}))"
                            user_membership = conn.search(ldap_group_dn, search_filter=search_filter_groups)
                            if user_membership:
                                for group in ldap_existing_groups:
                                    group_dn = f"cn={group},{ldap_group_dn}"
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
                            object_class = ['inetOrgPerson','organizationalPerson','top','person']
                            new_attributes = {
                            'objectClass': object_class,
                            'ou': 'Groups',
                            'ou': 'Users',
                            'cn': cn,
                            'givenName': givenName,
                            'sn': sn,
                            'uid': sAMAccountName,
                            'mail': mail,
                            'telephoneNumber': phoneNumber,
                            }
                            result = conn.add(dn, attributes=new_attributes)
                            if result:
                                #print(f"{cn} added successfully. ")
                                pass
                            else:
                                print(f"Failed to add user: {conn.result}")
                    dn,cn,sn,givenName,email,phoneNumber,sAMAccountName,memberOf = " ", " ", " ", " ", " ", " ", " ", []

                elif input_dn and total_lines_ad == line_number:
                    print(f"User is not found !!")
                elif total_lines_ad == line_number:
                    print ("Number of users : ",user_counter)

            elif line.startswith('dn') and not spec_search :
                dn = line.strip()
                components = dn.split(',')
                converted_cn = components[0].split('=')[1]
                converted_dn = f"cn={converted_cn},{ldap_base_dn}"
                dn = converted_dn
                user_counter = user_counter + 1
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
            elif line.startswith('telephoneNumber'):
                phoneNumber = line.strip()
                phoneNumber = content(phoneNumber)
            elif line.startswith('memberOf'):
                group = line.strip()
                components = group.split(",")
                memberOf.append(components[0].split('=')[1])

            else:
                pass
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
    result = conn.search(ldap_group_dn,search_filter,attributes=["cn"])
    for entry in conn.entries:
        ldap_existing_groups.append(entry.cn)

    conn.unbind()

def content(content):
    converted = content.split(": ")
    content = converted[1]
    return content


start_time = time.time()
command_ad = f'ldapsearch -x -D {ad_username} -w {ad_password} -H ldap://{ad_server}:{ad_port} -b {base_dn} -s sub -E pr=1000/noprompt "(&(objectClass=Person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )" cn sn telephoneNumber mail givenName sAMAccountName memberOf > ad_users.ldif'
print("Fetching - Active Directory Users...")
result_ad = subprocess.run(command_ad, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# Check the result
if result_ad.returncode == 0:
    print("Successfully fetched.")
    total_lines_ad = int(subprocess.check_output(["wc", "-l", "ad_users.ldif"]).split()[0])
else:
    print("Failed with the following error:")
    print(result.stderr)


file_path = 'ad_users.ldif'
print("Synchronization is in progress...")
getLdapGroups()
if argc == 1:
    pass
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
