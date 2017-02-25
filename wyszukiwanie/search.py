#!/usr/bin/python3
# -*- coding: utf-8 -*-

from googleapiclient.discovery import build
import psycopg2

#dane google
my_api_key = " AIzaSyBuNrMgksTEOHdsQE3Ee5Nig2XvSBDPf3w"
my_cse_id = "001503415831128023061:hl1dprcnp8k"

#dane do bazy danych
db="postgres"
dbuser="postgres"
dbpass="postgres"
dbhost="localhost"
dbport="5432"

szukaj = input('Wpisz frazę, która cię interesuje?\n')

#wyszukiwanie w google
def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    return res['items']
#funkcja do bazy danych   
def baza(szukany,db,dbuser,dbpass,dbhost,dbport):
    poprawnie = 1
    szukany = szukany.lower()
    try:
        conn = psycopg2.connect(database=db, user=dbuser, password=dbpass, host=dbhost, port=dbport)
        cur = conn.cursor()
    except:
      print ("\n--------Nie można połączyć się z bazą danych.--------\n")
      poprawnie = 0
      
    if (poprawnie == 1):  
    
        try:
          cur.execute("CREATE TABLE IF NOT EXISTS public.szukane(id int not null,fraza char(150) not null,wystapienia int not null);")
        except:
          print ("\nNie mogę stworzyć tabeli\n")
          poprawnie = 0
          
        try:
          cur.execute("select wystapienia from public.szukane where fraza= '"+ szukany+"';")
          wystapienia_row = cur.fetchall()
          
          if (len(wystapienia_row)!= 0):
            wystapienia = wystapienia_row[0][0]
            wystapienia += 1
            cur.execute("update public.szukane set wystapienia='"+str(wystapienia)+"' where fraza = '"+ szukany+"';")
          else:
            cur.execute("select id from public.szukane order by id desc limit 1;")
            id_row = cur.fetchall()
            if (len(id_row)!= 0):
                id = id_row[0][0]
            else:
                id = 0
            id+=1
            cur.execute("insert into public.szukane(id,fraza,wystapienia) values ("+str(id)+",'"+szukany+"', '1');")
                           
        except:
          poprawnie = 0
          print ("\n--------Nie dodano frazy--------\n")
       
        try:
            conn.commit()
            cur.close()
            conn.close()
        except:
            print ("\nNie mogę zamknąć bazy.\n")
            poprawnie = 0
            
    if(poprawnie == 1):
        print("\nFraza zapisana w bazie.\n")
#Zastępuje inaczej kodowane znaki
def inneKodowanie(fraza):
    lf = len(str(fraza.encode('ascii', 'replace')))
    fr = str(fraza.encode('ascii', 'replace'))[2:lf-1]
    return fr  

    
baza(szukaj,db,dbuser,dbpass,dbhost,dbport)

#jeśli osiągnieto limit wyszukiwań
try:
    results = google_search(szukaj, my_api_key, my_cse_id, num=10)    
except:
    results = []
    print("\n--------Przepraszamy, nie możemy wyszukać twojej frazy.--------\n")
    
if(results):
    for result in results:
        try:           
            print('Tytuł: '+result['title']+'\nStrona: '+result['link']+'\n\n')
        except:
            print('Tytuł: '+inneKodowanie(result['title'])+'\nStrona: '+inneKodowanie(result['link'])+'\n\n')
    
print  ("\n Copyright Łukasz Grześkowiak ")