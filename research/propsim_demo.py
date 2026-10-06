# Challenge geçme olasılığı vs işlem başı risk: basit Monte Carlo (PLAN.md bölüm 2.3)
import numpy as np
rng=np.random.default_rng(1)
def sim(risk,p=0.45,R=1.55,target=0.10,maxdd=0.10,daily=0.05,tpd=2,N=20000,maxdays=120):
    ok=0
    for _ in range(N):
        eq=1.0
        for d in range(maxdays):
            start=eq
            for t in range(tpd):
                eq+= risk*(R if rng.random()<p else -1)
                if eq<=1-maxdd or eq<=start-daily: break
            if eq>=1+target: ok+=1;break
            if eq<=1-maxdd or eq<=start-daily: break
    return ok/N
for r in [0.0025,0.005,0.0075,0.01,0.015,0.02,0.03]:
    print(f"{r*100:.2f}% -> {sim(r):.3f}")
print("edge 0 (p=0.392):")
for r in [0.005,0.01,0.02]:
    print(f"{r*100:.2f}% -> {sim(r,p=1/2.55):.3f}")
