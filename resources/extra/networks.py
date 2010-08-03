"""
Automatically generated from a VMB Opco_Settings_9.4.6.20529_RC9
"""


class NetworkOperator(object):
    netid = []
    name = None
    country = None
    apn = None
    username = None
    password = None
    dns1 = None
    dns2 = None
    smsc = None
    mmsc = None
    type = None
    wap1 = None
    wap2 = None

    def __repr__(self):
        args = (self.name, self.country, self.netid[0])
        return "<NetworkOperator %s %s netid: %s>" % args


class Vodafone_20205_Contract(NetworkOperator):
    netid = ["20205"]
    name = "Vodafone Greece"
    country = "Greece"
    type = "Contract"
    smsc = "+306942190000"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20205_Prepaid(NetworkOperator):
    netid = ["20205"]
    name = "Vodafone Greece"
    country = "Greece"
    type = "Prepaid"
    smsc = "+306942190000"
    apn = "web.session"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20404_Contract(NetworkOperator):
    netid = ["20404"]
    name = "Vodafone NL"
    country = "Netherlands"
    type = "Contract"
    smsc = "+316540881000"
    apn = "office.vodafone.nl"
    username = "vodafone"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_20404_Prepaid(NetworkOperator):
    netid = ["20404"]
    name = "Vodafone NL"
    country = "Netherlands"
    type = "Prepaid"
    smsc = "+316540881000"
    apn = "office.vodafone.nl"
    username = "vodafone"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_20601_Contract(NetworkOperator):
    netid = ["20601"]
    name = "Proximus"
    country = "Belgium"
    type = "Contract"
    smsc = "+32475161616"
    apn = "internet.proximus.be"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20601_Prepaid(NetworkOperator):
    netid = ["20601"]
    name = "Proximus"
    country = "Belgium"
    type = "Prepaid"
    smsc = "+32475161616"
    apn = "internet.proximus.be"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20810_Contract(NetworkOperator):
    netid = ["20810"]
    name = "SFR"
    country = "France"
    type = "Contract"
    smsc = "+33609001390"
    apn = "websfr"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20810_SFR_slsfr(NetworkOperator):
    netid = ["20810"]
    name = "SFR"
    country = "France"
    type = "SFR slsfr"
    smsc = "+33609001390"
    apn = "slsfr"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20810_SFR_internetpro(NetworkOperator):
    netid = ["20810"]
    name = "SFR"
    country = "France"
    type = "SFR internetpro"
    smsc = "+33609001390"
    apn = "internetpro"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20810_SFR_ipnet(NetworkOperator):
    netid = ["20810"]
    name = "SFR"
    country = "France"
    type = "SFR ipnet"
    smsc = "+33609001390"
    apn = "ipnet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_20810_Prepaid(NetworkOperator):
    netid = ["20810"]
    name = "SFR"
    country = "France"
    type = "Prepaid"
    smsc = "+33609001390"
    apn = "websfr"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23801_Contract(NetworkOperator):
    netid = ["23801"]
    name = "TDC Denmark"
    country = "Denmark"
    type = "Contract"
    smsc = "+4540390999"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23801_Prepaid(NetworkOperator):
    netid = ["23801"]
    name = "TDC Denmark"
    country = "Denmark"
    type = "Prepaid"
    smsc = "+4540390999"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_2380171_Contract(NetworkOperator):
    netid = ["2380171"]
    name = "TDC Norway"
    country = "Norway"
    type = "Contract"
    smsc = "+4540390966"
    apn = "internet.no"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_2380171_Prepaid(NetworkOperator):
    netid = ["2380171"]
    name = "TDC Norway"
    country = "Norway"
    type = "Prepaid"
    smsc = "+4540390966"
    apn = "internet.no"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_2380172_Contract(NetworkOperator):
    netid = ["2380172"]
    name = "TDC Sweden"
    country = "Sweden"
    type = "Contract"
    smsc = "+4540390955"
    apn = "internet.se"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_2380172_Prepaid(NetworkOperator):
    netid = ["2380172"]
    name = "TDC Sweden"
    country = "Sweden"
    type = "Prepaid"
    smsc = "+4540390955"
    apn = "internet.se"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_24802_Contract(NetworkOperator):
    netid = ["24802"]
    name = "Elisa Estonia"
    country = "Estonia"
    type = "Contract"
    smsc = "+37256100020"
    apn = "internet"
    username = ""
    password = ""
    dns1 = "194.204.0.1"
    dns2 = None


