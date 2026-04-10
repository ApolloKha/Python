case = {
    "T1": 40,
    "T2": 38,
    "T3": 60,
    "T4": 70,
    "T5": 50,

}
if 32 < case["T1"] < 50:
    print(f"A = {case['T1']}")
if 38 <= case["T2"] < 50:
    print(f"B = {case['T2']}")
if 59 < case["T3"] < 61:
    print(f"X = {case['T3']}")
else:
    print("Không có điều kiện nào thỏa")
 
print(f"case= {case}")