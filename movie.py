from pydantic import BaseModel, HttpUrl
from typing import List


class Movie(BaseModel):
    name: str
    synopsis: str
    rating: str
    poster: HttpUrl
    cast: List[str]
    director:str

    def show_details(self):
        return (
            f"[bold][yellow]Name: [/bold]{self.name}[/yellow]\n"
            f"[bold][orange]Director: [/bold]{self.director}[/orange]\n"
            f"[bold][blue]Synopsis:[/bold] {self.synopsis}[/blue]\n"
            f"[bold][purple]Rating: [/bold]{self.rating}[/purple]\n"
            f"[bold][green]Cast: [/bold]{",".join(self.cast)}[/green]"
        )
