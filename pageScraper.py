from time import sleep
from random import randint
import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import sys 
   
userGenres = sys.argv[1:] 
userGenres = [x.lower() for x in userGenres]
     
headers = {"Accept-Language": "en-US,en;q=0.5"}

titles = []
years = []
time = []
imdb_ratings = []
metascores = []
genres = []
us_gross = []
pages = np.arange(1, 1001, 50)
print(userGenres)
for page in pages: 
  page = requests.get("https://www.imdb.com/search/title/?groups=top_1000&start=" + str(page) + "&ref_=adv_nxt", headers=headers)
  soup = BeautifulSoup(page.text, 'html.parser')
  movie_div = soup.find_all('div', class_='lister-item mode-advanced')
  sleep(0.1*randint(1,5))

  for container in movie_div:
    genre = set(container.find('span', class_='genre').text[1:].lower().rstrip().split(", "))
    if set(userGenres).issubset(genre) or userGenres==[]:
      name = container.h3.a.text
      titles.append(name)
      year = container.h3.find('span', class_='lister-item-year').text
      years.append(year)
      runtime = container.p.find('span', class_='runtime') if container.p.find('span', class_='runtime') else ''
      time.append(runtime)
      imdb = float(container.strong.text)
      imdb_ratings.append(imdb)
      m_score = container.find('span', class_='metascore').text if container.find('span', class_='metascore') else ''
      metascores.append(m_score)
      nv = container.find_all('span', attrs={'name': 'nv'})
      genres.append(' '.join(genre))
      grosses = nv[1].text if len(nv) > 1 else ''
      us_gross.append(grosses)

movies = pd.DataFrame({
'movie': titles,
'year': years,
'imdb': imdb_ratings,
'metascore': metascores,
'genres': genres,
'us_grossMillions': us_gross,
'timeMin': time
})

movies['timeMin'] = movies['timeMin'].astype(str)
movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int)
movies['metascore'] = movies['metascore'].astype(str)
movies['metascore'] = movies['metascore'].str.extract('(\d+)')
movies['metascore'] = pd.to_numeric(movies['metascore'], errors='coerce')
movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')

#scraped data moved to a CSV file
print(movies)
movies.to_csv('movies.csv')