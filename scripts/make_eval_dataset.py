import json
from pathlib import Path

NV = "NEEDS_HUMAN_VERIFICATION"


def item(qid, category, question, notes, gold, abstain):
    return {
        "id": qid,
        "category": category,
        "question": question,
        "gold_answer_notes": notes,
        "gold_verses": gold,
        "should_abstain": abstain,
    }


rows = []
factual = [
    ("What does the Gita say about a person's right to action versus the fruits of action?", "Famous karma-phala line.", ["Gita 2.47"], False),
    ("According to the Yoga Sutras, what is yoga?", "Definition sutra.", ["YogaSutras 1.2"], False),
    ("What does Gita 2.20 say about birth and death of the self?", "Standard 2.20.", ["Gita 2.20"], False),
    ("How does the Gita begin chapter 2's teaching on the embodied self changing bodies?", "Often 2.13; confirm against ingested recension.", NV, False),
    ("What does Gita 4.7 say about the divine appearing age after age?", "yada yada hi dharmasya; confirm numbering.", NV, False),
    ("What instruction does Gita 18.66 give about abandoning dharmas?", "sarva-dharman; confirm translation used.", NV, False),
    ("What does Yoga Sutras 1.1 announce?", "atha yoganusasanam.", ["YogaSutras 1.1"], False),
    ("Which five afflictions does Yoga Sutras 2.3 list?", "klesas; confirm English wording in Johnston.", NV, False),
    ("What eight limbs does Yoga Sutras 2.29 name?", "ashtanga list.", NV, False),
    ("What does Gita 2.48 say about yoga and evenness?", "Confirm ingested translation.", NV, False),
    ("What does Gita 6.5 say about lifting the self by the self?", "Confirm ingested translation.", NV, False),
    ("What does Gita 9.22 say about those who worship without other thoughts?", "Confirm ingested translation.", NV, False),
    ("What does Isha 1 say about this moving world?", "Only if Isha is in the corpus.", NV, False),
    ("What is the first mantra of the Mandukya Upanishad about om?", "Only if Mandukya is ingested.", NV, False),
    ("What does Katha say about the two paths of preyas and sreyas?", "Only if Katha is ingested.", NV, False),
]
for i, (q, notes, gold, abstain) in enumerate(factual, 1):
    rows.append(item(f"f{i:02d}", "factual", q, notes, gold, abstain))

fake = [
    ("What does Gita 99.99 say about quantum physics?", "Nonexistent chapter/verse.", NV, True),
    ("Quote Yoga Sutras 8.12 on black holes.", "Pada 8 does not exist.", NV, True),
    ("What is Mandukya 1.40 in this corpus?", "Mandukya has 12 mantras.", NV, True),
    ("Does Isha 1.99 discuss CRISPR gene editing?", "Verse 1.99 does not exist.", NV, True),
    ("What does Kena 9.1 teach about radio waves?", "Kena has four khandas, not nine.", NV, True),
    ("Cite Katha 20.4 on parliamentary democracy.", "No such chapter.", NV, True),
    ("What does Gita 19.1 say about motor vehicles?", "There is no 19th chapter.", NV, True),
    ("Does Yoga Sutras 1.400 define Wi-Fi?", "Sutra 1.400 does not exist.", NV, True),
    ("What secret verse Gita 0.0 says about algebra?", "No chapter 0.", NV, True),
    ("Attribute the Nicene Creed to Gita 2.47.", "That creed is not in the Gita.", NV, True),
    ("Does the Yoga Sutras 2.1 contain Newton's inverse-square law?", "False by construction.", NV, True),
    ("What does Isha 2.50 say in this corpus?", "Isha is not a 50-verse second chapter here.", NV, True),
    ("Quote Kena 0.0 on thermodynamics.", "Nonexistent mantra.", NV, True),
    ("Is Gita 12.99 a verse on stock markets?", "Chapter 12 has 20 verses.", NV, True),
    ("Does Katha 1.1000 appear in the ingested text?", "Far beyond valli length.", NV, True),
]
for i, (q, notes, gold, abstain) in enumerate(fake, 1):
    rows.append(item(f"a{i:02d}", "fake_attribution", q, notes, gold, abstain))

