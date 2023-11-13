# openLDAPsync
synchronize bidirectional Active Directory - openLDAP


firstly check the connection and please be ensured about your active directory user specifications with considering following features.

configure .ini files and execute testConnections.py, you should see result of tests.


```
python3 testConnections.py
```

## Migration of Users

#### It doesn't cover Administrator, krbtgt, guest or another default users.

### Execute following script

```
python3 syncAD.py
```


