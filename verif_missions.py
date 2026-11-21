#!/usr/bin/env python3
"""Vérifie toutes les missions de CQuest (pour qui ajoute des missions) :
  - code : le fichier de départ compile mais ne passe pas les tests ; la solution passe
  - réponse avec auto=True : la sortie du code est bien la réponse attendue
  - QCM : les bonnes réponses existent
  - cours : chaque exemple compile
Usage : python3 verif_missions.py [id_mission ...]
"""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile

TMP = tempfile.mkdtemp(prefix="cquest_verif_")
os.environ["CQUEST_HOME"] = TMP
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cquest  # noqa: E402
from lecons import LECONS  # noqa: E402

COMPILE_PAS_EXPRES = {"compil_corrige", "enum_feu"}   # le départ ne compile pas, c'est voulu
EXEMPLES_EN_ERREUR = {("compil", 1)}          # exemple de cours volontairement faux


def silencieux(f, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = f(*a, **kw)
    return r, buf.getvalue()


def installer(m, contenu):
    d = os.path.join(TMP, "m", m["id"])
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    with open(os.path.join(d, m["fichier"]), "w") as f:
        f.write(contenu)
    for n, c in m.get("headers", {}).items():
        with open(os.path.join(d, n), "w") as f:
            f.write(c)
    return d


def compiler_run(code):
    d = os.path.join(TMP, "ex")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "e.c"), "w") as f:
        f.write(cquest.code_complet(code))
    rc, out, err = cquest.run(["gcc", "-Wall", "-std=c99", "e.c", "-o", "e"], cwd=d)
    if rc != 0:
        return None, err
    rc, out, err = cquest.run(["./e"], cwd=d, timeout=5)
    return out, err


def main():
    os.makedirs(cquest.BUILD, exist_ok=True)
    ids = set(sys.argv[1:])
    erreurs = []
    n = 0
    for m in cquest.MISSIONS:
        if ids and m["id"] not in ids:
            continue
        n += 1
        mid = m["id"]
        if m["kind"] in cquest.CODE:
            d = installer(m, m["starter"])
            cquest.preparer_build(m, d)
            compile_ok, sortie = silencieux(cquest.compiler_utilisateur, m, d, True)
            if not compile_ok and mid not in COMPILE_PAS_EXPRES:
                erreurs.append((mid, "le fichier de départ ne compile pas :\n" + sortie))
            elif compile_ok:
                ok, sortie = silencieux(cquest.verifier_code, m, d)
                if ok:
                    erreurs.append((mid, "le fichier de départ passe déjà les tests"))
            d = installer(m, m["solution"])
            ok, sortie = silencieux(cquest.verifier_code, m, d)
            if not ok:
                erreurs.append((mid, "la solution ne passe pas :\n" + sortie))
        elif m["kind"] == "reponse":
            if m.get("auto"):
                out, err = compiler_run(m["code"])
                if out is None:
                    erreurs.append((mid, "le code ne compile pas :\n" + err))
                elif not cquest.reponse_ok(m, out):
                    erreurs.append((mid, "sortie %r au lieu de %r" % (out, m["reponses"][0])))
        elif m["kind"] == "qcm":
            lettres = "abcdefgh"[:len(m["choix"])]
            if not m["bonnes"] or not set(m["bonnes"]) <= set(lettres):
                erreurs.append((mid, "bonnes réponses invalides"))
        print("." if not erreurs or erreurs[-1][0] != mid else "F", end="", flush=True)
    nex = 0
    if not ids:
        for theme, L in LECONS.items():
            for i, c in enumerate(L["cartes"]):
                for ex in c.get("exemples", []):
                    ex = cquest.ex_norm(ex)
                    nex += 1
                    d = os.path.join(TMP, "ex")
                    os.makedirs(d, exist_ok=True)
                    with open(os.path.join(d, "e.c"), "w") as f:
                        f.write(cquest.code_complet(ex["code"]))
                    rc, out, err = cquest.run(["gcc", "-Wall", "-std=c99", "e.c", "-o", "e"], cwd=d)
                    attendu_ko = (theme, i) in EXEMPLES_EN_ERREUR
                    if (rc != 0) != attendu_ko:
                        erreurs.append(("cours %s carte %d" % (theme, i + 1), err or "compile alors qu'il ne devrait pas"))
    print()
    for mid, msg in erreurs:
        print("\n### %s : %s" % (mid, msg.rstrip()))
    print("\n%d missions, %d exemples de cours vérifiés, %d problème(s)." % (n, nex, len(erreurs)))
    shutil.rmtree(TMP, ignore_errors=True)
    return 1 if erreurs else 0


if __name__ == "__main__":
    sys.exit(main())
