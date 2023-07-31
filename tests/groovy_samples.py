"""These are used in fixtures for various tests.

They get their own file because otherwise, they confuse Vi's syntax
highlighting.
"""

CREATEACCOUNTJSON = """
${  
    Map map1 = new HashMap();
    if (! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("objectClass",["top", "person","organizationalPerson","inetOrgPerson","posixAccount","shadowAccount", "googlePerson","osuPerson","lpSghePerson","eduPerson"]);
    else map1.put("objectClass",["top", "person","organizationalPerson","inetOrgPerson","shadowAccount", "osuPerson","lpSghePerson","eduPerson"]);
    if( user.customproperty28 != null && ! user?.customproperty28?.allWhitespace)  map1.put("osuUID",user.customproperty28);
    map1.put("cn", ( user?.customproperty8?.equalsIgnoreCase('Y')?'Name Withheld': ( user?.customproperty22?.equalsIgnoreCase('FML')? user.lastname + ', ' + user?.firstname + ' '+ (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.middlename): (user?.customproperty22?.equalsIgnoreCase('FL')? user?.lastname + ', ' + user?.firstname : (user?.customproperty22?.equalsIgnoreCase('FIL')? user?.lastname + ', ' + user.firstname + ' '+(user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.middlename?.charAt(0) ): (user?.customproperty22?.equalsIgnoreCase('ML')? user.lastname + ', ' + (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.middlename ) : user?.lastname+ ', ' + user.firstname + (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : ' ' + user?.middlename))))) + (user?.customproperty30?.equalsIgnoreCase('R')?' (retired)':'') ));
    map1.put("cn;lang-en",( user?.customproperty8?.equalsIgnoreCase('Y')?'Name Withheld': ( user?.customproperty22?.equalsIgnoreCase('FML')? user.customproperty46+ ', ' + user?.customproperty47+ ' '+ (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.customproperty48): (user?.customproperty22?.equalsIgnoreCase('FL')? user?.customproperty46+ ', ' + user?.customproperty47: (user?.customproperty22?.equalsIgnoreCase('FIL')? user?.customproperty46+ ', ' + user.customproperty47+ ' '+(user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.customproperty48?.charAt(0) ): (user?.customproperty22?.equalsIgnoreCase('ML')? user.customproperty46+ ', ' + (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.customproperty48) : user?.customproperty46+ ', ' + user.customproperty47+ (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : ' ' + user?.customproperty48))))) + (user?.customproperty30?.equalsIgnoreCase('R')?' (retired)':'') ));
    map1.put("givenName",( user?.customproperty8?.equalsIgnoreCase('Y')?'Name': ( user?.customproperty22?.equalsIgnoreCase('ML')?
 (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.middlename ) : user.firstname?:' ')));
    map1.put("givenName;lang-en",( user?.customproperty8?.equalsIgnoreCase('Y')?'Name': ( user?.customproperty22?.equalsIgnoreCase('ML')?
 (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.customproperty48) : user.customproperty47?:' ')));
    map1.put("sn",( user?.customproperty8?.equalsIgnoreCase('Y')?'Withheld': user.lastname));
    map1.put("sn;lang-en",( user?.customproperty8?.equalsIgnoreCase('Y')?'Withheld': user.customproperty46));
    map1.put("uid",user.systemUserName);    
    map1.put("osuid",user.username);
    map1.put("eduPersonPrincipalName",user.systemUserName.toLowerCase() + '@oregonstate.edu');
    map1.put("nsroledn",["cn=non-mfaPwdPolicyRole,ou=people,o=orst.edu","cn=onidrole,o=orst.edu"]);
    map1.put("osuMail",(user.systemUserName.toLowerCase() + '@' + (user?.customproperty30?.equalsIgnoreCase('R') ? 'retiree.': '') + 'oregonstate.edu'));
    if ( ( ! user?.customproperty30?.equalsIgnoreCase('R')) &&  user.customproperty21 != null && ! user?.customproperty21?.allWhitespace )  map1.put("homeDirectory",user.customproperty21);
    if ( ( ! user?.customproperty30?.equalsIgnoreCase('R')) &&  (user.customproperty21 == null ||  user?.customproperty21?.allWhitespace )) map1.put("homeDirectory", "/users/u"+(Math.abs(new Random().nextInt() % 2) + 1)+"/"+user?.systemUserName?.charAt(0)+"/"+user.systemUserName);
    if  ( ! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("uidNumber",user?.customproperty38?:' ');  
    if  ( ! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("gidNumber",user?.customproperty20?:' ');
 if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty8?.equalsIgnoreCase('Y')) map1.put("gecos",",,,"); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && (user?.customproperty22 == null || user?.customproperty22?.equalsIgnoreCase('FML'))) map1.put("gecos",(user?.customproperty47+ ' ' + user?.customproperty46+ ',,,')); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty22?.equalsIgnoreCase('ML')) map1.put("gecos",(user?.customproperty48+ ' ' + user?.customproperty46+ ',,,')); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty22?.equalsIgnoreCase('FIL')) map1.put("gecos",(user?.customproperty47+ ' '+ user?.customproperty46+ ',,,')); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty22?.equalsIgnoreCase('FL')) map1.put("gecos",(user?.customproperty47+ ' '+ user?.customproperty46+ ',,,'));
    if ( ( ! user?.customproperty30?.equalsIgnoreCase('R')) ) map1.put("loginShell",  user.customproperty35?:' ');        
    if( user.customproperty29 != null && ! user?.customproperty29?.allWhitespace)  map1.put("osuPIDM",user.customproperty29);   
    map1.put("osuPrimaryMail",(user.systemUserName.toLowerCase() + '@' + (user?.customproperty30?.equalsIgnoreCase('R') ? 'retiree.': '') + 'oregonstate.edu'));
    if( user.customproperty6 != null && ! user?.customproperty6?.allWhitespace)  map1.put("osuBirthdate",user.customproperty6);
    if( user.firstname != null && ! user?.firstname?.allWhitespace)  map1.put("osuGivenName",user.firstname);
    if( user.middlename != null && ! user?.middlename?.allWhitespace)  map1.put("osuMiddleName",user.middlename);
    if( user.lastname != null && ! user?.lastname?.allWhitespace)  map1.put("osuSn",user.lastname);
   if( user.customproperty8 != null && ! user?.customproperty8?.allWhitespace && user.customproperty8 == 'Y' ) map1.put("osuConfidential","1");
else map1.put("osuConfidential",'0');
    if( user.customproperty30 != null && ! user?.customproperty30?.allWhitespace) map1.put("osuPrimaryAffiliation",user.customproperty30);
    if( user.phonenumber != null && ! user?.phonenumber?.allWhitespace)  map1.put("telephoneNumber",user.phonenumber);
    if( user.secondaryPhone != null && ! user?.secondaryPhone?.allWhitespace)  map1.put("osuAltPhoneNumber",user.secondaryPhone);   
    if( user.customproperty18 != null && ! user?.customproperty18?.allWhitespace)  map1.put("facsimiletelephonenumber",user.customproperty18);
    if( user.customproperty36 != null && ! user?.customproperty36?.allWhitespace)  map1.put("title",user.customproperty36);
    if( user.customproperty15 != null && ! user?.customproperty15?.allWhitespace)  map1.put("osuDepartment",user.customproperty15);
    if( user.customproperty31 != null && ! user?.customproperty31?.allWhitespace) map1.put("mail", user?.customproperty31?:'');
    if( user.customproperty14 != null && ! user?.customproperty14?.allWhitespace)  map1.put("postalAddress",user.customproperty14);
    if( user.customproperty26 != null && ! user?.customproperty26?.allWhitespace)  map1.put("osuOfficeAddress",user.customproperty26);
    if( user.customproperty37 != null && ! user?.customproperty37?.allWhitespace)  map1.put("udcid",user.customproperty37);
    if( user.customproperty41 != null && ! user?.customproperty41?.allWhitespace)  map1.put("eduPersonPrincipalNamePrior", user?.customproperty41+ '@oregonstate.edu'?:'');
    if( ! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("googlePrincipalName", task.accountName.toLowerCase() + '@oregonstate.edu' ); 
   List afflist = [];
  if (user?.customproperty11?.equals('1')) afflist  << 'student';
  if (user?.employeeid?.equals('1')) afflist << 'employee';
  if (user?.customproperty9?.equals('1')) afflist << 'affiliate';
 map1.put("eduPersonAffiliation",afflist +(user?.customproperty10?.equals('1') ? ' ': 'member')); 
    if ( user?.customproperty30 != null && ! user?.customproperty30?.allWhitespace) 
        if      ( user?.customproperty30?.equalsIgnoreCase('O') || user?.customproperty30?.equalsIgnoreCase('R')) map1.put("eduPersonPrimaryAffiliation", 'affiliate');
        else if ( user?.customproperty30?.equalsIgnoreCase('E')) map1.put("eduPersonPrimaryAffiliation", 'employee');
        else if ( user?.customproperty30?.equalsIgnoreCase('S')) map1.put("eduPersonPrimaryAffiliation", 'student');
    
def map1Json = map1 as grails.converters.JSON;
print map1Json?.toString();

}
"""

