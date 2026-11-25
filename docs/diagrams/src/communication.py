"""Диаграмма кооперации (Communication Diagram): оформление выдачи книги (UC-10)."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(14, 7.4), dpi=170)
ax.set_xlim(0, 22); ax.set_ylim(0, 11.2); ax.axis("off"); ax.set_aspect("equal")
ax.text(11, 10.9, "Диаграмма кооперации: оформление выдачи книги (UC-10)", ha="center", fontsize=14, fontweight="bold")

BW, BH = 3.2, 1.0
OBJ = {
 "ow": (":Владелец", "«актор»", 1.9, 5.2),
 "lc": (":LoanController", "", 7.6, 5.2),
 "ls": (":LoanService", "", 13.6, 5.2),
 "rs": (":RequestService", "", 19.5, 5.2),
 "lr": (":LoanRepository", "", 13.6, 9.2),
 "b":  (":Book", "", 13.6, 1.2),
}
for k,(name, st, x, y) in OBJ.items():
    ax.add_patch(FancyBboxPatch((x-BW/2, y-BH/2), BW, BH, boxstyle="round,pad=0.02,rounding_size=0.12",
                                fc="#EEF4FB", ec="#1F3A5F", lw=1.6, zorder=3))
    ax.text(x, y+(0.12 if st else 0), name, ha="center", va="center", fontsize=13, fontweight="bold", zorder=4)
    if st: ax.text(x, y-0.28, st, ha="center", va="center", fontsize=9, color="#444", zorder=4)

def pt(k): return OBJ[k][2], OBJ[k][3]
def edge_pt(k, other):
    x,y = pt(k); ox,oy = pt(other)
    dx,dy = ox-x, oy-y
    t = min((BW/2)/abs(dx) if dx else 1e9, (BH/2)/abs(dy) if dy else 1e9)
    return x+dx*t, y+dy*t

# links (lines between objects)
for a,b in [("ow","lc"),("lc","ls"),("ls","rs"),("ls","b"),("ls","lr")]:
    p, q = edge_pt(a,b), edge_pt(b,a)
    ax.plot([p[0],q[0]],[p[1],q[1]], color="#1F3A5F", lw=1.6, zorder=2)

# messages: (from, to, text, side)  side=+1/-1 offset to the left/right of direction
MSG = [
 ("ow","lc","1: issueBook(bookId, borrower, dueDate)", +1),
 ("lc","ow","8: showMessage(«Книга выдана»)", +1),
 ("lc","ls","2: issue(bookId, borrower, dueDate)", +1),
 ("ls","lc","7: return loan", +1),
 ("ls","b","3: isAvailable()", +1),
 ("ls","b","5: changeStatus(ON_LOAN)", -1),
 ("ls","lr","4: save(loan)", -1),
 ("ls","rs","6: closeRequests(bookId)", +1),
]
for a,b,txt,side in MSG:
    p, q = edge_pt(a,b), edge_pt(b,a)
    dx,dy = q[0]-p[0], q[1]-p[1]; L = math.hypot(dx,dy); ux,uy = dx/L, dy/L
    nx,ny = -uy, ux   # left normal
    off = 0.34*side
    mx,my = (p[0]+q[0])/2, (p[1]+q[1])/2
    sx,sy = mx-ux*0.55+nx*off, my-uy*0.55+ny*off
    ex,ey = mx+ux*0.55+nx*off, my+uy*0.55+ny*off
    ax.annotate("", xy=(ex,ey), xytext=(sx,sy), zorder=5,
                arrowprops=dict(arrowstyle="-|>", lw=1.6, color="#C0392B", shrinkA=0, shrinkB=0, mutation_scale=16))
    vertical = abs(uy) > 0.5
    if vertical:
        sgn = nx*side
        tx,ty = mx+nx*(off+0.3*side), my
        ha = "left" if sgn > 0 else "right"
        ax.text(tx, ty, txt, ha=ha, va="center", fontsize=12, zorder=6)
    else:
        tx,ty = mx+nx*(off+0.42*side), my+ny*(off+0.42*side)
        ax.text(tx, ty, txt, ha="center", va="center", fontsize=12, zorder=6)
fig.savefig("../communication.png", bbox_inches="tight", pad_inches=0.15, facecolor="white")
