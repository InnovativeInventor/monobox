## monobox
A uniform flexible environment for coding, testing, and deploying using Docker

## Suggested Workflow
- Create your Monofile and Dockerfile. Your Monofile will include everything you need when developing, and your Dockerfile will include everything else
- When deploying, simply take your Dockerfile and use it in production!

## Recommendations
- Use the monobox shortcuts by adding `monobox package` to your Monofile.
- Add your `.gitconfig` file to your developing folder so it gets copied into the Dockerfile
- Add `/mono` to your `.gitignore`

## Planned Features
- [ ] Easy one-step deployment
- [ ] Remote fetching of monofiles
