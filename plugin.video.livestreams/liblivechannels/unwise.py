"""
06.06.21 Boogie, no license
this is direct port from js may suck in the performance but who cares
tested only with ascii, most likely will shit with unicode texts
"""


def unwise(w, i, s, e):
    var1 = 0
    var2 = 0
    var3 = 0
    var4 = []
    var5 = []
    while True:
        if var1 < 5:
            var5.append(w[var1])
        elif var1 < len(w):
            var4.append(w[var1])
        var1 += 1

        if var2 < 5:
            var5.append(i[var2])
        elif var2 < len(i):
            var4.append(i[var2])
        var2 += 1

        if var3 < 5:
            var5.append(s[var3])
        elif var3 < len(s):
            var4.append(s[var3])
        var3 += 1

        if (len(w) + len(i) + len(s) + len(e) == len(var4) + len(var5) + len(e)):
            break

    var6 = "".join(var4)
    var7 = "".join(var5)
    var2 = 0
    var8 = []
    for var1 in range(0, len(var4), 2):
        var9 = -1
        if ord(var7[var2]) % 2:
            var9 = 1
        var8.append(chr(int(var6[var1:var1 + 2], 36) - var9))

        var2 += 1
        if var2 >= len(var5):
            var2 = 0

    return "".join(var8)
