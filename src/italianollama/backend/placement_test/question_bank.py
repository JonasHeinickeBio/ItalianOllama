"""
Question bank for the Italian Placement Test.

Organized by CEFR level with modular structure for easy maintenance and extension.
Uses Pydantic models for type safety and validation.
"""

from italianollama.backend.placement_test.models import (
    CEFRLevel,
    Question,
    QuestionOption,
    TestSection,
    PlacementTestConfig,
)


# ============================================================================
# SECTION A: A1 LEVEL (Questions 1-10)
# ============================================================================

SECTION_A_QUESTIONS = [
    Question(
        id=1,
        level=CEFRLevel.A1,
        section="A",
        question_text="Al ristorante dobbiamo ______ un tavolo.",
        options=[
            QuestionOption(key="a", text="prenotare"),
            QuestionOption(key="b", text="cucinare"),
            QuestionOption(key="c", text="portare"),
            QuestionOption(key="d", text="ordinare"),
        ],
        correct_answer="a",
        correct_answer_text="prenotare",
        grammar_point="Infinitive collocations: prenotare un tavolo"
    ),
    Question(
        id=2,
        level=CEFRLevel.A1,
        section="A",
        question_text="Lei ______ Anna e abita ______ Roma.",
        options=[
            QuestionOption(key="a", text="è / a"),
            QuestionOption(key="b", text="ha / in"),
            QuestionOption(key="c", text="sei / da"),
            QuestionOption(key="d", text="sono / per"),
        ],
        correct_answer="a",
        correct_answer_text="è / a",
        grammar_point="Essere + preposition a (city)"
    ),
    Question(
        id=3,
        level=CEFRLevel.A1,
        section="A",
        question_text="«Di dove sei? Sei di Firenze?» — «No, non ______ di Firenze, sono di Milano.»",
        options=[
            QuestionOption(key="a", text="sei"),
            QuestionOption(key="b", text="sono"),
            QuestionOption(key="c", text="siamo"),
            QuestionOption(key="d", text="è"),
        ],
        correct_answer="b",
        correct_answer_text="sono",
        grammar_point="Essere io: non sono"
    ),
    Question(
        id=4,
        level=CEFRLevel.A1,
        section="A",
        question_text="______ zaino è sul banco.",
        options=[
            QuestionOption(key="a", text="Il"),
            QuestionOption(key="b", text="Lo"),
            QuestionOption(key="c", text="La"),
            QuestionOption(key="d", text="Un"),
        ],
        correct_answer="b",
        correct_answer_text="Lo",
        grammar_point="Lo before s + consonant (zaino)"
    ),
    Question(
        id=5,
        level=CEFRLevel.A1,
        section="A",
        question_text="Ogni mattina io ______ un caffè prima di uscire.",
        options=[
            QuestionOption(key="a", text="beve"),
            QuestionOption(key="b", text="bevono"),
            QuestionOption(key="c", text="bevo"),
            QuestionOption(key="d", text="beviamo"),
        ],
        correct_answer="c",
        correct_answer_text="bevo",
        grammar_point="Bere: io bevo"
    ),
    Question(
        id=6,
        level=CEFRLevel.A1,
        section="A",
        question_text="«Quanti anni hai?» — «______ ventidue anni.»",
        options=[
            QuestionOption(key="a", text="Sono"),
            QuestionOption(key="b", text="Ho"),
            QuestionOption(key="c", text="Faccio"),
            QuestionOption(key="d", text="Sto"),
        ],
        correct_answer="b",
        correct_answer_text="Ho",
        grammar_point="Avere for age: ho … anni"
    ),
    Question(
        id=7,
        level=CEFRLevel.A1,
        section="A",
        question_text="Il contrario di «grande» è:",
        options=[
            QuestionOption(key="a", text="lungo"),
            QuestionOption(key="b", text="bello"),
            QuestionOption(key="c", text="piccolo"),
            QuestionOption(key="d", text="caro"),
        ],
        correct_answer="c",
        correct_answer_text="piccolo",
        grammar_point="Antonyms: grande ↔ piccolo"
    ),
    Question(
        id=8,
        level=CEFRLevel.A1,
        section="A",
        question_text="Noi ______ in un appartamento al secondo piano.",
        options=[
            QuestionOption(key="a", text="vivo"),
            QuestionOption(key="b", text="vivete"),
            QuestionOption(key="c", text="vivono"),
            QuestionOption(key="d", text="viviamo"),
        ],
        correct_answer="d",
        correct_answer_text="viviamo",
        grammar_point="Vivere: noi viviamo"
    ),
    Question(
        id=9,
        level=CEFRLevel.A1,
        section="A",
        question_text="«Come stai?» — «______, grazie!»",
        options=[
            QuestionOption(key="a", text="Buongiorno"),
            QuestionOption(key="b", text="Prego"),
            QuestionOption(key="c", text="Bene"),
            QuestionOption(key="d", text="Certo"),
        ],
        correct_answer="c",
        correct_answer_text="Bene",
        grammar_point="Responding to come stai"
    ),
    Question(
        id=10,
        level=CEFRLevel.A1,
        section="A",
        question_text="Il plurale di «lo studente» è:",
        options=[
            QuestionOption(key="a", text="i studenti"),
            QuestionOption(key="b", text="li studenti"),
            QuestionOption(key="c", text="gli studenti"),
            QuestionOption(key="d", text="le studenti"),
        ],
        correct_answer="c",
        correct_answer_text="gli studenti",
        grammar_point="Plural: lo → gli (s + consonant)"
    ),
]


