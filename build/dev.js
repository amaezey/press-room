// Serve the repository root, the way Netlify does.
const ROOT = new URL('..', import.meta.url).pathname;

Bun.serve({
  port: 8777,
  fetch(req) {
    const path = new URL(req.url).pathname;
    const name = path === '/' ? 'index.html' : decodeURIComponent(path).replace(/^\/+/, '');
    if (name.includes('..')) return new Response('no', { status: 400 });
    return new Response(Bun.file(ROOT + name), {
      headers: { 'cache-control': 'no-store' },
    });
  },
});
console.log('serving ' + ROOT + ' on http://localhost:8777');
