"""These are used in fixtures for various tests.

They get their own file because otherwise, they confuse Vi's syntax
highlighting.
"""

BAD_JSON = """{                                                                                                                                               
"UpdateUserQry": [ "Update SAVIYNT_GYBONID set GYBONID_ACTIVITY_DATE=TO_DATE('${user.updatedate.format('M/d/y H:mm:ss')}', 'MM/DD/YYYY HH24:MI:SS'), GYBONID_ACTIVATED_DATE=${((user?.customproperty1 == null || us
er?.customproperty1?.allWhitespace) ? 'NULL' : 'TO_DATE(\''+user.customproperty1 + '\', \'YYYY-MM-DD HH24:MI:SS\')')}, GYBONID_HOME_DIR='${user.customproperty21?:''}', GYBONID_HAS_BEEN_ACTIVATED_IND=${user.custo
mproperty40}, GYBONID_LOGIN_NAME='${user.systemUserName}',GYBONID_ONID_CURRENT_USER=${user.customproperty27},GYBONID_OSUUID=${user.customproperty28}, GYBONID_PRIMARY_EMAIL_ADDRESS ='${user.email}', GYBONID_UID =
'${user.customproperty38}', GYBONID_SHELL='${user.customproperty35}',GYBONID_GID='${user.customproperty20}' WHERE GYBONID_OSU_ID ='${user.username}'" ]
 } """



JSON_WITH_SQL = """
{
	"ADDITIONALTABLES": {
		"USERS": "SELECT username, firstname, lastname, systemusername, customproperty28, customproperty41,customproperty42,customproperty38, customproperty20, customproperty19, customproperty35,customproperty21, email FROM USERS"
	},
	"COMPUTEDCOLUMNS": ["username", "systemusername", "employeeid", "customproperty28", "customproperty21", "firstname", "lastname", "comments", "createdate", "statuskey", "customproperty41", "customproperty42", "customproperty38", "customproperty20", "customproperty19", "customproperty35", "email"],
	"PREPROCESSQUERIES": ["ALTER TABLE currentusers ADD INDEX `USERNAME` (`USERNAME` ASC)", "ALTER TABLE NEWUSERDATA ADD INDEX `idx_temp_USERNAME` (`USERNAME` ASC)", "UPDATE newuserdata , ( SELECT @newuid := IFNULL(MAX(customproperty28),'10000000000') + 1 FROM currentusers WHERE customproperty28 LIKE '100%') tmp SET customproperty28 = @newuid:= @newuid + FLOOR(RAND()*20) + 1 WHERE LENGTH(TRIM(IFNULL(customproperty28,' '))) = 0 AND statuskey = 1", "UPDATE NEWUSERDATA INNER JOIN currentusers ON currentusers.username = newuserdata.username SET newuserdata.systemusername= currentusers.systemusername, newuserdata.customproperty20= currentusers.customproperty20, newuserdata.customproperty28= currentusers.customproperty28, newuserdata.customproperty19= currentusers.customproperty19, newuserdata.customproperty35= currentusers.customproperty35, newuserdata.customproperty38= currentusers.customproperty38, newuserdata.email= currentusers.email WHERE LENGTH(TRIM(IFNULL(newuserdata.systemusername, ' '))) = 0 and currentusers.systemusername is not null AND newuserdata.statuskey = 1", "UPDATE newuserdata SET customproperty35 = '/bin/bash' WHERE LENGTH(TRIM(IFNULL(customproperty35,' '))) = 0 AND IFNULL(newuserdata.customproperty30,'X') != 'R' AND statuskey = 1", "UPDATE newuserdata SET customproperty20='300'         WHERE LENGTH(TRIM(IFNULL(customproperty20,' '))) = 0 AND IFNULL(newuserdata.customproperty30,'X') != 'R' AND statuskey = 1", "UPDATE newuserdata SET customproperty19 = CASE WHEN IFNULL(customproperty8,'N') = 'Y' THEN ',,,' else CONCAT(firstname, ' ', lastname,',,,') END WHERE LENGTH(TRIM(IFNULL(systemusername,' '))) = 0 AND IFNULL(newuserdata.customproperty30,'X') != 'R' AND statuskey = 1", "UPDATE newuserdata left join currentusers on newuserdata.username = currentusers.username SET newuserdata.customproperty21 = IFNULL(currentusers.customproperty21,concat('/users/u',FLOOR(RAND()*2+1),'/',left(newuserdata.systemusername,1),'/',newuserdata.systemusername)) WHERE IFNULL(newuserdata.customproperty30,'X') != 'R' AND LENGTH(TRIM(IFNULL(newuserdata.customproperty21,' '))) = 0 and LENGTH(TRIM(IFNULL(newuserdata.systemusername,' '))) > 0 and newuserdata.statuskey = 1", "INSERT INTO NEWUSERDATA(username,customproperty42,systemusername,comments,createdate,firstname,lastname,statuskey,customproperty41,email) SELECT concat('PRIOR-',currentusers.systemusername) as username, currentusers.username as customproperty42,currentusers.systemusername as systemusername,(select concat('Systemusername change from ',currentusers.systemusername,' to ',newuserdata.systemusername)) as Comments, now() as createdate, currentusers.firstname as firstname, currentusers.lastname as lastname, 0 as statuskey, currentusers.customproperty41, currentusers.email FROM NEWUSERDATA inner join currentusers on newuserdata.username = currentusers.username WHERE newuserdata.systemusername != currentusers.systemusername", "UPDATE newuserdata INNER JOIN currentusers ON currentusers.username = newuserdata.username SET newuserdata.customproperty41= concat(case when ifnull(currentusers.customproperty41,'')= ' ' then '' else concat(currentusers.customproperty41,',') end, currentusers.systemusername) WHERE newuserdata.systemusername != currentusers.systemusername", "UPDATE newuserdata left JOIN currentusers ON currentusers.username = newuserdata.username , ( SELECT @newid := max(cast(customproperty38 as signed)) FROM currentusers) tmp SET newuserdata.customproperty38 = ifnull(currentusers.customproperty38, @newid:= @newid + 1) WHERE LENGTH(TRIM(IFNULL(newuserdata.customproperty38,' '))) = 0 AND IFNULL(newuserdata.customproperty30,'X') != 'R' AND newuserdata.statuskey = 1"]
}
"""
