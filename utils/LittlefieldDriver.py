import mechanize
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re

class LittlefieldDriver:
    '''
    A driver for the Littlefield simulation game that can access
    & interact with the game state.

    Inspired by the code & methodology from Greg Lewis's 2017 Medium post
    about connecting Littlefield data to Tableau via Python

    @Author: Spencer Elkington
    '''

    def __init__(self, config, secrets):

        self.base_address = config["GAME_ADDRESS"]
        self.name = config["GAME_NAME"]
        self.browser: mechanize.Browser = None
        self.logged_in = False
        self.historical_data = None
        
        try:
            self.login(
                address = secrets["LITTLEFIELD_ADDRESS"],
                username = secrets["LITTLEFIELD_USERNAME"],
                password = secrets["LITTLEFIELD_PASSWORD"]
            )
        except Exception as e:
            raise Exception(f"An error occured while logging into Littlefield: {e}")

        self.supply_graph = self.build_graph(config["nodes"])

    def login(self, address, username, password):
        # Initialize web driver & login
        self.browser: mechanize.Browser = mechanize.Browser()
        self.browser.open(address)

        self.browser.select_form(nr=0)
        self.browser.form['id'] = str(username)
        self.browser.form['password'] = str(password)
        self.browser.submit()

        self.browser.open(f'{self.base_address}/CheckAccess')

    def build_graph(self, node_list):

        graph: nx.DiGraph = nx.DiGraph()

        # Add all nodes to graph.
        for node_name, node_attrs in node_list.items():

            alias = node_name
            if "alias" in node_attrs.keys():
                alias = node_attrs["alias"]

            node = LittlefieldNode(
                self.browser,
                self.base_address,
                node_name,
                alias
            )

            graph.add_node(
                node_name,
                name = alias,
                node = node
            )

        # Create parent-child connections
        for node_name, relationships in node_list.items():
            if (relationships 
                and "children" in relationships.keys()
                and not relationships["children"] is None):

                for child_name in relationships["children"]:
                    graph.add_edge(node_name, child_name)

        return graph

    def draw_graph(self, output_location):
        labels = nx.get_node_attributes(self.supply_graph, 'name') 
        pos = nx.spring_layout(self.supply_graph, k = 500)

        nx.draw(
            self.supply_graph,
            labels = labels,
            node_size = 8000,
            pos = pos
        )

        plt.gcf().set_size_inches(11, 8.5)
        plt.savefig(output_location, dpi=150)
        return


    def fetch_data(self) -> pd.DataFrame:
        dfs = {}
        for name, attributes in self.supply_graph.nodes.items():
            node = attributes["node"]
            node_data = node.fetch_data()

            dfs[name] = node_data

        df = pd.DataFrame()
        for name, sub_df in dfs.items():
            # If it's the first DataFrame being added, use it
            # as the initial dataframe.
            if len(df) == 0:
                df = sub_df
            else:
                df = pd.concat([df, sub_df], axis=1)

        return df

    def data(self, refresh = False):
        if refresh or not self.historical_data:
            return self.fetch_data()
        else:
            return self.historical_data



class LittlefieldNode:
    '''
    A member of the LittlefieldDriver class used to access data from a
    specific node in the manufacturing graph
    '''

    def __init__(
        self,
        browser: mechanize.Browser,
        base: str,
        extension: str,
        alias: str
    ):

        self.browser = browser
        self.base_address = base
        self.extension = extension
        self.address = f"{base}/{extension}"
        self.alias = alias

    def fetch_data(self) -> pd.DataFrame:
        # Open node's webpage
        self.browser.open(self.address)
        response = str(self.browser.response().read())

        # Fetch information from main window
        stats_dict = self.get_page_statistics(response)

        # Get extended node data
        data_dict = self.scrape_data_pages(response)

        df = pd.DataFrame()
        for label, series in data_dict.items():
            if len(df) == 0:
                df = pd.DataFrame(series, columns=[label])
            else:
                df[label] = series

        for label, point in stats_dict.items():
            adj_label = f"{self.alias.upper()}_{label}"
            if len(df) == 0:
                df = pd.DataFrame([point], columns=[adj_label])
            else:
                df[adj_label] = point

        return df

    def get_page_statistics(self, mainpage_response):

        # Fetch & clean lines of data
        lines = mainpage_response.split(r"\n")
        data_lines = [line for line in lines if "<BR>" in line]
        data_lines = [re.sub("<.{1,4}>", "", line).strip() for line in data_lines]

        # Remove final button
        data_lines = data_lines[:-1]

        # Convert numerical observation to float type, and code-ize the
        # data labels.
        data = {}
        for line in data_lines:
            split_line = line.split(":")

            # If the observation doesn't have two parts, skip it
            if len(split_line) != 2:
                continue

            label = split_line[0]
            point = split_line[1]

            number_matches = re.findall(
                "([0-9]+\.?[0-9]*|\.[0-9]+)",
                point
            )

            # Clean datapoint
            if len(number_matches) > 0:
                point = float(number_matches[0])
            else:
                point = point.strip()

            # Clean Label
            label = label.replace(" ", "_").upper()
            data[label] = point

        return data


    def scrape_data_pages(self, mainpage_response):

        # Scrape node page for dataset URL extensions
        dataset_extensions = [
            ext
            for ext in re.findall(
                pattern = r"Plot\?data=[A-Z0-9]+&x=all",
                string = mainpage_response
            )
        ]

        # Prepend the base Littlefield address to extensions
        dataset_addresses = [
            f"{self.base_address}/{ext}"
            for ext in dataset_extensions
        ]

        series_dict = {}
        # Create & populate 
        for i, addr in enumerate(dataset_addresses):
            self.browser.open(addr)
            dataset_resp = str(self.browser.response().read())

            # Find the substring of quoted numbers representing the
            # data for the subplot
            data = re.findall(
                r"\\\'[0-9. ]{2,}\\\'",
                dataset_resp
            )

            # Grab the specific data label from the page extension
            label = dataset_extensions[i][10:-6]

            # If data was found, parse it into a DataFrame and append it
            # as a new column to the dataframe
            if len(data) > 0:
                data = data[0][2:-2]
                series = self.parse_page_table(data, label)
                series_dict[label] = series

        return series_dict

    def parse_page_table(
        self,
        data_string: str,
        label: str
    ) -> pd.DataFrame:
        '''
        Parse the string of a Littlefield dataset into a Pandas Dataframe
        '''

        raw = data_string.split(" ")
        index = raw[0::2]
        data =  raw[1::2]
        data_array = np.array([index, data]).transpose()

        df = pd.DataFrame(
            data = data_array,
            columns = ["day", label]
        )

        # Convert types from string
        try:
            df["day"] = df["day"].astype(int)
            df[label] = df[label].astype(float)
            df = df.set_index("day")
        except ValueError as e:
            # Because *sometimes* the days are given as fractions
            # (for whatever reason >:( ), if an error occurs on int cast
            # then we have to compress the days to the same axis.

            # It's possible to work around this by casting to a float,
            # then casting to an int. This implicitly truncates fractional
            # dates down to the integer day on which a new inventory
            # purchase occurs
            #
            # Because these are aggregated by sum, this column is transformed
            # to represent the sum total of whatever quantity the fractional
            # date represents.
            #
            # TODO: Change this later in case sum is a garbage way of general
            # aggregation :)
            df["day"] = df["day"].astype(float)
            df[label] = df[label].astype(float)
            df["day"] = df["day"].astype(int)

            df = df.groupby(by="day").sum()

        return df
