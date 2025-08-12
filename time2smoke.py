#!/usr/bin/env python3
"""
Work hours reminder daemon
Shows different images at specific minutes during Mon-Fri 8-18
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import cairo
import sys
import argparse
import datetime
import time
import threading
import os
import signal

class ReminderWindow(Gtk.Window):
    """Single-click dismissable reminder window"""
    def __init__(self, image_path, corner='bottom-right', offset=20, size=None, opacity=1.0):
        super().__init__()
        
        self.image_path = image_path
        self.corner = corner
        self.offset = offset
        self.opacity = opacity
        
        # Load the image
        try:
            self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(image_path)
            if size:
                width, height = size
                self.pixbuf = self.pixbuf.scale_simple(width, height, GdkPixbuf.InterpType.BILINEAR)
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            return
        
        self.setup_window()
        
    def setup_window(self):
        # Window setup
        self.set_decorated(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)  # Notification type for reminders
        
        # Set window size
        img_width = self.pixbuf.get_width()
        img_height = self.pixbuf.get_height()
        self.set_default_size(img_width, img_height)
        self.set_size_request(img_width, img_height)
        
        # Make window transparent
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        
        # Position the window
        self.position_window(img_width, img_height)
        
        # Drawing area
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.connect('draw', self.on_draw)
        self.add(self.drawing_area)
        
        # Click to dismiss
        self.connect("button-press-event", self.on_button_press)
        
    def position_window(self, width, height):
        # Get screen dimensions - more reliable method
        screen = Gdk.Screen.get_default()
        
        # Get the monitor where the mouse is (or primary)
        display = Gdk.Display.get_default()
        seat = display.get_default_seat()
        pointer = seat.get_pointer()
        _, x_mouse, y_mouse = pointer.get_position()
        monitor_num = screen.get_monitor_at_point(x_mouse, y_mouse)
        
        # Get the actual monitor geometry (considering panels)
        monitor_geom = screen.get_monitor_geometry(monitor_num)
        
        # Get workarea (excludes panels/taskbars)
        workarea = screen.get_monitor_workarea(monitor_num)
        
        # Use workarea for more accurate positioning
        screen_x = workarea.x
        screen_y = workarea.y
        screen_width = workarea.width
        screen_height = workarea.height
        
        # Calculate position based on corner
        if 'left' in self.corner:
            x = screen_x + self.offset
        else:  # right
            x = screen_x + screen_width - width - self.offset
            
        if 'top' in self.corner:
            y = screen_y + self.offset
        else:  # bottom
            y = screen_y + screen_height - height - self.offset
        
        self.move(x, y)
    
    def on_draw(self, widget, cr):
        Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
        cr.paint_with_alpha(self.opacity)
        return False
    
    def on_button_press(self, widget, event):
        # Any click dismisses the window
        self.destroy()
        return True

class ReminderDaemon:
    """Daemon that monitors time and shows reminders"""
    def __init__(self, image1, image2, corner='bottom-right', offset=20, size=None, 
                 opacity=1.0, sound=None, test_mode=False):
        self.image1 = image1
        self.image2 = image2
        self.corner = corner
        self.offset = offset
        self.size = size
        self.opacity = opacity
        self.sound = sound
        self.test_mode = test_mode
        self.current_window = None
        self.running = True
        
        # Validate images exist
        for img in [image1, image2]:
            if not os.path.exists(img):
                print(f"Error: Image file not found: {img}")
                sys.exit(1)
        
        # Set up signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
    def handle_signal(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\nShutting down reminder daemon...")
        self.running = False
        Gtk.main_quit()
        sys.exit(0)
    
    def is_work_time(self, dt):
        """Check if current time is Mon-Fri 8-18"""
        # In test mode, always return True
        if self.test_mode:
            return True
            
        # Monday = 0, Sunday = 6
        if dt.weekday() > 4:  # Saturday or Sunday
            return False
        
        # Check if between 8:00 and 18:59
        if 8 <= dt.hour < 19:
            return True
        
        return False
    
    def get_reminder_type(self, dt):
        """Determine which reminder to show based on time"""
        minute = dt.minute
        second = dt.second
        
        # In test mode, trigger more frequently
        if self.test_mode:
            # Every 10 seconds alternating
            if second % 20 < 10:
                return 1
            else:
                return 2
        
        # Check for XX:47:00
        if minute == 47 and second == 0:
            return 1
        
        # Check for XX:50:00
        if minute == 50 and second == 0:
            return 2
        
        return None
    
    def show_reminder(self, image_num):
        """Show the reminder window with specified image"""
        def _show():
            # Dismiss any existing window
            if self.current_window:
                self.current_window.destroy()
            
            # Choose image
            image_path = self.image1 if image_num == 1 else self.image2
            
            # Create and show new window
            self.current_window = ReminderWindow(
                image_path, 
                self.corner, 
                self.offset, 
                self.size, 
                self.opacity
            )
            self.current_window.show_all()
            
            # Play sound if specified
            if self.sound:
                os.system(f"paplay {self.sound} 2>/dev/null || aplay {self.sound} 2>/dev/null &")
            
            print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Showing reminder #{image_num}")
            
        # Schedule in GTK main thread
        GLib.idle_add(_show)
    
    def monitor_loop(self):
        """Background thread that monitors time"""
        last_shown = None
        
        while self.running:
            now = datetime.datetime.now()
            
            if self.is_work_time(now):
                reminder_type = self.get_reminder_type(now)
                
                if reminder_type:
                    # Create a unique key for this reminder moment
                    current_moment = f"{now.hour}:{now.minute}:{reminder_type}"
                    
                    # Only show if we haven't shown this exact reminder yet
                    if current_moment != last_shown:
                        self.show_reminder(reminder_type)
                        last_shown = current_moment
                        
                        # In test mode, sleep less
                        if self.test_mode:
                            time.sleep(5)
                        else:
                            time.sleep(1)  # Wait a second to avoid repeated triggers
            
            # Sleep a bit before next check
            time.sleep(0.5 if self.test_mode else 0.9)
    
    def run(self):
        """Start the daemon"""
        print(f"Reminder daemon started!")
        print(f"Image 1: {self.image1}")
        print(f"Image 2: {self.image2}")
        print(f"Schedule: Mon-Fri 8-18, at XX:47 and XX:50")
        
        if self.test_mode:
            print("TEST MODE: Showing reminders every 10 seconds")
        
        print("Press Ctrl+C to stop")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        monitor_thread.start()
        
        # Run GTK main loop
        Gtk.main()

def main():
    parser = argparse.ArgumentParser(
        description='Work hours reminder daemon - shows images at specific times',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Normal operation with two reminder images
  %(prog)s break.png standup.png
  
  # With custom position and size
  %(prog)s reminder1.png reminder2.png --corner top-right --size 200 200
  
  # Test mode (shows every 10 seconds)
  %(prog)s img1.png img2.png --test
  
  # With sound notification
  %(prog)s img1.png img2.png --sound /usr/share/sounds/freedesktop/stereo/bell.oga
        """
    )
    
    parser.add_argument('image1', help='Image to show at XX:47:00')
    parser.add_argument('image2', help='Image to show at XX:50:00')
    parser.add_argument('--corner', choices=['top-left', 'top-right', 'bottom-left', 'bottom-right'],
                       default='bottom-right', help='Corner position (default: bottom-right)')
    parser.add_argument('--offset', type=int, default=20, 
                       help='Offset from screen edge in pixels (default: 20)')
    parser.add_argument('--size', nargs=2, type=int, metavar=('WIDTH', 'HEIGHT'),
                       help='Resize images to WIDTH HEIGHT')
    parser.add_argument('--opacity', type=float, default=1.0,
                       help='Image opacity 0.0-1.0 (default: 1.0)')
    parser.add_argument('--sound', help='Sound file to play with reminder')
    parser.add_argument('--test', action='store_true', 
                       help='Test mode - show reminders every 10 seconds')
    
    args = parser.parse_args()
    
    # Validate opacity
    if not 0.0 <= args.opacity <= 1.0:
        print("Error: Opacity must be between 0.0 and 1.0")
        sys.exit(1)
    
    # Create and run daemon
    daemon = ReminderDaemon(
        args.image1,
        args.image2,
        corner=args.corner,
        offset=args.offset,
        size=tuple(args.size) if args.size else None,
        opacity=args.opacity,
        sound=args.sound,
        test_mode=args.test
    )
    
    try:
        daemon.run()
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == '__main__':
    main()
