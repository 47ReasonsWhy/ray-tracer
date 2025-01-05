import threading
import tkinter as tk
from threading import Thread
from tkinter import filedialog, messagebox, ttk

from examples import create_example_shapes, create_example_lights
from model import Vec3, Scene, Camera
from rendering import render
from utils import write_png


def load_scene():
	filepath = filedialog.askopenfilename(filetypes=[("Scene Files", "*.json"), ("All Files", "*.*")])
	if filepath:
		messagebox.showinfo("Scene loaded", f"Scene loaded from: {filepath} (placeholder, not implemented yet)")


class RayTracerGUI:
	def __init__(self, root):
		self.root = root
		self.root.title("Ray Tracer")

		# Init GUI

		# Load Scene
		self.load_button = tk.Button(root, text="Load Scene", command=load_scene)
		self.load_button.pack(pady=5)
		# Image Resolution
		tk.Label(root, text="Image Resolution (Width x Height):").pack()
		self.resolution_entry = tk.Entry(root)
		self.resolution_entry.insert(0, "320x240")
		self.resolution_entry.pack(pady=5)
		# Number of Threads
		tk.Label(root, text="Number of Threads:").pack()
		self.threads_entry = tk.Entry(root)
		self.threads_entry.insert(0, "4")
		self.threads_entry.pack(pady=5)
		# Camera Parameters
		tk.Label(root, text="Camera Parameters (Eye, LookAt, Distance):").pack()
		self.camera_entry = tk.Entry(root)
		self.camera_entry.insert(0, "0,0,0 2,0,0 800")
		self.camera_entry.pack(pady=5)
		# Control Buttons
		# Start
		self.start_button = tk.Button(root, text="Start", command=self.start_rendering)
		self.start_button.pack(pady=5)
		# Pause
		self.pause_button = tk.Button(root, text="Pause", command=self.pause_rendering, state=tk.DISABLED)
		self.pause_button.pack(pady=5)
		# Restart
		self.restart_button = tk.Button(root, text="Restart", command=self.restart_rendering, state=tk.DISABLED)
		self.restart_button.pack(pady=5)
		# Progress Visualization
		self.canvas = tk.Canvas(root, width=320, height=240, bg="black")
		self.canvas.pack(pady=10)
		# Export Button
		self.export_button = tk.Button(root, text="Export Image", command=self.export_image, state=tk.DISABLED)
		self.export_button.pack(pady=5)
		# Status Label
		self.status_label = tk.Label(root, text="Status: Idle")
		self.status_label.pack(pady=5)
		# Progress Bar
		self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=200, mode="determinate")
		self.progress_bar.pack(pady=5)

		# Internal state
		self.running = False
		self.rendering_thread = None

		self.width = 0
		self.height = 0
		self.pixels = None
		self.image_refs = []

	# self.progress = None

	def start_rendering(self):
		self.running = True
		self.status_label.config(text="Status: Rendering")
		self.start_button.config(state=tk.DISABLED)
		self.pause_button.config(state=tk.NORMAL)
		self.restart_button.config(state=tk.NORMAL)
		self.export_button.config(state=tk.DISABLED)

		# Parse input parameters
		resolution = self.resolution_entry.get()
		num_threads_input = self.threads_entry.get()
		camera_params = self.camera_entry.get()

		try:
			width, height = map(int, resolution.split("x"))
			num_threads = int(num_threads_input)
			eye, lookat, distance = camera_params.split()
			eye = Vec3(*map(float, eye.split(",")))
			lookat = Vec3(*map(float, lookat.split(",")))
			distance = float(distance)

			# Construct the scene
			scene = Scene(width=width, height=height, samples_per_pixel=1,  # for example
						  camera=Camera(eye=eye, lookat=lookat, distance=distance),
						  shapes=create_example_shapes(), lights=create_example_lights()
						  )

			# Update canvas size
			self.canvas.config(width=width, height=height)

			# Start the progress bar
			self.progress_bar.config(maximum=num_threads * num_threads, value=0)

			# Start the rendering thread
			self.rendering_thread = threading.Thread(target=self.render_work, args=(scene, num_threads))
			self.rendering_thread.start()

		except Exception as e:
			messagebox.showerror("Error", str(e))
			self.status_label.config(text="Status: Error")
			self.start_button.config(state=tk.NORMAL)
			self.pause_button.config(state=tk.DISABLED)
			self.restart_button.config(state=tk.DISABLED)
			self.export_button.config(state=tk.DISABLED)

	def pause_rendering(self):
		self.running = False
		self.status_label.config(text="Status: Paused")

	def restart_rendering(self):
		self.running = False
		self.status_label.config(text="Status: Restarting")
		self.rendering_thread.join()
		self.start_rendering()

	def render_work(self, scene: Scene, num_workers: int):
		"""Render the scene and update the GUI with the progress."""
		try:
			self.width = scene.width
			self.height = scene.height

			# Clear the pixels, canvas and image references
			self.pixels = [None for _ in range(self.width * self.height)]
			self.root.after(0, self.canvas.delete, "all")
			self.image_refs = []

			print(f"Starting parallel rendering with {num_workers} threads...")

			# Define the callback that the producer will call to update the GUI
			def callback(block_pixels, image):
				self.root.after(0, self.update_gui, block_pixels, image)

			# Start the producer
			producer = Thread(target=render, args=(scene, num_workers, callback), daemon=True)
			producer.start()
			# Wait for the producer to finish
			producer.join()

			# Finalize rendering
			self.status_label.config(text="Status: Finished successfully")
			self.export_button.config(state=tk.NORMAL)

		except Exception as e:
			messagebox.showerror("Error", str(e))
			self.status_label.config(text="Status: Error")
			self.export_button.config(state=tk.DISABLED)
		finally:
			self.running = False
			self.start_button.config(state=tk.NORMAL)
			self.pause_button.config(state=tk.DISABLED)
			self.restart_button.config(state=tk.DISABLED)

	def update_gui(self, block_pixels: list, image: tk.PhotoImage):
		"""Update the pixel colors and the canvas."""
		# Get image anchor (top-left corner)
		anchor_x = block_pixels[0][0]
		anchor_y = block_pixels[0][1]
		# print(f"Drawing image on ({anchor_x}, {anchor_y})")
		self.root.after(0, self.draw_image, image, anchor_x, anchor_y)
		for x, y, color in block_pixels:
			# Store the pixel color
			self.pixels[y * self.width + x] = color
		# Update the progress bar
		self.progress_bar.step()

	def draw_image(self, image: tk.PhotoImage, x: int, y: int):
		"""Draw the image on the canvas."""
		self.image_refs.append(image)
		self.canvas.create_image(x, y, anchor=tk.NW, image=image)
		self.canvas.update()

	def export_image(self):
		if self.pixels is None:
			messagebox.showerror("Error", "No image to export. The button should have been disabled.")
			return

		filepath = filedialog.asksaveasfilename(defaultextension=".png",
												filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")])
		if filepath:
			try:
				write_png(self.pixels, self.width, self.height, filename=filepath)
				messagebox.showinfo("Image exported", f"Image saved to: {filepath}")
			except Exception as e:
				messagebox.showerror("Error while exporting image", str(e))


if __name__ == "__main__":
	tk_root = tk.Tk()
	app = RayTracerGUI(tk_root)
	tk_root.mainloop()
