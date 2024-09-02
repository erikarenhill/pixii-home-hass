# Pixii Home for Home Assistant

This custom integration allows you to monitor your Pixii Home energy storage system through Home Assistant.

## Installation

### Using HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance.
2. In the HACS panel, click on "Integrations".
3. Click the three dots in the top right corner and select "Custom repositories".
4. Add `https://github.com/erikarenhill/pixii-home-hass` as a custom repository with the category "Integration".
5. Close the custom repositories window and click the "+" button in the bottom right corner to add a new integration.
6. Search for "Pixii Home" and select it.
7. Click "Install" and wait for the installation to complete.
8. Restart Home Assistant.

### Manual Installation

1. Copy the `custom_components/pixii_home` directory from this repository to your Home Assistant's `custom_components` directory.
2. Restart Home Assistant.

## Configuration

After installation, you can add the Pixii Home integration through the Home Assistant UI:

1. Go to Configuration > Integrations.
2. Click the "+" button to add a new integration.
3. Search for "Pixii Home" and select it.
4. Follow the configuration steps, providing your Pixii Home device's IP address and port.

## Features

This integration allows you to monitor various aspects of your Pixii Home energy storage system, including:

- Current power output
- Battery state of charge
- Energy production and consumption

Please note that this integration is currently for monitoring purposes only and does not provide control capabilities for the Pixii Home system.

## Issues and Contributions

If you encounter any issues or have suggestions for improvements, please [open an issue](https://github.com/erikarenhill/pixii-home-hass/issues) on the GitHub repository.

## Credits

This integration is developed and maintained by [@erikarenhill](https://github.com/erikarenhill).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support the Project

If you find this integration helpful and would like to support its development, you can buy me a coffee:

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://buymeacoffee.com/gax2vuf)