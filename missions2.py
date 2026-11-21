"""Missions de CQuest, thèmes 8 à 15 (enum → pièges)."""
import textwrap

D = textwrap.dedent

JOURS_H = r'''
#ifndef JOURS_H
#define JOURS_H

enum jour { LUNDI, MARDI, MERCREDI, JEUDI, VENDREDI, SAMEDI, DIMANCHE };

#endif
'''

POINT_H = r'''
#ifndef POINT_H
#define POINT_H

struct point {
    int x;
    int y;
};

#endif
'''

LISTE_H = r'''
#ifndef LISTE_H
#define LISTE_H

#include <stdlib.h>

struct cell {
    int value;
    struct cell *next;
};

#endif
'''

RESEAU_H = r'''
#ifndef RESEAU_H
#define RESEAU_H

#include <stdlib.h>

#define MAX_OUT 3
#define MAX_NODES 10

enum netkind { ROUTER, SWITCH, HOST, SERVER };

struct NetNode {
    int id;
    char *name;                     // on garde le pointeur reçu (pas de copie)
    enum netkind kind;
    struct NetNode *out[MAX_OUT];   // connexions sortantes, NULL = case libre
};

struct Network {
    struct NetNode *nodes[MAX_NODES];
    int count;                      // nombre de cases occupées dans nodes
    struct NetNode *start;          // point d'entrée du réseau (NULL au début)
};

#endif
'''

RESEAU_BASE = r'''
const char *netkind_str(enum netkind k) {
    switch (k) {
    case ROUTER: return "ROUTER";
    case SWITCH: return "SWITCH";
    case HOST: return "HOST";
    case SERVER: return "SERVER";
    }
    return "?";
}

struct NetNode *node_create(int id, char *name, enum netkind kind) {
    struct NetNode *n = malloc(sizeof(struct NetNode));
    n->id = id;
    n->name = name;
    n->kind = kind;
    for (int i = 0; i < MAX_OUT; i += 1)
        n->out[i] = NULL;
    return n;
}

int node_connect(struct NetNode *a, struct NetNode *b) {
    for (int i = 0; i < MAX_OUT; i += 1) {
        if (a->out[i] == NULL) {
            a->out[i] = b;
            return 1;
        }
    }
    return 0;
}

struct Network *net_create(void) {
    struct Network *net = malloc(sizeof(struct Network));
    net->count = 0;
    net->start = NULL;
    for (int i = 0; i < MAX_NODES; i += 1)
        net->nodes[i] = NULL;
    return net;
}

int net_add(struct Network *net, struct NetNode *n, int is_start) {
    if (net->count == MAX_NODES)
        return 0;
    net->nodes[net->count] = n;
    net->count += 1;
    if (is_start)
        net->start = n;
    return 1;
}
'''