# ============================================================================
# SECTION B: A2 LEVEL (Questions 11-20)
# ============================================================================

SECTION_B_QUESTIONS = [
    Question(
        id=11,
        level=CEFRLevel.A2,
        section="B",
        question_text="«Usciamo per prendere un aperitivo stasera?» — «Volentieri, ______!»",
        options=[
            QuestionOption(key="a", text="ci andiamo dopo"),
            QuestionOption(key="b", text="sì, ci sto"),
            QuestionOption(key="c", text="vado via"),
            QuestionOption(key="d", text="non mi va affatto"),
        ],
        correct_answer="b",
        correct_answer_text="sì, ci sto",
        grammar_point="Colloquial: ci sto = I'm in / count me in"
    ),
    Question(
        id=12,
        level=CEFRLevel.A2,
        section="B",
        question_text="Scusami, ______ dirmi che ore sono?",
        options=[
            QuestionOption(key="a", text="potresti"),
            QuestionOption(key="b", text="potevate"),
            QuestionOption(key="c", text="potranno"),
            QuestionOption(key="d", text="potrei"),
        ],
        correct_answer="a",
        correct_answer_text="potresti",
        grammar_point="Condizionale presente for polite request"
    ),
    Question(
        id=13,
        level=CEFRLevel.A2,
        section="B",
        question_text="«Non ti sento bene, ______ più forte!»",
        options=[
            QuestionOption(key="a", text="parli"),
            QuestionOption(key="b", text="parla"),
            QuestionOption(key="c", text="parlate"),
            QuestionOption(key="d", text="parlavo"),
        ],
        correct_answer="b",
        correct_answer_text="parla",
        grammar_point="Imperativo informale (tu): parla!"
    ),
    Question(
        id=14,
        level=CEFRLevel.A2,
        section="B",
        question_text="Ieri sera Maria ______ al cinema con le amiche.",
        options=[
            QuestionOption(key="a", text="è andata"),
            QuestionOption(key="b", text="ha andato"),
            QuestionOption(key="c", text="andava sempre"),
            QuestionOption(key="d", text="andrà"),
        ],
        correct_answer="a",
        correct_answer_text="è andata",
        grammar_point="Passato prossimo: andare takes essere"
    ),
    Question(
        id=15,
        level=CEFRLevel.A2,
        section="B",
        question_text="I miei genitori ______ tornati a casa tardi ieri sera.",
        options=[
            QuestionOption(key="a", text="hanno"),
            QuestionOption(key="b", text="sono"),
            QuestionOption(key="c", text="erano"),
            QuestionOption(key="d", text="stanno"),
        ],
        correct_answer="b",
        correct_answer_text="sono",
        grammar_point="Tornare takes essere as auxiliary"
    ),
    Question(
        id=16,
        level=CEFRLevel.A2,
        section="B",
        question_text="Non ho ______ visto quel film — devo ancora vederlo.",
        options=[
            QuestionOption(key="a", text="già"),
            QuestionOption(key="b", text="sempre"),
            QuestionOption(key="c", text="ancora"),
            QuestionOption(key="d", text="mai"),
        ],
        correct_answer="c",
        correct_answer_text="ancora",
        grammar_point="Non … ancora = not yet"
    ),
    Question(
        id=17,
        level=CEFRLevel.A2,
        section="B",
        question_text="A mia sorella ______ molto i libri di avventura.",
        options=[
            QuestionOption(key="a", text="piace"),
            QuestionOption(key="b", text="piacciono"),
            QuestionOption(key="c", text="piacono"),
            QuestionOption(key="d", text="piaci"),
        ],
        correct_answer="b",
        correct_answer_text="piacciono",
        grammar_point="Piacere agrees with logical subject (libri, plural)"
    ),
    Question(
        id=18,
        level=CEFRLevel.A2,
        section="B",
        question_text="Marco è più alto ______ sua sorella.",
        options=[
            QuestionOption(key="a", text="che"),
            QuestionOption(key="b", text="come"),
            QuestionOption(key="c", text="di"),
            QuestionOption(key="d", text="da"),
        ],
        correct_answer="c",
        correct_answer_text="di",
        grammar_point="Comparativo di maggioranza: più … di + noun"
    ),
    Question(
        id=19,
        level=CEFRLevel.A2,
        section="B",
        question_text="Hai il giornale? — Sì, ______ ho lasciato sul tavolo.",
        options=[
            QuestionOption(key="a", text="la"),
            QuestionOption(key="b", text="li"),
            QuestionOption(key="c", text="lo"),
            QuestionOption(key="d", text="ne"),
        ],
        correct_answer="c",
        correct_answer_text="lo",
        grammar_point="Direct object pronoun: lo = il giornale (masc. sing.)"
    ),
    Question(
        id=20,
        level=CEFRLevel.A2,
        section="B",
        question_text="Cosa significa «il mese scorso»?",
        options=[
            QuestionOption(key="a", text="next month"),
            QuestionOption(key="b", text="every month"),
            QuestionOption(key="c", text="last month"),
            QuestionOption(key="d", text="this month"),
        ],
        correct_answer="c",
        correct_answer_text="last month",
        grammar_point="Time expression: scorso = last/past"
    ),
]


