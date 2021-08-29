# Littlefield Driver Toolset

A driver, analysis, & automation toolset for the educational simulation game
[Littlefield](http://responsive.net/littlefield.html).

You can view updates about this project on [my personal blog](https://spelkington.github.io/Littlefield/)

## Setup

To use the Littlefield Driver toolset, you'll need to adjust two configurations:

- `configs/secrets.yaml` needs to contain the login link address, along with your Littlefield username and password.
    * You can find an example of what this file should look like at `configs/secrets.yaml.sample`.
- `configs/game.yaml` needs to be configured with the state of the game. This includes
    * The URL address for the game
    * A name for the game
    * A list of nodes, such as menus, queues, and stations, along with how these nodes are connected to each other. You can find an example of this layout at `configs/game.yaml.sample`.

## Documentation

For working code examples, check the `ipynb` directory.

### LittlefieldDriver

The LittlefieldDriver is an object designed to provide programmatic control of the Littlefield game state, including access to current/historical game states and the ability to interact with the game, such as purchasing station machines.

The LittlefieldDriver requires the user to provide their login URL, username, and password in in the `configs/secrets.yaml` file, and to configure the structure of the Littlefield game available at that URL.

#### Functions

- `data()`: Retrieves the historical game data.

## Planned Features

- Implement game interactions within the LittlefieldDriver
- Implement an analysis module that can periodically check the state of the game and make appropriate changes to optimize the game output.

## Contact

If you have questions or issues, you can raise a request via GitHub or email me at spelkington@gmail.com