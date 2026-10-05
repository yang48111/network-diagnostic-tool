import matplotlib.pyplot as plt


x = [1, 2, 3, 4, 5]

y = [10, 15, 12, 80, 14]


plt.plot(x, y)

plt.xlabel("Sequence")
plt.ylabel("Latency (ms)")
plt.title("Network Latency")

plt.show()