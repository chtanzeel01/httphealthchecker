import yaml
import requests
import time
import signal
import sys

# Global variables
endpoints = []
domain_availability = {}


def load_configuration(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def health_check():
    global domain_availability
    availability = {}
    for endpoint in endpoints:
        try:
            response = requests.request(
                method=endpoint.get('method', 'GET'),
                url=endpoint['url'],
                headers=endpoint.get('headers', {}),
                data=endpoint.get('body', None),
                timeout=5  # Set an appropriate timeout for the HTTP request
            )

            if 200 <= response.status_code < 300 and response.elapsed.total_seconds() < 0.5:
                status = "UP"
            else:
                status = "DOWN"
        except Exception as e:
            status = "DOWN"
        
        domain = endpoint['url'].split('//')[1].split('/')[0]
        availability[domain] = availability.get(domain, 0) + (1 if status == "UP" else 0)

    return availability


def log_availability():
    global domain_availability
    for domain, count in domain_availability.items():
        percentage = round((count / len(endpoints)) * 100)
        print(f"{domain} has {percentage}% availability percentage")


def signal_handler(sig, frame):
    print("Exiting the program.")
    sys.exit(0)


def main():
    global endpoints, domain_availability

    if len(sys.argv) != 2:
        print("Usage: python script.py <configuration_file_path>")
        sys.exit(1)

    configuration_file_path = sys.argv[1]

    signal.signal(signal.SIGINT, signal_handler)

    try:
        endpoints = load_configuration(configuration_file_path)

        while True:
            domain_availability = health_check()
            log_availability()
            time.sleep(15)

    except KeyboardInterrupt:
        print("Exiting the program.")


if __name__ == "__main__":
    main()
