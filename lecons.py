"""Cours du mode Apprentissage : pour chaque thème, des cartes (explication, exemples de code
qu'on compile et lance d'un appui sur Entrée, ou qu'on modifie avec e), puis une méthode.

Un exemple est soit du code (str), soit (code, remarque), soit un dict
{"code", "note", "args", "stdin"}. Un code sans main est placé dans un main automatiquement
(avec stdio.h, stdlib.h et string.h).
"""

PROGRAMME = [
    ("Étape 1 : les bases", "≈ 2 h", ["compil", "cond", "boucles"], None),
    ("Étape 2 : fonctions", "≈ 2 h", ["fonctions", "tableaux", "types"], None),
    ("Étape 3 : chaînes, pointeurs", "≈ 2 h 30", ["chaines", "enum", "pointeurs"], None),
    ("Étape 4 : mémoire", "≈ 2 h 30", ["struct", "entrees", "malloc", "listes"], None),
    ("Étape 5 : examen", "≈ 2 h", ["projets", "pieges"], "puis Examen blanc (1 h) et Mes erreurs"),
]

LECONS = {}

# ==========================================================================
LECONS["compil"] = {
    "cartes": [
        {"titre": "Un programme C, de bout en bout",
         "texte": """\
Un programme C est un fichier texte (.c) qu'on COMPILE pour obtenir un exécutable :
    gcc -Wall -Werror -std=c99 forma.c -o forma      puis      ./forma
-Wall      active les avertissements          -Werror   les transforme en erreurs
-std=c99   la version du langage              -o forma  le nom de l'exécutable (sinon a.out)
Le programme commence toujours par la fonction main. return 0; = « tout s'est bien passé ».""",
         "exemples": [(r'''#include <stdio.h>

int main(void) {
    printf("Bonjour !\n");
    return 0;
}''', "#include <stdio.h> donne accès à printf. \\n = retour à la ligne.")],
         "astuce": "Bien lire les messages du compilateur ! Toujours corriger la PREMIÈRE erreur d'abord."},
        {"titre": "Lire une erreur de compilation",
         "texte": """\
Un message gcc :   forma.c:5:20: error: 'nivaeu' undeclared
    fichier forma.c, ligne 5, colonne 20, puis l'explication.
« expected ';' before ... » : le ; manque à la fin de l'instruction PRÉCÉDENTE.
Une erreur peut en provoquer dix autres : corrige la première et recompile.""",
         "exemples": [(r'''int niveau = 1
printf("%d\n", nivaeu);''', "Deux erreurs : le ; manquant et le nom mal tapé. Tape e pour les corriger.")]},
        {"titre": "Variables et printf",
         "texte": """\
Déclarer :   type nom = valeur;     (int i = 0;   double d = 2.5;   char c = 'a';)
printf affiche un format où chaque % est remplacé par une valeur, dans l'ordre :
    %d entier    %f réel (%.2f : 2 décimales)    %c caractère    %s chaîne    %zu un sizeof
Entre deux int, / est une division ENTIÈRE et % donne le reste.""",
         "exemples": [r'''int a = 7;
printf("a = %d ; a/2 = %d ; reste = %d\n", a, a / 2, a % 2);
printf("en reel : %.2f\n", a / 2.0);''']},
        {"titre": "argc, argv et atoi",
         "texte": """\
int main(int argc, char **argv) reçoit les mots de la ligne de commande :
    ./prog 3 4   ->  argc = 3, argv[0] = "./prog", argv[1] = "3", argv[2] = "4"
Ce sont des CHAÎNES : atoi(argv[1]) les convertit en int (#include <stdlib.h>).
Vérifie toujours argc avant de lire argv[i] : sinon plantage.""",
         "exemples": [{"code": r'''#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv) {
    printf("argc = %d\n", argc);
    for (int i = 0; i < argc; i += 1)
        printf("argv[%d] = \"%s\"\n", i, argv[i]);
    if (argc == 3)
        printf("somme = %d\n", atoi(argv[1]) + atoi(argv[2]));
    return 0;
}''', "args": "3 4", "note": "Avec e, change le code ; les arguments passés sont 3 et 4."}]},
    ],
    "methode": """\
- Commence par recopier la squelette : #include, int main(int argc, char **argv) { ... return 0; }
- Programme avec arguments : 1) tester argc, 2) atoi, 3) calculer, 4) printf.
- Compile souvent (:verifier ou gcc -Wall ...) : une erreur à la fois, c'est plus facile.
- Le format de sortie doit être EXACT : espaces, majuscules, accents, \\n final.""",
}

