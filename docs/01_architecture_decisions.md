# Architecture Decision Record 01: Trade-Fair Voice Kiosk Constraints

## Identified Risks and Our Architectural Responses

1. **Latency:** asynchronous streaming, local STT (Vosk), optimized TTS.
2. **Noise (trade-fair floor):** local STT with hard Voice Activity Detection (VAD)
   plus a directional hardware microphone.
3. **Hallucinations (allergens):** a deterministic rule engine (Python if/else) for
   the menu. A language model has no authority to invent ingredients.
4. **No internet (offline):** local-first architecture end to end — offline TTS
   (Piper), offline STT (Vosk); no cloud dependency for the core loop.
5. **Session memory:** a local SQLite store tracks conversation context in real time.
6. **Interface (brand image):** a native desktop app in fullscreen kiosk mode —
   zero browsers in the critical path.
7. **Lead capture (CRM):** an opt-in SQLite module for collecting consent and phone
   numbers, off by default (RODO/GDPR).
8. **Cost (tokens):** local models only — no per-request paywall after deployment.
9. **Regulatory (age-gated challenge, <16 years):** age validation lives in Python
   business logic (hardcoded rules), not only in a prompt.
10. **Control (server outages):** full cloud independence; the app runs as a
    systemd service with auto-restart.
