import json
import pathlib

root = pathlib.Path(__file__).parent
gloss = pathlib.Path("/Users/nakazawanobuyuki/Desktop/WhisperShare/server/glossary")
scenarios = ["general", "medical", "business", "travel"]
terms = []
for scenario in scenarios:
    for term in json.loads((gloss / f"{scenario}.json").read_text())["terms"]:
        terms.append((scenario, term))
ids = [term["id"] for _, term in terms]
if len(ids) != 57 or len(set(ids)) != 57:
    raise SystemExit(f"expected 57 terms, got {len(ids)}")

meta = json.loads((root / "meta.json").read_text())
packs = []
for lang in meta:
    if lang.get("fromGlossary"):
        texts = {term["id"]: term[lang["id"]] for _, term in terms}
    else:
        texts = json.loads((root / "text" / f"{lang['id']}.json").read_text())
    missing = [item for item in ids if item not in texts or not str(texts[item]).strip()]
    extra = sorted(set(texts) - set(ids))
    if missing or extra:
        raise SystemExit(f"{lang['id']} missing={missing} extra={extra}")
    body = {
        "id": lang["id"],
        "label": lang["label"],
        "nativeLabel": lang["nativeLabel"],
        "sttLocale": lang["sttLocale"],
        "ttsVoiceLang": lang["ttsVoiceLang"],
        "scenarios": {name: [] for name in scenarios},
    }
    for scenario, term in terms:
        body["scenarios"][scenario].append(
            {"id": term["id"], "ja": term["ja"], "text": texts[term["id"]].strip()}
        )
    out = root / "packs" / f"{lang['id']}.json"
    out.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n")
    packs.append({key: lang[key] for key in ("id", "label", "nativeLabel", "sttLocale", "ttsVoiceLang")})
    packs[-1]["file"] = f"packs/{lang['id']}.json"
    packs[-1]["terms"] = 57

index = {
    "product": "whispershare",
    "includedInApp": ["ja", "en"],
    "packs": packs,
}
(root / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n")
print(f"{len(packs)} packs")
