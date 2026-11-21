#!/usr/bin/env python3
"""CQuest : réviser le C en écrivant du vrai code.

Lancement :  python3 cquest.py   (ou ./cquest)
Chaque mission de code a son dossier dans ~/.cquest/atelier/<mission> : tu y édites
ton fichier (nano, vim, code...), le jeu le compile avec gcc -Wall -Werror -std=c99
et le passe à des tests. Ton travail y reste d'une session à l'autre.
"""
import datetime
import json
import os
import random
import re
import shlex
import shutil
import signal
import subprocess
import sys
import textwrap
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import readline  # historique et édition de ligne
except ImportError:  # pragma: no cover
    readline = None

from missions import MISSIONS, NIVEAUX, THEMES  # noqa: E402
from fiches import FICHES  # noqa: E402
from lecons import LECONS, PROGRAMME  # noqa: E402

VERSION = "1.0"
DATA = os.path.expanduser(os.environ.get("CQUEST_HOME", "~/.cquest"))
ATELIER = os.path.join(DATA, "atelier")
EXAMEN_DIR = os.path.join(DATA, "examen")
BUILD = os.path.join(DATA, "build")
COURS_DIR = os.path.join(DATA, "cours")
SAVE_FILE = os.path.join(DATA, "sauvegarde.json")

CFLAGS = ["-Wall", "-Werror", "-std=c99", "-g"]
BASE_POINTS = {1: 10, 2: 20, 3: 30, 4: 50}
FACTEUR_INDICE = [1.0, 0.6, 0.3]
SEUIL_DEBLOCAGE = 0.6
GCC = shutil.which("gcc")
VALGRIND = shutil.which("valgrind")

# --------------------------------------------------------------------------
# Couleurs et affichage
# --------------------------------------------------------------------------
COULEUR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code):
    return ("\033[" + code + "m") if COULEUR else ""


class C:
    R = _c("0")
    B = _c("1")
    DIM = _c("2")
    ROUGE = _c("31")
    VERT = _c("32")
    JAUNE = _c("33")
    BLEU = _c("34")
    MAG = _c("35")
    CYAN = _c("36")


def rl(code):
    """Code couleur protégé pour readline (le prompt garde la bonne largeur)."""
    if not code:
        return ""
    return "\001" + code + "\002" if readline else code


def titre(txt):
    print()
    print(C.B + C.CYAN + "━" * 64 + C.R)
    print(C.B + "  " + txt + C.R)
    print(C.B + C.CYAN + "━" * 64 + C.R)


def info(txt):
    print(C.DIM + txt + C.R)


def ok(txt):
    print(C.VERT + C.B + txt + C.R)


def ko(txt):
    print(C.ROUGE + C.B + txt + C.R)


def warn(txt):
    print(C.JAUNE + txt + C.R)


def bloc(txt, couleur=""):
    for ligne in txt.rstrip("\n").split("\n"):
        print(couleur + "  " + ligne + C.R)


def code_bloc(code, couleur=""):
    """Affiche du code C avec les numéros de ligne."""
    lignes = code.rstrip("\n").split("\n")
    for i, l in enumerate(lignes, 1):
        print(C.DIM + "  %3d │ " % i + C.R + couleur + l + C.R)


def demander(prompt):
    """input() qui renvoie None sur Ctrl-D et '' sur Ctrl-C."""
    try:
        return input(prompt)
    except EOFError:
        print()
        return None
    except KeyboardInterrupt:
        print()
        return ""


def pause(msg="Entrée pour continuer"):
    demander(C.DIM + msg + C.R + " ")


def editeur():
    return os.environ.get("VISUAL") or os.environ.get("EDITOR") or (
        "nano" if shutil.which("nano") else "vi")


# --------------------------------------------------------------------------
# Compilation et tests
# --------------------------------------------------------------------------
TESTLIB = r"""
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int tl_fail = 0, tl_total = 0;
static int tl_quiet = 0;
static void tl_init(void) { setvbuf(stdout, NULL, _IONBF, 0); tl_quiet = getenv("CQ_QUIET") != NULL; }
static void section(const char *s) { if (!tl_quiet) printf("-- %s\n", s); }
static void tl_ok(const char *d) { if (!tl_quiet) printf("   [ok] %s\n", d); }

#define CHECK_INT(expr, expected, desc) do { \
    long _e = (long)(expected); long _g = (long)(expr); tl_total++; \
    if (_g != _e) { tl_fail++; \
        printf("   [ECHEC] %s\n           attendu : %ld   obtenu : %ld\n", desc, _e, _g); } \
    else tl_ok(desc); } while (0)

#define CHECK_TRUE(cond, desc) do { tl_total++; \
    if (!(cond)) { tl_fail++; printf("   [ECHEC] %s\n", desc); } \
    else tl_ok(desc); } while (0)

static void check_str(const char *got, const char *exp, const char *desc) {
    tl_total++;
    if (got == NULL || strcmp(got, exp) != 0) {
        tl_fail++;
        printf("   [ECHEC] %s\n           attendu : \"%s\"\n           obtenu  : ", desc, exp);
        if (got) printf("\"%s\"\n", got); else printf("NULL\n");
    } else tl_ok(desc);
}
#define CHECK_STR(got, exp, desc) check_str((got), (exp), (desc))

static void tl_print_tab(const int *t, int n) {
    printf("{");
    for (int i = 0; i < n; i++) printf(i ? ", %d" : "%d", t[i]);
    printf("}");
}
static void check_tab(const int *got, const int *exp, int n, const char *desc) {
    tl_total++;
    int same = got != NULL;
    for (int i = 0; same && i < n; i++) if (got[i] != exp[i]) same = 0;
    if (!same) {
        tl_fail++;
        printf("   [ECHEC] %s\n           attendu : ", desc); tl_print_tab(exp, n);
        printf("\n           obtenu  : ");
        if (got) tl_print_tab(got, n); else printf("NULL");
        printf("\n");
    } else tl_ok(desc);
}
#define CHECK_TAB(got, n, desc, ...) do { int _exp[] = __VA_ARGS__; check_tab((got), _exp, (n), (desc)); } while (0)

static int finish(void) {
    printf("RESULTAT %d/%d\n", tl_total - tl_fail, tl_total);
    return tl_fail ? 1 : 0;
}
"""


def run(argv, cwd=None, stdin_data=None, timeout=10, env=None):
    """Lance une commande, renvoie (rc, stdout, stderr). rc = 'timeout' si trop long."""
    try:
        p = subprocess.run(argv, cwd=cwd, input=stdin_data, capture_output=True, timeout=timeout,
                           env=env)
        return p.returncode, p.stdout.decode(errors="replace"), p.stderr.decode(errors="replace")
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or b"").decode(errors="replace")
        return "timeout", out, ""


def normaliser(txt):
    lignes = [l.rstrip() for l in txt.replace("\r", "").split("\n")]
    while lignes and not lignes[-1]:
        lignes.pop()
    return "\n".join(lignes)


def explique_rc(rc):
    if rc == "timeout":
        return "ton programme ne s'arrête pas (boucle infinie ? scanf qui attend ?)"
    if rc in (-11, 139):
        return "Segmentation fault : accès mémoire invalide (pointeur NULL, dépassement de tableau, argv[x] inexistant...)"
    if rc in (-6, 134):
        return "programme interrompu (abort) : souvent un free() en double ou une corruption mémoire"
    if rc in (-8, 136):
        return "erreur arithmétique (division par zéro ?)"
    return None


def nom_bin(m):
    return os.path.splitext(m["fichier"])[0]


def interdits(m, src):
    for h in m.get("forbid", []):
        if re.search(r"^\s*#\s*include\s*<%s>" % re.escape(h), src, re.M):
            return "Dans cette mission, #include <%s> est interdit : écris tout toi-même !" % h
    return None


def harness_source(m):
    inc = "".join('#include "%s"\n' % h for h in m.get("headers", {}))
    return ('#include "testlib.h"\n' + inc + m.get("protos", "") + "\n"
            "int main(void) {\n    tl_init();\n" + textwrap.indent(m["tests"], "    ") +
            "\n    return finish();\n}\n")