LECONS["cond"] = {
    "cartes": [
        {"titre": "if / else",
         "texte": """\
if (test) { ... } else { ... }      Le test vaut faux s'il vaut 0, vrai sinon.
Comparaisons :  ==  !=  <  >  <=  >=        (== compare, = affecte !)
Plusieurs cas :  if (...) { } else if (...) { } else { }
Sans accolades, seule l'instruction suivante est concernée.""",
         "exemples": [r'''int a = 15;
if (a % 5 == 0)
    printf("%d est multiple de 5\n", a);
else
    printf("%d n'est pas multiple de 5\n", a);''']},
        {"titre": "Combiner des tests",
         "texte": """\
&&  et (les deux)      ||  ou (au moins un)      !  non
((a > 0) && (a < 5))   a est dans ]0 ; 5[
((a % 2 == 0) || (a == 5))   a est pair ou vaut 5
Un test vaut 1 (vrai) ou 0 (faux) : on peut l'afficher avec %d.""",
         "exemples": [r'''int a = 7;
printf("%d %d %d\n", (a > 0) && (a < 5), (a % 2 == 0) || (a == 7), !(a > 3));'''],
         "astuce": "10 <= a <= 20 ne fait PAS ce qu'on croit : écris (a >= 10 && a <= 20)."},
        {"titre": "Le piège = au lieu de ==",
         "texte": """\
if (a = 0) AFFECTE 0 à a, puis teste 0 : toujours faux, et a est écrasé.
gcc -Wall te prévient (suggest parentheses around assignment) et -Werror refuse de compiler.
Pareil pour les négatifs : -3 % 2 vaut -1 en C. Pour « impair », teste a % 2 != 0.""",
         "exemples": [(r'''int a = -3;
printf("a %% 2 = %d\n", a % 2);
if (a % 2 == 1) printf("impair (test 1)\n");
if (a % 2 != 0) printf("impair (test 2)\n");''', "Seul le test 2 détecte que -3 est impair. (%% affiche un %.)")]},
    ],
    "methode": """\
- Liste tous les cas sur papier (positif, négatif, zéro, égalité) avant d'écrire les if.
- Un cas = une branche : if / else if / else couvre tout sans oubli.
- Relis chaque test : == (et pas =), && et || bien parenthésés, bornes < ou <= ?""",
}

LECONS["boucles"] = {
    "cartes": [
        {"titre": "while",
         "texte": """\
while (condition) { ... }   répète tant que la condition est vraie.
Il faut que quelque chose CHANGE dans la boucle, sinon elle ne s'arrête jamais (Ctrl+C).
Exemple du cours : multiplier a par b en additionnant b fois.""",
         "exemples": [r'''int r = 0;
int a = 3;
int b = 4;
while (b > 0) {
    r += a;    // r = r + a
    b -= 1;    // ou b--
}
printf("%d\n", r);''']},
        {"titre": "for",
         "texte": """\
for (init; condition; pas) { ... }  =  init; while (condition) { ...; pas; }
for (int i = 0; i < n; i += 1)      i n'existe que dans la boucle.
Compte à rebours : for (int i = n; i >= 0; i -= 1)""",
         "exemples": [r'''for (int i = 1; i <= 5; i += 1)
    printf("%d au carre = %d\n", i, i * i);''']},
        {"titre": "Boucles imbriquées",
         "texte": """\
Une boucle dans une boucle : la boucle intérieure fait TOUS ses tours à chaque tour de l'extérieure.
Typique pour dessiner (lignes / colonnes) ou comparer tous les couples d'éléments.""",
         "exemples": [r'''for (int i = 1; i <= 4; i += 1) {
    for (int j = 0; j < i; j += 1)
        printf("*");
    printf("\n");
}''']},
        {"titre": "Découper un nombre en chiffres",
         "texte": """\
x % 10 donne le dernier chiffre, x / 10 l'enlève. En boucle, on parcourt tous les chiffres :
    while (x > 0) { chiffre = x % 10; x = x / 10; }
Attention aux cas 0 (la boucle ne tourne pas) et négatifs (rends x positif avant).""",
         "exemples": [r'''int x = 1023;
int n = 0;
while (x > 0) {
    printf("chiffre : %d\n", x % 10);
    x = x / 10;
    n += 1;
}
printf("%d chiffres\n", n);''']},
    ],
    "methode": """\
- Avant d'écrire la boucle : que vaut la variable au début, quand s'arrête-t-on, qu'est-ce qui change ?
- Déroule les 2 premiers tours et le dernier à la main (tableau de valeurs sur papier).
- for quand on connaît le nombre de tours, while quand on attend une condition.
- Programme bloqué ? Boucle infinie : vérifie que la variable du test change bien.""",
}

