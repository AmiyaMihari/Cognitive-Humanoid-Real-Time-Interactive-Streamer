#!/usr/bin/env python
"""Bake the C.H.R.I.S. voice identity (design-once -> clone).

Runtime synthesis clones from fixed reference clips for a stable voice. This
script is the offline step that *creates* those clips with the VoiceDesign
model. Run it once per emotion:

    # 1. Generate candidates to audition:
    python scripts/bake_voice.py --emotion neutral --n 6
    #    -> identity/neutral/candidates/cand_01.wav ... cand_06.wav

    # 2. Listen, then promote the one you like to the reference clip:
    python scripts/bake_voice.py --emotion neutral --choose cand_03

For v1 only ``neutral`` is needed. The script already accepts all five emotions
(happy, sad, angry, fear, shame), so baking the emotion bank later (v2) is just
running it five more times.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Make the project root importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from effectors.effector_voice._models import (  # noqa: E402
    DEFAULT_LANGUAGE,
    DEFAULT_REF_TEXT,
    DEFAULT_VOICE_DESCRIPTION,
    EMOTION_INSTRUCTS,
    EMOTIONS,
    get_design_model_id,
    get_identity_dir,
    get_manifest_path,
)


def _default_instruct(emotion: str) -> str:
    """Compose the VoiceDesign instruct for ``emotion``."""
    if emotion == "neutral":
        return DEFAULT_VOICE_DESCRIPTION
    return f"{DEFAULT_VOICE_DESCRIPTION} {EMOTION_INSTRUCTS[emotion]}"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _generate(args: argparse.Namespace) -> None:
    """Generate N audition candidates with the VoiceDesign model."""
    import soundfile as sf

    # Reuse Voice's engine builder (dtype/device/cuDNN/flash-attn fallback) but
    # point it at the design model.
    from effectors.effector_voice.synthesizer import Voice

    instruct = args.instruct or _default_instruct(args.emotion)
    ref_text = args.ref_text

    emotion_dir = get_identity_dir() / args.emotion
    candidates_dir = emotion_dir / "candidates"
    candidates_dir.mkdir(parents=True, exist_ok=True)

    voice = Voice(model=get_design_model_id(), lang=args.language)
    engine = voice.engine
    print(f"Baking '{args.emotion}' with {get_design_model_id()}")
    print(f"  language : {args.language}")
    print(f"  instruct : {instruct}")
    print(f"  ref_text : {ref_text}")

    paths: list[Path] = []
    try:
        for i in range(1, args.n + 1):
            wavs, sr = engine.generate_voice_design(
                text=ref_text,
                language=args.language,
                instruct=instruct,
                max_new_tokens=voice.max_new_tokens,
            )
            out = candidates_dir / f"cand_{i:02d}.wav"
            sf.write(str(out), wavs[0], sr)
            paths.append(out)
            print(f"  [{i}/{args.n}] -> {out}")
            voice.clear_cuda_cache()
    finally:
        if args.unload:
            voice.unload()

    print("\nCandidates written. Audition them, then promote one with:")
    print(
        f"    python scripts/bake_voice.py --emotion {args.emotion} "
        f"--choose {paths[0].stem if paths else 'cand_01'}"
    )


def _choose(args: argparse.Namespace) -> None:
    """Promote a candidate to the emotion's reference clip and update manifest."""
    instruct = args.instruct or _default_instruct(args.emotion)
    ref_text = args.ref_text

    emotion_dir = get_identity_dir() / args.emotion
    candidate = emotion_dir / "candidates" / f"{args.choose}.wav"
    if not candidate.is_file():
        raise SystemExit(
            f"Candidate not found: {candidate}\n"
            f"Generate some first: python scripts/bake_voice.py "
            f"--emotion {args.emotion} --n {args.n}"
        )

    reference = emotion_dir / "reference.wav"
    shutil.copyfile(candidate, reference)
    (emotion_dir / "reference.txt").write_text(ref_text, encoding="utf-8")

    created_at = datetime.now(timezone.utc).isoformat()
    sha = _sha256(reference)
    meta = {
        "emotion": args.emotion,
        "reference": f"{args.emotion}/reference.wav",
        "ref_text": ref_text,
        "instruct": instruct,
        "language": args.language,
        "model": get_design_model_id(),
        "source_candidate": args.choose,
        "created_at": created_at,
        "sha256": sha,
    }
    (emotion_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Update the manifest (source of truth for what is baked).
    manifest_path = get_manifest_path()
    manifest: dict = {"version": 1, "emotions": {}}
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.setdefault("emotions", {})[args.emotion] = {
        k: meta[k]
        for k in ("reference", "ref_text", "instruct", "language", "model", "created_at", "sha256")
    }
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Promoted {candidate.name} -> {reference}")
    print(f"Updated manifest: {manifest_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--emotion", choices=EMOTIONS, default="neutral",
        help="Which emotion clip to bake (default: neutral).",
    )
    parser.add_argument(
        "--n", type=int, default=6,
        help="Number of audition candidates to generate (default: 6).",
    )
    parser.add_argument(
        "--ref-text", dest="ref_text", default=DEFAULT_REF_TEXT,
        help="Text spoken in the reference clip (default: DEFAULT_REF_TEXT).",
    )
    parser.add_argument(
        "--language", default=DEFAULT_LANGUAGE,
        help=f"Synthesis language (default: {DEFAULT_LANGUAGE}).",
    )
    parser.add_argument(
        "--instruct", default=None,
        help="VoiceDesign instruct (default: persona, composed per emotion).",
    )
    parser.add_argument(
        "--choose", default=None, metavar="cand_NN",
        help="Promote this candidate to the reference clip (e.g. cand_03).",
    )
    parser.add_argument(
        "--unload", action="store_true",
        help="Free VRAM when finished.",
    )
    args = parser.parse_args()

    if args.choose:
        _choose(args)
    else:
        _generate(args)


if __name__ == "__main__":
    main()
