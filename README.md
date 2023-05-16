# maskin-flipdot

This project uses a Raspberry Pi Zero W and a MAX485 chip to control Mobitec flipdot displays.

## Hardware

The hardware used in this project includes:

- Raspberry Pi Zero W
- MAX485 chip
- Mobitec flipdot display

<p align="center">
  <img src="schematic.png" width="50%" height="50%">
</p>


The pinout from the mobitec flipdot display is:

- Red — +24V
- Black — Ground
- White — RS-485 D+ (A)
- Green — RS-485 D- (B)

## Installation

To use this project, you'll need to do the following:

1. Clone the repository:

`cd ~`

`git clone https://github.com/Nosen92/maskin-flipdot`

`cd maskin-flipdot`

2. Install the required dependencies:

`pip install -r requirements.txt`


## Usage

To use the project, run the following command:

`python maskin_flipdot.py`

This will start the program and begin controlling the flipdot displays.

## Contributing

If you would like to contribute to this project, please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.