def preparer_build(m, dossier):
    os.makedirs(BUILD, exist_ok=True)
    for f in os.listdir(BUILD):
        p = os.path.join(BUILD, f)
        if os.path.isfile(p):
            os.remove(p)
    with open(os.path.join(BUILD, "testlib.h"), "w") as f:
        f.write(TESTLIB)


def compiler_utilisateur(m, dossier, afficher=True):
    """Compile le fichier du joueur. Renvoie True/False."""
    src = os.path.join(dossier, m["fichier"])
    if not os.path.exists(src):
        if afficher:
            ko("Fichier %s introuvable (:reset pour le recréer)." % m["fichier"])
        return False
    with open(src, errors="replace") as f:
        texte = f.read()
    msg = interdits(m, texte)
    if msg:
        if afficher:
            ko(msg)
        return False
    if m["kind"] == "prog":
        argv = [GCC] + CFLAGS + [m["fichier"], "-o", os.path.join(BUILD, "prog")]
        aff = "gcc %s %s -o %s" % (" ".join(CFLAGS), m["fichier"], nom_bin(m))
    else:
        argv = [GCC] + CFLAGS + ["-c", m["fichier"], "-o", os.path.join(BUILD, "user.o")]
        aff = "gcc %s -c %s" % (" ".join(CFLAGS), m["fichier"])
    if afficher:
        info("  $ " + aff)
    rc, out, err = run(argv, cwd=dossier, timeout=30)
    if rc != 0:
        if afficher:
            print(err.rstrip())
            ko("✘ La compilation échoue. Lis le PREMIER message (fichier:ligne:colonne: error: ...).")
        return False
    if m["kind"] == "fonc":
        h = os.path.join(BUILD, "test_main.c")
        with open(h, "w") as f:
            f.write(harness_source(m))
        argv = [GCC, "-std=gnu99", "-w", "-g", "-I", BUILD, "-I", dossier, h,
                os.path.join(BUILD, "user.o"), "-o", os.path.join(BUILD, "run")]
        rc, out, err = run(argv, cwd=dossier, timeout=30)
        if rc != 0:
            if afficher:
                if "multiple definition of `main'" in err or "multiple definition of 'main'" in err:
                    ko("✘ Ton fichier contient un main : enlève-le (le jeu fournit son propre main de test).")
                else:
                    manque = sorted(set(re.findall(r"undefined reference to [`'](\w+)'", err)))
                    if manque:
                        ko("✘ Fonction(s) introuvable(s) : %s. Vérifie le nom exact et les paramètres."
                           % ", ".join(manque))
                    else:
                        print(err.rstrip())
                        ko("✘ L'édition de liens échoue.")
        return rc == 0
    return True


def tester_prog(m, dossier, detail=True):
    """Lance le programme du joueur sur chaque test. Renvoie (réussis, total)."""
    binaire = os.path.join(BUILD, "prog")
    bons = 0
    for t in m["tests"]:
        args = t.get("args", "")
        entree = t.get("stdin")
        affiche = ("printf %r | " % entree if entree is not None else "") + "./%s %s" % (nom_bin(m), args)
        rc, out, _ = run([binaire] + shlex.split(args), cwd=dossier,
                         stdin_data=(entree or "").encode(), timeout=3)
        attendu = normaliser(t["attendu"])
        obtenu = normaliser(out)
        pb = explique_rc(rc)
        if pb is None and obtenu == attendu:
            bons += 1
            if detail:
                print(C.VERT + "   [ok] " + C.R + affiche)
            continue
        if detail:
            print(C.ROUGE + "   [ECHEC] " + C.R + affiche)
            if pb:
                print("           " + pb)
            else:
                print("           attendu :")
                bloc(textwrap.indent(attendu or "(rien)", "        "), C.VERT)
                print("           obtenu  :")
                bloc(textwrap.indent(obtenu or "(rien)", "        "), C.ROUGE)
    return bons, len(m["tests"])


def tester_fonc(m, dossier, detail=True):
    """Lance le main de test. Renvoie (réussis, total) ; total = 0 si plantage avant la fin."""
    binaire = os.path.join(BUILD, "run")
    if m.get("valgrind") and VALGRIND:
        if detail:
            info("  Vérification mémoire (valgrind)...")
        env = dict(os.environ, CQ_QUIET="1")
        rc, out, err = run([VALGRIND, "-q", "--error-exitcode=42", "--leak-check=full",
                            "--errors-for-leak-kinds=definite", binaire], cwd=dossier,
                           timeout=60, env=env)
        if rc == 42:
            if detail:
                lignes = [l for l in err.split("\n") if l.strip()]
                print("\n".join(lignes[:25]))
                ko("✘ valgrind a trouvé des erreurs mémoire : fuite (malloc sans free), lecture/écriture "
                   "hors de la zone allouée, '\\0' oublié...")
                info("  Repère « Invalid read/write » ou « definitely lost » et la ligne de TON fichier "
                     "indiquée juste en dessous (at ...  %s:ligne)." % m["fichier"])
            return 0, 1
    rc, out, err = run([binaire], cwd=dossier, timeout=10)
    res = re.search(r"RESULTAT (\d+)/(\d+)", out)
    if detail:
        corps = re.sub(r"RESULTAT \d+/\d+\n?", "", out).rstrip()
        for l in corps.split("\n"):
            if "[ECHEC]" in l:
                print(l.replace("[ECHEC]", C.ROUGE + "[ECHEC]" + C.R))
            elif "[ok]" in l:
                print(l.replace("[ok]", C.VERT + "[ok]" + C.R))
            elif l:
                print(l)
        pb = explique_rc(rc)
        if pb:
            ko("✘ " + pb + " (pendant le dernier test affiché)")
    if not res:
        return 0, 1
    return int(res.group(1)), int(res.group(2))


def verifier_code(m, dossier, mode="niveau"):
    """Compile + teste. Renvoie True si tout passe."""
    if not GCC:
        ko("gcc introuvable : sudo apt install -y build-essential gdb valgrind")
        return False
    detail = mode != "examen"
    preparer_build(m, dossier)
    print()
    if not compiler_utilisateur(m, dossier, afficher=True):
        return False
    info("  Tests...")
    if m["kind"] == "prog":
        bons, total = tester_prog(m, dossier, detail)
    else:
        bons, total = tester_fonc(m, dossier, detail)
    if bons == total:
        return True
    print()
    warn("  %d/%d tests passent." % (bons, total))
    return False


# --------------------------------------------------------------------------
# Sauvegarde, score
# --------------------------------------------------------------------------
def charger():
    try:
        with open(SAVE_FILE) as f:
            s = json.load(f)
    except (OSError, ValueError):
        s = {}
    for k, v in (("missions", {}), ("erreurs", {}), ("examens", []), ("lecons", {})):
        s.setdefault(k, v)
    return s


def sauver(s):
    os.makedirs(DATA, exist_ok=True)
    tmp = SAVE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f, indent=1, ensure_ascii=False)
    os.replace(tmp, SAVE_FILE)


SAVE = None


def score_total():
    return sum(r.get("points", 0) for r in SAVE["missions"].values())


def ajouter_erreur(mid, raison):
    e = SAVE["erreurs"].setdefault(mid, {"nb": 0})
    e["nb"] += 1
    e["raison"] = raison
    e["date"] = time.strftime("%Y-%m-%d %H:%M")