# ============================================================================
# SECTION C: B1 LEVEL (Questions 21-30)
# ============================================================================

SECTION_C_QUESTIONS = [
    Question(
        id=21,
        level=CEFRLevel.B1,
        section="C",
        question_text="Quando sono arrivato a scuola, la lezione ______ già iniziata.",
        options=[
            QuestionOption(key="a", text="è"),
            QuestionOption(key="b", text="era"),
            QuestionOption(key="c", text="sarà"),
            QuestionOption(key="d", text="ha"),
        ],
        correct_answer="b",
        correct_answer_text="era",
        grammar_point="Trapassato prossimo: era + participio (prior past event)"
    ),
    Question(
        id=22,
        level=CEFRLevel.B1,
        section="C",
        question_text="La ______ pizza d'Italia si mangia a Napoli.",
        options=[
            QuestionOption(key="a", text="migliore"),
            QuestionOption(key="b", text="più buona"),
            QuestionOption(key="c", text="meglio"),
            QuestionOption(key="d", text="migliore / più buona (both correct)"),
        ],
        correct_answer="d",
        correct_answer_text="migliore / più buona (both correct)",
        grammar_point="Superlativo relativo: migliore = più buona (both valid)"
    ),
    Question(
        id=23,
        level=CEFRLevel.B1,
        section="C",
        question_text="«Uscirai con Elena stasera?» — «Sì, ______ uscirò, andremo al cinema.»",
        options=[
            QuestionOption(key="a", text="la"),
            QuestionOption(key="b", text="le"),
            QuestionOption(key="c", text="ci"),
            QuestionOption(key="d", text="ne"),
        ],
        correct_answer="c",
        correct_answer_text="ci",
        grammar_point="Ci as pronoun replacing a place/person already mentioned"
    ),
    Question(
        id=24,
        level=CEFRLevel.B1,
        section="C",
        question_text="Da bambina, la nonna ______ ogni domenica una torta per tutta la famiglia.",
        options=[
            QuestionOption(key="a", text="ha preparato"),
            QuestionOption(key="b", text="preparava"),
            QuestionOption(key="c", text="preparerà"),
            QuestionOption(key="d", text="prepara"),
        ],
        correct_answer="b",
        correct_answer_text="preparava",
        grammar_point="Imperfetto for habitual/repeated past action"
    ),
    Question(
        id=25,
        level=CEFRLevel.B1,
        section="C",
        question_text="In Italia ______ molta pasta a pranzo.",
        options=[
            QuestionOption(key="a", text="uno mangia"),
            QuestionOption(key="b", text="si mangia"),
            QuestionOption(key="c", text="loro mangiano"),
            QuestionOption(key="d", text="ci mangia"),
        ],
        correct_answer="b",
        correct_answer_text="si mangia",
        grammar_point="Si impersonale: si + 3rd person singular"
    ),
    Question(
        id=26,
        level=CEFRLevel.B1,
        section="C",
        question_text="Ieri mattina Paolo ______ tardissimo e ha perso il treno.",
        options=[
            QuestionOption(key="a", text="si è svegliato"),
            QuestionOption(key="b", text="ha svegliato"),
            QuestionOption(key="c", text="si ha svegliato"),
            QuestionOption(key="d", text="svegliava"),
        ],
        correct_answer="a",
        correct_answer_text="si è svegliato",
        grammar_point="Reflexive verb svegliarsi: sempre + essere"
    ),
    Question(
        id=27,
        level=CEFRLevel.B1,
        section="C",
        question_text="Non riesco a ______ dove ho messo le chiavi.",
        options=[
            QuestionOption(key="a", text="ricordi"),
            QuestionOption(key="b", text="ricordando"),
            QuestionOption(key="c", text="ricordare"),
            QuestionOption(key="d", text="ricordo"),
        ],
        correct_answer="c",
        correct_answer_text="ricordare",
        grammar_point="Riuscire a + infinitive"
    ),
    Question(
        id=28,
        level=CEFRLevel.B1,
        section="C",
        question_text="La ragazza ______ mi ha aiutato ieri si chiama Giulia.",
        options=[
            QuestionOption(key="a", text="cui"),
            QuestionOption(key="b", text="che"),
            QuestionOption(key="c", text="chi"),
            QuestionOption(key="d", text="quale"),
        ],
        correct_answer="b",
        correct_answer_text="che",
        grammar_point="Relative pronoun che (subject/direct object)"
    ),
    Question(
        id=29,
        level=CEFRLevel.B1,
        section="C",
        question_text="Per arrivare al centro città ______ circa venti minuti a piedi.",
        options=[
            QuestionOption(key="a", text="ci voglio"),
            QuestionOption(key="b", text="ci vogliono"),
            QuestionOption(key="c", text="ci vuoi"),
            QuestionOption(key="d", text="si vogliono"),
        ],
        correct_answer="b",
        correct_answer_text="ci vogliono",
        grammar_point="Ci vuole / ci vogliono + plural time expression"
    ),
    Question(
        id=30,
        level=CEFRLevel.B1,
        section="C",
        question_text="______ studiassi di più, avresti voti migliori.",
        options=[
            QuestionOption(key="a", text="Quando"),
            QuestionOption(key="b", text="Che"),
            QuestionOption(key="c", text="Se"),
            QuestionOption(key="d", text="Come"),
        ],
        correct_answer="c",
        correct_answer_text="Se",
        grammar_point="2nd conditional: se + congiuntivo imperfetto"
    ),
]