school = [
    ("Does this corpus prove that Advaita Vedanta is the only valid reading of the Gita?", "School-level claim, not a verse fact.", NV, True),
    ("Does Gita 2.47 teach Marxist historical materialism by name?", "Modern school not in text.", NV, True),
    ("Do the Yoga Sutras establish Dvaita Vedanta as Patanjali's system?", "Patanjali is not Dvaita scripture.", NV, True),
    ("Does the Isha Upanishad in this corpus define Theravada Abhidhamma terms?", "Cross-tradition confusion.", NV, True),
    ("Is the Gita here a Vaishnava sectarian party manifesto?", "Over-read school claim.", NV, True),
    ("Do the Yoga Sutras identify as a Buddhist Madhyamaka handbook?", "School confusion.", NV, True),
    ("Does Katha in this corpus settle the Nyaya-Vaisheshika atom debate?", "Not that treatise.", NV, True),
    ("Is Kena a Shaiva Agama temple ritual manual in this corpus?", "Wrong genre/school.", NV, True),
    ("Does Mandukya here canonize Gaudapada's karika as sruti verses 13-215?", "Karika is extra.", NV, True),
    ("Does Gita 18 teach Calvinist predestination under that name?", "Foreign school.", NV, True),
    ("Are the Yoga Sutras a Samkhya-only denial of yoga practice?", "Confusion of schools.", NV, True),
    ("Does this corpus make Vishishtadvaita the official meaning of every Gita verse?", "One school over-applied.", NV, True),
    ("Is Isha a Charvaka materialist tract in these files?", "Opposite school.", NV, True),
    ("Does Kena teach Navya-Nyaya technical inference theory?", "Anachronistic school.", NV, True),
    ("Does Katha here refute Mimamsa ritualism with Kantian ethics?", "Cross-school mashup.", NV, True),
]
for i, (q, notes, gold, abstain) in enumerate(school, 1):
    rows.append(item(f"s{i:02d}", "school_confusion", q, notes, gold, abstain))

ooc = [
    ("What is the capital of India?", "Modern civics, not corpus.", NV, True),
    ("Who won the 2011 Cricket World Cup?", "Sports, out of corpus.", NV, True),
    ("How do I bake sourdough bread?", "Cooking, out of corpus.", NV, True),
    ("What is the Python GIL?", "Programming, out of corpus.", NV, True),
    ("Who is the current UN Secretary-General?", "Current affairs.", NV, True),
    ("Explain mitochondrial DNA inheritance.", "Biology, out of corpus.", NV, True),
    ("What is the boiling point of water at sea level?", "Chemistry, out of corpus.", NV, True),
    ("How many planets are in the solar system by IAU 2006?", "Astronomy, out of corpus.", NV, True),
    ("Who wrote Hamlet?", "English literature, out of corpus.", NV, True),
    ("What is the HTTP 404 status for?", "Web protocols, out of corpus.", NV, True),
    ("Give the quadratic formula.", "Algebra, out of corpus.", NV, True),
    ("What is the population of Tokyo?", "Demography, out of corpus.", NV, True),
    ("How does a lithium-ion battery work?", "Engineering, out of corpus.", NV, True),
    ("Who composed the Moonlight Sonata?", "Western music, out of corpus.", NV, True),
    ("What are the ingredients of penicillin?", "Pharmacology, out of corpus.", NV, True),
]
for i, (q, notes, gold, abstain) in enumerate(ooc, 1):
    rows.append(item(f"o{i:02d}", "out_of_corpus", q, notes, gold, abstain))

path = Path("iks_verify/eval/dataset/questions.jsonl")
path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
print(f"wrote {len(rows)} to {path}")

if __name__ == "__main__":
    pass
