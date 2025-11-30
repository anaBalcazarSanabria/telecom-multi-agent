"use client";

import { useState } from "react";
import { CopilotChat } from "@copilotkit/react-ui";
import { useCopilotChat } from "@copilotkit/react-core";
import { MessageRole, TextMessage } from "@copilotkit/runtime-client-gql";

export default function HomePage() {
  return (
    <main className="min-h-screen w-screen flex items-center justify-center bg-slate-900 text-white">
      <FloatingChat />
    </main>
  );
}

function FloatingChat() {
  return (
    <div className="relative">
      <div
        className="
          rounded-2xl
          bg-slate-950/90
          border border-slate-800
          shadow-2xl
          w-[680px]      /* Increased width */
          h-[700px]      /* Increased height */
          flex flex-col
          backdrop-blur-xl
        "
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800">
          <div>
            <h2 className="text-lg font-semibold">Assistant</h2>
            <p className="text-[12px] text-slate-400">
              Ask anything or choose a suggestion below.
            </p>
          </div>
        </div>

        {/* Suggested prompts */}
        <div className="px-5 pt-3 pb-2 border-b border-slate-800 bg-slate-900/40">
          <SuggestedPrompts />
        </div>

        {/* Chat window */}
        <div className="flex-1 min-h-0 p-0">
          <CopilotChat
            instructions={
              "You are a helpful assistant. Answer clearly, concisely, and do not mention tools unless asked."
            }
            labels={{
              title: "",
              initial: "Hi! How can I help you today?",
            }}
            className="h-full"
          />
        </div>
      </div>
    </div>
  );
}

function SuggestedPrompts() {
  const { appendMessage } = useCopilotChat();

  const suggestions = [
    "Explain what this demo is doing.",
    "Give me three ideas for improving this chat UI.",
    "Help me design a better system prompt for this assistant.",
  ];

  const handleClick = (text: string) => {
    appendMessage(
      new TextMessage({
        role: MessageRole.User,
        content: text,
      })
    );
  };

  return (
    <div className="flex flex-wrap gap-2">
      {suggestions.map((s) => (
        <button
          key={s}
          onClick={() => handleClick(s)}
          className="
            px-3 py-1
            rounded-full
            bg-slate-800
            text-[12px]
            text-slate-100
            hover:bg-slate-700
            transition
            whitespace-nowrap
          "
        >
          {s}
        </button>
      ))}
    </div>
  );
}
