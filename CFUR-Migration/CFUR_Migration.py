
# This program will set Call Forward Unregister values to match
# existing DN but use a special ICT CSS to migrate users to another 
# cluster.
#
# You can pass in the parameters on the command line or edit the
# sys.argv line at the bottom of the script.
#
# Install Python 2.7 and choose the option to add to path (off by default)
#
# Then install two modules
#  C:\>pip install requests
#  C:\>pip install BeautifulSoup4
# May need to use "python -m pip install requests"
#
# Then run the program CFUR-Migration.py
#  C:\>python CFUR-Migration.py hostname/IP username password CFUR-CSS


import sys
import requests
import warnings
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth


def main(argv):
   warnings.filterwarnings("ignore")
   hostname = ''
   username = ''
   password = ''
   cfur_css = ''

   
   try:
      hostname = sys.argv[1]
      username = sys.argv[2]
      password = sys.argv[3]
      cfur_css = sys.argv[4]
   except:
      print('Please enter hostname/IP Address, username, password, and the CFUR CSS to use')
      sys.exit()
	
   #Create a new session to maintain cookies across requests      
   s = requests.Session()
   
   headers= {"SOAPAction": "\"CUCM:DB ver=10.5 getPhone\"", "Content-Type": "text/xml"}

   #Get list of numplan PKIDs that need to be updated
   numplanquery = '<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\"><soapenv:Body><ns:executeSQLQuery><sql>select np.pkid from devicenumplanmap dnpm left join device d on dnpm.fkdevice=d.pkid left join numplan np on dnpm.fknumplan=np.pkid where d.tkclass = \'1\' or d.tkclass = \'10\'  or d.tkclass=\'252\' or d.tkclass=\'254\'</sql></ns:executeSQLQuery></SOAP-ENV:Envelope>'
   numplanxml = s.post('https://' + hostname + ':8443/axl/', verify=False, auth=HTTPBasicAuth(username,password),headers=headers, data=numplanquery)
   soup = BeautifulSoup(numplanxml.text)
   pkidlist = soup.find_all('pkid')
   
   for pkid in pkidlist:
       #Set CFUR External to not go to voicemail
       payload1 = '<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\"><soapenv:Body><ns:executeSQLUpdate><sql>update numplan set cfurvoicemailenabled = \'f\' where pkid=\'' + pkid.get_text() + '\'</sql></ns:executeSQLUpdate></SOAP-ENV:Envelope>'
       req1 = s.post('https://' + hostname + ':8443/axl/', verify=False, auth=HTTPBasicAuth(username,password),headers=headers, data=payload1)
       print('CFUR External Voicemail Response for ' + pkid.get_text() + ': ' + req1.text)

       #Set CFUR Internal to not go to voicemail
       payload2 = '<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\"><soapenv:Body><ns:executeSQLUpdate><sql>update numplan set cfurintvoicemailenabled = \'f\' where pkid=\'' + pkid.get_text() + '\'</sql></ns:executeSQLUpdate></SOAP-ENV:Envelope>'
       req2 = s.post('https://' + hostname + ':8443/axl/', verify=False, headers=headers, data=payload2)
       print('\nCFUR Internal Voicemail Response: for ' + pkid.get_text() + ': ' + req2.text)

       #Set CFUR External Number
       payload3 = '<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\"><soapenv:Body><ns:executeSQLUpdate><sql>update numplan set cfurdestination=dnorpattern where pkid=\'' + pkid.get_text() + '\'</sql></ns:executeSQLUpdate></SOAP-ENV:Envelope>'
       req3 = s.post('https://' + hostname + ':8443/axl/', verify=False, headers=headers, data=payload3)
       print('\nCFUR External Extension Response: for ' + pkid.get_text() + ': ' + req3.text)

       #Set CFUR Internal Number
       payload4 = '<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\"><soapenv:Body><ns:executeSQLUpdate><sql>update numplan set cfurintdestination=dnorpattern where pkid=\'' + pkid.get_text() + '\'</sql></ns:executeSQLUpdate></SOAP-ENV:Envelope>'
       req4 = s.post('https://' + hostname + ':8443/axl/', verify=False, headers=headers, data=payload4)
       print('\nCFUR Internal Extension Response: for ' + pkid.get_text() + ': ' + req4.text)

       #Set CFUR External CSS Number
       payload5 = '<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\"><soapenv:Body><ns:executeSQLUpdate><sql>update numplan set fkcallingsearchspace_cfur= (select pkid from callingsearchspace where name=\'' + cfur_css + '\') where pkid=\'' + pkid.get_text() + '\'</sql></ns:executeSQLUpdate></SOAP-ENV:Envelope>'
       req5 = s.post('https://' + hostname + ':8443/axl/', verify=False, headers=headers, data=payload5)
       print('\nCFUR External CSS Response: for ' + pkid.get_text() + ': ' + req5.text)

       #Set CFUR Internal CSS Number
       payload6 = '<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\" xmlns:ns=\"http://www.cisco.com/AXL/API/10.5\"><soapenv:Body><ns:executeSQLUpdate><sql>update numplan set fkcallingsearchspace_cfurint= (select pkid from callingsearchspace where name=\'' + cfur_css + '\') where pkid=\'' + pkid.get_text() + '\'</sql></ns:executeSQLUpdate></SOAP-ENV:Envelope>'
       req6 = s.post('https://' + hostname + ':8443/axl/', verify=False, headers=headers, data=payload6)
       print('\nCFUR Internal CSS Response: for ' + pkid.get_text() + ': ' + req6.text)

if __name__ == "__main__":
   #Replace the below values or pass the commands through the command-line and remove the below line
   sys.argv = ["CFUR-Migration.py", "192.168.1.1", "admin", "password", "ICT-CFUR-CSS"]
   main(sys.argv[1:])