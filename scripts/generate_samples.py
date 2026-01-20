from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SAMPLES = os.path.join(ROOT, 'samples')
os.makedirs(SAMPLES, exist_ok=True)


def make_pdf(path):
    c = canvas.Canvas(path, pagesize=letter)
    w, h = letter
    c.drawString(72, h-72, "Solar panel efficiency improves with better materials.")
    c.drawString(72, h-100, "This PDF discusses renewable energy and batteries.")
    c.showPage()
    c.drawString(72, h-72, "Wind turbines convert kinetic energy into electricity.")
    c.drawString(72, h-100, "Solar and wind are complementary sources.")
    c.save()


def make_png(path):
    img = Image.new('RGB', (320, 180), color=(240, 246, 255))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 310, 170], outline=(30, 60, 160), width=3)
    d.text((20, 20), "Sample Image: renewable", fill=(20, 40, 120))
    img.save(path)


if __name__ == '__main__':
    make_pdf(os.path.join(SAMPLES, 'sample.pdf'))
    make_png(os.path.join(SAMPLES, 'sample.png'))
    print("Generated samples in", SAMPLES)
