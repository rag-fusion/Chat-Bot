import os
import pytest
from backend.app.extractors import extract_pdf, extract_docx, extract_image


def test_extract_pdf():
  pdf = os.path.join('samples', 'sample.pdf')
  if not os.path.exists(pdf):
    pytest.skip('Sample PDF not found. Run: python backend/scripts/generate_samples.py')
  chunks = extract_pdf(pdf, 'sample.pdf')
  assert any('Solar panel' in c.content for c in chunks)


def test_extract_image():
  img = os.path.join('samples', 'sample.png')
  if not os.path.exists(img):
    pytest.skip('Sample image not found. Run: python backend/scripts/generate_samples.py')
  chunks = extract_image(img, 'sample.png')
  assert len(chunks) == 1
  assert 'Image:' in chunks[0].content


