# Ishihara Plate Generator

A Python desktop app that generates [Ishihara-style](https://en.wikipedia.org/wiki/Ishihara_test) color blindness test plates from arbitrary text.

## Features

- Enter any text to embed it in the plate
- Pick custom text and background colors via color picker
- Adjust min/max circle radius
- Save the generated plate as PNG or JPEG
- Dense, randomized circle packing with no overlaps, mimics real Ishihara plates

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python src/app.py
```

## How it works

- Circles are randomly packed inside a circular plate boundary using a spatial hash grid for fast, dense placement.
- Each circle's center is checked against a text mask rendered from the input string.
- Circles whose centers fall on the text get the **text color**; the rest get the **background color**.
- A small random color variance is applied to each circle to mimic real Ishihara plates.
