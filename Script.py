import csv
from collections import defaultdict
import re
import tkinter
from tkinter import filedialog


def parse_time(time_str):
    """
    Converteert tijdstrings zoals '1h 30m' naar minuten.
    """
    if not time_str:
        return 0
    hours = sum(int(x[:-1]) * 60 for x in re.findall(r'\d+h', time_str))
    minutes = sum(int(x[:-1]) for x in re.findall(r'\d+m', time_str))
    return hours + minutes


def extract_tag(title):
    """
    Haalt de tag uit de titel, bijvoorbeeld: '[PVA]: Task description' -> 'PVA'.
    """
    match = re.search(r'\[(.*?)]:', title)
    return match.group(1) if match else "Other"  # Standaard naar 'Other' als er geen tag is


def sum_time(csv_file):
    """
    Leest een CSV-bestand en somt de tijd op per assignee en per tag.
    """
    tag_times = defaultdict(lambda: defaultdict(int))  # {tag: {assignee: minutes}}
    tag_items = defaultdict(list)  # {tag: [(assignee, title, time_spent, original_estimate, status, issue, sprint)]}

    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('Title', '')
                tag = extract_tag(title)
                assignee = row.get('Assignee', 'Unknown')
                time_spent = parse_time(row.get('Time spent', '0m'))
                original_estimate = row.get('Original estimate', 'N/A')
                status = row.get('Status', 'N/A')
                issue = row.get('Issue', 'N/A')
                sprint = row.get('Sprint', 'N/A')

                tag_times[tag][assignee] += time_spent
                tag_items[tag].append((assignee, title, time_spent, original_estimate, status, issue, sprint))

    except Exception as e:
        print(f"Error reading file: {e}")
        return {}, {}

    # Converteer de tijden terug naar uren en minuten
    formatted_times = {
        tag: {assignee: f"{time // 60}h {time % 60}m" for assignee, time in assignees.items()}
        for tag, assignees in tag_times.items()
    }

    return formatted_times, tag_items


def get_max_title_length(tag_items):
    """
    Bepaal de maximale lengte van de titel per tag.
    """
    max_lengths = {}
    for tag, items in tag_items.items():
        max_lengths[tag] = max(len(item[1]) for item in items) + 2  # Het tweede item is de titel
    return max_lengths


def display_assignee_totals(pva_totals):
    """
    Print het totaal van de tijd per assignee.
    """
    assignee_totals = defaultdict(int)  # {assignee: total_minutes}

    for tag, assignees in pva_totals.items():
        for assignee, time_str in assignees.items():
            hours, minutes = map(int, time_str[:-1].split('h'))
            total_minutes = hours * 60 + minutes
            assignee_totals[assignee] += total_minutes

    # Print de totale tijd per assignee
    print("### Totale tijd per persoon ###")
    for assignee, total_minutes in assignee_totals.items():
        print(f"{assignee}: {total_minutes // 60}h {total_minutes % 60}m")


def display_results(tag_items, max_title_lengths):
    """
    Geeft de resultaten netjes weer, inclusief tijd per taak en relevante details.
    """
    for tag, items in tag_items.items():
        print(f"\n### {tag} ###")

        # Sorteren van taken per assignee en title
        sorted_items = sorted(items, key=lambda x: (x[0], x[1]))  # Sorteren op assignee en daarna op title

        # Maximale titel lengte per tag
        max_title_length = max_title_lengths.get(tag, 40)

        # Weergave van taken met alle relevante velden en uitlijning
        for assignee, title, time_spent, original_estimate, status, issue, sprint in sorted_items:
            print(f"- {assignee:<12} | {title:<{max_title_length}} | "
                  f"Time spent: {time_spent // 60:>3}h {time_spent % 60:>2}m | "
                  f"Original estimate: {original_estimate or '-':<10} | "
                  f"Status: {status:<12} | "
                  f"Issue: {issue:<10} | "
                  f"Sprint: {sprint or 'None':<20} |")


def main():
    # Open file dialog
    root = tkinter.Tk()
    root.withdraw()
    csv_file = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])

    if csv_file:  # Check of er een bestand is geselecteerd
        pva_totals, tag_items = sum_time(csv_file)
        if pva_totals:
            # Bepaal de maximale titel lengte per tag
            max_title_lengths = get_max_title_length(tag_items)

            # Toon de totale tijd per assignee
            display_assignee_totals(pva_totals)

            for tag, assignees in pva_totals.items():
                print(f"\n### Totale tijd voor {tag} ###")
                for assignee, total_time in assignees.items():
                    print(f"{assignee}: {total_time}")

            # Toon gedetailleerde taakinformatie per tag
            display_results(tag_items, max_title_lengths)
        else:
            print("Geen relevante taken gevonden.")
    else:
        print("Geen bestand geselecteerd.")


if __name__ == "__main__":
    main()
