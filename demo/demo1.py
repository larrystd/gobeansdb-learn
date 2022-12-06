import libmc


mc = libmc.Client(['localhost:7900'])
mc.set(" d", "bar")
print(mc.get(" d"))
