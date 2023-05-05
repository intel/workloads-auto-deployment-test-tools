import requests
import json

class DeployDashboard ():
    grafana_server_host = "127.0.0.1"
    grafana_server_port = "3000"
    grafana_api_key = ""
    grafana_request_headers = {}
    grafana_datasource_name = "PostgreSQL"
    grafana_datasource_data = {}
    dashboard_json_file_path = "../conf/dashboard.json"
    
    postgres_server_host = "127.0.0.1"
    postgres_server_port = "5432"
    postgres_db_name = "taas"
    postgres_user = "postgres"

    old_uid = "old_uid"

    def __init__(self):
        self.set_grafana_conf()

    def grafana_api_test (self, url, headers):
        try:
            response = requests.get(f'{url}/datasources', headers = headers).json()
            if type(response) is dict and response['message'] == 'invalid API key':
                return False
            else:
                return True
        except Exception as e:
            print(e)
            return False

    def set_grafana_conf (self):
        print('\n# Set grafana configs')
        self.grafana_api_key = input('## Please input grafana api key:\n')
        self.grafana_api_url = f'http://{self.grafana_server_host}:{self.grafana_server_port}/api'
        while True:
            if self.grafana_api_key == "exit":
                exit()
            self.grafana_request_headers = {
                'Authorization': 'Bearer ' + self.grafana_api_key,
                'Content-Type': 'application/json'
            }
            print('## Check availability of grafana api')
            if self.grafana_api_test(self.grafana_api_url, self.grafana_request_headers):
                print('-- Grafana api is OK to use!')
                break
            else:
                print('-- Grafana api cannot be used.')
                self.grafana_api_key = input("## Please config API key again...[type \"exit\" to exit]\n")
                continue

    def set_grafana_datasource_data (self):
        self.grafana_datasource_data = {
            "name": self.grafana_datasource_name,
            "type": "postgres",
            "url": f'{self.postgres_server_host}:{self.postgres_server_port}',
            "access": "proxy",
            "user": self.postgres_user,
            "isDefault": True,
            "database": self.postgres_db_name,
            "basicAuth": False,
            "jsonData": {
                "postgresVersion": 903,
                "sslmode": "disable",
                "tlsAuth": False,
                "tlsAuthWithCACert": False,
                "tlsConfigurationMethod": "file-path",
                "tlsSkhostVerify": True
            }
        }
    
    def create_datasource (self):
        print("\n# Create grafana datasource")
        self.set_grafana_datasource_data()
        datasource_endpoint = f'{self.grafana_api_url}/datasources'
        print("## Delete datasource has the same name if exists")
        try:
            delete_datasource_if_exists_response = requests.delete(
                f'{datasource_endpoint}/name/{self.grafana_datasource_name}',
                headers = self.grafana_request_headers
            )
            print("-- Cleaning has been done.")
        except Exception as e:
            print(e)
        try:
            print("## Create grafana datasource as default config")
            create_datasource_response = requests.post(
                datasource_endpoint,
                headers = self.grafana_request_headers,
                data = json.dumps(self.grafana_datasource_data)
            ).json()
            print("-- Datasource has been created successfully!")
        except Exception as e:
            print("-- Problems occurred:")
            print(e)

    def get_uid_of_datasource_by_name (self):
        print('## Get uid of the created data source')
        uid_endpoint = f'{self.grafana_api_url}/datasources/name/{self.grafana_datasource_name}'
        uid_response = requests.get(
            uid_endpoint,
            headers = self.grafana_request_headers
        ).json()
        uid = uid_response['uid']
        return uid

    def replace_uid_in_dashboard_json (self, old_uid, new_uid):
        with open('%s' % self.dashboard_json_file_path, 'r') as file:
            data = file.read()
            data = data.replace(old_uid, new_uid)
        with open('%s' % self.dashboard_json_file_path, 'w') as file:
            file.write(data)
        file.close()

    def import_dashboard_json (self):
        print('## Import dashboard json to grafana')
        with open('%s' % self.dashboard_json_file_path, 'r') as file:
            dashboard_json = json.loads(file.read())
        file.close()
        dashboard_endpoint = f'{self.grafana_api_url}/dashboards/db'
        try:
            create_dashboard_response = requests.post(
                dashboard_endpoint,
                headers = self.grafana_request_headers,
                data = json.dumps(dashboard_json)
            ).json()
            print('-- Json has been imported successfully!')
        except Exception as e:
            print('-- Problems occurred:')
            print(e)
        
    def create_dashboard (self):
        print('\n# Create grafana dashboard')
        old_uid = self.old_uid
        new_uid = self.get_uid_of_datasource_by_name()
        print('-- new_uid: ' + new_uid)
        try:
            self.replace_uid_in_dashboard_json(old_uid, new_uid)
        except Exception as e:
            print("-- Problems occurred:")
            print(e)
        try:
            self.import_dashboard_json()
        except Exception as e:
            print("-- Problems occurred:")
            print(e)
        try:
            self.replace_uid_in_dashboard_json(new_uid, old_uid)
        except Exception as e:
            print("-- Problems occurred:")
            print(e)

if __name__ == "__main__":
    deploy_dashboard = DeployDashboard()
    deploy_dashboard.create_datasource()
    deploy_dashboard.create_dashboard()