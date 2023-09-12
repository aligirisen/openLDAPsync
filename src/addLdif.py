import subprocess, os

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



script_directory = os.path.dirname(os.path.abspath(__file__))

ldif_directory = os.path.join(script_directory, "ldif")

# Create the ldif_contents directory if it doesn't exist
if not os.path.exists(ldif_directory):
    print("Directory is not existing")



ldif_files = [file for file in os.listdir(ldif_directory) if file.endswith(".ldif")]
os.chdir("ldif")

print(ldif_files)
# Loop through LDIF files and execute ldapmodify
for ldif_file in ldif_files:
    command = [
        "ldapmodify",
        "-a",
        "-x",
        "-D", ldap_admin_username,
        "-w", ldap_admin_password,
        "-H", ldap_server,
        "-f", ldif_file
    ]

    try:
        # Execute the ldapmodify command
        print(command)
        subprocess.run(command, check=True)
        print(f"Successfully executed {ldif_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {ldif_file}: {e}")
