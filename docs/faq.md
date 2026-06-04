# FAQ

### Is it really free?

Yes. The tool, the models (Real-ESRGAN, GFPGAN), and all dependencies are
open-source. There are no accounts, quotas, watermarks, or paid tiers. Everything
runs locally.

### Do my images get uploaded anywhere?

No. Processing happens entirely on your machine. The only network access is a
one-time download of the model weights from their official release pages (which
you can disable with `--no-download` after pre-seeding the cache).

### What does "16× better quality" actually mean?

It means **16× the resolution** (pixel width and height) with AI-reconstructed
detail and sharpness. Super-resolution invents plausible detail based on what it
learned during training — it cannot recover information that was never captured.
See [How it works](how-it-works.md#honest-expectations).

### Which model should I use?

- Photographs and general images → `general` (a.k.a. `photo`).
- Anime, illustrations, line art → `anime`.

### It's slow / using lots of memory. Help?

- On CPU, use a GPU if you can — it's dramatically faster.
- Reduce `--scale`, or process at 4× twice instead of 16× in one go.
- Add `--tile 256` (or smaller) to cap memory use on large images / small GPUs.

### I get a `basicsr` / `functional_tensor` import error.

Newer `torchvision` removed `torchvision.transforms.functional_tensor`, which old
`basicsr` releases import. Workarounds:

- Pin `torchvision<0.17`, or
- Patch the single import in BasicSR
  (`functional_tensor` → `functional`), or
- Use the `lanczos` backend (`-b lanczos`) if you don't need AI super-resolution.

### Can I run it without installing PyTorch?

Yes — `pip install image-upscaler` (without `[ai]`) gives you the Lanczos backend,
which is a high-quality classical resize. Use `-b lanczos`.

### Which image formats are supported?

Input: PNG, JPEG, WebP, BMP, TIFF. Output: any of those — choose with `-f/--format`
(defaults to the source format). Alpha channels are preserved where the format
supports them.

### Does it work on Windows / macOS / Linux?

Yes, all three. The base package and the test suite are exercised on all three in
CI.

### How do I process a whole folder?

```bash
upscale run ./folder -o ./out -s 4 --recursive
```

### Where are model weights stored?

In `~/.cache/image-upscaler/weights/` by default, or wherever
`IMAGE_UPSCALER_CACHE` points.
