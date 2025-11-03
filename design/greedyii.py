import matplotlib.pyplot as plt
from math import sqrt

def shortest_path(nums):
    nums_len=len(nums)
    visited_nodes = {0}
    best_index=0
    best=float('inf')
    path=[]
    path.append(nums[0])
    i=1
    while len(path)<nums_len:
      (n, m)=nums[i]
      if i in visited_nodes:
        i += 1
        i %= nums_len
        continue

      dist = distance((n, m), path[len(path)-1])
      if dist < best:
          best = dist
          best_index = i
      else:
          visited_nodes.add(best_index)
          best = float('inf')
          path.append(nums[best_index])

      i+=1
      i%=nums_len
    return path

def distance(num1, num2):
  return sqrt((num1[0] - num2[0])**2 + (num1[1] - num2[1])**2)

nums = [(20, 20), (20, 160), (20, 40), (30, 120), (40, 140), (40, 150), (50, 20), (60, 40), (60, 80), (60, 200), (70, 200), (80, 150), (90, 170), (90, 170), (100, 50), (100, 40), (100, 130), (100, 150), (110, 10), (110, 70), (120, 80), (130, 70), (130, 170), (140, 140), (140, 180), (150, 50),  (160, 20), (170, 100), (180, 70), (180, 200), (200, 30), (200, 70), (200, 100)]
print(shortest_path(nums))

plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
x, y = zip(*nums)
plt.scatter(x, y, marker='o', color='blue')
for i, p in enumerate(nums):
    plt.text(p[0]+2, p[1]+2, str(i), fontsize=8)
plt.title("Orden inicial")
plt.grid(True)

path=shortest_path(nums)
plt.subplot(1,2,2)
px, py = zip(*path)
plt.plot(px, py, marker='o', color='red')
for i, p in enumerate(path):
    plt.text(p[0]+2, p[1]+2, str(i), fontsize=8)
plt.title("Camino greedy")
plt.grid(True)
plt.tight_layout()
plt.show()

nums = [
  (10, 20), (20, 35), (30, 60), (40, 80), (50, 15),
  (60, 40), (70, 75), (80, 55), (90, 95), (100, 30),
  (15, 120), (25, 140), (35, 160), (45, 180), (55, 200),
  (65, 125), (75, 145), (85, 165), (95, 185), (105, 195),
  (120, 20), (130, 40), (140, 60), (150, 80), (160, 100),
  (120, 130), (130, 150), (140, 170), (150, 190), (160, 120),
  (170, 30), (180, 50), (190, 70), (200, 90), (175, 110),
  (180, 140), (190, 160), (200, 180), (170, 150), (160, 180),
  (15, 15), (25, 25), (35, 35), (45, 45), (55, 55),
  (100, 100), (110, 110), (120, 120), (130, 130), (140, 140)
]
print(shortest_path(nums))

plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
x, y = zip(*nums)
plt.scatter(x, y, marker='o', color='blue')
for i, p in enumerate(nums):
    plt.text(p[0]+2, p[1]+2, str(i), fontsize=8)
plt.title("Orden inicial")
plt.grid(True)

path=shortest_path(nums)
plt.subplot(1,2,2)
px, py = zip(*path)
plt.plot(px, py, marker='o', color='red')
for i, p in enumerate(path):
    plt.text(p[0]+2, p[1]+2, str(i), fontsize=8)
plt.title("Camino greedy")
plt.grid(True)
plt.tight_layout()
plt.show()