"use client";

import {
  CopilotChat,
  type CopilotChatSuggestion,
  RenderSuggestion,
  type RenderSuggestionsListProps,
} from "@copilotkit/react-ui";

// Suggestions to show in the chat UI
const DEFAULT_SUGGESTIONS: CopilotChatSuggestion[] = [
  {
    title: "Lookup my information",
    message: "Return user information",
    partial: false,
  },
  {
    title: "Network diagnostics",
    message: "Run network diagnostics for a ZIP code.",
    partial: false,
  },
];

export default function HomePage() {
  return (
    <main className="min-h-screen w-screen flex items-center justify-center bg-slate-900 text-white">
      <div
        className="
          rounded-2xl
          bg-slate-950/90
          border border-slate-800
          shadow-2xl
          w-[680px]
          h-[700px]
          flex flex-col
          backdrop-blur-xl
        "
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
          <h1 className="text-lg font-semibold">
            Telecom Customer Service Chatbot Demo
          </h1>
        </div>

        {/* Chat area */}
        <div className="flex-1 min-h-0">
          <CopilotChat
            instructions={`You are a multi-persona telecom assistant. 
              You are backed by a multi-agent backend that can:
              - Greet the user and say goodbye.
              - Look up customer account information.
              - Diagnose network issues using the telecom backend tools.
              - Check whether a user is eligible for incentives.

              Your job is to chat naturally with the user and decide when to call tools
              (based on the user's request) via the backend agent. Ask for the user's
              customer ID or ZIP code when needed. Be concise, friendly, and professional.`}
            labels={{
              title: "",
              initial:
                "Hi! Welcome to ACME wireless. I can answer questions about available plans, your account, and help with network diagnostics. What can I help you with?",
            }}
            className="h-full"
            suggestions={DEFAULT_SUGGESTIONS}
            RenderSuggestionsList={CustomSuggestionsList}
          />
        </div>
      </div>
    </main>
  );
}

// Custom suggestions list, unchanged
const CustomSuggestionsList = ({
  suggestions,
  onSuggestionClick,
}: RenderSuggestionsListProps) => {
  const listToRender = suggestions ?? [];

  if (listToRender.length === 0) return null;

  return (
    <div className="flex flex-col gap-2 p-4 border-b border-slate-800 bg-slate-950">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        Try asking:
      </h2>
      <div className="flex flex-wrap gap-2">
        {listToRender.map((suggestion, index) => (
          <RenderSuggestion
            key={index}
            title={suggestion.title}
            message={suggestion.message}
            partial={suggestion.partial}
            className="rounded-full border border-slate-700 bg-slate-800/80 px-3 py-1 text-xs text-slate-100 shadow-sm hover:bg-slate-700 cursor-pointer"
            onClick={() => onSuggestionClick(suggestion.message)}
          />
        ))}
      </div>
    </div>
  );
};