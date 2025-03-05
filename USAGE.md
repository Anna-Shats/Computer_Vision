# Usage Guide

## Getting Started

After completing the installation process outlined in `INSTALLATION.md`, follow these instructions to run the smart eye-tracking shelf system.

## Running the System

### Basic Usage

1. Activate your virtual environment if not already active:
   ```bash
   # For Windows
   venv\Scripts\activate
   
   # For macOS/Linux
   source venv/bin/activate
   ```

2. Run the main application:
   ```bash
   python main.py
   ```

3. The system will:
   - Automatically detect connected cameras
   - Prompt you to select a camera if multiple are available
   - Open the dashboard interface

### Configuration

You can customize the system behavior by modifying the `config.py` file:

- `CAMERA_INDEX`: Specify which camera to use (default: 0)
- `DETECTION_THRESHOLD`: Adjust the confidence threshold for eye detection
- `RECORDING_ENABLED`: Enable/disable data recording
- `VISUALIZATION_LEVEL`: Set level of real-time visualization (0=none, 1=basic, 2=detailed)

### Command Line Options

```bash
# Use a specific camera
python main.py --camera 1

# Run in debug mode
python main.py --debug

# Process a pre-recorded video instead of live feed
python main.py --video path/to/video.mp4

# Specify output folder for analytics
python main.py --output path/to/output
```

## Dashboard Interface

The dashboard contains the following sections:

1. **Live View**: Shows real-time camera feed with overlay of eye-tracking data
2. **Heat Map**: Displays attention density across the shelf
3. **Product Analytics**: Lists products sorted by attention metrics
4. **Timeline Analysis**: Shows attention patterns over time
5. **Export Options**: Save data and reports in various formats

### Keyboard Shortcuts

- `Space`: Pause/resume live tracking
- `R`: Start/stop recording session
- `H`: Toggle heatmap visualization
- `S`: Save current analytics snapshot
- `Esc`: Exit application

## Data Analysis

### Exporting Data

1. Click the "Export" button in the dashboard
2. Choose from available formats: CSV, JSON, Excel, or PDF report
3. Select the time range for the data export
4. Specify the export location

### Interpreting Results

- **Attention Time**: Duration (in seconds) customers looked at each product
- **Gaze Patterns**: Sequence of products viewed in typical customer journey
- **Engagement Score**: Combined metric of frequency and duration of views
- **Blind Spots**: Areas with less than 5% of total attention

## Self-Checkout Integration

To enable eye-tracking for self-checkout systems:

1. Connect the camera facing the customer at the self-checkout kiosk
2. Run with the checkout module enabled:
   ```bash
   python main.py --mode checkout
   ```
3. The system will track eye movements during the checkout process and provide UI/UX insights

## Troubleshooting

- **Poor Tracking Performance**: Ensure adequate lighting and camera positioning
- **High CPU Usage**: Lower the VISUALIZATION_LEVEL in config.py
- **Data Not Saving**: Check write permissions for the output directory
- **Camera Not Detected**: Try specifying the camera index explicitly with --camera

## Additional Resources

- Sample data sets are available in the `data/samples/` directory
- Example reports can be found in `docs/example_reports/` 