# ============================================================================
# SECTION D: B2 LEVEL (Questions 31-40)
# ============================================================================

SECTION_D_QUESTIONS = [
    Question(
        id=31,
        level=CEFRLevel.B2,
        section="D",
        question_text="______ avesse cucinato la pasta, i bambini avevano ancora fame.",
        options=[
            QuestionOption(key="a", text="Nonostante"),
            QuestionOption(key="b", text="Anche se"),
            QuestionOption(key="c", text="Sebbene"),
            QuestionOption(key="d", text="Nonostante / Sebbene (both)"),
        ],
        correct_answer="a",
        correct_answer_text="Nonostante",
        grammar_point="Nonostante + congiuntivo trapassato (concessive)"
    ),
    Question(
        id=32,
        level=CEFRLevel.B2,
        section="D",
        question_text="Volevamo andare a Roma ma non ______, eravamo troppo stanchi.",
        options=[
            QuestionOption(key="a", text="siamo potuti andare"),
            QuestionOption(key="b", text="abbiamo potuto andare"),
            QuestionOption(key="c", text="potevamo andare"),
            QuestionOption(key="d", text="both a & b correct"),
        ],
        correct_answer="d",
        correct_answer_text="both a & b correct",
        grammar_point="Modal verb potere in passato prossimo: aspectual flexibility"
    ),
    Question(
        id=33,
        level=CEFRLevel.B2,
        section="D",
        question_text="Erano preoccupati che la nonna ______ prima dell'inverno.",
        options=[
            QuestionOption(key="a", text="si ammali"),
            QuestionOption(key="b", text="si ammalasse"),
            QuestionOption(key="c", text="si ammalava"),
            QuestionOption(key="d", text="si ammalerebbe"),
        ],
        correct_answer="b",
        correct_answer_text="si ammalasse",
        grammar_point="Congiuntivo imperfetto after preoccupati che"
    ),
    Question(
        id=34,
        level=CEFRLevel.B2,
        section="D",
        question_text="«Il contratto ______ dal direttore ieri pomeriggio.» (passive)",
        options=[
            QuestionOption(key="a", text="è firmato"),
            QuestionOption(key="b", text="è stato firmato"),
            QuestionOption(key="c", text="ha firmato"),
            QuestionOption(key="d", text="veniva firmato da ieri"),
        ],
        correct_answer="b",
        correct_answer_text="è stato firmato",
        grammar_point="Passivo: essere + participio (completed past)"
    ),
    Question(
        id=35,
        level=CEFRLevel.B2,
        section="D",
        question_text="Dobbiamo finire tutto prima che lui ______ a casa.",
        options=[
            QuestionOption(key="a", text="torna"),
            QuestionOption(key="b", text="tornerà"),
            QuestionOption(key="c", text="torni"),
            QuestionOption(key="d", text="tornasse"),
        ],
        correct_answer="c",
        correct_answer_text="torni",
        grammar_point="Prima che + congiuntivo presente"
    ),
    Question(
        id=36,
        level=CEFRLevel.B2,
        section="D",
        question_text="Se avessi avuto più tempo, ______ il russo.",
        options=[
            QuestionOption(key="a", text="studierei"),
            QuestionOption(key="b", text="avrei studiato"),
            QuestionOption(key="c", text="studiassi"),
            QuestionOption(key="d", text="avevo studiato"),
        ],
        correct_answer="b",
        correct_answer_text="avrei studiato",
        grammar_point="Condizionale passato in 3rd conditional"
    ),
    Question(
        id=37,
        level=CEFRLevel.B2,
        section="D",
        question_text="Il romanzo di ______ ti ho parlato ieri era un capolavoro.",
        options=[
            QuestionOption(key="a", text="che"),
            QuestionOption(key="b", text="cui"),
            QuestionOption(key="c", text="chi"),
            QuestionOption(key="d", text="quale"),
        ],
        correct_answer="b",
        correct_answer_text="cui",
        grammar_point="Di cui = of which (relative pronoun with preposition)"
    ),
    Question(
        id=38,
        level=CEFRLevel.B2,
        section="D",
        question_text="Non riesco a fare a ______ di pensarci.",
        options=[
            QuestionOption(key="a", text="più"),
            QuestionOption(key="b", text="meno"),
            QuestionOption(key="c", text="tanto"),
            QuestionOption(key="d", text="parte"),
        ],
        correct_answer="b",
        correct_answer_text="meno",
        grammar_point="Fare a meno di + infinitive"
    ),
    Question(
        id=39,
        level=CEFRLevel.B2,
        section="D",
        question_text="Spero che voi ______ la situazione prima della riunione.",
        options=[
            QuestionOption(key="a", text="capite"),
            QuestionOption(key="b", text="capirete"),
            QuestionOption(key="c", text="capiate"),
            QuestionOption(key="d", text="capireste"),
        ],
        correct_answer="c",
        correct_answer_text="capiate",
        grammar_point="Congiuntivo presente after sperare che"
    ),
    Question(
        id=40,
        level=CEFRLevel.B2,
        section="D",
        question_text="«A meno che non ______, non possiamo procedere.»",
        options=[
            QuestionOption(key="a", text="viene"),
            QuestionOption(key="b", text="venga"),
            QuestionOption(key="c", text="veniva"),
            QuestionOption(key="d", text="venisse"),
        ],
        correct_answer="b",
        correct_answer_text="venga",
        grammar_point="A meno che non + congiuntivo presente"
    ),
]


