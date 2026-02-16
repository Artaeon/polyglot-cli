#!/usr/bin/env python3
"""Generate conjugation JSON files for Portuguese, Romanian, Croatian, Slovak, Ukrainian, Bulgarian."""

import json
import os

OUT = "/home/rrl/Projects/polyglot-cli/data/conjugations"
P = ["1sg", "2sg", "3sg", "1pl", "2pl", "3pl"]


def conj(forms_list, rom_list=None):
    """Build a tense dict from 6 forms and optional 6 romanizations."""
    if rom_list is None:
        rom_list = [None] * 6
    return {p: {"form": f, "romanization": r} for p, f, r in zip(P, forms_list, rom_list)}


def verb(cid, inf, tenses_dict, rom=None, pattern_id=None):
    """Build a verb entry."""
    return {
        "concept_id": cid,
        "infinitive": inf,
        "romanization": rom,
        "pattern_id": pattern_id,
        "forms": tenses_dict,
    }


def write_lang(lang_id, lang_name, person_labels, tenses, tense_labels, patterns, verbs_list):
    data = {
        "language_id": lang_id,
        "meta": {
            "persons": P,
            "person_labels_de": person_labels,
            "tenses": tenses,
            "tense_labels_de": tense_labels,
        },
        "conjugation_patterns": patterns,
        "verbs": verbs_list,
    }
    path = os.path.join(OUT, f"{lang_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Wrote {path} ({len(verbs_list)} verbs)")


# ============================================================
# PORTUGUESE
# ============================================================
def gen_pt():
    T = ["presente", "preterito_perfeito", "futuro_simples"]
    person_labels = {
        "1sg": "ich (eu)", "2sg": "du (tu)", "3sg": "er/sie (ele/ela)",
        "1pl": "wir (nós)", "2pl": "ihr (vós)", "3pl": "sie (eles/elas)",
    }
    tense_labels = {
        "presente": "Praesens", "preterito_perfeito": "Perfekt", "futuro_simples": "Futur",
    }
    patterns = [
        {"pattern_id": "ar_regular", "description_de": "-ar Verben",
         "rule_de": "Stamm + -o, -as, -a, -amos, -ais, -am"},
        {"pattern_id": "er_regular", "description_de": "-er Verben",
         "rule_de": "Stamm + -o, -es, -e, -emos, -eis, -em"},
        {"pattern_id": "ir_regular", "description_de": "-ir Verben",
         "rule_de": "Stamm + -o, -es, -e, -imos, -is, -em"},
    ]

    def v(cid, inf, pres, pret, fut, pat=None):
        return verb(cid, inf, {T[0]: conj(pres), T[1]: conj(pret), T[2]: conj(fut)}, pattern_id=pat)

    verbs = [
        v("be", "ser",
          ["sou", "és", "é", "somos", "sois", "são"],
          ["fui", "foste", "foi", "fomos", "fostes", "foram"],
          ["serei", "serás", "será", "seremos", "sereis", "serão"], "irregular"),
        v("have", "ter",
          ["tenho", "tens", "tem", "temos", "tendes", "têm"],
          ["tive", "tiveste", "teve", "tivemos", "tivestes", "tiveram"],
          ["terei", "terás", "terá", "teremos", "tereis", "terão"], "irregular"),
        v("go", "ir",
          ["vou", "vais", "vai", "vamos", "ides", "vão"],
          ["fui", "foste", "foi", "fomos", "fostes", "foram"],
          ["irei", "irás", "irá", "iremos", "ireis", "irão"], "irregular"),
        v("come", "vir",
          ["venho", "vens", "vem", "vimos", "vindes", "vêm"],
          ["vim", "vieste", "veio", "viemos", "viestes", "vieram"],
          ["virei", "virás", "virá", "viremos", "vireis", "virão"], "irregular"),
        v("eat", "comer",
          ["como", "comes", "come", "comemos", "comeis", "comem"],
          ["comi", "comeste", "comeu", "comemos", "comestes", "comeram"],
          ["comerei", "comerás", "comerá", "comeremos", "comereis", "comerão"], "er_regular"),
        v("drink", "beber",
          ["bebo", "bebes", "bebe", "bebemos", "bebeis", "bebem"],
          ["bebi", "bebeste", "bebeu", "bebemos", "bebestes", "beberam"],
          ["beberei", "beberás", "beberá", "beberemos", "bebereis", "beberão"], "er_regular"),
        v("say", "dizer",
          ["digo", "dizes", "diz", "dizemos", "dizeis", "dizem"],
          ["disse", "disseste", "disse", "dissemos", "dissestes", "disseram"],
          ["direi", "dirás", "dirá", "diremos", "direis", "dirão"], "irregular"),
        v("see", "ver",
          ["vejo", "vês", "vê", "vemos", "vedes", "veem"],
          ["vi", "viste", "viu", "vimos", "vistes", "viram"],
          ["verei", "verás", "verá", "veremos", "vereis", "verão"], "irregular"),
        v("hear", "ouvir",
          ["ouço", "ouves", "ouve", "ouvimos", "ouvis", "ouvem"],
          ["ouvi", "ouviste", "ouviu", "ouvimos", "ouvistes", "ouviram"],
          ["ouvirei", "ouvirás", "ouvirá", "ouviremos", "ouvireis", "ouvirão"], "irregular"),
        v("know", "saber",
          ["sei", "sabes", "sabe", "sabemos", "sabeis", "sabem"],
          ["soube", "soubeste", "soube", "soubemos", "soubestes", "souberam"],
          ["saberei", "saberás", "saberá", "saberemos", "sabereis", "saberão"], "irregular"),
        v("want", "querer",
          ["quero", "queres", "quer", "queremos", "quereis", "querem"],
          ["quis", "quiseste", "quis", "quisemos", "quisestes", "quiseram"],
          ["quererei", "quererás", "quererá", "quereremos", "querereis", "quererão"], "irregular"),
        v("can", "poder",
          ["posso", "podes", "pode", "podemos", "podeis", "podem"],
          ["pude", "pudeste", "pôde", "pudemos", "pudestes", "puderam"],
          ["poderei", "poderás", "poderá", "poderemos", "podereis", "poderão"], "irregular"),
        v("do_make", "fazer",
          ["faço", "fazes", "faz", "fazemos", "fazeis", "fazem"],
          ["fiz", "fizeste", "fez", "fizemos", "fizestes", "fizeram"],
          ["farei", "farás", "fará", "faremos", "fareis", "farão"], "irregular"),
        v("give", "dar",
          ["dou", "dás", "dá", "damos", "dais", "dão"],
          ["dei", "deste", "deu", "demos", "destes", "deram"],
          ["darei", "darás", "dará", "daremos", "dareis", "darão"], "irregular"),
        v("take", "tomar",
          ["tomo", "tomas", "toma", "tomamos", "tomais", "tomam"],
          ["tomei", "tomaste", "tomou", "tomámos", "tomastes", "tomaram"],
          ["tomarei", "tomarás", "tomará", "tomaremos", "tomareis", "tomarão"], "ar_regular"),
        v("read", "ler",
          ["leio", "lês", "lê", "lemos", "ledes", "leem"],
          ["li", "leste", "leu", "lemos", "lestes", "leram"],
          ["lerei", "lerás", "lerá", "leremos", "lereis", "lerão"], "irregular"),
        v("write", "escrever",
          ["escrevo", "escreves", "escreve", "escrevemos", "escreveis", "escrevem"],
          ["escrevi", "escreveste", "escreveu", "escrevemos", "escrevestes", "escreveram"],
          ["escreverei", "escreverás", "escreverá", "escreveremos", "escrevereis", "escreverão"], "er_regular"),
        v("sleep", "dormir",
          ["durmo", "dormes", "dorme", "dormimos", "dormis", "dormem"],
          ["dormi", "dormiste", "dormiu", "dormimos", "dormistes", "dormiram"],
          ["dormirei", "dormirás", "dormirá", "dormiremos", "dormireis", "dormirão"], "irregular"),
        v("live", "viver",
          ["vivo", "vives", "vive", "vivemos", "viveis", "vivem"],
          ["vivi", "viveste", "viveu", "vivemos", "vivestes", "viveram"],
          ["viverei", "viverás", "viverá", "viveremos", "vivereis", "viverão"], "er_regular"),
        v("work", "trabalhar",
          ["trabalho", "trabalhas", "trabalha", "trabalhamos", "trabalhais", "trabalham"],
          ["trabalhei", "trabalhaste", "trabalhou", "trabalhámos", "trabalhastes", "trabalharam"],
          ["trabalharei", "trabalharás", "trabalhará", "trabalharemos", "trabalhareis", "trabalharão"], "ar_regular"),
    ]
    write_lang("pt", "Portugiesisch", person_labels, T, tense_labels, patterns, verbs)