LECONS["fonctions"] = {
    "cartes": [
        {"titre": "Écrire une fonction",
         "texte": """\
type_retour nom(type param1, type param2) { ...; return valeur; }
void = ne renvoie rien. Une fonction doit être déclarée AVANT d'être utilisée :
soit on l'écrit au-dessus de main, soit on met son prototype en haut :  int greater(int a, int b);""",
         "exemples": [r'''#include <stdio.h>

int greater(int a, int b) {
    if (a > b)
        return a;
    return b;
}

void print(int a) {
    printf("%d\n", a);
}

int main(void) {
    print(greater(3, 8));
    return 0;
}''']},
        {"titre": "Les paramètres sont des copies",
         "texte": """\
Quand on appelle f(a), f reçoit une COPIE de la valeur de a. Modifier le paramètre dans f
ne change rien pour l'appelant. (Pour modifier, il faudra passer l'adresse : thème pointeurs.)""",
         "exemples": [r'''#include <stdio.h>

void f(int x) {
    x = 5;
    printf("dans f : x = %d\n", x);
}

int main(void) {
    int a = 1;
    f(a);
    printf("dans main : a = %d\n", a);
    return 0;
}''']},
        {"titre": "Récursivité",
         "texte": """\
Une fonction récursive s'appelle elle-même sur un problème plus petit.
Il faut TOUJOURS un cas de base qui s'arrête, sinon la pile déborde (Segmentation fault).
    fact(n) = n * fact(n - 1)    et    fact(0) = 1""",
         "exemples": [r'''#include <stdio.h>

int fact(int n) {
    if (n <= 1)
        return 1;
    return n * fact(n - 1);
}

int main(void) {
    for (int i = 0; i <= 6; i += 1)
        printf("%d! = %d\n", i, fact(i));
    return 0;
}''']},
        {"titre": "Tester ses fonctions",
         "texte": """\
Dans CQuest, les missions « fonctions » n'ont pas de main : le jeu fournit le sien.
Pour tester toi-même, :essai crée essai.c avec un main et les prototypes, puis :
    gcc -Wall -std=c99 essai.c tonfichier.c -o essai && ./essai""",
         "exemples": [],
         "astuce": "Ne mets pas de main dans un fichier de fonctions : sinon « multiple definition of main »."},
    ],
    "methode": """\
- Lis bien la signature demandée (nom, types, ordre des paramètres) : le main de test l'appelle telle quelle.
- Une fonction = un calcul : pas de printf dedans sauf si on le demande, on RENVOIE le résultat.
- Teste les cas limites : 0, négatifs, égalité, un seul élément.
- Récursif : écris d'abord le cas de base, puis l'appel sur un problème plus petit.""",
}

LECONS["tableaux"] = {
    "cartes": [
        {"titre": "Déclarer et parcourir",
         "texte": """\
int a[20];              20 cases, de a[0] à a[19], valeurs au hasard au départ
int b[3] = {0, 2, 4};   initialisé
Parcours :  for (int i = 0; i < n; i += 1) ... t[i] ...
Le C ne vérifie PAS les bornes : t[20] lit/écrit n'importe où.""",
         "exemples": [r'''int t[5] = {4, -2, 7, 1, 10};
int s = 0;
for (int i = 0; i < 5; i += 1)
    s += t[i];
printf("somme = %d\n", s);''']},
        {"titre": "Tableaux et fonctions",
         "texte": """\
int f(int t[], int n)   (ou int f(int *t, int n))  : la fonction reçoit l'ADRESSE du tableau.
- Elle ne connaît pas sa taille : on passe n en plus.
- Modifier t[0] dans f modifie le tableau de l'appelant.
- On ne peut pas renvoyer un tableau de la pile, ni faire t = u : on copie case par case.""",
         "exemples": [r'''#include <stdio.h>

void double_tout(int t[], int n) {
    for (int i = 0; i < n; i += 1)
        t[i] = 2 * t[i];
}

int main(void) {
    int t[3] = {1, 2, 3};
    double_tout(t, 3);
    printf("%d %d %d\n", t[0], t[1], t[2]);
    return 0;
}''']},
        {"titre": "Chercher le minimum (exemple du cours)",
         "texte": """\
Schéma classique : un candidat initialisé avec la première case, puis on compare les autres.
On peut garder la VALEUR (m = t[i]) ou l'INDICE (im = i) du meilleur.""",
         "exemples": [r'''#include <stdio.h>

int min(int t[], int l) {
    if (l == 0)
        return -1;
    int m = t[0];
    for (int i = 1; i < l; i += 1)
        if (t[i] < m)
            m = t[i];
    return m;
}

int main(void) {
    int t[] = {5, 3, 9, -2, 4};
    printf("%d\n", min(t, 5));
    return 0;
}''']},
        {"titre": "Trier",
         "texte": """\
Tri par sélection : pour chaque i, cherche le plus petit entre i et n - 1, puis échange-le avec t[i].
Échanger deux cases : int tmp = t[i]; t[i] = t[m]; t[m] = tmp;""",
         "exemples": [r'''int t[] = {5, -1, 8, 3, 0};
int n = 5;
for (int i = 0; i < n - 1; i += 1) {
    int m = i;
    for (int j = i + 1; j < n; j += 1)
        if (t[j] < t[m])
            m = j;
    int tmp = t[i];
    t[i] = t[m];
    t[m] = tmp;
}
for (int i = 0; i < n; i += 1)
    printf("%d ", t[i]);
printf("\n");''']},
    ],
    "methode": """\
- Dessine le tableau avec ses indices (0 à n-1) et suis la boucle à la main.
- Condition de boucle : i < n (jamais i <= n).
- Minimum / maximum : initialise avec t[0], pas avec 0.
- Tableau vide (n == 0) : que doit renvoyer la fonction ? Pense-y en premier.""",
}

