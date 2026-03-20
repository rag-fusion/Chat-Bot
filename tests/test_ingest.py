import os
import pytest
from backend.app.extractors import extract_pdf, extract_image


def test_extract_pdf(tmp_path):
  pdf = os.path.join('backend', 'samples', 'sample.pdf')
  if not os.path.exists(pdf):
    pytest.skip('Sample PDF not found.')
  chunks = extract_pdf(pdf, 'sample.pdf')
  assert chunks


def test_extract_image():
  img = os.path.join('backend', 'samples', 'sample.png')
  if not os.path.exists(img):
    pytest.skip('Sample image not found.')
  chunks = extract_image(img, 'sample.png')
  assert chunks


