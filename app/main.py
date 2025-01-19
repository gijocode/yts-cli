import os
import typer
import requests
from enum import Enum
from tenacity import retry, stop_after_delay
from rich import print
from rich.prompt import Prompt
from rich.console import Console
from wrappers.yts_wrapper import YTS
from wrappers.imdb_wrapper import IMDB
from iterfzf import iterfzf
from constants import GENRES, DOWNLOAD_PATH, LANGUAGES

app = typer.Typer()
yts = YTS()
imdb = IMDB()


class MainOptions(str, Enum):
    LIST_MOVIES = "1. List Movies"
    SEARCH_MOVIES = "2. Search Movies"


class ListOptions(str, Enum):
    LATEST = "1. Latest"
    GENRE = "2. Genre"
    LANGUAGE = "3. Language"


@app.command()
def main():
    print("[bold red]Welcome to YTS-CLI[/bold red]\n\n")
    choice = iterfzf(
        [opt.value for opt in MainOptions],
        prompt="What do you want to do? (Ctrl+C to exit): ",
    )
    if not choice:
        print("[bold yellow]Exiting...[/bold yellow]")
        return

    selected_option = MainOptions(choice)
    match selected_option:
        case MainOptions.LIST_MOVIES:
            list_movies()
        case MainOptions.SEARCH_MOVIES:
            search_movies()


def search_movies():
    query = Prompt.ask("[bold blue]Enter search term[/bold blue]")
    movies_list = yts.search_movies(query)
    select_movie(movies_list)


def list_movies():
    choice = iterfzf([opt.value for opt in ListOptions], prompt="List movies by: ")
    if not choice:
        print(
            "[bold yellow]No option selected. Returning to main menu...[/bold yellow]"
        )
        main()

    selected_option = ListOptions(choice)
    options = None
    match selected_option:
        case ListOptions.LATEST:
            options = "limit=50"
            movies_list = yts.list_movies(options=options)
        case ListOptions.GENRE:
            genre = iterfzf(GENRES, prompt="Select a Genre: ")
            if genre:
                options = f"genre={genre}"
                movies_list = yts.list_movies(options=options)
        case ListOptions.LANGUAGE:
            lang = iterfzf(LANGUAGES, prompt="Select a Language: ")
            if lang:
                lang_code = LANGUAGES.get(lang)
                movies_list = yts.list_movies_by_language(lang_code)

    select_movie(movies_list)


def select_movie(movies_generator):
    def movie_titles():
        while True:
            try:
                page = next(movies_generator)
                for movie in page:
                    yield movie.get("title_long")
            except StopIteration:
                break

    movie_choice = iterfzf(movie_titles(), prompt="Select a movie: ")

    if not movie_choice:
        main()

    movies = next(yts.search_movies(movie_choice))
    selected_movie = next(
        (movie for movie in movies if movie["title_long"] == movie_choice), None
    )
    if selected_movie:
        get_movie(selected_movie)


def get_movie(movie):
    print(f"Retrieving info about [bold green]{movie["title_english"]}[/bold green]")
    movie_imdb = imdb.get_movie(movie["imdb_code"])
    if not movie:
        print("[bold red]Movie not found.[/bold red]")
        return

    console = Console()
    console.clear()
    print(movie_imdb.show_details())
    choice = input("\n\nDownload torrent? (y/n): ").strip().lower()
    console.clear()
    if choice == "y":
        torrents = movie.get("torrents", [])
        options = [f'{t["quality"]} {t["type"]} {t["size"]}' for t in torrents]
        torrent_choice = iterfzf(options, prompt="Select Quality: ")

        if torrent_choice:
            selected_torrent = next(
                (t for t in torrents if t["size"] in torrent_choice), None
            )
            if selected_torrent:
                download_file(selected_torrent["url"], f'{movie.get("slug")}.torrent')
    else:
        main()


@retry(stop=stop_after_delay(10))
def download_file(url, filename):
    print(f"[bold green]Downloading {filename} to {DOWNLOAD_PATH}...[/bold green]")
    destination_path = os.path.join(DOWNLOAD_PATH, filename)
    response = requests.get(url)
    response.raise_for_status()

    with open(destination_path, "wb") as file:
        file.write(response.content)

    print(
        f"[bold green]File downloaded successfully to {destination_path}[/bold green]"
    )


if __name__ == "__main__":
    app()