# ============================================================
# ROMANIAN
# ============================================================
def gen_ro():
    T = ["prezent", "perfect_compus", "viitor"]
    person_labels = {
        "1sg": "ich (eu)", "2sg": "du (tu)", "3sg": "er/sie (el/ea)",
        "1pl": "wir (noi)", "2pl": "ihr (voi)", "3pl": "sie (ei/ele)",
    }
    tense_labels = {
        "prezent": "Praesens", "perfect_compus": "Perfekt (zusammengesetzt)", "viitor": "Futur",
    }
    patterns = [
        {"pattern_id": "a_conj", "description_de": "-a Konjugation (I.)", "rule_de": "Stamm + Endungen der I. Konjugation"},
        {"pattern_id": "ea_conj", "description_de": "-ea Konjugation (II.)", "rule_de": "Stamm + Endungen der II. Konjugation"},
        {"pattern_id": "e_conj", "description_de": "-e Konjugation (III.)", "rule_de": "Stamm + Endungen der III. Konjugation"},
        {"pattern_id": "i_conj", "description_de": "-i/-î Konjugation (IV.)", "rule_de": "Stamm + Endungen der IV. Konjugation"},
    ]
    # Romanian perfect compus: am/ai/a/am/ați/au + past participle
    def v(cid, inf, pres, pp, fut, pat=None):
        """pp = past participle for perfect compus (am/ai/a/am/ați/au + pp)."""
        pc = [f"am {pp}", f"ai {pp}", f"a {pp}", f"am {pp}", f"ați {pp}", f"au {pp}"]
        return verb(cid, inf, {T[0]: conj(pres), T[1]: conj(pc), T[2]: conj(fut)}, pattern_id=pat)

    verbs = [
        v("be", "a fi",
          ["sunt", "ești", "este", "suntem", "sunteți", "sunt"],
          "fost",
          ["voi fi", "vei fi", "va fi", "vom fi", "veți fi", "vor fi"], "irregular"),
        v("have", "a avea",
          ["am", "ai", "are", "avem", "aveți", "au"],
          "avut",
          ["voi avea", "vei avea", "va avea", "vom avea", "veți avea", "vor avea"], "irregular"),
        v("go", "a merge",
          ["merg", "mergi", "merge", "mergem", "mergeți", "merg"],
          "mers",
          ["voi merge", "vei merge", "va merge", "vom merge", "veți merge", "vor merge"], "e_conj"),
        v("come", "a veni",
          ["vin", "vii", "vine", "venim", "veniți", "vin"],
          "venit",
          ["voi veni", "vei veni", "va veni", "vom veni", "veți veni", "vor veni"], "i_conj"),
        v("eat", "a mânca",
          ["mănânc", "mănânci", "mănâncă", "mâncăm", "mâncați", "mănâncă"],
          "mâncat",
          ["voi mânca", "vei mânca", "va mânca", "vom mânca", "veți mânca", "vor mânca"], "a_conj"),
        v("drink", "a bea",
          ["beau", "bei", "bea", "bem", "beți", "beau"],
          "băut",
          ["voi bea", "vei bea", "va bea", "vom bea", "veți bea", "vor bea"], "ea_conj"),
        v("say", "a spune",
          ["spun", "spui", "spune", "spunem", "spuneți", "spun"],
          "spus",
          ["voi spune", "vei spune", "va spune", "vom spune", "veți spune", "vor spune"], "e_conj"),
        v("see", "a vedea",
          ["văd", "vezi", "vede", "vedem", "vedeți", "văd"],
          "văzut",
          ["voi vedea", "vei vedea", "va vedea", "vom vedea", "veți vedea", "vor vedea"], "ea_conj"),
        v("hear", "a auzi",
          ["aud", "auzi", "aude", "auzim", "auziți", "aud"],
          "auzit",
          ["voi auzi", "vei auzi", "va auzi", "vom auzi", "veți auzi", "vor auzi"], "i_conj"),
        v("know", "a ști",
          ["știu", "știi", "știe", "știm", "știți", "știu"],
          "știut",
          ["voi ști", "vei ști", "va ști", "vom ști", "veți ști", "vor ști"], "irregular"),
        v("want", "a vrea",
          ["vreau", "vrei", "vrea", "vrem", "vreți", "vor"],
          "vrut",
          ["voi vrea", "vei vrea", "va vrea", "vom vrea", "veți vrea", "vor vrea"], "irregular"),
        v("can", "a putea",
          ["pot", "poți", "poate", "putem", "puteți", "pot"],
          "putut",
          ["voi putea", "vei putea", "va putea", "vom putea", "veți putea", "vor putea"], "irregular"),
        v("do_make", "a face",
          ["fac", "faci", "face", "facem", "faceți", "fac"],
          "făcut",
          ["voi face", "vei face", "va face", "vom face", "veți face", "vor face"], "e_conj"),
        v("give", "a da",
          ["dau", "dai", "dă", "dăm", "dați", "dau"],
          "dat",
          ["voi da", "vei da", "va da", "vom da", "veți da", "vor da"], "irregular"),
        v("take", "a lua",
          ["iau", "iei", "ia", "luăm", "luați", "iau"],
          "luat",
          ["voi lua", "vei lua", "va lua", "vom lua", "veți lua", "vor lua"], "irregular"),
        v("read", "a citi",
          ["citesc", "citești", "citește", "citim", "citiți", "citesc"],
          "citit",
          ["voi citi", "vei citi", "va citi", "vom citi", "veți citi", "vor citi"], "i_conj"),
        v("write", "a scrie",
          ["scriu", "scrii", "scrie", "scriem", "scrieți", "scriu"],
          "scris",
          ["voi scrie", "vei scrie", "va scrie", "vom scrie", "veți scrie", "vor scrie"], "e_conj"),
        v("sleep", "a dormi",
          ["dorm", "dormi", "doarme", "dormim", "dormiți", "dorm"],
          "dormit",
          ["voi dormi", "vei dormi", "va dormi", "vom dormi", "veți dormi", "vor dormi"], "i_conj"),
        v("live", "a trăi",
          ["trăiesc", "trăiești", "trăiește", "trăim", "trăiți", "trăiesc"],
          "trăit",
          ["voi trăi", "vei trăi", "va trăi", "vom trăi", "veți trăi", "vor trăi"], "i_conj"),
        v("work", "a lucra",
          ["lucrez", "lucrezi", "lucrează", "lucrăm", "lucrați", "lucrează"],
          "lucrat",
          ["voi lucra", "vei lucra", "va lucra", "vom lucra", "veți lucra", "vor lucra"], "a_conj"),
    ]
    write_lang("ro", "Rumaenisch", person_labels, T, tense_labels, patterns, verbs)