LECONS["types"] = {
    "cartes": [
        {"titre": "Les types simples et sizeof",
         "texte": """\
char 1 octet (-128..127)   int 4 octets (au moins 2)   float 4   double 8   pointeur 8 (64 bits)
Derrière chaque type : une quantité de mémoire et une interprétation.
sizeof(type) ou sizeof(variable) donne le nombre d'octets ; pour int t[4], sizeof(t) = 16.""",
         "exemples": [r'''int t[4];
printf("char %zu, int %zu, double %zu, int* %zu, t %zu\n",
       sizeof(char), sizeof(int), sizeof(double), sizeof(int *), sizeof(t));''']},
        {"titre": "Le binaire",
         "texte": """\
Un octet = 8 bits. Le bit i vaut 2^i :  0100 1101 = 64 + 8 + 4 + 1 = 77
Signé (complément à deux) : -5 = inverser les bits de +5 (0000 0101 -> 1111 1010), puis +1 = 1111 1011.
Un char signé va de -128 à 127 : 127 + 1 « déborde » et donne -128.""",
         "exemples": [r'''unsigned char c = 77;
for (int i = 7; i >= 0; i -= 1)
    printf("%d", (c >> i) & 1);
printf(" = %d\n", c);
char d = 127;
d = d + 1;
printf("127 + 1 dans un char : %d\n", d);''']},
        {"titre": "Valeurs et caractères",
         "texte": """\
12 est un int, 0x32 un int en hexadécimal (= 50), 2.5 un double, 3.14f un float.
'a' est un int : son code ASCII (97). 'a' + 1 = 98 = 'b'.  (man ascii)
"abc" est un tableau de 4 char : 97, 98, 99 et 0.""",
         "exemples": [r'''char x = 'a' + 1;
printf("%c %d %d\n", x, x, 0x32);
printf("sizeof(\"abc\") = %zu\n", sizeof("abc"));''']},
        {"titre": "Conversions : int / int",
         "texte": """\
Le type du calcul dépend des opérandes : 7 / 2 (deux int) = 3, même si on range le résultat dans un double.
Pour une division réelle : 7.0 / 2, ou (double)7 / 2.""",
         "exemples": [r'''double d1 = 7 / 2;
double d2 = 7.0 / 2;
double d3 = (double)7 / 2;
printf("%.1f %.1f %.1f\n", d1, d2, d3);''']},
    ],
    "methode": """\
- Question « que vaut... » : n'hésite pas à écrire 3 lignes de code et à les lancer (:essayer).
- Binaire -> décimal : additionne les puissances de 2 des bits à 1.
- Décimal -> binaire : divise par 2 et note les restes (ou soustrais 128, 64, 32...).
- Méfie-toi de int / int et des débordements de char.""",
}

LECONS["chaines"] = {
    "cartes": [
        {"titre": "Une chaîne = un tableau de char terminé par 0",
         "texte": """\
"hello" = { 'h', 'e', 'l', 'l', 'o', 0 }   (le 0 s'écrit aussi '\\0')
char s[6] = "hello";  ou  char s[] = "hello";  (la taille est calculée, 0 compris)
On la passe à une fonction en char * ; printf("%s", s) l'affiche jusqu'au 0.""",
         "exemples": [r'''char s[] = "hello";
for (int i = 0; s[i] != '\0'; i += 1)
    printf("s[%d] = '%c' (%d)\n", i, s[i], s[i]);
printf("%s\n", s);''']},
        {"titre": "string.h",
         "texte": """\
strlen(s)          longueur (sans le 0)
strcmp(a, b)       0 si égales, < 0 si a avant b, > 0 sinon (JAMAIS a == b)
strcpy(dst, src)   copie src dans dst (dst doit être assez grand)
atoi(s)            "42" -> 42 (stdlib.h)""",
         "exemples": [r'''char a[20] = "chat";
char b[20];
strcpy(b, a);
printf("%zu %d %d\n", strlen(a), strcmp(a, b), strcmp("abc", "abd"));
printf("a == b ? %d (compare les adresses !)\n", a == b);''']},
        {"titre": "Modifier une chaîne caractère par caractère",
         "texte": """\
Un char est un nombre : on peut tester  s[i] >= 'a' && s[i] <= 'z'  et calculer  s[i] - 'a' + 'A'.
Attention : char *s = "hello" pointe sur une chaîne CONSTANTE (non modifiable) ;
char s[] = "hello" est une copie modifiable.""",
         "exemples": [r'''char s[] = "Hello World 42";
for (int i = 0; s[i] != '\0'; i += 1)
    if (s[i] >= 'a' && s[i] <= 'z')
        s[i] = s[i] - 'a' + 'A';
printf("%s\n", s);''']},
    ],
    "methode": """\
- Parcours type : for (int i = 0; s[i] != '\\0'; i += 1).
- Quand tu FABRIQUES une chaîne, n'oublie jamais d'écrire le '\\0' final.
- Taille d'un tableau pour une chaîne de n lettres : n + 1.
- Comparer : strcmp(a, b) == 0 ; copier : strcpy ou une boucle.""",
}

