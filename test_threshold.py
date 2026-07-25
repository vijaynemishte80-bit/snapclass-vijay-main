import numpy as np
from src.database.db import get_all_students

students = get_all_students()

for i in range(len(students)):
    for j in range(i+1, len(students)):
        emb1 = np.array(students[i]['face_embedding'])
        emb2 = np.array(students[j]['face_embedding'])
        distance = np.linalg.norm(emb1 - emb2)
        print(f"{students[i]['name']} vs {students[j]['name']}: {distance:.3f}")