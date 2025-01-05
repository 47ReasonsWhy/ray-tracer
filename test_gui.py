import tkinter as tk
import threading
import time
import random


def render_block(canvas, block_data, block_coords):
	"""
	Update the canvas with a single rendered block.
	"""
	x1, y1, x2, y2 = block_coords
	color = block_data  # Simulating rendering data as color
	canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)


def rendering_task(callback):
	"""
	Simulate a long-running rendering process. Calls the callback with data for each block.
	"""
	for i in range(10):  # Simulate 10 blocks being rendered
		time.sleep(0.5)  # Simulate time to render a block
		# Generate random color and coordinates for a block
		color = random.choice(["#FF5733", "#33FF57", "#3357FF", "#FFFF33", "#FF33FF"])
		x1, y1 = i * 50, 0
		x2, y2 = x1 + 50, 50
		callback(color, (x1, y1, x2, y2))  # Callback to update the GUI


def start_rendering():
	"""
	Start the rendering process in a thread.
	"""

	def update_gui(color, coords):
		root.after(0, render_block, canvas, color, coords)  # Update canvas safely

	threading.Thread(target=rendering_task, args=(update_gui,), daemon=True).start()


# Setup Tkinter GUI
root = tk.Tk()
root.title("Rendering Example")

canvas = tk.Canvas(root, width=500, height=50, bg="white")
canvas.pack(pady=10)

start_button = tk.Button(root, text="Start Rendering", command=start_rendering)
start_button.pack()

root.mainloop()