LECONS["enum"] = {
    "cartes": [
        {"titre": "enum : des constantes nommées",
         "texte": """\
enum couleur { TREFLE, CARREAU, COEUR, PIQUE };    (numérotées 0, 1, 2, 3)
enum couleur carte = COEUR;     int i = carte;  -> 2
On peut imposer des valeurs : enum { A, B = 5, C };  -> C vaut 6.
Utile pour des constantes thématiques au lieu de nombres magiques.""",
         "exemples": [r'''#include <stdio.h>

enum couleur { TREFLE, CARREAU, COEUR, PIQUE };

int main(void) {
    enum couleur carte = COEUR;
    printf("COEUR vaut %d\n", carte);
    for (enum couleur c = TREFLE; c <= PIQUE; c += 1)
        printf("%d ", c);
    printf("\n");
    return 0;
}''']},
        {"titre": "switch sur un enum",
         "texte": """\
switch (c) { case TREFLE: ...; break; case COEUR: ...; break; default: ...; }
Sans break, l'exécution continue dans le case suivant. Un return termine aussi.""",
         "exemples": [r'''#include <stdio.h>

enum couleur { TREFLE, CARREAU, COEUR, PIQUE };

const char *nom(enum couleur c) {
    switch (c) {
    case TREFLE: return "trefle";
    case CARREAU: return "carreau";
    case COEUR: return "coeur";
    case PIQUE: return "pique";
    }
    return "?";
}

int main(void) {
    printf("%s %s\n", nom(COEUR), nom(PIQUE));
    return 0;
}''']},
    ],
    "methode": """\
- Un enum = des int : on peut faire des calculs ((j + 1) % 7) et des comparaisons.
- Pour convertir en texte : switch avec un return par case, ou un tableau de chaînes indexé par l'enum.
- N'oublie pas le ; après l'accolade fermante de la définition.""",
}

LECONS["pointeurs"] = {
    "cartes": [
        {"titre": "Une adresse dans une variable",
         "texte": """\
int *p;   p contient une ADRESSE ; à cette adresse, on lit sizeof(int) octets comme un int.
&i     l'adresse de i (type int *)        *p    la valeur pointée (lire ou écrire)
NULL   adresse invalide (pointeur « vide »). Tous les pointeurs font 8 octets.""",
         "exemples": [r'''int i = 5;
int *p = &i;
printf("i = %d, *p = %d, adresse = %p\n", i, *p, (void *)p);
*p = 10;
printf("apres *p = 10 : i = %d\n", i);''']},
        {"titre": "Passage par adresse",
         "texte": """\
Pour qu'une fonction modifie une variable de l'appelant, on lui passe son adresse :
    void echange(int *a, int *b) { int tmp = *a; *a = *b; *b = tmp; }      echange(&x, &y);
C'est aussi comme ça qu'on « renvoie » plusieurs résultats (et c'est pour ça que scanf veut &x).""",
         "exemples": [r'''#include <stdio.h>

void echange(int *a, int *b) {
    int tmp = *a;
    *a = *b;
    *b = tmp;
}

int main(void) {
    int x = 1, y = 2;
    echange(&x, &y);
    printf("x = %d, y = %d\n", x, y);
    return 0;
}''']},
        {"titre": "Pointeurs et tableaux",
         "texte": """\
Un tableau utilisé dans une expression devient l'adresse de sa première case : int *p = t;
p[i] et *(p + i) désignent t[i]. p + 1 avance d'UNE CASE (4 octets pour un int).
Pas de contrôle de dépassement !""",
         "exemples": [r'''int t[5] = {10, 20, 30, 40, 50};
int *p = t;
int *q = p + 3;
printf("%d %d %d %d\n", p[1], *(p + 2), *q, *(q - 1));
for (int *i = t; i < t + 5; i += 1)
    printf("%d ", *i);
printf("\n");''']},
        {"titre": "Parcourir une chaîne avec un pointeur",
         "texte": """\
On avance un pointeur jusqu'au '\\0' ; la différence de deux pointeurs = nombre de cases entre eux.
Une fonction peut renvoyer un pointeur vers une case trouvée (ou NULL si absent).""",
         "exemples": [r'''#include <stdio.h>
#include <stdlib.h>

int len(char *string) {
    char *p = string;
    while (*p != '\0')
        p += 1;
    return p - string;
}

int *find(int *t, int n, int v) {
    for (int i = 0; i < n; i += 1)
        if (t[i] == v)
            return t + i;
    return NULL;
}

int main(void) {
    int t[] = {4, 8, 15, 16};
    printf("%d\n", len("bonjour"));
    int *r = find(t, 4, 15);
    if (r != NULL)
        printf("trouve a l'indice %d\n", (int)(r - t));
    return 0;
}''']},
    ],
    "methode": """\
- Dessine des boîtes : une pour la variable, une pour le pointeur avec une flèche vers la variable.
- int *p : « p est un pointeur » ; *p dans une expression : « la valeur pointée ».
- Avant *p, demande-toi : p pointe-t-il vers quelque chose de valide (pas NULL, pas libéré) ?
- Segmentation fault = presque toujours un pointeur invalide ou un dépassement de tableau.""",
}

