import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle, Circle

W, H = 24, 15.6
fig, ax = plt.subplots(figsize=(12, 7.8), dpi=200)
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
ax.set_aspect("equal")

EW, EH = 3.5, 1.0   # ellipse size
UC = {
 "01": ("Зарегистрироваться", 6.2, 14.0),
 "02": ("Войти в систему", 10.4, 14.0),
 "07": ("Просмотреть\nкаталог", 12.4, 12.0),
 "08": ("Найти книгу", 7.4, 9.3),
 "09": ("Просмотреть\nкарточку книги", 12.4, 9.6),
 "16": ("Запросить книгу", 8.0, 7.2),
 "17": ("Просмотреть\nмои книги", 8.0, 5.0),
 "14": ("Назначить\nкатегории и теги", 12.6, 4.9),
 "10": ("Оформить выдачу", 18.0, 11.0),
 "11": ("Оформить возврат", 18.0, 9.9),
 "12": ("Просмотреть книги\n«на руках»", 18.0, 8.8),
 "13": ("Просмотреть\nисторию выдач", 18.0, 7.7),
 "18": ("Просмотреть\nзапросы на книги", 18.0, 6.6),
 "04": ("Добавить книгу", 18.0, 5.5),
 "05": ("Редактировать\nкнигу", 18.0, 4.4),
 "06": ("Удалить книгу", 18.0, 3.3),
 "03": ("Пригласить\nчитателя", 18.0, 2.2),
 "15": ("Отправить\nнапоминание", 18.0, 1.2),
}
# ellipse height per node
def dims(k):
    return (EW, 1.0)

# boundary
ax.add_patch(Rectangle((4.0, 0.4), 16.0, 14.8, fill=False, lw=1.6, ec="#1f3a5f", zorder=1))
ax.text(4.25, 14.95, "Система «ДомБиблиотека»", fontsize=10, fontweight="bold", va="top", color="#1f3a5f")
ax.text(12, 15.5, "Диаграмма вариантов использования системы «ДомБиблиотека»", fontsize=11.5,
        fontweight="bold", ha="center", va="center")

def boundary_pt(c, other):
    cx, cy, a, b = c
    dx, dy = other[0]-cx, other[1]-cy
    t = 1/math.sqrt((dx/a)**2+(dy/b)**2)
    return (cx+t*dx, cy+t*dy)

def center(k):
    return (UC[k][1], UC[k][2])
def ell(k):
    return (UC[k][1], UC[k][2], EW/2, EH/2)

# actors
ACT = {
 "guest": ("Гость", 1.9, 14.0),
 "reader": ("Читатель", 1.9, 8.0),
 "owner": ("Владелец", 22.4, 12.8),
 "mail": ("Почтовый сервис\n(внешняя система)", 22.4, 1.6),
}
def draw_actor(x, y, label):
    ax.add_patch(Circle((x, y+0.95), 0.28, fill=False, lw=1.4, ec="black", zorder=3))
    ax.plot([x, x], [y+0.67, y-0.2], color="black", lw=1.4, zorder=3)
    ax.plot([x-0.5, x+0.5], [y+0.4, y+0.4], color="black", lw=1.4, zorder=3)
    ax.plot([x, x-0.45], [y-0.2, y-0.9], color="black", lw=1.4, zorder=3)
    ax.plot([x, x+0.45], [y-0.2, y-0.9], color="black", lw=1.4, zorder=3)
    ax.text(x, y-1.05, label, ha="center", va="top", fontsize=9.5, fontweight="bold")

for k, (lab, x, y) in ACT.items():
    draw_actor(x, y, lab)

STACK = {"10","11","12","13","18","04","05","06","03","15"}
def assoc(actor, uc):
    _, ax_, ay = ACT[actor]
    ac = (ax_, ay+0.3)
    if actor in ("owner","mail") and uc in STACK:
        e = ell(uc); p = (e[0]+e[2], e[1])
    else:
        p = boundary_pt(ell(uc), ac)
    ax.plot([ac[0], p[0]], [ac[1], p[1]], color="#333", lw=1.0, zorder=1)

for a, u in [("guest","01"),("reader","02"),("reader","07"),("reader","16"),("reader","17"),
             ("owner","02"),("owner","07"),("owner","10"),("owner","11"),("owner","12"),
             ("owner","13"),("owner","18"),("owner","04"),("owner","05"),("owner","06"),
             ("owner","03"),("owner","15"),("mail","15")]:
    assoc(a, u)

def rel(src, dst, kind, off=(0,0), lab_off=(0,0)):
    s, d = ell(src), ell(dst)
    p1 = boundary_pt(s, (d[0], d[1])); p2 = boundary_pt(d, (s[0], s[1]))
    ax.annotate("", xy=p2, xytext=p1, zorder=4,
                arrowprops=dict(arrowstyle="->", lw=1.1, ls=(0,(4,3)), color="#1f3a5f", shrinkA=0, shrinkB=0))
    mx, my = (p1[0]+p2[0])/2 + lab_off[0], (p1[1]+p2[1])/2 + lab_off[1]
    ax.text(mx, my, "«%s»" % kind, fontsize=8, ha="center", va="center", color="#1f3a5f",
            bbox=dict(fc="white", ec="none", pad=0.8), zorder=5)

rel("08","07","extend")
rel("09","07","extend")
rel("14","04","extend")
rel("14","05","extend")
rel("10","09","include", lab_off=(-0.3,0.55))
rel("16","09","include")

# ellipses on top
for k,(t,x,y) in UC.items():
    ax.add_patch(Ellipse((x,y), EW, EH, fc="#eef4fb", ec="#1f3a5f", lw=1.2, zorder=3))
    ax.text(x, y, t, ha="center", va="center", fontsize=8.6, zorder=6)
    dy = -0.38 if k in ("08","16","17") else 0.38
    ax.text(x-EW/2-0.05, y+dy, "UC-"+k, fontsize=6.3, color="#666", zorder=6, ha="right", va="center")

fig.savefig("../use-case.png", bbox_inches="tight", pad_inches=0.15, facecolor="white")
