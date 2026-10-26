# Deploy WeatherCast with Coolify

WeatherCast is deployed as two stateless containers from the root `compose.yaml`: the Nuxt web service and the FastAPI service. The companion `compose.local.yaml` publishes loopback ports for local Docker testing; do not select it as a Coolify Compose file.

## Current production deployment

- **Web app:** [https://weathercast.anderbel.com](https://weathercast.anderbel.com)
- **API health:** [https://api.weathercast.anderbel.com/health](https://api.weathercast.anderbel.com/health)
- **API documentation:** [https://api.weathercast.anderbel.com/docs](https://api.weathercast.anderbel.com/docs)
- **Hosting:** Hetzner CAX21 with Coolify and Docker Compose
- **TLS:** HTTPS certificates are managed by the Coolify proxy.

The API health check returns `{"status":"ok"}`. The public web app and API use separate hostnames. The Coolify dashboard is administered through its own HTTPS hostname; direct public access to its server ports is blocked by the Hetzner firewall.

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
   | `web` | `NUXT_PUBLIC_API_BASE` | `https://api.weathercast.anderbel.com/api/v1` |
   | `api` | `CORS_ORIGINS` | `https://weathercast.anderbel.com` |

   Use your own hostnames. Do not include a trailing slash in the web origin. If the web app has multiple public origins, separate them with commas in `CORS_ORIGINS`.

5. Deploy and wait for the API and web health checks to pass. For the production deployment, verify `https://api.weathercast.anderbel.com/health`, `https://api.weathercast.anderbel.com/docs`, and `https://weathercast.anderbel.com`.

The public API URL is intentionally configured at container runtime as well as passed to the Nuxt build. If changing it after a deployment, redeploy the web service so both server rendering and browser requests use the same URL.

## Operations

- Keep `main` as the release branch; deploy a reviewed commit and use Coolify rollback if a release fails.
- Keep inbound TCP ports `80` and `443` available for the Coolify proxy and `22` for SSH administration. Once the dashboard works through its HTTPS domain, do not expose Coolify's direct-access ports `8000`, `6001`, and `6002` publicly. Keep the Hetzner firewall attached to the server and verify the dashboard domain after firewall changes.
- Keep the API and web logs available while debugging provider timeouts or CORS configuration. Do not log visitor coordinates.
- Open-Meteo and OpenStreetMap are external dependencies. A healthy container only confirms the app process responds, not that those providers are available.
- OpenStreetMap's standard tile servers are suitable for modest interactive use with attribution, not bulk downloads or high-volume production traffic. Move to a provider with an appropriate service plan before scaling.
- WeatherCast currently stores no server-side user data, so it has no database backup requirement. Keep the Git repository and Coolify configuration backed up; if persistence is added later, define and test database backups before release.
- Review Open-Meteo terms before commercial use or scaling traffic.
