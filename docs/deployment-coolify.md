# Deploy WeatherCast with Coolify

WeatherCast is deployed as two stateless containers from the root `compose.yaml`: the Nuxt web service and the FastAPI service. The companion `compose.local.yaml` publishes loopback ports for local Docker testing; do not select it as a Coolify Compose file.

## Requirements

- A Coolify instance with access to this Git repository.
- A public domain or subdomain for the web app and a separate subdomain for the API.
- DNS records pointing both names to the VPS and ports 80/443 reachable by Coolify's proxy.

The Docker base images support `linux/amd64` and `linux/arm64`, including the Hetzner CAX21. Coolify builds on the server architecture. No database or persistent volume is required yet; location preferences live in the visitor's browser.

## Create the application

1. In Coolify, create a resource from the GitHub repository and select **Docker Compose**.
2. Set the Compose file path to `compose.yaml` at the repository root.
3. Configure the `web` service domain on container port `3000` and the `api` service domain on container port `8000`. Let Coolify issue HTTPS certificates.
4. Add these service environment variables before deploying:

   | Service | Variable | Example |
   | --- | --- | --- |
   | `web` | `NUXT_PUBLIC_API_BASE` | `https://api.example.com/api/v1` |
   | `api` | `CORS_ORIGINS` | `https://weather.example.com` |

   Use your own hostnames. Do not include a trailing slash in the web origin. If the web app has multiple public origins, separate them with commas in `CORS_ORIGINS`.

5. Deploy and wait for the API and web health checks to pass. Verify `https://api.example.com/health`, `https://api.example.com/docs`, and the public web page.

The public API URL is intentionally configured at container runtime as well as passed to the Nuxt build. If changing it after a deployment, redeploy the web service so both server rendering and browser requests use the same URL.

## Operations

- Keep `main` as the release branch; deploy a reviewed commit and use Coolify rollback if a release fails.
- Keep the API and web logs available while debugging provider timeouts or CORS configuration. Do not log visitor coordinates.
- Open-Meteo and OpenStreetMap are external dependencies. A healthy container only confirms the app process responds, not that those providers are available.
- OpenStreetMap's standard tile servers are suitable for modest interactive use with attribution, not bulk downloads or high-volume production traffic. Move to a provider with an appropriate service plan before scaling.
- WeatherCast currently stores no server-side user data, so it has no database backup requirement. Keep the Git repository and Coolify configuration backed up; if persistence is added later, define and test database backups before release.
- Review Open-Meteo terms before commercial use or scaling traffic.
