# NVIDIA free-endpoint model panel

Verified against NVIDIA's official API Catalog and API reference on 8 September 2026.

| Model | Project role | Endpoint ID | Availability behaviour |
|---|---|---|---|
| Nemotron 3.5 Lightning 30B | Fast strategy draft | `nvidia/nemotron-3.5-lightning-30b-a3b` | Verified with the configured account; default fallback |
| Nemotron 3 Nano Omni 30B | Document/context reasoning | `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning` | Verified with the configured account |
| GPT-OSS 20B | Rubric evaluation and structured reasoning | `openai/gpt-oss-20b` | Free trial endpoint; can queue on shared capacity |
| Muse Glimmer 30B | Creative messaging and narrative options | `meta/muse-glimmer-30b` | Free endpoint; can return an empty/truncated trial response |
| Gemma 4 31B | Long-context synthesis and multilingual work | `google/gemma-4-31b-it` | Free trial endpoint; can cold-start or queue |
| DiffusionGemma 26B | Experimental low-latency generation | `google/diffusiongemma-26b-a4b-it` | Free trial endpoint; availability varies |

The NVIDIA `/v1/models` response is a catalogue, not a guarantee that one API key can invoke every model. Trial access may be model-scoped and shared endpoints may return 403, 404, 429, an empty response, or a timeout. The application records the model that actually completed the request and falls back to verified Nemotron after a short experimental-model window.

Official references:

- https://build.nvidia.com/models?label=Text-to-Text
- https://docs.api.nvidia.com/nim/reference/llm-apis
- https://docs.api.nvidia.com/nim/docs/api-quickstart
