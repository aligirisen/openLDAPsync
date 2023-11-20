import subprocess, time, configparser, sys
from ldap3 import *

config = configparser.ConfigParser()
config.read('config.ini')

argc = len(sys.argv)

config_pref = configparser.ConfigParser()
config_pref.read('pref_config.ini')

#PREF
sync_group_mode = config_pref.get('PREF','sync_group')
ad_user_search_dn = config_pref.get('PREF','ad_user_search_dn')
ad_computer_search_dn = config_pref.get('PREF','ad_computer_search_dn')
ldap_directory_domain_dn = config_pref.get('PREF','ldap_default_directory_dn')
ldap_user_group_dn = config_pref.get('PREF','ldap_user_group_dn')
ldap_spec_directory = config_pref.get('PREF','ldap_spec_directory_dn')

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


ldap_existing_groups = []
known_directories = []
spec_search = False
input_dn = ""
ou_name = ""
def add_entry (conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf):
    if objectType == "Computer":
        object_class = ['top','person','inetOrgPerson','organizationalPerson']
        #object_class = ['inetOrgPerson','organizationalPerson','top','person']
        new_attributes = {
            'objectClass': object_class,
            'cn': cn,
            'uid': sAMAccountName,
            'sn': sn,
            }
        result = conn.add(dn, attributes=new_attributes)
        print(result,new_attributes)
        return
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

def modify_entry (conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf):
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
    search_filter_groups = f"(&(objectClass=groupOfNames)(member={dn}))"
    user_membership = conn.search(ldap_user_group_dn, search_filter=search_filter_groups)
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