def enregistrer(m, res, mode):
    mid = m["id"]
    if res.get("abandon"):
        return
    reussi = res["ok"] and not res["solution"]
    ind = min(res["indices"], 2)
    rec = SAVE["missions"].setdefault(mid, {"points": 0, "etoiles": 0, "reussie": False, "essais": 0})
    if mode == "apprentissage":
        rec["essais"] += 1
        pts = int(round(BASE_POINTS[m["diff"]] * FACTEUR_INDICE[2])) if reussi else 0
        rec["points"] = max(rec["points"], pts)
        rec["etoiles"] = max(rec["etoiles"], 1 if reussi else 0)
        rec["reussie"] = rec["reussie"] or res["ok"]
        res["points"], res["etoiles"] = pts, (1 if reussi else 0)
        if not res["ok"] or res["solution"] or res["passe"]:
            ajouter_erreur(mid, "solution vue" if res["solution"] else ("passée" if res["passe"] else "ratée"))
        sauver(SAVE)
        return
    if mode != "examen":
        pts = int(round(BASE_POINTS[m["diff"]] * FACTEUR_INDICE[ind])) if reussi else 0
        etoiles = (3 - ind) if reussi else 0
        rec["essais"] += 1
        rec["points"] = max(rec["points"], pts)
        rec["etoiles"] = max(rec["etoiles"], etoiles)
        rec["reussie"] = rec["reussie"] or res["ok"]
        res["points"], res["etoiles"] = pts, etoiles
    if not res["ok"] or res["solution"] or res["passe"]:
        raison = "solution vue" if res["solution"] else ("passée" if res["passe"] else "ratée")
        if res.get("timeout"):
            raison = "temps écoulé"
        ajouter_erreur(mid, raison + (" (examen)" if mode == "examen" else ""))
    elif ind >= 2:
        ajouter_erreur(mid, "2 indices utilisés")
    elif ind == 0 and mid in SAVE["erreurs"]:
        del SAVE["erreurs"][mid]
        res["corrigee"] = True
    sauver(SAVE)


# --------------------------------------------------------------------------
# Une mission
# --------------------------------------------------------------------------
PAR_ID = {m["id"]: m for m in MISSIONS}
ETOILES = lambda n: C.JAUNE + "★" * n + C.DIM + "☆" * (3 - n) + C.R  # noqa: E731
TYPE_LIB = {"prog": "programme", "fonc": "fonctions", "qcm": "QCM", "reponse": "question"}
CODE = ("prog", "fonc")


def entete(m, mode, rang=None):
    niv = NIVEAUX[m["niveau"] - 1][1]
    titre("%s  ·  %s" % (m["titre"], THEMES[m["theme"]]))
    sous = "Niveau %d (%s) · difficulté %s · %d pts" % (
        m["niveau"], niv, "●" * m["diff"] + "○" * (4 - m["diff"]), BASE_POINTS[m["diff"]])
    if m.get("bug"):
        sous += " · chasse aux bugs"
    if rang:
        sous = rang + " · " + sous
    info("  " + sous)
    print()
    bloc(m["enonce"])
    print()
    if m.get("code"):
        code_bloc(m["code"])
        print()


AIDE_CODE = """Commandes du jeu (toujours précédées de « : ») :
  :verifier   compile ton fichier (gcc -Wall -Werror -std=c99) et lance les tests
  :editer     ouvre ton fichier dans l'éditeur ($EDITOR, sinon nano)
  :voir       affiche ton fichier avec les numéros de ligne
  :essai      (missions « fonctions ») crée essai.c avec un main pour tester toi-même
  :indice     un indice (coûte des points : 3★ → 2★ → 1★)
  :solution   affiche la solution (0 point, la mission va dans « mes erreurs »)
  :enonce     réaffiche l'énoncé      :reset   remet le fichier de départ (ton code est perdu)
  :fiche      fiche du thème          :methode méthode pour ce type d'exo
  :passer     passe la mission        :menu    retour au menu
Tout le reste est une commande bash lancée dans le dossier de la mission :
  nano somme.c · code somme.c · gcc -Wall -std=c99 somme.c -o somme · ./somme 3 4 · ls"""


def aide_commandes(m, mode):
    if m["kind"] == "qcm":
        if mode == "examen":
            info("  Réponds par la ou les lettres (ex. b, ou ac). :passer pour sauter.")
        else:
            info("  Réponds par la ou les lettres (ex. b, ou ac).  :indice  :fiche  :passer  :menu")
        return
    if m["kind"] == "reponse":
        if mode == "examen":
            info("  Tape ta réponse. :passer pour sauter.")
        else:
            info("  Tape ta réponse.  :indice  :solution  :fiche  :passer  :menu")
            info("  Pas sûr ? :essayer ouvre le code dans l'éditeur pour le compiler et le lancer (la mission "
                 "ne rapportera plus qu'1★).")
        return
    if mode == "examen":
        info("  :verifier  :editer  :voir  :enonce  :reset  :passer  :menu   (+ commandes bash)")
    else:
        info("  :verifier  :editer  :voir  :indice  :solution  :fiche  :passer  :menu  (:aide)")
        info("  Les autres lignes sont des commandes bash (nano, code, gcc, ./prog...).")


def methode_affichee(m):
    if m.get("bug"):
        return "Lis le code, lance :verifier pour voir les tests qui échouent, puis corrige."
    return None


