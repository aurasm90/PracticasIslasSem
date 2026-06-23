import json

with open("datos/expedientes_vistos.json", "r", encoding="utf-8") as f:
    v1 = json.load(f)

with open("datos/licitaciones_v2.json", "r", encoding="utf-8") as f:
    v2 = json.load(f)

ids_v1 = set(l["id"] for l in v1)
ids_v2 = set(l["id"] for l in v2)

print(f"Total v1: {len(ids_v1)}")
print(f"Total v2: {len(ids_v2)}")
print(f"En v1 pero no en v2: {len(ids_v1 - ids_v2)}")
print(f"En v2 pero no en v1: {len(ids_v2 - ids_v1)}")
print(f"En ambos: {len(ids_v1 & ids_v2)}")
