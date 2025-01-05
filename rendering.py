import math
from multiprocessing import Queue, Pool, Manager

from model import Vec3, create_ray, intersect_shapes, visible, normalize, dot, multiply, Scene
from utils import bitmap_image

def render_block(scene: Scene, start_x: int, end_x: int, start_y: int, end_y: int,
				 q: Queue):
	"""
	Render a block of pixels in the scene.
	:param scene: Scene to render.
	:param start_x: Start x-coordinate of the block.
	:param end_x: End x-coordinate of the block.
	:param start_y: Start y-coordinate of the block.
	:param end_y: End y-coordinate of the block.
	:param q: Queue to store the results.
	"""
	block_pixels = []
	image_data_pixels = []
	for y in range(start_y, end_y):
		for x in range(start_x, end_x):
			acum = Vec3(0.0, 0.0, 0.0)
			for s in range(scene.samples_per_pixel):
				ray = create_ray(scene, x, y, s, scene.samples_per_pixel)
				isect = intersect_shapes(ray, scene.shapes)
				if isect is not None:
					for light in scene.lights:
						if visible(scene.shapes, isect.hit, light.position):
							lambertian = (1.0 / math.pi) * isect.color
							wi = normalize(light.position - isect.hit)
							theta = math.fabs(dot(isect.normal, wi))
							color = multiply(lambertian, light.intensity) * theta
							acum = acum + color
			acum = float(1.0 / scene.samples_per_pixel) * acum
			# Convert the color to rgb format
			r = min(255, int(acum.x * 256.0))
			g = min(255, int(acum.y * 256.0))
			b = min(255, int(acum.z * 256.0))
			rgb = Vec3(r, g, b)
			block_pixels.append((x, y, rgb))
			image_data_pixels.append((r, g, b))

	# Render the image
	q.put((start_x, end_x, start_y, end_y, block_pixels, image_data_pixels))
	#print(f"Block ({start_x}, {start_y}) rendered.")


def render(scene: Scene, num_workers: int, callback):
	"""Render the scene in parallel (if num_threads > 1)."""
	width, height = scene.width, scene.height

	# Split the image into blocks and render each block in parallel.
	block_width = width // num_workers
	block_height = height // num_workers
	blocks = []

	for i in range(num_workers):
		for j in range(num_workers):
			start_x = i * block_width
			end_x = width if i == num_workers - 1 else (i + 1) * block_width
			start_y = j * block_height
			end_y = height if j == num_workers - 1 else (j + 1) * block_height
			blocks.append((start_x, end_x, start_y, end_y))

	with Manager() as manager:
		q = manager.Queue()
		with Pool(processes=num_workers) as pool:
			# Render each block in parallel
			pool.starmap_async(
				render_block,
				[(scene, start_x, end_x, start_y, end_y, q) for start_x, end_x, start_y, end_y in blocks]
			)

			# Each time a block is rendered, call the callback
			num_blocks_left = len(blocks)
			while num_blocks_left > 0:
				start_x, end_x, start_y, end_y, block_pixels, image_data_pixels = q.get()
				#print(f"Block ({start_x}, {start_y}) received and image creation started.")
				image = bitmap_image(image_data_pixels, end_x - start_x, end_y - start_y)
				#print(f"Block ({start_x}, {start_y}) image created.")
				callback(block_pixels, image)
				num_blocks_left -= 1

			# Wait for the pool to finish
			pool.close()
			pool.join()

	print("All blocks rendered.")
