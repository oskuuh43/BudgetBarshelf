# Alko Cocktail and Spirit Ratings App

## Overview

**alko_app** is a desktop application designed to help users compare alcoholic beverages sold by the Finnish state-owned liquor store, **Alko**.
The application provides an "all in one" platform for browsing products by value, community ratings, and ingredient usability in cocktails.


## Features

### Product Explorer:

- **Alcohol per Euro Calculator**: See how much alcohol you get for every euro spent.
- **Search & Filter**: Narrow down products by spirit-category or product-name.
- **Dark/Light Theme**: Theme switching between **light** mode and **dark** mode.

### Rum & Whiskey Ratings:

- **Community Ratings**: Displays cimmunity ratings for the rums and whiskeys available at Alko.
- **User Ratings**: Users can assign and save their own ratings for rum and whiskey products.

###  Cocktail Explorer:

- **Cocktail Recipes**: Browse a large selection of cocktail recipes.
- **Ingredient Filtering**: Find cocktails to make based on ingredients you have at home.

### Usability:

- Packaged as a **standalone executable `.exe`** file for a simple app startup without needing to worry about dependencies.
- The application can also be run from your **Python codebase**
  

## Screenshots

### The Main Window:

View and compare all Alko products based on their alcohol content per euro. This page includes search and filtering functionalities, aswell as the option to switch between dark and light mode.