class Vodafone_24802_Prepaid(NetworkOperator):
    netid = ["24802"]
    name = "Elisa Estonia"
    country = "Estonia"
    type = "Prepaid"
    smsc = "+37256100020"
    apn = "internet"
    username = ""
    password = ""
    dns1 = "194.204.0.1"
    dns2 = None


class Vodafone_27801_Contract(NetworkOperator):
    netid = ["27801"]
    name = "Vodafone Malta"
    country = "Malta"
    type = "Contract"
    smsc = "+356941816"
    apn = "internet"
    username = "internet"
    password = "internet"
    dns1 = "80.85.96.131"
    dns2 = "80.85.97.70"


class Vodafone_27801_Prepaid(NetworkOperator):
    netid = ["27801"]
    name = "Vodafone Malta"
    country = "Malta"
    type = "Prepaid"
    smsc = "+356941816"
    apn = "internet"
    username = "internet"
    password = "internet"
    dns1 = "80.85.96.131"
    dns2 = "80.85.97.70"


class Vodafone_50503_Contract(NetworkOperator):
    netid = ["50503"]
    name = "Vodafone Australia"
    country = "Australia"
    type = "Contract"
    smsc = "+61415011501"
    apn = "vfinternet.au"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_50503_Prepaid(NetworkOperator):
    netid = ["50503"]
    name = "Vodafone Australia"
    country = "Australia"
    type = "Prepaid"
    smsc = "+61415011501"
    apn = "vfprepaymbb"
    username = "web"
    password = "web"
    dns1 = None
    dns2 = None


class Vodafone_22210_Contract(NetworkOperator):
    netid = ["22210"]
    name = "vodafone IT"
    country = "Italy"
    type = "Contract"
    smsc = "+393492000200"
    apn = "web.omnitel.it"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_22210_Prepaid(NetworkOperator):
    netid = ["22210"]
    name = "vodafone IT"
    country = "Italy"
    type = "Prepaid"
    smsc = "+393492000200"
    apn = "web.omnitel.it"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23415_Contract(NetworkOperator):
    netid = ["23415"]
    name = "Vodafone UK"
    country = "United Kingdom"
    type = "Contract"
    smsc = "+447785016005"
    apn = "internet"
    username = "web"
    password = "web"
    dns1 = None
    dns2 = None


class Vodafone_23415_Contract_WAP(NetworkOperator):
    netid = ["23415"]
    name = "Vodafone UK"
    country = "United Kingdom"
    type = "Contract"
    smsc = "+447785016005"
    mmsc = "http://mms.vodafone.co.uk/servlets/mms"
    apn = "wap.vodafone.co.uk"
    username = "wap"
    password = "wap"
    wap2 = "212.183.137.12:8799"


class Vodafone_23415_Prepaid(NetworkOperator):
    netid = ["23415"]
    name = "Vodafone UK"
    country = "United Kingdom"
    type = "Prepaid"
    smsc = "+447785016005"
    apn = "PPBUNDLE.INTERNET"
    username = "web"
    password = "web"
    dns1 = None
    dns2 = None


class Vodafone_23415_Prepaid_WAP(NetworkOperator):
    netid = ["23415"]
    name = "Vodafone UK"
    country = "United Kingdom"
    type = "Prepaid"
    smsc = "+447785016005"
    apn = "pp.vodafone.co.uk"
    mmsc = "http://mms.vodafone.co.uk/servlets/mms"
    username = "web"
    password = "web"
    dns1 = None
    dns2 = None
    wap2 = "212.183.137.12:8799"


class Vodafone_26202_Contract(NetworkOperator):
    netid = ["26202"]
    name = "Vodafone.de"
    country = "Germany"
    type = "Contract"
    smsc = "+491722270333"
    apn = "web.vodafone.de"
    username = ""
    password = ""
    dns1 = "139.7.30.125"
    dns2 = "139.7.30.126"


