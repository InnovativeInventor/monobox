## monobox
A uniform flexible environment for coding, testing, and deploying using Docker

## Suggested Workflow
- Create your Monofile and Dockerfile. Your Monofile will include everything you need when developing, and your Dockerfile will include everything else
- When deploying, simply take your Dockerfile and use it in production!

For guidanceguidance, look at this example monobox project: https://github.com/InnovativeInventor/monobox-example.

## Recommendations
- Use the monobox shortcuts by adding `monobox package` to your Monofile. You can explore the list of boxes at https://boxes.homelabs.space/
- Add your `.gitconfig` file to your developing folder so it gets copied into the Dockerfile
- Add `.monobox` to your `.gitignore`
- If you want to use your own boxes, just create a folder called boxes and follow the same structure in https://github.com/InnovativeInventor/boxes

## Options
```
Usage: monobox [OPTIONS] COMMAND [ARGS]...

  A uniform flexible environment for coding, testing, and deploying using
  Docker.

Options:
  --help  Show this message and exit.

Commands:
  bash     Runs bash when starting up
  default  Starts the container using your defaults
  deploy   Deploys your application using your Dockerfile
  python   Runs the python interperter instead of bash
  sh       Runs sh when starting up

```

## Troubleshooting
If you see `launchpadlib 1.10.6 requires testresources, which is not installed.`, then run `sudo apt install python-testresources` and restart the terminal.
