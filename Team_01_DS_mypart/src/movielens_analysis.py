import csv
from collections import Counter,defaultdict, OrderedDict
import requests
from bs4 import BeautifulSoup
import time, json, os, re, pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import statistics
import numpy

class Movies:
    """
    Analyzing data from movies.csv
    """

    def __init__(self, path_to_the_file):
        """
        Put here any fields that you think you will need.
        """  
        self.path = path_to_the_file
        self.data = [] 
        try:
            with open(self.path, 'r') as file:
                next(file) 
                count = 0
                for line in file:
                    if count >= 1000:
                        break
                    self.data.append(line.strip())
                    count += 1
        except FileNotFoundError:
            print(f"File not found at {self.path}")
            self.data = []

    def dist_by_release(self):
        """
        The method returns a dict or an OrderedDict where the keys are years and the values are counts. 
        You need to extract years from the titles. Sort it by counts descendingly.
        """
        dictYears = {}
        for line in self.data:
            year = re.findall(r'\((\d{4})\)', str(line))
            if year:
                intYear = int(year[0])
                dictYears[intYear] = dictYears.get(intYear, 0) + 1
        release_years = dict(
            sorted(dictYears.items(), key=lambda item: item[1], reverse=True)
        )
        return release_years

    def dist_by_genres(self):
        """
        The method returns a dict where the keys are genres and the values are counts.
     Sort it by counts descendingly.
        """
        genres = Counter()
        for line in self.data:
            parts = line.split(",")
            genres_str = parts[-1]
            for g in genres_str.split("|"):
                genres[g] += 1
        genres = dict(sorted(genres.items(), key=lambda item: item[1], reverse=True))
        return genres

    def most_genres(self, n: int):
        """
        The method returns a dict with top-n movies where the keys are movie titles and 
        the values are the number of genres of the movie. Sort it by numbers descendingly.
        """
        movies = {}
        for line in self.data:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",", 2)
            if len(parts) < 3:
                continue

            movie_id, title, genres_str = parts
            genres_count = len(genres_str.split("|"))
            movies[title] = genres_count

            movies = dict(sorted(movies.items(), key=lambda x: x[1], reverse=True)[:n])
            return movies



    def movies_in_genre(self, genre: str, n: int):
        """
        Returns top-n movies for the given genre, sorted by number of genres.
        """
        result = {}
        for line in self.data:
            line = line.strip()
            if not line:
                continue

            parts = line.split(",", 2)
            if len(parts) < 3:
                continue 

            movie_id, title, genres_str = parts
            genres_list = [g.strip() for g in genres_str.split("|")]

            if genre in genres_list:
                result[title] = len(genres_list) 

        top_movies = dict(sorted(result.items(), key=lambda x: x[1], reverse=True)[:n])
        return top_movies
    

def average(rating)->float:
    return sum(rating)/len(rating)
def median(rating)->float:
    sorted_data = sorted(rating)
    mid = len(sorted_data) // 2

    return (sorted_data[mid - 1] + sorted_data[mid]) / 2 if len(sorted_data) % 2 == 0 else sorted_data[mid]