# ============================================================
# CROATIAN
# ============================================================
def gen_hr():
    T = ["prezent", "perfekt", "futur"]
    person_labels = {
        "1sg": "ich (ja)", "2sg": "du (ti)", "3sg": "er/sie/es (on/ona/ono)",
        "1pl": "wir (mi)", "2pl": "ihr (vi)", "3pl": "sie (oni/one/ona)",
    }
    tense_labels = {
        "prezent": "Praesens", "perfekt": "Perfekt", "futur": "Futur I",
    }
    patterns = [
        {"pattern_id": "a_conj", "description_de": "-ati Verben (a-Konjugation)"},
        {"pattern_id": "e_conj", "description_de": "-eti/-ati Verben (e-Konjugation)"},
        {"pattern_id": "i_conj", "description_de": "-iti Verben (i-Konjugation)"},
    ]
    # Croatian perfekt: sam/si/je/smo/ste/su + l-participle (masc sg default)
    # Croatian futur I: ću/ćeš/će/ćemo/ćete/će + infinitive (short form)
    AUX_PRES = ["sam", "si", "je", "smo", "ste", "su"]
    AUX_FUT = ["ću", "ćeš", "će", "ćemo", "ćete", "će"]

    def v(cid, inf, pres, lpart, pat=None):
        """lpart = l-participle masculine singular for perfekt; futur = infinitive-based."""
        perf = [f"{a} {lpart}" for a in AUX_PRES]
        # For futur I, the infinitive drops final -i for most verbs when combined with ću etc.
        # But the standard written form is: inf + ću -> e.g. radit ću / ja ću raditi
        # Use the more common "ja ću + infinitive" form for clarity:
        fut = [f"{a} {inf}" for a in AUX_FUT]
        return verb(cid, inf, {T[0]: conj(pres), T[1]: conj(perf), T[2]: conj(fut)}, pattern_id=pat)

    verbs = [
        v("be", "biti",
          ["jesam", "jesi", "jest", "jesmo", "jeste", "jesu"],
          "bio", "irregular"),
        v("have", "imati",
          ["imam", "imaš", "ima", "imamo", "imate", "imaju"],
          "imao", "a_conj"),
        v("go", "ići",
          ["idem", "ideš", "ide", "idemo", "idete", "idu"],
          "išao", "irregular"),
        v("come", "doći",
          ["dođem", "dođeš", "dođe", "dođemo", "dođete", "dođu"],
          "došao", "irregular"),
        v("eat", "jesti",
          ["jedem", "jedeš", "jede", "jedemo", "jedete", "jedu"],
          "jeo", "irregular"),
        v("drink", "piti",
          ["pijem", "piješ", "pije", "pijemo", "pijete", "piju"],
          "pio", "irregular"),
        v("say", "reći",
          ["reknem", "rekneš", "rekne", "reknemo", "reknete", "reknu"],
          "rekao", "irregular"),
        v("see", "vidjeti",
          ["vidim", "vidiš", "vidi", "vidimo", "vidite", "vide"],
          "vidio", "i_conj"),
        v("hear", "čuti",
          ["čujem", "čuješ", "čuje", "čujemo", "čujete", "čuju"],
          "čuo", "irregular"),
        v("know", "znati",
          ["znam", "znaš", "zna", "znamo", "znate", "znaju"],
          "znao", "a_conj"),
        v("want", "htjeti",
          ["hoću", "hoćeš", "hoće", "hoćemo", "hoćete", "hoće"],
          "htio", "irregular"),
        v("can", "moći",
          ["mogu", "možeš", "može", "možemo", "možete", "mogu"],
          "mogao", "irregular"),
        v("do_make", "raditi",
          ["radim", "radiš", "radi", "radimo", "radite", "rade"],
          "radio", "i_conj"),
        v("give", "dati",
          ["dajem", "daješ", "daje", "dajemo", "dajete", "daju"],
          "dao", "irregular"),
        v("take", "uzeti",
          ["uzmem", "uzmeš", "uzme", "uzmemo", "uzmete", "uzmu"],
          "uzeo", "irregular"),
        v("read", "čitati",
          ["čitam", "čitaš", "čita", "čitamo", "čitate", "čitaju"],
          "čitao", "a_conj"),
        v("write", "pisati",
          ["pišem", "pišeš", "piše", "pišemo", "pišete", "pišu"],
          "pisao", "e_conj"),
        v("sleep", "spavati",
          ["spavam", "spavaš", "spava", "spavamo", "spavate", "spavaju"],
          "spavao", "a_conj"),
        v("live", "živjeti",
          ["živim", "živiš", "živi", "živimo", "živite", "žive"],
          "živio", "i_conj"),
        v("work", "raditi",
          ["radim", "radiš", "radi", "radimo", "radite", "rade"],
          "radio", "i_conj"),
    ]
    # Note: "do_make" and "work" both map to "raditi" in Croatian; that's correct.
    # Let's use "činiti" for do_make to differentiate:
    verbs[12] = verb("do_make", "činiti", {
        T[0]: conj(["činim", "činiš", "čini", "činimo", "činite", "čine"]),
        T[1]: conj([f"{a} činio" for a in AUX_PRES]),
        T[2]: conj([f"{a} činiti" for a in AUX_FUT]),
    }, pattern_id="i_conj")

    write_lang("hr", "Kroatisch", person_labels, T, tense_labels, patterns, verbs)


