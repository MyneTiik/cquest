"""Missions de CQuest.

Quatre sortes de missions :
  prog     : écrire (ou corriger) un programme complet, testé avec des arguments / une entrée
  fonc     : écrire des fonctions (sans main) ; un main de test caché les appelle
  qcm      : question à choix (prédire, repérer un piège)
  reponse  : réponse courte à taper (que vaut..., qu'affiche...)

Les tests des missions « fonc » sont du C qui utilise CHECK_INT, CHECK_STR, CHECK_TRUE,
CHECK_TAB(t, n, desc, {valeurs}) et section("...").
"""
import textwrap

THEMES = {
    "compil": "Compiler, main, printf, argv",
    "cond": "Conditions : if, opérateurs",
    "boucles": "Boucles : while et for",
    "fonctions": "Fonctions (et récursivité)",
    "tableaux": "Tableaux de pile",
    "types": "Types, sizeof, binaire, ASCII",
    "chaines": "Chaînes de caractères",
    "enum": "enum",
    "pointeurs": "Pointeurs",
    "struct": "struct",
    "entrees": "scanf, fgets, macros, globales",
    "malloc": "Allocation dynamique (malloc/free)",
    "listes": "Listes chaînées",
    "projets": "Projets type examen (César, réseau)",
    "pieges": "Pièges classiques du C",
}
NIVEAUX = [(i + 1, nom, [cle]) for i, (cle, nom) in enumerate(THEMES.items())]
NIVEAU_DE = {cle: i + 1 for i, cle in enumerate(THEMES)}

MISSIONS = []


def _d(s):
    return textwrap.dedent(s).strip("\n") + "\n" if s else s


def _add(kind, mid, theme, titre, enonce, diff, **kw):
    m = {"kind": kind, "id": mid, "theme": theme, "niveau": NIVEAU_DE[theme], "titre": titre,
         "enonce": textwrap.dedent(enonce).strip("\n"), "diff": diff}
    for k in ("solution", "starter", "protos", "tests", "code", "explication"):
        if k in kw and isinstance(kw[k], str):
            kw[k] = _d(kw[k])
            if k in ("explication",):
                kw[k] = kw[k].rstrip("\n")
    if "headers" in kw:
        kw["headers"] = {n: _d(c) for n, c in kw["headers"].items()}
    m.update(kw)
    m.setdefault("indices", [])
    m.setdefault("solution", "")
    assert mid not in {x["id"] for x in MISSIONS}, mid
    MISSIONS.append(m)


def prog(mid, theme, titre, enonce, diff, fichier, starter, solution, tests, **kw):
    """tests : liste de (args, attendu) ou (args, attendu, stdin)."""
    ts = []
    for t in tests:
        d = {"args": t[0], "attendu": t[1]}
        if len(t) > 2:
            d["stdin"] = t[2]
        ts.append(d)
    _add("prog", mid, theme, titre, enonce, diff, fichier=fichier, starter=starter,
         solution=solution, tests=ts, **kw)


def fonc(mid, theme, titre, enonce, diff, fichier, starter, solution, protos, tests, **kw):
    _add("fonc", mid, theme, titre, enonce, diff, fichier=fichier, starter=starter,
         solution=solution, protos=protos, tests=tests, **kw)


def qcm(mid, theme, titre, enonce, diff, choix, bonnes, **kw):
    _add("qcm", mid, theme, titre, enonce, diff, choix=choix, bonnes=bonnes, **kw)


def rep(mid, theme, titre, enonce, diff, reponses, **kw):
    """reponses : liste des réponses acceptées (la première est affichée).
    auto=True : la sortie du champ code doit être exactement reponses[0] (vérifié par les tests)."""
    if isinstance(reponses, str):
        reponses = [reponses]
    kw.setdefault("solution", reponses[0])
    _add("reponse", mid, theme, titre, enonce, diff, reponses=reponses, **kw)


# ==========================================================================
# 1. Compiler, main, printf, argv
# ==========================================================================
prog("compil_corrige", "compil", "Premier contact avec gcc", """
    bonjour.c ne compile pas. Lance :verifier, lis les messages de gcc, corrige le fichier
    jusqu'à ce qu'il compile et affiche :
        Bienvenue dans CQuest, niveau 1 !
    """, 1, "bonjour.c",
    starter=r'''
    #include <stdio.h>

    int main(int argc, char **argv) {
        int niveau = 1
        printf("Bienvenue dans CQuest, niveau %d !\n", nivaeu);
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>

    int main(int argc, char **argv) {
        int niveau = 1;
        printf("Bienvenue dans CQuest, niveau %d !\n", niveau);
        return 0;
    }
    ''',
    tests=[("", "Bienvenue dans CQuest, niveau 1 !")],
    bug=True,
    indices=["Un message gcc : bonjour.c:5:20: error: ... = fichier, ligne 5, colonne 20. Corrige la PREMIÈRE erreur d'abord.",
             "« expected ',' or ';' » : il manque un ; à la fin de l'instruction de la ligne AU-DESSUS.",
             "« undeclared » : le nom de variable est mal tapé."],
    explication="Lis toujours la première erreur : les suivantes en découlent souvent.")

prog("compil_printf", "compil", "Formater avec printf", """
    Dans affiche.c, la variable a vaut 7. Affiche EXACTEMENT, avec un seul printf et des %d :
        a vaut 7, son double vaut 14, sa moitie vaut 3
    (les nombres doivent être calculés à partir de a, pas écrits en dur).
    """, 1, "affiche.c",
    starter=r'''
    #include <stdio.h>

    int main(void) {
        int a = 7;
        printf("a vaut %d\n", a);   // TODO : compléter la phrase avec deux autres %d
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>

    int main(void) {
        int a = 7;
        printf("a vaut %d, son double vaut %d, sa moitie vaut %d\n", a, a * 2, a / 2);
        return 0;
    }
    ''',
    tests=[("", "a vaut 7, son double vaut 14, sa moitie vaut 3")],
    indices=["Chaque %d du format est remplacé, dans l'ordre, par une valeur placée après la virgule.",
             'printf("a vaut %d, ...\\n", a, a * 2, a / 2);'],
    explication="7 / 2 vaut 3 : entre deux int, / fait une division entière.")

