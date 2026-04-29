import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.API_BASE_URL || "http://127.0.0.1:9001";

async function proxy(req: NextRequest, params: { path: string[] }) {
  const path = params.path.join("/");
  const search = req.nextUrl.search;
  const url = `${API_BASE}/${path}${search}`;

  try {
    const res = await fetch(url, {
      method: req.method,
      headers: { "Content-Type": "application/json" },
      body: req.method !== "GET" && req.method !== "HEAD" ? await req.text() : undefined,
    });
    const data = await res.text();
    return new NextResponse(data, {
      status: res.status,
      headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
    });
  } catch (e: any) {
    return NextResponse.json({ error: "Backend unavailable", detail: e.message }, { status: 503 });
  }
}

export async function GET(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxy(req, await params);
}
export async function POST(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  return proxy(req, await params);
}
