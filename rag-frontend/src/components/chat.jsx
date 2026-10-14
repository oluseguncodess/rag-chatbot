import { useEffect, useRef } from "react";

function Sources({ sources }) {
  if (!sources?.length) return null;

  return (
    <details className="mt-3 text-sm text-[#030164]">
      <summary className="cursor-pointer font-medium">
        Sources ({sources.length})
      </summary>
      <ul className="mt-2 space-y-2">
        {sources.map((s, i) => (
          <li key={i} className="border-l-2 border-[#A8BBA3] pl-3">
            <p className="font-medium">Page {s.page}</p>
            <p className="opacity-80">{s.text}</p>
          </li>
        ))}
      </ul>
    </details>
  );
}

export default function Chat({ messages, isLoading }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 min-h-0 w-full max-w-200 overflow-y-auto flex flex-col gap-4 px-1">
      {messages.map((msg, index) => {
        const isUser = msg.role === "user";
        return (
          <div
            key={index}
            className={`max-w-[85%] p-4 rounded-3xl wrap-break-word ${
              isUser ? "self-end" : "self-start"
            } ${msg.isError ? "bg-red-100" : "bg-[#FCF9EA]"}`}
          >
            <p
              className={`w-full whitespace-pre-wrap ${
                msg.isError ? "text-red-800" : "text-[#030164]"
              }`}
            >
              {msg.content}
            </p>
            {!isUser && !msg.isError && <Sources sources={msg.sources} />}
          </div>
        );
      })}

      {isLoading && (
        <div className="self-start p-4 rounded-3xl bg-[#FCF9EA] text-[#030164] animate-pulse">
          Searching the document…
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}