# ============================================================
# SLOVAK
# ============================================================
def gen_sk():
    T = ["pritomny", "minuly", "buduci"]
    person_labels = {
        "1sg": "ich (ja)", "2sg": "du (ty)", "3sg": "er/sie/es (on/ona/ono)",
        "1pl": "wir (my)", "2pl": "ihr (vy)", "3pl": "sie (oni/ony)",
    }
    tense_labels = {
        "pritomny": "Praesens", "minuly": "Vergangenheit", "buduci": "Futur",
    }
    patterns = [
        {"pattern_id": "a_conj", "description_de": "-ať Verben"},
        {"pattern_id": "e_conj", "description_de": "-eť/-ieť Verben"},
        {"pattern_id": "i_conj", "description_de": "-iť Verben"},
    ]
    # Slovak past: l-participle + som/si/—/sme/ste/— (masc sg forms)
    # Slovak future for imperfective: budem/budeš/bude/budeme/budete/budú + infinitive
    AUX_PAST = ["som", "si", "", "sme", "ste", ""]
    AUX_FUT = ["budem", "budeš", "bude", "budeme", "budete", "budú"]

    def v(cid, inf, pres, lpart, pat=None, fut_override=None):
        past = []
        for a in AUX_PAST:
            past.append(f"{lpart} {a}".strip() if a else lpart)
        if fut_override:
            fut = fut_override
        else:
            fut = [f"{a} {inf}" for a in AUX_FUT]
        return verb(cid, inf, {T[0]: conj(pres), T[1]: conj(past), T[2]: conj(fut)}, pattern_id=pat)

    verbs = [
        v("be", "byť",
          ["som", "si", "je", "sme", "ste", "sú"],
          "bol", "irregular",
          fut_override=["budem", "budeš", "bude", "budeme", "budete", "budú"]),
        v("have", "mať",
          ["mám", "máš", "má", "máme", "máte", "majú"],
          "mal", "irregular"),
        v("go", "ísť",
          ["idem", "ideš", "ide", "ideme", "idete", "idú"],
          "išiel", "irregular",
          fut_override=["pôjdem", "pôjdeš", "pôjde", "pôjdeme", "pôjdete", "pôjdu"]),
        v("come", "prísť",
          ["prídem", "prídeš", "príde", "prídeme", "prídete", "prídu"],
          "prišiel", "irregular"),
        v("eat", "jesť",
          ["jem", "ješ", "je", "jeme", "jete", "jedia"],
          "jedol", "irregular"),
        v("drink", "piť",
          ["pijem", "piješ", "pije", "pijeme", "pijete", "pijú"],
          "pil", "irregular"),
        v("say", "povedať",
          ["poviem", "povieš", "povie", "povieme", "poviete", "povedia"],
          "povedal", "e_conj"),
        v("see", "vidieť",
          ["vidím", "vidíš", "vidí", "vidíme", "vidíte", "vidia"],
          "videl", "e_conj"),
        v("hear", "počuť",
          ["počujem", "počuješ", "počuje", "počujeme", "počujete", "počujú"],
          "počul", "irregular"),
        v("know", "vedieť",
          ["viem", "vieš", "vie", "vieme", "viete", "vedia"],
          "vedel", "e_conj"),
        v("want", "chcieť",
          ["chcem", "chceš", "chce", "chceme", "chcete", "chcú"],
          "chcel", "irregular"),
        v("can", "môcť",
          ["môžem", "môžeš", "môže", "môžeme", "môžete", "môžu"],
          "mohol", "irregular"),
        v("do_make", "robiť",
          ["robím", "robíš", "robí", "robíme", "robíte", "robia"],
          "robil", "i_conj"),
        v("give", "dať",
          ["dám", "dáš", "dá", "dáme", "dáte", "dajú"],
          "dal", "irregular"),
        v("take", "vziať",
          ["vezmem", "vezmeš", "vezme", "vezmeme", "vezmete", "vezmú"],
          "vzal", "irregular"),
        v("read", "čítať",
          ["čítam", "čítaš", "číta", "čítame", "čítate", "čítajú"],
          "čítal", "a_conj"),
        v("write", "písať",
          ["píšem", "píšeš", "píše", "píšeme", "píšete", "píšu"],
          "písal", "e_conj"),
        v("sleep", "spať",
          ["spím", "spíš", "spí", "spíme", "spíte", "spia"],
          "spal", "irregular"),
        v("live", "žiť",
          ["žijem", "žiješ", "žije", "žijeme", "žijete", "žijú"],
          "žil", "irregular"),
        v("work", "pracovať",
          ["pracujem", "pracuješ", "pracuje", "pracujeme", "pracujete", "pracujú"],
          "pracoval", "a_conj"),
    ]
    write_lang("sk", "Slowakisch", person_labels, T, tense_labels, patterns, verbs)


