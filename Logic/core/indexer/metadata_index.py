from index_reader import Index_reader
from indexes_enum import Indexes, Index_types
import json

class Metadata_index:
    def __init__(self, path=''):
        """
        Initializes the Metadata_index.

        Parameters
        ----------
        path : str
            The path to the indexes.
        """
        self.document_reader = Index_reader(path, Indexes.DOCUMENTS)
        self.documents = self.read_documents()
        self.metadata_index = self.create_metadata_index()

    def read_documents(self):
        """
        Reads the documents.

        Returns
        -------
        list
            A list of documents.
        """
        return self.document_reader.index

    def create_metadata_index(self):
        """
        Creates the metadata index.
        """
        metadata_index = {}
        metadata_index['average_document_length'] = {
            'stars': self.get_average_document_field_length('stars'),
            'genres': self.get_average_document_field_length('genres'),
            'summaries': self.get_average_document_field_length('summaries')
        }
        metadata_index['document_count'] = len(self.documents)
        return metadata_index

    def get_average_document_field_length(self, field):
        """
        Returns the average length of the field in all documents in the index.

        Parameters
        ----------
        field : str
            The field to get the document lengths for.

        Returns
        -------
        float
            The average length of the field in all documents.
        """

        total_length=0
        for doc in self.documents.values():

            if doc[field] is not None:

             for str in doc[field]:
                total_length+=len(str)

        return total_length / len(self.documents)

    def store_metadata_index(self, path):
        """
        Stores the metadata index to a file.

        Parameters
        ----------
        path : str
            The path to the directory where the indexes are stored.
        """
        path = path + Indexes.DOCUMENTS.value + '_' + Index_types.METADATA.value + '.json'
        with open(path, 'w') as file:
            json.dump(self.metadata_index, file, indent=4)


if __name__ == "__main__":
    meta_index = Metadata_index("./indexes/")
    meta_index.store_metadata_index("./indexes/")