# ============================================================================
# SECTION E: C1 LEVEL (Questions 41-50)
# ============================================================================

SECTION_E_QUESTIONS = [
    Question(
        id=41,
        level=CEFRLevel.C1,
        section="E",
        question_text="Il gelato ______ mangiato velocemente, altrimenti si scioglie.",
        options=[
            QuestionOption(key="a", text="va"),
            QuestionOption(key="b", text="deve essere"),
            QuestionOption(key="c", text="si deve"),
            QuestionOption(key="d", text="è da"),
        ],
        correct_answer="a",
        correct_answer_text="va",
        grammar_point="Andare + participio = obligation (va mangiato)"
    ),
    Question(
        id=42,
        level=CEFRLevel.C1,
        section="E",
        question_text="Che la pizza non ______ facile da preparare è un dato di fatto.",
        options=[
            QuestionOption(key="a", text="è"),
            QuestionOption(key="b", text="sia"),
            QuestionOption(key="c", text="era"),
            QuestionOption(key="d", text="fosse"),
        ],
        correct_answer="b",
        correct_answer_text="sia",
        grammar_point="Congiuntivo after che (factive complement clause)"
    ),
    Question(
        id=43,
        level=CEFRLevel.C1,
        section="E",
        question_text="Quando ______ che lui era partito, gli ______ subito.",
        options=[
            QuestionOption(key="a", text="ho saputo / ho telefonato"),
            QuestionOption(key="b", text="sapevo / telefonavo"),
            QuestionOption(key="c", text="seppi / telefonai"),
            QuestionOption(key="d", text="sapevo / ho telefonato"),
        ],
        correct_answer="c",
        correct_answer_text="seppi / telefonai",
        grammar_point="Passato remoto for narrative past (literary/formal)"
    ),
    Question(
        id=44,
        level=CEFRLevel.C1,
        section="E",
        question_text="Se ______ prima, non avremmo perso il treno.",
        options=[
            QuestionOption(key="a", text="partissimo"),
            QuestionOption(key="b", text="fossimo partiti"),
            QuestionOption(key="c", text="eravamo partiti"),
            QuestionOption(key="d", text="partivamo"),
        ],
        correct_answer="b",
        correct_answer_text="fossimo partiti",
        grammar_point="Congiuntivo trapassato (essere) in 3rd conditional"
    ),
    Question(
        id=45,
        level=CEFRLevel.C1,
        section="E",
        question_text="Vorrei che tu mi ______ la verità ieri sera.",
        options=[
            QuestionOption(key="a", text="dica"),
            QuestionOption(key="b", text="dicessi"),
            QuestionOption(key="c", text="avessi detto"),
            QuestionOption(key="d", text="diresti"),
        ],
        correct_answer="c",
        correct_answer_text="avessi detto",
        grammar_point="Volere che + congiuntivo trapassato (past unfulfilled wish)"
    ),
    Question(
        id=46,
        level=CEFRLevel.C1,
        section="E",
        question_text="______ avendo studiato tutta la notte, non ha superato l'esame.",
        options=[
            QuestionOption(key="a", text="Nonostante"),
            QuestionOption(key="b", text="Pur"),
            QuestionOption(key="c", text="Sebbene"),
            QuestionOption(key="d", text="Benché"),
        ],
        correct_answer="b",
        correct_answer_text="Pur",
        grammar_point="Pur + gerundio = concessive"
    ),
    Question(
        id=47,
        level=CEFRLevel.C1,
        section="E",
        question_text="Non c'è nessun medico qui che ______ aiutarci.",
        options=[
            QuestionOption(key="a", text="può"),
            QuestionOption(key="b", text="possa"),
            QuestionOption(key="c", text="potrebbe"),
            QuestionOption(key="d", text="potrà"),
        ],
        correct_answer="b",
        correct_answer_text="possa",
        grammar_point="Nessuno che + congiuntivo (existential negation)"
    ),
    Question(
        id=48,
        level=CEFRLevel.C1,
        section="E",
        question_text="La ringrazio per ______ contattato così presto.",
        options=[
            QuestionOption(key="a", text="mi avere"),
            QuestionOption(key="b", text="avermi"),
            QuestionOption(key="c", text="avere mi"),
            QuestionOption(key="d", text="mi aver stato"),
        ],
        correct_answer="b",
        correct_answer_text="avermi",
        grammar_point="Clitic attaches before infinitive in formal register"
    ),
    Question(
        id=49,
        level=CEFRLevel.C1,
        section="E",
        question_text="Il treno ______ partire quando siamo finalmente arrivati alla stazione.",
        options=[
            QuestionOption(key="a", text="stava per"),
            QuestionOption(key="b", text="stava di"),
            QuestionOption(key="c", text="era per"),
            QuestionOption(key="d", text="andava a"),
        ],
        correct_answer="a",
        correct_answer_text="stava per",
        grammar_point="Stare per + infinitive = to be about to"
    ),
    Question(
        id=50,
        level=CEFRLevel.C1,
        section="E",
        question_text="Per quante difficoltà ______ nella vita, non ha mai perso il sorriso.",
        options=[
            QuestionOption(key="a", text="incontrasse"),
            QuestionOption(key="b", text="avesse incontrato"),
            QuestionOption(key="c", text="avrebbe incontrato"),
            QuestionOption(key="d", text="aveva incontrato"),
        ],
        correct_answer="b",
        correct_answer_text="avesse incontrato",
        grammar_point="Per quanto + congiuntivo trapassato (literary concessive)"
    ),
]


