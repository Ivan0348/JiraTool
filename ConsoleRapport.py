from tkinter import filedialog, Tk
from utils import sum_time, get_max_title_length, display_assignee_totals, display_results


def main():
    # Selecteer een CSV-bestand
    root = Tk()
    root.withdraw()
    csv_file = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])

    if csv_file:
        totals, tag_items = sum_time(csv_file)

        if totals:
            max_title_lengths = get_max_title_length(tag_items)
            display_assignee_totals(totals)
            display_results(tag_items, max_title_lengths)


if __name__ == "__main__":
    main()