def ajouter(prog, fonc, qcm, rep):
    # ======================================================================
    # 8. enum
    # ======================================================================
    fonc("enum_jours", "enum", "Les jours de la semaine", """
        jours.h définit :  enum jour { LUNDI, MARDI, MERCREDI, JEUDI, VENDREDI, SAMEDI, DIMANCHE };
        Dans jours.c (pas de main), écris :
          const char *jour_str(enum jour j)        "lundi", ..., "dimanche" ; "inconnu" sinon
          int est_weekend(enum jour j)             1 pour SAMEDI et DIMANCHE
          enum jour lendemain(enum jour j)         DIMANCHE -> LUNDI
          enum jour jour_apres(enum jour j, int n) n jours plus tard (n >= 0, peut être grand)
        """, 2, "jours.c",
        starter=r'''
        #include "jours.h"

        const char *jour_str(enum jour j) {
            // TODO
            return "inconnu";
        }

        int est_weekend(enum jour j) {
            // TODO
            return 0;
        }

        enum jour lendemain(enum jour j) {
            // TODO
            return LUNDI;
        }

        enum jour jour_apres(enum jour j, int n) {
            // TODO
            return LUNDI;
        }
        ''',
        solution=r'''
        #include "jours.h"

        const char *jour_str(enum jour j) {
            switch (j) {
            case LUNDI: return "lundi";
            case MARDI: return "mardi";
            case MERCREDI: return "mercredi";
            case JEUDI: return "jeudi";
            case VENDREDI: return "vendredi";
            case SAMEDI: return "samedi";
            case DIMANCHE: return "dimanche";
            default: return "inconnu";
            }
        }

        int est_weekend(enum jour j) {
            return j == SAMEDI || j == DIMANCHE;
        }

        enum jour lendemain(enum jour j) {
            return (j + 1) % 7;
        }

        enum jour jour_apres(enum jour j, int n) {
            return (j + n) % 7;
        }
        ''',
        headers={"jours.h": JOURS_H},
        protos="const char *jour_str(enum jour j);\nint est_weekend(enum jour j);\n"
               "enum jour lendemain(enum jour j);\nenum jour jour_apres(enum jour j, int n);",
        tests=r'''
        section("jour_str");
        CHECK_STR(jour_str(LUNDI), "lundi", "jour_str(LUNDI)");
        CHECK_STR(jour_str(MERCREDI), "mercredi", "jour_str(MERCREDI)");
        CHECK_STR(jour_str(DIMANCHE), "dimanche", "jour_str(DIMANCHE)");
        CHECK_STR(jour_str((enum jour)12), "inconnu", "jour_str(12)");
        section("est_weekend");
        CHECK_INT(est_weekend(SAMEDI), 1, "est_weekend(SAMEDI)");
        CHECK_INT(est_weekend(DIMANCHE), 1, "est_weekend(DIMANCHE)");
        CHECK_INT(est_weekend(VENDREDI), 0, "est_weekend(VENDREDI)");
        section("lendemain");
        CHECK_INT(lendemain(LUNDI), MARDI, "lendemain(LUNDI) == MARDI");
        CHECK_INT(lendemain(DIMANCHE), LUNDI, "lendemain(DIMANCHE) == LUNDI");
        section("jour_apres");
        CHECK_INT(jour_apres(VENDREDI, 3), LUNDI, "jour_apres(VENDREDI, 3) == LUNDI");
        CHECK_INT(jour_apres(MARDI, 14), MARDI, "jour_apres(MARDI, 14) == MARDI");
        CHECK_INT(jour_apres(JEUDI, 100), SAMEDI, "jour_apres(JEUDI, 100) == SAMEDI");
        ''',
        indices=["Un enum, ce sont des entiers nommés : LUNDI = 0, ..., DIMANCHE = 6.",
                 "jour_str : switch (j) { case LUNDI: return \"lundi\"; ... default: return \"inconnu\"; }",
                 "lendemain : (j + 1) % 7. jour_apres : même idée, sans boucle."])

    fonc("enum_feu", "enum", "Feu tricolore", """
        Dans feu.c, définis (au début du fichier) l'enum :
            enum feu { VERT, ORANGE, ROUGE };
        puis écris :
          enum feu feu_suivant(enum feu f)      VERT -> ORANGE -> ROUGE -> VERT
          const char *feu_str(enum feu f)       "vert", "orange", "rouge"
          int peut_passer(enum feu f)           1 seulement pour VERT
        """, 1, "feu.c",
        starter=r'''
        // TODO : définir enum feu ici

        // TODO : feu_suivant, feu_str, peut_passer
        ''',
        solution=r'''
        enum feu { VERT, ORANGE, ROUGE };

        enum feu feu_suivant(enum feu f) {
            if (f == VERT)
                return ORANGE;
            if (f == ORANGE)
                return ROUGE;
            return VERT;
        }

        const char *feu_str(enum feu f) {
            if (f == VERT)
                return "vert";
            if (f == ORANGE)
                return "orange";
            return "rouge";
        }

        int peut_passer(enum feu f) {
            return f == VERT;
        }
        ''',
        protos="enum feu { VERT, ORANGE, ROUGE };\nenum feu feu_suivant(enum feu f);\n"
               "const char *feu_str(enum feu f);\nint peut_passer(enum feu f);",
        tests=r'''
        CHECK_INT(feu_suivant(VERT), ORANGE, "feu_suivant(VERT) == ORANGE");
        CHECK_INT(feu_suivant(ORANGE), ROUGE, "feu_suivant(ORANGE) == ROUGE");
        CHECK_INT(feu_suivant(ROUGE), VERT, "feu_suivant(ROUGE) == VERT");
        CHECK_STR(feu_str(VERT), "vert", "feu_str(VERT)");
        CHECK_STR(feu_str(ROUGE), "rouge", "feu_str(ROUGE)");
        CHECK_STR(feu_str(ORANGE), "orange", "feu_str(ORANGE)");
        CHECK_INT(peut_passer(VERT), 1, "peut_passer(VERT)");
        CHECK_INT(peut_passer(ORANGE), 0, "peut_passer(ORANGE)");
        ''',
        indices=["Syntaxe (slide enum) : enum feu { VERT, ORANGE, ROUGE };  (avec le ; final)",
                 "Les valeurs sont dans l'ordre : VERT = 0, ORANGE = 1, ROUGE = 2. "
                 "feu_suivant peut donc aussi s'écrire (f + 1) % 3."])

    rep("enum_rep_valeur", "enum", "Valeur d'un enum", """
        Qu'affiche ce code (tiré du cours) ?
        """, 1, ["2"],
        code=r'''
        #include <stdio.h>

        enum couleur { TREFLE, CARREAU, COEUR, PIQUE };

        int main(void) {
            enum couleur carte = COEUR;
            int i = carte;
            printf("%d\n", i);
            return 0;
        }
        ''', auto=True,
        explication="Numérotation automatique à partir de 0 : TREFLE 0, CARREAU 1, COEUR 2, PIQUE 3.")

    rep("enum_rep_saut", "enum", "Enum avec valeurs imposées", """
        Qu'affiche ce code ?
        """, 2, ["0 5 6"],
        code=r'''
        #include <stdio.h>

        enum niveau { DEBUT, MILIEU = 5, FIN };

        int main(void) {
            printf("%d %d %d\n", DEBUT, MILIEU, FIN);
            return 0;
        }
        ''', auto=True,
        explication="On peut imposer une valeur ; les suivantes continuent à +1 : FIN = 6.")

    qcm("enum_qcm_interet", "enum", "À quoi sert un enum ?", """
        Pourquoi écrire  enum couleur { TREFLE, CARREAU, COEUR, PIQUE };
        plutôt que d'utiliser directement 0, 1, 2, 3 dans le code ?
        """, 1,
        ["c'est plus rapide à l'exécution", "le code est plus lisible : COEUR dit ce que 2 veut dire",
         "un enum prend moins de mémoire qu'un int", "c'est obligatoire pour faire un switch"],
        "b",
        explication="Un enum ne change rien pour la machine (ce sont des int) : il donne des noms aux "
                    "constantes. Même idée que les #define (« pas de constante en dur dans le code »).")

    # ======================================================================
    # 9. Pointeurs
    # ======================================================================
    fonc("ptr_echange", "pointeurs", "Passage par adresse", """
        Dans pointeurs.c (pas de main), écris :
          void echange(int *a, int *b)                  échange les valeurs pointées
          void division(int a, int b, int *q, int *r)   *q = quotient, *r = reste (b != 0)
          void incremente(int *p, int n)                ajoute n à l'entier pointé
        """, 1, "pointeurs.c",
        starter=r'''
        void echange(int *a, int *b) {
            // TODO
        }

        void division(int a, int b, int *q, int *r) {
            // TODO
        }

        void incremente(int *p, int n) {
            // TODO
        }
        ''',
        solution=r'''
        void echange(int *a, int *b) {
            int tmp = *a;
            *a = *b;
            *b = tmp;
        }

        void division(int a, int b, int *q, int *r) {
            *q = a / b;
            *r = a % b;
        }

        void incremente(int *p, int n) {
            *p = *p + n;
        }
        ''',
        protos="void echange(int *a, int *b);\nvoid division(int a, int b, int *q, int *r);\n"
               "void incremente(int *p, int n);",
        tests=r'''
        section("echange");
        int x = 1, y = 2;
        echange(&x, &y);
        CHECK_TRUE(x == 2 && y == 1, "x=1, y=2 ; echange(&x, &y) -> x=2, y=1");
        int z = 7;
        echange(&z, &z);
        CHECK_INT(z, 7, "echange(&z, &z) ne change pas z");
        section("division");
        int q = -99, r = -99;
        division(17, 5, &q, &r);
        CHECK_TRUE(q == 3 && r == 2, "division(17, 5, &q, &r) -> q=3, r=2");
        division(4, 8, &q, &r);
        CHECK_TRUE(q == 0 && r == 4, "division(4, 8, &q, &r) -> q=0, r=4");
        section("incremente");
        int v = 10;
        incremente(&v, 5);
        CHECK_INT(v, 15, "v=10 ; incremente(&v, 5)");
        incremente(&v, -20);
        CHECK_INT(v, -5, "puis incremente(&v, -20)");
        ''',
        indices=["Pour modifier une variable de l'appelant, on reçoit son adresse (int *a) et on écrit dans *a.",
                 "echange : il faut une variable temporaire.  int tmp = *a; *a = *b; *b = tmp;"])

    fonc("ptr_min_max", "pointeurs", "Renvoyer plusieurs résultats", """
        Dans pointeurs.c (pas de main), écris :
          void min_max(int t[], int n, int *min, int *max)
              range la plus petite et la plus grande valeur de t dans *min et *max (n >= 1)
          int *plus_petit(int *t, int n)
              (exo du cours) POINTEUR vers la plus petite case (la première si égalité), NULL si n == 0
        """, 2, "pointeurs.c",
        starter=r'''
        #include <stdlib.h>

        void min_max(int t[], int n, int *min, int *max) {
            // TODO
        }

        int *plus_petit(int *t, int n) {
            // TODO
            return NULL;
        }
        ''',
        solution=r'''
        #include <stdlib.h>

        void min_max(int t[], int n, int *min, int *max) {
            *min = t[0];
            *max = t[0];
            for (int i = 1; i < n; i += 1) {
                if (t[i] < *min)
                    *min = t[i];
                if (t[i] > *max)
                    *max = t[i];
            }
        }

        int *plus_petit(int *t, int n) {
            if (n == 0)
                return NULL;
            int *m = t;
            for (int i = 1; i < n; i += 1)
                if (t[i] < *m)
                    m = t + i;
            return m;
        }
        ''',
        protos="void min_max(int t[], int n, int *min, int *max);\nint *plus_petit(int *t, int n);",
        tests=r'''
        int t[] = {5, -3, 12, 0, 12, -3, 8};
        int mn = 999, mx = -999;
        section("min_max");
        min_max(t, 7, &mn, &mx);
        CHECK_TRUE(mn == -3 && mx == 12, "min_max({5,-3,12,0,12,-3,8}) -> min=-3, max=12");
        int w[] = {-5, -9, -2};
        min_max(w, 3, &mn, &mx);
        CHECK_TRUE(mn == -9 && mx == -2, "min_max({-5,-9,-2}) -> min=-9, max=-2  (que des négatifs)");
        section("plus_petit");
        CHECK_TRUE(plus_petit(t, 7) == &t[1], "plus_petit({5,-3,12,0,12,-3,8}, 7) == &t[1]");
        CHECK_TRUE(plus_petit(t, 1) == &t[0], "plus_petit(t, 1) == &t[0]");
        CHECK_TRUE(plus_petit(t, 0) == NULL, "plus_petit(t, 0) == NULL");
        CHECK_TRUE(plus_petit(t + 2, 2) == &t[3], "plus_petit(t + 2, 2) == &t[3]  (sous-tableau {12, 0})");
        ''',
        indices=["min_max : initialise *min et *max avec t[0] (pas avec 0 : et si tout est négatif ?).",
                 "plus_petit : garde un pointeur m vers le meilleur ; à la fin return m; (t + i == &t[i])."])

    fonc("ptr_bugs", "pointeurs", "Chasse aux bugs : pointeurs", """
        bugs.c compile sans erreur mais contient 5 BUGS, un par fonction. Lance :verifier, regarde
        quels tests échouent, comprends pourquoi et corrige. Chaque bug se corrige en changeant
        très peu de caractères.
          longueur(s)              longueur d'une chaîne (parcours avec un pointeur)
          compte_inf_egal(t, v)    nombre d'éléments <= v dans t (t se termine par -1)
          trouve(t, n, v)          pointeur vers la première case qui vaut v, NULL si absent
          cherche_motif(texte, m)  adresse de la première occurrence de m dans texte, NULL si absent
          inverse(t, n)            renverse le tableau sur place
        """, 3, "bugs.c",
        starter=r'''
        #include <stdlib.h>

        /* longueur de la chaine s (sans le '\0') */
        int longueur(char *s) {
            char *p = s;
            while (*p != '\0')
                p += 1;
            return p - s + 1;
        }

        /* nombre d'elements de t inferieurs OU EGAUX a v ; t se termine par -1 */
        int compte_inf_egal(int *t, int v) {
            int c = 0;
            for (int *i = t; *i != -1; i += 1)
                if (*i < v)
                    c += 1;
            return c;
        }

        /* pointeur vers la premiere case de t (taille n) qui vaut v, NULL si absent */
        int *trouve(int *t, int n, int v) {
            for (int i = 0; i <= n; i += 1)
                if (t[i] == v)
                    return t + i;
            return NULL;
        }

        /* adresse de la premiere occurrence de motif dans texte, NULL si absent */
        char *cherche_motif(char *texte, char *motif) {
            for (char *p = texte; *p != '\0'; p += 1) {
                char *a = p;
                char *b = motif;
                while (*a != '\0' && *a == *b) {
                    a += 1;
                    b += 1;
                }
                if (*b == '\0')
                    return texte;
            }
            return NULL;
        }

        /* renverse le tableau t de taille n sur place */
        void inverse(int *t, int n) {
            int *debut = t;
            int *fin = t + n;
            while (debut < fin) {
                int tmp = *debut;
                *debut = *fin;
                *fin = tmp;
                debut += 1;
                fin -= 1;
            }
        }
        ''',
        solution=r'''
        #include <stdlib.h>

        int longueur(char *s) {
            char *p = s;
            while (*p != '\0')
                p += 1;
            return p - s;                       // pas de + 1
        }

        int compte_inf_egal(int *t, int v) {
            int c = 0;
            for (int *i = t; *i != -1; i += 1)
                if (*i <= v)                    // <= et pas <
                    c += 1;
            return c;
        }

        int *trouve(int *t, int n, int v) {
            for (int i = 0; i < n; i += 1)      // < n : t[n] n'existe pas
                if (t[i] == v)
                    return t + i;
            return NULL;
        }

        char *cherche_motif(char *texte, char *motif) {
            for (char *p = texte; *p != '\0'; p += 1) {
                char *a = p;
                char *b = motif;
                while (*a != '\0' && *a == *b) {
                    a += 1;
                    b += 1;
                }
                if (*b == '\0')
                    return p;                   // la position trouvée, pas le début
            }
            return NULL;
        }

        void inverse(int *t, int n) {
            int *debut = t;
            int *fin = t + n - 1;               // la dernière case est t[n - 1]
            while (debut < fin) {
                int tmp = *debut;
                *debut = *fin;
                *fin = tmp;
                debut += 1;
                fin -= 1;
            }
        }
        ''',
        protos="int longueur(char *s);\nint compte_inf_egal(int *t, int v);\nint *trouve(int *t, int n, int v);\n"
               "char *cherche_motif(char *texte, char *motif);\nvoid inverse(int *t, int n);\n"
               "struct piege { int t[4]; int apres[4]; };",
        tests=r'''
        section("longueur");
        CHECK_INT(longueur("hello"), 5, "longueur(\"hello\")");
        CHECK_INT(longueur(""), 0, "longueur(\"\")");
        section("compte_inf_egal");
        int t[] = {3, 8, 1, 5, 8, -1};
        CHECK_INT(compte_inf_egal(t, 5), 3, "compte_inf_egal({3,8,1,5,8,-1}, 5)");
        CHECK_INT(compte_inf_egal(t, 8), 5, "compte_inf_egal({3,8,1,5,8,-1}, 8)");
        CHECK_INT(compte_inf_egal(t, 0), 0, "compte_inf_egal({3,8,1,5,8,-1}, 0)");
        section("trouve");
        struct piege p = { {4, 7, 9, 7}, {42, 42, 42, 42} };
        CHECK_TRUE(trouve(p.t, 4, 7) == &p.t[1], "trouve({4,7,9,7}, 4, 7) == &t[1]");
        CHECK_TRUE(trouve(p.t, 4, 4) == &p.t[0], "trouve({4,7,9,7}, 4, 4) == &t[0]");
        CHECK_TRUE(trouve(p.t, 4, 42) == NULL, "trouve({4,7,9,7}, 4, 42) == NULL  (sans lire t[4] !)");
        section("cherche_motif");
        char texte[] = "un chat et un chien";
        CHECK_TRUE(cherche_motif(texte, "ch") == texte + 3, "cherche_motif(\"un chat et un chien\", \"ch\") == texte + 3");
        CHECK_TRUE(cherche_motif(texte, "chien") == texte + 14, "cherche_motif(..., \"chien\") == texte + 14");
        CHECK_TRUE(cherche_motif(texte, "un") == texte, "cherche_motif(..., \"un\") == texte");
        CHECK_TRUE(cherche_motif(texte, "chiot") == NULL, "cherche_motif(..., \"chiot\") == NULL");
        section("inverse");
        struct piege q = { {1, 2, 3, 4}, {99, 99, 99, 99} };
        inverse(q.t, 4);
        CHECK_TAB(q.t, 4, "inverse({1,2,3,4})", {4, 3, 2, 1});
        CHECK_TRUE(q.apres[0] == 99, "inverse n'écrit pas après la fin du tableau");
        int r[] = {5, 6, 7};
        inverse(r, 3);
        CHECK_TAB(r, 3, "inverse({5,6,7})", {7, 6, 5});
        ''',
        bug=True,
        indices=["Prends UN test qui échoue et refais le calcul sur papier en suivant le code ligne à ligne.",
                 "Les bugs classiques : un + 1 de trop, < au lieu de <=, <= au lieu de <, renvoyer le début "
                 "au lieu de la position trouvée, t + n au lieu de t + n - 1.",
                 "gdb aide aussi : gcc -g -Wall -std=c99 essai.c bugs.c -o essai && gdb ./essai "
                 "(break longueur, run, next, print p - s)."])

    fonc("ptr_multiples", "pointeurs", "Multiples de cibles", """
        Dans cibles.c (pas de main), écris (exo feuille 4 du cours) :
          int nb_multiples_cibles(int *values, int nv, int *targets, int nt)
              nombre d'éléments de values qui sont multiples d'AU MOINS un élément de targets
              ({4,5,7,9}, {2,3}) -> 2   (4 est multiple de 2, 9 de 3)
        Parcours les tableaux avec des pointeurs (p < values + nv) plutôt qu'avec des indices.
        """, 2, "cibles.c",
        starter=r'''
        int nb_multiples_cibles(int *values, int nv, int *targets, int nt) {
            // TODO
            return 0;
        }
        ''',
        solution=r'''
        int nb_multiples_cibles(int *values, int nv, int *targets, int nt) {
            int c = 0;
            for (int *v = values; v < values + nv; v += 1) {
                for (int *t = targets; t < targets + nt; t += 1) {
                    if (*v % *t == 0) {
                        c += 1;
                        break;
                    }
                }
            }
            return c;
        }
        ''',
        protos="int nb_multiples_cibles(int *values, int nv, int *targets, int nt);",
        tests=r'''
        int v1[] = {4, 5, 7, 9}, t1[] = {2, 3};
        CHECK_INT(nb_multiples_cibles(v1, 4, t1, 2), 2, "({4,5,7,9}, {2,3})");
        int v2[] = {6, 12, 7}, t2[] = {2, 3};
        CHECK_INT(nb_multiples_cibles(v2, 3, t2, 2), 2, "({6,12,7}, {2,3})  (6 compte une seule fois)");
        int t3[] = {1};
        CHECK_INT(nb_multiples_cibles(v1, 4, t3, 1), 4, "(..., {1})");
        CHECK_INT(nb_multiples_cibles(v1, 4, t1, 0), 0, "(..., targets vide)");
        ''',
        indices=["Deux boucles imbriquées. Dès qu'une cible divise la valeur, compte-la et sors de la boucle "
                 "intérieure (break), sinon tu la comptes plusieurs fois.",
                 "Avec des pointeurs : for (int *v = values; v < values + nv; v += 1) ... *v ..."])

    rep("ptr_rep_base", "pointeurs", "Écrire à travers un pointeur", """
        Qu'affiche ce code (tiré du cours) ?
        """, 1, ["10 a"],
        code=r'''
        int i = 5;
        char c = 'a';
        int *p = NULL;
        p = &i;
        *p = 10;
        char *s = &c;
        printf("%d %c\n", i, *s);
        ''', auto=True,
        explication="p contient l'adresse de i : *p = 10 modifie i. s pointe sur c : *s vaut 'a'.")

    rep("ptr_rep_arith", "pointeurs", "Arithmétique de pointeurs", """
        Qu'affiche ce code ?
        """, 2, ["5 4 9"],
        code=r'''
        int t[10] = {0};
        int *p = t;
        p[0] = 5;
        p[1] = 4;
        p[3] = 9;
        int *q = p + 3;
        printf("%d %d %d\n", t[0], *(p + 1), *q);
        ''', auto=True,
        explication="p pointe sur t[0] ; p[i] et *(p + i) désignent la même case t[i] ; q = p + 3 pointe sur t[3].")

    rep("ptr_rep_len", "pointeurs", "Différence de pointeurs", """
        Qu'affiche ce code ?
        """, 2, ["7"],
        code=r'''
        char *s = "bonjour";
        char *p = s;
        while (*p != '\0')
            p += 1;
        printf("%d\n", (int)(p - s));
        ''', auto=True,
        explication="p avance jusqu'au '\\0' ; p - s = nombre de cases parcourues = la longueur (slide « pointeurs »).")

    qcm("ptr_qcm_types", "pointeurs", "Types et pointeurs", """
        int i = 3;
        int *p = &i;
        Quelles affirmations sont vraies ?
        """, 2,
        ["p contient l'adresse de i", "*p vaut 3", "&i est de type int", "sizeof(p) vaut 8 (adresse 64 bits)"],
        "abd",
        explication="&i est de type int * (une adresse vers un int). Tous les pointeurs font 8 octets "
                    "sur une machine 64 bits, quel que soit le type pointé.")

    qcm("ptr_qcm_null", "pointeurs", "Pointeur non initialisé", """
        Que se passe-t-il le plus probablement ?
        """, 2,
        ["ça affiche 5", "Segmentation fault : p ne pointe vers aucune zone valide",
         "ça ne compile pas", "p devient automatiquement l'adresse d'un nouvel int"],
        "b",
        code=r'''
        int *p = NULL;
        *p = 5;
        printf("%d\n", *p);
        ''',
        explication="NULL est une adresse invalide : écrire dedans fait planter le programme. Un pointeur "
                    "doit pointer vers une vraie variable (p = &i) ou une zone allouée (malloc).")

    # ======================================================================
    # 10. struct
    # ======================================================================
    fonc("struct_points", "struct", "Des points", """
        point.h définit :   struct point { int x; int y; };
        Dans points.c (pas de main), écris :
          struct point point_init(int x, int y)                 renvoie le point (x ; y)
          void point_deplace(struct point *p, int dx, int dy)   déplace le point pointé (avec ->)
          int distance2(struct point a, struct point b)         (xa-xb)² + (ya-yb)²
        """, 1, "points.c",
        starter=r'''
        #include "point.h"

        struct point point_init(int x, int y) {
            struct point p = {0, 0};
            // TODO
            return p;
        }

        void point_deplace(struct point *p, int dx, int dy) {
            // TODO
        }

        int distance2(struct point a, struct point b) {
            // TODO
            return 0;
        }
        ''',
        solution=r'''
        #include "point.h"

        struct point point_init(int x, int y) {
            struct point p;
            p.x = x;
            p.y = y;
            return p;
        }

        void point_deplace(struct point *p, int dx, int dy) {
            p->x += dx;
            p->y += dy;
        }

        int distance2(struct point a, struct point b) {
            int dx = a.x - b.x;
            int dy = a.y - b.y;
            return dx * dx + dy * dy;
        }
        ''',
        headers={"point.h": POINT_H},
        protos="struct point point_init(int x, int y);\nvoid point_deplace(struct point *p, int dx, int dy);\n"
               "int distance2(struct point a, struct point b);",
        tests=r'''
        section("point_init");
        struct point a = point_init(3, -4);
        CHECK_TRUE(a.x == 3 && a.y == -4, "point_init(3, -4) -> (3;-4)");
        section("point_deplace");
        struct point b = {1, 1};
        point_deplace(&b, 5, -2);
        CHECK_TRUE(b.x == 6 && b.y == -1, "b=(1;1), point_deplace(&b, 5, -2) -> (6;-1)");
        section("distance2");
        struct point o = {0, 0}, c = {-1, 2}, d = {2, 6};
        CHECK_INT(distance2(o, a), 25, "distance2((0;0), (3;-4))");
        CHECK_INT(distance2(a, a), 0, "distance2(a, a)");
        CHECK_INT(distance2(c, d), 25, "distance2((-1;2), (2;6))");
        ''',
        indices=["p.x pour une struct, ptr->x pour un POINTEUR vers une struct (= (*ptr).x).",
                 "point_deplace reçoit un pointeur : sans lui, on modifierait une copie."])

    fonc("struct_nuage", "struct", "Tableau de points", """
        point.h définit :   struct point { int x; int y; };
        Dans nuage.c (pas de main), écris :
          struct point barycentre(struct point t[], int n)
              moyenne des x et moyenne des y (division entière), n >= 1
          int plus_proche(struct point t[], int n, struct point cible)
              indice du point de t le plus proche de cible (le premier si égalité), -1 si n == 0
        (Tu peux réécrire une petite fonction distance2 dans ce fichier.)
        """, 2, "nuage.c",
        starter=r'''
        #include "point.h"

        struct point barycentre(struct point t[], int n) {
            struct point g = {0, 0};
            // TODO
            return g;
        }

        int plus_proche(struct point t[], int n, struct point cible) {
            // TODO
            return -1;
        }
        ''',
        solution=r'''
        #include "point.h"

        struct point barycentre(struct point t[], int n) {
            struct point g = {0, 0};
            for (int i = 0; i < n; i += 1) {
                g.x += t[i].x;
                g.y += t[i].y;
            }
            g.x /= n;
            g.y /= n;
            return g;
        }

        static int distance2(struct point a, struct point b) {
            return (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y);
        }

        int plus_proche(struct point t[], int n, struct point cible) {
            if (n == 0)
                return -1;
            int m = 0;
            for (int i = 1; i < n; i += 1)
                if (distance2(t[i], cible) < distance2(t[m], cible))
                    m = i;
            return m;
        }
        ''',
        headers={"point.h": POINT_H},
        protos="struct point barycentre(struct point t[], int n);\n"
               "int plus_proche(struct point t[], int n, struct point cible);",
        tests=r'''
        struct point t[] = {{0, 0}, {4, 0}, {4, 6}, {0, 6}};
        section("barycentre");
        struct point g = barycentre(t, 4);
        CHECK_TRUE(g.x == 2 && g.y == 3, "barycentre(carré (0;0)(4;0)(4;6)(0;6)) -> (2;3)");
        g = barycentre(t + 2, 1);
        CHECK_TRUE(g.x == 4 && g.y == 6, "barycentre({(4;6)}, 1) -> (4;6)");
        section("plus_proche");
        struct point c1 = {5, 5}, c2 = {2, 3};
        CHECK_INT(plus_proche(t, 4, c1), 2, "plus_proche(carré, 4, (5;5))");
        CHECK_INT(plus_proche(t, 4, c2), 0, "plus_proche(carré, 4, (2;3))  (égalité -> le premier)");
        CHECK_INT(plus_proche(t, 0, c1), -1, "plus_proche(t, 0, ...)");
        ''',
        indices=["t[i].x : le champ x de la case i du tableau de struct.",
                 "plus_proche : comme indice_min, mais on compare distance2(t[i], cible)."])

    fonc("struct_personne", "struct", "Struct avec des chaînes", """
        Dans personne.c, la struct est déjà définie (slide « struct » du cours) :
            struct person { char first[20]; char last[20]; int age; };
        Écris (tu peux utiliser <string.h>) :
          void person_init(struct person *p, char *first, char *last, int age)
              remplit les champs (copie les chaînes avec strcpy ; elles font moins de 20 caractères)
          int meme_famille(struct person *a, struct person *b)    1 si même nom (last), 0 sinon
          int plus_age(struct person t[], int n)                  indice de la personne la plus âgée
        """, 2, "personne.c",
        starter=r'''
        #include <string.h>

        struct person {
            char first[20];
            char last[20];
            int age;
        };

        void person_init(struct person *p, char *first, char *last, int age) {
            // TODO
        }

        int meme_famille(struct person *a, struct person *b) {
            // TODO
            return 0;
        }

        int plus_age(struct person t[], int n) {
            // TODO
            return 0;
        }
        ''',
        solution=r'''
        #include <string.h>

        struct person {
            char first[20];
            char last[20];
            int age;
        };

        void person_init(struct person *p, char *first, char *last, int age) {
            strcpy(p->first, first);
            strcpy(p->last, last);
            p->age = age;
        }

        int meme_famille(struct person *a, struct person *b) {
            return strcmp(a->last, b->last) == 0;
        }

        int plus_age(struct person t[], int n) {
            int m = 0;
            for (int i = 1; i < n; i += 1)
                if (t[i].age > t[m].age)
                    m = i;
            return m;
        }
        ''',
        protos="struct person { char first[20]; char last[20]; int age; };\n"
               "void person_init(struct person *p, char *first, char *last, int age);\n"
               "int meme_famille(struct person *a, struct person *b);\nint plus_age(struct person t[], int n);",
        tests=r'''
        struct person t[3];
        char prenom[] = "Ada";
        person_init(&t[0], prenom, "Lovelace", 36);
        prenom[0] = 'X';
        section("person_init");
        CHECK_STR(t[0].first, "Ada", "first == \"Ada\"  (copié, pas juste le pointeur)");
        CHECK_STR(t[0].last, "Lovelace", "last == \"Lovelace\"");
        CHECK_INT(t[0].age, 36, "age == 36");
        person_init(&t[1], "Byron", "Lovelace", 52);
        person_init(&t[2], "Alan", "Turing", 41);
        section("meme_famille");
        CHECK_INT(meme_famille(&t[0], &t[1]), 1, "Ada Lovelace / Byron Lovelace");
        CHECK_INT(meme_famille(&t[0], &t[2]), 0, "Ada Lovelace / Alan Turing");
        section("plus_age");
        CHECK_INT(plus_age(t, 3), 1, "plus_age (36, 52, 41)");
        CHECK_INT(plus_age(t, 1), 0, "plus_age (un seul)");
        ''',
        indices=["Un champ tableau ne s'affecte pas (p->first = first est refusé) : strcpy(p->first, first);",
                 "Comparer deux chaînes : strcmp(a->last, b->last) == 0."])

    qcm("struct_qcm_copie", "struct", "Struct passée par valeur", """
        Qu'affiche ce programme ?
        """, 2,
        ["0", "10", "ça ne compile pas", "une valeur au hasard"],
        "a",
        code=r'''
        #include <stdio.h>

        struct point { int x; int y; };

        void raz(struct point p) {
            p.x = 10;
        }

        int main(void) {
            struct point a = {.x = 0, .y = 0};
            raz(a);
            printf("%d\n", a.x);
            return 0;
        }
        ''',
        explication="Une struct passée en paramètre est COPIÉE entièrement. Pour la modifier : "
                    "void raz(struct point *p) { p->x = 10; } et raz(&a);")

    qcm("struct_qcm_fleche", "struct", "Point ou flèche ?", """
        struct point x = {.x = 5, .y = 10};
        struct point *ptr = &x;
        Quelles écritures modifient le champ y de x ?
        """, 2,
        ["ptr->y = 20;", "(*ptr).y = 20;", "ptr.y = 20;", "x.y = 20;"],
        "abd",
        explication="ptr->y est un raccourci pour (*ptr).y. ptr.y ne compile pas : ptr est un pointeur, "
                    "pas une struct.")

    rep("struct_rep_sizeof", "struct", "Taille d'une struct", """
        Qu'affiche ce code ?
        """, 2, ["8 80"],
        code=r'''
        #include <stdio.h>

        struct point { int x; int y; };

        int main(void) {
            struct point t[10];
            printf("%zu %zu\n", sizeof(struct point), sizeof(t));
            return 0;
        }
        ''', auto=True,
        explication="Deux int de 4 octets = 8 ; un tableau de 10 struct = 80.")

    # ======================================================================
    # 11. scanf, fgets, macros, globales
    # ======================================================================
    prog("entrees_stats", "entrees", "Statistiques au clavier", """
        stats.c lit des entiers sur l'entrée standard jusqu'à ce qu'il n'y en ait plus, puis affiche :
            nombre=N somme=S min=A max=B
            echo "3 7 1" | ./stats     ->  nombre=3 somme=11 min=1 max=7
        S'il n'y a aucun nombre : « aucun nombre ». (Au clavier, Ctrl+D signale la fin.)
        """, 2, "stats.c",
        starter=r'''
        #include <stdio.h>

        int main(void) {
            // TODO : lire avec scanf jusqu'à la fin, puis afficher
            return 0;
        }
        ''',
        solution=r'''
        #include <stdio.h>

        int main(void) {
            int x;
            int n = 0, s = 0, mn = 0, mx = 0;
            while (scanf("%d", &x) == 1) {
                if (n == 0 || x < mn)
                    mn = x;
                if (n == 0 || x > mx)
                    mx = x;
                s += x;
                n += 1;
            }
            if (n == 0)
                printf("aucun nombre\n");
            else
                printf("nombre=%d somme=%d min=%d max=%d\n", n, s, mn, mx);
            return 0;
        }
        ''',
        tests=[("", "nombre=3 somme=11 min=1 max=7", "3 7 1\n"),
               ("", "nombre=2 somme=3 min=-2 max=5", "5\n-2\n"),
               ("", "nombre=1 somme=42 min=42 max=42", "42"),
               ("", "nombre=4 somme=-32 min=-20 max=-1", "-8 -3 -20\n-1\n"),
               ("", "aucun nombre", ""),
               ("", "nombre=2 somme=30 min=10 max=20", "10 20 fin 30")],
        indices=["scanf renvoie le nombre de valeurs lues : while (scanf(\"%d\", &x) == 1) { ... }",
                 "N'oublie pas le & : scanf a besoin de l'ADRESSE de x.",
                 "min/max : initialise-les avec le PREMIER nombre lu, pas avec 0."])

    prog("entrees_fgets", "entrees", "Lire des lignes avec fgets", """
        maj.c lit l'entrée ligne par ligne avec fgets (buffer de taille BSIZE = 100, à définir
        avec un #define) et réaffiche chaque ligne en majuscules, précédée de son numéro :
            printf "salut\\nca va ?\\n" | ./maj   ->   1: SALUT
                                                     2: CA VA ?
        """, 2, "maj.c",
        starter=r'''
        #include <stdio.h>
        #include <string.h>

        // TODO : #define BSIZE 100

        int main(void) {
            // TODO : char buffer[BSIZE]; while (fgets(buffer, BSIZE, stdin) != NULL) { ... }
            return 0;
        }
        ''',
        solution=r'''
        #include <stdio.h>
        #include <string.h>

        #define BSIZE 100

        int main(void) {
            char buffer[BSIZE];
            int n = 0;
            while (fgets(buffer, BSIZE, stdin) != NULL) {
                n += 1;
                for (int i = 0; buffer[i] != '\0'; i += 1)
                    if (buffer[i] >= 'a' && buffer[i] <= 'z')
                        buffer[i] = buffer[i] - 'a' + 'A';
                printf("%d: %s", n, buffer);
            }
            return 0;
        }
        ''',
        tests=[("", "1: SALUT\n2: CA VA ?", "salut\nca va ?\n"), ("", "1: ABC 123", "abc 123\n"), ("", "", ""),
               ("", "1: X\n2: \n3: Y", "x\n\ny\n")],
        indices=["fgets renvoie NULL quand il n'y a plus rien à lire : while (fgets(buffer, BSIZE, stdin) != NULL)",
                 "fgets garde le '\\n' à la fin de la ligne : printf(\"%d: %s\", n, buffer) suffit, sans \\n.",
                 "Pour les majuscules : même boucle que majuscules() du thème chaînes."])

    qcm("entrees_qcm_scanf", "entrees", "scanf et le &", """
        int i;
        Laquelle de ces lignes lit correctement un entier au clavier ?
        """, 1,
        ["scanf(\"%d\", i);", "scanf(\"%d\", &i);", "scanf(\"%d\", *i);", "i = scanf(\"%d\");"],
        "b",
        explication="scanf doit ÉCRIRE dans i : il lui faut son adresse &i. Exception : pour une chaîne "
                    "(char buffer[20]), buffer est déjà une adresse : scanf(\"%s\", buffer).")

    rep("entrees_rep_globale", "entrees", "Variable globale", """
        Qu'affiche ce programme ? (écris les nombres séparés par des espaces)
        """, 2, ["1 2 3", "1\n2\n3"],
        code=r'''
        #include <stdio.h>

        int compteur = 0;

        void f(void) {
            compteur += 1;
            printf("%d\n", compteur);
        }

        int main(void) {
            f();
            f();
            f();
            return 0;
        }
        ''',
        explication="Une globale existe pendant tout le programme et garde sa valeur entre les appels "
                    "(slide « variables globales »). Une variable locale de f repartirait de 0 à chaque appel.")

    rep("entrees_rep_define", "entrees", "Macros", """
        Qu'affiche ce code ?
        """, 2, ["20"],
        code=r'''
        #include <stdio.h>

        #define N 10

        int main(void) {
            int t[N * 2];
            printf("%zu\n", sizeof(t) / sizeof(t[0]));
            return 0;
        }
        ''', auto=True,
        explication="Avant la compilation, N est remplacé par 10 : int t[10 * 2], soit 20 cases.")

    qcm("entrees_qcm_fgets", "entrees", "scanf(\"%s\") ou fgets ?", """
        char buffer[20];   On veut lire la ligne « Jean Dupont » tapée au clavier.
        Quelles affirmations sont vraies ?
        """, 3,
        ["scanf(\"%s\", buffer) ne lit que « Jean » (il s'arrête à l'espace)",
         "fgets(buffer, 20, stdin) lit toute la ligne, '\\n' compris",
         "fgets peut déborder si la ligne fait plus de 20 caractères",
         "scanf(\"%s\", &buffer[20]) est la bonne façon d'écrire"],
        "ab",
        explication="%s lit un mot (jusqu'à un espace) et ne connaît pas la taille du tableau ; fgets reçoit la "
                    "taille, c'est pour ça qu'il est « sécurisé » : il lit au plus 19 caractères + '\\0'.")

    # ======================================================================
    # 12. malloc / free
    # ======================================================================
    fonc("malloc_tab", "malloc", "Tableaux dynamiques", """
        Dans memoire.c (pas de main), écris des fonctions qui renvoient une zone allouée avec malloc
        (c'est l'appelant qui fera free) :
          int *tab_cree(int n, int v)     tableau de n cases valant toutes v
          int *tab_copie(int *t, int n)   nouvelle copie des n cases de t
        valgrind surveille : lecture/écriture hors zone et fuite = échec.
        """, 2, "memoire.c",
        starter=r'''
        #include <stdlib.h>

        int *tab_cree(int n, int v) {
            // TODO
            return NULL;
        }

        int *tab_copie(int *t, int n) {
            // TODO
            return NULL;
        }
        ''',
        solution=r'''
        #include <stdlib.h>

        int *tab_cree(int n, int v) {
            int *t = malloc(n * sizeof(int));
            for (int i = 0; i < n; i += 1)
                t[i] = v;
            return t;
        }

        int *tab_copie(int *t, int n) {
            int *c = malloc(n * sizeof(int));
            for (int i = 0; i < n; i += 1)
                c[i] = t[i];
            return c;
        }
        ''',
        protos="int *tab_cree(int n, int v);\nint *tab_copie(int *t, int n);",
        tests=r'''
        section("tab_cree");
        int *t = tab_cree(5, 7);
        CHECK_TRUE(t != NULL, "tab_cree(5, 7) != NULL");
        if (t) CHECK_TAB(t, 5, "tab_cree(5, 7)", {7, 7, 7, 7, 7});
        section("tab_copie");
        int src[] = {1, 2, 3};
        int *c = tab_copie(src, 3);
        CHECK_TRUE(c != NULL && c != src, "tab_copie renvoie une NOUVELLE zone");
        if (c && c != src) {
            CHECK_TAB(c, 3, "tab_copie({1,2,3})", {1, 2, 3});
            c[0] = 50;
            CHECK_INT(src[0], 1, "modifier la copie ne modifie pas l'original");
        }
        free(t);
        if (c != src) free(c);
        ''',
        valgrind=True,
        indices=["malloc(nombre d'octets) : pour n int, malloc(n * sizeof(int)).",
                 "Le pointeur renvoyé s'utilise comme un tableau : t[i] = v;"])

    fonc("malloc_strcat", "malloc", "Concaténer (slide strcat)", """
        Dans concat.c (pas de main), écris (exemple du cours) :
          char *ma_strcat(const char *a, const char *b)
              renvoie une NOUVELLE chaîne allouée avec malloc contenant a puis b
              ma_strcat("hello", "world") -> "helloworld"
        Tu peux utiliser strlen. valgrind surveille (attention au '\\0' !).
        """, 2, "concat.c",
        starter=r'''
        #include <stdlib.h>
        #include <string.h>

        char *ma_strcat(const char *a, const char *b) {
            // TODO
            return NULL;
        }
        ''',
        solution=r'''
        #include <stdlib.h>
        #include <string.h>

        char *ma_strcat(const char *a, const char *b) {
            int lena = strlen(a);
            int lenb = strlen(b);
            char *r = malloc(sizeof(char) * (lena + lenb + 1));
            int j = 0;
            for (int i = 0; i < lena; i += 1, j += 1)
                r[j] = a[i];
            for (int i = 0; i < lenb; i += 1, j += 1)
                r[j] = b[i];
            r[j] = '\0';
            return r;
        }
        ''',
        protos="char *ma_strcat(const char *a, const char *b);",
        tests=r'''
        char *s1 = ma_strcat("hello", "world");
        CHECK_STR(s1, "helloworld", "ma_strcat(\"hello\", \"world\")");
        char *s2 = ma_strcat("", "abc");
        CHECK_STR(s2, "abc", "ma_strcat(\"\", \"abc\")");
        char *s3 = ma_strcat("", "");
        CHECK_STR(s3, "", "ma_strcat(\"\", \"\")");
        free(s1); free(s2); free(s3);
        ''',
        valgrind=True,
        indices=["Taille à allouer : strlen(a) + strlen(b) + 1 (le +1 pour le '\\0').",
                 "Copie a, puis b à la suite, puis écris le '\\0' final."])

    fonc("malloc_repete", "malloc", "Répéter une chaîne", """
        Dans repete.c (pas de main), écris :
          char *repete(const char *s, int n)
              nouvelle chaîne (malloc) contenant s répétée n fois : repete("ab", 3) -> "ababab"
              n = 0 -> "" (une chaîne vide allouée, pas NULL)
        valgrind surveille.
        """, 3, "repete.c",
        starter=r'''
        #include <stdlib.h>
        #include <string.h>

        char *repete(const char *s, int n) {
            // TODO
            return NULL;
        }
        ''',
        solution=r'''
        #include <stdlib.h>
        #include <string.h>

        char *repete(const char *s, int n) {
            int l = strlen(s);
            char *r = malloc(l * n + 1);
            for (int k = 0; k < n; k += 1)
                for (int i = 0; i < l; i += 1)
                    r[k * l + i] = s[i];
            r[l * n] = '\0';
            return r;
        }
        ''',
        protos="char *repete(const char *s, int n);",
        tests=r'''
        char *r1 = repete("ab", 3);
        CHECK_STR(r1, "ababab", "repete(\"ab\", 3)");
        char *r2 = repete("xyz", 1);
        CHECK_STR(r2, "xyz", "repete(\"xyz\", 1)");
        char *r3 = repete("ab", 0);
        CHECK_STR(r3, "", "repete(\"ab\", 0)");
        char *r4 = repete("", 5);
        CHECK_STR(r4, "", "repete(\"\", 5)");
        free(r1); free(r2); free(r3); free(r4);
        ''',
        valgrind=True,
        indices=["Longueur totale : strlen(s) * n, + 1 pour le '\\0'.",
                 "La k-ième copie commence à la case k * strlen(s)."])

    fonc("malloc_filtre", "malloc", "Filtrer dans un nouveau tableau", """
        Dans filtre.c (pas de main), écris :
          int *filtre_pairs(int *t, int n, int *taille)
              renvoie un NOUVEAU tableau (malloc) contenant seulement les valeurs paires de t,
              dans l'ordre, et range leur nombre dans *taille.
              {3, 4, 8, 1, -2} -> {4, 8, -2} et *taille = 3
              (s'il n'y en a aucune : *taille = 0, et tu peux renvoyer NULL)
        valgrind surveille.
        """, 3, "filtre.c",
        starter=r'''
        #include <stdlib.h>

        int *filtre_pairs(int *t, int n, int *taille) {
            // TODO
            *taille = 0;
            return NULL;
        }
        ''',
        solution=r'''
        #include <stdlib.h>

        int *filtre_pairs(int *t, int n, int *taille) {
            int c = 0;
            for (int i = 0; i < n; i += 1)
                if (t[i] % 2 == 0)
                    c += 1;
            *taille = c;
            if (c == 0)
                return NULL;
            int *r = malloc(c * sizeof(int));
            int j = 0;
            for (int i = 0; i < n; i += 1)
                if (t[i] % 2 == 0) {
                    r[j] = t[i];
                    j += 1;
                }
            return r;
        }
        ''',
        protos="int *filtre_pairs(int *t, int n, int *taille);",
        tests=r'''
        int t[] = {3, 4, 8, 1, -2};
        int k = -1;
        int *r = filtre_pairs(t, 5, &k);
        CHECK_INT(k, 3, "filtre_pairs({3,4,8,1,-2}) : *taille");
        if (r && k == 3) CHECK_TAB(r, 3, "filtre_pairs({3,4,8,1,-2})", {4, 8, -2});
        free(r);
        int u[] = {1, 3, 5};
        int *r2 = filtre_pairs(u, 3, &k);
        CHECK_INT(k, 0, "filtre_pairs({1,3,5}) : *taille");
        free(r2);
        ''',
        valgrind=True,
        indices=["Deux passages : d'abord compter les pairs (pour savoir combien allouer), puis remplir.",
                 "*taille = c; renvoie la taille à l'appelant (passage par adresse)."])

    qcm("malloc_qcm_free", "malloc", "Après free", """
        Qu'est-ce qui ne va pas dans ce code ?
        """, 2,
        ["rien", "après free(p), la zone ne nous appartient plus : lire *p est interdit (use after free)",
         "il faut écrire free(*p)", "malloc(sizeof(int)) réserve 1 octet au lieu de 4"],
        "b",
        code=r'''
        int *p = malloc(sizeof(int));
        *p = 5;
        free(p);
        printf("%d\n", *p);
        ''',
        explication="« après cet appel, on ne doit plus utiliser les données à l'adresse contenue dans i » "
                    "(slide malloc). valgrind le signale : Invalid read of size 4.")

    qcm("malloc_qcm_local", "malloc", "Renvoyer un tableau local", """
        Pourquoi cette fonction est-elle fausse ?
        """, 3,
        ["elle est correcte",
         "t est une variable locale (dans la pile) : elle disparaît à la fin de la fonction, l'adresse "
         "renvoyée ne vaut plus rien",
         "il faut écrire return &t;",
         "il manque un free(t) avant le return"],
        "b",
        code=r'''
        int *cree_tab(void) {
            int t[10];
            for (int i = 0; i < 10; i += 1)
                t[i] = i;
            return t;
        }
        ''',
        explication="« On ne peut pas renvoyer un tableau » de la pile. Solution : int *t = malloc(10 * "
                    "sizeof(int)); la zone du tas reste réservée jusqu'au free.")

    qcm("malloc_qcm_pile_tas", "malloc", "Pile ou tas ?", """
        Quelles affirmations sont vraies (slide « variable » du cours) ?
        """, 2,
        ["les variables locales et les paramètres sont dans la pile",
         "une zone obtenue par malloc est dans le tas",
         "une variable peut être directement dans le tas",
         "on manipule les données du tas à travers des pointeurs"],
        "abd",
        explication="Une variable est dans la pile (locale, paramètre) ou globale, jamais dans le tas : on "
                    "accède au tas via un pointeur qui contient l'adresse renvoyée par malloc.")

    # ======================================================================
    # 13. Listes chaînées
    # ======================================================================
    fonc("liste_bases", "listes", "Construire une liste", """
        liste.h définit :   struct cell { int value; struct cell *next; };
        Dans liste.c (pas de main), écris (exercice liste chaînée du cours) :
          void cell_init(struct cell *c, int v)              value = v, next = NULL
          void cell_chaine(struct cell *a, struct cell *b)   insère b JUSTE APRÈS a (a peut déjà
                                                             avoir un suivant, qui passe après b)
          int liste_longueur(struct cell *l)                 nombre de cellules (0 si l == NULL)
          int liste_somme(struct cell *l)                    somme des valeurs
        """, 2, "liste.c",
        starter=r'''
        #include "liste.h"

        void cell_init(struct cell *c, int v) {
            // TODO
        }

        void cell_chaine(struct cell *a, struct cell *b) {
            // TODO
        }

        int liste_longueur(struct cell *l) {
            // TODO
            return 0;
        }

        int liste_somme(struct cell *l) {
            // TODO
            return 0;
        }
        ''',
        solution=r'''
        #include "liste.h"

        void cell_init(struct cell *c, int v) {
            c->value = v;
            c->next = NULL;
        }

        void cell_chaine(struct cell *a, struct cell *b) {
            b->next = a->next;
            a->next = b;
        }

        int liste_longueur(struct cell *l) {
            int n = 0;
            for (struct cell *p = l; p != NULL; p = p->next)
                n += 1;
            return n;
        }

        int liste_somme(struct cell *l) {
            int s = 0;
            for (struct cell *p = l; p != NULL; p = p->next)
                s += p->value;
            return s;
        }
        ''',
        headers={"liste.h": LISTE_H},
        protos=r'''
        void cell_init(struct cell *c, int v);
        void cell_chaine(struct cell *a, struct cell *b);
        int liste_longueur(struct cell *l);
        int liste_somme(struct cell *l);
        static const char *str(struct cell *l) {
            static char buf[512];
            int k = 0, n = 0;
            buf[0] = '\0';
            for (struct cell *p = l; p != NULL && n < 50; p = p->next, n++)
                k += snprintf(buf + k, sizeof buf - k, n ? " %d" : "%d", p->value);
            if (n == 50) snprintf(buf + k, sizeof buf - k, " ... (la liste boucle !)");
            return buf;
        }
        ''',
        tests=r'''
        struct cell c[3];
        memset(c, 0, sizeof c);
        section("cell_init");
        c[0].value = 123; c[0].next = &c[1];
        cell_init(&c[0], 5);
        CHECK_TRUE(c[0].value == 5 && c[0].next == NULL, "cell_init(&c, 5) -> value=5, next=NULL");
        section("cell_chaine");
        cell_init(&c[0], 1); cell_init(&c[1], 3); cell_init(&c[2], 2);
        cell_chaine(&c[0], &c[1]);
        CHECK_STR(str(&c[0]), "1 3", "1, puis cell_chaine(1, 3)");
        cell_chaine(&c[0], &c[2]);
        CHECK_STR(str(&c[0]), "1 2 3", "1 3, puis cell_chaine(1, 2) -> 2 s'insère entre 1 et 3");
        section("liste_longueur / liste_somme");
        CHECK_INT(liste_longueur(&c[0]), 3, "liste_longueur(1 2 3)");
        CHECK_INT(liste_longueur(NULL), 0, "liste_longueur(NULL)");
        CHECK_INT(liste_somme(&c[0]), 6, "liste_somme(1 2 3)");
        CHECK_INT(liste_somme(NULL), 0, "liste_somme(NULL)");
        ''',
        indices=["Parcours type : for (struct cell *p = l; p != NULL; p = p->next) { ... p->value ... }",
                 "cell_chaine, dans cet ordre : b->next = a->next;  puis  a->next = b;",
                 "Dessine les cases et les flèches sur papier !"])

    fonc("liste_inverse", "listes", "Renverser une liste", """
        liste.h définit :   struct cell { int value; struct cell *next; };
        Dans liste.c (pas de main), écris :
          struct cell *liste_inverse(struct cell *l)
              renverse l'ordre de la liste en changeant les next, renvoie la nouvelle tête
              1 -> 2 -> 3   devient   3 -> 2 -> 1
        """, 3, "liste.c",
        starter=r'''
        #include "liste.h"

        struct cell *liste_inverse(struct cell *l) {
            // TODO
            return l;
        }
        ''',
        solution=r'''
        #include "liste.h"

        struct cell *liste_inverse(struct cell *l) {
            struct cell *prec = NULL;
            struct cell *cour = l;
            while (cour != NULL) {
                struct cell *suiv = cour->next;
                cour->next = prec;
                prec = cour;
                cour = suiv;
            }
            return prec;
        }
        ''',
        headers={"liste.h": LISTE_H},
        protos=r'''
        struct cell *liste_inverse(struct cell *l);
        static const char *str(struct cell *l) {
            static char buf[512];
            int k = 0, n = 0;
            buf[0] = '\0';
            for (struct cell *p = l; p != NULL && n < 50; p = p->next, n++)
                k += snprintf(buf + k, sizeof buf - k, n ? " %d" : "%d", p->value);
            if (n == 50) snprintf(buf + k, sizeof buf - k, " ... (la liste boucle !)");
            return buf;
        }
        static struct cell *build(struct cell c[], int vals[], int n) {
            for (int i = 0; i < n; i++) { c[i].value = vals[i]; c[i].next = (i + 1 < n) ? &c[i + 1] : NULL; }
            return n ? &c[0] : NULL;
        }
        ''',
        tests=r'''
        struct cell c[10];
        int v[] = {1, 2, 3, 4, 5};
        CHECK_STR(str(liste_inverse(build(c, v, 5))), "5 4 3 2 1", "liste_inverse(1 2 3 4 5)");
        CHECK_STR(str(liste_inverse(build(c, v, 2))), "2 1", "liste_inverse(1 2)");
        CHECK_STR(str(liste_inverse(build(c, v, 1))), "1", "liste_inverse(1)");
        CHECK_TRUE(liste_inverse(NULL) == NULL, "liste_inverse(NULL) == NULL");
        ''',
        indices=["Trois pointeurs : prec (NULL au début), cour (= l), suiv.",
                 "À chaque tour : suiv = cour->next; cour->next = prec; prec = cour; cour = suiv;",
                 "À la fin, prec est la nouvelle tête."])

    fonc("liste_retire", "listes", "Retirer des valeurs", """
        liste.h définit :   struct cell { int value; struct cell *next; };
        Dans liste.c (pas de main), écris :
          struct cell *liste_retire(struct cell *l, int v)
              retire TOUTES les cellules valant v (même en tête), renvoie la nouvelle tête
              (pas de free : ici les cellules ne viennent pas de malloc)
              7 1 7 7 2 7, retire 7  ->  1 2
        """, 3, "liste.c",
        starter=r'''
        #include "liste.h"

        struct cell *liste_retire(struct cell *l, int v) {
            // TODO
            return l;
        }
        ''',
        solution=r'''
        #include "liste.h"

        struct cell *liste_retire(struct cell *l, int v) {
            while (l != NULL && l->value == v)
                l = l->next;
            for (struct cell *p = l; p != NULL; p = p->next)
                while (p->next != NULL && p->next->value == v)
                    p->next = p->next->next;
            return l;
        }
        ''',
        headers={"liste.h": LISTE_H},
        protos=r'''
        struct cell *liste_retire(struct cell *l, int v);
        static const char *str(struct cell *l) {
            static char buf[512];
            int k = 0, n = 0;
            buf[0] = '\0';
            for (struct cell *p = l; p != NULL && n < 50; p = p->next, n++)
                k += snprintf(buf + k, sizeof buf - k, n ? " %d" : "%d", p->value);
            if (n == 50) snprintf(buf + k, sizeof buf - k, " ... (la liste boucle !)");
            return buf;
        }
        static struct cell *build(struct cell c[], int vals[], int n) {
            for (int i = 0; i < n; i++) { c[i].value = vals[i]; c[i].next = (i + 1 < n) ? &c[i + 1] : NULL; }
            return n ? &c[0] : NULL;
        }
        ''',
        tests=r'''
        struct cell c[10];
        int v2[] = {7, 1, 7, 7, 2, 7};
        CHECK_STR(str(liste_retire(build(c, v2, 6), 7)), "1 2", "liste_retire(7 1 7 7 2 7, 7)");
        int v3[] = {4, 4, 4};
        CHECK_TRUE(liste_retire(build(c, v3, 3), 4) == NULL, "liste_retire(4 4 4, 4) == NULL");
        int v4[] = {1, 2, 3};
        CHECK_STR(str(liste_retire(build(c, v4, 3), 9)), "1 2 3", "liste_retire(1 2 3, 9)");
        CHECK_STR(str(liste_retire(build(c, v4, 3), 3)), "1 2", "liste_retire(1 2 3, 3)");
        ''',
        indices=["D'abord la tête : tant que l existe et vaut v, avance l.",
                 "Ensuite, pour chaque p : tant que p->next existe et vaut v, saute-le : p->next = p->next->next;"])

    fonc("liste_triee", "listes", "Insertion triée", """
        liste.h définit :   struct cell { int value; struct cell *next; };
        Dans liste.c (pas de main), écris (bonus du cours) :
          struct cell *liste_insere_trie(struct cell *l, struct cell *c)
              l est triée par ordre croissant ; insère la cellule c à sa place, renvoie la nouvelle tête
        """, 3, "liste.c",
        starter=r'''
        #include "liste.h"

        struct cell *liste_insere_trie(struct cell *l, struct cell *c) {
            // TODO
            return l;
        }
        ''',
        solution=r'''
        #include "liste.h"

        struct cell *liste_insere_trie(struct cell *l, struct cell *c) {
            if (l == NULL || c->value <= l->value) {
                c->next = l;
                return c;
            }
            struct cell *p = l;
            while (p->next != NULL && p->next->value < c->value)
                p = p->next;
            c->next = p->next;
            p->next = c;
            return l;
        }
        ''',
        headers={"liste.h": LISTE_H},
        protos=r'''
        struct cell *liste_insere_trie(struct cell *l, struct cell *c);
        static const char *str(struct cell *l) {
            static char buf[512];
            int k = 0, n = 0;
            buf[0] = '\0';
            for (struct cell *p = l; p != NULL && n < 50; p = p->next, n++)
                k += snprintf(buf + k, sizeof buf - k, n ? " %d" : "%d", p->value);
            if (n == 50) snprintf(buf + k, sizeof buf - k, " ... (la liste boucle !)");
            return buf;
        }
        ''',
        tests=r'''
        struct cell c[6];
        int vals[] = {5, 2, 8, 1, 5, 9};
        struct cell *l = NULL;
        for (int i = 0; i < 6; i += 1) {
            c[i].value = vals[i];
            c[i].next = NULL;
            l = liste_insere_trie(l, &c[i]);
        }
        CHECK_STR(str(l), "1 2 5 5 8 9", "insertions de 5, 2, 8, 1, 5, 9 dans une liste vide");
        struct cell z = {0, NULL};
        CHECK_STR(str(liste_insere_trie(l, &z)), "0 1 2 5 5 8 9", "puis insertion de 0 (nouvelle tête)");
        ''',
        indices=["Cas de la tête : si la liste est vide ou si c->value <= l->value, c devient la tête.",
                 "Sinon, avance p tant que p->next existe et p->next->value < c->value, puis insère c après p."])

    fonc("liste_malloc", "listes", "Liste allouée dynamiquement", """
        liste.h définit :   struct cell { int value; struct cell *next; };
        Dans liste.c (pas de main), écris :
          struct cell *cell_nouvelle(int v)               malloc une cellule, value = v, next = NULL
          struct cell *liste_depuis_tab(int *t, int n)    liste t[0] -> t[1] -> ... (NULL si n == 0)
          void liste_libere(struct cell *l)               free de TOUTES les cellules
        valgrind surveille : aucune fuite autorisée.
        """, 4, "liste.c",
        starter=r'''
        #include "liste.h"

        struct cell *cell_nouvelle(int v) {
            // TODO
            return NULL;
        }

        struct cell *liste_depuis_tab(int *t, int n) {
            // TODO
            return NULL;
        }

        void liste_libere(struct cell *l) {
            // TODO
        }
        ''',
        solution=r'''
        #include "liste.h"

        struct cell *cell_nouvelle(int v) {
            struct cell *c = malloc(sizeof(struct cell));
            c->value = v;
            c->next = NULL;
            return c;
        }

        struct cell *liste_depuis_tab(int *t, int n) {
            struct cell *tete = NULL;
            for (int i = n - 1; i >= 0; i -= 1) {
                struct cell *c = cell_nouvelle(t[i]);
                c->next = tete;
                tete = c;
            }
            return tete;
        }

        void liste_libere(struct cell *l) {
            while (l != NULL) {
                struct cell *suiv = l->next;
                free(l);
                l = suiv;
            }
        }
        ''',
        headers={"liste.h": LISTE_H},
        protos=r'''
        struct cell *cell_nouvelle(int v);
        struct cell *liste_depuis_tab(int *t, int n);
        void liste_libere(struct cell *l);
        static const char *str(struct cell *l) {
            static char buf[512];
            int k = 0, n = 0;
            buf[0] = '\0';
            for (struct cell *p = l; p != NULL && n < 50; p = p->next, n++)
                k += snprintf(buf + k, sizeof buf - k, n ? " %d" : "%d", p->value);
            if (n == 50) snprintf(buf + k, sizeof buf - k, " ... (la liste boucle !)");
            return buf;
        }
        ''',
        tests=r'''
        section("cell_nouvelle");
        struct cell *c = cell_nouvelle(4);
        CHECK_TRUE(c != NULL && c->value == 4 && c->next == NULL, "cell_nouvelle(4)");
        free(c);
        section("liste_depuis_tab");
        int t[] = {3, 1, 4, 1, 5};
        struct cell *l = liste_depuis_tab(t, 5);
        CHECK_STR(str(l), "3 1 4 1 5", "liste_depuis_tab({3,1,4,1,5})");
        CHECK_TRUE(liste_depuis_tab(t, 0) == NULL, "liste_depuis_tab(t, 0) == NULL");
        section("liste_libere");
        liste_libere(l);
        liste_libere(NULL);
        CHECK_TRUE(1, "liste_libere ne plante pas (valgrind vérifie qu'il ne reste aucune fuite)");
        ''',
        valgrind=True,
        indices=["cell_nouvelle : malloc(sizeof(struct cell)), puis initialise les DEUX champs.",
                 "liste_depuis_tab : le plus simple est de partir de la fin du tableau et d'ajouter en tête.",
                 "liste_libere : sauvegarde l->next AVANT free(l) (après, on ne peut plus lire l)."])

    qcm("liste_qcm_ordre", "listes", "Ordre des affectations", """
        On veut insérer la cellule b juste après la cellule a. Quel ordre est correct ?
        """, 2,
        ["a->next = b;  puis  b->next = a->next;",
         "b->next = a->next;  puis  a->next = b;",
         "les deux marchent",
         "a = b;  puis  b->next = a;"],
        "b",
        explication="Si on commence par a->next = b, on perd l'adresse de l'ancien suivant de a, et "
                    "b->next = a->next fait pointer b sur lui-même : la liste boucle.")

    # ======================================================================
    # 14. Projets type examen
    # ======================================================================
    fonc("projet_cesar", "projets", "Code de César", """
        Dans cesar.c (pas de main), écris les trois versions du code de César (exercice du cours).
        Chaque lettre est décalée de d dans l'alphabet en bouclant ("y" décalé de 3 -> "b").
        Minuscules et majuscules sont décalées (en restant min/maj), le reste ne change pas.
        d peut être négatif ou plus grand que 26.
          void cesar_code_i(char *msg, int d)                     remplace msg par sa version codée
          void cesar_code_s(const char *msg, int d, char *out)    écrit la version codée dans out
          char *cesar_code_d(const char *msg, int d)              renvoie une nouvelle chaîne (malloc)
            "bonjour", 2 -> "dqplqwt"        "dqplqwt", -2 -> "bonjour"
        valgrind surveille.
        """, 4, "cesar.c",
        starter=r'''
        #include <stdlib.h>
        #include <string.h>

        void cesar_code_i(char *msg, int d) {
            // TODO
        }

        void cesar_code_s(const char *msg, int d, char *out) {
            // TODO
        }

        char *cesar_code_d(const char *msg, int d) {
            // TODO
            return NULL;
        }
        ''',
        solution=r'''
        #include <stdlib.h>
        #include <string.h>

        static char decale(char c, int d) {
            d = ((d % 26) + 26) % 26;
            if (c >= 'a' && c <= 'z')
                return 'a' + (c - 'a' + d) % 26;
            if (c >= 'A' && c <= 'Z')
                return 'A' + (c - 'A' + d) % 26;
            return c;
        }

        void cesar_code_i(char *msg, int d) {
            for (int i = 0; msg[i] != '\0'; i += 1)
                msg[i] = decale(msg[i], d);
        }

        void cesar_code_s(const char *msg, int d, char *out) {
            int i;
            for (i = 0; msg[i] != '\0'; i += 1)
                out[i] = decale(msg[i], d);
            out[i] = '\0';
        }

        char *cesar_code_d(const char *msg, int d) {
            char *r = malloc(strlen(msg) + 1);
            cesar_code_s(msg, d, r);
            return r;
        }
        ''',
        protos="void cesar_code_i(char *msg, int d);\nvoid cesar_code_s(const char *msg, int d, char *out);\n"
               "char *cesar_code_d(const char *msg, int d);",
        tests=r'''
        section("cesar_code_i");
        char m1[] = "bonjour";
        cesar_code_i(m1, 2);
        CHECK_STR(m1, "dqplqwt", "cesar_code_i(\"bonjour\", 2)");
        cesar_code_i(m1, -2);
        CHECK_STR(m1, "bonjour", "cesar_code_i(\"dqplqwt\", -2)");
        char m2[] = "xyz abc";
        cesar_code_i(m2, 3);
        CHECK_STR(m2, "abc def", "cesar_code_i(\"xyz abc\", 3)");
        section("cesar_code_s");
        char out[64];
        memset(out, 'X', sizeof out);
        out[63] = '\0';
        cesar_code_s("Hello, World 42!", 1, out);
        CHECK_STR(out, "Ifmmp, Xpsme 42!", "cesar_code_s(\"Hello, World 42!\", 1, out)");
        const char *orig = "Zebre";
        cesar_code_s(orig, 27, out);
        CHECK_STR(out, "Afcsf", "cesar_code_s(\"Zebre\", 27, out)");
        section("cesar_code_d");
        char *r1 = cesar_code_d("abc", -1);
        CHECK_STR(r1, "zab", "cesar_code_d(\"abc\", -1)");
        char *r2 = cesar_code_d("", 5);
        CHECK_STR(r2, "", "cesar_code_d(\"\", 5)");
        char *r3 = cesar_code_d("Abc", -53);
        CHECK_STR(r3, "Zab", "cesar_code_d(\"Abc\", -53)");
        free(r1); free(r2); free(r3);
        ''',
        valgrind=True,
        indices=["Écris d'abord une petite fonction  char decale(char c, int d)  et utilise-la dans les trois.",
                 "Piège : -1 % 26 vaut -1 en C. Ramène d entre 0 et 25 : d = ((d % 26) + 26) % 26;",
                 "cesar_code_d : malloc(strlen(msg) + 1) puis réutilise cesar_code_s."])

    fonc("projet_reseau1", "projets", "Réseau (1/2) : créer les équipements", """
        Exercice « réseau » du cours, première partie. reseau.h (fourni) définit enum netkind
        { ROUTER, SWITCH, HOST, SERVER }, struct NetNode (id, name, kind, out[3]) et struct Network
        (nodes[10], count, start). Dans reseau.c (pas de main), écris :
          const char *netkind_str(enum netkind k)         "ROUTER", "SWITCH", "HOST", "SERVER"
          struct NetNode *node_create(int id, char *name, enum netkind kind)
              malloc + initialisation ; name : on garde le pointeur reçu ; les out[] à NULL
          int node_connect(struct NetNode *a, struct NetNode *b)
              connexion a -> b dans la première case libre de a->out ; 1 si ok, 0 si a est plein
          struct Network *net_create(void)                malloc, count = 0, start = NULL
          int net_add(struct Network *net, struct NetNode *n, int is_start)
              ajoute n à la fin de nodes (0 si plein, 1 sinon) ; si is_start, n devient start
        valgrind surveille (le main de test fait les free).
        """, 3, "reseau.c",
        starter=r'''
        #include "reseau.h"

        const char *netkind_str(enum netkind k) {
            // TODO
            return "?";
        }

        struct NetNode *node_create(int id, char *name, enum netkind kind) {
            // TODO
            return NULL;
        }

        int node_connect(struct NetNode *a, struct NetNode *b) {
            // TODO
            return 0;
        }

        struct Network *net_create(void) {
            // TODO
            return NULL;
        }

        int net_add(struct Network *net, struct NetNode *n, int is_start) {
            // TODO
            return 0;
        }
        ''',
        solution='#include "reseau.h"\n' + RESEAU_BASE,
        headers={"reseau.h": RESEAU_H},
        protos=r'''
        const char *netkind_str(enum netkind k);
        struct NetNode *node_create(int id, char *name, enum netkind kind);
        int node_connect(struct NetNode *a, struct NetNode *b);
        struct Network *net_create(void);
        int net_add(struct Network *net, struct NetNode *n, int is_start);
        ''',
        tests=r'''
        section("netkind_str");
        CHECK_STR(netkind_str(ROUTER), "ROUTER", "netkind_str(ROUTER)");
        CHECK_STR(netkind_str(SERVER), "SERVER", "netkind_str(SERVER)");
        CHECK_STR(netkind_str(HOST), "HOST", "netkind_str(HOST)");
        section("node_create");
        struct NetNode *r = node_create(1, "box", ROUTER);
        CHECK_TRUE(r != NULL, "node_create != NULL");
        if (!r) return finish();
        CHECK_TRUE(r->id == 1 && r->kind == ROUTER, "id = 1, kind = ROUTER");
        CHECK_STR(r->name, "box", "name = \"box\"");
        CHECK_TRUE(r->out[0] == NULL && r->out[1] == NULL && r->out[2] == NULL, "out[0..2] == NULL");
        section("node_connect");
        struct NetNode *h[4];
        for (int i = 0; i < 4; i += 1) h[i] = node_create(10 + i, "pc", HOST);
        CHECK_INT(node_connect(r, h[0]), 1, "node_connect(r, h0)");
        CHECK_INT(node_connect(r, h[1]), 1, "node_connect(r, h1)");
        CHECK_INT(node_connect(r, h[2]), 1, "node_connect(r, h2)");
        CHECK_INT(node_connect(r, h[3]), 0, "node_connect(r, h3) : r est plein");
        CHECK_TRUE(r->out[0] == h[0] && r->out[1] == h[1] && r->out[2] == h[2], "r->out = {h0, h1, h2}");
        section("net_create / net_add");
        struct Network *net = net_create();
        CHECK_TRUE(net != NULL, "net_create != NULL");
        if (!net) return finish();
        CHECK_TRUE(net->count == 0 && net->start == NULL, "count = 0, start = NULL");
        CHECK_INT(net_add(net, h[0], 0), 1, "net_add(net, h0, 0)");
        CHECK_INT(net_add(net, r, 1), 1, "net_add(net, r, 1)");
        CHECK_TRUE(net->count == 2 && net->nodes[0] == h[0] && net->nodes[1] == r, "nodes = {h0, r}, count = 2");
        CHECK_TRUE(net->start == r, "start == r");
        for (int i = 0; i < 8; i += 1) net_add(net, h[1], 0);
        CHECK_INT(net_add(net, h[2], 0), 0, "11e net_add : réseau plein -> 0");
        CHECK_INT(net->count, 10, "count reste à 10");
        free(net);
        free(r);
        for (int i = 0; i < 4; i += 1) free(h[i]);
        ''',
        valgrind=True,
        indices=["node_create : struct NetNode *n = malloc(sizeof(struct NetNode)); puis n->id = id; ... "
                 "et une boucle pour mettre les out[i] à NULL.",
                 "node_connect : cherche le premier i tel que a->out[i] == NULL.",
                 "net_add : net->nodes[net->count] = n; net->count += 1;"])

    fonc("projet_reseau2", "projets", "Réseau (2/2) : parcourir le réseau", """
        Suite de l'exercice « réseau ». reseau.c contient déjà les fonctions de la partie 1.
        Ajoute :
          int net_count(struct Network *net, enum netkind k)   nombre d'équipements de type k
          int net_node_id(struct Network *net, struct NetNode *n)   indice de n dans nodes, -1 sinon
          int net_to_node(struct Network *net, struct NetNode *n)
              nombre d'équipements du réseau qui ont une connexion (out) vers n
          struct NetNode *net_send(struct Network *net, int max)
              part de start et suit toujours out[0] ; renvoie l'équipement où l'on s'arrête
              (out[0] == NULL). Renvoie NULL si plus de max équipements ont été traversés (boucle)
              ou si start est NULL.
          int net_loop(struct Network *net)
              1 si, en suivant out[0] depuis start, on repasse par un équipement déjà vu, 0 sinon
        """, 4, "reseau.c",
        starter='#include "reseau.h"\n\n// ---- partie 1 (déjà faite) ----\n' + RESEAU_BASE + D(r'''
        // ---- partie 2 : à toi ----

        int net_count(struct Network *net, enum netkind k) {
            // TODO
            return 0;
        }

        int net_node_id(struct Network *net, struct NetNode *n) {
            // TODO
            return -1;
        }

        int net_to_node(struct Network *net, struct NetNode *n) {
            // TODO
            return 0;
        }

        struct NetNode *net_send(struct Network *net, int max) {
            // TODO
            return NULL;
        }

        int net_loop(struct Network *net) {
            // TODO
            return 0;
        }
        '''),
        solution='#include "reseau.h"\n' + RESEAU_BASE + D(r'''
        int net_count(struct Network *net, enum netkind k) {
            int c = 0;
            for (int i = 0; i < net->count; i += 1)
                if (net->nodes[i]->kind == k)
                    c += 1;
            return c;
        }

        int net_node_id(struct Network *net, struct NetNode *n) {
            for (int i = 0; i < net->count; i += 1)
                if (net->nodes[i] == n)
                    return i;
            return -1;
        }

        int net_to_node(struct Network *net, struct NetNode *n) {
            int c = 0;
            for (int i = 0; i < net->count; i += 1)
                for (int j = 0; j < MAX_OUT; j += 1)
                    if (net->nodes[i]->out[j] == n) {
                        c += 1;
                        break;
                    }
            return c;
        }

        struct NetNode *net_send(struct Network *net, int max) {
            struct NetNode *p = net->start;
            int vus = 0;
            while (p != NULL) {
                vus += 1;
                if (vus > max)
                    return NULL;
                if (p->out[0] == NULL)
                    return p;
                p = p->out[0];
            }
            return NULL;
        }

        int net_loop(struct Network *net) {
            struct NetNode *vus[MAX_NODES + 1];
            int nb = 0;
            for (struct NetNode *p = net->start; p != NULL; p = p->out[0]) {
                for (int i = 0; i < nb; i += 1)
                    if (vus[i] == p)
                        return 1;
                if (nb == MAX_NODES + 1)
                    return 1;
                vus[nb] = p;
                nb += 1;
            }
            return 0;
        }
        '''),
        headers={"reseau.h": RESEAU_H},
        protos=r'''
        int net_count(struct Network *net, enum netkind k);
        int net_node_id(struct Network *net, struct NetNode *n);
        int net_to_node(struct Network *net, struct NetNode *n);
        struct NetNode *net_send(struct Network *net, int max);
        int net_loop(struct Network *net);
        static struct NetNode N[6];
        static void mk(int i, enum netkind k) { N[i].id = i; N[i].name = "n"; N[i].kind = k;
            N[i].out[0] = N[i].out[1] = N[i].out[2] = NULL; }
        ''',
        tests=r'''
        struct Network net;
        net.count = 0; net.start = NULL;
        mk(0, ROUTER); mk(1, SWITCH); mk(2, HOST); mk(3, HOST); mk(4, SERVER); mk(5, HOST);
        for (int i = 0; i < 5; i += 1) net.nodes[net.count++] = &N[i];
        net.start = &N[0];
        // 0 -> 1 -> 4 ; 0 -> 2 ; 1 -> 3 ; 2 -> 4
        N[0].out[0] = &N[1]; N[0].out[1] = &N[2];
        N[1].out[0] = &N[4]; N[1].out[1] = &N[3];
        N[2].out[0] = &N[4];
        section("net_count");
        CHECK_INT(net_count(&net, HOST), 2, "net_count(HOST)  (N[5] n'est pas dans le réseau)");
        CHECK_INT(net_count(&net, ROUTER), 1, "net_count(ROUTER)");
        CHECK_INT(net_count(&net, SERVER), 1, "net_count(SERVER)");
        section("net_node_id");
        CHECK_INT(net_node_id(&net, &N[3]), 3, "net_node_id(N3)");
        CHECK_INT(net_node_id(&net, &N[5]), -1, "net_node_id(N5) (absent)");
        section("net_to_node");
        CHECK_INT(net_to_node(&net, &N[4]), 2, "net_to_node(N4)  (depuis N1 et N2)");
        CHECK_INT(net_to_node(&net, &N[0]), 0, "net_to_node(N0)");
        section("net_send");
        CHECK_TRUE(net_send(&net, 10) == &N[4], "net_send : 0 -> 1 -> 4, s'arrête sur N4");
        CHECK_TRUE(net_send(&net, 2) == NULL, "net_send(max = 2) : 3 équipements traversés -> NULL");
        section("net_loop");
        CHECK_INT(net_loop(&net), 0, "net_loop : pas de boucle");
        N[4].out[0] = &N[1];
        CHECK_INT(net_loop(&net), 1, "net_loop après N4 -> N1 : boucle 1 -> 4 -> 1");
        CHECK_TRUE(net_send(&net, 10) == NULL, "net_send avec la boucle -> NULL");
        net.start = NULL;
        CHECK_TRUE(net_send(&net, 10) == NULL, "net_send sans start -> NULL");
        CHECK_INT(net_loop(&net), 0, "net_loop sans start -> 0");
        ''',
        indices=["net_count / net_node_id : une boucle de 0 à net->count - 1 sur net->nodes[i].",
                 "net_send : un pointeur p = net->start, et un compteur ; avance avec p = p->out[0].",
                 "net_loop : mémorise les équipements visités dans un tableau, et vérifie à chaque pas "
                 "si le nouvel équipement y est déjà."])

    prog("projet_calculatrice", "projets", "Mini-calculatrice", """
        calc.c reçoit une opération sous forme de trois arguments :  a op b
            ./calc 7 + 5  -> 12       ./calc 7 / 2  -> 3       ./calc 7 % 2 -> 1
            ./calc 6 x 7  -> 42  (x pour multiplier : * serait interprété par le shell)
        Erreurs (afficher le message et return 1) :
            mauvais nombre d'arguments      -> usage: ./calc a op b
            division ou modulo par zéro     -> erreur: division par zero
            opérateur inconnu               -> erreur: operateur inconnu
        """, 3, "calc.c",
        starter=r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        int main(int argc, char **argv) {
            // TODO
            return 0;
        }
        ''',
        solution=r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>

        int main(int argc, char **argv) {
            if (argc != 4) {
                printf("usage: ./calc a op b\n");
                return 1;
            }
            int a = atoi(argv[1]);
            int b = atoi(argv[3]);
            char *op = argv[2];
            if (strcmp(op, "+") == 0)
                printf("%d\n", a + b);
            else if (strcmp(op, "-") == 0)
                printf("%d\n", a - b);
            else if (strcmp(op, "x") == 0)
                printf("%d\n", a * b);
            else if (strcmp(op, "/") == 0 || strcmp(op, "%") == 0) {
                if (b == 0) {
                    printf("erreur: division par zero\n");
                    return 1;
                }
                if (op[0] == '/')
                    printf("%d\n", a / b);
                else
                    printf("%d\n", a % b);
            } else {
                printf("erreur: operateur inconnu\n");
                return 1;
            }
            return 0;
        }
        ''',
        tests=[("7 + 5", "12"), ("7 - 10", "-3"), ("6 x 7", "42"), ("7 / 2", "3"), ("7 % 2", "1"),
               ("1 / 0", "erreur: division par zero"), ("1 % 0", "erreur: division par zero"),
               ("1 ^ 2", "erreur: operateur inconnu"), ("1 +", "usage: ./calc a op b")],
        indices=["L'opérateur est la chaîne argv[2] : compare-la avec strcmp(argv[2], \"+\") == 0, ou "
                 "regarde son premier caractère argv[2][0] == '+'.",
                 "Vérifie b == 0 AVANT de diviser."])

    # ======================================================================
    # 15. Pièges classiques
    # ======================================================================
    fonc("pieges_bugs", "pieges", "Chasse aux bugs : pièges classiques", """
        pieges.c compile sans erreur mais chaque fonction contient un piège classique du C.
        Lance :verifier, comprends pourquoi les tests échouent et corrige (peu de caractères à chaque fois).
          moyenne(t, n)        moyenne exacte des n valeurs (double)
          dernier(t, n)        dernière valeur du tableau
          est_voyelle(c)       1 si c est une voyelle minuscule (a e i o u y)
          compte_negatifs(t,n) nombre de valeurs < 0
        """, 3, "pieges.c",
        starter=r'''
        double moyenne(int t[], int n) {
            int s = 0;
            for (int i = 0; i < n; i += 1)
                s += t[i];
            return s / n;
        }

        int dernier(int t[], int n) {
            return t[n];
        }

        int est_voyelle(char c) {
            if (c == 'a' || 'e' || 'i' || 'o' || 'u' || 'y')
                return 1;
            return 0;
        }

        int compte_negatifs(int t[], int n) {
            int c = 0;
            for (int i = 0; i < n; i += 1) {
                if (t[i] < 0)
                    c += 1;
                return c;
            }
            return c;
        }
        ''',
        solution=r'''
        double moyenne(int t[], int n) {
            int s = 0;
            for (int i = 0; i < n; i += 1)
                s += t[i];
            return (double)s / n;                // sinon division entière
        }

        int dernier(int t[], int n) {
            return t[n - 1];                     // la dernière case est n - 1
        }

        int est_voyelle(char c) {
            if (c == 'a' || c == 'e' || c == 'i' || c == 'o' || c == 'u' || c == 'y')
                return 1;
            return 0;
        }

        int compte_negatifs(int t[], int n) {
            int c = 0;
            for (int i = 0; i < n; i += 1) {
                if (t[i] < 0)
                    c += 1;
            }
            return c;                            // APRÈS la boucle, pas dedans
        }
        ''',
        protos="double moyenne(int t[], int n);\nint dernier(int t[], int n);\nint est_voyelle(char c);\n"
               "int compte_negatifs(int t[], int n);\nstruct piege { int t[3]; int apres; };",
        tests=r'''
        int t[] = {1, 2, 4};
        section("moyenne");
        CHECK_TRUE(moyenne(t, 3) > 2.33 && moyenne(t, 3) < 2.34, "moyenne({1,2,4}) == 2.333...");
        CHECK_TRUE(moyenne(t, 2) == 1.5, "moyenne({1,2}) == 1.5");
        section("dernier");
        struct piege p = { {5, 6, 7}, 99 };
        CHECK_INT(dernier(p.t, 3), 7, "dernier({5,6,7}, 3)");
        section("est_voyelle");
        CHECK_INT(est_voyelle('e'), 1, "est_voyelle('e')");
        CHECK_INT(est_voyelle('a'), 1, "est_voyelle('a')");
        CHECK_INT(est_voyelle('b'), 0, "est_voyelle('b')");
        CHECK_INT(est_voyelle('z'), 0, "est_voyelle('z')");
        section("compte_negatifs");
        int u[] = {-1, 5, -3, 0};
        CHECK_INT(compte_negatifs(u, 4), 2, "compte_negatifs({-1,5,-3,0})");
        int w[] = {2, -4, -6};
        CHECK_INT(compte_negatifs(w, 3), 2, "compte_negatifs({2,-4,-6})");
        CHECK_INT(compte_negatifs(t, 3), 0, "compte_negatifs({1,2,4})");
        ''',
        bug=True,
        indices=["moyenne : s / n est calculé entre deux int AVANT la conversion en double.",
                 "est_voyelle : (c == 'a' || 'e') se lit (c == 'a') || ('e') ; et 'e' vaut 101, donc vrai !",
                 "compte_negatifs : à quel moment la fonction rend-elle la main ? Combien de tours fait la boucle ?"])

    qcm("pieges_qcm_pointvirgule", "pieges", "Le ; de trop", """
        Qu'affiche ce code, compilé SANS -Werror ?
        """, 2,
        ["0 1 2 3 4", "5", "rien", "ça ne compile pas"],
        "b",
        code=r'''
        int i;
        for (i = 0; i < 5; i += 1);
            printf("%d ", i);
        ''',
        explication="Le ; après le for est une instruction vide : c'est elle qui est répétée 5 fois. Le printf "
                    "est exécuté une seule fois, après la boucle, quand i vaut 5. Bonne nouvelle : gcc -Wall "
                    "le signale (misleading indentation), donc -Werror le refuse.")

    qcm("pieges_qcm_sizeof_param", "pieges", "sizeof d'un paramètre tableau", """
        Qu'affiche ce programme (machine 64 bits) ?
        """, 3,
        ["40", "10", "8", "4"],
        "c",
        code=r'''
        #include <stdio.h>

        void f(int t[]) {
            printf("%zu\n", sizeof(t));
        }

        int main(void) {
            int t[10];
            f(t);
            return 0;
        }
        ''',
        explication="Dans f, int t[] est en réalité un int * : sizeof donne la taille d'un pointeur (8). "
                    "« On ne peut pas connaître la taille du tableau » (slide tableaux) : il faut la passer "
                    "en paramètre. (gcc -Wall prévient d'ailleurs avec -Wsizeof-array-argument.)")

    qcm("pieges_qcm_moins", "pieges", "Modulo négatif", """
        Pour tester si un int n est impair, quelles conditions sont correctes pour TOUS les n,
        y compris négatifs ?
        """, 2,
        ["n % 2 == 1", "n % 2 != 0", "n % 2 == -1 || n % 2 == 1", "n / 2 == 1"],
        "bc",
        explication="En C, le reste a le signe du dividende : -3 % 2 vaut -1. n % 2 == 1 rate donc les "
                    "impairs négatifs.")

    qcm("pieges_qcm_char_egal", "pieges", "Guillemets ou apostrophes", """
        char c = 'a';     Quelle comparaison est correcte ?
        """, 1,
        ["c == \"a\"", "c == 'a'", "strcmp(c, \"a\") == 0", "c = 'a'"],
        "b",
        explication="'a' est un caractère (le nombre 97) ; \"a\" est une chaîne (tableau {'a', 0}, donc une "
                    "adresse). Un char se compare avec ==, une chaîne avec strcmp.")

    qcm("pieges_qcm_init", "pieges", "Variable non initialisée", """
        Que vaut s à la fin ?
        """, 2,
        ["10", "on ne sait pas : s n'a jamais été initialisée, elle contient ce qui traînait en mémoire",
         "0, les variables valent 0 par défaut", "ça ne compile pas"],
        "b",
        code=r'''
        int s;
        for (int i = 1; i <= 4; i += 1)
            s += i;
        ''',
        explication="Une variable locale non initialisée a une valeur indéterminée. Toujours écrire int s = 0;. "
                    "(Seules les variables globales sont mises à 0 automatiquement.)")

    qcm("pieges_qcm_overflow_tab", "pieges", "Dépasser du tableau", """
        int t[5];
        for (int i = 0; i <= 5; i += 1) t[i] = 0;
        Que se passe-t-il ?
        """, 2,
        ["tout va bien", "le compilateur refuse", "on écrit dans t[5], qui n'existe pas : comportement indéfini "
         "(une autre variable écrasée, ou un plantage)", "le tableau s'agrandit tout seul"],
        "c",
        explication="i <= 5 fait 6 tours. Le C ne vérifie pas les bornes : il faut i < 5. valgrind ou "
                    "gcc -fsanitize=address détectent ce genre d'erreur.")

    qcm("pieges_qcm_retour_scanf", "pieges", "Les erreurs qui compilent", """
        Parmi ces erreurs, lesquelles sont REFUSÉES par gcc -Wall -Werror -std=c99 ?
        """, 3,
        ["if (a = b) ...", "une variable déclarée mais jamais utilisée",
         "lire t[10] dans un tableau de 10 cases", "oublier le & dans scanf(\"%d\", i) avec int i"],
        "abd",
        explication="-Wall prévient pour l'affectation dans un if, la variable inutilisée et le scanf dont le "
                    "type ne correspond pas (-Wformat). Le dépassement de tableau, lui, compile : c'est à toi "
                    "de faire attention.")
