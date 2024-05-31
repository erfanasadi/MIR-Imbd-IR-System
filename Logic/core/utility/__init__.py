
# import json
# import LSH
# import preprocess
# if __name__ == '__main__':
#     f = open('LSHFakeData.json')
#     data = json.load(f)
#     lsh=LSH.MinHashLSH(data,100)
#     buckets=lsh.perform_lsh()
#     lsh.jaccard_similarity_test(buckets,data)
#
#     f = open('IMDB_crawled.json')
#     data = json.load(f)
#
#     preprocessor = preprocess.Preprocessor(data)
#     preprocessed_docs = preprocessor.preprocess()
#     f = open('IMDB_crawledP.json', "w")
#     json.dump(preprocessed_docs,f)