class Vodafone_26202_WebSession(NetworkOperator):
    netid = ["26202"]
    name = "Vodafone.de"
    country = "Germany"
    type = "WebSession"
    smsc = "+491722270333"
    apn = "event.vodafone.de"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_26202_Corporate(NetworkOperator):
    netid = ["26202"]
    name = "Vodafone.de"
    country = "Germany"
    type = "Corporate"
    smsc = "+491722270333"
    apn = "event.vodafone.de"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_26801_Contract(NetworkOperator):
    netid = ["26801"]
    name = "vodafone P"
    country = "Portugal"
    type = "Contract"
    smsc = "+351911616161"
    apn = "internet.vodafone.pt"
    username = "vodafone"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_27201_Contract(NetworkOperator):
    netid = ["27201"]
    name = "Vodafone IE"
    country = "Ireland"
    type = "Contract"
    smsc = "+35387699989"
    apn = "hs.vodafone.ie"
    username = "vodafone"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_27201_Prepaid(NetworkOperator):
    netid = ["27201"]
    name = "Vodafone IE"
    country = "Ireland"
    type = "Prepaid"
    smsc = "+35387699989"
    apn = "hs.vodafone.ie"
    username = "vodafone"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_21401_Contract(NetworkOperator):
    netid = ["21401"]
    name = "vodafone ES"
    country = "Spain"
    type = "Contract"
    smsc = "+34607003110"
    apn = "ac.vodafone.es"
    username = "vodafone"
    password = "vodafone"
    dns1 = "212.73.32.3"
    dns2 = "212.73.32.67"


class Vodafone_21401_Prepaid(NetworkOperator):
    netid = ["21401"]
    name = "vodafone ES"
    country = "Spain"
    type = "Prepaid"
    smsc = "+34607003110"
    apn = "ac.vodafone.es"
    username = "vodafone"
    password = "vodafone"
    dns1 = "212.73.32.3"
    dns2 = "212.73.32.67"


class Vodafone_21670_Contract(NetworkOperator):
    netid = ["21670"]
    name = "Vodafone Hungary"
    country = "Hungary"
    type = "Contract"
    smsc = "+36709996500"
    apn = "internet.vodafone.net"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_21670_Prepaid(NetworkOperator):
    netid = ["21670"]
    name = "Vodafone Hungary"
    country = "Hungary"
    type = "Prepaid"
    smsc = "+36709996500"
    apn = "vitamax.internet.vodafone.net"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23201_Contract(NetworkOperator):
    netid = ["23201"]
    name = "A1"
    country = "Austria"
    type = "Contract"
    smsc = "+436640501"
    apn = "A1.net"
    username = "ppp@A1plus.at"
    password = "ppp"
    dns1 = None
    dns2 = None


class Vodafone_65501_Prepaid(NetworkOperator):
    netid = ["65501"]
    name = "Vodacom"
    country = "South Africa"
    type = "Prepaid"
    smsc = "+27829129"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_27402_Contract(NetworkOperator):
    netid = ["27402"]
    name = "Vodafone Iceland"
    country = "Iceland"
    type = "Contract"
    smsc = "+3546999099"
    apn = "vmc.gprs.is"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_27402_Prepaid(NetworkOperator):
    netid = ["27402"]
    name = "Vodafone Iceland"
    country = "Iceland"
    type = "Prepaid"
    smsc = "+3546999099"
    apn = "vmc.gprs.is"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_45406_Contract(NetworkOperator):
    netid = ["45406"]
    name = "SmarTone-Vodafone"
    country = "Hong Kong"
    type = "Contract"
    smsc = "+85290100000"
    apn = "Internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_42602_Contract(NetworkOperator):
    netid = ["42602"]
    name = "Zain BH"
    country = "Bahrain"
    type = "Contract"
    smsc = "+97336135135"
    apn = "internet"
    username = "internet"
    password = "internet"
    dns1 = None
    dns2 = None


class Vodafone_42602_Prepaid(NetworkOperator):
    netid = ["42602"]
    name = "Zain BH"
    country = "Bahrain"
    type = "Prepaid"
    smsc = "+97336135135"
    apn = "internet"
    username = "internet"
    password = "internet"
    dns1 = None
    dns2 = None


class Vodafone_21910_Contract(NetworkOperator):
    netid = ["21910"]
    name = "Vipnet"
    country = "Croatia"
    type = "Contract"
    smsc = "+385910401"
    apn = "data.vip.hr"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_21910_Prepaid(NetworkOperator):
    netid = ["21910"]
    name = "Vipnet"
    country = "Croatia"
    type = "Prepaid"
    smsc = "+385910401"
    apn = "data.vip.hr"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_24405_Contract(NetworkOperator):
    netid = ["24405"]
    name = "Elisa"
    country = "Finland"
    type = "Contract"
    smsc = "+358508771010"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_24405_Prepaid(NetworkOperator):
    netid = ["24405"]
    name = "Elisa"
    country = "Finland"
    type = "Prepaid"
    smsc = "+358508771010"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_29340_Contract(NetworkOperator):
    netid = ["29340"]
    name = "Si.mobil"
    country = "Slovenia"
    type = "Contract"
    smsc = "+38640441000"
    apn = "internet.simobil.si"
    username = "simobil"
    password = "internet"
    dns1 = None
    dns2 = None


