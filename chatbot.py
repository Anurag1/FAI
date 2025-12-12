from core.engine import FractalEngine
engine = FractalEngine()
while True:
    q = input('> ')
    print(engine.encode(q))
