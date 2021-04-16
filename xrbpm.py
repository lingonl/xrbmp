#!/usr/bin/env python3

import collections, liblo, math, sys, time, warnings

len(sys.argv) == 3 or sys.exit(f'🖖usage: {sys.argv[0]} host bpm')

host    = sys.argv[1]
bpm     = max(int(sys.argv[2]), 1)

P = collections.namedtuple('P', ['fx', 'par', 'min', 'max', 'slope', 'units'])

def hertz(bpm):
    return bpm / 60

def seconds(bpm):
    return 60 / bpm

def linf(p, v): 
    return (v - p.min) / (p.max - p.min)

def logf(p, v):
    return math.log(v / p.min) / math.log(p.max / p.min)


tunables = [
    P(10, 2, 0.001, 3, linf, seconds),
    P(11, 1, 0.001, 3, linf, seconds),
    P(12, 1, 0.001, 3, linf, seconds),
    P(13, 1, 0.05,  5, logf, seconds),
    P(14, 1, 0.05,  5, logf, seconds),
    P(15, 1, 0.05,  5, logf, seconds),
    P(18, 1, 0.1,   4, logf, hertz),
    P(19, 1, 0.05,  5, logf, hertz),
    P(21, 1, 0.001, 3, linf, seconds),
    P(22, 1, 0.05,  4, logf, hertz),
    P(23, 1, 0.05,  4, logf, hertz),
    P(24, 1, 0.001, 3, linf, seconds),
    P(25, 1, 0.001, 3, linf, seconds),
    P(26, 1, 0.001, 3, linf, seconds),
]

response = None
def receive(*args):
    global response
    print('🎚', args[0], *args[1])
    response = args[1]

def send(*args, recv=True):
    global server, host, response
    
    print('🖥', *args)

    server.send(liblo.Address(host, 10024, liblo.UDP), *args)
    
    if not recv: return True
    
    server.recv(5000) or sys.exit(f'❌{args[0]}')

    return response

warnings.filterwarnings('ignore', category=DeprecationWarning)

server = liblo.Server()
server.add_method(None, None, receive)

send('/status')

for n in [1, 2, 3, 4]:
    (fx, na) = send(f'/fx/{n}')

    for p in tunables:
        if p.fx != fx: continue

        v = p.units(bpm)
        while v < p.min: v *= 2
        while v > p.max: v /= 2
        vosc = p.slope(p, v)

        send(f'/fx/{n}/par/{p.par:02}', vosc, recv=False)