# ============================================================
# UKRAINIAN
# ============================================================
def gen_uk():
    T = ["teperishnij", "mynulyj", "majbutnij"]
    person_labels = {
        "1sg": "ich (я)", "2sg": "du (ти)", "3sg": "er/sie/es (він/вона/воно)",
        "1pl": "wir (ми)", "2pl": "ihr (ви)", "3pl": "sie (вони)",
    }
    tense_labels = {
        "teperishnij": "Praesens (теперішній)",
        "mynulyj": "Vergangenheit (минулий)",
        "majbutnij": "Futur (майбутній)",
    }
    patterns = [
        {"pattern_id": "first_conj", "description_de": "I. Konjugation (-ати/-яти)"},
        {"pattern_id": "second_conj", "description_de": "II. Konjugation (-ити/-іти)"},
    ]
    # Ukrainian past: l-form varies by gender, we use masc sg for all persons (simplified like Russian file)
    # Ukrainian future imperfective: буду/будеш/буде/будемо/будете/будуть + infinitive
    AUX_FUT = ["буду", "будеш", "буде", "будемо", "будете", "будуть"]

    def cr(forms, roms):
        return conj(forms, roms)

    def v(cid, inf, inf_rom, pres, pres_r, past_m, past_m_r, fut=None, fut_r=None, pat=None):
        if fut is None:
            fut = [f"{a} {inf}" for a in AUX_FUT]
            fut_r = [f"{a} {inf_rom}" for a in ["budu", "budesh", "bude", "budemo", "budete", "budut'"]]
        # Past: same l-form for all persons (masc singular)
        past_forms = [past_m] * 6
        past_roms = [past_m_r] * 6
        return verb(cid, inf, {
            T[0]: cr(pres, pres_r),
            T[1]: cr(past_forms, past_roms),
            T[2]: cr(fut, fut_r),
        }, rom=inf_rom, pattern_id=pat)

    verbs = [
        v("be", "бути", "buty",
          ["є", "є", "є", "є", "є", "є"],
          ["ye", "ye", "ye", "ye", "ye", "ye"],
          "був", "buv",
          ["буду", "будеш", "буде", "будемо", "будете", "будуть"],
          ["budu", "budesh", "bude", "budemo", "budete", "budut'"], "irregular"),
        v("have", "мати", "maty",
          ["маю", "маєш", "має", "маємо", "маєте", "мають"],
          ["mayu", "mayesh", "maye", "mayemo", "mayete", "mayut'"],
          "мав", "mav", pat="first_conj"),
        v("go", "іти", "ity",
          ["іду", "ідеш", "іде", "ідемо", "ідете", "ідуть"],
          ["idu", "idesh", "ide", "idemo", "idete", "idut'"],
          "ішов", "ishov",
          ["піду", "підеш", "піде", "підемо", "підете", "підуть"],
          ["pidu", "pidesh", "pide", "pidemo", "pidete", "pidut'"], "irregular"),
        v("come", "приходити", "prykhodity",
          ["приходжу", "приходиш", "приходить", "приходимо", "приходите", "приходять"],
          ["prykhodzu", "prykhodish", "prykhodyt'", "prykhodimo", "prykhodite", "prykhodat'"],
          "приходив", "prykhodiv", pat="second_conj"),
        v("eat", "їсти", "yisty",
          ["їм", "їси", "їсть", "їмо", "їсте", "їдять"],
          ["yim", "yisy", "yist'", "yimo", "yiste", "yidyat'"],
          "їв", "yiv", pat="irregular"),
        v("drink", "пити", "pyty",
          ["п'ю", "п'єш", "п'є", "п'ємо", "п'єте", "п'ють"],
          ["p'yu", "p'yesh", "p'ye", "p'yemo", "p'yete", "p'yut'"],
          "пив", "pyv", pat="irregular"),
        v("say", "казати", "kazaty",
          ["кажу", "кажеш", "каже", "кажемо", "кажете", "кажуть"],
          ["kazhu", "kazhesh", "kazhe", "kazhemo", "kazhete", "kazhut'"],
          "казав", "kazav", pat="first_conj"),
        v("see", "бачити", "bachyty",
          ["бачу", "бачиш", "бачить", "бачимо", "бачите", "бачать"],
          ["bachu", "bachysh", "bachyt'", "bachymo", "bachyte", "bachat'"],
          "бачив", "bachyv", pat="second_conj"),
        v("hear", "чути", "chuty",
          ["чую", "чуєш", "чує", "чуємо", "чуєте", "чують"],
          ["chuyu", "chuyesh", "chuye", "chuyemo", "chuyete", "chuyut'"],
          "чув", "chuv", pat="first_conj"),
        v("know", "знати", "znaty",
          ["знаю", "знаєш", "знає", "знаємо", "знаєте", "знають"],
          ["znayu", "znayesh", "znaye", "znayemo", "znayete", "znayut'"],
          "знав", "znav", pat="first_conj"),
        v("want", "хотіти", "khotity",
          ["хочу", "хочеш", "хоче", "хочемо", "хочете", "хочуть"],
          ["khochu", "khochesh", "khoche", "khochemo", "khochete", "khochut'"],
          "хотів", "khotiv", pat="irregular"),
        v("can", "могти", "mohty",
          ["можу", "можеш", "може", "можемо", "можете", "можуть"],
          ["mozhu", "mozhesh", "mozhe", "mozhemo", "mozhete", "mozhut'"],
          "міг", "mih", pat="irregular"),
        v("do_make", "робити", "robyty",
          ["роблю", "робиш", "робить", "робимо", "робите", "роблять"],
          ["roblyu", "robysh", "robyt'", "robymo", "robyte", "roblyat'"],
          "робив", "robyv", pat="second_conj"),
        v("give", "давати", "davaty",
          ["даю", "даєш", "дає", "даємо", "даєте", "дають"],
          ["dayu", "dayesh", "daye", "dayemo", "dayete", "dayut'"],
          "давав", "davav", pat="first_conj"),
        v("take", "брати", "braty",
          ["беру", "береш", "бере", "беремо", "берете", "беруть"],
          ["beru", "beresh", "bere", "beremo", "berete", "berut'"],
          "брав", "brav", pat="first_conj"),
        v("read", "читати", "chytaty",
          ["читаю", "читаєш", "читає", "читаємо", "читаєте", "читають"],
          ["chytayu", "chytayesh", "chytaye", "chytayemo", "chytayete", "chytayut'"],
          "читав", "chytav", pat="first_conj"),
        v("write", "писати", "pysaty",
          ["пишу", "пишеш", "пише", "пишемо", "пишете", "пишуть"],
          ["pyshu", "pyshesh", "pyshe", "pyshemo", "pyshete", "pyshut'"],
          "писав", "pysav", pat="first_conj"),
        v("sleep", "спати", "spaty",
          ["сплю", "спиш", "спить", "спимо", "спите", "сплять"],
          ["splyu", "spysh", "spyt'", "spymo", "spyte", "splyat'"],
          "спав", "spav", pat="irregular"),
        v("live", "жити", "zhyty",
          ["живу", "живеш", "живе", "живемо", "живете", "живуть"],
          ["zhyvu", "zhyvesh", "zhyve", "zhyvemo", "zhyvete", "zhyvut'"],
          "жив", "zhyv", pat="irregular"),
        v("work", "працювати", "pratsyuvaty",
          ["працюю", "працюєш", "працює", "працюємо", "працюєте", "працюють"],
          ["pratsyuyu", "pratsyuyesh", "pratsyuye", "pratsyuyemo", "pratsyuyete", "pratsyuyut'"],
          "працював", "pratsyuvav", pat="first_conj"),
    ]
    write_lang("uk", "Ukrainisch", person_labels, T, tense_labels, patterns, verbs)


