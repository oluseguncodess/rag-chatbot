import { useMutation } from "@tanstack/react-query";

const API_URL = "http://127.0.0.1:8000/api/chat";

async function postQuestion(question) {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to fetch response from backend");
  }

  return res.json(); // { question, answer, sources, role }
}

// useMutation is a hook, so it must be called inside a component or another hook
export function useChatMutation(options = {}) {
  return useMutation({
    mutationFn: postQuestion,
    ...options,
  });
}