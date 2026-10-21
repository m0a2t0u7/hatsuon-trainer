# ElevenLabs pronunciation audio

`jessica-padded.mp3` contains the verified candidate excerpts from the user-supplied Jessica recording. Each excerpt has 0.08 seconds of leading silence and 0.42 seconds of trailing silence. `jessica-map.json` stores playback ranges, ending 0.27 seconds before the following excerpt begins. The browser streams a single audio element and stops on a 15 ms position check; it does not decode the entire recording into a Web Audio buffer.

Coverage: 810 of 938 unique vowel/consonant vocabulary spellings. This is transcript alignment and acoustic-boundary validation, not a human audit of every pronunciation. 128 words remain on device TTS because of uncertain recognition, boundaries or ambiguous pronunciations. `regenerate-words.txt` lists them; `unmatched-words.json` records the reasons in the working source. Homographs such as live/read/lead/close/use/present/record/contract/project/increase/tear/minute require meaning-specific pronunciation confirmation before replacement. British English and phrases always use device TTS.

Playback defaults to ElevenLabs where a matching clip is available; users can select device TTS in Settings. Loading/decoding/autoplay failures fall back to device TTS. Leaving the tab or turning off the screen stops playback to avoid delayed segment-end timers playing subsequent words. Screen-off/background playback is not supported.

Source audio was decoded from the original upload to 24 kHz mono PCM and encoded once at 48 kbps after excerpt selection and silence insertion. Existing learning progress and settings storage keys are preserved.

Validation: syntax check; mock tests of clip bounds, same-word repetition, cancellation during load, autoplay rejection, missing-word/British fallback and hidden-tab stop; existing loop/next-phoneme/cancellation tests. Android playback and every individual clip have not been manually audited.
