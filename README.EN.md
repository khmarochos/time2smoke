# Work Reminder Daemon & Corner PNG Display

<p align="center">
  <img src="cigarette.png" alt="Reminder Icon" width="128" height="128">
</p>

A lightweight GTK-based reminder system for Linux (X.org/Cinnamon) that displays transparent PNG images at specific times or positions on your screen.

## 🎯 Features

### Reminder Daemon
- **Invisible background service** - Runs hidden, no system tray icon
- **Work hours only** - Active Monday-Friday, 8:00-18:59
- **Precise timing** - Shows reminders at exact seconds (XX:47:00, XX:50:00)
- **Click to dismiss** - Single click removes the reminder
- **Multi-monitor support** - Works correctly with multiple displays
- **Panel-aware positioning** - Respects taskbars and panels

### Corner PNG Display
- **Transparent PNG support** - Full alpha channel support
- **Flexible positioning** - Any corner of the screen
- **Click to close** - Simple interaction
- **Adjustable opacity** - From fully transparent to opaque
- **Click-through mode** - Optional ghost overlay mode
- **Drag support** - Move the image around (Tkinter version)

## 📋 Requirements

### System Requirements
- Linux with X.org (tested on Cinnamon)
- Python 3.6+
- GTK 3.0+

### Python Dependencies
```bash
# For GTK version (recommended)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0

# For Tkinter version (fallback)
pip install pillow
```

## 🚀 Quick Start

### Work Reminder Daemon

```bash
# Test mode - shows reminders every 10 seconds
python3 reminder-daemon.py break.png standup.png --test

# Production mode - shows at XX:47 and XX:50 during work hours
python3 reminder-daemon.py break.png standup.png

# Run in background
nohup python3 reminder-daemon.py break.png standup.png &
```

### Corner PNG Display

```bash
# Basic usage - shows image in bottom-right corner
python3 corner-png-gtk.py logo.png

# Custom position and size
python3 corner-png-gtk.py logo.png --corner top-left --size 128 128

# Semi-transparent overlay
python3 corner-png-gtk.py watermark.png --opacity 0.5 --clickthrough
```

## 📖 Detailed Usage

### Reminder Daemon Options

```
usage: reminder-daemon.py [-h] [--corner {top-left,top-right,bottom-left,bottom-right}]
                          [--offset OFFSET] [--size WIDTH HEIGHT] [--opacity OPACITY]
                          [--sound SOUND] [--test]
                          image1 image2

positional arguments:
  image1                Image to show at XX:47:00
  image2                Image to show at XX:50:00

optional arguments:
  -h, --help           Show help message
  --corner             Corner position (default: bottom-right)
  --offset             Offset from screen edge in pixels (default: 20)
  --size WIDTH HEIGHT  Resize images to specified dimensions
  --opacity            Image opacity 0.0-1.0 (default: 1.0)
  --sound              Sound file to play with reminder
  --test               Test mode - show reminders every 10 seconds
```

### Corner PNG Display Options

```
usage: corner-png-gtk.py [-h] [--corner {top-left,top-right,bottom-left,bottom-right}]
                         [--offset OFFSET] [--size WIDTH HEIGHT] [--opacity OPACITY]
                         [--clickthrough]
                         image

positional arguments:
  image                Path to PNG image

optional arguments:
  -h, --help          Show help message
  --corner            Corner position (default: bottom-right)
  --offset            Offset from screen edge in pixels (default: 20)
  --size WIDTH HEIGHT Resize image to specified dimensions
  --opacity           Image opacity 0.0-1.0 (default: 1.0)
  --clickthrough      Make window click-through (cannot be clicked)
```

## ⚙️ Configuration

### Auto-start on Login

Create a desktop entry file:

```bash
nano ~/.config/autostart/work-reminder.desktop
```

Add the following content:

```ini
[Desktop Entry]
Type=Application
Name=Work Reminder
Comment=Shows reminder images during work hours
Exec=/usr/bin/python3 /path/to/reminder-daemon.py /path/to/image1.png /path/to/image2.png
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
```

### Custom Schedule

To modify the reminder schedule, edit the `get_reminder_type` method in `reminder-daemon.py`:

```python
def get_reminder_type(self, dt):
    minute = dt.minute
    second = dt.second
    
    # Custom schedule example:
    if minute == 0 and second == 0:  # Every hour
        return 1
    if minute == 30 and second == 0:  # Every half hour
        return 2
    
    return None
```

## 🎨 Use Cases

### Pomodoro Timer
Use the reminder daemon to signal work/break intervals:
- Image 1: "Take a break" reminder at XX:25
- Image 2: "Back to work" reminder at XX:30

### Stand-up Reminder
Remind yourself to stand and stretch:
- Image 1: "Stand up" icon at XX:50
- Image 2: "Stretch" icon at XX:55

### Meeting Alerts
Visual cues for recurring meetings:
- Image 1: "Standup meeting" at 09:45
- Image 2: "Team sync" at 14:45

### Watermark/Branding
Display a semi-transparent logo:
```bash
python3 corner-png-gtk.py company-logo.png --opacity 0.3 --clickthrough
```

## 🐛 Troubleshooting

### Images appear in wrong corner
- The scripts use `get_monitor_workarea()` to respect panels
- Run `debug-corners.py` to test corner positioning
- Check if Cinnamon panels are configured correctly

### Reminder doesn't appear
- Verify system time is correct
- Check if it's within work hours (Mon-Fri 8-18)
- Use `--test` mode to verify images load correctly
- Check image file paths are absolute

### Click-through doesn't work
- Not all window managers support click-through
- GTK version has better click-through support than Tkinter

### High CPU usage
- Normal idle CPU usage should be < 0.1%
- If high, check image file sizes (resize large images)
- Ensure you're not running multiple instances

## 🔧 Advanced Features

### Multiple Reminder Sets
Run multiple daemons with different schedules:
```bash
# Pomodoro reminders
python3 reminder-daemon.py work.png break.png --offset 20 &

# Hydration reminders  
python3 reminder-daemon.py water1.png water2.png --offset 100 &
```

### Sound Notifications
Add audio alerts to reminders:
```bash
python3 reminder-daemon.py img1.png img2.png \
    --sound /usr/share/sounds/freedesktop/stereo/bell.oga
```

### Debug Mode
Test corner positioning:
```bash
python3 debug-corners.py
```

## 📝 License

This project is provided as-is for personal and commercial use.

## 🤝 Contributing

Feel free to fork, modify, and adapt these scripts to your needs. Suggestions and improvements are welcome!

## 📚 Version History

- **v1.0** - Initial release with basic corner display
- **v2.0** - Added reminder daemon with work hours scheduling  
- **v2.1** - Fixed corner positioning for multi-monitor setups
- **v2.2** - Added click-through mode and sound support

## 💡 Tips

1. **Image Format**: Use PNG images with transparency for best results
2. **Image Size**: Keep images reasonably sized (< 500x500px) for performance
3. **Test First**: Always use `--test` mode before setting up auto-start
4. **Logs**: When running with `nohup`, check logs in `/tmp/reminder.log`
5. **Multiple Monitors**: The window appears on the monitor where your mouse is

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Test with the debug script
4. Run in test mode to isolate timing issues

---

*Stay productive and take regular breaks! 🚀*
