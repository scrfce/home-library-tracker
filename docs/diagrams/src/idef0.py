"""IDEF0: контекстная диаграмма A-0 и декомпозиция A0 системы «ДомБиблиотека»."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import Rectangle

HALO = [pe.withStroke(linewidth=6, foreground="white")]

def poly(ax, pts, label=None, lpos=None, ha="center", va="bottom", fs=12, halo=False, z=4):
    xs, ys = zip(*pts)
    kw = dict(path_effects=HALO) if halo else {}
    ax.plot(xs, ys, color="black", lw=1.5, zorder=z, solid_joinstyle="miter", **kw)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), zorder=z+1,
                arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5, mutation_scale=15, shrinkA=0, shrinkB=0))
    if label:
        ax.text(lpos[0], lpos[1], label, ha=ha, va=va, fontsize=fs, zorder=z+2, linespacing=1.15)

def block(ax, x, y, w, h, text, num, fs=11.5):
    ax.add_patch(Rectangle((x, y), w, h, fc="white", ec="black", lw=2.0, zorder=3))
    ax.text(x+w/2, y+h/2+0.05, text, ha="center", va="center", fontsize=fs, fontweight="bold", zorder=4, linespacing=1.25)
    ax.text(x+w-0.12, y+0.1, num, ha="right", va="bottom", fontsize=10.5, zorder=4)

def setup(w, h, title, fsz):
    fig, ax = plt.subplots(figsize=fsz, dpi=170)
    ax.set_xlim(0, w); ax.set_ylim(0, h); ax.axis("off"); ax.set_aspect("equal")
    ax.text(w/2, h-0.35, title, ha="center", va="center", fontsize=14, fontweight="bold")
    return fig, ax

# ---------------- A-0 ----------------
fig, ax = setup(27, 14.2, "IDEF0. Контекстная диаграмма A-0: «Управлять учётом и выдачей книг домашней библиотеки»", (14.6, 7.7))
bx, by, bw, bh = 8.0, 3.9, 10.0, 4.6
block(ax, bx, by, bw, bh, "Управлять учётом\nи выдачей книг\nдомашней библиотеки", "A0", fs=16)
ins = ["Данные регистрации\nи входа", "Сведения о книгах", "Запросы читателей", "Данные о выдаче\nи возврате"]
for i, t in enumerate(ins):
    y = by + bh - 0.7 - i*1.2
    poly(ax, [(0.4, y), (bx, y)], t, (0.5, y+0.1), ha="left")
for t, x in [("Права доступа\nпо ролям", bx+1.7), ("Правила библиотеки\n(сроки, лимиты, поля)", bx+5.0), ("Требования\nFR и NFR", bx+8.3)]:
    poly(ax, [(x, by+bh+1.8), (x, by+bh)], t, (x, by+bh+1.9))
for t, x in [("Владелец\nи Читатель", bx+1.7), ("Веб-приложение\n«ДомБиблиотека»", bx+5.0), ("Почтовый сервис", bx+8.3)]:
    poly(ax, [(x, by-1.8), (x, by)], t, (x, by-1.9), va="top")
outs = ["Актуальный каталог\nкниг", "Список запросов\nдля Владельца", "Журнал выдач, списки\n«на руках», «мои книги»", "Письма-напоминания\nо возврате"]
for i, t in enumerate(outs):
    y = by + bh - 0.7 - i*1.2
    poly(ax, [(bx+bw, y), (bx+bw+2.2, y)], t, (bx+bw+2.35, y), ha="left", va="center")
fig.savefig("../idef0-a-0.png", bbox_inches="tight", pad_inches=0.15, facecolor="white")
plt.close(fig)

# ---------------- A0 ----------------
fig, ax = setup(36, 18.4, "IDEF0. Диаграмма декомпозиции A0: основные функции системы «ДомБиблиотека»", (18.2, 8.8))
W, H = 4.6, 2.0
X = [4.6, 9.8, 15.0, 20.2, 25.4]
Y = [12.8, 10.1, 7.4, 4.7, 2.0]
names = ["Управлять доступом\nпользователей", "Вести каталог\nкниг", "Обрабатывать\nзапросы читателей", "Оформлять выдачу\nи возврат книг", "Контролировать\nсроки и отправлять\nнапоминания"]
for i in range(5):
    block(ax, X[i], Y[i], W, H, names[i], "A%d" % (i+1), fs=11.4)
mid = [y+H/2 for y in Y]
FS = 11.8

# boundary inputs (left)
poly(ax, [(0.2, mid[0]), (X[0], mid[0])], "Данные регистрации\nи входа", (0.3, mid[0]+0.1), ha="left", fs=FS)
for i, t in [(1, "Сведения о книгах"), (2, "Запросы читателей"), (3, "Данные о выдаче\nи возврате")]:
    poly(ax, [(0.2, mid[i]-0.5), (X[i], mid[i]-0.5)], t, (0.3, mid[i]-0.62), ha="left", va="top", fs=FS)

# boundary controls (short stubs on top)
poly(ax, [(X[0]+2.1, Y[0]+H+1.0), (X[0]+2.1, Y[0]+H)], "Права доступа\nпо ролям", (X[0]+2.1, Y[0]+H+1.1), fs=FS)
poly(ax, [(X[1]+3.3, Y[1]+H+0.8), (X[1]+3.3, Y[1]+H)], "Требования FR и NFR", (X[1]+3.3, Y[1]+H+0.9), fs=FS)
poly(ax, [(X[3]+4.0, Y[3]+H+0.6), (X[3]+4.0, Y[3]+H)], "Правила выдачи\n(срок, один получатель)", (X[3]+4.0, Y[3]+H+0.7), fs=FS)
poly(ax, [(X[4]+4.0, Y[4]+H+0.6), (X[4]+4.0, Y[4]+H)], "График проверки сроков\n(1 раз в сутки)", (X[4]+4.0, Y[4]+H+0.7), fs=FS)

# A1 -> A2, A3 : права пользователя (control, branching)
bus = Y[0]+H-1.1
poly(ax, [(X[0]+W, bus), (X[1]+0.9, bus), (X[1]+0.9, Y[1]+H)], None)
poly(ax, [(X[1]+0.9, bus), (X[2]+4.1, bus), (X[2]+4.1, Y[2]+H)], None)
ax.text(X[0]+W+0.2, bus+0.12, "Права пользователя", fontsize=FS, ha="left", va="bottom", zorder=8)

# internal input flows
def step(i, label, wlabel=2.6):
    x0 = X[i]+W; gx = x0+0.3
    y0 = mid[i]-0.5; y1 = mid[i+1]+0.5
    poly(ax, [(x0, y0), (gx, y0), (gx, y1), (X[i+1], y1)], None)
    ax.text(gx+0.15, Y[i+1]+H+0.35, label, fontsize=FS, ha="left", va="center", zorder=8)
step(1, "Статус книги")
step(2, "Запрос на выдачу")
step(3, "Сроки возврата")

# boundary outputs (right); only first one needs a halo (crosses control branch)
R = 31.0
poly(ax, [(X[1]+W, mid[1]+0.5), (R, mid[1]+0.5)], "Актуальный каталог книг", (R+0.15, mid[1]+0.5), ha="left", va="center", fs=FS, halo=True, z=6)
poly(ax, [(X[2]+W, mid[2]+0.5), (R, mid[2]+0.5)], "Список запросов\nдля Владельца", (R+0.15, mid[2]+0.5), ha="left", va="center", fs=FS)
poly(ax, [(X[3]+W, mid[3]+0.5), (R, mid[3]+0.5)], "Журнал выдач, списки\n«на руках», «мои книги»", (R+0.15, mid[3]+0.5), ha="left", va="center", fs=FS)
poly(ax, [(X[4]+W, mid[4]), (R, mid[4])], "Письма-напоминания\nо возврате", (R+0.15, mid[4]), ha="left", va="center", fs=FS)

# mechanisms (short stubs below)
for i, t in enumerate(["Веб-приложение\n«ДомБиблиотека»", "Владелец", "Читатель\nи Владелец", "Владелец", "Почтовый сервис"]):
    x = X[i]+1.4
    poly(ax, [(x, Y[i]-0.9), (x, Y[i])], t, (x, Y[i]-1.0), va="top", fs=FS)
fig.savefig("../idef0-a0.png", bbox_inches="tight", pad_inches=0.15, facecolor="white")
