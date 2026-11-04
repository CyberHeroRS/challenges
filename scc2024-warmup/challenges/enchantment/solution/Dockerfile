FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
# challenge_assets is bind-mounted in at test time, directly from the same
# assets/ directory the "pdf" build step renders enchantment.pdf from (see
# challenge.yaml's test[0].mounts) -- the build's final stage only exports
# the rendered PDF itself (FROM scratch), not the raw glyph images/.tex
# source the solver needs to reconstruct the glyph-to-letter mapping.
COPY solv.py ./
CMD ["python", "solv.py"]
