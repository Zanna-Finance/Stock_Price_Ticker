import board
import busio
import displayio
import terminalio
import time
import digitalio
import gc9a01
import wifi
import socketpool
import ssl
import adafruit_requests
from adafruit_display_text import label

# Release any displays
displayio.release_displays()

# API key and base URL for Tiingo
API_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BASE_URL = "https://api.tiingo.com/iex/"

# Wi-Fi connection settings
WIFI_SSID = "WIFI_NAME"
WIFI_PASSWORD = "WIFI_PASSWORD"

# Define pins
tft_dc = board.D3
tft_cs = board.D1
tft_bl = board.D6

# Set up SPI display
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = gc9a01.GC9A01(display_bus, width=240, height=240, rotation=0)

# Backlight
backlight = digitalio.DigitalInOut(tft_bl)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = True

# Connect to WiFi
print("Connecting to WiFi...")
wifi.radio.connect(WIFI_SSID, WIFI_PASSWORD)
print(f"Connected to {WIFI_SSID}")
print(f"IP Address: {wifi.radio.ipv4_address}")

# Create session for API requests
pool = socketpool.SocketPool(wifi.radio)
session = adafruit_requests.Session(pool, ssl.create_default_context())

# Create display groups
main_group = displayio.Group()
display.root_group = main_group

