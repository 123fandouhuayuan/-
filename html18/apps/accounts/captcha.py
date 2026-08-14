import random
import string
import io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.conf import settings


class CaptchaGenerator:
    def __init__(self, width=160, height=60, char_count=4):
        self.width = width
        self.height = height
        self.char_count = char_count
        self.char_set = string.ascii_uppercase + string.digits

    def generate_code(self):
        return ''.join(random.choices(self.char_set, k=self.char_count))

    def create_captcha_image(self, code):
        bg_color = (random.randint(220, 240), random.randint(220, 240), random.randint(220, 240))
        img = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(img)

        self.draw干扰曲线(draw, code)
        self.draw干扰点(draw)
        self.draw干扰线(draw)

        for i, char in enumerate(code):
            self.draw_char(draw, char, i)

        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

        return img

    def draw_char(self, draw, char, index):
        font_sizes = [35, 38, 40, 42, 45]
        font_size = random.choice(font_sizes)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        x = int(self.width * 0.15) + index * int((self.width * 0.7) / self.char_count)
        y = random.randint(5, int(self.height * 0.3))

        hue = random.randint(0, 360)
        color = self.hsv_to_rgb(hue, random.randint(40, 70), random.randint(30, 60))

        for offset_x in [-1, 0, 1]:
            for offset_y in [-1, 0, 1]:
                draw.text((x + offset_x, y + offset_y), char, fill=(150, 150, 150), font=font)

        draw.text((x, y), char, fill=color, font=font)

    def draw干扰曲线(self, draw, code):
        for _ in range(3):
            points = []
            start_x = random.randint(0, int(self.width * 0.2))
            start_y = random.randint(int(self.height * 0.3), int(self.height * 0.7))

            for i in range(5):
                points.append((
                    start_x + i * int(self.width * 0.2),
                    start_y + random.randint(-15, 15)
                ))

            hue = random.randint(200, 280)
            color = self.hsv_to_rgb(hue, random.randint(30, 50), random.randint(150, 200))

            for i in range(len(points) - 1):
                draw.line([points[i], points[i + 1]], fill=color, width=2)

    def draw干扰点(self, draw):
        for _ in range(150):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 2)
            hue = random.randint(0, 360)
            color = self.hsv_to_rgb(hue, random.randint(20, 50), random.randint(50, 100))
            draw.ellipse([x, y, x + size, y + size], fill=color)

    def draw干扰线(self, draw):
        for _ in range(5):
            x1 = random.randint(0, self.width)
            y1 = random.randint(0, self.height)
            x2 = random.randint(0, self.width)
            y2 = random.randint(0, self.height)
            hue = random.randint(180, 240)
            color = self.hsv_to_rgb(hue, random.randint(30, 60), random.randint(180, 220))
            width = random.randint(1, 2)
            draw.line([x1, y1, x2, y2], fill=color, width=width)

    def hsv_to_rgb(self, h, s, v):
        import colorsys
        h = h / 360.0
        s = s / 100.0
        v = v / 100.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def get_image_bytes(self, code=None):
        if code is None:
            code = self.generate_code()
        img = self.create_captcha_image(code)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', quality=85)
        buffer.seek(0)
        return code, buffer.getvalue()


def generate_captcha():
    generator = CaptchaGenerator()
    code = generator.generate_code()
    _, image_bytes = generator.get_image_bytes(code)
    return code, image_bytes


def generate_captcha_with_code(code):
    generator = CaptchaGenerator()
    _, image_bytes = generator.get_image_bytes(code)
    return image_bytes
