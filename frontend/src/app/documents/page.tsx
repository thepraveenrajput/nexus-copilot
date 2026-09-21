"use client";

import { ChangeEvent, useEffect, useState } from "react";

type DocumentItem = {
  id: number;
  filename: string;
  file_type: string;
  status: string;
  qdrant_collection: string;
  created_at: string;
};

const API_URL = "http://127.0.0.1:8000";

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState("");

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

  // --------------------------------------------------
  // LOAD DOCUMENTS
  // --------------------------------------------------

  const loadDocuments = async () => {
    try {
      const response = await fetch(`${API_URL}/documents`, {
        method: "GET",
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to load documents");
      }

      setDocuments(data);
    } catch (error) {
      console.error("Document loading failed:", error);

      setMessage(
        error instanceof Error ? error.message : "Failed to load documents.",
      );
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  // --------------------------------------------------
  // UPLOAD DOCUMENT
  // --------------------------------------------------

  const handleUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setUploading(true);
    setMessage("");

    try {
      const formData = new FormData();

      formData.append("file", file);

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

      setMessage(
        `${data.filename} indexed successfully • ${data.chunks} chunk${
          data.chunks === 1 ? "" : "s"
        }`,
      );

      await loadDocuments();
    } catch (error) {
      console.error("Document upload failed:", error);

      setMessage(
        error instanceof Error ? error.message : "Document upload failed.",
      );
    } finally {
      setUploading(false);

      event.target.value = "";
    }
  };

  // --------------------------------------------------
  // DELETE DOCUMENT
  // --------------------------------------------------

  const handleDelete = async (documentId: number) => {
    const confirmed = window.confirm(
      "Delete this document and its indexed knowledge?",
    );

    if (!confirmed) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/documents/${documentId}`, {
        method: "DELETE",
        headers: {
          ...getAuthHeaders(),
        },
      });

      if (response.status === 401) {
        handleUnauthorized();
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Delete failed");
      }

      setMessage("Document deleted successfully.");

      await loadDocuments();
    } catch (error) {
      console.error("Document deletion failed:", error);

      setMessage(
        error instanceof Error ? error.message : "Document deletion failed.",
      );
    }
  };

  // --------------------------------------------------
  // STATISTICS
  // --------------------------------------------------

  const indexedCount = documents.filter(
    (document) => document.status === "indexed",
  ).length;

  const processingCount = documents.filter(
    (document) => document.status === "processing",
  ).length;

  const failedCount = documents.filter(
    (document) => document.status === "failed",
  ).length;

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <main className="min-h-screen bg-[#f7f8fa] text-[#111318]">
      <div className="mx-auto min-h-screen max-w-6xl px-5 py-8 md:px-8">
        {/* HEADER */}

        <header className="flex items-center justify-between border-b border-black/8 pb-6">
          <div className="flex items-center gap-4">
            <a
              href="/"
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-black/8 bg-white text-sm transition hover:bg-gray-50"
            >
              ←
            </a>

            <div>
              <p className="text-xs text-gray-400">NexusCopilot</p>

              <h1 className="text-xl font-semibold tracking-tight">
                Documents
              </h1>
            </div>
          </div>

          <label className="cursor-pointer rounded-lg bg-black px-4 py-2.5 text-xs font-medium text-white transition hover:bg-gray-800">
            {uploading ? "Indexing..." : "Upload Document"}

            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </header>

        {/* DESCRIPTION */}

        <div className="py-8">
          <h2 className="text-2xl font-semibold tracking-tight">
            Knowledge Base
          </h2>

          <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-500">
            Upload company policies, SOPs, reports, and other internal
            documents. NexusCopilot indexes them for grounded AI answers.
          </p>
        </div>

        {/* STATS */}

        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-2xl border border-black/8 bg-white p-5 shadow-sm">
            <p className="text-xs text-gray-400">Total documents</p>

            <p className="mt-2 text-2xl font-semibold">{documents.length}</p>
          </div>

          <div className="rounded-2xl border border-black/8 bg-white p-5 shadow-sm">
            <p className="text-xs text-gray-400">Indexed</p>

            <p className="mt-2 text-2xl font-semibold text-green-600">
              {indexedCount}
            </p>
          </div>

          <div className="rounded-2xl border border-black/8 bg-white p-5 shadow-sm">
            <p className="text-xs text-gray-400">Processing / Failed</p>

            <p className="mt-2 text-2xl font-semibold">
              {processingCount + failedCount}
            </p>
          </div>
        </div>

        {/* MESSAGE */}

        {message && (
          <div className="mt-6 rounded-xl border border-black/8 bg-white px-4 py-3 text-xs text-gray-600">
            {message}
          </div>
        )}

        {/* DOCUMENT LIST */}

        <section className="mt-6 overflow-hidden rounded-2xl border border-black/8 bg-white shadow-sm">
          <div className="border-b border-black/8 px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold">Uploaded documents</h3>

                <p className="mt-1 text-[11px] text-gray-400">
                  Documents available to the AI knowledge base
                </p>
              </div>

              <button
                onClick={loadDocuments}
                className="rounded-lg border border-black/8 px-3 py-1.5 text-[11px] font-medium text-gray-600 transition hover:bg-gray-50"
              >
                Refresh
              </button>
            </div>
          </div>

          {documents.length === 0 ? (
            <div className="px-6 py-16 text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 text-lg">
                +
              </div>

              <p className="mt-4 text-sm font-medium">No documents yet</p>

              <p className="mt-1 text-xs text-gray-400">
                Upload a PDF or DOCX to build your knowledge base.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-black/5">
              {documents.map((document) => (
                <div
                  key={document.id}
                  className="flex flex-col gap-4 px-6 py-5 sm:flex-row sm:items-center sm:justify-between"
                >
                  {/* DOCUMENT INFO */}

                  <div className="flex min-w-0 items-center gap-4">
                    <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gray-100 text-[10px] font-bold uppercase">
                      {document.file_type.replace(".", "")}
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-sm font-semibold">
                        {document.filename}
                      </p>

                      <p className="mt-1 text-[11px] text-gray-400">
                        Uploaded{" "}
                        {new Date(document.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* STATUS + ACTION */}

                  <div className="flex items-center gap-3">
                    <span
                      className={`rounded-full px-3 py-1 text-[10px] font-semibold ${
                        document.status === "indexed"
                          ? "bg-green-100 text-green-700"
                          : document.status === "failed"
                            ? "bg-red-100 text-red-700"
                            : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {document.status}
                    </span>

                    <button
                      onClick={() => handleDelete(document.id)}
                      className="rounded-lg border border-black/8 px-3 py-1.5 text-[11px] font-medium text-red-600 transition hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* FOOTER */}

        <p className="mt-6 text-center text-[10px] text-gray-400">
          NexusCopilot · Enterprise AI Knowledge Base
        </p>
      </div>
    </main>
  );
}
