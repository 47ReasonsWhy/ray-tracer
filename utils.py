from PIL import ImageTk, Image
from PIL.Image import Transpose


def write_raw_png(buf, width, height):
	import zlib
	import struct
	width_byte_4 = width * 4
	raw_data = b"".join(
		b'\x00' + buf[span:span + width_byte_4] for span in range((height - 1) * width * 4, -1, - width_byte_4))

	def png_pack(png_tag, data):
		chunk_head = png_tag + data
		return struct.pack("!I", len(data)) + chunk_head + struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head))

	return b"".join([
		b'\x89PNG\r\n\x1a\n',
		png_pack(b'IHDR', struct.pack("!2I5B", width, height, 8, 6, 0, 0, 0)),
		png_pack(b'IDAT', zlib.compress(raw_data, 9)),
		png_pack(b'IEND', b'')])


def write_png(pixels, width, height, filename='output.png'):
	# RGBA format
	buf = bytearray()
	for y in range(height):
		for x in range(width):
			p = pixels[y * width + x]
			# r = min(255, int(p.x * 256.0))
			# g = min(255, int(p.y * 256.0))
			# b = min(255, int(p.z * 256.0))
			buf.append(p.x)  # r
			buf.append(p.y)  # g
			buf.append(p.z)  # b
			buf.append(255)

	data = write_raw_png(buf, width=width, height=height)
	with open(filename, 'wb') as fp:
		fp.write(data)


def bitmap_image(pixels, width, height):
	"""Convert the pixel colors to a bitmap image."""
	# Convert the pixels to the PhotoImage format (this is done as a string of hex values)
	# photo_data = ''.join(f'{r:02x}{g:02x}{b:02x}' for r, g, b in pixels)

	# Create a PhotoImage using the RGB data
	# print("Creating PhotoImage...")
	image = Image.new("RGB", (width, height))

	# Convert the image to a format that tkinter can display
	# photo_image = PhotoImage(width=width, height=height)

	# print("Putting data...")
	# photo_image.put(photo_data)
	image.putdata(pixels)

	# Flip the image vertically since the origin is in the top-left corner
	image = image.transpose(Transpose.FLIP_TOP_BOTTOM)

	# print("Returning PhotoImage...")
	# return photo_image
	return ImageTk.PhotoImage(image)
