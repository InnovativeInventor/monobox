## monobox
A uniform flexible environment for coding, testing, and deploying using Docker

## Suggested Workflow
- Create your Monofile and Dockerfile. Your Monofile will include everything you need when developing, and your Dockerfile will include everything else
- When deploying, simply take your Dockerfile and use it in production!

## Recommendations
- Use the monobox shortcuts by adding `monobox package` to your Monofile.
- Add your `.gitconfig` file to your developing folder so it gets copied into the Dockerfile
- Add `.monobox` to your `.gitignore`

## Planned Features
- [ ] Easy one-step deployment
- [ ] Remote fetching of monofiles

## Options
```
usage: monobox.py [-h] [--python]

A uniform flexible environment for coding, testing, and deploying using Docker

optional arguments:
  -h, --help    show this help message and exit
  --python, -p  Runs the python interperter instead of bash (default=bash)
```
