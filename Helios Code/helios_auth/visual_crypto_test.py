from PIL import Image, ImageDraw
import random
import base64
from io import BytesIO

# Function to decode Base64 string into PIL Image
def decode_base64_to_image(base64_str):
    image_data = base64.b64decode(base64_str)
    return Image.open(BytesIO(image_data))

def encode_image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


# Function to generate visual cryptography shares from original image
def generate_visual_cryptography_shares(original_image):
    width, height = original_image.size
    share1 = Image.new('1', (width * 2, height))  # Share 1 will be twice as wide as original image
    share2 = Image.new('1', (width * 2, height))  # Share 2 will be twice as wide as original image
    draw1 = ImageDraw.Draw(share1)
    draw2 = ImageDraw.Draw(share2)
    
    for y in range(height):
        for x in range(width):
            r, g, b = original_image.getpixel((x, y))
            intensity = (r + g + b) // 3  # Compute the average intensity
            if intensity < 128:  # Dark pixel
                draw1.point((2*x, y), fill=0)  # Share 1 pixel (black)
                draw2.point((2*x+1, y), fill=255)  # Share 2 pixel (white)
            else:  # Light pixel
                draw1.point((2*x, y), fill=255)  # Share 1 pixel (white)
                draw2.point((2*x+1, y), fill=0)  # Share 2 pixel (black)



    
    return share1, share2


def combine_visual_cryptography_shares(share1, share2):
    width, height = share1.size
    combined_image = Image.new('1', (width // 2, height))  # Combined image will be half as wide as share
    
    for y in range(height):
        for x in range(width // 2):
            pixel1 = share1.getpixel((x, y))
            pixel2 = share2.getpixel((x, y))
            combined_pixel = min(pixel1, pixel2)  # Combine pixels by taking the minimum value
            combined_image.putpixel((x, y), combined_pixel)
    
    return combined_image

# def combine_visual_cryptography_shares(share1, share2):
#     width, height = share1.size
#     combined_image = Image.new('1', (width // 2, height))  # Combined image will be half as wide as share
    
#     combined_image.paste(share1, (0, 0))
#     combined_image.paste(share2, (width // 2, 0))
    
#     return combined_image




# Example usage
if __name__ == "__main__":
    # Example Base64 encoded image string
    base64_str1 = ""

    # Decode Base64 string into PIL Image (assuming 'original_image_base64' contains the Base64 string)
    original_image = decode_base64_to_image(base64_str1)
    original_image.show()

    # Generate visual cryptography shares from the original image
    share1, share2 = generate_visual_cryptography_shares(original_image)
    share1.show()
    share2.show()

    # Combine the shares back into the original image
    combined_image = combine_visual_cryptography_shares(share1, share2)
    combined_image.show()

    # Optionally, encode the combined image into a Base64 string
    combined_image_base64 = encode_image_to_base64(combined_image)
    print(combined_image_base64)