class Vodafone_29340_Prepaid(NetworkOperator):
    netid = ["29340"]
    name = "Si.mobil"
    country = "Slovenia"
    type = "Prepaid"
    smsc = "+38640441000"
    apn = "internet.simobil.si"
    username = "simobil"
    password = "internet"
    dns1 = None
    dns2 = None


class Vodafone_53001_Contract(NetworkOperator):
    netid = ["53001"]
    name = "Vodafone NZ"
    country = "New Zealand"
    type = "Contract"
    smsc = "+6421600600"
    apn = "www.vodafone.net.nz"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_53001_Prepaid(NetworkOperator):
    netid = ["53001"]
    name = "Vodafone NZ"
    country = "New Zealand"
    type = "Prepaid"
    smsc = "+6421600600"
    apn = "www.vodafone.net.nz"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_60202_Contract(NetworkOperator):
    netid = ["60202"]
    name = "Vodafone Egypt"
    country = "Egypt"
    type = "Contract"
    smsc = "+20105996500"
    apn = "internet.vodafone.net"
    username = "internet"
    password = "internet"
    dns1 = "163.121.128.134"
    dns2 = "212.103.160.18"


class Vodafone_60202_Prepaid(NetworkOperator):
    netid = ["60202"]
    name = "Vodafone Egypt"
    country = "Egypt"
    type = "Prepaid"
    smsc = "+20105996500"
    apn = "internet.vodafone.net"
    username = "internet"
    password = "internet"
    dns1 = "163.121.128.134"
    dns2 = "212.103.160.18"


