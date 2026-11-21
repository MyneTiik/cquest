# CQuest

Jeu de révision du langage C dans le terminal : tu écris du **vrai code**, le jeu le compile avec
`gcc -Wall -Werror -std=c99` et le passe à des tests. Construit sur le modèle de BashQuest, avec un
contenu qui suit le cours « programmation C » (de la compilation aux listes chaînées).

## Installation (Linux / WSL)

```bash
sudo apt update && sudo apt install -y build-essential gdb valgrind python3 git
cd ~
git clone https://github.com/MyneTiik/cquest.git
cd cquest
./cquest            # ou : python3 cquest.py
```

Clone le dépôt dans le home Linux (`~`), pas dans `/mnt/c/...`.

## Contenu

- Python 3 sans dépendance + gcc (valgrind conseillé pour les missions sur malloc).
- **109 missions** sur 15 thèmes : programmes testés avec des arguments / une entrée, fonctions testées
  par un main caché, chasses aux bugs, QCM et questions « qu'affiche ce code ? ».
- Chaque mission de code a son dossier `~/.cquest/atelier/<mission>/` : tu y édites ton fichier
  (nano, vim, `code`...) et ton travail est gardé d'une session à l'autre.
  La progression est dans `~/.cquest/sauvegarde.json`.
- **Apprentissage** (menu 0) : pour chaque thème un cours en cartes avec des exemples de code que l'on
  compile et lance d'un appui sur Entrée (ou qu'on modifie avec `e`), une méthode, puis des exos guidés.
- Modes : campagne (15 niveaux, étoiles, indices payants), partie rapide, examens chronométrés
  (express 15 min, contrôle 30 min, examen blanc 1 h, personnalisé ; le code compte double),
  par thème, mes erreurs, fiches de révision.
- Dans une mission de code : `:verifier`, `:editer`, `:voir`, `:essai` (crée un main de test),
  `:indice`, `:solution`, `:fiche`, `:methode`, `:reset`, `:passer`, `:menu`, `:aide`.
  Toute autre ligne est une commande bash lancée dans le dossier de la mission
  (`nano somme.c`, `gcc -Wall -std=c99 somme.c -o somme`, `./somme 3 4`, `valgrind ./essai`...).
- `CQUEST_TOUT=1 ./cquest` débloque tous les niveaux de la campagne.

## Ajouter des missions

Dans `missions.py` / `missions2.py`, avec `prog`, `fonc`, `qcm` et `rep`.
Puis `python3 verif_missions.py` vérifie tout : le fichier de départ ne passe pas les tests, la solution
les passe, la sortie des questions « qu'affiche... » est la bonne, et chaque exemple du cours compile.
