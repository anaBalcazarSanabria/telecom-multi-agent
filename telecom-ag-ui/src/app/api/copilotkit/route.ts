// app/api/copilotkit/route.ts
import {
  CopilotRuntime,
  GoogleGenerativeAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";

// 1️⃣ LLM adapter: Google Gemini via GoogleGenerativeAIAdapter
const serviceAdapter = new GoogleGenerativeAIAdapter({
  model: process.env.GEMINI_MODEL || "gemini-2.0-flash",
  apiKey: process.env.GOOGLE_API_KEY,
});

// 2️⃣ Runtime: Direct-to-LLM (no AG-UI / external agents here)
const runtime = new CopilotRuntime({});

// 3️⃣ Next.js API route
export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};