UPDATEACCOUNTJSON = """
${ Map map1 = new HashMap(); map1.put("cn", ( user?.customproperty8?.equalsIgnoreCase('Y')?'Name Withheld': ( user?.customproperty22?.equalsIgnoreCase('FML')? user.lastname + ', ' + user?.firstname + ' '+ (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.middlename): (user?.customproperty22?.equalsIgnoreCase('FL')? user?.lastname + ', ' + user?.firstname : (user?.customproperty22?.equalsIgnoreCase('FIL')? user?.lastname + ', ' + user.firstname + ' '+(user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.middlename?.charAt(0) ): (user?.customproperty22?.equalsIgnoreCase('ML')? user.lastname + ', ' + (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.middlename ) : user?.lastname+ ', ' + user.firstname + (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : ' ' + user?.middlename))))) + (user?.customproperty30?.equalsIgnoreCase('R')?' (retired)':'') )); map1.put("cn;lang-en",( user?.customproperty8?.equalsIgnoreCase('Y')?'Name Withheld': ( user?.customproperty22?.equalsIgnoreCase('FML')? user.customproperty46+ ', ' + user?.customproperty47+ ' '+ (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.customproperty48): (user?.customproperty22?.equalsIgnoreCase('FL')? user?.customproperty46+ ', ' + user?.customproperty47: (user?.customproperty22?.equalsIgnoreCase('FIL')? user?.customproperty46+ ', ' + user.customproperty47+ ' '+(user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.customproperty48?.charAt(0) ): (user?.customproperty22?.equalsIgnoreCase('ML')? user.customproperty46+ ', ' + (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : '' + user?.customproperty48) : user?.customproperty46+ ', ' + user.customproperty47+ (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : ' ' + user?.customproperty48))))) + (user?.customproperty30?.equalsIgnoreCase('R')?' (retired)':'') )); map1.put("givenName",( user?.customproperty8?.equalsIgnoreCase('Y')?'Name': ( user?.customproperty22?.equalsIgnoreCase('ML')? (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.middlename ) : user.firstname?:' '))); map1.put("givenName;lang-en",( user?.customproperty8?.equalsIgnoreCase('Y')?'Name': ( user?.customproperty22?.equalsIgnoreCase('ML')? (user?.middlename == null || user?.middlename ?.allWhitespace ? '' : user?.customproperty48) : user.customproperty47?:' '))); map1.put("sn",( user?.customproperty8?.equalsIgnoreCase('Y')?'Withheld': user.lastname)); map1.put("sn;lang-en",( user?.customproperty8?.equalsIgnoreCase('Y')?'Withheld': user.customproperty46)); if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty8?.equalsIgnoreCase('Y')) map1.put("gecos",",,,"); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && (user?.customproperty22 == null || user?.customproperty22?.equalsIgnoreCase('FML'))) map1.put("gecos",(user?.customproperty47+ ' ' + user?.customproperty46+ ',,,')); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty22?.equalsIgnoreCase('ML')) map1.put("gecos",(user?.customproperty48+ ' ' + user?.customproperty46+ ',,,')); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty22?.equalsIgnoreCase('FIL')) map1.put("gecos",(user?.customproperty47+ ' '+ user?.customproperty46+ ',,,')); else if ( ! user?.customproperty30?.equalsIgnoreCase('R') && user?.customproperty22?.equalsIgnoreCase('FL')) map1.put("gecos",(user?.customproperty47+ ' '+ user?.customproperty46+ ',,,'));  if ( ! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("gidNumber",user?.customproperty20?:' '); if ( ! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("uidNumber",user?.customproperty38?:' '); if( user.customproperty29 != null && ! user?.customproperty29?.allWhitespace) map1.put("osuPIDM",user.customproperty29); map1.put("uid",user.systemUserName); if( user.customproperty6 != null && ! user?.customproperty6?.allWhitespace) map1.put("osuBirthdate",user.customproperty6); if( user.firstname != null && ! user?.firstname?.allWhitespace) map1.put("osuGivenName",user.firstname); if( user.middlename != null && ! user?.middlename?.allWhitespace) map1.put("osuMiddleName",user.middlename); if( user.lastname != null && ! user?.lastname?.allWhitespace) map1.put("osuSn",user.lastname); if( user.customproperty8 != null && ! user?.customproperty8?.allWhitespace && user.customproperty8 == 'Y' ) map1.put("osuConfidential","1"); else map1.put("osuConfidential",'0'); if( user.customproperty30 != null && ! user?.customproperty30?.allWhitespace) map1.put("osuPrimaryAffiliation",user.customproperty30); if( user.phonenumber != null && ! user?.phonenumber?.allWhitespace) map1.put("telephoneNumber",user.phonenumber); if( user.secondaryPhone != null && ! user?.secondaryPhone?.allWhitespace) map1.put("osuAltPhoneNumber",user.secondaryPhone); if( user.customproperty18 != null && ! user?.customproperty18?.allWhitespace) map1.put("facsimiletelephonenumber",user.customproperty18); if( user.customproperty36 != null && ! user?.customproperty36?.allWhitespace) map1.put("title",user.customproperty36); if( user.customproperty15 != null && ! user?.customproperty15?.allWhitespace) map1.put("osuDepartment",user.customproperty15); 
if( user.customproperty31 != null && ! user?.customproperty31?.allWhitespace) map1.put("mail", user?.customproperty31?:'');
if( user.customproperty14 != null && ! user?.customproperty14?.allWhitespace) map1.put("postalAddress",user.customproperty14); if( user.customproperty26 != null && ! user?.customproperty26?.allWhitespace) map1.put("osuOfficeAddress",user.customproperty26); if( user.customproperty37 != null && ! user?.customproperty37?.allWhitespace) map1.put("udcid",user.customproperty37); if( user.customproperty41 != null && ! user?.customproperty41?.allWhitespace) map1.put("eduPersonPrincipalNamePrior", user?.customproperty41+ '@oregonstate.edu'?:''); if ( ( ! user?.customproperty30?.equalsIgnoreCase('R')) && user.customproperty21 != null && ! user?.customproperty21?.allWhitespace ) map1.put("homeDirectory",user.customproperty21); map1.put("eduPersonPrincipalName",user.systemUserName.toLowerCase() + '@oregonstate.edu'); if( ! user?.customproperty30?.equalsIgnoreCase('R')) map1.put("googlePrincipalName", user.systemUserName.toLowerCase() + '@oregonstate.edu' ); List afflist = []; if (user?.customproperty11?.equals('1')) afflist << 'student'; if (user?.employeeid?.equals('1')) afflist << 'employee'; if (user?.customproperty9?.equals('1')) afflist << 'affiliate'; map1.put("eduPersonAffiliation",afflist +(user?.customproperty10?.equals('1') ? ' ': 'member')); if ( user?.customproperty30 != null && ! user?.customproperty30?.allWhitespace) if ( user?.customproperty30?.equalsIgnoreCase('O') || user?.customproperty30?.equalsIgnoreCase('R')) map1.put("eduPersonPrimaryAffiliation", 'affiliate'); else if ( user?.customproperty30?.equalsIgnoreCase('E')) map1.put("eduPersonPrimaryAffiliation", 'employee'); else if ( user?.customproperty30?.equalsIgnoreCase('S')) map1.put("eduPersonPrimaryAffiliation", 'student'); def map1Json = map1 as grails.converters.JSON; print map1Json?.toString(); }
"""