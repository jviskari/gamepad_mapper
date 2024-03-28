import sys
import usb.core
import keyboard  # We'll use the 'keyboard' library for detecting space bar presses

def find_gamepad(vendor_id, product_id):
    device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    if device is None:
        raise ValueError("Device not found")
    return device

def read_idle_report(device):
    # Read the idle report (baseline state)

    reattach = False
    if device.is_kernel_driver_active(0):
        reattach = True
        device.detach_kernel_driver(0)

    try:
        cfg = device[0]
        intf = cfg[(0, 0)]
        ep = intf[0]
        idle_report = device.read(ep.bEndpointAddress, ep.wMaxPacketSize, timeout=1000)
        return idle_report
    except usb.core.USBError as e:
        print("Error reading idle report:", e)
        return None

def read_reports(device, idle_report):
    reattach = False
    if device.is_kernel_driver_active(0):
        reattach = True
        device.detach_kernel_driver(0)

    try:
        cfg = device[0]
        intf = cfg[(0, 0)]
        ep = intf[0]

        print("Press buttons in order (left, right, up, down, button1, button2, ...)")
        previous_report = idle_report  # Initialize with idle report
        while True:
            try:
                data = device.read(ep.bEndpointAddress, ep.wMaxPacketSize, timeout=1000)
                if data != previous_report:
                    #print("Report changed:", data)
                    hex_array = [hex(i) for i in data]
                    print(hex_array)

                    previous_report = data  # Update previous report
                # Add your logic here to interpret the data (button states, etc.)
            except usb.core.USBError as e:
                print("Error reading data:", e)
                break

            if keyboard.is_pressed("space"):
                print("\nReading aborted by user.")
                break

    except KeyboardInterrupt:
        print("\nExiting...")

    usb.util.dispose_resources(device)

    if reattach:
        device.attach_kernel_driver(0)

def main():
    if len(sys.argv) != 3:
        print("Usage: python gamepad_reader.py <vendor_id> <product_id>")
        sys.exit(1)

    try:
        vendor_id = int(sys.argv[1], 16)  # Convert hex string to integer
        product_id = int(sys.argv[2], 16)
    except ValueError:
        print("Invalid vendor or product ID. Please provide valid hexadecimal values.")
        sys.exit(1)

    try:
        gamepad_device = find_gamepad(vendor_id, product_id)
        print("Gamepad found:")
        print(gamepad_device)
        idle_report = read_idle_report(gamepad_device)
        if idle_report:
            read_reports(gamepad_device, idle_report)  # Start reading reports
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
