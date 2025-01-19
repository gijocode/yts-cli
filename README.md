# YTS-CLI

A command-line interface (CLI) tool that allows you to browse and search movies from YTS, view movie details, and download torrents.

## Features

- List movies by categories such as:
  - Latest
  - Genre
  - Language
- Search movies by title.
- View detailed information about a movie (IMDb rating, plot, etc.).
- Download movie torrents in selected quality.

## Installation

To get started, clone the repository and install the necessary dependencies:

1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2.	Navigate to the project directory:

   ```bash
        cd <project-directory>
   ```


3.	Install the required dependencies using pip:

   ```bash
        pip install -r requirements.txt
   ```



This will install all the necessary libraries for the project to run.

## Usage

Once the dependencies are installed, you can run the CLI by executing the following command:

   ```bash
python app.py
   ```

## Dependencies

The required libraries for this project are listed in the requirements.txt file. You can install them using:

   ```bash
    pip install -r requirements.txt
   ```

The project uses the following libraries:
-	requests: For making HTTP requests.
-	tenacity: For retrying failed requests.
-	rich: For rich text and console output.
-	iterfzf: For interactive fuzzy searching in the CLI.
-	yts-wrapper: A wrapper for YTS API.
-	imdb-wrapper: A wrapper for IMDb API.
-	typer: For creating the command-line interface.

Make sure you have installed [fzf](https://github.com/junegunn/fzf) for your corresponding OS
## Contributing

Contributions are welcome! If you have suggestions, bug fixes, or improvements, feel free to open an issue or submit a pull request.

## License

This project is open source and available under the MIT License.
