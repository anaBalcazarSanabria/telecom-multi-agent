import {
  CopilotRuntime,
  ExperimentalEmptyAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";
import { HttpAgent } from "@ag-ui/client";

// 1️⃣ Use EmptyAdapter here – we rely entirely on your ADK agent
const serviceAdapter = new ExperimentalEmptyAdapter();

// 2️⃣ ADK multi-agent endpoint (FastAPI server from agent.py)
const adkAgent = new HttpAgent({
  url:
    process.env.ADK_AGENT_URL ||
    "http://127.0.0.1:8000/api/apps/multi-tool-agent/invoke",
});

// 3️⃣ Register the ADK multi-agent in CopilotRuntime
const runtime = new CopilotRuntime({
  agents: {
    telecom_multi: adkAgent, // 👈 same name you use in <CopilotKit agent="...">
  },
});

// 4️⃣ Build the CopilotKit endpoint once
const endpoint = copilotRuntimeNextJSAppRouterEndpoint({
  runtime,
  serviceAdapter,
  endpoint: "/api/copilotkit",
});

// 5️⃣ Export handlers for Next.js
export async function POST(req: NextRequest) {
  return endpoint.handleRequest(req);
}

export async function GET(req: NextRequest) {
  return endpoint.handleRequest(req);
}