# ============================================================================
# PLACEMENT TEST CONFIGURATION
# ============================================================================

def get_placement_test() -> PlacementTestConfig:
    """
    Get the complete placement test configuration.
    
    Returns:
        PlacementTestConfig with all sections and questions
    """
    return PlacementTestConfig(
        name="Italian Language Placement Test",
        description="Comprehensive 50-question placement test (A1–C1) modelled on CILS, PLIDA, CLA UniTrento",
        language="Italian",
        version="2.0.0",
        sections=[
            TestSection(
                level=CEFRLevel.A1,
                section_letter="A",
                passing_score=7,
                questions=SECTION_A_QUESTIONS,
            ),
            TestSection(
                level=CEFRLevel.A2,
                section_letter="B",
                passing_score=7,
                questions=SECTION_B_QUESTIONS,
            ),
            TestSection(
                level=CEFRLevel.B1,
                section_letter="C",
                passing_score=7,
                questions=SECTION_C_QUESTIONS,
            ),
            TestSection(
                level=CEFRLevel.B2,
                section_letter="D",
                passing_score=7,
                questions=SECTION_D_QUESTIONS,
            ),
            TestSection(
                level=CEFRLevel.C1,
                section_letter="E",
                passing_score=7,
                questions=SECTION_E_QUESTIONS,
            ),
        ],
    )
