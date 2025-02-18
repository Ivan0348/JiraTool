import webbrowser
from flask import Flask, render_template
from tkinter import filedialog, Tk
from utils import sum_time, get_max_title_length, display_assignee_totals, display_results

app = Flask(__name__)
totals = {}
tag_items = {}

@app.route("/")
def index():
    """Render de resultaten op een webpagina."""
    return render_template("indexDatatables.html", totals=totals, tag_items=tag_items)


def main():
    # Selecteer een CSV-bestand
    root = Tk()
    root.withdraw()
    csv_file = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])

    if csv_file:
        global totals, tag_items
        totals, tag_items = sum_time(csv_file)

        if totals:
            max_title_lengths = get_max_title_length(tag_items)
            display_assignee_totals(totals)
            display_results(tag_items, max_title_lengths)
            print("\nFlask-server gestart op http://127.0.0.1:5000/")
            webbrowser.open("http://127.0.0.1:5000/")
            app.run(debug=False)


if __name__ == "__main__":
    main()