class Rating(object):
    def __init__(self,file_path:str):
        self.file_path = file_path
        self.mass = []
    def read_file(self):
        try:
            with open(file=self.file_path,mode="r") as r:
                for line in r:
                    self.mass.append(line.strip().split(','))
        except FileNotFoundError as err1:
            print(err1)
        except FileExistsError as err2:
            print(err2)
        
    class Movies(object):
        def __init__(self,ratings:list):
            self.ratings = ratings
        def dist_by_year(self)->dict:
            dict_year = dict()
            try:
                self.ratings = [[user_id,movie_id,rating,datetime.fromtimestamp(int(timestamp)).year] for user_id,movie_id,rating,timestamp in self.ratings[1:]]
                dict_year = Counter(i[3] for i in self.ratings)
            except Exception as err:
                print(err)
            return dict(sorted(dict_year.items()))
        
        def dist_by_rating(self)->dict:
            try:
                dict_rating = dict()
                dict_rating = dict(sorted(Counter(i[2] for i in self.ratings[1:]).items(),key=lambda x: x[1]))
            except Exception as err:
                print(err)
            return dict_rating
        
        def top_by_num_of_ratings(self, n:int)->dict:
            try:
                top_n_dict = dict()
                top_n_dict = dict(sorted(Counter(i[1] for i in self.ratings).items(),key=lambda x : x[1],reverse=True)[:n])
            except Exception as err:
                print(err)
            return top_n_dict
        
        def top_by_ratings(self, n: int, metric='average') -> dict:
            
            ratings_dict = defaultdict(list)

            for user_id, movie_id, rating, _ in self.ratings[1:]:
                ratings_dict[movie_id].append(float(rating))

            if metric == 'average':
                top_movies = {movie_id: round(statistics.mean(ratings), 2) for movie_id, ratings in ratings_dict.items()}
            elif metric == 'median':
                top_movies = {movie_id: round(statistics.median(ratings), 2) for movie_id, ratings in ratings_dict.items()}
            else:
                raise ValueError("Metric must be 'average' or 'median'.")

            return dict(sorted(top_movies.items(), key=lambda x: x[1], reverse=True)[:n])


        

        def top_controversial(self, n: int) -> dict:
           
            ratings_dict = defaultdict(list)

            
            for user_id, movie_id, rating, _ in self.ratings[1:]:
                ratings_dict[movie_id].append(float(rating))

            variances = {movie_id: round(numpy.var(ratings), 2) for movie_id, ratings in ratings_dict.items()}
            return dict(sorted(variances.items(), key=lambda x: x[1], reverse=True)[:n])

        
    class Users(Movies):
        def __init__(self, ratings_data):
            self.ratings = ratings_data
        def dist_num_rat(self)->dict:
            try:
                dict_rating = dict()
                dict_rating = dict(sorted(Counter(i[1] for i in self.ratings[1:]).items(),key= lambda x: x[0]))
            except Exception as err:
                print(err)
            return dict_rating
        def top_by_ratings_avg(self, n: int, metric='average')->dict:
            ratings_dict = defaultdict(list)

            for user_id, movie_id, rating, _ in self.ratings[1:]:
                ratings_dict[movie_id].append(float(rating))

            if metric == 'average':
                top_movies = {movie_id: round(statistics.mean(ratings), 2) for movie_id, ratings in ratings_dict.items()}
            else:
                raise ValueError("Metric must be average")

            return dict(sorted(top_movies.items(), key=lambda x: x[1], reverse=True)[:n])

        

        def top_controversial(self, n: int) -> dict:
           
            ratings_dict = defaultdict(list)

            
            for user_id, movie_id, rating, _ in self.ratings[1:]:
                ratings_dict[movie_id].append(float(rating))

            variances = {movie_id: round(numpy.var(ratings), 2) for movie_id, ratings in ratings_dict.items()}
            return dict(sorted(variances.items(), key=lambda x: x[1], reverse=True)[:n])

            
                       
class Tags(object):
    def __init__(self,file_path:str):
        self.file_path = file_path
        self.mass = []
    def read_file(self):
        try:

            with open(file=self.file_path,mode="r") as r:
                for line in r:
                   self.mass.append(line.strip().split(','))
        except FileNotFoundError as err1:
            print(err1)
        except FileExistsError as err2:
            print(err2)
        return self.mass
    def most_words(self,n:int)->dict:
        top_n = dict()
        self.m = self.read_file()
        try:
            for user_id,movie_id,tag,timestamp in self.m[1:]:
                top_n[tag] = len(tag.split(' '))
        except Exception as err:
            print(err)
        top_n = dict(sorted(top_n.items(),key=lambda x : x[1],reverse=True)[:n])
        return top_n
    def longest(self,n:int)->list:
        long_tag = dict()
        self.m = self.read_file()
        try:
            for user_id,movie_id,tag,timestamp in self.m[1:]:
                long_tag[tag] = len(tag)
        except Exception as err:
            print(err)
        top_n = list(i[0] for i in sorted(long_tag.items(),key=lambda x : x[1],reverse=True))[:n]
        return top_n
    def most_words_and_longest(self, n:int)->list:
        try:
            top_n_tags_most_words = set(self.most_words(n))
            top_n_longest_tags = set(self.longest(n))
            total = list(top_n_tags_most_words.intersection(top_n_longest_tags))
        except Exception as err:
            print(err)
        return total
    def popular(self,n:int)->dict:
        try:
            popular_tags = dict()
            self.m = self.read_file()
            popular_tags = dict(sorted(Counter([tag for user_id,movie_id,tag,timestamp in self.m[1:]]).items(),key=lambda x : x[1],reverse=True)[1:n])
        except Exception as err:
            print(err)
        return popular_tags
    def tags_with(self, word:str)->list:
        try:

            tags_with_word = list()
            self.m = self.read_file()
            tags_with_word = sorted(list(set([tag for user_id,movie_id,tag,timestamp in self.m[1:] if word in tag.split(' ')])))
        except Exception as err:
            print(err)
        return tags_with_word