prog("compil_somme", "compil", "Somme de deux arguments", """
    somme.c reçoit deux entiers en argument et affiche leur somme :
        ./somme 3 4    ->  7
        ./somme -5 2   ->  -3
    S'il n'y a pas exactement deux arguments : afficher « usage: ./somme a b » et return 1.
    """, 1, "somme.c",
    starter=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        // TODO : vérifier argc, convertir argv[1] et argv[2] avec atoi, afficher la somme
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        if (argc != 3) {
            printf("usage: ./somme a b\n");
            return 1;
        }
        int a = atoi(argv[1]);
        int b = atoi(argv[2]);
        printf("%d\n", a + b);
        return 0;
    }
    ''',
    tests=[("3 4", "7"), ("-5 2", "-3"), ("0 0", "0"), ("1000 2345", "3345"),
           ("5", "usage: ./somme a b"), ("", "usage: ./somme a b"), ("1 2 3", "usage: ./somme a b")],
    indices=["./somme 3 4 : argc vaut 3, argv[0] = \"./somme\", argv[1] = \"3\", argv[2] = \"4\".",
             "argv[1] est une chaîne : atoi(argv[1]) la convertit en int (#include <stdlib.h>).",
             "Teste argc AVANT de lire argv[1] : lire un argument qui n'existe pas fait planter."])

rep("compil_argc", "compil", "Compter les arguments", """
    On lance :   ./prog un deux trois
    Que vaut argc dans le main de prog ?
    """, 1, ["4"],
    indices=["Le nom du programme compte."],
    explication="argv[0] = \"./prog\", argv[1] = \"un\", argv[2] = \"deux\", argv[3] = \"trois\" : argc = 4.")

qcm("compil_qcm_o", "compil", "Que produit gcc ?", """
    On tape :   gcc -Wall -Werror -std=c99 forma.c -o forma
    Que se passe-t-il si forma.c contient une variable déclarée mais jamais utilisée ?
    """, 2,
    ["gcc crée l'exécutable forma et affiche juste un avertissement",
     "gcc refuse de compiler : avec -Werror, l'avertissement devient une erreur",
     "gcc crée a.out au lieu de forma",
     "le programme compile mais plante à l'exécution"],
    "b",
    explication="-Wall active les avertissements (unused variable en fait partie) et -Werror les "
                "transforme en erreurs : pas d'exécutable. -o forma choisit le nom (sinon a.out).")

qcm("compil_qcm_err", "compil", "Lire un message d'erreur", """
    gcc affiche :
        calc.c:12:5: error: expected ';' before 'return'
    Où se trouve, le plus souvent, l'oubli à corriger ?
    """, 2,
    ["à la ligne 12, colonne 5, juste avant return",
     "à la fin de l'instruction qui PRÉCÈDE le return (souvent la ligne 11)",
     "à la dernière ligne du fichier",
     "dans le #include en haut du fichier"],
    "b",
    explication="gcc s'aperçoit du ; manquant seulement quand il tombe sur le mot suivant (return, "
                "ligne 12). Le ; manque à la fin de l'instruction d'avant.")

qcm("compil_qcm_atoi", "compil", "argv et atoi", """
    Dans int main(int argc, char **argv), on lance ./prog 42.
    Pourquoi écrit-on  int n = atoi(argv[1]);  et pas  int n = argv[1];  ?
    """, 1,
    ["argv[1] est la chaîne de caractères \"42\", pas le nombre 42 : atoi la convertit",
     "argv[1] contient le nom du programme",
     "atoi vérifie que l'argument existe",
     "c'est pareil, atoi est juste plus lisible"],
    "a",
    explication="Tout ce qui arrive par la ligne de commande est du texte (char *). atoi = ascii to int.")

rep("compil_rep_div", "compil", "Division entière", """
    Qu'affiche ce code ? (tape la sortie exacte)
    """, 1, ["3-1"],
    code=r'''
    printf("%d-%d\n", 7 / 2, 7 % 2);
    ''', auto=True,
    explication="7 / 2 entre deux int = 3 (on garde la partie entière), 7 % 2 = 1 (le reste).")


# ==========================================================================
# 2. Conditions
# ==========================================================================
prog("cond_compare", "cond", "Comparer deux nombres", """
    compare.c reçoit a et b et affiche DEUX lignes :
      ligne 1 : « a est plus grand que b », « a est egal a b » ou « a est plus petit que b »
      ligne 2 : « a est pair » ou « a est impair »
        ./compare 5 3   ->  5 est plus grand que 3
                            5 est impair
    Mauvais nombre d'arguments : « usage: ./compare a b » et return 1.
    Attention aux nombres négatifs.
    """, 2, "compare.c",
    starter=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        if (argc != 3) {
            printf("usage: ./compare a b\n");
            return 1;
        }
        int a = atoi(argv[1]);
        int b = atoi(argv[2]);
        if (a > b)
            printf("%d est plus grand que %d\n", a, b);
        else if (a == b)
            printf("%d est egal a %d\n", a, b);
        else
            printf("%d est plus petit que %d\n", a, b);
        if (a % 2 == 0)
            printf("%d est pair\n", a);
        else
            printf("%d est impair\n", a);
        return 0;
    }
    ''',
    tests=[("5 3", "5 est plus grand que 3\n5 est impair"), ("2 9", "2 est plus petit que 9\n2 est pair"),
           ("-4 -4", "-4 est egal a -4\n-4 est pair"), ("0 1", "0 est plus petit que 1\n0 est pair"),
           ("-3 -10", "-3 est plus grand que -10\n-3 est impair"),
           ("-7 0", "-7 est plus petit que 0\n-7 est impair"), ("5", "usage: ./compare a b")],
    indices=["if (a > b) { ... } else if (a == b) { ... } else { ... }",
             "Pair : a % 2 == 0. Piège : en C, -3 % 2 vaut -1, donc « a % 2 == 1 » rate les impairs négatifs."])

prog("cond_signe", "cond", "Signe d'un nombre", """
    signe.c reçoit un entier x et affiche « positif », « negatif » ou « nul ».
        ./signe 12  -> positif        ./signe -3  -> negatif        ./signe 0  -> nul
    Sans argument : « usage: ./signe x » et return 1.
    """, 1, "signe.c",
    starter=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        if (argc != 2) {
            printf("usage: ./signe x\n");
            return 1;
        }
        int x = atoi(argv[1]);
        if (x > 0)
            printf("positif\n");
        else if (x < 0)
            printf("negatif\n");
        else
            printf("nul\n");
        return 0;
    }
    ''',
    tests=[("12", "positif"), ("-3", "negatif"), ("0", "nul"), ("1", "positif"), ("", "usage: ./signe x")],
    indices=["Trois cas : if / else if / else."])

fonc("cond_max3", "cond", "Le plus grand de trois", """
    Dans max3.c (pas de main), écris :
      int max3(int a, int b, int c)    renvoie le plus grand des trois
      int min3(int a, int b, int c)    renvoie le plus petit des trois
    """, 1, "max3.c",
    starter=r'''
    int max3(int a, int b, int c) {
        // TODO
        return 0;
    }

    int min3(int a, int b, int c) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int max3(int a, int b, int c) {
        int m = a;
        if (b > m)
            m = b;
        if (c > m)
            m = c;
        return m;
    }

    int min3(int a, int b, int c) {
        int m = a;
        if (b < m)
            m = b;
        if (c < m)
            m = c;
        return m;
    }
    ''',
    protos="int max3(int a, int b, int c);\nint min3(int a, int b, int c);",
    tests=r'''
    section("max3");
    CHECK_INT(max3(1, 2, 3), 3, "max3(1, 2, 3)");
    CHECK_INT(max3(3, 2, 1), 3, "max3(3, 2, 1)");
    CHECK_INT(max3(2, 9, 4), 9, "max3(2, 9, 4)");
    CHECK_INT(max3(-5, -2, -9), -2, "max3(-5, -2, -9)");
    CHECK_INT(max3(4, 4, 4), 4, "max3(4, 4, 4)");
    section("min3");
    CHECK_INT(min3(1, 2, 3), 1, "min3(1, 2, 3)");
    CHECK_INT(min3(3, 2, 1), 1, "min3(3, 2, 1)");
    CHECK_INT(min3(2, -9, 4), -9, "min3(2, -9, 4)");
    ''',
    indices=["Garde le meilleur candidat dans une variable m, puis compare-le aux deux autres."])

fonc("cond_bissextile", "cond", "Années bissextiles", """
    Dans annee.c (pas de main), écris :
      int bissextile(int a)
          1 si l'année a est bissextile, 0 sinon. Règle : divisible par 4 mais pas par 100,
          OU divisible par 400.   2024 -> 1   1900 -> 0   2000 -> 1   2023 -> 0
      int jours_fevrier(int a)    29 ou 28 selon l'année
    """, 2, "annee.c",
    starter=r'''
    int bissextile(int a) {
        // TODO
        return 0;
    }

    int jours_fevrier(int a) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int bissextile(int a) {
        return (a % 4 == 0 && a % 100 != 0) || a % 400 == 0;
    }

    int jours_fevrier(int a) {
        if (bissextile(a))
            return 29;
        return 28;
    }
    ''',
    protos="int bissextile(int a);\nint jours_fevrier(int a);",
    tests=r'''
    section("bissextile");
    CHECK_INT(bissextile(2024), 1, "bissextile(2024)");
    CHECK_INT(bissextile(2023), 0, "bissextile(2023)");
    CHECK_INT(bissextile(1900), 0, "bissextile(1900)");
    CHECK_INT(bissextile(2000), 1, "bissextile(2000)");
    CHECK_INT(bissextile(2100), 0, "bissextile(2100)");
    CHECK_INT(bissextile(1996), 1, "bissextile(1996)");
    section("jours_fevrier");
    CHECK_INT(jours_fevrier(2024), 29, "jours_fevrier(2024)");
    CHECK_INT(jours_fevrier(1900), 28, "jours_fevrier(1900)");
    ''',
    indices=["« divisible par 4 » s'écrit a % 4 == 0.",
             "Combine avec && (et), || (ou) et des parenthèses : (A && B) || C.",
             "jours_fevrier peut appeler bissextile."])

qcm("cond_qcm_affect", "cond", "= ou == ?", """
    Qu'affiche ce code ?
    """, 2,
    ["zero", "pas zero", "rien, ça ne compile pas avec -Wall -Werror",
     "a vaut 5"],
    "c",
    code=r'''
    int a = 5;
    if (a = 0)
        printf("zero\n");
    else
        printf("pas zero\n");
    ''',
    indices=["= affecte, == compare. Que vaut l'expression (a = 0) ?"],
    explication="(a = 0) range 0 dans a et vaut 0 (faux) : sans options, le code afficherait « pas zero » "
                "en ayant écrasé a. gcc -Wall prévient (« suggest parentheses around assignment »), et "
                "-Werror en fait une erreur. Pour comparer : a == 0.")

rep("cond_rep_logique", "cond", "Opérateurs logiques", """
    Qu'affiche ce code ? (une condition vraie vaut 1, fausse vaut 0)
    """, 2, ["0 1 0"],
    code=r'''
    int a = 7;
    printf("%d %d %d\n", (a > 0) && (a < 5), (a % 2 == 0) || (a == 7), !(a > 3));
    ''', auto=True,
    explication="(7>0)&&(7<5) = 1&&0 = 0 ; (faux)||(vrai) = 1 ; !(vrai) = 0.")

qcm("cond_qcm_intervalle", "cond", "Tester un intervalle", """
    Quelle condition teste correctement que a est dans [10 ; 20] (bornes comprises) ?
    """, 2,
    ["(10 <= a <= 20)", "(a >= 10 && a <= 20)", "(a >= 10 || a <= 20)", "(a > 10 && a < 20)"],
    "b",
    explication="10 <= a <= 20 se lit (10 <= a) <= 20, soit 0 <= 20 ou 1 <= 20 : toujours vrai ! "
                "|| serait vrai pour tout nombre ; > et < excluent les bornes.")


# ==========================================================================
# 3. Boucles
# ==========================================================================
prog("boucles_chiffres", "boucles", "Compter les chiffres", """
    chiffres.c reçoit un entier x et affiche son nombre de chiffres (exo démo du cours).
        ./chiffres 45 -> 2     ./chiffres 1023 -> 4     ./chiffres 0 -> 1     ./chiffres -450 -> 3
    Sans argument : « usage: ./chiffres x » et return 1. Utilise une boucle (pas de strlen).
    """, 2, "chiffres.c",
    starter=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        if (argc != 2) {
            printf("usage: ./chiffres x\n");
            return 1;
        }
        int x = atoi(argv[1]);
        if (x < 0)
            x = -x;
        int n = 1;
        while (x >= 10) {
            x = x / 10;
            n += 1;
        }
        printf("%d\n", n);
        return 0;
    }
    ''',
    tests=[("45", "2"), ("1023", "4"), ("7", "1"), ("1000000", "7"), ("0", "1"), ("-450", "3"), ("-9", "1"),
           ("", "usage: ./chiffres x")],
    indices=["x / 10 enlève le dernier chiffre : 1023 / 10 = 102.",
             "Compte les divisions. Cas spéciaux : 0 (a 1 chiffre) et les négatifs (rends x positif d'abord)."])

