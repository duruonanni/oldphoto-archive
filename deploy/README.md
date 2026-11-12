# Repository-first deployment

1. Change and review source in this repository; do not patch live dist/.
2. Keep the real catalog and images outside Git. Update them through a separate, reviewed data workflow.
3. Run tests, then build into a **new** staging directory with the repository's virtual environment.
4. Check category counts, text, image availability, person intersections, pagination and lightbox. Inspect the output before deploying.
5. Back up the old deployment outside the public document root. Publish the inspected staging artifacts, not another untested rebuild.
6. Verify origin and public pages, representative images and no browser errors. Record the source commit and manifest; restore the backup if validation fails.

For nginx, mount the selected static output read-only at `/usr/share/nginx/html`, publish only on `127.0.0.1`, and connect the chosen hostname through your tunnel. Keep credentials out of this repository.

**Existing Docker bind mounts:** renaming the mounted host directory does not reliably change what an existing container serves: it can retain the old inode. Do not use a directory-swap deployment without checking the mount strategy. Recreate only the affected container against a versioned release path, or update files under a stable mounted root with backup and verification. This project deliberately does not guess or mutate your production container.

Noindex is not access control. A public site's content can be downloaded; a cached image may survive its removal at the origin. `publish: false` prevents export in a fresh build but does not delete older deployments or caches.
