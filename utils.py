import csv
import re
from collections import defaultdict


def parse_time(time_str):
    """Convert time strings like '1h 30m' to total minutes."""
    hours, minutes = 0, 0
    if 'h' in time_str:
        hours = int(time_str.split('h')[0].strip())
        time_str = time_str.split('h')[1]
    if 'm' in time_str:
        minutes = int(time_str.split('m')[0].strip())
    return hours * 60 + minutes


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
    tag_original_estimates = defaultdict(lambda: defaultdict(int))  # {tag: {assignee: original_estimate_minutes}}
    tag_items = defaultdict(list)  # {tag: [(assignee, title, time_spent, original_estimate, status, issue, sprint)]}

    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                title = row.get('Title', '')
                tag = extract_tag(title.upper())
                assignee = row.get('Assignee', 'Unknown')
                time_spent = parse_time(row.get('Time spent', '0m'))
                original_estimate = parse_time(row.get('Original estimate', 'N/A'))
                work_ratio = work_ratio_time_to_percentage(row.get('Work Ratio', '-'))
                status = row.get('Status', 'N/A')
                issue = row.get('Issue', 'N/A')
                issue_with_url = "https://my-lex.atlassian.net/browse/" + issue
                sprint = row.get('Sprint', 'N/A')
                title_without_tag = ':'.join(title.split(':')[1:]).strip()

                tag_times[tag][assignee] += time_spent
                tag_original_estimates[tag][assignee] += original_estimate
                tag_items[tag].append((assignee, title_without_tag, time_spent, original_estimate, work_ratio,
                                       status, issue, issue_with_url, sprint))
    except Exception as e:
        print(f"Error reading file: {e}")
        return {}, {}

    # Converteer de tijden terug naar uren en minuten
    formatted_times = {
        tag: {assignee: f"{time // 60}h {time % 60}m" for assignee, time in assignees.items()}
        for tag, assignees in tag_times.items()
    }

    formatted_original_estimates = {
        tag: {assignee: f"{time // 60}h {time % 60}m" for assignee, time in assignees.items()}
        for tag, assignees in tag_original_estimates.items()
    }

    return formatted_times, formatted_original_estimates, tag_items


def get_max_title_length(items):
    """
    Bepaal de maximale lengte van de titel per tag.
    """
    max_lengths = {}
    for tag, items in items.items():
        max_lengths[tag] = max(len(item[1]) for item in items) + 2  # Het tweede item is de titel
    return max_lengths


def display_assignee_totals(item_totals):
    """
    Print het totaal van de tijd per assignee.
    """
    assignee_totals = defaultdict(int)  # {assignee: total_minutes}

    for tag, assignees in item_totals.items():
        for assignee, time_str in assignees.items():
            if assignee != '':
                hours, minutes = map(int, time_str[:-1].split('h'))
                total_minutes = hours * 60 + minutes
                assignee_totals[assignee] += total_minutes

    # Print output
    print("### Totale tijd per persoon ###")
    for assignee, total_minutes in assignee_totals.items():
        if assignee != '':
            print(f"{assignee}: {total_minutes // 60}h {total_minutes % 60}m")


def work_ratio_time_to_percentage(time_str):
    """
    Converteert een tijd-string naar een werk ratio percentage.
    """
    if time_str == "":
        return '-'
    else:
        minutes, seconds = 0, 0
        if 'm' in time_str:
            minutes = int(time_str.split('m')[0].strip())
            time_str = time_str.split('m')[-1].strip()
        if 's' in time_str:
            seconds = int(time_str.replace('s', '').strip())

        percentage = (minutes * 60) + seconds
        return f"{percentage:.2f}%"


def display_results(items, max_title_lengths):
    """
    Geeft de resultaten weer op de console.
    """
    for tag, items in items.items():
        print(f"\n### {tag} ###")

        # Sorteren van taken per assignee en title
        sorted_items = sorted(items,
                              key=lambda x: (x[0].upper(), x[1].upper()))  # Sorteren op assignee en daarna op title

        # Maximale titel lengte per tag
        max_title_length = max_title_lengths.get(tag, 40)

        for assignee, title, time_spent, original_estimate, work_ratio, status, issue, issue_with_url, sprint in sorted_items:
            time_display = f"{time_spent // 60:>3}h {time_spent % 60:>2}m" if time_spent > 0 else "-"

            print(f"- {assignee:<12} | {title:<{max_title_length}} | "
                  f"Time spent: {time_display:<10} | "
                  f"Original estimate: {original_estimate or '-':<15} | "
                  f"Work ratio: {work_ratio or '-':<10} | "
                  f"Status: {status or '-':<12} | "
                  f"Issue: {issue_with_url or '-'} | "
                  f"Sprint: {sprint or '-':<20}")
