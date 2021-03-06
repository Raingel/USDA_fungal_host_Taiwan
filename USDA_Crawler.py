# %%
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import string
from datetime import datetime
# %%
ROOT='./'

# %%
def USDA_fetch(HostGenus = '', HostSpecies = '', FungusGenus = 'Sa*', FungusSpecies = ''):
    headers = {
     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    df = pd.DataFrame(columns=['host', 'pathogen'])
    rs = requests.Session()
    Search_form = rs.get('https://nt.ars-grin.gov/fungaldatabases/fungushost/fungushost.cfm',headers=headers)
    payload = {
        'FungusGenus':FungusGenus,
        'FungusSpecies':FungusSpecies,
        'fieldsSelected':'2',
        'FungusGroup':'',
        'fungusOrder':'',
        'HostGenus':HostGenus,
        'HostSpecies':HostSpecies,
        'HostFamily':'',
        'Locality':'Taiwan',
        'Regions':'',
        'DisplayOrder':'Host-Fungus',
        'email':'',
        'emailradio':'comma',
        'Submit':'Search'
            }
    # 將查詢參數加入 POST 請求中
    Submit_search = rs.post("https://nt.ars-grin.gov/fungaldatabases/fungushost/new_frameFungusHostReport.cfm", data=payload, headers=headers)
    try:
        result = rs.get("https://nt.ars-grin.gov/fungaldatabases/fungushost/new_rptFungusHost.cfm", headers=headers)
        content_list = result.text.split('\n')
        for line in content_list:
            host = re.findall(r'MainHeading \'>(.*):.*',line)
            pathogen = re.findall(r'<p class=\'Hanging \'>(.*?)Taiwan(.*?)</a>,</p>',line)
            if pathogen != []:
                for pathogen_name in pathogen:
                    refs = re.findall(r'displayLit\(\'([0-9]*)\',\'fungushost', pathogen_name[1])
                    ref_link = ["https://nt.ars-grin.gov/fungaldatabases/fungushost/new_rptOneLit.cfm?fungRec={}&thisError".format(r) for r in refs]
                    pathogen_name_cln=pathogen_name[0].replace(':','')              
                    df = pd.concat([df,pd.DataFrame([{'host':now_host[0],'pathogen':pathogen_name_cln, 'ref':"\n".join(ref_link)}])])
            if host:
                now_host = host
    except Exception as e:
        print (e)
    return df



# %%
a_z = string.ascii_lowercase


# %%
df = pd.DataFrame()
for FungusGenus in a_z:
    for FungusSpecies in a_z: 
        for i in range(0,5):
            try:
                dfOutput = USDA_fetch(FungusGenus=FungusGenus+"*", FungusSpecies=FungusSpecies+"*")
                df = pd.concat([df, dfOutput])
                print (FungusGenus, FungusSpecies, len(df))
                break
            except Exception as e:
                print (FungusGenus, FungusSpecies, e)



# %%
df.to_csv('./data/USDA_Taiwan.csv', index = False)
df.to_csv('./data/USDA_Taiwan_{}.csv'.format(datetime.today().strftime("%Y-%m-%d")), index = False)