class Partie:
    """Une mission en cours."""

    def __init__(self, m, mode, deadline=None, rang=None):
        self.m = m
        self.mode = mode
        self.deadline = deadline
        self.rang = rang
        self.res = {"id": m["id"], "ok": False, "indices": 0, "solution": False,
                    "passe": False, "abandon": False, "timeout": False}

    # -- dossier de travail ---------------------------------------------
    @property
    def dossier(self):
        if self.mode == "examen":
            return os.path.join(EXAMEN_DIR, self.m["id"])
        return os.path.join(ATELIER, self.m["id"])

    def installer(self, force=False):
        m, d = self.m, self.dossier
        os.makedirs(d, exist_ok=True)
        cible = os.path.join(d, m["fichier"])
        if force or not os.path.exists(cible):
            with open(cible, "w") as f:
                f.write(m["starter"])
        for nom, contenu in m.get("headers", {}).items():
            with open(os.path.join(d, nom), "w") as f:
                f.write(contenu)

    def restant(self):
        if not self.deadline:
            return ""
        r = max(0, int(self.deadline - time.time()))
        return rl(C.JAUNE) + "[%d:%02d] " % (r // 60, r % 60) + rl(C.R)

    def temps_ecoule(self):
        return self.deadline is not None and time.time() > self.deadline

    # -- commandes communes -------------------------------------------------
    def commande_commune(self, cmd):
        """Gère :indice, :solution, :fiche, :methode. Renvoie True si traitée."""
        m, examen = self.m, self.mode == "examen"
        indices = m.get("indices", [])
        if cmd in ("indice", "i"):
            if examen:
                warn("Pas d'indice pendant l'examen.")
            elif self.res["indices"] < len(indices):
                self.res["indices"] += 1
                n = self.res["indices"]
                warn("Indice %d/%d : " % (n, len(indices)) + indices[n - 1])
                if n >= 2 and self.mode != "apprentissage":
                    info("(la mission ne rapportera plus qu'1★ ; :solution pour la réponse)")
            else:
                warn("Plus d'indice. :solution pour voir la réponse.")
            return True
        if cmd in ("solution", "sol"):
            if examen:
                warn("Pas de solution pendant l'examen (:passer pour sauter).")
            else:
                self.res["solution"] = True
                self.montrer_solution()
                if m["kind"] in CODE:
                    info("Recopie-la (ou adapte ton code) puis :verifier pour la valider "
                         "(0 point, la mission ira dans « mes erreurs »).")
            return True
        if cmd == "fiche":
            if examen:
                warn("Pas de fiche pendant l'examen.")
            else:
                afficher_fiche(m["theme"])
            return True
        if cmd in ("methode", "méthode", "m"):
            if examen:
                warn("Pas de méthode pendant l'examen.")
            else:
                afficher_methode(m["theme"])
            return True
        return False

    def montrer_solution(self):
        m = self.m
        print(C.MAG + "Solution :" + C.R)
        if m["kind"] in CODE:
            code_bloc(m["solution"], C.MAG)
        elif m["kind"] == "qcm":
            bloc("Bonne(s) réponse(s) : " + ", ".join(sorted(m["bonnes"])), C.MAG)
        else:
            bloc(m["solution"], C.MAG)
        if m.get("explication"):
            bloc(m["explication"], C.DIM)

    # -- boucle principale -------------------------------------------------
    def jouer(self):
        if self.m["kind"] == "qcm":
            return self.jouer_qcm()
        if self.m["kind"] == "reponse":
            return self.jouer_reponse()
        return self.jouer_code()

    def guide(self):
        if self.mode == "apprentissage":
            annonce_guide(self.m)
            self.res["indices"] = min(1, len(self.m.get("indices", [])))

    def jouer_code(self):
        m = self.m
        self.installer(force=(self.mode == "examen"))
        entete(m, self.mode, self.rang)
        chemin = os.path.join(self.dossier, m["fichier"])
        print(C.B + "  Ton fichier : " + C.R + chemin.replace(os.path.expanduser("~"), "~"))
        for h in m.get("headers", {}):
            info("  (fourni : %s, à ne pas modifier)" % h)
        aide_commandes(m, self.mode)
        self.guide()
        examen = self.mode == "examen"
        while True:
            if self.temps_ecoule():
                warn("\n⏱  Temps écoulé !")
                self.res["timeout"] = True
                break
            try:
                prompt = self.restant() + rl(C.CYAN + C.B) + m["fichier"] + rl(C.R) + "> "
                ligne = input(prompt)
            except EOFError:
                print()
                ligne = ":menu"
            except KeyboardInterrupt:
                print()
                continue
            s = ligne.strip()
            if not s:
                continue
            if s in ("exit", "quit", "logout"):
                s = ":menu"
            if s.startswith(":"):
                cmd = s[1:].split()[0].lower() if len(s) > 1 else ""
                if cmd in ("aide", "help", "h", "?"):
                    print(AIDE_CODE)
                elif self.commande_commune(cmd):
                    pass
                elif cmd in ("verifier", "vérifier", "v", "check"):
                    if verifier_code(m, self.dossier, self.mode):
                        self.reussite()
                        break
                elif cmd in ("editer", "éditer", "ed", "edit"):
                    subprocess.call(shlex.split(editeur()) + [m["fichier"]], cwd=self.dossier)
                    info("  (sauvegardé ? :verifier pour tester)")
                elif cmd in ("voir", "cat", "l"):
                    with open(chemin, errors="replace") as f:
                        code_bloc(f.read())
                elif cmd == "essai":
                    self.essai()
                elif cmd in ("enonce", "énoncé", "e"):
                    entete(m, self.mode, self.rang)
                elif cmd == "reset":
                    r = demander("Remettre le fichier de départ ? Ton code sera perdu. (o/N) > ")
                    if r and r.strip().lower() in ("o", "oui"):
                        self.installer(force=True)
                        ok("Fichier remis à zéro.")
                elif cmd in ("passer", "skip", "p"):
                    self.res["passe"] = True
                    if not examen:
                        self.montrer_solution()
                    break
                elif cmd in ("menu", "q", "quitter"):
                    self.res["abandon"] = True
                    if not examen:
                        info("  Ton code reste dans %s." % self.dossier.replace(os.path.expanduser("~"), "~"))
                    break
                else:
                    warn("Commande du jeu inconnue. :aide pour la liste.")
                continue
            subprocess.call(["bash", "-c", ligne], cwd=self.dossier)
        return self.res

    def essai(self):
        m = self.m
        if m["kind"] != "fonc":
            info("  Pour un programme : gcc -Wall -std=c99 %s -o %s puis ./%s ..." % (
                m["fichier"], nom_bin(m), nom_bin(m)))
            return
        p = os.path.join(self.dossier, "essai.c")
        if not os.path.exists(p):
            inc = "".join('#include "%s"\n' % h for h in m.get("headers", {}))
            with open(p, "w") as f:
                f.write("#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n" + inc +
                        "\n// prototypes des fonctions de " + m["fichier"] + "\n" +
                        m.get("protos", "") + "\n\nint main(void) {\n"
                        "    // appelle tes fonctions ici et affiche les résultats, par exemple :\n"
                        "    // printf(\"%d\\n\", ma_fonction(3, 4));\n    return 0;\n}\n")
            ok("  essai.c créé. Écris ton main dedans (nano essai.c), puis compile avec :")
        else:
            info("  essai.c existe déjà. Compile-le avec :")
        print("    gcc -Wall -std=c99 -g essai.c %s -o essai && ./essai" % m["fichier"])
        if m.get("valgrind"):
            print("    valgrind --leak-check=full ./essai")

    def reussite(self):
        self.res["ok"] = True
        print()
        if self.mode == "examen":
            ok("✔ Mission validée.")
            return
        ok("✔ Mission réussie !")
        if self.m.get("explication"):
            bloc(self.m["explication"], C.DIM)
        if self.m["kind"] in CODE and self.m.get("montrer_solution", True):
            info("  Une solution possible (compare avec la tienne) :")
            code_bloc(self.m["solution"], C.DIM)

    # -- QCM --------------------------------------------------------------
    def jouer_qcm(self):
        m = self.m
        examen = self.mode == "examen"
        entete(m, self.mode, self.rang)
        lettres = "abcdefgh"[:len(m["choix"])]
        for l, c in zip(lettres, m["choix"]):
            print("  %s%s)%s %s" % (C.B, l, C.R, c.replace("\n", "\n     ")))
        print()
        bonnes = set(m["bonnes"])
        if len(bonnes) > 1:
            info("  (plusieurs bonnes réponses : tape toutes les lettres, ex. ac)")
        aide_commandes(m, self.mode)
        self.guide()
        while True:
            if self.temps_ecoule():
                warn("⏱  Temps écoulé !")
                self.res["timeout"] = True
                return self.res
            r = demander(self.restant() + "réponse> ")
            if r is None:
                r = ":menu"
            r = r.strip().lower()
            if not r:
                continue
            if r.startswith(":"):
                c = r[1:]
                if c in ("indice", "i", "fiche", "methode", "méthode", "m"):
                    self.commande_commune(c)
                elif c in ("passer", "p"):
                    self.res["passe"] = True
                    break
                elif c in ("menu", "q"):
                    self.res["abandon"] = True
                    return self.res
                elif c in ("enonce", "e"):
                    return self.jouer_qcm()
                else:
                    warn("Réponds par une lettre, ou :indice / :passer / :menu.")
                continue
            choix = set(x for x in r if x.isalpha())
            if not choix or not choix <= set(lettres):
                warn("Réponds avec les lettres %s." % ", ".join(lettres))
                continue
            self.res["ok"] = choix == bonnes
            break
        print()
        if examen:
            info("Réponse enregistrée.")
            return self.res
        if self.res["ok"]:
            ok("✔ Bonne réponse !")
        else:
            ko("✘ Raté. Bonne réponse : " + ", ".join(sorted(bonnes)))
        if m.get("explication"):
            bloc(m["explication"], C.DIM)
        return self.res

    # -- réponse libre ------------------------------------------------------
    def jouer_reponse(self):
        m = self.m
        examen = self.mode == "examen"
        entete(m, self.mode, self.rang)
        aide_commandes(m, self.mode)
        self.guide()
        essais = 0
        while True:
            if self.temps_ecoule():
                warn("⏱  Temps écoulé !")
                self.res["timeout"] = True
                return self.res
            r = demander(self.restant() + "réponse> ")
            if r is None:
                r = ":menu"
            s = r.strip()
            if not s:
                continue
            if s.startswith(":"):
                c = s[1:].lower()
                if self.commande_commune(c):
                    if c in ("solution", "sol") and not examen:
                        break
                elif c in ("essayer", "essai"):
                    if examen:
                        warn("Pas d'essai pendant l'examen.")
                    else:
                        self.res["indices"] = max(self.res["indices"], 2)
                        essayer_code(m.get("verif") or m.get("code", ""), editer=True)
                elif c in ("passer", "p"):
                    self.res["passe"] = True
                    break
                elif c in ("menu", "q"):
                    self.res["abandon"] = True
                    return self.res
                elif c in ("enonce", "e"):
                    entete(m, self.mode, self.rang)
                else:
                    warn("Tape ta réponse, ou :indice / :solution / :passer / :menu.")
                continue
            essais += 1
            if reponse_ok(m, s):
                self.res["ok"] = True
                break
            if examen:
                break
            if essais >= 2:
                ko("✘ Toujours pas.")
                self.res["ok"] = False
                break
            warn("Non. Encore un essai (ou :indice).")
        print()
        if examen:
            info("Réponse enregistrée.")
            return self.res
        if self.res["ok"]:
            ok("✔ Bonne réponse !")
        elif not self.res["solution"]:
            ko("✘ La réponse était : " + m["solution"])
        if m.get("explication") and not self.res["solution"]:
            bloc(m["explication"], C.DIM)
        return self.res


def norm_rep(s):
    return re.sub(r"\s+", "", s.strip().lower().strip('"').strip("'"))


def reponse_ok(m, s):
    return norm_rep(s) in [norm_rep(x) for x in m["reponses"]]


# --------------------------------------------------------------------------
# Exemples de code (cours, :essayer)
# --------------------------------------------------------------------------
def code_complet(code):
    if re.search(r"\bmain\s*\(", code):
        return code
    corps = textwrap.indent(code.strip("\n"), "    ")
    return ("#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n\n"
            "int main(void) {\n" + corps + "\n    return 0;\n}\n")


def essayer_code(code, args="", stdin=None, editer=False, afficher_code=False):
    """Écrit le code dans ~/.cquest/cours/exemple.c, le compile (-Wall) et le lance."""
    os.makedirs(COURS_DIR, exist_ok=True)
    src = os.path.join(COURS_DIR, "exemple.c")
    with open(src, "w") as f:
        f.write(code_complet(code))
    if editer:
        info("  Le code est dans %s : modifie-le si tu veux, sauvegarde et quitte l'éditeur."
             % src.replace(os.path.expanduser("~"), "~"))
        subprocess.call(shlex.split(editeur()) + [src])
    if afficher_code:
        with open(src) as f:
            code_bloc(f.read())
    rc, out, err = run([GCC, "-Wall", "-std=c99", "-g", "exemple.c", "-o", "exemple"], cwd=COURS_DIR,
                       timeout=30)
    if err.strip():
        print(C.JAUNE + err.rstrip() + C.R)
    if rc != 0:
        ko("  (ne compile pas)")
        return
    info("  $ ./exemple " + args)
    if stdin is None:
        subprocess.call(["./exemple"] + shlex.split(args), cwd=COURS_DIR)
    else:
        rc, out, err = run(["./exemple"] + shlex.split(args), cwd=COURS_DIR, stdin_data=stdin.encode(),
                           timeout=5)
        print(out.rstrip())
        p = explique_rc(rc)
        if p:
            warn("  " + p)


# --------------------------------------------------------------------------
# Fiches, méthode, apprentissage
# --------------------------------------------------------------------------
def afficher_fiche(theme):
    txt = FICHES.get(theme)
    titre("Fiche : " + THEMES.get(theme, theme))
    if not txt:
        info("  (pas de fiche pour ce thème)")
        return
    bloc(txt)
    print()


def afficher_methode(theme):
    L = LECONS.get(theme)
    if not L:
        return
    print()
    print(C.JAUNE + C.B + "  Méthode : " + THEMES[theme] + C.R)
    bloc(L["methode"], C.JAUNE)
    print()


def annonce_guide(m):
    print()
    info("  Exercice guidé : indices gratuits (:indice), :methode, :fiche, :solution si tu bloques.")
    ind = m.get("indices", [])
    if ind:
        print(C.JAUNE + "  💡 Piste : " + ind[0] + C.R)
    print()


def missions_niveau(n):
    return [m for m in MISSIONS if m["niveau"] == n]


def progression_niveau(n):
    ms = missions_niveau(n)
    faits = sum(1 for m in ms if SAVE["missions"].get(m["id"], {}).get("reussie"))
    et = sum(SAVE["missions"].get(m["id"], {}).get("etoiles", 0) for m in ms)
    return faits, len(ms), et


def debloque(n):
    if n == 1 or os.environ.get("CQUEST_TOUT"):
        return True
    f, t, _ = progression_niveau(n - 1)
    return t == 0 or f / t >= SEUIL_DEBLOCAGE


def bilan_mission(m, res):
    if res.get("abandon"):
        return
    if res["ok"] and not res["solution"]:
        print("  %s  +%d pts   (score total : %d)" % (ETOILES(res.get("etoiles", 0)),
                                                   res.get("points", 0), score_total()))
        if res.get("corrigee"):
            ok("  Erreur corrigée : la mission sort de « mes erreurs ».")
    elif res["ok"]:
        info("  Validée avec la solution : 0 point. Elle est dans « mes erreurs ».")
    else:
        info("  0 point. La mission est ajoutée à « mes erreurs ».")


def theme_exos(theme):
    ms = [m for m in MISSIONS if m["theme"] == theme]
    f = sum(1 for m in ms if SAVE["missions"].get(m["id"], {}).get("reussie"))
    return f, len(ms)


def cours_fini(theme):
    return SAVE["lecons"].get(theme, {}).get("fini", False)


def theme_fini(theme):
    f, t = theme_exos(theme)
    return cours_fini(theme) and t and f / t >= SEUIL_DEBLOCAGE


def prochaine_etape():
    for _, _, themes, _ in PROGRAMME:
        for t in themes:
            if not cours_fini(t):
                return ("cours", t)
            if not theme_fini(t):
                return ("exos", t)
    return ("examen", None)


def libelle_etape(e):
    k, t = e
    if k == "cours":
        return "cours « %s »" % THEMES[t]
    if k == "exos":
        return "exos guidés « %s »" % THEMES[t]
    return "examen blanc + mes erreurs"


def lancer_etape(e):
    k, t = e
    if k == "cours":
        if jouer_lecon(t):
            r = demander("Enchaîner sur les exercices guidés de ce thème ? (O/n) > ")
            if r is not None and r.strip().lower() not in ("n", "non"):
                exos_guides(t)
    elif k == "exos":
        exos_guides(t)
    else:
        menu_examen()


def ex_norm(ex):
    """Un exemple : str (code) | (code, note) | dict(code, note, args, stdin)."""
    if isinstance(ex, str):
        return {"code": ex}
    if isinstance(ex, tuple):
        return {"code": ex[0], "note": ex[1] if len(ex) > 1 else None}
    return ex


def montrer_exemple(ex):
    ex = ex_norm(ex)
    print()
    print("  " + C.CYAN + "Exemple :" + C.R)
    code_bloc(ex["code"])
    while True:
        r = demander(C.DIM + "  Entrée = compiler et lancer · e = le modifier puis lancer · "
                     "s = passer · m = quitter le cours" + C.R + " ")
        if r is None or r.strip().lower() == "m":
            return "menu"
        r = r.strip().lower()
        if r == "s":
            return "ok"
        if r in ("", "e"):
            print()
            essayer_code(ex["code"], ex.get("args", ""), ex.get("stdin"), editer=(r == "e"),
                         afficher_code=(r == "e"))
            if ex.get("note"):
                print("  " + C.JAUNE + "→ " + ex["note"] + C.R)
            r2 = demander(C.DIM + "  Entrée = suite · e = le modifier et relancer" + C.R + " ")
            if r2 is None:
                return "menu"
            if r2.strip().lower() == "e":
                essayer_code(open(os.path.join(COURS_DIR, "exemple.c")).read(), ex.get("args", ""),
                             ex.get("stdin"), editer=True, afficher_code=True)
            return "ok"


def jouer_lecon(theme):
    L = LECONS[theme]
    cartes = L["cartes"]
    rec = SAVE["lecons"].setdefault(theme, {"vu": 0, "fini": False})
    titre("Cours : " + THEMES[theme] + "  (%d cartes)" % len(cartes))
    info("  Chaque carte explique une notion avec des exemples de code. Pour chaque exemple :\n"
         "  Entrée le compile et le lance, e l'ouvre dans l'éditeur pour que tu le modifies\n"
         "  (c'est en cassant et en modifiant qu'on comprend).")
    i = 0
    if 0 < rec["vu"] < len(cartes) and not rec["fini"]:
        r = demander("Reprendre à la carte %d ? (O/n) > " % (rec["vu"] + 1))
        if r is not None and r.strip().lower() not in ("n", "non"):
            i = rec["vu"]
    while i < len(cartes):
        c = cartes[i]
        titre("%s · carte %d/%d · %s" % (THEMES[theme], i + 1, len(cartes), c["titre"]))
        bloc(c["texte"])
        quitter = False
        for ex in c.get("exemples", []):
            if montrer_exemple(ex) == "menu":
                quitter = True
                break
        if quitter:
            sauver(SAVE)
            return False
        if c.get("astuce"):
            print()
            print(C.JAUNE + textwrap.fill("💡 " + c["astuce"], 76, initial_indent="  ",
                                          subsequent_indent="     ") + C.R)
        print()
        r = demander(C.DIM + "Entrée : carte suivante · p : précédente · m : menu" + C.R + " ")
        if r is None or r.strip().lower() == "m":
            sauver(SAVE)
            return False
        if r.strip().lower() == "p":
            i = max(0, i - 1)
            continue
        i += 1
        rec["vu"] = max(rec["vu"], i)
        sauver(SAVE)
    rec["fini"] = True
    sauver(SAVE)
    titre("Méthode pour les exercices : " + THEMES[theme])
    bloc(L["methode"], C.JAUNE)
    print()
    ok("  Cours terminé !")
    return True


def serie(liste, mode, nom):
    """Joue une liste de missions à la suite (rapide, thème, erreurs, guidé)."""
    bilan = []
    for i, m in enumerate(liste, 1):
        res = Partie(m, mode, rang="%s %d/%d" % (nom, i, len(liste))).jouer()
        enregistrer(m, res, mode)
        if res.get("abandon"):
            break
        bilan.append((m, res))
        bilan_mission(m, res)
        if i < len(liste):
            r = demander(C.DIM + "Entrée : suivante · m : arrêter" + C.R + " ")
            if r is None or r.strip().lower() in ("m", "q", "r"):
                break
    if bilan:
        reussies = sum(1 for _, r in bilan if r["ok"] and not r["solution"])
        titre("Bilan : %d/%d réussies" % (reussies, len(bilan)))
        for m, r in bilan:
            s = (C.VERT + "✔" if r["ok"] and not r["solution"] else C.ROUGE + "✘") + C.R
            print("  %s %s" % (s, m["titre"]))
        pause()


def exos_guides(theme):
    ms = sorted([m for m in MISSIONS if m["theme"] == theme], key=lambda m: (m["diff"], MISSIONS.index(m)))
    a_faire = [m for m in ms if not SAVE["missions"].get(m["id"], {}).get("reussie")]
    liste = a_faire or ms
    afficher_methode(theme)
    info("  %d exercice(s) guidé(s), du plus facile au plus dur. Réussis en guidé = 1★ ;"
         " rejoue-les en campagne pour 3★." % len(liste))
    serie(liste, "apprentissage", "Exercice guidé")


def menu_programme():
    while True:
        titre("Programme conseillé")
        info("  Pour chaque thème : le cours, puis les exos guidés (60 % réussis = thème validé).")
        print()
        for etape, duree, themes, extra in PROGRAMME:
            print("  " + C.B + "%-22s" % etape + C.R + C.DIM + duree + C.R)
            for t in themes:
                f, n = theme_exos(t)
                marque = C.VERT + "✔" if theme_fini(t) else (C.JAUNE + "…" if cours_fini(t) or f else C.DIM + "·")
                cours = "cours ✔" if cours_fini(t) else "cours à lire"
                print("     %s%s %-40s %s · exos %d/%d" % (marque, C.R, THEMES[t], cours, f, n))
            if extra:
                print("     " + C.DIM + "→ " + extra + C.R)
        print()
        e = prochaine_etape()
        r = demander("Entrée = lancer la prochaine étape (%s) · r = retour > " % libelle_etape(e))
        if r is None or r.strip().lower() in ("r", "q"):
            return
        if not r.strip():
            lancer_etape(e)


def menu_apprentissage():
    tl = list(THEMES.keys())
    while True:
        titre("Apprentissage : cours, exemples, méthode, exos guidés")
        for i, t in enumerate(tl, 1):
            f, n = theme_exos(t)
            rec = SAVE["lecons"].get(t, {})
            nb = len(LECONS[t]["cartes"])
            cours = C.VERT + "cours ✔" + C.R if rec.get("fini") else (
                "cours %d/%d" % (rec.get("vu", 0), nb) if rec.get("vu") else C.DIM + "cours · %d cartes" % nb + C.R)
            print("  %2d. %-40s %s   exos %d/%d" % (i, THEMES[t], cours, f, n))
        print()
        print("   p. Programme conseillé")
        print()
        e = prochaine_etape()
        info("  numéro = cours puis exos guidés · e3 = exos guidés du thème 3 · m3 = méthode du thème 3")
        r = demander("Entrée = prochaine étape (%s) · r = retour > " % libelle_etape(e))
        if r is None or r.strip().lower() in ("r", "q"):
            return
        r = r.strip().lower()
        if not r:
            lancer_etape(e)
        elif r == "p":
            menu_programme()
        elif r.isdigit() and 1 <= int(r) <= len(tl):
            lancer_etape(("cours", tl[int(r) - 1]))
        elif r[:1] in ("e", "m") and r[1:].strip().isdigit() and 1 <= int(r[1:]) <= len(tl):
            t = tl[int(r[1:]) - 1]
            if r[0] == "e":
                exos_guides(t)
            else:
                afficher_methode(t)
                pause()


# --------------------------------------------------------------------------
# Campagne, rapide, thème, erreurs
# --------------------------------------------------------------------------
def menu_campagne():
    while True:
        titre("Campagne : niveaux")
        for n, nom, _ in NIVEAUX:
            f, t, et = progression_niveau(n)
            if debloque(n):
                barre = C.VERT + "█" * f + C.DIM + "░" * (t - f) + C.R
                print("  %2d. %-34s %s %2d/%-2d  %s★" % (n, nom, barre, f, t, et))
            else:
                print(C.DIM + "  %2d. %-34s 🔒 (finis %d%% du niveau %d)" % (
                    n, nom, int(SEUIL_DEBLOCAGE * 100), n - 1) + C.R)
        print()
        info("  Score total : %d pts" % score_total())
        r = demander("niveau (numéro, Entrée = premier niveau pas fini, r = retour) > ")
        if r is None or r.strip().lower() in ("r", "q"):
            return
        r = r.strip()
        if not r:
            cible = next((n for n, _, _ in NIVEAUX if debloque(n)
                          and progression_niveau(n)[0] < progression_niveau(n)[1]), None)
            if cible is None:
                ok("Tout est fini, bravo !")
                continue
        elif r.isdigit() and 1 <= int(r) <= len(NIVEAUX):
            cible = int(r)
        else:
            continue
        if not debloque(cible):
            warn("Niveau verrouillé. (Le mode « par thème » permet de tout jouer.)")
            continue
        menu_niveau(cible)


def menu_niveau(n):
    while True:
        ms = missions_niveau(n)
        titre("Niveau %d : %s" % (n, NIVEAUX[n - 1][1]))
        for i, m in enumerate(ms, 1):
            rec = SAVE["missions"].get(m["id"], {})
            marque = ETOILES(rec.get("etoiles", 0)) if rec.get("reussie") else C.DIM + "···" + C.R
            print("  %2d. %s  %-46s %s" % (i, marque, m["titre"], C.DIM + TYPE_LIB[m["kind"]] + C.R))
        print()
        r = demander("mission (numéro, Entrée = suivante pas faite, r = retour) > ")
        if r is None or r.strip().lower() in ("r", "q"):
            return
        r = r.strip()
        if r.isdigit() and 1 <= int(r) <= len(ms):
            idx = int(r) - 1
        elif not r:
            idx = next((i for i, m in enumerate(ms)
                        if not SAVE["missions"].get(m["id"], {}).get("reussie")), None)
            if idx is None:
                ok("Niveau terminé ! Tu peux rejouer une mission pour gagner des étoiles.")
                continue
        else:
            continue
        while idx is not None and idx < len(ms):
            m = ms[idx]
            res = Partie(m, "niveau", rang="Mission %d/%d" % (idx + 1, len(ms))).jouer()
            enregistrer(m, res, "niveau")
            if res.get("abandon"):
                break
            bilan_mission(m, res)
            r = demander(C.DIM + "Entrée : mission suivante · m : menu du niveau" + C.R + " ")
            if r is None or r.strip().lower() in ("m", "r", "q"):
                break
            idx += 1
        nouveau = n + 1
        if nouveau <= len(NIVEAUX) and debloque(nouveau) and not SAVE.get("annonce_%d" % nouveau):
            SAVE["annonce_%d" % nouveau] = True
            sauver(SAVE)
            ok("🔓 Niveau %d débloqué : %s" % (nouveau, NIVEAUX[nouveau - 1][1]))


def menu_rapide():
    pool_ = [m for m in MISSIONS if m["kind"] in ("qcm", "reponse") or m["diff"] <= 2]
    jamais = [m for m in pool_ if not SAVE["missions"].get(m["id"], {}).get("reussie")]
    random.shuffle(jamais)
    random.shuffle(pool_)
    choix = (jamais[:3] + [m for m in pool_ if m not in jamais[:3]])[:5]
    random.shuffle(choix)
    serie(choix, "rapide", "Rapide")


def menu_theme():
    themes = list(THEMES.keys())
    while True:
        titre("Par thème")
        for i, t in enumerate(themes, 1):
            f, n = theme_exos(t)
            print("  %2d. %-40s %2d/%-2d" % (i, THEMES[t], f, n))
        print()
        r = demander("thème (numéro, f+numéro = fiche, r = retour) > ")
        if r is None or r.strip().lower() in ("r", "q"):
            return
        r = r.strip().lower()
        if r.startswith("f") and r[1:].strip().isdigit():
            k = int(r[1:])
            if 1 <= k <= len(themes):
                afficher_fiche(themes[k - 1])
                pause()
            continue
        if not (r.isdigit() and 1 <= int(r) <= len(themes)):
            continue
        t = themes[int(r) - 1]
        ms = [m for m in MISSIONS if m["theme"] == t]
        a_faire = [m for m in ms if not SAVE["missions"].get(m["id"], {}).get("reussie")]
        o = demander("Toutes les missions (t) ou seulement celles pas encore réussies (Entrée, %d) ? " % len(a_faire))
        if o is None:
            continue
        liste = ms if o.strip().lower() == "t" or not a_faire else a_faire
        serie(sorted(liste, key=lambda m: (m["diff"], m["niveau"])), "theme", THEMES[t])


def menu_erreurs():
    while True:
        errs = [(mid, e) for mid, e in SAVE["erreurs"].items() if mid in PAR_ID]
        titre("Mes erreurs (%d)" % len(errs))
        if not errs:
            ok("  Aucune erreur en attente. Joue des missions et des examens pour en accumuler !")
            pause()
            return
        errs.sort(key=lambda x: (-x[1]["nb"], x[1].get("date", "")))
        for i, (mid, e) in enumerate(errs, 1):
            m = PAR_ID[mid]
            print("  %2d. %-44s %s×%d · %s%s" % (i, m["titre"], C.ROUGE, e["nb"], e.get("raison", ""), C.R))
        print()
        info("  Une mission sort de la liste quand tu la réussis sans indice.")
        r = demander("Entrée = tout rejouer (les plus ratées d'abord), numéro = une seule, r = retour > ")
        if r is None or r.strip().lower() in ("r", "q"):
            return
        r = r.strip()
        if r.isdigit() and 1 <= int(r) <= len(errs):
            serie([PAR_ID[errs[int(r) - 1][0]]], "erreurs", "Erreur")
        elif not r:
            serie([PAR_ID[mid] for mid, _ in errs], "erreurs", "Erreur")


# --------------------------------------------------------------------------
# Examen
# --------------------------------------------------------------------------
def pool(kinds, themes=None, diff_max=4):
    return [m for m in MISSIONS if m["kind"] in kinds and m["diff"] <= diff_max
            and (not themes or m["theme"] in themes)]


def tirer(lst, n, deja):
    lst = [m for m in lst if m["id"] not in deja]
    random.shuffle(lst)
    choisi, themes = [], set()
    for m in lst:  # on évite deux missions du même thème quand c'est possible
        if len(choisi) >= n:
            break
        if m["theme"] not in themes:
            choisi.append(m)
            themes.add(m["theme"])
    for m in lst:
        if len(choisi) >= n:
            break
        if m not in choisi:
            choisi.append(m)
    deja.update(m["id"] for m in choisi)
    return choisi


def composer(n_quest, n_code, themes=None, code_dur=False, diff_max=4):
    deja = set()
    quest = tirer(pool(("qcm", "reponse"), themes), n_quest, deja)
    code = []
    if n_code and code_dur:
        code += tirer([m for m in pool(CODE, themes) if m["diff"] >= 3], 1, deja)
    code += tirer(pool(CODE, themes, diff_max), n_code - len(code), deja)
    random.shuffle(quest)
    code.sort(key=lambda m: m["diff"])
    return quest + code


def menu_examen():
    titre("Mode examen")
    print("  1. Contrôle express   15 min · 5 questions + 1 exercice de code")
    print("  2. Contrôle           30 min · 5 questions + 2 exercices de code")
    print("  3. Examen blanc       1 h    · 6 questions + 4 exercices de code (dont 1 dur)")
    print("  4. Personnalisé       durée, nombre et thèmes au choix")
    print()
    info("  Pas d'indice, pas de fiche, pas de solution. :passer pour sauter. Note sur 20 à la fin.")
    info("  Les exercices de code comptent double. Pour les questions : une seule tentative.")
    r = demander("choix (r = retour) > ")
    if r is None:
        return
    r = r.strip()
    if r == "1":
        lst, duree, nom = composer(5, 1, diff_max=2), 15, "Contrôle express"
    elif r == "2":
        lst, duree, nom = composer(5, 2, diff_max=3), 30, "Contrôle"
    elif r == "3":
        lst, duree, nom = composer(6, 4, code_dur=True), 60, "Examen blanc"
    elif r == "4":
        res = examen_perso()
        if not res:
            return
        lst, duree, nom = res
    else:
        return
    if not lst:
        warn("Aucune mission ne correspond.")
        return
    lancer_examen(lst, duree, nom)


def demander_entier(msg, defaut, mini, maxi):
    while True:
        r = demander("%s [%d] > " % (msg, defaut))
        if r is None:
            return None
        r = r.strip()
        if not r:
            return defaut
        if r.isdigit() and mini <= int(r) <= maxi:
            return int(r)
        warn("Entre un nombre entre %d et %d." % (mini, maxi))


def examen_perso():
    duree = demander_entier("Durée en minutes", 20, 1, 240)
    if duree is None:
        return None
    print("  Contenu : 1. tout   2. questions seulement   3. code seulement   4. thèmes au choix")
    c = demander("contenu [1] > ")
    if c is None:
        return None
    c = c.strip() or "1"
    themes = None
    if c == "4":
        tl = list(THEMES.keys())
        for i, t in enumerate(tl, 1):
            print("  %2d. %s" % (i, THEMES[t]))
        r = demander("numéros séparés par des espaces > ")
        if r is None:
            return None
        themes = [tl[int(x) - 1] for x in r.split() if x.isdigit() and 1 <= int(x) <= len(tl)]
        if not themes:
            return None
    dispo = len(pool(("qcm", "reponse") + CODE, themes))
    n = demander_entier("Nombre de missions (max %d)" % dispo, min(8, dispo), 1, dispo)
    if n is None:
        return None
    if c == "2":
        n_code = 0
    elif c == "3":
        n_code = n
    else:
        n_code = min(len(pool(CODE, themes)), max(1, n // 3))
    lst = composer(n - n_code, n_code, themes)
    return lst, duree, "Examen personnalisé"


def lancer_examen(lst, duree, nom):
    titre("%s : %d missions en %d min" % (nom, len(lst), duree))
    for i, m in enumerate(lst, 1):
        print("  %2d. %-46s %s" % (i, THEMES[m["theme"]], C.DIM + TYPE_LIB[m["kind"]] + C.R))
    print()
    r = demander("Entrée pour démarrer le chrono (r = annuler) > ")
    if r is None or r.strip().lower() == "r":
        return
    shutil.rmtree(EXAMEN_DIR, ignore_errors=True)
    debut = time.time()
    deadline = debut + duree * 60
    resultats = []
    for i, m in enumerate(lst, 1):
        if time.time() > deadline:
            resultats.append((m, {"ok": False, "solution": False, "passe": False, "indices": 0,
                                  "timeout": True, "abandon": False, "id": m["id"]}))
            continue
        res = Partie(m, "examen", deadline=deadline, rang="Examen %d/%d" % (i, len(lst))).jouer()
        if res.get("abandon"):
            r = demander("Abandonner l'examen ? (o/N) > ")
            if r and r.strip().lower() in ("o", "oui", "y"):
                warn("Examen abandonné (non noté).")
                return
            res = Partie(m, "examen", deadline=deadline, rang="Examen %d/%d" % (i, len(lst))).jouer()
            if res.get("abandon"):
                warn("Examen abandonné (non noté).")
                return
        resultats.append((m, res))
    temps = int(time.time() - debut)
    poids = lambda m: 2 if m["kind"] in CODE else 1  # noqa: E731
    total = sum(poids(m) for m, _ in resultats)
    gagne = sum(poids(m) for m, r in resultats if r["ok"])
    note = round(20 * gagne / total * 2) / 2 if total else 0
    titre("%s terminé : %s/20" % (nom, ("%g" % note)))
    info("  Temps : %d min %02d s sur %d min · le code compte double" % (temps // 60, temps % 60, duree))
    print()
    for m, r in resultats:
        s = C.VERT + "✔" if r["ok"] else C.ROUGE + "✘"
        print("  %s%s %s %s" % (s, C.R, m["titre"], C.DIM + "(" + THEMES[m["theme"]] + ")" + C.R))
    for m, r in resultats:
        enregistrer(m, r, "examen")
    rates = [(m, r) for m, r in resultats if not r["ok"]]
    if rates:
        print()
        rep = demander("Voir la correction des %d missions ratées ? (O/n) > " % len(rates))
        if rep is not None and rep.strip().lower() not in ("n", "non"):
            for m, r in rates:
                titre("Correction : " + m["titre"])
                bloc(m["enonce"], C.DIM)
                if m.get("code"):
                    code_bloc(m["code"], C.DIM)
                print()
                if m["kind"] == "qcm":
                    ok("  Bonne réponse : " + ", ".join(sorted(m["bonnes"])))
                    for l, c in zip("abcdefgh", m["choix"]):
                        if l in m["bonnes"]:
                            bloc("%s) %s" % (l, c), C.VERT)
                elif m["kind"] == "reponse":
                    ok("  Réponse : " + m["solution"])
                else:
                    code_bloc(m["solution"], C.MAG)
                if m.get("explication"):
                    bloc(m["explication"], C.DIM)
                if pause_ou_stop():
                    break
        info("  Les missions ratées sont dans « mes erreurs ». Ton code d'examen est dans ~/.cquest/examen/.")
    SAVE["examens"].append({"date": time.strftime("%Y-%m-%d %H:%M"), "mode": nom,
                            "note": note, "missions": len(resultats), "duree_s": temps})
    sauver(SAVE)
    pause()


def pause_ou_stop():
    r = demander(C.DIM + "Entrée : suivante · m : arrêter" + C.R + " ")
    return r is None or r.strip().lower() in ("m", "q")


# --------------------------------------------------------------------------
# Progression, fiches, accueil
# --------------------------------------------------------------------------
def menu_progression():
    titre("Progression")
    total = len(MISSIONS)
    faites = sum(1 for mid, r in SAVE["missions"].items() if r.get("reussie") and mid in PAR_ID)
    print("  Missions réussies : %d/%d   Score : %d pts   Erreurs en attente : %d" % (
        faites, total, score_total(), len([e for e in SAVE["erreurs"] if e in PAR_ID])))
    print()
    for t, nom in THEMES.items():
        f, n = theme_exos(t)
        pct = f / n if n else 0
        barre = C.VERT + "█" * int(pct * 20) + C.DIM + "░" * (20 - int(pct * 20)) + C.R
        print("  %-40s %s %3d%%" % (nom, barre, int(pct * 100)))
    if SAVE["examens"]:
        print()
        print(C.B + "  Derniers examens" + C.R)
        for e in SAVE["examens"][-8:]:
            print("  %s  %-22s %5s/20  (%d missions, %d min)" % (
                e["date"], e["mode"], "%g" % e["note"], e["missions"], e["duree_s"] // 60))
    print()
    r = demander("Entrée = retour · reset = effacer toute la progression > ")
    if r and r.strip() == "reset":
        c = demander("Vraiment tout effacer ? (ton code dans l'atelier est gardé) Tape « oui » > ")
        if c and c.strip() == "oui":
            SAVE.clear()
            SAVE.update({"missions": {}, "erreurs": {}, "examens": [], "lecons": {}})
            sauver(SAVE)
            ok("Progression effacée.")


def menu_fiches():
    tl = list(THEMES.keys())
    while True:
        titre("Fiches de révision")
        for i, t in enumerate(tl, 1):
            print("  %2d. %s" % (i, THEMES[t]))
        r = demander("fiche (numéro, r = retour) > ")
        if r is None or r.strip().lower() in ("r", "q"):
            return
        if r.strip().isdigit() and 1 <= int(r) <= len(tl):
            afficher_fiche(tl[int(r) - 1])
            pause()


BANNIERE = r"""
    ____ ___                  _
   / ___/ _ \ _   _  ___  ___| |_
  | |  | | | | | | |/ _ \/ __| __|
  | |__| |_| | |_| |  __/\__ \ |_
   \____\__\_\\__,_|\___||___/\__|
"""


def accueil_avertissements():
    if not GCC:
        warn("  ⚠ gcc introuvable : sudo apt install -y build-essential gdb valgrind")
    elif not VALGRIND:
        warn("  ⚠ valgrind absent : les missions sur malloc seront moins strictes "
             "(sudo apt install -y valgrind)")


def main():
    global SAVE
    try:  # nos print et la sortie des programmes lancés restent dans le bon ordre
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    for d in (DATA, ATELIER, BUILD, COURS_DIR):
        os.makedirs(d, exist_ok=True)
    SAVE = charger()
    if readline:
        readline.parse_and_bind("tab: complete")
    if hasattr(signal, "SIGTSTP"):
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)
    while True:
        print(C.CYAN + C.B + BANNIERE + C.R)
        info("  Réviser le C en écrivant du vrai code · v%s · %d missions" % (VERSION, len(MISSIONS)))
        accueil_avertissements()
        print()
        n_err = len([e for e in SAVE["erreurs"] if e in PAR_ID])
        print(C.B + C.JAUNE + "  Prochaine étape conseillée : %s" % libelle_etape(prochaine_etape()) + C.R)
        print()
        print("  0. Apprentissage (cours, exemples à lancer, méthode, exos guidés)")
        print("  1. Campagne (niveaux + score)          score : %d pts" % score_total())
        print("  2. Partie rapide (5 missions)")
        print("  3. Examen chronométré (contrôle, examen blanc, personnalisé)")
        print("  4. Par thème")
        print("  5. Mes erreurs" + (" (%d)" % n_err if n_err else ""))
        print("  6. Progression")
        print("  7. Fiches de révision")
        print("  q. Quitter")
        print()
        r = demander("> ")
        if r is None:
            break
        r = r.strip().lower()
        if r == "0":
            menu_apprentissage()
        elif r == "1":
            menu_campagne()
        elif r == "2":
            menu_rapide()
        elif r == "3":
            menu_examen()
        elif r == "4":
            menu_theme()
        elif r == "5":
            menu_erreurs()
        elif r == "6":
            menu_progression()
        elif r == "7":
            menu_fiches()
        elif r in ("q", "quitter", "exit"):
            break
    print("À plus, et bon courage pour le C !")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nÀ plus !")
