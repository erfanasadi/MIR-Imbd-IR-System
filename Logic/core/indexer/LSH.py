import numpy as np
import itertools
import random


class MinHashLSH:
    def __init__(self, documents, num_hashes):
        """
        Initialize the MinHashLSH

        Parameters
        ----------
        documents : list of str
            The input documents for similarity analysis.
        num_hashes : int
            Number of hashes for mini-hashing.
        """
        self.documents = documents
        self.num_hashes = num_hashes

    def shingle_document(self, document, k=2):
        """
        Convert a document into a set of shingles.

        Parameters
        ----------
        document : str
            The input document.
        k : int
            The size of each shingle.

        Returns
        ----------
        set
            A set of shingles.
        """
        shingles = set()

        if document["summaries"] is not None :
         for summary in document["summaries"]:
          words = summary.split()
          for i in range(len(words) - k + 1):
            shingle = ' '.join(words[i:i + k])
            shingles.add(shingle)
        return shingles

    def build_characteristic_matrix(self):
        """
        Build the characteristic matrix representing the presence of shingles in documents.

        Returns
        ----------
        numpy.ndarray
            The binary characteristic matrix.
        """
        # Create an empty set to store all unique shingles across all documents
        all_shingles_set = set()

        # Iterate through each document to collect all unique shingles
        for doc in self.documents:

            shingles = self.shingle_document(doc)
            print(shingles)
            all_shingles_set.update(shingles)

        # Sort the set of all shingles to maintain consistent ordering
        all_shingles_list = sorted(all_shingles_set)

        # Initialize the characteristic matrix with zeros
        char_matrix = np.zeros((len(self.documents), len(all_shingles_list)), dtype=int)

        # Create a mapping from shingle to its index in the matrix
        shingle_to_index = {shingle: i for i, shingle in enumerate(all_shingles_list)}

        # Iterate through each document and update the matrix based on shingle presence
        for i, doc in enumerate(self.documents):
            shingles = self.shingle_document(doc)
            for shingle in shingles:
                j = shingle_to_index[shingle]
                char_matrix[i, j] = 1

        return char_matrix

    def min_hash_signature(self):
        """
        Perform Min-Hashing to generate hash signatures for documents.

        Returns
        ----------
        numpy.ndarray
            The Min-Hash signatures matrix.
        """
        char_matrix = self.build_characteristic_matrix()
        print(char_matrix)
        num_docs, num_shingles = char_matrix.shape
        print(num_docs,num_shingles)
        # Generate random permutations for hashing
        permutations = [np.random.permutation(num_shingles) for _ in range(self.num_hashes)]

        signatures = np.full((self.num_hashes, num_docs), np.inf)

        for i in range(num_docs):
            doc_shingles = char_matrix[i, :]
            for j in range(self.num_hashes):
                # Find the first shingle hashed to 1 for this permutation
                idx = np.where(doc_shingles[permutations[j]] == 1)[0]
                if len(idx) > 0:
                    signatures[j, i] = idx[0]

        return signatures

    def lsh_buckets(self, signature, bands=20, rows_per_band=5):
        """
        Group documents into Locality-Sensitive Hashing (LSH) buckets based on Min-Hash signatures.

        Parameters
        ----------
        signature : numpy.ndarray
            Min-Hash signatures for documents.
        bands : int
            Number of bands for LSH.
        rows_per_band : int
            Number of rows per band.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """
        num_docs = signature.shape[1]
        buckets = {}

        for band in range(bands):
            # Generate hash values for each band
            band_hashes = {}
            for doc_idx in range(num_docs):
                band_signature = signature[band * rows_per_band: (band + 1) * rows_per_band, doc_idx]
                print("bs",band_signature)
                band_hash = hash(tuple(band_signature))
                if band_hash in band_hashes:
                    band_hashes[band_hash].append(doc_idx)
                else:
                    band_hashes[band_hash] = [doc_idx]
            print("bandhash",band_hashes)
            # Add documents to buckets based on band hashes
            for band_hash, doc_indices in band_hashes.items():
                bucket_id = (band, band_hash)
                if bucket_id in buckets:
                    buckets[bucket_id].extend(doc_indices)
                else:
                    buckets[bucket_id] = doc_indices
        print(len(buckets.items()))
        return buckets

    def perform_lsh(self):
        """
        Perform the entire Locality-Sensitive Hashing (LSH) process using Jaccard similarity.

        Returns
        ----------
        dict
            A dictionary mapping bucket IDs to lists of document indices.
        """
        # Generate Min-Hash signatures for documents
        signatures = self.min_hash_signature()
        print(signatures)
        # Perform Locality-Sensitive Hashing (LSH) to group documents into buckets
        buckets = self.lsh_buckets(signatures)
        print(buckets)

        # Create a dictionary to store similar document pairs within buckets
        similar_pairs = {}

        # Iterate through each bucket
        print(buckets.items())
        for bucket_id, doc_indices in buckets.items():
            # Iterate through pairs of documents in the bucket
            for i in range(len(doc_indices)):
                for j in range(i + 1, len(doc_indices)):
                    doc1_idx = doc_indices[i]
                    doc2_idx = doc_indices[j]
                    print(doc2_idx,doc2_idx)
                    # Calculate Jaccard similarity between documents
                    doc1_set = self.shingle_document(self.documents[doc1_idx])
                    doc2_set = self.shingle_document(self.documents[doc2_idx])
                    jaccard_similarity = self.jaccard_score(doc1_set, doc2_set)

                    # If Jaccard similarity is above a threshold (e.g., 0.5), consider them similar
                    if jaccard_similarity > 0.5:
                        
                        # Add the pair of similar documents to the dictionary
                        if bucket_id in similar_pairs:
                            similar_pairs[bucket_id].append((doc1_idx, doc2_idx))
                        else:
                            similar_pairs[bucket_id] = [(doc1_idx, doc2_idx)]

        return similar_pairs

    def jaccard_score(self, first_set, second_set):
        """
        Calculate Jaccard score for two sets.

        Parameters
        ----------
        first_set : set
            Set of the first shingled document.
        second_set : set
            Set of the second shingled document.

        Returns
        ----------
        float
            Jaccard score.
        """
        intersection_size = len(first_set.intersection(second_set))
        union_size = len(first_set.union(second_set))

        if union_size == 0:
            return 0  # handle edge case where both sets are empty

        return intersection_size / union_size

    def jaccard_similarity_test(self, buckets, all_documents):
        """
        Test your near duplicate detection code based on jaccard similarity.

        Parameters
        ----------
        buckets : dict
            A dictionary mapping bucket IDs to lists of document indices.
        all_documents : list
            The input documents for similarity analysis.
        """
        correct_near_duplicates = 0
        all_near_duplicates = 0
        print("test",buckets)
        for bucket_id in buckets.keys():
            docs_in_this_bucket = buckets[bucket_id]
            unique_doc_ids = set(docs_in_this_bucket)
            print(unique_doc_ids)
            if len(unique_doc_ids) >= 1:

                for comb in unique_doc_ids:
                    all_near_duplicates += 1

                    first_doc_id = comb[0]
                    second_doc_id = comb[1]

                    first_shingled_doc = self.shingle_document(all_documents[first_doc_id], 2)
                    second_shingled_doc = self.shingle_document(all_documents[second_doc_id], 2)

                    near_duplicated_jaccard_score = self.jaccard_score(first_shingled_doc, second_shingled_doc)
                    current_score = 0

                    for _ in range(5):
                        random_doc_id = random.randint(0, len(all_documents) - 1)
                        while random_doc_id == first_doc_id or random_doc_id == second_doc_id:
                            random_doc_id = random.randint(0, len(all_documents) - 1)
                        random_shingled_doc = self.shingle_document(all_documents[random_doc_id], 2)

                        random_jaccard_score = self.jaccard_score(first_shingled_doc, random_shingled_doc)

                        if near_duplicated_jaccard_score > random_jaccard_score:
                            current_score += 1

                    if current_score == 5:
                        correct_near_duplicates += 1
        print(correct_near_duplicates,all_near_duplicates)
        # a good score is around 0.8
        print("your final score in near duplicate detection:", correct_near_duplicates / all_near_duplicates)
