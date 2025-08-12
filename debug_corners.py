#!/usr/bin/env python3
"""
Debug script to test corner positioning on Cinnamon/X.org
Shows screen info and places test windows in all corners
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib
import sys

def create_test_window(text, corner, color):
    """Create a small test window with text"""
    window = Gtk.Window()
    window.set_decorated(False)
    window.set_skip_taskbar_hint(True)
    window.set_keep_above(True)
    
    # Create label with colored background
    label = Gtk.Label(label=text)
    label.set_margin_left(10)
    label.set_margin_right(10)
    label.set_margin_top(10)
    label.set_margin_bottom(10)
    
    # Set CSS for background color
    css_provider = Gtk.CssProvider()
    css = f"""
    window {{
        background-color: {color};
    }}
    label {{
        color: white;
        font-weight: bold;
        font-size: 14px;
    }}
    """
    css_provider.load_from_data(css.encode())
    
    style_context = window.get_style_context()
    style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    
    window.add(label)
    
    # Position window
    window.set_size_request(150, 50)
    
    # Get screen dimensions
    screen = Gdk.Screen.get_default()
    
    # Try to get monitor info
    n_monitors = screen.get_n_monitors()
    print(f"Number of monitors: {n_monitors}")
    
    for i in range(n_monitors):
        geom = screen.get_monitor_geometry(i)
        work = screen.get_monitor_workarea(i)
        print(f"Monitor {i}:")
        print(f"  Geometry: {geom.x},{geom.y} {geom.width}x{geom.height}")
        print(f"  Workarea: {work.x},{work.y} {work.width}x{work.height}")
    
    # Use primary monitor workarea
    monitor_num = screen.get_primary_monitor()
    workarea = screen.get_monitor_workarea(monitor_num)
    
    offset = 20
    width = 150
    height = 50
    
    # Calculate position
    if 'left' in corner:
        x = workarea.x + offset
    else:  # right
        x = workarea.x + workarea.width - width - offset
        
    if 'top' in corner:
        y = workarea.y + offset
    else:  # bottom
        y = workarea.y + workarea.height - height - offset
    
    window.move(x, y)
    
    # Click to close
    window.connect('button-press-event', lambda w, e: window.destroy())
    
    return window

def main():
    # Print system info
    print("=== Screen Information ===")
    screen = Gdk.Screen.get_default()
    print(f"Screen size: {screen.get_width()}x{screen.get_height()}")
    print(f"Primary monitor: {screen.get_primary_monitor()}")
    print("")
    
    # Create test windows
    windows = [
        create_test_window("TOP-LEFT\n(click to close)", "top-left", "#e74c3c"),
        create_test_window("TOP-RIGHT\n(click to close)", "top-right", "#3498db"),
        create_test_window("BOTTOM-LEFT\n(click to close)", "bottom-left", "#2ecc71"),
        create_test_window("BOTTOM-RIGHT\n(click to close)", "bottom-right", "#9b59b6"),
    ]
    
    for window in windows:
        window.show_all()
    
    print("\nTest windows created in all corners.")
    print("Click any window to close it.")
    print("Press Ctrl+C to exit.\n")
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == '__main__':
    main()
