# Gutenberg Word Frequency FINAL
# Author: Angelo Francia
# Date: 14 05 2025
""" This program provides a GUI tool to analyze books from Gutenberg website
It downloads the bookt ext from a URL, counts word frequencies, stores results
in a SQlite database and allows searches by book title. 
"""
import sqlite3 
import tkinter as tk 
from tkinter import messagebox
import re
from collections import Counter
import urllib.request 


## Database setup ----------------
def initialize_database():
    """
    Creates SQlite database and a table to store book word frequencies
    if they dont alr exist
    """
    conn = sqlite3.connect("franciabooks.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_frequencies (
            title TEXT,
            word TEXT,
            frequency INT,
            PRIMARY KEY (title, word)
        )
    ''')
    conn.commit()
    conn.close()

## Helper Functions ------
    
def download_book(url):
    """
    download the book text from Project Gutengberg URL.
    Paramters:
        url(str): direct link to the .txt version of the book
    Returns:
        str: decoded book text or None if fails
    """
    try:
        response = urllib.request.urlopen(url)
        raw_text = response.read().decode('utf-8') #reads raw data as bytes which isnt a regular string NOT READABLE and the DECODE converts raw bytes into readable string MOST COMMON TEXT FORMAT
        return raw_text
    except Exception as e:
        print(f"we had an error downloaded book: {e}")
        return None
    
def get_top_words(text, num_words=10):
    """
    Get the most frequent words in the given text.
    Parameters:
        text(str): The full book text
        num_words (int): Number of frequent words to return
    Returns:
        list of tuples: ex. (word, frequency)
    """
    text = text.lower()
    words = re.findall(r'\b[a-z]+\b', text)
    word_counts = Counter(words)
    return word_counts.most_common(num_words)

def extract_title(book_text):
    """
    Extracts the book title from the book text (if its even there)
    Paramters:
        book_text (str): raw text of the book
    Returns:
        str: the title if found otherwise >
    """
    for line in book_text.split('\n'):
        if line.strip().lower().startswith('title:'):
            return line.strip()[6:].strip()
    return "Unknown Title"



def save_to_database(title, word_freqs):
    """
    Save the title and top word frequencies to SQLite database.

    Parameters:
        title(str): Title of book
        word_freqs(list): List of (word, frequency) tuples.
    """
    try:
        conn = sqlite3.connect("franciabooks.db")
        cursor = conn.cursor()

        for word, freq in word_freqs:
            cursor.execute('''
                INSERT OR REPLACE INTO word_frequencies (title, word, frequency)
                VALUES (?, ?, ?)
            ''', (title, word, freq))
        conn.commit()
        conn.close()
        print(f"Saved '{title}' to the database.")
    except Exception as e:
        print(f"Error saving to database: {e}")

def search_database(title):
    """
    Search the database for a book by title and retrieve top words

    Parameters:
        title(str): The title of the book to search for
    Returns:
        list of tuples: (word, frequency) or none
    """
    try:
        conn = sqlite3.connect("franciabooks.db")
        cursor = conn.cursor() # controller that lets you execute SQL commands like SELECT
        cursor.execute('''
            SELECT word, frequency  
            FROM word_frequencies
            WHERE title = ?
            ORDER BY frequency DESC
            LIMIT 10
        ''', (title,)) # passes in the title as a tuple
        results = cursor.fetchall() # gets the rows returned by query (tuples)
        conn.close()

        if results:
            return results
        else:
            return None
    except Exception as e:
        print(f"Error searching database: {e}")
        return None


## GUI Functions -----------


def on_search_title():
    title = title_entry.get().strip()
    if not title:
        messagebox.showwarning("Missing Title", "Enter a book title.")
        return
    results = search_database(title)
    output_area.delete("1.0", tk.END) #clears the textbox 
    if results:
        output_area.insert(tk.END, f"Top words for '{title}':\n")
        for word, freq in results:
            output_area.insert(tk.END, f"{word}: {freq}\n")
    else:
        output_area.insert(tk.END, "Book was not found.\n")

def on_fetch_from_url():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Missing info", "Please enter both a URL.")
        return
    book_text = download_book(url)
    if book_text:
        title = extract_title(book_text)
        top_words = get_top_words(book_text)
        save_to_database(title, top_words)
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, f"Saved '{title}' to database with top words:\n")
        for word, freq in top_words:
            output_area.insert(tk.END, f"{word}: {freq}\n")
    else:
        output_area.delete("1.0", tk.END)
        output_area.insert(tk.END, "Book could not be downloaded.\n")


## GUI Setup ----------------

#first we initialize database
initialize_database()

#Create GUI window
window = tk.Tk()
window.configure(bg="#008080")
window.title("Gutenberg Word Frequency Tool")

#Labels and Inputs
tk.Label(window, text="Enter Book Title:", bg="#008080", fg="white").grid(row=0, column=0, sticky="w")
title_entry = tk.Entry(window, width=50, bg="White", fg="#006064")
title_entry.grid(row=0, column=1)

tk.Label(window, text="Enter Gutenberg .txt URL:", bg="#008080", fg="white").grid(row=1, column=0, sticky="w")
url_entry = tk.Entry(window, width=50, bg="white", fg="#006064")
url_entry.grid(row=1, column=1)

#Buttons
tk.Button(window, text="Search by Title", command=on_search_title, bg = "#0097A7", fg="white").grid(row=2, column=0, pady=5)
tk.Button(window, text="Fetch from URL", command=on_fetch_from_url, bg = "#0097A7", fg="white").grid(row=2, column=1, pady=5)

#Output area
output_area = tk.Text(window, width=60, height = 15, bg="white", fg="#006064")
output_area.grid(row=3, column=0, columnspan=2, pady=10)

#run the GUI loop
window.mainloop()


# https://www.gutenberg.org/cache/epub/64317/pg64317.txt

""" OPTIONAL TESTING
if __name__ == '__main__':
    initialize_database()
    print("the database was initiallized")

    #opitional test
    sample = "TESTING THE CASES!!!!!!!!!!"
    print("Sample word counts:", get_top_words(sample))

    #download and save book from Gutenberg
    url = "https://www.gutenberg.org/cache/epub/37106/pg37106.txt"
    title = "Little Women"
    book_text = download_book(url)
    if book_text:
        top_words = get_top_words(book_text)
        save_to_database(title, top_words)
    else:
        print("nah")

    #Search the database for the book
    results = search_database(title)
    if results:
        print(f"\nTop words for '{title}' from the database:")
        for word, freq in results:
            print(f"{word}: {freq}")
    else:
        print(f"'{title}' not found in the database.")
        
"""
