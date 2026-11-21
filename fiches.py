"""Fiches de révision (résumés courts, d'après le cours « programmation C »)."""

FICHES = {
"compil": """\
gcc -Wall -Werror -std=c99 f.c -o f     puis ./f      (sans -o : a.out)
Erreur gcc : f.c:LIGNE:COLONNE: error: ...  -> corrige la PREMIÈRE ; « expected ';' » = ligne d'avant
#include <stdio.h> (printf, scanf)   <stdlib.h> (atoi, malloc, free)   <string.h> (strlen...)
int main(int argc, char **argv) { ... return 0; }
./prog 3 4 : argc = 3, argv[1] = "3" (chaîne !) -> atoi(argv[1]) ; tester argc AVANT argv[i]
printf("a=%d moitie=%d\\n", a, a / 2);   %d int  %f double (%.2f)  %c char  %s chaîne  %zu sizeof
7 / 2 = 3 (entre int)    7 % 2 = 1 (reste)    commentaires : // ligne   /* bloc */""",

"cond": """\
if (test) { ... } else if (test2) { ... } else { ... }      faux = 0, vrai = tout le reste
==  !=  <  >  <=  >=        = AFFECTE, == COMPARE  (if (a = 0) : bug, refusé par -Wall -Werror)
&& et   || ou   ! non       ((a > 0) && (a < 5))  ->  a dans ]0;5[
Intervalle : (a >= 10 && a <= 20), jamais 10 <= a <= 20
Pair : a % 2 == 0     impair : a % 2 != 0   (car -3 % 2 vaut -1)""",

"boucles": """\
while (cond) { ... }                 tant que ; quelque chose doit changer dedans !
for (int i = 0; i < n; i += 1) { }   n tours, i de 0 à n-1 ; i n'existe que dans le for
for (int i = n; i >= 0; i -= 1)      à rebours
Chiffres : x % 10 = dernier chiffre, x / 10 l'enlève (cas 0 et négatifs à part)
Boucles imbriquées : l'intérieure fait tous ses tours à chaque tour de l'extérieure
Programme bloqué = boucle infinie -> Ctrl+C""",

"fonctions": """\
int greater(int a, int b) { if (a > b) return a; return b; }      void print(int a) { ... }
Déclarer avant d'utiliser : écrire la fonction au-dessus, ou mettre le prototype  int greater(int a, int b);
Paramètres = COPIES : modifier x dans f ne change pas la variable de l'appelant (-> pointeurs)
Récursif : cas de base + appel sur plus petit :  fact(n) = n <= 1 ? 1 : n * fact(n - 1)
Pas de main dans un fichier de fonctions testé par CQuest ; :essai pour un main de test""",

"tableaux": """\
int a[20];   int b[3] = {0, 2, 4};    indices 0..taille-1, AUCUN contrôle de dépassement
Fonction : int f(int t[], int n) ou int f(int *t, int n) ; la taille n doit être passée
Modifier t[i] dans f modifie le tableau de l'appelant
Interdit : renvoyer un tableau local, t = u (copier case par case)
sizeof(t) / sizeof(t[0]) = nombre de cases (seulement là où t est déclaré)
Min : m = t[0]; for (i = 1; i < n; i++) if (t[i] < m) m = t[i];
Échange : tmp = t[i]; t[i] = t[j]; t[j] = tmp;""",

"types": """\
char 1 (-128..127, unsigned 0..255)   int 4   float 4   double 8   pointeur 8   (sizeof)
int t[4] -> sizeof(t) = 16       sizeof("abc") = 4 (avec le 0)
Bits : bit i vaut 2^i ;  0100 1101 = 64+8+4+1 = 77
-5 sur 8 bits : +5 = 0000 0101 -> inverser 1111 1010 -> +1 = 1111 1011
char 127 + 1 = -128 (débordement)
0x32 = 50   2.5 double   3.14f float   'a' = 97, 'A' = 65, '0' = 48 (man ascii)
double d = 7 / 2; -> 3.0      7.0 / 2 ou (double)7 / 2 -> 3.5
(c >> i) & 1 = bit i de c""",

"chaines": """\
"hello" = {'h','e','l','l','o','\\0'} -> char s[6] ou char s[] = "hello"
Parcours : for (int i = 0; s[i] != '\\0'; i += 1)
string.h : strlen(s)  strcmp(a, b) (0 si égales)  strcpy(dst, src)       stdlib.h : atoi(s)
JAMAIS a == b pour comparer des chaînes (compare les adresses)
'a' (char, nombre 97) ≠ "a" (chaîne, adresse)
Majuscule : if (c >= 'a' && c <= 'z') c = c - 'a' + 'A';
Fabriquer une chaîne : toujours écrire le '\\0' final ; taille = longueur + 1""",

"enum": """\
enum couleur { TREFLE, CARREAU, COEUR, PIQUE };    -> 0, 1, 2, 3   (le ; final !)
enum couleur carte = COEUR;   int i = carte;  -> 2
enum { A, B = 5, C };  -> C = 6
switch (c) { case COEUR: ...; break; default: ...; }    (sans break : on continue au case suivant)
Calculs possibles : (j + 1) % 7 pour le jour suivant""",

"pointeurs": """\
int *p;  p contient une adresse      &i : adresse de i (type int *)      *p : valeur pointée
int *p = NULL;   adresse invalide, *p -> Segmentation fault
Modifier dans une fonction :  void f(int *x) { *x = 5; }   appel f(&a);
int *p = t;   p[i] == *(p + i) == t[i] ;  p + 1 avance d'une case
Différence de pointeurs = nombre de cases : len = p - s
Renvoyer un pointeur : return t + i;  ou  return NULL;  (absent)
Tous les pointeurs font 8 octets""",

"struct": """\
struct point { int x; int y; };          struct point p;  p.x = 5;
struct point a = {.x = 5, .y = 10};   struct point b = a;  (copie)
struct point *ptr = &a;   ptr->x = 20;  ==  (*ptr).x = 20
Passée par valeur = copie : pour modifier, void f(struct point *p) { p->x = ...; }  f(&a);
Tableau : struct point t[10];  t[i].x
Champ char nom[20] : strcpy(p->nom, "...")  (pas de =)
Initialiser TOUS les champs (pointeurs à NULL)""",

"entrees": """\
scanf("%d", &i);   scanf("%d %d", &i, &j);   scanf("%s", buffer);  (un mot, sans &)
while (scanf("%d", &x) == 1) { ... }   lit jusqu'à la fin (Ctrl+D au clavier)
#define BSIZE 1024        char buffer[BSIZE];
fgets(buffer, BSIZE, stdin)   une ligne, '\\n' compris, NULL à la fin ; sécurisé (taille donnée)
atoi(buffer)  atof(buffer)
Globale : déclarée hors des fonctions, vit tout le programme, vaut 0 au départ
Tester : echo "3 7 1" | ./prog""",

"malloc": """\
int *t = malloc(n * sizeof(int));   ...   free(t);       (#include <stdlib.h>)
Chaîne de longueur L : malloc(L + 1)  (le '\\0')
Pile : locales et paramètres (disparaissent en fin de fonction) ; tas : malloc (jusqu'au free)
Interdit : renvoyer l'adresse d'une locale, utiliser après free, free deux fois
valgrind --leak-check=full ./prog :
  Invalid read/write = hors zone ; definitely lost = fuite ; regarde « at ... fichier.c:ligne »""",

"listes": """\
struct cell { int value; struct cell *next; };    dernière cellule : next = NULL
for (struct cell *p = l; p != NULL; p = p->next) ... p->value ...
Insérer b après a : b->next = a->next; a->next = b;   (dans cet ordre)
Retirer le suivant de p : p->next = p->next->next;
Inverser : prec = NULL ; tant que cour : suiv = cour->next; cour->next = prec; prec = cour; cour = suiv;
Nouvelle cellule : c = malloc(sizeof(struct cell)); c->value = v; c->next = NULL;
Libérer : while (l) { suiv = l->next; free(l); l = suiv; }
Une fonction qui peut changer la tête la renvoie""",

"projets": """\
Ordre : structures / enum -> création (malloc + init) -> connexions -> parcours
César : d = ((d % 26) + 26) % 26;  'a' + (c - 'a' + d) % 26
Trois variantes : _i sur place, _s dans un paramètre out, _d malloc + return
Réseau : node_create (malloc, out[i] = NULL), node_connect (1re case libre),
         net_add (nodes[count++] = n), parcours via out[0], boucle = équipement déjà vu""",

"pieges": """\
if (a = b)  ->  ==        if (...);  for (...);  -> le ; vide la boucle/condition
(c == 'a' || 'e') -> (c == 'a' || c == 'e')        10 <= a <= 20 -> (a >= 10 && a <= 20)
int / int -> entier        -3 % 2 == -1        variable locale non initialisée
t[n] hors tableau (i < n, pas i <= n)        sizeof(t) d'un paramètre = 8
"abc" == "abc" compare des adresses -> strcmp      'a' ≠ "a"
malloc(strlen(s)) -> + 1      return &local      use after free      scanf sans &""",
}
