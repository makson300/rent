import requests  
r=requests.post('https://api.telegram.org/bot8670983320:AAHqvLcDqR_10vh_HywE0I_5S6mPkMJ4wYc/setChatMenuButton', proxies={'http':'http://127.0.0.1:10809','https':'http://127.0.0.1:10809'}, json={'menu_button':{'type':'web_app', 'text':'SkyRent', 'web_app':{'url':'https://skyrent.pro'}}})  
print(r.text)  
