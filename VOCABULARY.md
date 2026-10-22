# Vocabulary and recording preparation

The pronunciation practice now contains **1,500 distinct headwords** and
**1,900 sound-specific practice entries**. Existing words and progress keys are
preserved. 562 new everyday, school and workplace words were added. Six existing
words are also listed under another sound that they contain. Of the 45 sound
groups, 44 have at least 30 entries. `/ʒ/` has 20 entries: uncommon spellings were
not added just to meet a numerical quota.

Jessica audio covers 1,489 headwords: the unchanged original 810 plus 679 from
the ten user-supplied recordings. A further recording replaces 18 sentence clips;
coverage now uses 1,488 isolated words and one example sentence (`desert`).
The 11 uncertain words remain on device speech and in the pending recording list.

## Recording

Open **音声収録リスト** from the practice home or settings. It shows 1, 5, 10 or
20 words at a time (initially 10), with plain-text copy and TXT export. No spoken
numbers, pause tags or Japanese text are included in the generation script.
Some ambiguous headwords use short sentences. When word-only extraction is
uncertain, the app labels the full spoken sentence as **例文音声**. Smaller input may help isolate paste problems,
but it does not guarantee that ElevenLabs will stop freezing.

`audio/recording-manifest.json` is the canonical target/utterance/IPA mapping.
Its `batches` are the initial 10-word batches; the app can repartition the same
ordered `entries` into other batch sizes. `audio/recording-batches/` contains
the two remaining scripts (10 + 1 words), and `audio/recording-all.txt` contains the complete
plain-text script. A “created” mark in the app is preparation tracking only;
it does not change the number of integrated audio recordings.

## Pronunciation and level notes

New pronunciations were checked against the Carnegie Mellon University
Pronouncing Dictionary (CMUdict), with conventional IPA rendering and accepted
American variants. Japanese meanings and the middle-school/high-school/work
labels are editorial learning aids, not certified curriculum or CEFR levels.
The word's selected meaning matters for homographs.

CMUdict source: https://github.com/cmusphinx/cmudict

Copyright and redistribution terms: `third-party/CMUDICT-LICENSE.txt`.
Additional pronunciation spot checks used Cambridge Dictionary, including
the American pronunciation of *character* and *hoodie*.

The audio was aligned using saved ASR, script order and waveform silence.
All individual clips have not been manually listened to. Original 690-entry
recording scripts are preserved in `audio/new-20261022/archive/recording-manifest.json`. Android device audio and clipboard behavior require testing
on the user's device.
