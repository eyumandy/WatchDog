export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "POST" && url.pathname === "/execute-sql") {
      try {
        const { sql, bindings } = await request.json();

        if (!sql) {
          return new Response("SQL query is required", { status: 400 });
        }

        const result = await env.DB.prepare(sql).bind(...bindings.map(b => b.value)).run();
        return new Response(JSON.stringify(result), { status: 200 });
      } catch (error) {
        return new Response(`Error: ${error.message}`, { status: 500 });
      }
    }

    return new Response("Not Found", { status: 404 });
  },
};
