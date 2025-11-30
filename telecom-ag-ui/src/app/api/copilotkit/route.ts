import {
  CopilotRuntime,
  GoogleGenerativeAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";

// 1️⃣ LLM adapter: Google Gemini via GoogleGenerativeAIAdapter
const serviceAdapter = new GoogleGenerativeAIAdapter({
  // Optional: you can omit these and let it default,
  // but it's nice to be explicit:
  model: process.env.GEMINI_MODEL || "gemini-2.0-flash",
  apiKey: process.env.GOOGLE_API_KEY,
});

// 2️⃣ Runtime: direct-to-LLM (no agents here)
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
