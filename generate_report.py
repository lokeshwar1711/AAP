import yaml
import re

def read_expected_versions(input_file_path):
    expected_versions = {}
    with open(input_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(':')
            if len(parts) == 2:
                parameter, version = parts
                try:
                    expected_versions[parameter.strip()] = float(version.strip())
                except ValueError:
                    print(f"Warning: Unable to convert version to float for line: {line}")
            else:
                print(f"Warning: Skipping improperly formatted line: {line}")
    return expected_versions

def extract_version(version_str):
    match = re.search(r"(\d+\.\d+)", version_str)
    if match:
        return float(match.group(1))
    return None

def generate_html_report(yaml_file_path, html_output_path, input_file_path):
    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)

    expected_versions = read_expected_versions(input_file_path)

    # Extract hostnames and parameters
    hosts = list(data.keys())
    parameters = list(data[hosts[0]].keys())

    # Start HTML content
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Agent Status and Versions Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .running { background-color: #d4edda; } /* Green background */
            .inactive { background-color: #f8d7da; } /* Red background */
            .version-good { background-color: #d4edda; } /* Green background */
            .version-bad { background-color: #f8d7da; } /* Red background */
        </style>
    </head>
    <body>
        <h1>Agent Status and Versions Report</h1>
        <table>
            <tr>
                <th>Parameter</th>
                <th>Baseline</th>
    """

    # Add table headers for each host
    for host in hosts:
        html_content += f"<th>Host: {host}</th>"
    
    html_content += "</tr>"

    # Helper function to determine the class for status cells
    def get_status_class(value):
        if 'inactive' in value.lower():
            return 'inactive'
        elif 'running' in value.lower() or 'active' in value.lower():
            return 'running'
        else:
            return ''

    # Helper function to determine the class for version cells
    def get_version_class(parameter, value):
        actual_version = extract_version(value)
        expected_version = expected_versions.get(parameter, None)
        if actual_version is not None and expected_version is not None:
            if actual_version >= expected_version:
                return 'version-good'
            else:
                return 'version-bad'
        return ''

    # Add table rows for each parameter
    for parameter in parameters:
        html_content += f"<tr><td>{parameter}</td>"
        baseline_value = expected_versions.get(parameter, 'N/A')
        html_content += f"<td>{baseline_value}</td>"
        for host in hosts:
            value = data[host].get(parameter, 'N/A')
            if 'status' in parameter.lower():
                status_class = get_status_class(value)
                html_content += f"<td class='{status_class}'>{value}</td>"
            elif 'version' in parameter.lower():
                version_class = get_version_class(parameter, value)
                html_content += f"<td class='{version_class}'>{value}</td>"
            else:
                html_content += f"<td>{value}</td>"
        html_content += "</tr>"

    # Close HTML content
    html_content += """
        </table>
    </body>
    </html>
    """

    # Write the HTML content to the output file
    with open(html_output_path, 'w') as file:
        file.write(html_content)

if __name__ == "__main__":
    yaml_file_path = "/var/www/html/agent-reports/report.yaml"
    html_output_path = "/var/www/html/agent-reports/report.html"
    input_file_path = "/var/www/html/agent-reports/agentVersions.txt"
    generate_html_report(yaml_file_path, html_output_path, input_file_path)
