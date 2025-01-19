import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_delay, wait_exponential
from models.movie import Movie


class IMDB:
    def __init__(self):
        self.base_url = "https://www.imdb.com"
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    @retry(stop=stop_after_delay(10), wait=wait_exponential(multiplier=1, min=1, max=5))
    def get_movie(self, imdb_id):
        try:
            movie_url = f"{self.base_url}/title/{imdb_id}/"
            response = requests.get(movie_url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise exception for HTTP errors
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch data from IMDB: {e}")

        soup = BeautifulSoup(response.text, "html.parser")

        name = self._extract_text(
            soup, "span", {"data-testid": "hero__primary-text"}, default="Unknown Title"
        )
        synopsis = self._extract_text(
            soup, "span", {"data-testid": "plot-l"}, default="Synopsis not available"
        )
        poster = self._extract_attr(
            soup, "img", {"class": "ipc-image"}, "src", default="No Poster Available"
        )
        rating = self._extract_text(
            soup,
            "div",
            {"data-testid": "hero-rating-bar__aggregate-rating__score"},
            default="NA",
        )
        release_info = self._extract_text(soup,"a",{"class":"ipc-metadata-list-item__list-content-item--link"},default="NA")
        cast = self._extract_cast(soup, limit=9)

        return Movie(name=name,synopsis=synopsis,rating=rating,poster=poster,cast=cast, director=release_info)

    def _extract_text(self, soup, tag, attrs, default=""):
        try:
            element = soup.find(tag, attrs=attrs)
            return element.text.strip() if element else default
        except Exception:
            return default

    def _extract_attr(self, soup, tag, attrs, attr_name, default=""):
        try:
            element = soup.find(tag, attrs=attrs)
            return element[attr_name].strip() if element and attr_name in element.attrs else default
        except Exception:
            return default

    def _extract_cast(self, soup, limit=5):
        try:
            cast_members = soup.find_all(
                "a", attrs={"data-testid": "title-cast-item__actor"}, limit=limit
            )
            return [actor.text.strip() for actor in cast_members]
        except Exception:
            return "Cast information not available"
