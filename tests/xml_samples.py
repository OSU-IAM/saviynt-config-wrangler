<dataMapping>
    <sql-query description="This is the Source DB Query" uniquecolumnsascommaseparated="username">
        <![CDATA[SELECT  CASE WHEN (GYBONID_CURRENT_USER_IND = 1 AND GYBONID_MANUALLY_DISABLED_DATE IS NULL) THEN 1 ELSE 0 END AS STATUSKEY, GYBONID_AFFILIATION_CODE AS CUSTOMPROPERTY2,TO_CHAR(GYBONID_AFFILIATION_DATE, 'YYYY-MM-DD HH24:MI:SS') as CUSTOMPROPERTY3,GYBONID_AFFILIATION_END_TERM AS CUSTOMPROPERTY4,GYBONID_AFFILIATION_TERM AS CUSTOMPROPERTY5,GYBONID_ALT_PHONE_NUMBER AS SECONDARYPHONE,to_char(GYBONID_BIRTH_DATE ,'YYYYMMDD')AS CUSTOMPROPERTY6,TO_CHAR(GYBONID_CLEANUP_DATE, 'YYYY-MM-DD HH24:MI:SS') as CUSTOMPROPERTY7,GYBONID_CONFID_IND AS CUSTOMPROPERTY8,GYBONID_CURRENT_AFFIL_IND AS CUSTOMPROPERTY9,GYBONID_CURRENT_EMPLOYEE_IND AS EMPLOYEEID,GYBONID_CURRENT_RETIREE_IND AS CUSTOMPROPERTY10,GYBONID_CURRENT_STUDENT_IND AS CUSTOMPROPERTY11,GYBONID_CURRENT_USER_IND AS CUSTOMPROPERTY12,TO_CHAR(GYBONID_DATE_TO_DEACTIVATE, 'YYYY-MM-DD HH24:MI:SS') as CUSTOMPROPERTY13,TO_CHAR(GYBONID_DEACTIVATED_DATE , 'YYYY-MM-DD HH24:MI:SS') as ENDDATE,GYBONID_DEPT_ADDRESS AS CUSTOMPROPERTY14,GYBONID_DEPT_DESC AS CUSTOMPROPERTY15,GYBONID_DESFIRE_ID AS CUSTOMPROPERTY16,GYBONID_PRIMARY_EMAIL_ADDRESS AS EMAIL,GYBONID_FAX_NUMBER AS CUSTOMPROPERTY18,GYBONID_FIRST_NAME AS FIRSTNAME,GYBONID_LAST_NAME AS LASTNAME,GYBONID_LOGIN_NAME AS SYSTEMUSERNAME,GYBONID_MI_NAME AS MIDDLENAME,TO_CHAR(GYBONID_MANUALLY_DEACTIV_DATE , 'YYYY-MM-DD HH24:MI:SS') as CUSTOMPROPERTY24,TO_CHAR(GYBONID_MANUALLY_DISABLED_DATE , 'YYYY-MM-DD HH24:MI:SS') as CUSTOMPROPERTY25,GYBONID_OFFICE_ADDRESS AS CUSTOMPROPERTY26,GYBONID_OSUUID AS CUSTOMPROPERTY28,GYBONID_HOME_DIR AS CUSTOMPROPERTY21,GYBONID_GID AS CUSTOMPROPERTY20, GYBONID_SHELL AS CUSTOMPROPERTY35, GYBONID_UID AS CUSTOMPROPERTY38,GYBONID_OSU_ID AS USERNAME,GYBONID_PHONE_NUMBER AS PHONENUMBER,GYBONID_PIDM AS CUSTOMPROPERTY29,GYBONID_PRIMARY_AFFILIATION AS CUSTOMPROPERTY30,GYBONID_EMAIL_ADDRESS AS CUSTOMPROPERTY31, GYBONID_PROX_CSN AS CUSTOMPROPERTY32,GYBONID_PROX_ID AS CUSTOMPROPERTY33,TO_CHAR(GYBONID_REMOVED_FROM_ONID_DATE , 'YYYY-MM-DD HH24:MI:SS') as CUSTOMPROPERTY34,GYBONID_TITLE_DESC AS CUSTOMPROPERTY36,GYBONID_UDC_ID AS CUSTOMPROPERTY37,TO_CHAR(GYBONID_WARNING_DATE , 'YYYY-MM-DD HH24:MI:SS') as CUSTOMPROPERTY39, REGEXP_REPLACE(REGEXP_REPLACE(LOWER(GYBONID_LAST_NAME),'(jr|jr\.|sr|sr\.|i|ii|iii|iv|v|vi|vii|viii|ix|x)$'), '[^a-z]', '') AS CUSTOMPROPERTY44, REGEXP_REPLACE(LOWER(GYBONID_FIRST_NAME), '[^a-z]', '') AS CUSTOMPROPERTY45, REGEXP_REPLACE(DECOMPOSE(GYBONID_LAST_NAME,'CANONICAL'),'[^'||CHR(32)||'-'||CHR(127)||']','') AS CUSTOMPROPERTY46, REGEXP_REPLACE(DECOMPOSE(GYBONID_FIRST_NAME,'CANONICAL'),'[^'||CHR(32)||'-'||CHR(127)||']','') AS CUSTOMPROPERTY47, REGEXP_REPLACE(DECOMPOSE(GYBONID_MI_NAME,'CANONICAL'),'[^'||CHR(32)||'-'||CHR(127)||']','') AS CUSTOMPROPERTY48, GYBONID_ACTIVITY_DATE FROM  SAVIYNT_GYBONID]]>
    </sql-query>
    <importsettings>
        <zeroDayProvisioning>true</zeroDayProvisioning>
        <generateEmail>true</generateEmail>
        <userNotInFileAction>NOACTION</userNotInFileAction>
        <checkRules>true</checkRules>
        <buildUserMap>true</buildUserMap>
        <generateSystemUsername>true</generateSystemUsername>
         <userOperationsAllowed>CREATE,UPDATE</userOperationsAllowed>
        <userReconcillationField>username</userReconcillationField>
    </importsettings>
    <mapper description="This is the mapping field for Saviynt Field name" dateformat="date" incrementalcolumn="GYBONID_ACTIVITY_DATE">
        <mapfield saviyntproperty="CUSTOMPROPERTY2" sourceproperty="CUSTOMPROPERTY2" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY3" sourceproperty="CUSTOMPROPERTY3" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY4" sourceproperty="CUSTOMPROPERTY4" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY5" sourceproperty="CUSTOMPROPERTY5" type="character"/>
        <mapfield saviyntproperty="SECONDARYPHONE" sourceproperty="SECONDARYPHONE" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY6" sourceproperty="CUSTOMPROPERTY6" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY7" sourceproperty="CUSTOMPROPERTY7" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY8" sourceproperty="CUSTOMPROPERTY8" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY9" sourceproperty="CUSTOMPROPERTY9" type="character"/>
        <mapfield saviyntproperty="EMPLOYEEID" sourceproperty="EMPLOYEEID" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY10" sourceproperty="CUSTOMPROPERTY10" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY11" sourceproperty="CUSTOMPROPERTY11" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY12" sourceproperty="CUSTOMPROPERTY12" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY13" sourceproperty="CUSTOMPROPERTY13" type="character"/>
        <mapfield saviyntproperty="ENDDATE" sourceproperty="ENDDATE" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY14" sourceproperty="CUSTOMPROPERTY14" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY15" sourceproperty="CUSTOMPROPERTY15" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY16" sourceproperty="CUSTOMPROPERTY16" type="character"/>
        <mapfield saviyntproperty="EMAIL" sourceproperty="EMAIL" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY18" sourceproperty="CUSTOMPROPERTY18" type="character"/>
        <mapfield saviyntproperty="FIRSTNAME" sourceproperty="FIRSTNAME" type="character"/>
        <mapfield saviyntproperty="LASTNAME" sourceproperty="LASTNAME" type="character"/>
        <mapfield saviyntproperty="SYSTEMUSERNAME" sourceproperty="SYSTEMUSERNAME" type="character"/>
        <mapfield saviyntproperty="MIDDLENAME" sourceproperty="MIDDLENAME" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY24" sourceproperty="CUSTOMPROPERTY24" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY25" sourceproperty="CUSTOMPROPERTY25" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY26" sourceproperty="CUSTOMPROPERTY26" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY28" sourceproperty="CUSTOMPROPERTY28" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY20" sourceproperty="CUSTOMPROPERTY20" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY21" sourceproperty="CUSTOMPROPERTY21" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY35" sourceproperty="CUSTOMPROPERTY35" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY38" sourceproperty="CUSTOMPROPERTY38" type="character"/>
        <mapfield saviyntproperty="USERNAME" sourceproperty="USERNAME" type="character"/>
        <mapfield saviyntproperty="PHONENUMBER" sourceproperty="PHONENUMBER" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY29" sourceproperty="CUSTOMPROPERTY29" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY30" sourceproperty="CUSTOMPROPERTY30" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY31" sourceproperty="CUSTOMPROPERTY31" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY32" sourceproperty="CUSTOMPROPERTY32" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY33" sourceproperty="CUSTOMPROPERTY33" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY34" sourceproperty="CUSTOMPROPERTY34" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY36" sourceproperty="CUSTOMPROPERTY36" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY37" sourceproperty="CUSTOMPROPERTY37" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY39" sourceproperty="CUSTOMPROPERTY39" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY23" sourceproperty="GYBONID_ACTIVITY_DATE" type="timestamp"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY44" sourceproperty="CUSTOMPROPERTY44" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY45" sourceproperty="CUSTOMPROPERTY45" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY46" sourceproperty="CUSTOMPROPERTY46" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY47" sourceproperty="CUSTOMPROPERTY47" type="character"/>
        <mapfield saviyntproperty="CUSTOMPROPERTY48" sourceproperty="CUSTOMPROPERTY48" type="character"/>
        <mapfield saviyntproperty="STATUSKEY" sourceproperty="STATUSKEY" type="number"/>
    </mapper>
</dataMapping>
