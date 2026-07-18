import os
from PIL import Image, ImageDraw

# Create icons folder
os.makedirs('static/icons', exist_ok=True)

# Icon sizes needed
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

print("Creating PWA icons...")

for size in sizes:
    # Create image
    img = Image.new('RGB', (size, size), color=(102, 126, 234))
    draw = ImageDraw.Draw(img)
    
    # Draw circle
    margin = size // 5
    draw.ellipse([margin, margin, size - margin, size - margin], 
                 outline=(255, 255, 255), width=size//30)
    
    # Draw checkmark
    draw.line([size//2.5, size//2, size//1.8, size//1.5], 
              fill=(255, 255, 255), width=size//25)
    draw.line([size//1.8, size//1.5, size//1.3, size//2.8], 
              fill=(255, 255, 255), width=size//25)
    
    # Save
    img.save(f'static/icons/icon-{size}.png')
    print(f'✅ Created icon-{size}.png')

print("\n🎉 All icons created in static/icons/ folder")