# Create bitmap for background
bg_bitmap = displayio.Bitmap(240, 240, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x000033  # Dark blue background
bg_sprite = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
main_group.append(bg_sprite)

# Create header rectangle
header_bitmap = displayio.Bitmap(240, 40, 1)
header_palette = displayio.Palette(1)
header_palette[0] = 0x000044  # Slightly lighter blue for header
header_sprite = displayio.TileGrid(header_bitmap, pixel_shader=header_palette)
main_group.append(header_sprite)

# Stock info UI Labels - use only terminalio font to keep it simple
stock_label = label.Label(terminalio.FONT, text="Loading...", color=0xFFFFFF, scale=2)
stock_label.x = 70
stock_label.y = 20
main_group.append(stock_label)

price_label = label.Label(terminalio.FONT, text="--", color=0xFFFFFF, scale=3)
price_label.x = 60
price_label.y = 80
main_group.append(price_label)

change_label = label.Label(terminalio.FONT, text="--", color=0xFFFFFF, scale=2)
change_label.x = 60
change_label.y = 110
main_group.append(change_label)

bid_ask_label = label.Label(terminalio.FONT, text="B:-- A:--", color=0xFFFFFF)
bid_ask_label.x = 40
bid_ask_label.y = 140
main_group.append(bid_ask_label)

volume_label = label.Label(terminalio.FONT, text="Vol:--", color=0xFFFFFF)
volume_label.x = 40
volume_label.y = 160
main_group.append(volume_label)

high_low_label = label.Label(terminalio.FONT, text="H:-- L:--", color=0xFFFFFF)
high_low_label.x = 40
high_low_label.y = 180
main_group.append(high_low_label)

status_label = label.Label(terminalio.FONT, text="--", color=0xAAAAAA)
status_label.x = 60
status_label.y = 220
main_group.append(status_label)

# List of stock tickers to display
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA"]
current_ticker_index = 0

# Ticker timing settings
ticker_display_time = 10  # seconds to display each stock
last_ticker_change = time.monotonic()

# Helper: Format price with color
def format_price_change(current, prev_close):
    if prev_close is None or current is None:
        return "--", 0xFFFFFF
    
    change = current - prev_close
    pct_change = (change / prev_close) * 100 if prev_close > 0 else 0
    
    # Determine color based on price movement
    if change > 0:
        color = 0x00FF00  # Green for up
        change_text = f"+${change:.2f} ({pct_change:.1f}%)"
    elif change < 0:
        color = 0xFF0000  # Red for down
        change_text = f"${change:.2f} ({pct_change:.1f}%)"
    else:
        color = 0xFFFFFF  # White for no change
        change_text = f"$0.00 (0.0%)"
    
    return change_text, color

# Helper: Fetch stock data
def fetch_stock_data(ticker):
    url = f"{BASE_URL}{ticker}?token={API_KEY}"
    
    try:
        response = session.get(url)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            data = data[0]  # Handle case when API returns a list
        
        if "error" in data:
            print(f"API Error: {data['error']}")
            return None
        
        # Extract relevant fields
        last_price = data.get('last') or data.get('tngoLast')
        bid_price = data.get('bidPrice')
        ask_price = data.get('askPrice')
        volume = data.get('volume')
        high = data.get('high')
        low = data.get('low')
        prev_close = data.get('prevClose')
        
        return {
            'last': last_price,
            'bid': bid_price,
            'ask': ask_price,
            'volume': volume,
            'high': high,
            'low': low,
            'prev_close': prev_close,
            'timestamp': time.localtime()
        }
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Stock data cache
stock_cache = {}

# Helper: Update display with stock data
def update_display(ticker, stock_data):
    # Update UI with stock data
    stock_label.text = ticker
    
    if stock_data:
        # Price and change
        if stock_data['last'] is not None:
            price_label.text = f"${stock_data['last']:.2f}"
            
            # Calculate and format price change
            change_text, change_color = format_price_change(stock_data['last'], stock_data['prev_close'])
            change_label.text = change_text
            change_label.color = change_color
        else:
            price_label.text = "N/A"
            change_label.text = "N/A"
        
        # Bid/Ask
        if stock_data['bid'] is not None and stock_data['ask'] is not None:
            bid_ask_label.text = f"B:${stock_data['bid']:.2f} A:${stock_data['ask']:.2f}"
        else:
            bid_ask_label.text = "B/A:N/A"
        
        # Volume
        if stock_data['volume'] is not None:
            # Format volume with K/M/B
            vol = stock_data['volume']
            if vol >= 1000000000:
                vol_str = f"{vol/1000000000:.1f}B"
            elif vol >= 1000000:
                vol_str = f"{vol/1000000:.1f}M"
            elif vol >= 1000:
                vol_str = f"{vol/1000:.1f}K"
            else:
                vol_str = str(vol)
            volume_label.text = f"Vol:{vol_str}"
        else:
            volume_label.text = "Vol:N/A"
        
        # High/Low
        high_low_label.text = f"H:${stock_data['high']:.1f} L:${stock_data['low']:.1f}" if (
            stock_data['high'] is not None and stock_data['low'] is not None
        ) else "H/L:N/A"
        
        # Update timestamp
        current_tm = stock_data['timestamp']
        time_str = f"{current_tm.tm_hour:02d}:{current_tm.tm_min:02d}"
        status_label.text = f"At {time_str}"
    else:
        price_label.text = "--"
        change_label.text = "--"
        bid_ask_label.text = "B:-- A:--"
        volume_label.text = "Vol:--"
        high_low_label.text = "H:-- L:--"
        status_label.text = "No data"

# Main loop
update_interval = 30  # seconds
last_data_update = 0

while True:
    current_time = time.monotonic()
    
    # Auto-rotate through tickers
    if current_time - last_ticker_change >= ticker_display_time:
        current_ticker_index = (current_ticker_index + 1) % len(tickers)
        last_ticker_change = current_time
    
    # Current ticker to display
    ticker = tickers[current_ticker_index]
    
    # Check if we need to update data
    ticker_cache_age = 0
    if ticker in stock_cache:
        ticker_cache_age = current_time - stock_cache[ticker]['fetch_time']
    
    # Update stock data if needed
    if ticker not in stock_cache or ticker_cache_age > update_interval:
        status_label.text = "Loading..."
        display.refresh()
        
        stock_data = fetch_stock_data(ticker)
        
        if stock_data:
            # Add fetch time to cache
            stock_data['fetch_time'] = current_time
            stock_cache[ticker] = stock_data
            last_data_update = current_time
        else:
            status_label.text = "Error"
    
    # Display data from cache
    if ticker in stock_cache:
        update_display(ticker, stock_cache[ticker])
    else:
        update_display(ticker, None)
    
    # Clear old cache entries
    if len(stock_cache) > 10:
        oldest_ticker = None
        oldest_time = float('inf')
        for t, data in stock_cache.items():
            if data['fetch_time'] < oldest_time:
                oldest_time = data['fetch_time']
                oldest_ticker = t
        if oldest_ticker:
            del stock_cache[oldest_ticker]
    
    display.refresh()
    time.sleep(0.1)