![image](https://github.com/user-attachments/assets/0510bad2-7514-4c31-948e-b356f80b23c6)


### Light-mode enabled:

The option to choose the applications theme based on your own preferenses.

![image](https://github.com/user-attachments/assets/4018327e-6b63-40b8-b0a2-825390bea0f1)


### Rum Ratings Window:

Compare rums available at Alko using community ratings.
You can also add your own ratings for each rum.

![image](https://github.com/user-attachments/assets/64d8dc5d-57aa-41ce-b112-bf18c938a17d)


### Whiskey Ratings Window:

Compare whiskeys available at Alko using community ratings.
You can also add your own ratings for each whiskey.

![image](https://github.com/user-attachments/assets/3762434b-b29e-42a5-944a-ebc65c254ca6)



### Rum and Whiskey Rating Functionality:

Rating windows for whiskeys and rums – useful for keeping track of your personal preferences.

![image](https://github.com/user-attachments/assets/6003f069-4519-49ca-91c2-58cbcc03b649)
![image](https://github.com/user-attachments/assets/414ff7cf-8e55-4ed1-9d04-cc337a70a3f9)

### Cocktail Explorer:

Browse a large database of cocktail recipes.

![image](https://github.com/user-attachments/assets/fdbf5c1f-173a-4ec9-b166-a0a3b8e378c3)


### Bar-shelf Functionality:

Filter cocktails based on what ingredients you currently have.

![image](https://github.com/user-attachments/assets/b1aa5aff-619d-4972-974e-e3e4e04c45c5)


### Detailed Cocktail View:

Detailed instructions for making the cocktails.

![image](https://github.com/user-attachments/assets/bb378d3c-3f34-4389-b323-447e7461cf88)



##  How To run

### Option 1: Run the Executable (.exe)

If you just want to use the app without installing Python or dependencies:

1. **Download the latest release** from the GitHub Releases page:  
    [https://github.com/oskuuh43/alko_app/releases](https://github.com/oskuuh43/alko_app/releases)  -- add correct link --

2. **Unzip** the downloaded `.zip` file.

3. Inside the extracted folder, you’ll find:
   - `alko_app.exe` – the application executable
   - `_internal/` – required folder containing Excel files and other resources

4. **Double-click** `alko_app.exe` to launch the app.

No further installation is needed.


### Option 2: Run from the Code

If you want to run or modify the code yourself:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/oskuuh43/alko_app.git
   cd alko_app

2. **Install the required dependencies**:

   ```bash
   pip install -r requirements.txt

3. **Run The Application**:
   
   ```bash
   python main.py

Make sure the assets/ folder is present in the project root. It contains all required datasets.


## Project Structure

The **project structure for the application** is the following:

<img width="635" height="731" alt="image" src="https://github.com/user-attachments/assets/c42123d9-4764-466d-bea7-e843edfcd1d2" />

## Sources

The sources listed below are relied on for finding the needed information for this application:

### Alko Product Data

  [alkon-hinnasto-tekstitiedostona.xlsx](https://www.alko.fi/INTERSHOP/static/WFS/Alko-OnlineShop-Site/-/Alko-OnlineShop/fi_FI/Alkon%20Hinnasto%20Tekstitiedostona/alkon-hinnasto-tekstitiedostona.xlsx)

### Rum Ratings

- [The Rum Howler Blog](https://therumhowlerblog.com/) *(main source for ratings, scraped using a webscraper I Developed)*
- [RumX](https://www.rum-x.com/)
- [The Rum Barrel](https://therumbarrel.co.uk/)
- [Master of Malt – Rum](https://www.masterofmalt.com/)
- [Isokaato – Rum](https://www.isokaato.com/)
- [Rhum Attitude](https://www.rhumattitude.com/en/)
- [Excellence Rhum](https://www.excellencerhum.com/en/)
- [Amazon UK – Rum reviews](https://www.amazon.co.uk/)
- [Reddit r/rum](https://www.reddit.com/r/rum/)

*The custom webscraper scraper will be linked here once published.*

### Whiskey Ratings

- [WhiskyScores.com](https://whiskyscores.com/) *(main source for ratings, scraped using a webscraper I Developed)*
- [Whiskybase](https://www.whiskybase.com/)
- [WhiskyRant](https://www.whiskyrant.com/)
- [Minimiehen Seikkailut (FI)](https://minimiehenseikkailut.blogspot.com/)
- [Distiller](https://distiller.com/)
- [Film & Whiskey Podcast](https://www.filmwhiskey.com/)
- [Liquor.com – Whiskey](https://www.liquor.com/)
- [Breaking Bourbon](https://www.breakingbourbon.com/)
- [Master of Malt – Whiskey](https://www.masterofmalt.com/)
- Reddit communities:
  - [r/bourbon](https://www.reddit.com/r/bourbon/)
  - [r/irishwhiskey](https://www.reddit.com/r/irishwhiskey/)
  - [r/worldwhisky](https://www.reddit.com/r/worldwhisky/)
  - [r/Scotch](https://www.reddit.com/r/Scotch/)
- [Dramface](https://www.dramface.com/)
- [Sublime Imbibing](https://sublimeimbibing.ca/)
- [Whiskey in My Wedding Ring](https://www.whiskeyinmyweddingring.com/)
- [Words of Whisky](https://wordsofwhisky.com/)

*The webscraper will be linked here once published.*

### Cocktail Recipes

- **Cocktail Ingredients Dataset (Kaggle)**  
  [https://www.kaggle.com/datasets/ai-first/cocktail-ingredients](https://www.kaggle.com/datasets/ai-first/cocktail-ingredients)

This dataset contains thousands of cocktail recipes.

### Useful programming information

- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/) – GUI design
- [Pandas Documentation](https://pandas.pydata.org/docs/user_guide/index.html#user-guide) – Data handling
- [PyInstaller](https://pyinstaller.org/en/stable/) – `.exe` packaging

## Where Data Is Stored

The application stores data in different locations depending on the type of data and how the app is run (as a `.exe` or from the source code). 
Below is an overview of where data is stored:

### Alko Product Data

- **Location (.exe):**  
  `C:\Users\<YourUsername>\.alko_app\alko_price_list.xlsx`

- **Location (Run from Source Code):**  
  `assets/alko_price_list.xlsx`

### User Ratings (Rum & Whiskey)

- **Location (Both Executable and Source):**
  
  `C:\Users\<YourUsername>\.alko_user_whiskey_ratings.json`
  
  `C:\Users\<YourUsername>\.alko_user_rum_ratings.json`

These files store your personal rum and whiskey ratings.

### Bar Shelf Data

- **Location (Both Executable and Source):**  
  `C:\Users\<YourUsername>\.alko_app_shelf.json`

This file contains the list of ingredients you've selected in the “Manage My Bar” window.

### Static Resources (Cocktail Recipes, Review Datasets, etc.)

- **Location (Development):**  
  `assets/`

- **Location (Executable):**  
  `_internal/assets/`

## Words from the creator
...............



