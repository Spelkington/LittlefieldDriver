# Littlefield Driver Toolset

A driver, analysis, & automation toolset for the educational simulation game
[Littlefield](http://responsive.net/littlefield.html)

## Setup

## Documentation

### LittlefieldDriver

The LittlefieldDriver is an object designed to provide programmatic control of the Littlefield game state, including access to current/historical game states and the ability to interact with the game, such as purchasing station machines.

The LittlefieldDriver requires the user to provide their login URL, username, and password in in the `configs/secrets.yaml` file, and to configure the structure of the Littlefield game available at that URL.

#### Functions

- `data`: Retrieves the historical game data.

## Planned Features

- Implement game interactions within the LittlefieldDriver
- Implement an analysis module that can periodically check the state of the game and make appropriate changes to optimize the game output.

## Contact

If you have questions or issues, you can raise a request via GitHub or email me at spelkington@gmail.com