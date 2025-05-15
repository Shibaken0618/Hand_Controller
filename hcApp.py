import cv2, tkinter as tk
from PIL import Image, ImageTk
from hand_controller import HandController

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Hand Control App')
        self.hand = HandController()

        # Canvas for video
        self.canvas_w, self.canvas_h = 640, 480
        self.canvas = tk.Canvas(root, width=self.canvas_w, height=self.canvas_h)
        self.canvas.pack()
        # Mode label
        self.mode_label = tk.Label(root, text='', font=('Arial', 14))
        self.mode_label.pack(pady=5)

        # Start update loop
        self.update_frame()
        root.protocol('WM_DELETE_WINDOW', self.on_close)
        root.mainloop()

    def update_frame(self):
        frame, mode = self.hand.next_frame()
        if frame is not None:
            # Convert BGR to RGB, then to PhotoImage
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor='nw', image=imgtk)
            self.canvas.image = imgtk
            self.mode_label.config(text=f'Mode: {mode}')
        # call again
        self.root.after(20, self.update_frame)

    def on_close(self):
        self.hand.cleanup()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    App(root)