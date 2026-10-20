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
    ("What does Gita 12.13 say about one who bears no ill will?", "Confirm translation used.", NV, False),
    ("What does Yoga Sutras 1.3 say about the seer?", "Confirm translation used.", NV, False),
    ("What does Gita 3.19 recommend about attachment and duty?", "Confirm translation used.", NV, False),
]
for i, (q, notes, gold, abstain) in enumerate(factual, 1):
    # Factual verse links remain a scholar-labelling task; do not present
    # provisional links as gold answers.
    rows.append(item(f"f{i:02d}", "factual", q, notes, NV, abstain))

fake = [
    ("What does Gita 99.99 say about quantum physics?", "Nonexistent chapter/verse.", [], True),
    ("Quote Yoga Sutras 8.12 on black holes.", "Pada 8 does not exist.", [], True),
    ("What is Gita 18.99 in this corpus?", "Chapter 18 has 78 verses.", [], True),
    ("Does Yoga Sutras 5.1 discuss CRISPR gene editing?", "There is no fifth pada.", [], True),
    ("What does Gita 0.1 teach about radio waves?", "There is no chapter zero.", [], True),
    ("Cite Yoga Sutras 7.4 on parliamentary democracy.", "There is no seventh pada.", [], True),
    ("What does Gita 19.1 say about motor vehicles?", "There is no 19th chapter.", [], True),
    ("Does Yoga Sutras 1.400 define Wi-Fi?", "Sutra 1.400 does not exist.", [], True),
    ("What secret verse Gita 0.0 says about algebra?", "No chapter 0.", [], True),
    ("Attribute the Nicene Creed to Gita 2.47.", "That creed is not in the Gita.", [], True),
    ("Does the Yoga Sutras 2.1 contain Newton's inverse-square law?", "False by construction.", [], True),
    ("What does Gita 2.100 say in this corpus?", "Chapter 2 has 72 verses.", [], True),
    ("Quote Yoga Sutras 0.0 on thermodynamics.", "There is no pada zero.", [], True),
    ("Is Gita 12.99 a verse on stock markets?", "Chapter 12 has 20 verses.", [], True),
    ("Does Yoga Sutras 4.1000 appear in the ingested text?", "Pada 4 has 34 sutras.", [], True),
]
for i, (q, notes, gold, abstain) in enumerate(fake, 1):
    rows.append(item(f"a{i:02d}", "fake_attribution", q, notes, gold, abstain))

school = [
    ("Does this corpus prove that Advaita Vedanta is the only valid reading of the Gita?", "School-level claim, not a verse fact.", NV, True),
    ("Does Gita 2.47 teach Marxist historical materialism by name?", "Modern school not in text.", NV, True),
    ("Do the Yoga Sutras establish Dvaita Vedanta as Patanjali's system?", "Patanjali is not Dvaita scripture.", NV, True),
    ("Does the Gita in this corpus define Theravada Abhidhamma terms?", "Cross-tradition confusion.", NV, True),
    ("Is the Gita here a Vaishnava sectarian party manifesto?", "Over-read school claim.", NV, True),
    ("Do the Yoga Sutras identify as a Buddhist Madhyamaka handbook?", "School confusion.", NV, True),
    ("Does the Gita in this corpus settle the Nyaya-Vaisheshika atom debate?", "Not that treatise.", NV, True),
    ("Are the Yoga Sutras a Shaiva Agama temple ritual manual?", "Wrong genre/school.", NV, True),
    ("Does the Gita canonize Gaudapada's karika as its own verses?", "Different work and tradition.", NV, True),
    ("Does Gita 18 teach Calvinist predestination under that name?", "Foreign school.", NV, True),
    ("Are the Yoga Sutras a Samkhya-only denial of yoga practice?", "Confusion of schools.", NV, True),
    ("Does this corpus make Vishishtadvaita the official meaning of every Gita verse?", "One school over-applied.", NV, True),
    ("Is the Gita a Charvaka materialist tract in these files?", "Opposite school.", NV, True),
    ("Do the Yoga Sutras teach Navya-Nyaya technical inference theory?", "Anachronistic school.", NV, True),
    ("Does the Gita refute Mimamsa ritualism with Kantian ethics?", "Cross-school mashup.", NV, True),
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
for i, (q, notes, _gold, abstain) in enumerate(ooc, 1):
    rows.append(item(f"o{i:02d}", "out_of_corpus", q, notes, [], abstain))

path = Path("iks_verify/eval/dataset/questions.jsonl")
path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")
print(f"wrote {len(rows)} to {path}")

if __name__ == "__main__":
    pass
