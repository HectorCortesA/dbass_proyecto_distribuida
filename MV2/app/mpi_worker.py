import sys, json, math, os
from mpi4py import MPI
from pymongo import MongoClient

user_id = sys.argv[1]
db_name = sys.argv[2]
table_name = sys.argv[3]
raw_field = sys.argv[4]

if raw_field.startswith("AVG:"):
    op = "avg"
    field = raw_field.split(":", 1)[1]
elif raw_field.startswith("COUNT"):
    op = "count"
    field = ""
else:
    op = "sum"
    field = raw_field

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
    
    if op == "count":
        documents = list(collection.find({}, {"_id": 1}))
        chunk_size = math.ceil(len(documents) / size) if size > 0 else 0
        chunks = [documents[i:i + chunk_size] for i in range(0, len(documents), chunk_size)]
        while len(chunks) < size: chunks.append([])
    else:
        documents = list(collection.find({}, {field: 1, "_id": 0}))
        values = [doc[field] for doc in documents if field in doc and isinstance(doc[field], (int, float))]
        chunk_size = math.ceil(len(values) / size) if size > 0 else 0
        chunks = [values[i:i + chunk_size] for i in range(0, len(values), chunk_size)]
        while len(chunks) < size: chunks.append([])

local_data = comm.scatter(chunks, root=0)

if op == "count":
    local_count = len(local_data)
    total_count = comm.reduce(local_count, op=MPI.SUM, root=0)
    if rank == 0:
        print(json.dumps({"count": total_count}))
elif op == "avg":
    local_sum = sum(local_data)
    local_count = len(local_data)
    total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)
    total_count = comm.reduce(local_count, op=MPI.SUM, root=0)
    if rank == 0:
        avg_val = (total_sum / total_count) if total_count > 0 else 0
        print(json.dumps({"average": avg_val}))
else:
    local_sum = sum(local_data)
    total_sum = comm.reduce(local_sum, op=MPI.SUM, root=0)
    if rank == 0:
        print(json.dumps({"total": total_sum}))