# ============================================================
# BULGARIAN
# ============================================================
def gen_bg():
    T = ["segashno", "minalo", "budeshte"]
    person_labels = {
        "1sg": "ich (аз)", "2sg": "du (ти)", "3sg": "er/sie/es (той/тя/то)",
        "1pl": "wir (ние)", "2pl": "ihr (вие)", "3pl": "sie (те)",
    }
    tense_labels = {
        "segashno": "Praesens (сегашно време)",
        "minalo": "Vergangenheit (минало свършено време)",
        "budeshte": "Futur (бъдеще време)",
    }
    patterns = [
        {"pattern_id": "first_conj", "description_de": "I. Konjugation (-а/-е)"},
        {"pattern_id": "second_conj", "description_de": "II. Konjugation (-и)"},
        {"pattern_id": "third_conj", "description_de": "III. Konjugation (-а/-я)"},
    ]
    # Bulgarian future: ще + present tense forms
    # Bulgarian past (aorist): specific aorist forms

    def cr(forms, roms):
        return conj(forms, roms)

    def v(cid, inf, inf_rom, pres, pres_r, aor, aor_r, pat=None):
        # Future = ще + present forms
        fut = [f"ще {f}" for f in pres]
        fut_r = [f"shte {r}" for r in pres_r]
        return verb(cid, inf, {
            T[0]: cr(pres, pres_r),
            T[1]: cr(aor, aor_r),
            T[2]: cr(fut, fut_r),
        }, rom=inf_rom, pattern_id=pat)

    verbs = [
        v("be", "съм", "sam",
          ["съм", "си", "е", "сме", "сте", "са"],
          ["sam", "si", "e", "sme", "ste", "sa"],
          ["бях", "беше", "беше", "бяхме", "бяхте", "бяха"],
          ["byah", "beshe", "beshe", "byahme", "byahte", "byaha"], "irregular"),
        v("have", "имам", "imam",
          ["имам", "имаш", "има", "имаме", "имате", "имат"],
          ["imam", "imash", "ima", "imame", "imate", "imat"],
          ["имах", "имаше", "имаше", "имахме", "имахте", "имаха"],
          ["imah", "imashe", "imashe", "imahme", "imahte", "imaha"], "third_conj"),
        v("go", "отивам", "otivam",
          ["отивам", "отиваш", "отива", "отиваме", "отивате", "отиват"],
          ["otivam", "otivash", "otiva", "otivame", "otivate", "otivat"],
          ["отидох", "отиде", "отиде", "отидохме", "отидохте", "отидоха"],
          ["otidoh", "otide", "otide", "otidohme", "otidohte", "otidoha"], "third_conj"),
        v("come", "идвам", "idvam",
          ["идвам", "идваш", "идва", "идваме", "идвате", "идват"],
          ["idvam", "idvash", "idva", "idvame", "idvate", "idvat"],
          ["дойдох", "дойде", "дойде", "дойдохме", "дойдохте", "дойдоха"],
          ["doydoh", "doyde", "doyde", "doydohme", "doydohte", "doydoha"], "third_conj"),
        v("eat", "ям", "yam",
          ["ям", "ядеш", "яде", "ядем", "ядете", "ядат"],
          ["yam", "yadesh", "yade", "yadem", "yadete", "yadat"],
          ["ядох", "яде", "яде", "ядохме", "ядохте", "ядоха"],
          ["yadoh", "yade", "yade", "yadohme", "yadohte", "yadoha"], "irregular"),
        v("drink", "пия", "piya",
          ["пия", "пиеш", "пие", "пием", "пиете", "пият"],
          ["piya", "piesh", "pie", "piem", "piete", "piyat"],
          ["пих", "пи", "пи", "пихме", "пихте", "пиха"],
          ["pih", "pi", "pi", "pihme", "pihte", "piha"], "first_conj"),
        v("say", "казвам", "kazvam",
          ["казвам", "казваш", "казва", "казваме", "казвате", "казват"],
          ["kazvam", "kazvash", "kazva", "kazvame", "kazvate", "kazvat"],
          ["казах", "каза", "каза", "казахме", "казахте", "казаха"],
          ["kazah", "kaza", "kaza", "kazahme", "kazahte", "kazaha"], "third_conj"),
        v("see", "виждам", "vizhdam",
          ["виждам", "виждаш", "вижда", "виждаме", "виждате", "виждат"],
          ["vizhdam", "vizhdash", "vizhda", "vizhdame", "vizhdate", "vizhdat"],
          ["видях", "видя", "видя", "видяхме", "видяхте", "видяха"],
          ["vidyah", "vidya", "vidya", "vidyahme", "vidyahte", "vidyaha"], "third_conj"),
        v("hear", "чувам", "chuvam",
          ["чувам", "чуваш", "чува", "чуваме", "чувате", "чуват"],
          ["chuvam", "chuvash", "chuva", "chuvame", "chuvate", "chuvat"],
          ["чух", "чу", "чу", "чухме", "чухте", "чуха"],
          ["chuh", "chu", "chu", "chuhme", "chuhte", "chuha"], "third_conj"),
        v("know", "знам", "znam",
          ["знам", "знаеш", "знае", "знаем", "знаете", "знаят"],
          ["znam", "znayesh", "znaye", "znayem", "znayete", "znayat"],
          ["знаех", "знаеше", "знаеше", "знаехме", "знаехте", "знаеха"],
          ["znayeh", "znayeshe", "znayeshe", "znayehme", "znayehte", "znayeha"], "irregular"),
        v("want", "искам", "iskam",
          ["искам", "искаш", "иска", "искаме", "искате", "искат"],
          ["iskam", "iskash", "iska", "iskame", "iskate", "iskat"],
          ["исках", "искаше", "искаше", "искахме", "искахте", "искаха"],
          ["iskah", "iskashe", "iskashe", "iskahme", "iskahte", "iskaha"], "third_conj"),
        v("can", "мога", "moga",
          ["мога", "можеш", "може", "можем", "можете", "могат"],
          ["moga", "mozhesh", "mozhe", "mozhem", "mozhete", "mogat"],
          ["можах", "можа", "можа", "можахме", "можахте", "можаха"],
          ["mozhah", "mozha", "mozha", "mozhahme", "mozhahte", "mozhaha"], "irregular"),
        v("do_make", "правя", "pravya",
          ["правя", "правиш", "прави", "правим", "правите", "правят"],
          ["pravya", "pravish", "pravi", "pravim", "pravite", "pravyat"],
          ["правих", "прави", "прави", "правихме", "правихте", "правиха"],
          ["pravih", "pravi", "pravi", "pravihme", "pravihte", "praviha"], "second_conj"),
        v("give", "давам", "davam",
          ["давам", "даваш", "дава", "даваме", "давате", "дават"],
          ["davam", "davash", "dava", "davame", "davate", "davat"],
          ["дадох", "даде", "даде", "дадохме", "дадохте", "дадоха"],
          ["dadoh", "dade", "dade", "dadohme", "dadohte", "dadoha"], "third_conj"),
        v("take", "вземам", "vzemam",
          ["вземам", "вземаш", "взема", "вземаме", "вземате", "вземат"],
          ["vzemam", "vzemash", "vzema", "vzemame", "vzemate", "vzemat"],
          ["взех", "взе", "взе", "взехме", "взехте", "взеха"],
          ["vzeh", "vze", "vze", "vzehme", "vzehte", "vzeha"], "third_conj"),
        v("read", "чета", "cheta",
          ["чета", "четеш", "чете", "четем", "четете", "четат"],
          ["cheta", "chetesh", "chete", "chetem", "chetete", "chetat"],
          ["четох", "чете", "чете", "четохме", "четохте", "четоха"],
          ["chetoh", "chete", "chete", "chetohme", "chetohte", "chetoha"], "first_conj"),
        v("write", "пиша", "pisha",
          ["пиша", "пишеш", "пише", "пишем", "пишете", "пишат"],
          ["pisha", "pishesh", "pishe", "pishem", "pishete", "pishat"],
          ["писах", "писа", "писа", "писахме", "писахте", "писаха"],
          ["pisah", "pisa", "pisa", "pisahme", "pisahte", "pisaha"], "first_conj"),
        v("sleep", "спя", "spya",
          ["спя", "спиш", "спи", "спим", "спите", "спят"],
          ["spya", "spish", "spi", "spim", "spite", "spyat"],
          ["спах", "спа", "спа", "спахме", "спахте", "спаха"],
          ["spah", "spa", "spa", "spahme", "spahte", "spaha"], "second_conj"),
        v("live", "живея", "zhiveya",
          ["живея", "живееш", "живее", "живеем", "живеете", "живеят"],
          ["zhiveya", "zhiveyesh", "zhiveye", "zhiveyem", "zhiveyete", "zhiveyat"],
          ["живях", "живя", "живя", "живяхме", "живяхте", "живяха"],
          ["zhivyah", "zhivya", "zhivya", "zhivyahme", "zhivyahte", "zhivyaha"], "first_conj"),
        v("work", "работя", "rabotya",
          ["работя", "работиш", "работи", "работим", "работите", "работят"],
          ["rabotya", "rabotish", "raboti", "rabotim", "rabotite", "rabotyat"],
          ["работих", "работи", "работи", "работихме", "работихте", "работиха"],
          ["rabotih", "raboti", "raboti", "rabotihme", "rabotihte", "rabotiha"], "second_conj"),
    ]
    write_lang("bg", "Bulgarisch", person_labels, T, tense_labels, patterns, verbs)


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    gen_pt()
    gen_ro()
    gen_hr()
    gen_sk()
    gen_uk()
    gen_bg()
    print("Done. Generated 6 conjugation files.")