class Vodafone_54201_Contract(NetworkOperator):
    netid = ["54201"]
    name = "Vodafone Fiji"
    country = "Fiji"
    type = "Contract"
    smsc = "+679901400"
    apn = "vfinternet.fj"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_54201_Prepaid(NetworkOperator):
    netid = ["54201"]
    name = "Vodafone Fiji"
    country = "Fiji"
    type = "Prepaid"
    smsc = "+679901400"
    apn = "prepay.vfinternet.fj"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_28001_Contract(NetworkOperator):
    netid = ["28001"]
    name = "Cytamobile-Vodafone"
    country = "Cyprus"
    type = "Contract"
    smsc = "+35799700000"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_28001_Prepaid(NetworkOperator):
    netid = ["28001"]
    name = "Cytamobile-Vodafone"
    country = "Cyprus"
    type = "Prepaid"
    smsc = "+35799700000"
    apn = "pp.internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_22601_Contract(NetworkOperator):
    netid = ["22601"]
    name = "Vodafone RO"
    country = "Romania"
    type = "Contract"
    smsc = "+40722004000"
    apn = "internet.vodafone.ro"
    username = "internet.vodafone.ro"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_22601_Prepaid(NetworkOperator):
    netid = ["22601"]
    name = "Vodafone RO"
    country = "Romania"
    type = "Prepaid"
    smsc = "+40722004000"
    apn = "internet.vodafone.ro"
    username = "internet.vodafone.ro"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_52503_Contract(NetworkOperator):
    netid = ["52503"]
    name = "MobileOne"
    country = "Singapore"
    type = "Contract"
    smsc = "+6596845999"
    apn = "sunsurf"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_52503_Prepaid(NetworkOperator):
    netid = ["52503"]
    name = "MobileOne"
    country = "Singapore"
    type = "Prepaid"
    smsc = "+6596845999"
    apn = "prepaidbb"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_27602_Contract(NetworkOperator):
    netid = ["27602"]
    name = "Vodafone Albania"
    country = "Albania"
    type = "Contract"
    smsc = "+355692000200"
    apn = "vodafoneweb"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_27602_Prepaid(NetworkOperator):
    netid = ["27602"]
    name = "Vodafone Albania"
    country = "Albania"
    type = "Prepaid"
    smsc = "+355692000200"
    apn = "vodafoneweb"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23003_Contract(NetworkOperator):
    netid = ["23003"]
    name = "Vodafone CZ"
    country = "Czech Republic"
    type = "Contract"
    smsc = "+420608005681"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23003_Prepaid(NetworkOperator):
    netid = ["23003"]
    name = "Vodafone CZ"
    country = "Czech Republic"
    type = "Prepaid"
    smsc = "+420608005681"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23003_Corporate(NetworkOperator):
    netid = ["23003"]
    name = "Vodafone CZ"
    country = "Czech Republic"
    type = "Corporate"
    smsc = "+420608005681"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_28401_Contract(NetworkOperator):
    netid = ["28401"]
    name = "M-Tel BG"
    country = "Bulgaria"
    type = "Contract"
    smsc = "+35988000301"
    apn = "inet-gprs.mtel.bg"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_28401_Prepaid(NetworkOperator):
    netid = ["28401"]
    name = "M-Tel BG"
    country = "Bulgaria"
    type = "Prepaid"
    smsc = "+35988000301"
    apn = "inet-gprs.mtel.bg"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_24705_Contract(NetworkOperator):
    netid = ["24705"]
    name = "Bite Latvija"
    country = "Latvia"
    type = "Contract"
    smsc = "+37125850115"
    apn = "Internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_24705_Prepaid(NetworkOperator):
    netid = ["24705"]
    name = "Bite Latvija"
    country = "Latvia"
    type = "Prepaid"
    smsc = "+37125850115"
    apn = "Internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_24602_Contract(NetworkOperator):
    netid = ["24602"]
    name = "Bite Lietuva"
    country = "Lithuania"
    type = "Contract"
    smsc = "+37069950115"
    apn = "banga"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_24602_Prepaid(NetworkOperator):
    netid = ["24602"]
    name = "Bite Lietuva"
    country = "Lithuania"
    type = "Prepaid"
    smsc = "+37069950115"
    apn = "banga"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_50219_Contract(NetworkOperator):
    netid = ["50219"]
    name = "Celcom Malaysia"
    country = "Malaysia"
    type = "Contract"
    smsc = "+60193900000"
    apn = "celcom3g"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_50219_Prepaid(NetworkOperator):
    netid = ["50219"]
    name = "Celcom Malaysia"
    country = "Malaysia"
    type = "Prepaid"
    smsc = "+60193900000"
    apn = "celcom3g"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_41302_Contract(NetworkOperator):
    netid = ["41302"]
    name = "DIALOG"
    country = "Sri Lanka"
    type = "Contract"
    smsc = "+9477000003"
    apn = "Dialogbb"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_41302_Prepaid(NetworkOperator):
    netid = ["41302"]
    name = "DIALOG"
    country = "Sri Lanka"
    type = "Prepaid"
    smsc = "+9477000003"
    apn = "kitbb.com"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_22801_Contract(NetworkOperator):
    netid = ["22801"]
    name = "Swisscom"
    country = "Switzerland"
    type = "Contract"
    smsc = "+417949990000"
    apn = "gprs.swisscom.ch"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_22801_Prepaid(NetworkOperator):
    netid = ["22801"]
    name = "Swisscom"
    country = "Switzerland"
    type = "Prepaid"
    smsc = "+417949990000"
    apn = "gprs.swisscom.ch"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_28602_Faturali(NetworkOperator):
    netid = ["28602"]
    name = "Vodafone TR"
    country = "Turkey"
    type = "Faturali"
    smsc = "+905429800033"
    apn = "internet"
    username = "vodafone"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_28602_Kontorlu(NetworkOperator):
    netid = ["28602"]
    name = "Vodafone TR"
    country = "Turkey"
    type = "Kontorlu"
    smsc = "+905429800033"
    apn = "internet"
    username = "vodafone"
    password = "vodafone"
    dns1 = None
    dns2 = None


class Vodafone_23403_Contract(NetworkOperator):
    netid = ["23403"]
    name = "Airtel-Vodafone"
    country = "Jersey"
    type = "Contract"
    smsc = "+447829791004"
    apn = "airtel-ci-gprs.com"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_23403_Prepaid(NetworkOperator):
    netid = ["23403"]
    name = "Airtel-Vodafone"
    country = "Jersey"
    type = "Prepaid"
    smsc = "+447829791004"
    apn = "airtel-ci-gprs.com"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_73001_Contract(NetworkOperator):
    netid = ["73001"]
    name = "Entel PCS"
    country = "Chile"
    type = "Contract"
    smsc = "+5698890005"
    apn = "imovil.entelpcs.cl"
    username = "entelpcs"
    password = "entelpcs"
    dns1 = None
    dns2 = None


class Vodafone_73001_Prepaid(NetworkOperator):
    netid = ["73001"]
    name = "Entel PCS"
    country = "Chile"
    type = "Prepaid"
    smsc = "+5698890005"
    apn = "imovil.entelpcs.cl"
    username = "entelpcs"
    password = "entelpcs"
    dns1 = None
    dns2 = None


