# 🔥 Red Demon Maze Game

**Red Demon Maze** on põnev 2D labürindi mäng Pythonis, kus pead põgenema punase deemoniga. Mäng on loodud **Pyglet** teegi abil ja sisaldab erinevaid level’e, taustamuusikat ja hirmutavaid jumpscare ekraane. (TÖÖTAB VSCODES!)

---

## 🎮 Mängu ülevaade

- 3 erinevat levelit
- A* vaenlane, kes sind jälitab
- Jumpscare ekraan, kui vaenlane kätte saab
- Lihtne labürindi graafika
- Taustamuusika ja sammude helid

---

## 🛠️ Nõuded

- Python 3.8 või uuem
- [Pyglet](https://pyglet.readthedocs.io/en/latest/) (`pip install pyglet`)

---

## 📂 Repo struktuur

red-demon-maze/
├─ main.py # Mängu peamine kood
├─ assets/ # Kõik pildid ja helid
│ ├─ lukama pilt.png # Start screen
│ ├─ jumpscare.jpg # Jumpscare pilt
│ ├─ jumpscare.wav.mp3 # Jumpscare heli
│ ├─ dark-horror-soundscape-345814.mp3 # Taustamuusika
│ └─ step-351163.mp3 # Sammude heli
└─ README.md # See fail

yaml
Copy code

> **Oluline:** assets kaust peab olema **samal tasemel kui `main.py`**, et kõik pildid ja helid töötaksid.

---

## ⚡ Kuidas mängu käivitada

1. Clone repo:

```bash
git clone https://github.com/username/red-demon-maze.git
cd red-demon-maze
Paigalda sõltuvus:

bash
Copy code
pip install pyglet
Käivita mäng:

bash
Copy code
python main.py
🎮 Mängukontrollid
Klahv	Funktsioon
W	Liigu üles
S	Liigu alla
A	Liigu vasakule
D	Liigu paremale
SPACE	Alusta mängu

