"use client";

import { useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

type Source = {
  document_id: number;
  filename: string;
  page_number: number | null;
  chunk_index: number;
  score: number;
  text: string;
};

type ChatResponse = {
  question: string;
  answer: string;
  sources: Source[];
};

type ConversationResponse = {
  id: number;
  title: string;
};

type Conversation = {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
};

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
};

type CurrentUser = {
  id?: number;
  email?: string;
  full_name?: string;
  role?: string;
};

export default function Home() {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<Source[]>([]);
  const [expandedSource, setExpandedSource] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const [conversationId, setConversationId] = useState<number | null>(null);
  const [conversationLoading, setConversationLoading] = useState(true);

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);

  // Current logged-in user
  const [currentUser, setCurrentUser] = useState<CurrentUser | null>(null);

  // --------------------------------------------------
  // AUTHENTICATION
  // --------------------------------------------------

  const getAuthHeaders = (): Record<string, string> => {
    const token = localStorage.getItem("nexus_access_token");

    if (!token) {
      return {};
    }

    return {
      Authorization: `Bearer ${token}`,
    };
  };

  const handleUnauthorized = () => {
    localStorage.removeItem("nexus_access_token");
    localStorage.removeItem("nexus_user");
    window.location.href = "/login";
  };

  const handleLogout = () => {
    localStorage.removeItem("nexus_access_token");
    localStorage.removeItem("nexus_user");
    window.location.href = "/login";
  };

  // --------------------------------------------------
  // CREATE NEW CONVERSATION
  // --------------------------------------------------

  const createConversation = async () => {
    try {
      setConversationLoading(true);

      const response = await fetch(`${API_URL}/conversations`, {
        method: "POST",
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      const data: ConversationResponse = await response.json();

      if (!response.ok) {
        throw new Error(data.title || "Unable to create conversation.");
      }

      setConversationId(data.id);
      setMessages([]);
      setQuestion("");
      setAnswer("");
      setSources([]);
      setExpandedSource(null);

      await loadConversations();
    } catch (error) {
      console.error("Conversation creation failed:", error);
      setConversationId(null);
    } finally {
      setConversationLoading(false);
    }
  };

  // --------------------------------------------------
  // LOAD DOCUMENT
  // --------------------------------------------------

  const uploadDocument = async () => {
    if (!file) {
      setUploadMessage("Choose a PDF or DOCX file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    setUploadMessage("");

    try {
      const response = await fetch(`${API_URL}/documents/upload`, {
        method: "POST",
        headers: {
          ...getAuthHeaders(),
        },
        body: formData,
      });

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed");
      }

      setUploadMessage(
        `${data.filename} indexed successfully • ${
          data.chunks
        } chunk${data.chunks === 1 ? "" : "s"}`,
      );

      setFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (error) {
      setUploadMessage(
        error instanceof Error ? error.message : "Upload failed",
      );
    } finally {
      setUploading(false);
    }
  };

  // --------------------------------------------------
  // ASK QUESTION
  // --------------------------------------------------

  const askQuestion = async () => {
    if (!question.trim() || loading) {
      return;
    }

    if (!conversationId) {
      setAnswer("Creating your conversation. Please try again in a moment.");
      return;
    }

    const currentQuestion = question.trim();

    setQuestion("");

    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...getAuthHeaders(),
        },
        body: JSON.stringify({
          question: currentQuestion,
          conversation_id: conversationId,
        }),
      });

      const data: ChatResponse = await response.json();

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        throw new Error("Unable to process your question.");
      }

      setAnswer(data.answer);
      setSources(data.sources);

      await loadConversations();

      await loadMessages(conversationId, data.sources, data.answer);
    } catch (error) {
      setAnswer(
        error instanceof Error ? error.message : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // LOAD CONVERSATION LIST
  // --------------------------------------------------

  const loadConversations = async () => {
    try {
      const response = await fetch(`${API_URL}/conversations`, {
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        throw new Error("Unable to load conversations.");
      }

      const data: Conversation[] = await response.json();

      setConversations(data);
    } catch (error) {
      console.error("Conversation history failed:", error);
    }
  };

  // --------------------------------------------------
  // DELETE CONVERSATION
  // --------------------------------------------------

  const deleteConversation = async (conversationIdToDelete: number) => {
    const confirmed = window.confirm(
      "Delete this conversation and all its messages?",
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(
        `${API_URL}/conversations/${conversationIdToDelete}`,
        {
          method: "DELETE",
          headers: {
            ...getAuthHeaders(),
          },
        },
      );

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Unable to delete conversation.");
      }

      if (conversationId === conversationIdToDelete) {
        setConversationId(null);
        setMessages([]);
        setAnswer("");
        setSources([]);
        setQuestion("");
        setExpandedSource(null);
      }

      await loadConversations();
    } catch (error) {
      console.error("Conversation deletion failed:", error);
    }
  };

  // --------------------------------------------------
  // LOAD CONVERSATION MESSAGES
  // --------------------------------------------------

  const loadMessages = async (
    selectedConversationId: number,
    latestSources: Source[] = [],
    latestAnswer?: string,
  ) => {
    try {
      setConversationLoading(true);

      const response = await fetch(
        `${API_URL}/conversations/${selectedConversationId}/messages`,
        {
          headers: {
            ...getAuthHeaders(),
          },
        },
      );

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      if (!response.ok) {
        throw new Error("Unable to load conversation messages.");
      }

      const data: Message[] = await response.json();

      setMessages(data);
      setConversationId(selectedConversationId);

      setQuestion("");

      const lastAssistantMessage = [...data]
        .reverse()
        .find((message) => message.role === "assistant");

      if (latestAnswer !== undefined) {
        setAnswer(latestAnswer);
      } else if (lastAssistantMessage) {
        setAnswer(lastAssistantMessage.content);
      } else {
        setAnswer("");
      }

      setSources(latestSources);
    } catch (error) {
      console.error("Message loading failed:", error);

      setMessages([]);
      setAnswer("Unable to load this conversation.");
      setSources([]);
    } finally {
      setConversationLoading(false);
    }
  };

  // --------------------------------------------------
  // NEW CHAT
  // --------------------------------------------------

  const clearChat = async () => {
    setQuestion("");
    setAnswer("");
    setSources([]);
    setExpandedSource(null);
    setMessages([]);
    setUploadMessage("");

    await createConversation();
  };

  // --------------------------------------------------
  // INITIALIZE CONVERSATION
  // --------------------------------------------------

  useEffect(() => {
    // Load user from localStorage ONLY on the client
    const storedUser = localStorage.getItem("nexus_user");

    if (storedUser) {
      try {
        setCurrentUser(JSON.parse(storedUser));
      } catch {
        setCurrentUser(null);
      }
    }

    const initializeConversation = async () => {
      const token = localStorage.getItem("nexus_access_token");

      if (!token) {
        window.location.href = "/login";
        return;
      }

      try {
        setConversationLoading(true);

        const response = await fetch(`${API_URL}/conversations`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 401) {
          handleUnauthorized();
          return;
        }

        if (!response.ok) {
          throw new Error("Unable to load conversations.");
        }

        const data: Conversation[] = await response.json();

        setConversations(data);

        if (data.length > 0) {
          await loadMessages(data[0].id);
        } else {
          setConversationId(null);
          setMessages([]);
          setAnswer("");
          setSources([]);
          setConversationLoading(false);
        }
      } catch (error) {
        console.error("Conversation initialization failed:", error);

        setConversationId(null);
        setMessages([]);
        setAnswer("");
        setSources([]);
        setConversationLoading(false);
      }
    };

    initializeConversation();
  }, []);

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main className="min-h-screen bg-[#f7f8fa] text-[#111318]">
      <div className="flex min-h-screen">
        {/* SIDEBAR */}

        <aside className="hidden w-[270px] flex-col border-r border-black/8 bg-white px-5 py-6 lg:flex">
          <div className="flex items-center gap-3 px-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-black text-sm font-bold text-white">
              N
            </div>

            <div>
              <h1 className="text-[15px] font-semibold tracking-tight">
                NexusCopilot
              </h1>

              <p className="text-[11px] text-gray-500">Enterprise AI</p>
            </div>
          </div>

          <div className="mt-10">
            <p className="px-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-gray-400">
              Workspace
            </p>

            <div className="mt-3 space-y-1">
              <button className="flex w-full items-center gap-3 rounded-xl bg-black px-3 py-2.5 text-left text-sm font-medium text-white">
                <span>✦</span>
                AI Copilot
              </button>

              <button
                onClick={() => {
                  window.location.href = "/documents";
                }}
                className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-gray-600 transition hover:bg-gray-100"
              >
                <span>◫</span>
                Documents
              </button>

              <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm text-gray-600 transition hover:bg-gray-100">
                <span>◷</span>
                History
              </button>
            </div>

            {/* CONVERSATION HISTORY */}

            {conversations.length > 0 && (
              <div className="mt-5">
                <p className="px-2 text-[10px] font-semibold uppercase tracking-[0.16em] text-gray-400">
                  Recent conversations
                </p>

                <div className="mt-2 max-h-52 space-y-1 overflow-y-auto">
                  {conversations.map((conversation) => (
                    <div
                      key={conversation.id}
                      className={`group flex items-center gap-1 rounded-lg transition ${
                        conversation.id === conversationId
                          ? "bg-gray-100"
                          : "hover:bg-gray-50"
                      }`}
                    >
                      <button
                        onClick={() => loadMessages(conversation.id)}
                        disabled={conversationLoading}
                        className={`min-w-0 flex-1 truncate px-3 py-2 text-left text-[11px] ${
                          conversation.id === conversationId
                            ? "font-medium text-black"
                            : "text-gray-500"
                        } disabled:cursor-wait`}
                      >
                        {conversation.title}
                      </button>

                      <button
                        onClick={() => deleteConversation(conversation.id)}
                        disabled={conversationLoading}
                        className="mr-2 hidden rounded px-1.5 py-1 text-[11px] text-gray-400 transition hover:bg-red-50 hover:text-red-600 group-hover:block"
                        title="Delete conversation"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* SIDEBAR BOTTOM */}

          <div className="mt-auto">
            <div className="rounded-2xl border border-black/8 bg-[#f7f8fa] p-4">
              <div className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-green-500" />

                <span className="text-xs font-medium">System operational</span>
              </div>

              <p className="mt-2 text-[11px] leading-5 text-gray-500">
                RAG retrieval and local AI inference are available.
              </p>
            </div>

            {/* ADMIN DASHBOARD + USER */}

            {currentUser && (
              <>
                {currentUser.role === "admin" && (
                  <button
                    onClick={() => {
                      window.location.href = "/admin";
                    }}
                    className="mb-3 mt-4 flex w-full items-center gap-3 rounded-xl border border-black/8 bg-white px-3 py-2.5 text-left text-xs font-medium text-gray-700 transition hover:bg-gray-50"
                  >
                    <span>⚙</span>
                    Admin Dashboard
                  </button>
                )}

                <div className="border-t border-black/8 pt-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-200 text-xs font-semibold">
                      PS
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-xs font-semibold">
                        {currentUser.full_name || "Praveen"}
                      </p>

                      <p className="text-[10px] capitalize text-gray-500">
                        {currentUser.role || "employee"}
                      </p>
                    </div>
                  </div>

                  {/* LOGOUT */}

                  <button
                    onClick={handleLogout}
                    className="mt-3 w-full rounded-xl border border-black/8 bg-white px-3 py-2 text-left text-xs font-medium text-gray-600 transition hover:bg-gray-50 hover:text-black"
                  >
                    Sign out
                  </button>
                </div>
              </>
            )}
          </div>
        </aside>

        {/* MAIN */}

        <section className="flex min-w-0 flex-1 flex-col">
          {/* TOP BAR */}

          <header className="flex h-[72px] items-center justify-between border-b border-black/8 bg-white/90 px-5 backdrop-blur md:px-8">
            <div>
              <p className="text-xs text-gray-400">Workspace</p>

              <h2 className="text-sm font-semibold">AI Knowledge Copilot</h2>
            </div>

            <div className="flex items-center gap-3">
              <div className="hidden items-center gap-2 rounded-full border border-black/8 bg-white px-3 py-1.5 text-[11px] text-gray-500 sm:flex">
                <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                Qwen 1.5B · Local
              </div>

              <button
                onClick={clearChat}
                disabled={conversationLoading}
                className="rounded-lg border border-black/8 px-3 py-1.5 text-xs font-medium text-gray-600 transition hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                New chat
              </button>
            </div>
          </header>

          {/* CONTENT */}

          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto w-full max-w-5xl px-5 py-10 md:px-8">
              {/* HERO */}

              {!answer &&
                !loading &&
                messages.length === 0 &&
                !conversationLoading && (
                  <div className="mx-auto max-w-3xl py-10 text-center md:py-16">
                    <div className="mx-auto mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-black text-xl text-white shadow-lg">
                      ✦
                    </div>

                    <h2 className="text-3xl font-semibold tracking-[-0.04em] md:text-4xl">
                      Ask your company knowledge.
                    </h2>

                    <p className="mx-auto mt-4 max-w-xl text-sm leading-6 text-gray-500">
                      Upload policies, SOPs, reports, and internal documents.
                      NexusCopilot retrieves relevant information and generates
                      grounded answers from your knowledge base.
                    </p>

                    <div className="mt-8 grid gap-3 text-left sm:grid-cols-3">
                      {[
                        [
                          "⌁",
                          "Grounded answers",
                          "Answers backed by your documents",
                        ],
                        [
                          "◈",
                          "Semantic search",
                          "Find meaning, not just keywords",
                        ],
                        ["◉", "Private AI", "Local Qwen inference"],
                      ].map(([icon, title, text]) => (
                        <div
                          key={title}
                          className="rounded-2xl border border-black/8 bg-white p-4 shadow-sm"
                        >
                          <div className="text-lg">{icon}</div>

                          <p className="mt-3 text-xs font-semibold">{title}</p>

                          <p className="mt-1 text-[11px] leading-5 text-gray-500">
                            {text}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

              {/* LOADING CONVERSATION */}

              {conversationLoading && !loading && messages.length === 0 && (
                <div className="mx-auto max-w-3xl py-16 text-center">
                  <div className="flex items-center justify-center gap-2">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-black" />
                    <span className="h-2 w-2 animate-pulse rounded-full bg-black [animation-delay:150ms]" />
                    <span className="h-2 w-2 animate-pulse rounded-full bg-black [animation-delay:300ms]" />
                  </div>

                  <p className="mt-3 text-xs text-gray-400">
                    Loading conversation...
                  </p>
                </div>
              )}

              {/* CHAT */}

              {(answer || loading || messages.length > 0) && (
                <div className="mx-auto max-w-3xl">
                  {/* STORED MESSAGES */}

                  {messages.length > 0 && (
                    <div className="space-y-7">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className="border-b border-black/5 pb-7"
                        >
                          <div className="mb-3 flex items-center gap-2">
                            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-black text-[10px] text-white">
                              {message.role === "user" ? "P" : "N"}
                            </div>

                            <span className="text-xs font-medium text-gray-500">
                              {message.role === "user" ? "You" : "NexusCopilot"}
                            </span>
                          </div>

                          <div className="rounded-2xl border border-black/8 bg-white p-5 shadow-sm">
                            <p className="whitespace-pre-wrap text-[15px] leading-7">
                              {message.content}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* CURRENT LOADING */}

                  {loading && (
                    <div className="border-t border-black/8 pt-7">
                      <div className="mb-3 flex items-center gap-2">
                        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-black text-[10px] text-white">
                          N
                        </div>

                        <span className="text-xs font-medium text-gray-500">
                          NexusCopilot
                        </span>
                      </div>

                      <div className="flex items-center gap-2 py-4">
                        <span className="h-2 w-2 animate-pulse rounded-full bg-black" />

                        <span className="h-2 w-2 animate-pulse rounded-full bg-black [animation-delay:150ms]" />

                        <span className="h-2 w-2 animate-pulse rounded-full bg-black [animation-delay:300ms]" />

                        <span className="ml-2 text-xs text-gray-400">
                          Searching your knowledge base...
                        </span>
                      </div>
                    </div>
                  )}

                  {/* SOURCES */}

                  {!loading && answer && sources.length > 0 && (
                    <div className="mt-7">
                      <div className="mb-3 flex items-center justify-between">
                        <p className="text-xs font-semibold">Sources</p>

                        <p className="text-[10px] text-gray-400">
                          {sources.length} retrieved
                        </p>
                      </div>

                      <div className="space-y-3">
                        {sources.map((source, index) => {
                          const sourceKey = `${source.document_id}-${source.chunk_index}-${index}`;

                          const isExpanded = expandedSource === sourceKey;

                          return (
                            <div
                              key={sourceKey}
                              className="rounded-xl border border-black/8 bg-white p-4 transition hover:border-black/15"
                            >
                              <div className="flex items-start justify-between gap-4">
                                <div className="min-w-0 flex-1">
                                  {/* DOCUMENT HEADER */}

                                  <div className="flex items-center gap-2">
                                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-[10px] font-bold uppercase text-gray-600">
                                      {source.filename.split(".").pop() ||
                                        "DOC"}
                                    </div>

                                    <p className="truncate text-xs font-semibold">
                                      {source.filename}
                                    </p>
                                  </div>

                                  {/* DOCUMENT METADATA */}

                                  <div className="mt-2 flex flex-wrap items-center gap-2 text-[10px] text-gray-400">
                                    <span>Document #{source.document_id}</span>

                                    {source.page_number !== null && (
                                      <>
                                        <span>•</span>

                                        <span>Page {source.page_number}</span>
                                      </>
                                    )}

                                    <span>•</span>

                                    <span>Chunk {source.chunk_index}</span>
                                  </div>

                                  {/* VIEW SOURCE */}

                                  <button
                                    onClick={() =>
                                      setExpandedSource(
                                        isExpanded ? null : sourceKey,
                                      )
                                    }
                                    className="mt-3 text-[11px] font-medium text-gray-600 transition hover:text-black"
                                  >
                                    {isExpanded
                                      ? "Hide source ↑"
                                      : "View source ↓"}
                                  </button>

                                  {/* EXPANDED SOURCE */}

                                  {isExpanded && (
                                    <div className="mt-3 rounded-lg border border-black/5 bg-gray-50 p-3">
                                      <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-gray-400">
                                        Retrieved content
                                      </p>

                                      <p className="whitespace-pre-wrap text-xs leading-5 text-gray-600">
                                        {source.text}
                                      </p>

                                      <div className="mt-3 flex flex-wrap gap-2 text-[10px] text-gray-400">
                                        <span>
                                          Document ID: {source.document_id}
                                        </span>

                                        {source.page_number !== null && (
                                          <>
                                            <span>•</span>

                                            <span>
                                              Page: {source.page_number}
                                            </span>
                                          </>
                                        )}

                                        <span>•</span>

                                        <span>Chunk: {source.chunk_index}</span>
                                      </div>
                                    </div>
                                  )}
                                </div>

                                {/* RELEVANCE */}

                                <span className="shrink-0 rounded-full bg-green-100 px-2.5 py-1 text-[10px] font-semibold text-green-700">
                                  {Math.round(source.score * 100)}% relevance
                                </span>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* COMPOSER */}

          <div className="border-t border-black/8 bg-[#f7f8fa] px-5 py-5 md:px-8">
            <div className="mx-auto max-w-3xl">
              {/* UPLOAD */}

              <div className="mb-3 flex items-center justify-between rounded-xl border border-black/8 bg-white px-4 py-3">
                <div className="flex min-w-0 items-center gap-3">
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-xs">
                    +
                  </div>

                  <div className="min-w-0">
                    <p className="text-xs font-semibold">Add knowledge</p>

                    <p className="truncate text-[10px] text-gray-400">
                      {file ? file.name : "Upload PDF or DOCX documents"}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={(e) => {
                      setFile(e.target.files?.[0] || null);
                      setUploadMessage("");
                    }}
                  />

                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="rounded-lg border border-black/8 px-3 py-1.5 text-[11px] font-medium transition hover:bg-gray-50"
                  >
                    Choose file
                  </button>

                  {file && (
                    <button
                      onClick={uploadDocument}
                      disabled={uploading}
                      className="rounded-lg bg-black px-3 py-1.5 text-[11px] font-medium text-white transition hover:bg-gray-800 disabled:opacity-50"
                    >
                      {uploading ? "Indexing..." : "Index"}
                    </button>
                  )}
                </div>
              </div>

              {/* UPLOAD MESSAGE */}

              {uploadMessage && (
                <div className="mb-3 rounded-lg border border-black/8 bg-white px-4 py-2.5 text-[11px] text-gray-500">
                  <span className="mr-2 text-green-600">●</span>

                  {uploadMessage}
                </div>
              )}

              {/* CHAT INPUT */}

              <div className="rounded-2xl border border-black/10 bg-white p-2 shadow-[0_8px_30px_rgba(0,0,0,0.06)]">
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      askQuestion();
                    }
                  }}
                  placeholder={
                    conversationLoading
                      ? "Loading conversation..."
                      : "Ask anything about your documents..."
                  }
                  disabled={conversationLoading}
                  rows={2}
                  className="w-full resize-none bg-transparent px-3 py-2 text-sm outline-none placeholder:text-gray-400 disabled:cursor-not-allowed disabled:opacity-60"
                />

                <div className="flex items-center justify-between border-t border-black/5 px-2 pt-2">
                  <p className="text-[10px] text-gray-400">
                    Enter to send · Shift + Enter for new line
                  </p>

                  <button
                    onClick={askQuestion}
                    disabled={
                      !question.trim() ||
                      loading ||
                      conversationLoading ||
                      !conversationId
                    }
                    className="flex h-9 w-9 items-center justify-center rounded-xl bg-black text-sm text-white transition hover:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    ↑
                  </button>
                </div>
              </div>

              <p className="mt-3 text-center text-[10px] text-gray-400">
                NexusCopilot can make mistakes. Verify important information
                against the cited source.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
