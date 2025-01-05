from model import Sphere, Vec3, PointLight, Camera, Scene
from rendering import render
from utils import write_png


def create_example_shapes():
	shapes = [
		Sphere(position=Vec3(2.0, -0.12, 0.0), radius=0.2, color=Vec3(1.0, 0.4, 0.4)),
		Sphere(position=Vec3(1.5, 0.1, 0.1), radius=0.1, color=Vec3(1.0, 1.0, 0.4)),
		Sphere(position=Vec3(1.7, 0.1, -0.15), radius=0.1, color=Vec3(0.4, 0.4, 1.0)),
	]
	return shapes


def create_example_lights():
	lights = [
		PointLight(position=Vec3(0.0, 0.0, 0.0), intensity=Vec3(1.0, 1.0, 1.0)),
		PointLight(position=Vec3(1.0, 2.0, 0.0), intensity=Vec3(3.0, 3.0, 3.0)),
	]
	return lights


def create_example_scene():
	camera = Camera(eye=Vec3(0.0, 0.0, 0.0), lookat=Vec3(2.0, 0.0, 0.0), distance=800.0)
	shapes = create_example_shapes()
	lights = create_example_lights()
	width = 320
	height = 240
	samples_per_pixel = 1

	scene = Scene(width=width, height=height, samples_per_pixel=samples_per_pixel,
				  camera=camera, shapes=shapes, lights=lights)
	return scene


def run_example():
	scene = create_example_scene()
	pixels = render(scene=scene, num_workers=1)
	write_png(pixels, scene.width, scene.height, "test.png")
