import sys, json, math, os
from mpi4py import MPI
from pymongo import MongoClient

user_id = sys.argv[1]
db_name = sys.argv[2]
table_name = sys.argv[3]
field = sys.argv[4]

MONGO_URL = os.getenv("MONGO_URL", "mongodb://mongodb_core:27017")
client = MongoClient(MONGO_URL)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()
chunks = None

if rank == 0:
    database_name = db_name if db_name.startswith(f"{user_id}_") else f"{user_id}_{db_name}"
    db = client[database_name]
    collection = db[table_name]
    
    documents = list(collection.find({}, {field: 1, "_id": 0}))
    values = [doc[field] for doc in documents if field in doc and isinstance(doc[field], (int, float))]
    
    chunk_size = math.ceil(len(values) / size) if size > 0 else 0
    chunks = [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
    while len(chunks) < size: chunks.append([])

local_data = comm.scatter(chunks, root=0)
local_sum = sum(local_data)
total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)

if rank == 0:
    print(json.dumps({"total": total_sum}))