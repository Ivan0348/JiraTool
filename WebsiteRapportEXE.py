import webbrowser
from flask import Flask, render_template_string
from tkinter import filedialog, Tk
from utils import sum_time, get_max_title_length, display_assignee_totals, display_results

app = Flask(__name__)
totals = {}
tag_items = {}

HTML_TEMPLATE = """ 

<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jira Report</title>
    <link href="https://cdn.datatables.net/1.10.16/css/jquery.dataTables.min.css" rel="stylesheet">
    <style>
        /* Algemene body stijl */
        body {
            font-family: 'Myriad Pro', sans-serif;
            background-color: #f4f5f7;
            margin: 0;
            padding: 0;
            color: #172b4d;
        }

        h1, h2, h3 {
            color: #357de8;
            font-weight: normal;
        }

        h1 {
            text-align: center;
            margin-top: 40px;
            font-size: 32px;
        }

        h2 {
            margin-top: 30px;
            font-size: 24px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h3 {
            margin-top: 20px;
            font-size: 20px;
        }

        .section {
            background-color: #ffffff;
            border-radius: 8px;
            margin: 20px auto;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            width: 95%;
            max-width: 1600px;
        }

        /* Tabel styling */
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e1e4e8;
        }

        th {
            background-color: #f4f5f7;
            color: #172b4d;
            font-weight: normal;
        }

        tr:hover {
            background-color: #f1f3f5;
        }

        /* Specifieke stijlen voor de kolommen */
        td {
            color: #6b778c;
        }

        td:first-child, th:first-child {
            font-weight: bold;
            color: #357de8;
        }

        /* Style voor lege tijd ("-") */
        td:empty {
            color: #dfe1e6;
        }

        /* Stijl voor footer */
        footer {
            text-align: center;
            margin-top: 40px;
            font-size: 14px;
            color: #6b778c;
        }

        .toggle-icon {
            font-size: 18px;
            color: #357de8;
            cursor: pointer;
        }

        /* Initiale stijl voor de inhoud: verborgen */
        .toggle-content {
            display: none;
        }

        .max_height {
            max-height: 100px;
            overflow: hidden;
            cursor: pointer;
        }

    </style>
    <script>
        function toggleSection(tag) {
            let section = document.getElementById(tag + "-content");
            let icon = document.getElementById(tag + "-icon");
            if (section.style.display === "none") {
                section.style.display = "block";
                icon.innerHTML = "&#9660;"; // Omlaag-pijl
            } else if (section.style.display === "") {
                section.style.display = "block";
                icon.innerHTML = "&#9660;"; // Omlaag-pijl
            } else {
                section.style.display = "none";
                icon.innerHTML = "&#9654;"; // Rechts-pijl
            }
        }
    </script>
</head>
<body>
 <div class="container">
    <h1>Jira Report</h1>

    <!-- Totale tijd per persoon over alle tags -->
    <div class="section">
        <h2>Totale tijd per persoon</h2>
        <table>
            <thead>
                <tr>
                    <th>Assignee</th>
                    <th>Totale tijd</th>
                </tr>
            </thead>
            {% set assignee_totals = {} %}
            {% for tag, assignees in totals.items() %}
                {% for assignee, total_time in assignees.items() %}
                    {% if assignee != '' %}
                        {% set minutes = (total_time.split('h')[0]|int) * 60 + (total_time.split('h')[1].replace('m', '')|int) %}
                        {% set _ = assignee_totals.update({assignee: assignee_totals.get(assignee, 0) + minutes}) %}
                    {% endif %}
                {% endfor %}
            {% endfor %}
            <tbody>
                {% for assignee, total_minutes in assignee_totals.items() | sort %}
                <tr>
                    <td>{{ assignee }}</td>
                    <td>{{ total_minutes // 60 }}h {{ total_minutes % 60 }}m</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <!-- Details per tag -->
    {% for tag, items in tag_items.items() %}
    <div class="section">
        <div onclick="toggleSection('{{ tag }}')" class="max_height">
            <h2>{{ tag }}
                <span class="toggle-icon" id="{{ tag }}-icon">&#9654;</span>
            </h2>
        </div>
        <div class="toggle-content" id="{{ tag }}-content">
            <table class="dataframe" id="datatable2">
                <thead>
                    <tr>
                        <th>Assignee</th>
                        <th>Title</th>
                        <th>Time Spent</th>
                        <th>Original Estimate</th>
                        <th>Work Ratio</th>
                        <th>Status</th>
                        <th>Issue</th>
                        <th>Sprint</th>
                    </tr>
                </thead>
                <tbody>
                {% for assignee, title, time_spent, original_estimate, work_ratio, status, issue, issue_with_url, sprint in items | sort(attribute='1') | sort(attribute='0') %}
                    <tr>
                        <td>{{ assignee or 'NONE' }}</td>
                        <td>{{ title or '-' }}</td>
                        <td>{% if time_spent %}{{ time_spent // 60 }}h {{ time_spent % 60 }}m{% else %}-{% endif %}</td>
                        <td>{{ original_estimate or '-' }}</td>
                        <td>{{ work_ratio }}</td>
                        <td>{{ status or '-' }}</td>
                        <td>
                            {% if issue %}
                                <a href="{{ issue_with_url }}" target="_blank">{{ issue }}</a>
                            {% else %}
                                -
                            {% endif %}
                    </td>
                        <td>{{ sprint or '-' }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>

            <!-- Totale tijd per assignee per tag (onder de takenlijst) -->
            <h3>Totale tijd per persoon voor {{ tag }}</h3>
            <table>
                <thead>
                    <tr>
                        <th>Assignee</th>
                        <th>Totale tijd</th>
                    </tr>
                </thead>
                <tbody>
                {% for assignee, total_time in totals[tag].items() | sort %}
                    <tr>
                        <td>{{ assignee or 'NONE' }}</td>
                        <td>{{ total_time }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endfor %}

    <footer>
        <p>&copy; 2025 Jira Report - Alle rechten voorbehouden.</p>
    </footer>
    <script src="https://code.jquery.com/jquery-1.12.4.js" type="text/javascript"></script>
    <script src="https://cdn.datatables.net/1.10.16/js/jquery.dataTables.min.js" type="text/javascript"></script>
    <script type="text/javascript">
        $(document).ready(function() {
            $('table.dataframe').each(function() {
                 $(this).DataTable({
                    "paging": false,
                    "info": false,
                    "lengthChange": false
                });
            });
        });
    </script>
 </div>
</body>
</html>

 """


@app.route("/")
def index():
    """Render de resultaten op een webpagina."""
    return render_template_string(HTML_TEMPLATE, totals=totals, tag_items=tag_items)


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