prog("boucles_entre", "boucles", "Les nombres entre a et b", """
    entre.c reçoit a et b et affiche tous les entiers de a à b inclus, un par ligne (exo démo).
    Si a > b, on compte à rebours.
        ./entre 3 6  ->  3 4 5 6 (un par ligne)        ./entre 2 -1  ->  2 1 0 -1
    Mauvais nombre d'arguments : « usage: ./entre a b » et return 1.
    """, 1, "entre.c",
    starter=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        if (argc != 3) {
            printf("usage: ./entre a b\n");
            return 1;
        }
        int a = atoi(argv[1]);
        int b = atoi(argv[2]);
        if (a <= b) {
            for (int i = a; i <= b; i += 1)
                printf("%d\n", i);
        } else {
            for (int i = a; i >= b; i -= 1)
                printf("%d\n", i);
        }
        return 0;
    }
    ''',
    tests=[("3 6", "3\n4\n5\n6"), ("2 -1", "2\n1\n0\n-1"), ("5 5", "5"), ("-2 1", "-2\n-1\n0\n1"),
           ("4", "usage: ./entre a b")],
    indices=["for (int i = a; i <= b; i += 1) printf(\"%d\\n\", i);",
             "Pour le compte à rebours : une deuxième boucle avec i -= 1 et la condition i >= b."])

prog("boucles_table", "boucles", "Table de multiplication", """
    table.c reçoit n et affiche sa table de 1 à 10 :
        ./table 7  ->  7 x 1 = 7
                       7 x 2 = 14
                       ...
                       7 x 10 = 70
    Sans argument : « usage: ./table n » et return 1.
    """, 1, "table.c",
    starter=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        if (argc != 2) {
            printf("usage: ./table n\n");
            return 1;
        }
        int n = atoi(argv[1]);
        for (int i = 1; i <= 10; i += 1)
            printf("%d x %d = %d\n", n, i, n * i);
        return 0;
    }
    ''',
    tests=[("7", "\n".join("7 x %d = %d" % (i, 7 * i) for i in range(1, 11))),
           ("-3", "\n".join("-3 x %d = %d" % (i, -3 * i) for i in range(1, 11))),
           ("", "usage: ./table n")],
    indices=["Une boucle for de 1 à 10 inclus, et un printf avec trois %d."])

