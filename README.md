# ScuffBot

This bot is the custom server management bot which runs on the Scuffcord [discord server](discord.gg/scuffcordoce).

## Usage

This repo will deploy into OCI using CI/CD.

If you would like to run locally:

1. Copy [config.template.yml](./config.template.yml) to `config.yml`
2. Run the following

```bash
docker run -v --rm $(pwd)/config.yml:/app/config.yml $(docker build -q .)
```
