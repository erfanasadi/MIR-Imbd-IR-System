# import index
# import json
# if __name__ == '__main__':
#  f = open('../IMDB_crawledP.json')
#  data = json.load(f)
#  data2=[]
#  for data1 in data.values():
#    data2.append(data1)
#
#  index=index.Index(data2)
#  index.store_index("./indexes/","stars")
#  index.store_index("./indexes/","summaries")
#  index.store_index("./indexes/", "genres")
#  index.store_index("./indexes/", "documents")
#  index.check_if_indexing_is_good("summaries")