LECONS["struct"] = {
    "cartes": [
        {"titre": "Créer un type",
         "texte": """\
struct point { int x; int y; };      (le ; final !)
struct point p;  p.x = 5;  p.y = 10;
struct point a = {.x = 5, .y = 10};  struct point b = a;  (copie de tous les champs)""",
         "exemples": [r'''#include <stdio.h>

struct point {
    int x;
    int y;
};

void print_point(struct point a) {
    printf("(%d;%d)\n", a.x, a.y);
}

int main(void) {
    struct point p = {.x = 5, .y = 10};
    struct point q = p;
    q.x = 0;
    print_point(p);
    print_point(q);
    return 0;
}''']},
        {"titre": "Pointeur vers une struct : ->",
         "texte": """\
struct point *ptr = &x;    ptr->x = 20;   (raccourci de (*ptr).x = 20)
Une struct passée par valeur est COPIÉE : pour la modifier dans une fonction, passe son adresse.
C'est aussi plus efficace pour les grosses struct.""",
         "exemples": [r'''#include <stdio.h>

struct point { int x; int y; };

void point_init(struct point *p, int x, int y) {
    p->x = x;
    p->y = y;
}

int main(void) {
    struct point b;
    point_init(&b, 4, 6);
    printf("(%d;%d)\n", b.x, b.y);
    return 0;
}''']},
        {"titre": "Tableaux de struct, struct dans des struct",
         "texte": """\
struct point t[10];   t[i].x = i;
Une struct peut contenir des tableaux (char first[20]), des enum, d'autres struct, des pointeurs
(struct cell *next : la base des listes chaînées). Il faut initialiser TOUS les champs à la création.""",
         "exemples": [r'''#include <stdio.h>
#include <string.h>

struct person {
    char first[20];
    char last[20];
};

int main(void) {
    struct person t[2];
    strcpy(t[0].first, "Ada");
    strcpy(t[0].last, "Lovelace");
    strcpy(t[1].first, "Alan");
    strcpy(t[1].last, "Turing");
    for (int i = 0; i < 2; i += 1)
        printf("%s %s\n", t[i].first, t[i].last);
    return 0;
}''']},
    ],
    "methode": """\
- . pour une struct, -> pour un pointeur vers une struct. En cas de doute, regarde le type de la variable.
- Fonction qui modifie une struct : paramètre struct X *p, appel f(&s).
- Champ tableau de char : on le remplit avec strcpy, pas avec =.""",
}

LECONS["entrees"] = {
    "cartes": [
        {"titre": "scanf",
         "texte": """\
scanf("%d", &i);   lit un entier (il faut l'ADRESSE de i)
scanf("%s", buffer);   lit un mot (sans espace) ; buffer est déjà une adresse
scanf renvoie le nombre de valeurs lues : while (scanf("%d", &x) == 1) lit jusqu'à la fin.
Au clavier, Ctrl+D signale la fin de l'entrée.""",
         "exemples": [{"code": r'''int x, s = 0, n = 0;
while (scanf("%d", &x) == 1) {
    s += x;
    n += 1;
}
printf("%d nombres, somme %d\n", n, s);''', "stdin": "3 7 1\n10\n",
                       "note": "L'entrée « 3 7 1 / 10 » est envoyée automatiquement au programme."}]},
        {"titre": "fgets et les macros",
         "texte": """\
#define BSIZE 1024    remplacé par 1024 avant la compilation (pas de constante en dur dans le code).
fgets(buffer, BSIZE, stdin) lit une ligne entière (espaces et '\\n' compris), au plus BSIZE - 1 caractères :
c'est la version sécurisée. Elle renvoie NULL à la fin de l'entrée.
atoi(buffer) / atof(buffer) convertissent en int / double.""",
         "exemples": [{"code": r'''#include <stdio.h>
#include <stdlib.h>

#define BSIZE 100

int main(void) {
    char buffer[BSIZE];
    int n = 0;
    while (fgets(buffer, BSIZE, stdin) != NULL) {
        n += 1;
        printf("ligne %d : %s", n, buffer);
    }
    return 0;
}''', "stdin": "Jean Dupont\n42\n"}]},
        {"titre": "Variables globales",
         "texte": """\
Déclarée hors de toute fonction : existe du début à la fin du programme, garde sa valeur,
accessible partout, initialisée à 0 par défaut. À utiliser avec modération.""",
         "exemples": [r'''#include <stdio.h>

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
}''']},
    ],
    "methode": """\
- Lecture jusqu'à la fin : la condition de la boucle EST la lecture (scanf(...) == 1, fgets(...) != NULL).
- Les valeurs min/max : initialise-les avec la première valeur lue.
- Tester sans taper : echo "3 7 1" | ./prog   ou   printf "a\\nb\\n" | ./prog""",
}

