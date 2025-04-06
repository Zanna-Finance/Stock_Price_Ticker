# CircuitPython Stock Tracker

A real-time stock ticker display using Seeed Studio hardware and the Tiingo financial data API.

## Overview

This project creates a compact, portable stock price tracker that cycles through a list of stock tickers, displaying real-time price data, movement indicators, and key trading metrics. Perfect for keeping an eye on your portfolio without needing to constantly check your phone or computer.

## Features

- Displays real-time stock prices
- Auto-rotates through multiple stock tickers
- Shows key metrics: current price, price change, bid/ask, volume, daily high/low
- Color-coded price changes (green for up, red for down)
- Automatic data refresh
- Compact and portable

## Hardware Requirements

- [Seeed Studio XIAO RP2040](https://www.seeedstudio.com/XIAO-RP2040-v1-0-p-5026.html) or compatible CircuitPython board
- [Seeed Studio Round Display for XIAO](https://www.seeedstudio.com/Seeed-Studio-Round-Display-for-XIAO-p-5593.html) - GC9A01 based 1.28" 240x240 round LCD
- USB cable for power and programming

## Software Requirements

- CircuitPython 8.x or newer
- Tiingo API key (free tier available)
- Wi-Fi network connection

## Installation

### 1. Set up CircuitPython

1. Download the latest version of CircuitPython for your board from the [CircuitPython website](https://circuitpython.org/downloads)
2. Connect your board to your computer via USB
3. Put your board in bootloader mode (usually by double-clicking the reset button)
4. Drag and drop the CircuitPython UF2 file onto the board's drive

### 2. Install Required Libraries

Download the following CircuitPython libraries from the [CircuitPython bundle](https://circuitpython.org/libraries):

- adafruit_display_text
- adafruit_requests
- adafruit_bus_device
- gc9a01.mpy

Copy these libraries to the `lib` folder on your CircuitPython device.

### 3. Get a Tiingo API Key

1. Sign up for a free account at [Tiingo](https://www.tiingo.com/account/api/token)
2. Once registered, go to your account page to get your API key
3. Keep this key secure - you'll need it for the next step

### 4. Configure the Code

1. Clone this repository or download the `code.py` file
2. Open `code.py` in a text editor
3. Update the following variables:
   - `API_KEY`: Replace with your Tiingo API key
   - `WIFI_SSID`: Your Wi-Fi network name
   - `WIFI_PASSWORD`: Your Wi-Fi password
4. Optional: Modify the `tickers` list to include your preferred stock symbols

### 5. Deploy the Code

1. Save the modified `code.py` file
2. Copy it to the root directory of your CircuitPython device
3. The code should start running automatically

## Usage

Once powered and connected to Wi-Fi, the display will:

1. Connect to your Wi-Fi network
2. Begin cycling through the stock tickers defined in the code
3. Update the display with current price data
4. Automatically refresh data at regular intervals

### Customizing the Display

- To change which stocks are displayed, modify the `tickers` list in the code
- Adjust `ticker_display_time` to control how long each stock is displayed
- Modify `update_interval` to change how frequently the data is refreshed

## Troubleshooting

- **Display shows "Error"**: Check your Wi-Fi connection and API key
- **Incorrect prices**: Ensure the API is providing data for your selected tickers
- **Display not updating**: Verify your Wi-Fi connection is stable

## Power Considerations

For portable use, consider connecting to a battery pack. The code includes power-saving features like limiting the update frequency to conserve battery life.

## Credits

- Hardware platform by [Seeed Studio](https://www.seeedstudio.com)
- Financial data provided by [Tiingo API](https://www.tiingo.com)

## License

This project is released under the MIT License.