prog("boucles_triangle", "boucles", "Triangle d'étoiles", """
    triangle.c reçoit n et affiche un triangle de n lignes : la ligne i contient i étoiles.
        ./triangle 4  ->  *
                          **
                          ***
                          ****
    n <= 0 : n'affiche rien. Sans argument : « usage: ./triangle n » et return 1.
    """, 2, "triangle.c",
    starter=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    #include <stdio.h>
    #include <stdlib.h>

    int main(int argc, char **argv) {
        if (argc != 2) {
            printf("usage: ./triangle n\n");
            return 1;
        }
        int n = atoi(argv[1]);
        for (int i = 1; i <= n; i += 1) {
            for (int j = 0; j < i; j += 1)
                printf("*");
            printf("\n");
        }
        return 0;
    }
    ''',
    tests=[("4", "*\n**\n***\n****"), ("1", "*"), ("0", ""), ("6", "\n".join("*" * i for i in range(1, 7))),
           ("", "usage: ./triangle n")],
    indices=["Deux boucles imbriquées : une pour les lignes (i de 1 à n), une pour les étoiles de la ligne.",
             "Après la boucle intérieure, printf(\"\\n\") pour passer à la ligne suivante."])

fonc("boucles_somme_chiffres", "boucles", "Somme des chiffres", """
    Dans chiffres.c (pas de main), écris :
      int somme_chiffres(int x)     somme des chiffres de x (le signe ne compte pas)
                                    1234 -> 10    -507 -> 12    0 -> 0
      int miroir(int x)             x écrit à l'envers, x >= 0 :  1234 -> 4321    120 -> 21
    """, 2, "chiffres.c",
    starter=r'''
    int somme_chiffres(int x) {
        // TODO
        return 0;
    }

    int miroir(int x) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int somme_chiffres(int x) {
        if (x < 0)
            x = -x;
        int s = 0;
        while (x > 0) {
            s += x % 10;
            x = x / 10;
        }
        return s;
    }

    int miroir(int x) {
        int r = 0;
        while (x > 0) {
            r = r * 10 + x % 10;
            x = x / 10;
        }
        return r;
    }
    ''',
    protos="int somme_chiffres(int x);\nint miroir(int x);",
    tests=r'''
    section("somme_chiffres");
    CHECK_INT(somme_chiffres(1234), 10, "somme_chiffres(1234)");
    CHECK_INT(somme_chiffres(-507), 12, "somme_chiffres(-507)");
    CHECK_INT(somme_chiffres(0), 0, "somme_chiffres(0)");
    CHECK_INT(somme_chiffres(9), 9, "somme_chiffres(9)");
    section("miroir");
    CHECK_INT(miroir(1234), 4321, "miroir(1234)");
    CHECK_INT(miroir(120), 21, "miroir(120)");
    CHECK_INT(miroir(7), 7, "miroir(7)");
    CHECK_INT(miroir(0), 0, "miroir(0)");
    ''',
    indices=["x % 10 donne le dernier chiffre, x / 10 l'enlève.",
             "miroir : à chaque tour, r = r * 10 + dernier chiffre."])

rep("boucles_rep_while", "boucles", "Suivre un while", """
    Qu'affiche ce code (tiré du cours) ?
    """, 1, ["12"],
    code=r'''
    int r = 0;
    int a = 3;
    int b = 4;
    while (b > 0) {
        r += a;
        b -= 1;
    }
    printf("%d\n", r);
    ''', auto=True,
    explication="La boucle ajoute a à r, b fois : 3 + 3 + 3 + 3 = 12. C'est une multiplication.")

rep("boucles_rep_for", "boucles", "Compter les tours", """
    Qu'affiche ce code ?
    """, 1, ["4"],
    code=r'''
    int n = 0;
    for (int i = 0; i < 10; i += 3)
        n += 1;
    printf("%d\n", n);
    ''', auto=True,
    explication="i prend les valeurs 0, 3, 6, 9 (12 n'est pas < 10) : 4 tours.")

qcm("boucles_qcm_infinie", "boucles", "Boucle infinie", """
    Laquelle de ces boucles ne s'arrête JAMAIS ?
    """, 2,
    ["int i = 0; while (i < 10) { printf(\"%d\", i); i += 1; }",
     "int i = 0; while (i < 10) { printf(\"%d\", i); }",
     "for (int i = 10; i > 0; i -= 2) printf(\"%d\", i);",
     "int i = 1; while (i < 100) i = i * 2;"],
    "b",
    explication="En b, i n'est jamais modifié : i < 10 reste vrai pour toujours. Si ton programme ne "
                "rend pas la main, Ctrl+C l'arrête.")


# ==========================================================================
# 4. Fonctions
# ==========================================================================
fonc("fonc_greater_puissance", "fonctions", "Premières fonctions", """
    Dans fonctions.c (pas de main : le jeu fournit le sien), écris :
      int greater(int a, int b)      le plus grand des deux (exemple du cours)
      int puissance(int x, int n)    x puissance n, n >= 0, avec une boucle
                                     puissance(2, 10) -> 1024    puissance(5, 0) -> 1
    """, 1, "fonctions.c",
    starter=r'''
    int greater(int a, int b) {
        // TODO
        return 0;
    }

    int puissance(int x, int n) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int greater(int a, int b) {
        if (a > b)
            return a;
        return b;
    }

    int puissance(int x, int n) {
        int r = 1;
        for (int i = 0; i < n; i += 1)
            r = r * x;
        return r;
    }
    ''',
    protos="int greater(int a, int b);\nint puissance(int x, int n);",
    tests=r'''
    section("greater");
    CHECK_INT(greater(3, 8), 8, "greater(3, 8)");
    CHECK_INT(greater(8, 3), 8, "greater(8, 3)");
    CHECK_INT(greater(-2, -9), -2, "greater(-2, -9)");
    CHECK_INT(greater(4, 4), 4, "greater(4, 4)");
    section("puissance");
    CHECK_INT(puissance(2, 10), 1024, "puissance(2, 10)");
    CHECK_INT(puissance(5, 0), 1, "puissance(5, 0)");
    CHECK_INT(puissance(-3, 3), -27, "puissance(-3, 3)");
    CHECK_INT(puissance(7, 1), 7, "puissance(7, 1)");
    ''',
    indices=["Forme : type_retour nom(type param, ...) { ... return valeur; }",
             "puissance : pars de r = 1 et multiplie n fois par x.",
             "Pour tester toi-même : :essai crée essai.c avec un main."])

fonc("fonc_multiples_rect", "fonctions", "Multiples et triangles", """
    Dans exos.c (pas de main), écris (exos démo du cours) :
      int nb_multiples(int a, int b, int c)
          nombre d'entiers de [a ; b] multiples de c (a <= b, c > 0)
          nb_multiples(1, 10, 3) -> 3    nb_multiples(0, 10, 5) -> 3
      int est_rectangle(int a, int b, int c)
          1 si le triangle de côtés a, b, c est rectangle (hypoténuse a, b OU c), 0 sinon
    """, 2, "exos.c",
    starter=r'''
    int nb_multiples(int a, int b, int c) {
        // TODO
        return 0;
    }

    int est_rectangle(int a, int b, int c) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int nb_multiples(int a, int b, int c) {
        int n = 0;
        for (int i = a; i <= b; i += 1)
            if (i % c == 0)
                n += 1;
        return n;
    }

    int est_rectangle(int a, int b, int c) {
        return a * a + b * b == c * c || a * a + c * c == b * b || b * b + c * c == a * a;
    }
    ''',
    protos="int nb_multiples(int a, int b, int c);\nint est_rectangle(int a, int b, int c);",
    tests=r'''
    section("nb_multiples");
    CHECK_INT(nb_multiples(1, 10, 3), 3, "nb_multiples(1, 10, 3)");
    CHECK_INT(nb_multiples(0, 10, 5), 3, "nb_multiples(0, 10, 5)");
    CHECK_INT(nb_multiples(7, 7, 7), 1, "nb_multiples(7, 7, 7)");
    CHECK_INT(nb_multiples(8, 8, 7), 0, "nb_multiples(8, 8, 7)");
    CHECK_INT(nb_multiples(-6, 6, 3), 5, "nb_multiples(-6, 6, 3)");
    section("est_rectangle");
    CHECK_INT(est_rectangle(3, 4, 5), 1, "est_rectangle(3, 4, 5)");
    CHECK_INT(est_rectangle(5, 3, 4), 1, "est_rectangle(5, 3, 4)");
    CHECK_INT(est_rectangle(4, 5, 3), 1, "est_rectangle(4, 5, 3)");
    CHECK_INT(est_rectangle(6, 8, 10), 1, "est_rectangle(6, 8, 10)");
    CHECK_INT(est_rectangle(2, 3, 4), 0, "est_rectangle(2, 3, 4)");
    CHECK_INT(est_rectangle(5, 5, 5), 0, "est_rectangle(5, 5, 5)");
    ''',
    indices=["nb_multiples : boucle de a à b inclus, et i % c == 0.",
             "est_rectangle : Pythagore, en testant les 3 hypoténuses possibles avec ||."])

fonc("fonc_pgcd", "fonctions", "PGCD et PPCM", """
    Dans arith.c (pas de main), écris :
      int pgcd(int a, int b)    plus grand diviseur commun (a, b > 0), algorithme d'Euclide :
                                tant que b != 0 : (a, b) devient (b, a % b) ; le résultat est a
      int ppcm(int a, int b)    plus petit multiple commun = a * b / pgcd(a, b)
    """, 2, "arith.c",
    starter=r'''
    int pgcd(int a, int b) {
        // TODO
        return 0;
    }

    int ppcm(int a, int b) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int pgcd(int a, int b) {
        while (b != 0) {
            int r = a % b;
            a = b;
            b = r;
        }
        return a;
    }

    int ppcm(int a, int b) {
        return a / pgcd(a, b) * b;
    }
    ''',
    protos="int pgcd(int a, int b);\nint ppcm(int a, int b);",
    tests=r'''
    section("pgcd");
    CHECK_INT(pgcd(12, 18), 6, "pgcd(12, 18)");
    CHECK_INT(pgcd(18, 12), 6, "pgcd(18, 12)");
    CHECK_INT(pgcd(7, 13), 1, "pgcd(7, 13)");
    CHECK_INT(pgcd(25, 5), 5, "pgcd(25, 5)");
    CHECK_INT(pgcd(9, 9), 9, "pgcd(9, 9)");
    section("ppcm");
    CHECK_INT(ppcm(4, 6), 12, "ppcm(4, 6)");
    CHECK_INT(ppcm(7, 3), 21, "ppcm(7, 3)");
    CHECK_INT(ppcm(5, 10), 10, "ppcm(5, 10)");
    ''',
    indices=["Pour faire « (a, b) devient (b, a % b) », il faut une variable temporaire : r = a % b; a = b; b = r;",
             "ppcm peut appeler pgcd."])

fonc("fonc_premier", "fonctions", "Nombres premiers", """
    Dans premiers.c (pas de main), écris :
      int est_premier(int n)    1 si n est premier, 0 sinon (0 et 1 ne sont pas premiers)
      int nb_premiers(int n)    combien de nombres premiers entre 2 et n inclus
                                nb_premiers(10) -> 4   (2, 3, 5, 7)
    """, 2, "premiers.c",
    starter=r'''
    int est_premier(int n) {
        // TODO
        return 0;
    }

    int nb_premiers(int n) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int est_premier(int n) {
        if (n < 2)
            return 0;
        for (int d = 2; d * d <= n; d += 1)
            if (n % d == 0)
                return 0;
        return 1;
    }

    int nb_premiers(int n) {
        int c = 0;
        for (int i = 2; i <= n; i += 1)
            if (est_premier(i))
                c += 1;
        return c;
    }
    ''',
    protos="int est_premier(int n);\nint nb_premiers(int n);",
    tests=r'''
    section("est_premier");
    CHECK_INT(est_premier(2), 1, "est_premier(2)");
    CHECK_INT(est_premier(17), 1, "est_premier(17)");
    CHECK_INT(est_premier(21), 0, "est_premier(21)");
    CHECK_INT(est_premier(1), 0, "est_premier(1)");
    CHECK_INT(est_premier(0), 0, "est_premier(0)");
    CHECK_INT(est_premier(49), 0, "est_premier(49)");
    CHECK_INT(est_premier(97), 1, "est_premier(97)");
    section("nb_premiers");
    CHECK_INT(nb_premiers(10), 4, "nb_premiers(10)");
    CHECK_INT(nb_premiers(1), 0, "nb_premiers(1)");
    CHECK_INT(nb_premiers(100), 25, "nb_premiers(100)");
    ''',
    indices=["n est premier s'il n'a aucun diviseur d entre 2 et n - 1 (n % d == 0).",
             "Dès qu'un diviseur est trouvé : return 0. Après la boucle : return 1.",
             "nb_premiers appelle est_premier pour chaque i de 2 à n."])

fonc("fonc_recursif", "fonctions", "Récursivité", """
    Dans recursif.c (pas de main), écris ces fonctions SANS boucle, en les faisant
    s'appeler elles-mêmes (exo récursivité du cours) :
      int fact(int n)         n! = n * (n-1) * ... * 1, et 0! = 1
      int fibo(int n)         fibo(0) = 0, fibo(1) = 1, fibo(n) = fibo(n-1) + fibo(n-2)
      int somme_rec(int n)    1 + 2 + ... + n (0 si n <= 0)
    """, 3, "recursif.c",
    starter=r'''
    int fact(int n) {
        // TODO
        return 0;
    }

    int fibo(int n) {
        // TODO
        return 0;
    }

    int somme_rec(int n) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int fact(int n) {
        if (n <= 1)
            return 1;
        return n * fact(n - 1);
    }

    int fibo(int n) {
        if (n < 2)
            return n;
        return fibo(n - 1) + fibo(n - 2);
    }

    int somme_rec(int n) {
        if (n <= 0)
            return 0;
        return n + somme_rec(n - 1);
    }
    ''',
    protos="int fact(int n);\nint fibo(int n);\nint somme_rec(int n);",
    tests=r'''
    section("fact");
    CHECK_INT(fact(0), 1, "fact(0)");
    CHECK_INT(fact(1), 1, "fact(1)");
    CHECK_INT(fact(5), 120, "fact(5)");
    CHECK_INT(fact(10), 3628800, "fact(10)");
    section("fibo");
    CHECK_INT(fibo(0), 0, "fibo(0)");
    CHECK_INT(fibo(1), 1, "fibo(1)");
    CHECK_INT(fibo(7), 13, "fibo(7)");
    CHECK_INT(fibo(20), 6765, "fibo(20)");
    section("somme_rec");
    CHECK_INT(somme_rec(4), 10, "somme_rec(4)");
    CHECK_INT(somme_rec(0), 0, "somme_rec(0)");
    CHECK_INT(somme_rec(100), 5050, "somme_rec(100)");
    ''',
    indices=["Une fonction récursive a toujours : un cas de base (on renvoie directement) et un appel "
             "à elle-même sur un problème plus petit.",
             "fact : si n <= 1 return 1 ; sinon return n * fact(n - 1);"])

qcm("fonc_qcm_valeur", "fonctions", "Passage par valeur", """
    Qu'affiche ce programme ?
    """, 2,
    ["1", "5", "6", "ça ne compile pas"],
    "a",
    code=r'''
    #include <stdio.h>

    void f(int x) {
        x = 5;
    }

    int main(void) {
        int a = 1;
        f(a);
        printf("%d\n", a);
        return 0;
    }
    ''',
    indices=["f reçoit une COPIE de a."],
    explication="Les paramètres sont des copies : modifier x ne touche pas a. Pour qu'une fonction "
                "modifie une variable de l'appelant, il faut lui passer son adresse (thème pointeurs).")

rep("fonc_rep_appels", "fonctions", "Suivre des appels", """
    Qu'affiche ce programme ?
    """, 2, ["13"],
    code=r'''
    #include <stdio.h>

    int double_de(int x) {
        return 2 * x;
    }

    int plus_un(int x) {
        return x + 1;
    }

    int main(void) {
        printf("%d\n", plus_un(double_de(plus_un(5))));
        return 0;
    }
    ''', auto=True,
    explication="On évalue de l'intérieur vers l'extérieur : plus_un(5) = 6, double_de(6) = 12, plus_un(12) = 13.")

qcm("fonc_qcm_proto", "fonctions", "Fonction déclarée trop tard", """
    Ce fichier est compilé avec gcc -Wall -Werror -std=c99. Que se passe-t-il ?
    """, 3,
    ["il compile et affiche 9",
     "erreur : carre est utilisée avant d'être déclarée (implicit declaration)",
     "il compile mais affiche une valeur au hasard",
     "erreur : main doit être la dernière fonction du fichier"],
    "b",
    code=r'''
    #include <stdio.h>

    int main(void) {
        printf("%d\n", carre(3));
        return 0;
    }

    int carre(int x) {
        return x * x;
    }
    ''',
    explication="Le compilateur lit de haut en bas : quand il voit carre(3), il ne la connaît pas encore. "
                "Solutions : définir carre AVANT main, ou mettre son prototype en haut : int carre(int x);")


# ==========================================================================
# 5. Tableaux
# ==========================================================================
fonc("tab_somme_min", "tableaux", "Somme et minimum", """
    Dans tableaux.c (pas de main), écris :
      int somme_tab(int t[], int l)     somme des l cases de t
      int indice_min(int t[], int l)    indice de la plus petite valeur (la première si égalité),
                                        -1 si l == 0
    """, 1, "tableaux.c",
    starter=r'''
    int somme_tab(int t[], int l) {
        // TODO
        return 0;
    }

    int indice_min(int t[], int l) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int somme_tab(int t[], int l) {
        int s = 0;
        for (int i = 0; i < l; i += 1)
            s += t[i];
        return s;
    }

    int indice_min(int t[], int l) {
        if (l == 0)
            return -1;
        int m = 0;
        for (int i = 1; i < l; i += 1)
            if (t[i] < t[m])
                m = i;
        return m;
    }
    ''',
    protos="int somme_tab(int t[], int l);\nint indice_min(int t[], int l);",
    tests=r'''
    int t1[] = {4, -2, 7, 1, -2, 10};
    int t2[] = {42};
    int t3[] = {9, 8, 7, 6};
    section("somme_tab");
    CHECK_INT(somme_tab(t1, 6), 18, "somme_tab({4,-2,7,1,-2,10}, 6)");
    CHECK_INT(somme_tab(t1, 3), 9, "somme_tab({4,-2,7,...}, 3)  (seulement 3 cases)");
    CHECK_INT(somme_tab(t2, 1), 42, "somme_tab({42}, 1)");
    CHECK_INT(somme_tab(t1, 0), 0, "somme_tab(t, 0)");
    section("indice_min");
    CHECK_INT(indice_min(t1, 6), 1, "indice_min({4,-2,7,1,-2,10}, 6)");
    CHECK_INT(indice_min(t2, 1), 0, "indice_min({42}, 1)");
    CHECK_INT(indice_min(t3, 4), 3, "indice_min({9,8,7,6}, 4)");
    CHECK_INT(indice_min(t1, 0), -1, "indice_min(t, 0)");
    ''',
    indices=["Une fonction ne connaît pas la taille d'un tableau reçu : c'est pour ça qu'on passe l.",
             "indice_min : garde l'INDICE du minimum (m), et compare t[i] < t[m]."])

fonc("tab_sum_arrays", "tableaux", "Additionner deux tableaux", """
    Dans tableaux.c (pas de main), écris (exo du cours) :
      void sum_arrays(int a[], int b[], int r[], int n)    r[i] = a[i] + b[i] pour chaque case
      void copie_tab(int src[], int dst[], int n)          copie les n cases de src dans dst
    """, 1, "tableaux.c",
    starter=r'''
    void sum_arrays(int a[], int b[], int r[], int n) {
        // TODO
    }

    void copie_tab(int src[], int dst[], int n) {
        // TODO
    }
    ''',
    solution=r'''
    void sum_arrays(int a[], int b[], int r[], int n) {
        for (int i = 0; i < n; i += 1)
            r[i] = a[i] + b[i];
    }

    void copie_tab(int src[], int dst[], int n) {
        for (int i = 0; i < n; i += 1)
            dst[i] = src[i];
    }
    ''',
    protos="void sum_arrays(int a[], int b[], int r[], int n);\nvoid copie_tab(int src[], int dst[], int n);",
    tests=r'''
    int a[] = {1, 2, 3, 4}, b[] = {10, 20, 30, 40}, r[] = {0, 0, 0, 0};
    section("sum_arrays");
    sum_arrays(a, b, r, 4);
    CHECK_TAB(r, 4, "sum_arrays({1,2,3,4}, {10,20,30,40})", {11, 22, 33, 44});
    CHECK_TAB(a, 4, "a n'est pas modifié", {1, 2, 3, 4});
    section("copie_tab");
    int d[5] = {0, 0, 0, 0, -1};
    copie_tab(b, d, 4);
    CHECK_TAB(d, 5, "copie_tab({10,20,30,40}, d, 4)  (la 5e case ne bouge pas)", {10, 20, 30, 40, -1});
    ''',
    indices=["On ne peut pas renvoyer un tableau : la fonction écrit dans r, et l'appelant voit le résultat.",
             "Une boucle for de 0 à n - 1."])

fonc("tab_tous_presents", "tableaux", "Inclusion de tableaux triés", """
    Dans tableaux.c (pas de main), écris (exo du cours) :
      int tous_presents(int a[], int la, int b[], int lb)
          a et b sont triés (croissant). Renvoie 1 si chaque élément de b est dans a, 0 sinon.
          ({1,3,5,7,9,11}, {3,9}) -> 1      ({1,3,5,7,9,11}, {3,4}) -> 0
    """, 3, "tableaux.c",
    starter=r'''
    int tous_presents(int a[], int la, int b[], int lb) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int tous_presents(int a[], int la, int b[], int lb) {
        int i = 0;
        for (int j = 0; j < lb; j += 1) {
            while (i < la && a[i] < b[j])
                i += 1;
            if (i == la || a[i] != b[j])
                return 0;
        }
        return 1;
    }
    ''',
    protos="int tous_presents(int a[], int la, int b[], int lb);",
    tests=r'''
    int s1[] = {1, 3, 5, 7, 9, 11}, s2[] = {3, 9}, s3[] = {3, 4}, s4[] = {11}, s5[] = {0}, s6[] = {1, 3, 5, 7, 9, 11};
    CHECK_INT(tous_presents(s1, 6, s2, 2), 1, "tous_presents({1,3,5,7,9,11}, {3,9})");
    CHECK_INT(tous_presents(s1, 6, s3, 2), 0, "tous_presents({1,3,5,7,9,11}, {3,4})");
    CHECK_INT(tous_presents(s1, 6, s4, 1), 1, "tous_presents({1,3,5,7,9,11}, {11})");
    CHECK_INT(tous_presents(s1, 6, s5, 1), 0, "tous_presents({1,3,5,7,9,11}, {0})");
    CHECK_INT(tous_presents(s1, 6, s6, 6), 1, "tous_presents(a, a)");
    CHECK_INT(tous_presents(s1, 6, s5, 0), 1, "tous_presents(a, b vide)");
    ''',
    indices=["Version simple : pour chaque b[j], une boucle sur a pour le chercher.",
             "Version maline (car triés) : un seul indice i dans a, qu'on avance tant que a[i] < b[j]."])

fonc("tab_parcours", "tableaux", "Suivre les indices", """
    Dans tableaux.c (pas de main), écris (exo du cours) :
      int parcours(int t[], int n)
          t[i] contient l'indice de la case suivante, -1 = fin. En partant de la case 0 :
          renvoie 0 si toutes les cases sont visitées, 1 s'il y a un cycle,
          2 si le parcours s'arrête sans tout visiter.
          {1, 2, -1} -> 0      {1, 0, 2} -> 1      {-1, 0, 1} -> 2
    """, 3, "tableaux.c",
    starter=r'''
    int parcours(int t[], int n) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int parcours(int t[], int n) {
        int vu[n];
        for (int i = 0; i < n; i += 1)
            vu[i] = 0;
        int i = 0;
        int c = 0;
        while (i != -1) {
            if (vu[i])
                return 1;
            vu[i] = 1;
            c += 1;
            i = t[i];
        }
        if (c == n)
            return 0;
        return 2;
    }
    ''',
    protos="int parcours(int t[], int n);",
    tests=r'''
    int p1[] = {1, 2, -1}, p2[] = {1, 0, 2}, p3[] = {-1, 0, 1}, p4[] = {2, -1, 1}, p5[] = {1, 2, 1}, p6[] = {-1};
    CHECK_INT(parcours(p1, 3), 0, "parcours({1,2,-1})");
    CHECK_INT(parcours(p2, 3), 1, "parcours({1,0,2})");
    CHECK_INT(parcours(p3, 3), 2, "parcours({-1,0,1})");
    CHECK_INT(parcours(p4, 3), 0, "parcours({2,-1,1})");
    CHECK_INT(parcours(p5, 3), 1, "parcours({1,2,1})");
    CHECK_INT(parcours(p6, 1), 0, "parcours({-1})");
    ''',
    indices=["Crée un tableau int vu[n] rempli de 0 pour marquer les cases visitées.",
             "Suis i = t[i] depuis 0 : case déjà vue -> cycle (1) ; -1 -> fin.",
             "À la fin : as-tu visité n cases ? -> 0, sinon 2."])

fonc("tab_tri", "tableaux", "Trier un tableau", """
    Dans tri.c (pas de main), écris (exo tri du cours) :
      void tri(int t[], int n)       trie t par ordre croissant (tri par sélection ou à bulles)
      int est_trie(int t[], int n)   1 si t est trié par ordre croissant, 0 sinon
    """, 3, "tri.c",
    starter=r'''
    void tri(int t[], int n) {
        // TODO
    }

    int est_trie(int t[], int n) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    void tri(int t[], int n) {
        for (int i = 0; i < n - 1; i += 1) {
            int m = i;
            for (int j = i + 1; j < n; j += 1)
                if (t[j] < t[m])
                    m = j;
            int tmp = t[i];
            t[i] = t[m];
            t[m] = tmp;
        }
    }

    int est_trie(int t[], int n) {
        for (int i = 1; i < n; i += 1)
            if (t[i - 1] > t[i])
                return 0;
        return 1;
    }
    ''',
    protos="void tri(int t[], int n);\nint est_trie(int t[], int n);",
    tests=r'''
    section("est_trie");
    int a[] = {1, 2, 2, 5}, b[] = {1, 3, 2}, c[] = {7};
    CHECK_INT(est_trie(a, 4), 1, "est_trie({1,2,2,5})");
    CHECK_INT(est_trie(b, 3), 0, "est_trie({1,3,2})");
    CHECK_INT(est_trie(c, 1), 1, "est_trie({7})");
    CHECK_INT(est_trie(c, 0), 1, "est_trie(tableau vide)");
    section("tri");
    int t[] = {5, -1, 8, 3, 3, 0, 12, -7};
    tri(t, 8);
    CHECK_TAB(t, 8, "tri({5,-1,8,3,3,0,12,-7})", {-7, -1, 0, 3, 3, 5, 8, 12});
    int u[] = {4, 3, 2, 1};
    tri(u, 4);
    CHECK_TAB(u, 4, "tri({4,3,2,1})", {1, 2, 3, 4});
    int v[] = {9, 1, 5};
    tri(v, 2);
    CHECK_TAB(v, 3, "tri({9,1,5}, 2) ne touche que les 2 premières cases", {1, 9, 5});
    ''',
    indices=["Tri par sélection : pour chaque i, cherche le minimum entre i et n - 1, puis échange-le avec t[i].",
             "Échanger t[i] et t[m] : int tmp = t[i]; t[i] = t[m]; t[m] = tmp;",
             "est_trie : dès que t[i-1] > t[i], ce n'est pas trié."])

fonc("tab_occurrences", "tableaux", "Chercher dans un tableau", """
    Dans recherche.c (pas de main), écris :
      int compte_occurrences(int t[], int n, int v)   combien de cases valent v
      int dernier_indice(int t[], int n, int v)       indice de la DERNIÈRE case valant v, -1 si absent
    """, 1, "recherche.c",
    starter=r'''
    int compte_occurrences(int t[], int n, int v) {
        // TODO
        return 0;
    }

    int dernier_indice(int t[], int n, int v) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int compte_occurrences(int t[], int n, int v) {
        int c = 0;
        for (int i = 0; i < n; i += 1)
            if (t[i] == v)
                c += 1;
        return c;
    }

    int dernier_indice(int t[], int n, int v) {
        for (int i = n - 1; i >= 0; i -= 1)
            if (t[i] == v)
                return i;
        return -1;
    }
    ''',
    protos="int compte_occurrences(int t[], int n, int v);\nint dernier_indice(int t[], int n, int v);",
    tests=r'''
    int t[] = {3, 7, 3, 1, 3, 9};
    section("compte_occurrences");
    CHECK_INT(compte_occurrences(t, 6, 3), 3, "compte_occurrences({3,7,3,1,3,9}, 3)");
    CHECK_INT(compte_occurrences(t, 6, 4), 0, "compte_occurrences(..., 4)");
    CHECK_INT(compte_occurrences(t, 2, 3), 1, "compte_occurrences(t, 2, 3)  (2 premières cases)");
    section("dernier_indice");
    CHECK_INT(dernier_indice(t, 6, 3), 4, "dernier_indice({3,7,3,1,3,9}, 3)");
    CHECK_INT(dernier_indice(t, 6, 9), 5, "dernier_indice(..., 9)");
    CHECK_INT(dernier_indice(t, 6, 8), -1, "dernier_indice(..., 8)");
    CHECK_INT(dernier_indice(t, 0, 3), -1, "dernier_indice(t, 0, 3)");
    ''',
    indices=["dernier_indice : parcours le tableau à l'envers (de n - 1 à 0) et renvoie le premier trouvé."])

qcm("tab_qcm_copie", "tableaux", "Copier un tableau", """
    int t[3] = {1, 2, 3};
    int u[3];
    Comment mettre dans u les valeurs de t ?
    """, 1,
    ["u = t;", "u[] = t[];", "for (int i = 0; i < 3; i += 1) u[i] = t[i];", "u = {1, 2, 3};"],
    "c",
    explication="On ne peut ni affecter ni copier un tableau d'un coup en C (slide « tableaux de pile ») : "
                "il faut copier case par case. Les accolades ne servent qu'à l'initialisation.")

qcm("tab_qcm_bornes", "tableaux", "Indices valides", """
    int b[3] = {0, 2, 4};
    Quelles affirmations sont vraies ?
    """, 2,
    ["b[0] vaut 0 et b[2] vaut 4", "b[3] vaut 4", "lire b[3] sort du tableau : comportement indéfini, "
     "le compilateur ne vérifie pas", "b[1] vaut 0"],
    "ac",
    explication="Indices de 0 à taille - 1. Le C ne contrôle pas les dépassements : b[3] lit la mémoire "
                "d'à côté (valeur au hasard, ou plantage).")

rep("tab_rep_sizeof", "tableaux", "Taille d'un tableau", """
    Qu'affiche ce code ?
    """, 2, ["40 10"],
    code=r'''
    int t[10];
    printf("%zu %zu\n", sizeof(t), sizeof(t) / sizeof(t[0]));
    ''', auto=True,
    explication="sizeof(t) = 10 cases × 4 octets = 40 ; divisé par la taille d'une case = nombre de cases. "
                "Attention : ça ne marche que là où t est déclaré, pas dans une fonction qui le reçoit.")


# ==========================================================================
# 6. Types, sizeof, binaire, ASCII
# ==========================================================================
rep("types_sizeof_tab", "types", "sizeof d'un tableau", """
    int t[4];
    Que vaut sizeof(t) (sur ta machine, un int fait 4 octets) ?
    """, 1, ["16"],
    code=r'''
    int t[4];
    printf("%zu\n", sizeof(t));
    ''', auto=True,
    explication="4 cases × 4 octets = 16 octets (slide sizeof).")

rep("types_ascii", "types", "Les caractères sont des nombres", """
    Qu'affiche ce code ?
    """, 1, ["99 Z"],
    code=r'''
    char x = 'a' + 2;
    printf("%d %c\n", x, 'A' + 25);
    ''', auto=True,
    indices=["'a' vaut 97 dans la table ASCII, 'A' vaut 65. man ascii dans un terminal."],
    explication="'a' + 2 = 99 (la lettre c) affiché avec %d ; 'A' + 25 = 90 = 'Z' affiché avec %c.")

rep("types_hexa", "types", "Hexadécimal", """
    Que vaut 0x32 en décimal ?
    """, 1, ["50"],
    code=r'''
    printf("%d\n", 0x32);
    ''', auto=True,
    explication="0x32 = 3 × 16 + 2 = 50.")

rep("types_binaire", "types", "Lire du binaire", """
    Que vaut, en décimal, l'octet non signé dont les bits sont   0100 1101 ?
    """, 1, ["77"],
    indices=["Le bit de droite vaut 1, puis 2, 4, 8, 16, 32, 64, 128."],
    explication="64 + 8 + 4 + 1 = 77 (exemple de la slide « les types »).")

rep("types_debordement", "types", "Débordement d'un char", """
    Qu'affiche ce code ? (char signé sur 8 bits : de -128 à 127)
    """, 3, ["-128"],
    code=r'''
    char c = 127;
    c = c + 1;
    printf("%d\n", c);
    ''', auto=True,
    explication="127 = 0111 1111. +1 donne 1000 0000, qui en complément à deux vaut -128 : "
                "on « déborde » et on revient au début de l'intervalle.")

rep("types_sizeof_chaine", "types", "Taille d'une chaîne constante", """
    Que vaut sizeof("abc") ?
    """, 2, ["4"],
    code=r'''
    printf("%zu\n", sizeof("abc"));
    ''', auto=True,
    explication="\"abc\" est un tableau de 4 char : 'a', 'b', 'c' et le 0 final ('\\0').")

rep("types_div_double", "types", "int / int dans un double", """
    Qu'affiche ce code ?
    """, 2, ["3.0"],
    code=r'''
    double d = 7 / 2;
    printf("%.1f\n", d);
    ''', auto=True,
    explication="7 / 2 est calculé entre deux int AVANT d'être rangé dans d : 3, puis converti en 3.0. "
                "Pour avoir 3.5 : 7.0 / 2 ou (double)7 / 2.")

rep("types_complement", "types", "Complément à deux", """
    Écris -5 sur 8 bits en complément à deux (8 chiffres 0/1).
    """, 3, ["11111011"],
    indices=["Écris +5 en binaire (0000 0101), inverse tous les bits, puis ajoute 1."],
    explication="+5 = 0000 0101 → inversé 1111 1010 → +1 = 1111 1011 (slide « les types »).")

fonc("types_bits", "types", "Manipuler les bits", """
    Dans bits.c (pas de main), écris (feuille 3, représentation) :
      int bit(unsigned char c, int i)         la valeur (0 ou 1) du bit d'indice i de c (bit 0 = 2^0)
      int nb_bits_a_un(unsigned char c)       combien de bits de c valent 1
      void binaire(unsigned char c, char out[9])
          écrit dans out les 8 bits de c, du bit 7 au bit 0, suivis de '\\0' : 77 -> "01001101"
    """, 3, "bits.c",
    starter=r'''
    int bit(unsigned char c, int i) {
        // TODO
        return 0;
    }

    int nb_bits_a_un(unsigned char c) {
        // TODO
        return 0;
    }

    void binaire(unsigned char c, char out[9]) {
        // TODO
    }
    ''',
    solution=r'''
    int bit(unsigned char c, int i) {
        for (int k = 0; k < i; k += 1)
            c = c / 2;
        return c % 2;
    }

    int nb_bits_a_un(unsigned char c) {
        int n = 0;
        for (int i = 0; i < 8; i += 1)
            n += bit(c, i);
        return n;
    }

    void binaire(unsigned char c, char out[9]) {
        for (int i = 0; i < 8; i += 1)
            out[i] = '0' + bit(c, 7 - i);
        out[8] = '\0';
    }
    ''',
    protos="int bit(unsigned char c, int i);\nint nb_bits_a_un(unsigned char c);\nvoid binaire(unsigned char c, char out[9]);",
    tests=r'''
    section("bit");
    CHECK_INT(bit(77, 0), 1, "bit(77, 0)");
    CHECK_INT(bit(77, 1), 0, "bit(77, 1)");
    CHECK_INT(bit(77, 6), 1, "bit(77, 6)");
    CHECK_INT(bit(77, 7), 0, "bit(77, 7)");
    CHECK_INT(bit(255, 7), 1, "bit(255, 7)");
    section("nb_bits_a_un");
    CHECK_INT(nb_bits_a_un(77), 4, "nb_bits_a_un(77)");
    CHECK_INT(nb_bits_a_un(0), 0, "nb_bits_a_un(0)");
    CHECK_INT(nb_bits_a_un(255), 8, "nb_bits_a_un(255)");
    section("binaire");
    char out[9] = "XXXXXXXX";
    binaire(77, out);
    CHECK_STR(out, "01001101", "binaire(77)");
    binaire(5, out);
    CHECK_STR(out, "00000101", "binaire(5)");
    binaire(251, out);
    CHECK_STR(out, "11111011", "binaire(251)  (= -5 en complément à deux)");
    ''',
    indices=["Diviser par 2 décale les bits vers la droite : le bit i de c est le dernier bit de c / 2^i, "
             "c'est-à-dire (c / 2^i) % 2.",
             "Avec les opérateurs de bits : (c >> i) & 1.",
             "binaire : le caractère '0' + b vaut '0' ou '1' ; n'oublie pas out[8] = '\\0'."])

qcm("types_qcm_tailles", "types", "Tailles des types", """
    Sur ta machine (Linux 64 bits), quelles affirmations sont vraies ?
    """, 2,
    ["sizeof(char) vaut 1", "sizeof(int) vaut 4", "sizeof(double) vaut 4", "sizeof(int *) vaut 8"],
    "abd",
    explication="char 1, int 4 (au moins 2 d'après la norme), float 4, double 8, et tous les pointeurs "
                "8 octets (adresses 64 bits).")


# ==========================================================================
# 7. Chaînes de caractères
# ==========================================================================
fonc("ch_len_cpy", "chaines", "strlen et strcpy à la main", """
    Dans chaines.c (pas de main), écris SANS #include <string.h> :
      int ma_strlen(char *s)                 longueur de s (sans le '\\0')
      void ma_strcpy(char *dst, char *src)   copie src dans dst, '\\0' compris
    """, 1, "chaines.c",
    starter=r'''
    // pas de #include <string.h> ici !

    int ma_strlen(char *s) {
        // TODO
        return 0;
    }

    void ma_strcpy(char *dst, char *src) {
        // TODO
    }
    ''',
    solution=r'''
    int ma_strlen(char *s) {
        int i = 0;
        while (s[i] != '\0')
            i += 1;
        return i;
    }

    void ma_strcpy(char *dst, char *src) {
        int i = 0;
        while (src[i] != '\0') {
            dst[i] = src[i];
            i += 1;
        }
        dst[i] = '\0';
    }
    ''',
    protos="int ma_strlen(char *s);\nvoid ma_strcpy(char *dst, char *src);",
    tests=r'''
    section("ma_strlen");
    CHECK_INT(ma_strlen("hello"), 5, "ma_strlen(\"hello\")");
    CHECK_INT(ma_strlen(""), 0, "ma_strlen(\"\")");
    CHECK_INT(ma_strlen("a b c"), 5, "ma_strlen(\"a b c\")");
    section("ma_strcpy");
    char dst[32];
    memset(dst, 'X', sizeof dst);
    dst[31] = '\0';
    ma_strcpy(dst, "bonjour");
    CHECK_STR(dst, "bonjour", "ma_strcpy(dst, \"bonjour\")  (le '\\0' est-il copié ?)");
    memset(dst, 'X', sizeof dst);
    ma_strcpy(dst, "");
    CHECK_INT(dst[0], 0, "ma_strcpy(dst, \"\") : dst[0] doit valoir '\\0'");
    ''',
    forbid=["string.h"],
    indices=["Une chaîne finit par '\\0' : avance tant que s[i] != '\\0'.",
             "ma_strcpy : après la boucle, il faut encore écrire le '\\0' final dans dst."])

fonc("ch_compte_maj", "chaines", "Compter et mettre en majuscules", """
    Dans chaines.c (pas de main), écris SANS #include <string.h> ni <ctype.h> :
      int compte_char(char *s, char c)    nombre d'apparitions de c dans s
      void majuscules(char *s)            met les minuscules a-z de s en majuscules (dans s)
    """, 2, "chaines.c",
    starter=r'''
    int compte_char(char *s, char c) {
        // TODO
        return 0;
    }

    void majuscules(char *s) {
        // TODO
    }
    ''',
    solution=r'''
    int compte_char(char *s, char c) {
        int n = 0;
        for (int i = 0; s[i] != '\0'; i += 1)
            if (s[i] == c)
                n += 1;
        return n;
    }

    void majuscules(char *s) {
        for (int i = 0; s[i] != '\0'; i += 1)
            if (s[i] >= 'a' && s[i] <= 'z')
                s[i] = s[i] - 'a' + 'A';
    }
    ''',
    protos="int compte_char(char *s, char c);\nvoid majuscules(char *s);",
    tests=r'''
    section("compte_char");
    CHECK_INT(compte_char("abracadabra", 'a'), 5, "compte_char(\"abracadabra\", 'a')");
    CHECK_INT(compte_char("abracadabra", 'z'), 0, "compte_char(\"abracadabra\", 'z')");
    CHECK_INT(compte_char("", 'a'), 0, "compte_char(\"\", 'a')");
    section("majuscules");
    char m1[] = "hello World 42 !";
    majuscules(m1);
    CHECK_STR(m1, "HELLO WORLD 42 !", "majuscules(\"hello World 42 !\")");
    char m2[] = "{az}`";
    majuscules(m2);
    CHECK_STR(m2, "{AZ}`", "majuscules(\"{az}`\")  (seulement les lettres a-z)");
    ''',
    forbid=["string.h", "ctype.h"],
    indices=["Un char est un nombre : on peut écrire s[i] >= 'a' && s[i] <= 'z'.",
             "'a' - 'A' vaut 32 : s[i] = s[i] - 'a' + 'A';"])

fonc("ch_strcmp", "chaines", "Comparer deux chaînes", """
    Dans chaines.c (pas de main), écris SANS #include <string.h> :
      int ma_strcmp(char *a, char *b)
          0 si a et b sont égales, un nombre < 0 si a est avant b (ordre ASCII), > 0 si a est après
    """, 2, "chaines.c",
    starter=r'''
    int ma_strcmp(char *a, char *b) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int ma_strcmp(char *a, char *b) {
        int i = 0;
        while (a[i] != '\0' && a[i] == b[i])
            i += 1;
        return a[i] - b[i];
    }
    ''',
    protos="int ma_strcmp(char *a, char *b);\nstatic int sign(int x) { return (x > 0) - (x < 0); }",
    tests=r'''
    CHECK_INT(ma_strcmp("abc", "abc"), 0, "ma_strcmp(\"abc\", \"abc\")");
    CHECK_INT(sign(ma_strcmp("abc", "abd")), -1, "ma_strcmp(\"abc\", \"abd\") est négatif");
    CHECK_INT(sign(ma_strcmp("b", "abc")), 1, "ma_strcmp(\"b\", \"abc\") est positif");
    CHECK_INT(sign(ma_strcmp("ab", "abc")), -1, "ma_strcmp(\"ab\", \"abc\") est négatif");
    CHECK_INT(sign(ma_strcmp("abc", "ab")), 1, "ma_strcmp(\"abc\", \"ab\") est positif");
    CHECK_INT(ma_strcmp("", ""), 0, "ma_strcmp(\"\", \"\")");
    CHECK_INT(sign(ma_strcmp("Zoo", "abc")), -1, "ma_strcmp(\"Zoo\", \"abc\") est négatif ('Z' = 90 < 'a' = 97)");
    ''',
    forbid=["string.h"],
    indices=["Avance tant que les deux caractères sont égaux et qu'on n'est pas au bout.",
             "Puis renvoie la différence a[i] - b[i] : 0 si les deux sont au '\\0'."])

fonc("ch_palindrome", "chaines", "Palindromes et inversion", """
    Dans mots.c (pas de main), écris (tu peux utiliser strlen de <string.h>) :
      int est_palindrome(char *s)     1 si s se lit pareil dans les deux sens ("kayak", "", "a"), 0 sinon
      void inverse_chaine(char *s)    renverse s sur place : "abcd" -> "dcba"
    """, 2, "mots.c",
    starter=r'''
    #include <string.h>

    int est_palindrome(char *s) {
        // TODO
        return 0;
    }

    void inverse_chaine(char *s) {
        // TODO
    }
    ''',
    solution=r'''
    #include <string.h>

    int est_palindrome(char *s) {
        int i = 0;
        int j = strlen(s) - 1;
        while (i < j) {
            if (s[i] != s[j])
                return 0;
            i += 1;
            j -= 1;
        }
        return 1;
    }

    void inverse_chaine(char *s) {
        int i = 0;
        int j = strlen(s) - 1;
        while (i < j) {
            char tmp = s[i];
            s[i] = s[j];
            s[j] = tmp;
            i += 1;
            j -= 1;
        }
    }
    ''',
    protos="int est_palindrome(char *s);\nvoid inverse_chaine(char *s);",
    tests=r'''
    section("est_palindrome");
    CHECK_INT(est_palindrome("kayak"), 1, "est_palindrome(\"kayak\")");
    CHECK_INT(est_palindrome("abba"), 1, "est_palindrome(\"abba\")");
    CHECK_INT(est_palindrome("abca"), 0, "est_palindrome(\"abca\")");
    CHECK_INT(est_palindrome("a"), 1, "est_palindrome(\"a\")");
    CHECK_INT(est_palindrome(""), 1, "est_palindrome(\"\")");
    section("inverse_chaine");
    char s1[] = "abcd";
    inverse_chaine(s1);
    CHECK_STR(s1, "dcba", "inverse_chaine(\"abcd\")");
    char s2[] = "hello";
    inverse_chaine(s2);
    CHECK_STR(s2, "olleh", "inverse_chaine(\"hello\")");
    char s3[] = "";
    inverse_chaine(s3);
    CHECK_STR(s3, "", "inverse_chaine(\"\")");
    ''',
    indices=["Deux indices : i part du début, j de la fin (strlen(s) - 1), et ils se rapprochent.",
             "Attention : pour \"\", strlen - 1 vaut -1 ; la boucle while (i < j) ne tourne pas, tant mieux."])

fonc("ch_mots", "chaines", "Compter les mots", """
    Dans mots.c (pas de main), écris :
      int compte_mots(char *s)
          nombre de mots de s ; les mots sont séparés par un ou plusieurs espaces
          "le chat dort" -> 3     "  deux   mots " -> 2     "" -> 0
    """, 3, "mots.c",
    starter=r'''
    int compte_mots(char *s) {
        // TODO
        return 0;
    }
    ''',
    solution=r'''
    int compte_mots(char *s) {
        int n = 0;
        for (int i = 0; s[i] != '\0'; i += 1)
            if (s[i] != ' ' && (i == 0 || s[i - 1] == ' '))
                n += 1;
        return n;
    }
    ''',
    protos="int compte_mots(char *s);",
    tests=r'''
    CHECK_INT(compte_mots("le chat dort"), 3, "compte_mots(\"le chat dort\")");
    CHECK_INT(compte_mots("  deux   mots "), 2, "compte_mots(\"  deux   mots \")");
    CHECK_INT(compte_mots(""), 0, "compte_mots(\"\")");
    CHECK_INT(compte_mots("     "), 0, "compte_mots(\"     \")");
    CHECK_INT(compte_mots("seul"), 1, "compte_mots(\"seul\")");
    ''',
    indices=["Un mot commence là où on a un caractère non-espace précédé d'un espace (ou du début).",
             "Compte ces débuts de mots : s[i] != ' ' && (i == 0 || s[i-1] == ' ')."])

qcm("ch_qcm_hello", "chaines", "Place pour le '\\0'", """
    Quel est le problème de cette ligne ?
        char s[5] = "hello";
    """, 2,
    ["aucun", "\"hello\" a besoin de 6 cases : il n'y a pas de place pour le '\\0' final",
     "il faut écrire char s = \"hello\";", "il faut des apostrophes : 'hello'"],
    "b",
    explication="\"hello\" = 'h','e','l','l','o',0 : 6 char. Sans le 0 final, printf(\"%s\") ou strlen "
                "continuent à lire au-delà du tableau. Écris char s[6] ou, plus simple, char s[] = \"hello\".")

qcm("ch_qcm_egal", "chaines", "Comparer des chaînes", """
    char a[] = "chat";
    char b[] = "chat";
    Que fait le test  if (a == b) ?
    """, 2,
    ["il compare les lettres : vrai", "il compare les ADRESSES des deux tableaux : faux",
     "il ne compile pas", "il copie b dans a"],
    "b",
    explication="Un tableau utilisé dans une expression devient l'adresse de sa première case : a == b "
                "compare deux adresses différentes. Pour comparer le contenu : strcmp(a, b) == 0.")

rep("ch_rep_strlen", "chaines", "strlen ou sizeof ?", """
    Qu'affiche ce code ?
    """, 2, ["3 20"],
    code=r'''
    char s[20] = "abc";
    printf("%zu %zu\n", strlen(s), sizeof(s));
    ''', auto=True,
    explication="strlen compte les caractères avant le '\\0' (3) ; sizeof donne la place réservée "
                "pour le tableau (20 octets).")

from missions2 import ajouter  # noqa: E402

ajouter(prog, fonc, qcm, rep)