class Vodafone_73001_WebSession(NetworkOperator):
    netid = ["73001"]
    name = "Entel PCS"
    country = "Chile"
    type = "WebSession"
    smsc = "+5698890005"
    apn = "imovil.entelpcs.cl"
    username = "entelpcs"
    password = "entelpcs"
    dns1 = None
    dns2 = None


class Vodafone_73001_Corporate(NetworkOperator):
    netid = ["73001"]
    name = "Entel PCS"
    country = "Chile"
    type = "Corporate"
    smsc = "+5698890005"
    apn = "imovil.entelpcs.cl"
    username = "entelpcs"
    password = "entelpcs"
    dns1 = None
    dns2 = None


class Vodafone_62002_Contract(NetworkOperator):
    netid = ["62002"]
    name = "Vodafone Ghana"
    country = "Ghana"
    type = "Contract"
    smsc = "+233200000007"
    apn = "browse"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_62002_Prepaid(NetworkOperator):
    netid = ["62002"]
    name = "Vodafone Ghana"
    country = "Ghana"
    type = "Prepaid"
    smsc = "+233200000007"
    apn = "browse"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_65101_Contract(NetworkOperator):
    netid = ["65101"]
    name = "Vodacom Lesotho"
    country = "Lesotho"
    type = "Contract"
    smsc = "+26655820088"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_65101_Prepaid(NetworkOperator):
    netid = ["65101"]
    name = "Vodacom Lesotho"
    country = "Lesotho"
    type = "Prepaid"
    smsc = "+26655820088"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_28802_Contract(NetworkOperator):
    netid = ["28802"]
    name = "Vodafone FO"
    country = "Faroe Islands"
    type = "Contract"
    smsc = "+298501440"
    apn = "vmc.vodafone.fo"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_42702_Contract(NetworkOperator):
    netid = ["42702"]
    name = "Vodafone Qatar"
    country = "Qatar"
    type = "Contract"
    smsc = "+9747922222"
    apn = "web.vodafone.com.qa"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_64004_Contract(NetworkOperator):
    netid = ["64004"]
    name = "Vodacom Tanzania"
    country = "Tanzania"
    type = "Contract"
    smsc = "+25575114"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_64004_Prepaid(NetworkOperator):
    netid = ["64004"]
    name = "Vodacom Tanzania"
    country = "Tanzania"
    type = "Prepaid"
    smsc = "+25575114"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_64304_Contract(NetworkOperator):
    netid = ["64304"]
    name = "Vodacom Mozambique"
    country = "Mozambique"
    type = "Contract"
    smsc = "+25884080011"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_64304_Prepaid(NetworkOperator):
    netid = ["64304"]
    name = "Vodacom Mozambique"
    country = "Mozambique"
    type = "Prepaid"
    smsc = "+25884080011"
    apn = "internet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40401_Contract(NetworkOperator):
    netid = ["40401"]
    name = "Vodafone India Haryana"
    country = "India"
    type = "Contract"
    smsc = "+919839099999"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40401_Prepaid(NetworkOperator):
    netid = ["40401"]
    name = "Vodafone India Haryana"
    country = "India"
    type = "Prepaid"
    smsc = "+919839099999"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40405_Contract(NetworkOperator):
    netid = ["40405"]
    name = "Vodafone India Gujarat"
    country = "India"
    type = "Contract"
    smsc = "+919825001002"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40405_Prepaid(NetworkOperator):
    netid = ["40405"]
    name = "Vodafone India Gujarat"
    country = "India"
    type = "Prepaid"
    smsc = "+919825001002"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40411_Contract(NetworkOperator):
    netid = ["40411"]
    name = "Vodafone India Delhi"
    country = "India"
    type = "Contract"
    smsc = "+919811009998"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40411_Prepaid(NetworkOperator):
    netid = ["40411"]
    name = "Vodafone India Delhi"
    country = "India"
    type = "Prepaid"
    smsc = "+919811009998"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40413_Contract(NetworkOperator):
    netid = ["40413"]
    name = "Vodafone India Andhra Pradesh"
    country = "India"
    type = "Contract"
    smsc = "+919885005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40413_Prepaid(NetworkOperator):
    netid = ["40413"]
    name = "Vodafone India Andhra Pradesh"
    country = "India"
    type = "Prepaid"
    smsc = "+919885005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40415_Contract(NetworkOperator):
    netid = ["40415"]
    name = "Vodafone India UP East"
    country = "India"
    type = "Contract"
    smsc = "+919839099999"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40415_Prepaid(NetworkOperator):
    netid = ["40415"]
    name = "Vodafone India UP East"
    country = "India"
    type = "Prepaid"
    smsc = "+919839099999"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40420_Contract(NetworkOperator):
    netid = ["40420"]
    name = "Vodafone India Mumbai"
    country = "India"
    type = "Contract"
    smsc = "+919820005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40420_Prepaid(NetworkOperator):
    netid = ["40420"]
    name = "Vodafone India Mumbai"
    country = "India"
    type = "Prepaid"
    smsc = "+919820005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40427_Contract(NetworkOperator):
    netid = ["40427"]
    name = "Vodafone India Maharashtra and Goa"
    country = "India"
    type = "Contract"
    smsc = "+919823000040"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40427_Prepaid(NetworkOperator):
    netid = ["40427"]
    name = "Vodafone India Maharashtra and Goa"
    country = "India"
    type = "Prepaid"
    smsc = "+919823000040"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40430_Contract(NetworkOperator):
    netid = ["40430"]
    name = "Vodafone India Kolkata"
    country = "India"
    type = "Contract"
    smsc = "+919830099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40430_Prepaid(NetworkOperator):
    netid = ["40430"]
    name = "Vodafone India Kolkata"
    country = "India"
    type = "Prepaid"
    smsc = "+919830099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40443_Contract(NetworkOperator):
    netid = ["40443"]
    name = "Vodafone India Tamilnadu"
    country = "India"
    type = "Contract"
    smsc = "+919843000040"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40443_Prepaid(NetworkOperator):
    netid = ["40443"]
    name = "Vodafone India Tamilnadu"
    country = "India"
    type = "Prepaid"
    smsc = "+919843000040"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40446_Contract(NetworkOperator):
    netid = ["40446"]
    name = "Vodafone India Kerala"
    country = "India"
    type = "Contract"
    smsc = "+919846000040"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40446_Prepaid(NetworkOperator):
    netid = ["40446"]
    name = "Vodafone India Kerala"
    country = "India"
    type = "Prepaid"
    smsc = "+919846000040"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40460_Contract(NetworkOperator):
    netid = ["40460"]
    name = "Vodafone India Rajasthan"
    country = "India"
    type = "Contract"
    smsc = "+919839099999"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40460_Prepaid(NetworkOperator):
    netid = ["40460"]
    name = "Vodafone India Rajasthan"
    country = "India"
    type = "Prepaid"
    smsc = "+919839099999"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40484_Contract(NetworkOperator):
    netid = ["40484"]
    name = "Vodafone India Chennai"
    country = "India"
    type = "Contract"
    smsc = "+919884005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40484_Prepaid(NetworkOperator):
    netid = ["40484"]
    name = "Vodafone India Chennai"
    country = "India"
    type = "Prepaid"
    smsc = "+919884005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40486_Contract(NetworkOperator):
    netid = ["40486"]
    name = "Vodafone India Karnataka"
    country = "India"
    type = "Contract"
    smsc = "+919886005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40486_Prepaid(NetworkOperator):
    netid = ["40486"]
    name = "Vodafone India Karnataka"
    country = "India"
    type = "Prepaid"
    smsc = "+919886005444"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40488_Contract(NetworkOperator):
    netid = ["40488"]
    name = "Vodafone India Punjab"
    country = "India"
    type = "Contract"
    smsc = "+919888009998"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40488_Prepaid(NetworkOperator):
    netid = ["40488"]
    name = "Vodafone India Punjab"
    country = "India"
    type = "Prepaid"
    smsc = "+919888009998"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40566_Contract(NetworkOperator):
    netid = ["40566"]
    name = "Vodafone India UP West"
    country = "India"
    type = "Contract"
    smsc = "+919719009998"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40566_Prepaid(NetworkOperator):
    netid = ["40566"]
    name = "Vodafone India UP West"
    country = "India"
    type = "Prepaid"
    smsc = "+919719009998"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40567_Contract(NetworkOperator):
    netid = ["40567"]
    name = "Vodafone India West Bengal"
    country = "India"
    type = "Contract"
    smsc = "+919732099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40567_Prepaid(NetworkOperator):
    netid = ["40567"]
    name = "Vodafone India West Bengal"
    country = "India"
    type = "Prepaid"
    smsc = "+919732099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405750_Contract(NetworkOperator):
    netid = ["405750"]
    name = "Vodafone India Jammu and Kasmir"
    country = "India"
    type = "Contract"
    smsc = "+919796009905"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405750_Prepaid(NetworkOperator):
    netid = ["405750"]
    name = "Vodafone India Jammu and Kasmir"
    country = "India"
    type = "Prepaid"
    smsc = "+919796009905"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405751_Contract(NetworkOperator):
    netid = ["405751"]
    name = "Vodafone India Assam"
    country = "India"
    type = "Contract"
    smsc = "+919706099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405751_Prepaid(NetworkOperator):
    netid = ["405751"]
    name = "Vodafone India Assam"
    country = "India"
    type = "Prepaid"
    smsc = "+919706099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405752_Contract(NetworkOperator):
    netid = ["405752"]
    name = "Vodafone India Bihar"
    country = "India"
    type = "Contract"
    smsc = "+919709099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405752_Prepaid(NetworkOperator):
    netid = ["405752"]
    name = "Vodafone India Bihar"
    country = "India"
    type = "Prepaid"
    smsc = "+919709099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405753_Contract(NetworkOperator):
    netid = ["405753"]
    name = "Vodafone India Orissa"
    country = "India"
    type = "Contract"
    smsc = "+919776099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405753_Prepaid(NetworkOperator):
    netid = ["405753"]
    name = "Vodafone India Orissa"
    country = "India"
    type = "Prepaid"
    smsc = "+919776099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405754_Contract(NetworkOperator):
    netid = ["405754"]
    name = "Vodafone India Himachal Pradesh"
    country = "India"
    type = "Contract"
    smsc = "+919796009905"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405754_Prepaid(NetworkOperator):
    netid = ["405754"]
    name = "Vodafone India Himachal Pradesh"
    country = "India"
    type = "Prepaid"
    smsc = "+919796009905"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405755_Contract(NetworkOperator):
    netid = ["405755"]
    name = "Vodafone India North East"
    country = "India"
    type = "Contract"
    smsc = "+919774099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405755_Prepaid(NetworkOperator):
    netid = ["405755"]
    name = "Vodafone India North East"
    country = "India"
    type = "Prepaid"
    smsc = "+919774099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405756_Contract(NetworkOperator):
    netid = ["405756"]
    name = "Vodafone India Madhya Pradesh"
    country = "India"
    type = "Contract"
    smsc = "+919713099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_405756_Prepaid(NetworkOperator):
    netid = ["405756"]
    name = "Vodafone India Madhya Pradesh"
    country = "India"
    type = "Prepaid"
    smsc = "+919713099990"
    apn = "www"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_42403_Contract(NetworkOperator):
    netid = ["42403"]
    name = "du EITC"
    country = "Dubai"
    type = "Contract"
    smsc = "+971555515515"
    apn = "du"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_42403_Prepaid(NetworkOperator):
    netid = ["42403"]
    name = "du EITC"
    country = "Dubai"
    type = "Prepaid"
    smsc = "+971555515515"
    apn = "du"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_64710_Contract(NetworkOperator):
    netid = ["64710"]
    name = "SRR"
    country = "Reunion"
    type = "Contract"
    smsc = "+262850909"
    apn = "websfr"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_27077_Contract(NetworkOperator):
    netid = ["27077"]
    name = "Tango"
    country = "Luxembourg"
    type = "Contract"
    smsc = "+352091000030"
    apn = "hspa"
    username = "tango"
    password = "tango"
    dns1 = None
    dns2 = None


