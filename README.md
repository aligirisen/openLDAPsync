# openLDAPsync
synchronize bidirectional Active Directory - openLDAP


firstly check the connection and please be ensured about your active directory user specifications with considering following features.


## Migration of Groups

### openLDAP does not has a default groups. So you have to create your own groups. Sync script's current version supports Groups, Users and Administration group migration.

### Take a glance at tree.
```
								---> cn=Administrators
---> DIT ---> ROOT DSE ---> dc=your-domain,dc=com --> ou=Groups ---> cn=DnsAdmins
								---> ou=Users
```
### Execute the following script
```
python3 createGroups.py
```
### Groups are created. Now lets grant full access to the Administrators group for user entries

```
sudo ldapmodify -H ldapi:/// -Y EXTERNAL -f Administrator_access.ldif
```



## Migration of Users


#### must have users in cn=Users group active directory side. It doesn't cover Administrator, krbtgt, guest or another default users.

### Execute following script

```
python3 syncAD.py
```



openLDAP should support UTF-8 for email addresses.