class Links:
    def __init__(self, path_to_the_file):
        '''Инициализирует класс Links, загружает данные и кэш.'''
        self.path_to_the_file = path_to_the_file
        self.links = []
        self.movieId_to_imdbId = {}
        self.imdb_data_cache = {}
        self.cache_filepath = "imdb_data_cache.json"
        self.data_load()
        self._load_cache_from_json()

    def data_load(self):
        '''Загружает данные из CSV файла links.csv.'''
        try:
            with open(self.path_to_the_file, mode='r', encoding='UTF-8') as file:
                reader = csv.DictReader(file, delimiter=',', quotechar='"')
                for row in reader:
                    link_data = {
                        'movieId': row['movieId'],
                        'imdbId': row['imdbId'],
                        'tmdbId': row['tmdbId']
                    }
                    self.links.append(link_data)
                    self.movieId_to_imdbId[row['movieId']] = row['imdbId']

        except FileNotFoundError:
            print(f"Ошибка: Файл {self.path_to_the_file} не найден.")
            self.links = []
            self.movieId_to_imdbId = {}

        except Exception as e:
            print(f"Произошла ошибка при загрузке данных: {e}")
            self.links = []
            self.movieId_to_imdbId = {}

    def _load_cache_from_json(self):
        '''Загружает кэш из JSON файла при инициализации.'''
        if os.path.exists(self.cache_filepath):
            try:
                with open(self.cache_filepath, 'r', encoding='utf-8') as f:
                    self.imdb_data_cache = json.load(f)
            except json.JSONDecodeError:
                print(f"Ошибка чтения кэш-файла {self.cache_filepath}. Кэш будет создан заново.")
                self.imdb_data_cache = {}
            except Exception as e:
                print(f"Ошибка при загрузке кэша из файла {self.cache_filepath}: {e}")
                self.imdb_data_cache = {}
        else:
            self.imdb_data_cache = {}


    def _save_cache_to_json(self):
        '''Сохраняет кэш в JSON файл.'''
        try:
            with open(self.cache_filepath, 'w', encoding='utf-8') as f:
                json.dump(self.imdb_data_cache, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка при сохранении кэша в файл {self.cache_filepath}: {e}")


    def _safe_extract_text(self, element):
        '''Безопасно извлекает текст из элемента BeautifulSoup.'''
        return element.get_text(strip=True) if element else None

    def _parse_director(self, soup):
        """Извлекает имя(имена) режиссера со страницы IMDb."""
        # более общий селектор
        credit_blocks = soup.select("li[data-testid='title-pc-principal-credit']")
        directors = []
        for block in credit_blocks:
            # ищем все ссылки внутри блока
            links = block.select("a[href^='/name/']")
            for a in links:
                text = self._safe_extract_text(a)
                if text and text not in directors:
                    directors.append(text)

        return ", ".join(directors) if directors else None



    def _parse_generic_boxoffice(self, soup, testid):
         '''Извлекает значения Box Office (бюджет, сборы) по testid.'''
         section = soup.find('li', {'data-testid': testid})
         if not section:
             return None

         value_element = section.find('span', class_='ipc-metadata-list-item__list-content-item')
         if not value_element:
             value_element = section.find('div', class_='ipc-metadata-list-item__content-container')
         return self._safe_extract_text(value_element)

    def _parse_runtime(self, soup):
        '''Извлекает продолжительность фильма со страницы.'''
        runtime_section = soup.find('li', {'data-testid': 'title-techspec_runtime'})
        if not runtime_section:
            return None

        value_div = runtime_section.find('div', class_='ipc-metadata-list-item__content-container')
        return self._safe_extract_text(value_div)

    def _parse_title(self, soup):
        '''Извлекает название фильма.'''
        title_element = soup.select_one('h1[data-testid="hero__pageTitle"]')
        return self._safe_extract_text(title_element)

    def _parse_imdb_page(self, soup, field):
        '''Диспетчер парсинга для разных полей.'''
        try:
            if field == 'Director':
                return self._parse_director(soup)
            elif field == 'Budget':
                return self._parse_generic_boxoffice(soup, 'title-boxoffice-budget')
            elif field == 'Cumulative Worldwide Gross':
                return self._parse_generic_boxoffice(soup, 'title-boxoffice-cumulativeworldwidegross')
            elif field == 'Runtime':
                runtime_str = self._parse_runtime(soup)
                return runtime_str
            elif field == 'Title':
                return self._parse_title(soup)
            else:
                return None
        except Exception as e:
            return None

    def _generate_cache_filename(self, movie_ids, fields):
        '''Генерирует имя файла кэша.'''
        filename = "imdb_data_cache.json"
        return filename

    def get_imdb(self, list_of_movies, list_of_fields, use_cache=True, force_fetch=False):
        '''Возвращает словарь {movieId: {field: value, ...}} для заданных фильмов.'''
        imdb_info = {}
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        session.headers.update(headers)
        processed_movie_ids = set()

        for movie_id in list_of_movies:
            if movie_id in processed_movie_ids:
                continue
            processed_movie_ids.add(movie_id)

            if use_cache and not force_fetch and movie_id in self.imdb_data_cache:
                imdb_info[movie_id] = self.imdb_data_cache[movie_id]
                continue

            imdb_id = self.movieId_to_imdbId.get(movie_id)
            if not imdb_id:
                print(f"Предупреждение: IMDB ID не найден для movieId {movie_id}. Пропускается.")
                continue

            imdb_id_formatted = f"tt{imdb_id.zfill(7)}" if not imdb_id.startswith('tt') else imdb_id
            url = f"https://www.imdb.com/title/{imdb_id_formatted}/"

            try:
                response = session.get(url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                field_data_dict = {}
                for field in list_of_fields:
                    parsed_value = self._parse_imdb_page(soup, field)
                    field_data_dict[field] = parsed_value

                imdb_info[movie_id] = field_data_dict
                self.imdb_data_cache[movie_id] = field_data_dict
                time.sleep(0.1)

            except requests.exceptions.Timeout:
                 print(f"Ошибка: Таймаут при запросе {url} для movieId {movie_id}")
                 field_data_dict = {field: "Ошибка: Таймаут" for field in list_of_fields}
                 imdb_info[movie_id] = field_data_dict
                 self.imdb_data_cache[movie_id] = field_data_dict


            except requests.exceptions.RequestException as e:
                print(f"Ошибка при запросе {url} для movieId {movie_id}: {e}")
                field_data_dict = {field: f"Ошибка сети: {e}" for field in list_of_fields}
                imdb_info[movie_id] = field_data_dict
                self.imdb_data_cache[movie_id] = field_data_dict

            except Exception as e:
                print(f"Неожиданная ошибка для movieId {movie_id}: {e}")
                field_data_dict = {field: f"Ошибка обработки: {e}" for field in list_of_fields}
                imdb_info[movie_id] = field_data_dict
                self.imdb_data_cache[movie_id] = field_data_dict


        if use_cache and force_fetch:
            self._save_cache_to_json()
        elif use_cache and not force_fetch and not os.path.exists(self.cache_filepath):
            self._save_cache_to_json()

        return imdb_info

    def fetch_initial_data(self, movie_ids, fields):
        '''Предварительно загружает данные для movie_ids и сохраняет в кэш.'''
        self.get_imdb(movie_ids, fields, use_cache=True, force_fetch=True)


    def top_directors(self, n, process_limit=100):
        '''Возвращает топ-N режиссеров по количеству фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить топ режиссеров.")
            return {}

        actual_limit = min(process_limit, len(all_movie_ids))
        movie_ids_to_process = all_movie_ids[:actual_limit]
        director_counts = Counter()

        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Director' not in movie_data or not movie_data['Director']:
                continue

            director_string = movie_data['Director']

            if isinstance(director_string, str) and director_string.startswith("Ошибка:"):
                continue
            directors = [d.strip() for d in director_string.split(',')]
            for director in directors:
                if director:
                    director_counts[director] += 1

        top_n_list = director_counts.most_common(n)
        top_directors_dict = dict(top_n_list)
        return top_directors_dict


    def _parse_budget_string(self, budget_str):
        '''Преобразует строку бюджета в числовое значение (int).'''
        if not budget_str or not isinstance(budget_str, str):
            return None

        cleaned_str = re.sub(r'[$,€£\s]|(GBP)|(USD)|(EUR)|(CAD)|(AUD)|(NZD)|(CHF)|(CNY)|(JPY)|(KRW)|(RUB)|[,\s]\(.*\)', '', budget_str, flags=re.IGNORECASE).strip()
        numeric_part = ''.join(re.findall(r'\d', cleaned_str))

        if not numeric_part:
            return None

        try:
            return int(numeric_part)
        except ValueError:
            return None


    def most_expensive(self, n, process_limit=1000):
        '''Возвращает словарь топ-N самых дорогих фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_budgets = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Budget' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            budget_str = movie_data['Budget']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                 continue
            if budget_str is None or isinstance(budget_str, str) and budget_str.startswith("Ошибка:"):
                continue

            budget_num = self._parse_budget_string(budget_str)
            if budget_num is not None and title:
                 movies_with_budgets.append((title, budget_num))

        movies_with_budgets.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_budgets[:n]
        budgets = dict(top_n_movies)
        return budgets


    def most_profitable(self, n, process_limit=1000):
        '''Возвращает словарь топ-N самых прибыльных фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить самые прибыльные фильмы.")
            return {}

        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_profits = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Budget' not in movie_data or 'Cumulative Worldwide Gross' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            budget_str = movie_data['Budget']
            gross_str = movie_data['Cumulative Worldwide Gross']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                continue
            if budget_str is None or isinstance(budget_str, str) and budget_str.startswith("Ошибка:"):
                continue
            if gross_str is None or isinstance(gross_str, str) and gross_str.startswith("Ошибка:"):
                continue

            budget_num = self._parse_budget_string(budget_str)
            gross_num = self._parse_budget_string(gross_str)

            if budget_num is not None and gross_num is not None and title:
                profit = gross_num - budget_num
                movies_with_profits.append((title, profit))

        if not movies_with_profits:
            print("Не найдено фильмов с корректно извлеченными бюджетами и сборами.")
            return {}

        movies_with_profits.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_profits[:n]
        profits = dict(top_n_movies)
        return profits

    def _parse_runtime_minutes(self, runtime_str):
        '''Преобразует строку продолжительности в минуты (int).'''
        if not runtime_str or not isinstance(runtime_str, str):
            return None

        runtime_str = runtime_str.lower().replace('мин', 'minutes').replace('ч', 'hours').strip()
        total_minutes = 0
        try:
            hours_match = re.search(r'(\d+)(?:hours|h)', runtime_str)
            minutes_match = re.search(r'(\d+)(?:minutes|min)', runtime_str)

            hours = int(hours_match.group(1)) if hours_match else 0
            minutes = int(minutes_match.group(1)) if minutes_match else 0

            if not hours_match and not minutes_match:
                return None

            total_minutes = hours * 60 + minutes

        except (AttributeError, ValueError):
            return None

        return total_minutes

    def longest(self, n, process_limit=1000):
        '''Возвращает словарь топ-N самых длинных фильмов, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить самые длинные фильмы.")
            return {}

        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_runtimes = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Runtime' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            runtime_str = movie_data['Runtime']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                continue
            if runtime_str is None or isinstance(runtime_str, str) and runtime_str.startswith("Ошибка:"):
                continue

            runtime_minutes = self._parse_runtime_minutes(runtime_str)

            if runtime_minutes is not None and title:
                movies_with_runtimes.append((title, runtime_minutes))

        if not movies_with_runtimes:
            print("Не найдено фильмов с корректно извлеченной продолжительностью.")
            return {}

        movies_with_runtimes.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_runtimes[:n]
        runtimes = dict(top_n_movies)
        return runtimes


    def top_cost_per_minute(self, n, process_limit=1000):
        '''Возвращает словарь топ-N фильмов с самой высокой стоимостью минуты, используя кэш.'''
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены. Невозможно определить стоимость минуты.")
            return {}

        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        movies_with_costs = []
        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data or 'Budget' not in movie_data or 'Runtime' not in movie_data or 'Title' not in movie_data:
                continue

            title = movie_data['Title']
            budget_str = movie_data['Budget']
            runtime_str = movie_data['Runtime']

            if title is None or isinstance(title, str) and title.startswith("Ошибка:"):
                continue
            if budget_str is None or isinstance(budget_str, str) and budget_str.startswith("Ошибка:"):
                continue
            if runtime_str is None or isinstance(runtime_str, str) and runtime_str.startswith("Ошибка:"):
                continue

            budget_num = self._parse_budget_string(budget_str)
            runtime_minutes = self._parse_runtime_minutes(runtime_str)

            if budget_num is not None and runtime_minutes is not None and runtime_minutes > 0 and title:
                cost_per_minute = budget_num / runtime_minutes
                movies_with_costs.append((title, cost_per_minute))

        if not movies_with_costs:
            print("Не найдено фильмов с корректно извлеченными бюджетами и продолжительностью.")
            return {}

        movies_with_costs.sort(key=lambda x: x[1], reverse=True)
        top_n_movies = movies_with_costs[:n]
        costs = {title: round(cost, 2) for title, cost in top_n_movies}
        return costs
    

    def director_efficiency(self, top_n=5, process_limit=1000):
        """
        Возвращает топ-N режиссеров по "эффективности":
        отношение суммарной прибыли к суммарному бюджету всех фильмов режиссера.
        Использует кэш IMDb.
        """
        all_movie_ids = list(self.movieId_to_imdbId.keys())
        if not all_movie_ids:
            print("Ошибка: Данные о фильмах не загружены.")
            return {}

        if process_limit is not None and process_limit > 0:
            movie_ids_to_process = all_movie_ids[:min(process_limit, len(all_movie_ids))]
        else:
            movie_ids_to_process = all_movie_ids

        director_stats = defaultdict(lambda: {'profit': 0, 'budget': 0})

        for movie_id in movie_ids_to_process:
            movie_data = self.imdb_data_cache.get(str(movie_id))
            if not movie_data:
                continue

            title = movie_data.get('Title')
            budget_str = movie_data.get('Budget')
            gross_str = movie_data.get('Cumulative Worldwide Gross')
            director_str = movie_data.get('Director')

            if not title or not budget_str or not gross_str or not director_str:
                continue
            if any(isinstance(x, str) and x.startswith("Ошибка:") for x in [title, budget_str, gross_str]):
                continue

            budget_num = self._parse_budget_string(budget_str)
            gross_num = self._parse_budget_string(gross_str)
            if budget_num is None or gross_num is None or budget_num == 0:
                continue

            profit = gross_num - budget_num
            directors = [d.strip() for d in director_str.split(',')]
            for director in directors:
                director_stats[director]['profit'] += profit
                director_stats[director]['budget'] += budget_num

        efficiency_dict = {}
        for director, stats in director_stats.items():
            if stats['budget'] > 0:
                efficiency = stats['profit'] / stats['budget']
                efficiency_dict[director] = round(efficiency, 2)

        top_directors = dict(sorted(efficiency_dict.items(), key=lambda x: x[1], reverse=True)[:top_n])
        return top_directors   

    
@pytest.fixture
def movies():
    return Movies("ml-latest-small/movies.csv")
    
class TestMovies:

    def test_dist_by_release(self, movies):
        result = movies.dist_by_release()
        assert isinstance(result, dict)
        assert all(isinstance(k, int) for k in result.keys())
        assert all(isinstance(v, int) for v in result.values())
        values = list(result.values())
        assert values == sorted(values, reverse=True)
        assert result[1995] == 224  # все фильмы 1995

    def test_dist_by_genres(self, movies):
        result = movies.dist_by_genres()
        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result.keys())
        assert all(isinstance(v, int) for v in result.values())
        values = list(result.values())
        assert values == sorted(values, reverse=True)
        assert result["Comedy"] == 365
        assert result["Fantasy"] == 69

    def test_most_genres(self, movies):
        result = movies.most_genres(5)
        assert isinstance(result, dict)
        assert len(result) <= 5
        assert all(isinstance(k, str) for k in result.keys())
        assert all(isinstance(v, int) for v in result.values())
        top_movie = list(result.keys())[0]
        assert top_movie == "Toy Story (1995)"
        assert result[top_movie] == 5

    def test_movies_in_genre(self, movies):
        result = movies.movies_in_genre("Comedy", 5)
        assert isinstance(result, dict)
        assert len(result) <= 5
        assert all("Comedy" in line for line in movies.data if any(title in line for title in result.keys()))


LINKS_CSV_FILE = "ml-latest-small/links.csv"


@pytest.fixture()
def links_instance():
    return Links(LINKS_CSV_FILE)

class TestLinksClass:
    def test_links_data_load_success(self, links_instance):
        """Тест загрузки данных Links."""
        assert isinstance(links_instance.links, list)
        assert len(links_instance.links) > 0

    def test_links_top_directors_returns_dict_sorted(self, links_instance):
        """Тест top_directors возвращает словарь и отсортирован."""
        result = links_instance.top_directors(3, process_limit=10)
        assert isinstance(result, dict)
        director_counts = list(result.values())
        if director_counts:
            assert all(director_counts[i] >= director_counts[i+1] for i in range(len(director_counts)-1))

    def test__parse_budget_string_success(self, links_instance):
        """Тест метода _parse_budget_string, успешное преобразование."""
        budget_str = "$123,456,789 (estimated)"
        parsed_budget = links_instance._parse_budget_string(budget_str)
        assert parsed_budget == 123456789
        assert isinstance(parsed_budget, int)

    def test__parse_runtime_minutes_success(self, links_instance):
        """Тест метода _parse_runtime_minutes, успешное преобразование."""
        runtime_str = "2hours 30minutes"
        runtime_minutes = links_instance._parse_runtime_minutes(runtime_str)
        assert runtime_minutes == 150
        assert isinstance(runtime_minutes, int)

    @patch('requests.Session.get')
    def test_get_imdb_returns_dict_of_dicts(self, mock_get, links_instance):
        """Тест get_imdb возвращает словарь словарей."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<h1 data-testid=\"hero__pageTitle\">Test Movie</h1>" 
        mock_get.return_value = mock_response

        movie_ids_to_test = ['1']
        fields_to_test = ['Title']
        result = links_instance.get_imdb(movie_ids_to_test, fields_to_test, use_cache=False)
        assert isinstance(result, dict) 
        assert '1' in result 
        movie_data = result['1']
        assert isinstance(movie_data, dict) 
        assert 'Title' in movie_data 
        assert movie_data['Title'] == 'Test Movie' 

    def test_most_expensive_returns_dict_sorted(self, links_instance):
        """Тест most_expensive возвращает словарь и отсортирован."""
        result = links_instance.most_expensive(2, process_limit=5)
        assert isinstance(result, dict)
        budgets = list(result.values())
        if budgets:
            assert all(budgets[i] >= budgets[i+1] for i in range(len(budgets)-1))

    def test_most_profitable_returns_dict_sorted(self, links_instance):
        """Тест most_profitable возвращает словарь и отсортирован."""
        result = links_instance.most_profitable(2, process_limit=5)
        assert isinstance(result, dict)
        profits = list(result.values())
        if profits:
            assert all(profits[i] >= profits[i+1] for i in range(len(profits)-1))

    def test_longest_returns_dict_sorted(self, links_instance):
        """Тест longest возвращает словарь и отсортирован."""
        result = links_instance.longest(2, process_limit=5)
        assert isinstance(result, dict)
        runtimes = list(result.values())
        if runtimes:
            assert all(runtimes[i] >= runtimes[i+1] for i in range(len(runtimes)-1))

    def test_top_cost_per_minute_returns_dict_sorted(self, links_instance):
        """Тест top_cost_per_minute возвращает словарь и отсортирован."""
        result = links_instance.top_cost_per_minute(2, process_limit=5)
        assert isinstance(result, dict)
        costs = list(result.values())
        if costs:
            assert all(costs[i] >= costs[i+1] for i in range(len(costs)-1))


    def test_director_efficiency_returns_dict(self, links_instance):
        """Тест метода director_efficiency возвращает словарь и корректные значения."""
        result = links_instance.director_efficiency(top_n=3, process_limit=10)
        assert isinstance(result, dict)
        for director, efficiency in result.items():
            assert isinstance(director, str)
            assert isinstance(efficiency, float)
            assert efficiency >= 0


class TestRating:
    
    @pytest.fixture
    def rat(self):
        return Rating('ml-latest-small/rats.csv')
        
    def test_rat_read_file(self, rat): 
        rat.read_file()
        res = rat.mass
        assert isinstance(res, list)
    def test_mov_dict_by_year(self, rat): 
        result = rat.Movies(rat.mass).dist_by_year()
        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result.keys())
        assert all(isinstance(v, int) for v in result.values())
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_dist_by_rating(self,rat):
        result = rat.Movies(rat.mass).dist_by_rating()
        result = rat.Movies(rat.mass).dist_by_year()
        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result.keys())
        assert all(isinstance(v, int) for v in result.values())
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_top_by_num_of_ratings(self,rat):
        n = 10
        result = rat.Movies(rat.mass).top_by_num_of_ratings(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        
        assert all(isinstance(k, str) for k in result.keys())
        
        assert all(isinstance(v, int) for v in result.values())
        
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_top_by_ratings(self,rat):
        n = 10
        result = rat.Movies(rat.mass).top_by_ratings(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        
        assert all(isinstance(k, str) for k in result.keys())
        
        assert all(isinstance(v, int) for v in result.values())

        result1 = rat.Movies(rat.mass).top_by_ratings(n,metric='median')
        assert isinstance(result1, dict)
        assert len(result1) <= n
        assert all(isinstance(k, str) for k in result1.keys())
        
        assert all(isinstance(v, int) for v in result1.values())
        values = list(result.values())
        assert values == sorted(values,reverse=True)
        values = list(result1.values())
        assert values == sorted(values,reverse=True)
    def test_top_controversial(self,rat):
        n = 10
        result = rat.Movies(rat.mass).top_controversial(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        
        assert all(isinstance(k, str) for k in result.keys())
        
        assert all(isinstance(v, int) for v in result.values())
        
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_dist_num_rat(self,rat):
        result = rat.Users(rat.mass).dist_num_rat()
        assert isinstance(result, dict)
        assert all(isinstance(k, str) for k in result.keys())
        assert all(isinstance(v, int) for v in result.values())
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_top_by_ratings_avg(self,rat):
        n = 10
        result = rat.Movies(rat.mass).top_by_ratings(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        
        assert all(isinstance(k, str) for k in result.keys())
        
        assert all(isinstance(v, int) for v in result.values())
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_top_controversia(self,rat):
        n = 10
        result = rat.Users(rat.mass).top_controversial(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        
        assert all(isinstance(k, str) for k in result.keys())
        
        assert all(isinstance(v, int) for v in result.values())
        
        values = list(result.values())
        assert values == sorted(values,reverse=True)

class TestTags:
    
    @pytest.fixture
    def tags(self):

        return Tags('ml-latest-small/tags.csv')

    def tags_read_file(self, tags):
        res = tags.read_file()
        assert isinstance(res, list)
    def test_tags_most_words(self, tags):
        n = 10
        result = tags.most_words(n)
        assert isinstance(result, dict)
        assert len(result) <= n
        
        assert all(isinstance(k, str) for k in result.keys())
        
        assert all(isinstance(v, int) for v in result.values())
        
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_tags_longest(self,tags):
        n = 10
        result = tags.longest(n)
        assert isinstance(result,list)
        assert len(result) <= n
        assert all(isinstance(tag, str) for tag in result)
    def test_most_words_longest(self,tags):
        n = 10
        result = tags.most_words_and_longest(n)
        assert isinstance(result,list)
        assert len(result) <= n
        assert all(isinstance(tag, str) for tag in result)
    def test_popular(self,tags):
        n = 10
        result = tags.popular(n)
        assert isinstance(result,dict)
        assert len(result) <= n
        assert all(isinstance(k, str) for k in result.keys())
        assert all(isinstance(v, int) for v in result.values())
        values = list(result.values())
        assert values == sorted(values,reverse=True)
    def test_tags_with(self,tags):
        word1 = 'police'
        word2 = 'funny'
        word3 = 'Police'
        result1 = tags.tags_with(word1)
        result2 = tags.tags_with(word2)
        result3 = tags.tags_with(word3)
        assert isinstance(result1,list)
        assert isinstance(result2,list)
        assert isinstance(result3,list)
        assert all(isinstance(tag, str) for tag in result1)
        assert all(isinstance(tag, str) for tag in result2)
        assert all(isinstance(tag, str) for tag in result3)







