import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from tenacity import Retrying, retry, stop_after_delay
from bs4 import BeautifulSoup


class YTS:
    def __init__(self):
        self.url = "https://yts.mx"
        self.api_url = f"{self.url}/api/v2"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def list_movies(self, options):
        page = 1
        while True:
            list_movies_url = f"{self.api_url}/list_movies.json?{options}&page={page}"
            retry_instance = Retrying(stop=stop_after_delay(3))
            for attempt in retry_instance:
                with attempt:
                    resp = requests.get(list_movies_url)
                    resp.raise_for_status()
            movies = resp.json().get("data", {}).get("movies")
            if not movies:
                break
            page += 1
            yield movies

    def search_movies(self, search_term, get_best_match=False):
        page = 1
        while True:
            search_movies_url = f"{self.api_url}/list_movies.json"
            querystring = {"query_term": f"{search_term}", "page": page}
            retry_instance = Retrying(stop=stop_after_delay(3))
            for attempt in retry_instance:
                with attempt:
                    resp = requests.get(search_movies_url, params=querystring)
                    resp.raise_for_status()
            movies = resp.json().get("data", {}).get("movies")
            if not movies:
                break
            page += 1
            if get_best_match:
                for movie in movies:
                    if movie.get("title_english") == search_term:
                        yield [movie]
                        break
            else:
                yield movies

    def list_movies_by_language(self, language):

        page = 1
        while True:
            # YTS API does not support filter by language, so its back to good old scraping.
            url = f"{self.url}/browse-movies/0/all/all/0/latest/0/{language}"
            if page > 1:
                parameters = {"page": page}
            else:
                parameters={}
            retry_instance = Retrying(stop=stop_after_delay(3))
            for attempt in retry_instance:
                with attempt:
                    response = requests.get(url, headers=self.headers, timeout=10,params=parameters)
                    response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            movie_elements = soup.find_all("a", class_="browse-movie-title")


            if movie_elements:
                movie_titles = [
                    movie.get_text(strip=True).replace(f"[{language.upper()}]", "") for movie in movie_elements
                ]

                def search_movie_task(movie):
                    return next(self.search_movies(movie, get_best_match=True))

                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {executor.submit(search_movie_task, movie): movie for movie in movie_titles}

                    for future in as_completed(futures):
                        try:
                            yield future.result()
                        except Exception as e:
                            print(f"Error processing movie '{futures[future]}': {e}")
            else:
                break
            page += 1