LECONS["malloc"] = {
    "cartes": [
        {"titre": "malloc et free",
         "texte": """\
malloc(nb_octets) réserve une zone dans le TAS et renvoie son adresse (#include <stdlib.h>) :
    int *t = malloc(n * sizeof(int));    puis t[i] comme un tableau
La zone reste réservée jusqu'à free(t). Après free, on n'y touche plus.
Pile : variables locales, détruites en fin de fonction.  Tas : zones malloc, détruites par free.""",
         "exemples": [r'''int n = 5;
int *t = malloc(n * sizeof(int));
for (int i = 0; i < n; i += 1)
    t[i] = i * i;
for (int i = 0; i < n; i += 1)
    printf("%d ", t[i]);
printf("\n");
free(t);''']},
        {"titre": "Renvoyer une zone allouée (exemple strcat)",
         "texte": """\
Une fonction ne peut pas renvoyer un tableau local, mais elle peut renvoyer une zone malloc :
c'est l'appelant qui fera free. Pour une chaîne de longueur L, il faut L + 1 octets ('\\0').""",
         "exemples": [r'''#include <stdio.h>
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

int main(void) {
    char *s = ma_strcat("hello", "world");
    printf("%s\n", s);
    free(s);
    return 0;
}''']},
        {"titre": "valgrind",
         "texte": """\
valgrind --leak-check=full ./prog   lance le programme en surveillant la mémoire :
  Invalid read / write of size N   lecture/écriture hors d'une zone (souvent le '\\0' oublié, ou après free)
  definitely lost                  un malloc jamais libéré (fuite)
Sous chaque message, la ligne « at ... (fichier.c:ligne) » indique où ça se passe.""",
         "exemples": [(r'''char *s = malloc(5);
strcpy(s, "hello");   // 6 octets dans une zone de 5 !
printf("%s\n", s);''', "Ça a l'air de marcher... Lance valgrind ./exemple dans ~/.cquest/cours pour voir l'erreur et la fuite.")]},
    ],
    "methode": """\
- Pour chaque malloc, demande-toi : combien d'octets (n * sizeof(type), +1 pour une chaîne) ? qui fera le free ?
- Ne renvoie jamais l'adresse d'une variable locale : malloc.
- Après free(p), n'utilise plus p.
- Lance valgrind sur ton programme d'essai : zéro erreur, zéro « definitely lost ».""",
}

LECONS["listes"] = {
    "cartes": [
        {"titre": "Une cellule et son suivant",
         "texte": """\
struct cell { int value; struct cell *next; };
Une liste = des cellules reliées par next ; la dernière a next = NULL ; on garde un pointeur sur la tête.
    tête -> [3|•] -> [1|•] -> [4|NULL]
Il faut initialiser les champs à la création (value ET next).""",
         "exemples": [r'''#include <stdio.h>

struct cell {
    int value;
    struct cell *next;
};

int main(void) {
    struct cell c[3];
    for (int i = 0; i < 3; i += 1) {
        c[i].value = (i + 1) * 10;
        c[i].next = NULL;
    }
    c[0].next = &c[1];
    c[1].next = &c[2];
    for (struct cell *p = &c[0]; p != NULL; p = p->next)
        printf("%d -> ", p->value);
    printf("NULL\n");
    return 0;
}''']},
        {"titre": "Insérer, retirer",
         "texte": """\
Insérer b après a :   b->next = a->next;   a->next = b;    (dans CET ordre)
Retirer le suivant de p :   p->next = p->next->next;
Retirer la tête : la nouvelle tête est l'ancienne tête->next (la fonction renvoie la tête).""",
         "exemples": [r'''#include <stdio.h>

struct cell { int value; struct cell *next; };

void affiche(struct cell *l) {
    for (; l != NULL; l = l->next)
        printf("%d ", l->value);
    printf("\n");
}

int main(void) {
    struct cell a = {1, NULL}, b = {2, NULL}, c = {3, NULL};
    a.next = &c;
    affiche(&a);
    b.next = a.next;
    a.next = &b;
    affiche(&a);
    a.next = a.next->next;
    affiche(&a);
    return 0;
}''']},
        {"titre": "Liste en mémoire dynamique",
         "texte": """\
En vrai, chaque cellule est créée avec malloc(sizeof(struct cell)), et la liste est libérée cellule par
cellule. Pour libérer, sauvegarde next AVANT free :  suiv = l->next; free(l); l = suiv;""",
         "exemples": [r'''#include <stdio.h>
#include <stdlib.h>

struct cell { int value; struct cell *next; };

int main(void) {
    struct cell *tete = NULL;
    for (int i = 1; i <= 4; i += 1) {
        struct cell *c = malloc(sizeof(struct cell));
        c->value = i;
        c->next = tete;      // ajout en tête
        tete = c;
    }
    for (struct cell *p = tete; p != NULL; p = p->next)
        printf("%d ", p->value);
    printf("\n");
    while (tete != NULL) {
        struct cell *suiv = tete->next;
        free(tete);
        tete = suiv;
    }
    return 0;
}''']},
    ],
    "methode": """\
- DESSINE : des boîtes [valeur|•] et des flèches. Simule chaque affectation de next en déplaçant la flèche.
- Pense aux cas : liste vide (NULL), un seul élément, modification de la tête.
- Avant p->next->value, vérifie que p->next != NULL.
- Une fonction qui peut changer la tête la RENVOIE.""",
}