def search_lines(filename_ad, total_lines_ad, input_dn):
    user_counter,new_user_counter = 0,0
    global spec_search
    global ou_name
    server = Server(ldap_server, port=ldap_port)
    conn = Connection(server, user=ldap_admin_username, password=ldap_admin_password, auto_bind=True)
    dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf = " " , " ", " ", " ", " ", " ", " ", " "," " , []
    with open(filename_ad, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if line.startswith('#') or line.startswith(' '):
                if dn != " " and sAMAccountName != " " and cn != " " :
                    if input_dn and spec_search:#spec user modify
                        search_result = conn.search(dn, '(objectClass=person)')
                        if search_result:
                            modify_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf,)
                            print("Existing changes have been applied")
                            break
                        else:
                            print("user is not existing on ldap")
                            break
                    elif not input_dn:
                        search_result = conn.search(dn, '(objectClass=person)')
                        if search_result:# user modify
                            user_counter = user_counter + 1
                            modify_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf)
                        else: #directory modify and add new user 
                            dir_dn = f'{ou_name},{ldap_directory}'
                            if dir_dn not in known_directories:
                                exist_directory = conn.search(dir_dn,'(objectClass=*)')
                                known_directories.append(f'{ou_name},{ldap_directory}')
                            else:
                                exist_directory is True
                            if exist_directory:
                                filter_str = f'(uid={sAMAccountName})'
                                exist_uid = conn.search(search_base=ldap_base_dn, search_filter=filter_str, search_scope=SUBTREE, attributes=['cn'])
                                if exist_uid:
                                    entry = conn.entries[0]
                                    conn.delete(entry.entry_dn)
                                add_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf)
                                new_user_counter = new_user_counter + 1
                                
                            elif sync_group_mode and not exist_directory:
                                groups_dn = ldap_base_dn
                                for directory in reversed(org_unit_list):
                                    group_str = f"{directory},{groups_dn}"
                                    groups_dn = group_str
                                    groups_attributes = {
                                            'objectClass': ['top','pardusLider', 'organizationalUnit'],
                                            'description': directory,
                                            }
                                    result = conn.add(group_str, attributes=groups_attributes)
                                    if not result:
                                        print("Directory could not create",group_str)
                                add_entry(conn,dn,cn,sn,givenName,mail,phoneNumber,homePostalAddress,sAMAccountName,objectType,memberOf)
                                new_user_counter = new_user_counter + 1
                                for group in memberOf:
                                    group_dn = f"cn={group},{ldap_user_group_dn}"
                                    conn.modify(group_dn, {'member': [(MODIFY_ADD, [dn])]})
                    dn,cn,sn,givenName,mail,homePostalAddress,phoneNumber,sAMAccountName,objectType,memberOf = " ", " ", " ", " ", " ", " ", " ", " "," ", []

                elif input_dn and total_lines_ad == line_number:
                    print(f"User is not found !!")
                elif total_lines_ad == line_number:
                    print ("Number of users : ",user_counter)
                    print ("Number of new users : ",new_user_counter)

            elif line.startswith('dn:') and not spec_search :
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
                            ou_name = ('ou=' + component[3:])
                            if component[3:] not in org_unit_list:
                                org_unit_list.append('ou=' + component[3:])
                    elif component.startswith('OU='):
                        formatted_components.append('ou=' + component[3:])
                        org_unit_list.append('ou=' + component[3:])

                ou_name = ','.join(org_unit_list)
                new_dn = ','.join(formatted_components)
                
                if ldap_spec_directory == "default" or ldap_spec_directory == "":#for creating new directory if it is not existing.
                    ldap_directory = ldap_directory_domain_dn
                else:
                    ldap_spec_directories = ldap_spec_directory.split(",")
                    for directory in ldap_spec_directories:
                        org_unit_list.append(directory)
                   
                    ldap_directory = f"{ldap_spec_directory},{ldap_directory_domain_dn}"
                if input_dn == dn:
                    spec_search = True
                    dn = input_dn
            elif line.startswith('cn:'):
                cn = line.strip()
                cn = content(cn)
            elif line.startswith('sn:'):
                sn = line.strip()
                sn = content(sn)
            elif line.startswith('givenName:'):
                givenName = line.strip()
                givenName = content(givenName)
            elif line.startswith('sAMAccountName:'):
                sAMAccountName = line.strip()
                sAMAccountName = content(sAMAccountName)
                dn = f"uid={sAMAccountName},{ou_name},{ldap_directory}"
            elif line.startswith('mail:'):
                mail = line.strip()
                mail = content(mail)
            elif line.startswith('homePostalAddress:'):
                homePostalAddress = line.strip()
                homePostalAddress = content(homePostalAddress)
            elif line.startswith('telephoneNumber:'):
                phoneNumber = line.strip()
                phoneNumber = content(phoneNumber)
            elif line.startswith('objectClass:'):
                objectClass = line.strip()
                objectClass = content(objectClass)
                if objectClass == "computer":
                    objectType = "Computer"
            elif line.startswith('operatingSystem:'):
                sn = line.strip()
                sn = content(sn)
            elif line.startswith('memberOf:'):
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
    result = conn.search(ldap_user_group_dn,search_filter)
    for entry in conn.entries:
        ldap_existing_groups.append(entry.cn)

    conn.unbind()

def content(content):
    converted = content.split(": ")
    content = converted[1]
    return content


start_time = time.time()


command_ad_computer = f'ldapsearch -x -b {ad_computer_search_dn} -H ldap://{ad_server}:{ad_port} -D {ad_username} -w {ad_password} "(objectClass=computer)" > ad_users.ldif'
print("Fetching - Active Directory Computers...")
result_ad_computer = subprocess.run(command_ad_computer, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


command_ad = f'ldapsearch -x -D {ad_username} -w {ad_password} -H ldap://{ad_server}:{ad_port} -b {ad_user_search_dn} "(&(objectClass=person)(objectCategory=person)(!(sAMAccountName=krbtgt))(!(sAMAccountName=Administrator))(!(sAMAccountName=Guest)) )" -s sub -E pr=1000/noprompt  cn sn telephoneNumber mail homePostalAddress givenName sAMAccountName memberOf >> ad_users.ldif'
print("Fetching - Active Directory Users...")
result_ad = subprocess.run(command_ad, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


# Check the result
if result_ad.returncode == 0 and result_ad_computer.returncode == 0:
    print("Successfully fetched.")
    total_lines_ad = int(subprocess.check_output(["wc", "-l", "ad_users.ldif"]).split()[0])
else:
    total_lines_ad = int(subprocess.check_output(["wc", "-l", "ad_users.ldif"]).split()[0])
    print("Fetching failed program will execute with existing ldif file. Error:")
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
