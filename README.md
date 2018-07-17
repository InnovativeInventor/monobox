## monobox
A uniform flexible environment for coding, testing, and deploying using Docker

## Suggested Workflow
- Create your Monofile and Dockerfile. Your Monofile will include everything you need when developing, and your Dockerfile will include everything else
- When deploying, simply take your Dockerfile and use it in production!

## Recommendations
- Use the monobox shortcuts by adding `monobox package` to your Monofile.
- Add your `.gitconfig` file to your developing folder so it gets copied into the Dockerfile
- Add `.monobox` to your `.gitignore`

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
