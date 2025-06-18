import tkinter as tk
import sys # Import sys module
import math # For calculations in drawing

# --- Roulette Data ---
EUROPEAN_WHEEL_SEQUENCE = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
GREEN_NUMBER = 0

def get_number_color(number):
    if number == GREEN_NUMBER:
        return "green"
    elif number in RED_NUMBERS:
        return "red"
    elif number in BLACK_NUMBERS:
        return "black"
    return "gray" # Should not happen for valid numbers

# Main application file for Om Namo Roulette
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Om Namo European Roulette Analyzer")

    # --- Main Frames for Layout ---
    left_frame = tk.Frame(root)
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10) # expand=False for left

    right_frame = tk.Frame(root) # Will hold the canvas
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Controls and History (in left_frame) ---
    controls_frame = tk.Frame(left_frame) # Frame for entry and buttons
    controls_frame.pack(pady=5)

    entry_label = tk.Label(controls_frame, text="Enter Number:")
    entry_label.pack(pady=(0,5)) # Padding below label
    number_entry = tk.Entry(controls_frame, width=30) # Give entry a bit more width
    number_entry.pack(pady=(0,10)) # Padding below entry

    results_history = []

    # history_listbox needs to be defined before new_add_number and new_reset_data if they use it directly
    # However, update_listbox is defined later but captures history_listbox from the main scope.
    # This is fine in Python as long as history_listbox is assigned before update_listbox is called.
    history_listbox = tk.Listbox(left_frame, height=15, width=30) # Create here

    def update_listbox():
        history_listbox.delete(0, tk.END)
        for item in results_history:
            history_listbox.insert(tk.END, item)

    # Original add_number and reset_data are effectively replaced by new_add_number and new_reset_data
    # No need for original_add_number = add_number etc. anymore.

    def new_add_number():
        try:
            num_str = number_entry.get()
            num = int(num_str)
            if 0 <= num <= 36:
                results_history.append(num)
                number_entry.delete(0, tk.END)
                update_listbox()
            else:
                print("Invalid input. Please enter a number between 0 and 36.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

    def new_reset_data():
        results_history.clear()
        print("Data reset.")
        update_listbox()

    button_frame = tk.Frame(controls_frame) # Frame for buttons for better organization
    button_frame.pack()

    add_button = tk.Button(button_frame, text="Add Result", command=new_add_number)
    add_button.pack(side=tk.LEFT, padx=5, pady=(0,5))

    reset_button = tk.Button(button_frame, text="Reset Data", command=new_reset_data)
    reset_button.pack(side=tk.LEFT, padx=5, pady=(0,5))

    # Listbox to display history - moved creation up, just pack it here
    history_listbox.pack(pady=10, fill=tk.BOTH, expand=True) # Fill and expand in left_frame

    # --- Roulette Wheel Canvas (in right_frame) ---
    wheel_canvas = tk.Canvas(right_frame, width=300, height=300, bg="ivory") # Changed bg for distinction
    wheel_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0,5)) # Pack at top, add padding below

    # --- Roulette Table Canvas (in right_frame) ---
    table_canvas = tk.Canvas(right_frame, width=300, height=250, bg="lightgray") # Adjusted size
    table_canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(5,0)) # Pack at bottom

    def draw_roulette_wheel(canvas, sequence):
        canvas.delete("all") # Clear previous drawings if any
        width = int(canvas.winfo_width()) # Use actual width after packing
        height = int(canvas.winfo_height()) # Use actual height after packing

        # If dimensions are too small (e.g. before window is fully drawn), use configured ones or default
        if width < 50: width = int(canvas.cget("width"))
        if height < 50: height = int(canvas.cget("height"))

        center_x, center_y = width / 2, height / 2
        radius = min(width, height) / 2 * 0.9  # 90% of half size

        num_segments = len(sequence)
        if num_segments == 0: return # Avoid division by zero
        angle_step = 360.0 / num_segments

        for i, number_val in enumerate(sequence): # Renamed 'number' to 'number_val' to avoid conflict
            start_angle = i * angle_step
            extent = angle_step

            color = get_number_color(number_val)

            canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle - 90 + (angle_step / 2), # Corrected option: start
                extent=extent,
                fill=color,
                outline="black",
                width=1
            )

            text_angle_rad = math.radians(start_angle + extent / 2 - 90 + (angle_step / 2)) # Align with arc center
            text_radius_factor = 0.70 # Slightly closer to center

            text_x = center_x + radius * text_radius_factor * math.cos(text_angle_rad)
            text_y = center_y + radius * text_radius_factor * math.sin(text_angle_rad)

            text_color = "white" if color != "gray" else "black"
            if number_val == GREEN_NUMBER : text_color = "white" # Ensure 0 is white on green

            canvas.create_text(text_x, text_y, text=str(number_val), fill=text_color, font=("Arial", 8, "bold")) # Smaller font

    # Call drawing function after a delay to allow canvas to get its size
    # Or bind to <Configure> event for dynamic redraw
    root.update_idletasks() # Process pending geometry calculations
    draw_roulette_wheel(wheel_canvas, EUROPEAN_WHEEL_SEQUENCE)

    def draw_roulette_table(canvas):
        canvas.delete("all")
        width = int(canvas.winfo_width())
        height = int(canvas.winfo_height())
        if width < 50: width = int(canvas.cget("width"))
        if height < 50: height = int(canvas.cget("height"))

        # Define layout parameters
        num_rows = 12
        num_cols = 3
        padding = 5

        # Zero box (spans top)
        zero_box_height = (height - (num_rows + 1) * padding) / (num_rows + 1) # approx height of one number box
        zero_box_width = width - 2 * padding
        canvas.create_rectangle(padding, padding,
                                padding + zero_box_width, padding + zero_box_height,
                                fill=get_number_color(0), outline="black")
        canvas.create_text(padding + zero_box_width / 2, padding + zero_box_height / 2,
                           text="0", fill="white", font=("Arial", 10, "bold"))

        box_width = (width - (num_cols + 1) * padding) / num_cols
        box_height = (height - zero_box_height - (num_rows + 2) * padding) / num_rows # +2 for padding around zero and bottom

        # Numbered boxes (1-36)
        for number_val in range(1, 37):
            # Determine column and row
            col_index = (number_val - 1) % num_cols
            row_index = (number_val - 1) // num_cols

            # Calculate box coordinates
            x1 = padding + col_index * (box_width + padding)
            y1 = padding + zero_box_height + padding + row_index * (box_height + padding)
            x2 = x1 + box_width
            y2 = y1 + box_height

            color = get_number_color(number_val)
            text_color = "white" if color in ["red", "black"] else "black"

            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            canvas.create_text(x1 + box_width / 2, y1 + box_height / 2,
                               text=str(number_val), fill=text_color, font=("Arial", 10, "bold"))

    draw_roulette_table(table_canvas)
    # wheel_canvas.bind("<Configure>", lambda event: draw_roulette_wheel(wheel_canvas, EUROPEAN_WHEEL_SEQUENCE))
    # table_canvas.bind("<Configure>", lambda event: draw_roulette_table(table_canvas))


    # --- Verification Section ---
    print("Initial state: UI elements should be created.")
    if not (number_entry.winfo_exists() and add_button.winfo_exists() and
            reset_button.winfo_exists() and history_listbox.winfo_exists() and
            wheel_canvas.winfo_exists() and table_canvas.winfo_exists()): # Added table_canvas check
        print("ERROR: UI elements (including Canvas and Table Canvas) not created as expected.")
        root.destroy()
        sys.exit(1)

    if len(wheel_canvas.find_all()) == 0:
        print("WARNING: Roulette wheel canvas is empty.")
    if len(table_canvas.find_all()) == 0: # Check for table_canvas items
        print("WARNING: Roulette table canvas is empty.")

    print(f"Initial results_history: {results_history}")
    print(f"Initial listbox_contents: {history_listbox.get(0, tk.END)}")

    # Simulate adding valid numbers, including duplicates, in specific order
    print("\nSimulating valid number additions (chronological, with duplicates):")
    # Sequence: 5, 10, 5
    number_entry.insert(0, "5")
    add_button.invoke()
    print(f"After adding '5': results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")

    number_entry.insert(0, "10")
    add_button.invoke()
    print(f"After adding '10': results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")

    number_entry.insert(0, "5") # Add 5 again (duplicate)
    add_button.invoke()
    print(f"After adding '5' again: results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")

    number_entry.insert(0, "0")
    add_button.invoke()
    print(f"After adding '0': results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")


    # Simulate adding invalid number (out of range)
    print("\nSimulating invalid number (out of range):")
    number_entry.insert(0, "37")
    add_button.invoke()
    print(f"After attempting '37': results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")

    # Simulate adding invalid input (not a number)
    print("\nSimulating invalid input (text):")
    number_entry.insert(0, "abc")
    add_button.invoke()
    print(f"After attempting 'abc': results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")

    # Simulate reset
    print("\nSimulating reset:")
    reset_button.invoke()
    print(f"After reset: results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")

    # Simulate adding after reset
    print("\nSimulating add after reset:")
    number_entry.delete(0, tk.END)
    number_entry.insert(0, "5")
    add_button.invoke()
    print(f"After adding '5' post-reset: results_history={results_history}, listbox={history_listbox.get(0, tk.END)}")

    # Final check: listbox content vs results_history
    # Note: listbox.get returns tuple of strings, results_history is list of ints
    listbox_content_as_int = tuple(map(int, history_listbox.get(0, tk.END)))
    if tuple(results_history) == listbox_content_as_int:
        print("\nFinal check: Listbox content matches results_history.")
    else:
        print(f"\nERROR: Listbox content {listbox_content_as_int} does not match results_history {results_history}.")

    print("\nVerification complete.")
    root.destroy() # Clean up the window
