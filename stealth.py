import random
import string

#
# This module fills memory with random data and pieces of code
# It avoids any anti-cheat program to be able to detect this hack by looking at fixed memory locations
#
def rand_letters(len):
    return "".join([random.choice(string.letters) for x in xrange(len)]) #@UnusedVariable

for i in range(random.randint(2,1024)):
    name = "RAND_" + rand_letters(random.randint(8,24))
    val = rand_letters(random.randint(16,1000))
    exec "%s = '%s'" % (name, val)
