# Third-party components

## MathJax 3.2.2

- Upstream: https://github.com/mathjax/MathJax-src
- Package: mathjax-full 3.2.2
- Vendored file: assets/vendor/mathjax-tex-svg.js (upstream es5/tex-svg-full.js)
- License: Apache License 2.0; full text retained as assets/vendor/MathJax-LICENSE.
- The upstream component is copied without functional changes. HTML publication embeds it in the generated reader to enable offline SVG math.

## Installed PDF dependencies

scripts/requirements.txt pins pypdfium2 5.14.0, matching the locally tested runtime. bootstrap.py downloads it through pip into an isolated task-local environment when necessary. It is not vendored here; its distribution contains its own licensing notices and binary dependencies. Page images are encoded to PNG with the Python standard library; Pillow and NumPy are not required.

This notice describes third-party components and does not choose a license for the author's original Skill or tool code.