LECONS["projets"] = {
    "cartes": [
        {"titre": "Aborder un exercice long",
         "texte": """\
Les sujets type examen (César, réseau) enchaînent plusieurs petites fonctions.
1. Lis tout le sujet et écris les structures / enum d'abord.
2. Fais les fonctions dans l'ordre : les suivantes réutilisent les premières.
3. Teste chaque fonction dès qu'elle est écrite (un main d'essai), avant de passer à la suivante.""",
         "exemples": []},
        {"titre": "César : une fonction outil",
         "texte": """\
Quand trois fonctions font presque la même chose, écris une fonction outil commune.
Pour César : char decale(char c, int d). Ramène d entre 0 et 25 : d = ((d % 26) + 26) % 26;
puis 'a' + (c - 'a' + d) % 26 pour une minuscule.""",
         "exemples": [r'''#include <stdio.h>

char decale(char c, int d) {
    d = ((d % 26) + 26) % 26;
    if (c >= 'a' && c <= 'z')
        return 'a' + (c - 'a' + d) % 26;
    return c;
}

int main(void) {
    char s[] = "bonjour";
    for (int i = 0; s[i] != '\0'; i += 1)
        s[i] = decale(s[i], 2);
    printf("%s\n", s);
    return 0;
}''']},
        {"titre": "Les trois façons de rendre un résultat",
         "texte": """\
_i : sur place     void f(char *msg)               modifie la chaîne reçue
_s : dans un param void f(const char *msg, char *out) écrit dans un tableau fourni par l'appelant
_d : dynamique     char *f(const char *msg)          malloc + return, l'appelant fait free
C'est un classique d'examen : sache écrire les trois.""",
         "exemples": []},
    ],
    "methode": """\
- Commence par les structures, puis les fonctions de création/initialisation, puis le reste.
- Réutilise tes fonctions (decale, node_connect...) plutôt que de recopier du code.
- Garde un main d'essai qui construit un petit exemple et affiche tout.
- valgrind à la fin pour vérifier qu'il n'y a ni fuite ni accès invalide.""",
}

LECONS["pieges"] = {
    "cartes": [
        {"titre": "Les pièges qui compilent",
         "texte": """\
- if (cond);   ou   for (...);   : le ; termine l'instruction, le bloc suivant n'est plus concerné
- (c == 'a' || 'e')   : 'e' est toujours vrai ; il faut (c == 'a' || c == 'e')
- int / int    : division entière, même rangée dans un double
- t[n]         : hors du tableau (dernier = t[n - 1])
- variable locale non initialisée : valeur au hasard (int s = 0;)""",
         "exemples": [(r'''int c = 0;
for (int i = 0; i < 3; i += 1);
    c += 1;
printf("c = %d\n", c);''', "Un seul tour : le ; après le for est la boucle entière. gcc -Wall le signale (misleading indentation).")]},
        {"titre": "Les pièges mémoire",
         "texte": """\
- oublier le '\\0' (malloc(strlen(s)) au lieu de strlen(s) + 1)
- renvoyer l'adresse d'une variable locale
- utiliser une zone après free, ou free deux fois
- sizeof(t) dans une fonction qui reçoit t : taille d'un pointeur (8), pas du tableau
- comparer des chaînes avec == (compare les adresses)""",
         "exemples": [r'''#include <stdio.h>

void f(int t[]) {
    printf("dans f : sizeof(t) = %zu\n", sizeof(t));
}

int main(void) {
    int t[10];
    printf("dans main : sizeof(t) = %zu\n", sizeof(t));
    f(t);
    return 0;
}''']},
        {"titre": "Les outils pour les débusquer",
         "texte": """\
gcc -Wall -Werror      refuse beaucoup d'erreurs bêtes (=, variable inutilisée, format printf/scanf)
gcc -g + gdb           pas à pas : break f, run, next, print x, backtrace (après un plantage)
valgrind               accès mémoire invalides et fuites
gcc -fsanitize=address -g   détecte les dépassements de tableau au moment où ils arrivent""",
         "exemples": []},
    ],
    "methode": """\
- Quand un test échoue, refais le calcul à la main sur ce cas précis, ligne par ligne.
- Relis tes if/for : un ; en fin de ligne ? des accolades oubliées ?
- Bornes : < n ou <= n ? n ou n - 1 ?
- Mémoire : +1 pour le '\\0', free une seule fois, jamais après.""",
}
