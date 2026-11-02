# Renders the participant PDF from enchantment.tex and the glyph images.
FROM debian:bookworm-slim AS render
RUN apt-get update && \
    apt-get install -y --no-install-recommends texlive-latex-base texlive-latex-recommended && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY enchantment.tex .
COPY assets ./assets
RUN pdflatex -interaction=nonstopmode -halt-on-error enchantment.tex

FROM scratch
COPY --from=render /build/enchantment.pdf /enchantment.pdf