class Vodafone_27077_Prepaid(NetworkOperator):
    netid = ["27077"]
    name = "Tango"
    country = "Luxembourg"
    type = "Prepaid"
    smsc = "+352091000030"
    apn = "hspa"
    username = "tango"
    password = "tango"
    dns1 = None
    dns2 = None


class Vodafone_40004_Contract(NetworkOperator):
    netid = ["40004"]
    name = "Azerfon"
    country = "Azerbaijan"
    type = "Contract"
    smsc = "+994702000700"
    apn = "Azerfon"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_40004_Prepaid(NetworkOperator):
    netid = ["40004"]
    name = "Azerfon"
    country = "Azerbaijan"
    type = "Prepaid"
    smsc = "+994702000700"
    apn = "Azerfon"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_63001_Contract(NetworkOperator):
    netid = ["63001"]
    name = "Vodacom Congo"
    country = "Congo (DRC)"
    type = "Contract"
    smsc = "0811030"
    apn = "vodanet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None


class Vodafone_63001_Prepaid(NetworkOperator):
    netid = ["63001"]
    name = "Vodacom Congo"
    country = "Congo (DRC)"
    type = "Prepaid"
    smsc = "0811030"
    apn = "vodanet"
    username = ""
    password = ""
    dns1 = None
    dns2 = None
