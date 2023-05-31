from typing import Iterable


class ManagerBase:
    def __init__(self):
        if self.manager_name is None:
            self.manager_name = "ManagerBase"
        print("Init Manager -> ({name})".format(name=self.manager_name))

    def dispose(self):
        print("Disposing Manager -> ({name})".format(name=self.manager_name))
        pass

    def get_auctions(self):
        print("Getting auctions with Manager -> ({name})".format(name=self.manager_name))
        pass

    def filter_auctions(self, auctions_to_remove: list[str]):
        print("Filtering auctions for Manager -> ({name})".format(name=self.manager_name))
        pass

    def get_items_raw(self, is_my_items: bool):
        print("Getting all items for ({name})".format(name=self.manager_name))
        pass

    def load_from_file(self, f: Iterable[str]):
        print("Loading all items on file for ({name})".format(name=self.manager_name))

    def filter_items(self, keywords_to_filter: list[str]):
        print("Filtering items for ({name})".format(name=self.manager_name))
        pass

    def refresh_items(self):
        print("Refreshing items for ({name})".format(name=self.manager_name))
        pass

    def refresh_items_select(self):
        print("Refreshing select items for ({name})".format(name=self.manager_name))
        pass